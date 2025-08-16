# -*- coding: utf-8 -*-
"""資料來源組合：MySQL 歷史 + Redis 即時。"""
import json
from datetime import datetime
from typing import Dict, List, Iterable
from strategy.storage.mysql import load_history
from strategy.storage.redis_client import get_redis
from .events import Tick, Bar
from .barbuilder import BarBuilder
from strategy.config import USE_PUBSUB, REDIS_PATTERNS, REDIS_LIST_KEYS

class MySQLHistory:
    def __init__(self, symbols: List[str], bars: int, frame: str = "1min"):
        self.symbols = symbols
        self.bars = bars
        self.frame = frame

    def warmup(self) -> Dict[str, List[Bar]]:
        out: Dict[str, List[Bar]] = {}
        for s in self.symbols:
            df = load_history(s, limit_bars=self.bars, frame=self.frame)
            out[s] = [Bar(s, r.ts, r.o, r.h, r.l, r.c, int(r.v)) for r in df.itertuples()]
        return out

class RedisTickStream:
    """從 Redis 提取即時 Tick：支援 Pub/Sub 或 List（BRPOP）。"""
    def __init__(self):
        self.r = get_redis()
        self.mode_pubsub = USE_PUBSUB
        if self.mode_pubsub:
            self.ps = self.r.pubsub()
            for p in REDIS_PATTERNS:
                self.ps.psubscribe(p)
        else:
            self.list_keys = REDIS_LIST_KEYS
            if not self.list_keys:
                raise ValueError("List 模式需要在 config.REDIS_LIST_KEYS 設定 keys")

    def __iter__(self) -> Iterable[Tick]:
        if self.mode_pubsub:
            for msg in self.ps.listen():
                if msg.get("type") not in ("message", "pmessage"):
                    continue
                d = json.loads(msg["data"])
                yield _tick_from_dict(d)
        else:
            while True:
                # 阻塞等待任一 list 有資料（1 秒 timeout 以便可中斷）
                res = self.r.brpop(self.list_keys, timeout=1)
                if not res:
                    continue
                _, payload = res
                d = json.loads(payload)
                yield _tick_from_dict(d)

def _tick_from_dict(d: dict) -> Tick:
    return Tick(
        symbol=d.get("symbol"),
        contract=d.get("contract", ""),
        ts=datetime.fromisoformat(d["timestamp"]),
        price=float(d.get("close") or d.get("price")),
        vol=int(d.get("volume", 1)),
    )

class HybridFeed:
    """先回填歷史 bar，再連接 Redis 即時 tick，並持續輸出封口後的 bar。"""
    def __init__(self, symbols: List[str], warmup_bars: int, frame: str = "1min"):
        self.hist = MySQLHistory(symbols, warmup_bars, frame)
        self.redis = RedisTickStream()
        self.builder = BarBuilder(frame)
        self.last_minute = {}

    def warmup_bars(self) -> Dict[str, List[Bar]]:
        return self.hist.warmup()

    def stream_bars(self) -> Iterable[Bar]:
        for tick in self.redis:
            m = tick.ts.replace(second=0, microsecond=0)
            last = self.last_minute.get(tick.symbol)
            if last is not None and m > last:
                # 先吐出上一分鐘封口 bar
                for b in self.builder.pop_closed_bars(tick.symbol, m):
                    yield b
            self.last_minute[tick.symbol] = m
            self.builder.on_tick(tick)
