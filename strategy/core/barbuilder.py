# -*- coding: utf-8 -*-
"""Tick → Bar 聚合器。

簡化版的 1 分鐘 K 生成：
- 每次收到 Tick，用該 Tick 所屬的分鐘作為 key 更新當根 bar 的 OHLCV
- 一旦分鐘跳變，上一根 bar 視為封口，可被取出（pop）
"""
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
from .events import Tick, Bar

class BarBuilder:
    def __init__(self, frame: str = "1min"):
        # 本版本僅處理 1min，保留 frame 參數以利未來擴充
        self.frame = frame
        self.state: Dict[str, Dict[datetime, Dict[str, float]]] = defaultdict(dict)

    def on_tick(self, t: Tick):
        minute = t.ts.replace(second=0, microsecond=0)
        bucket = self.state[t.symbol].get(minute)
        if not bucket:
            self.state[t.symbol][minute] = bucket = {
                "o": t.price, "h": t.price, "l": t.price, "c": t.price, "v": t.vol
            }
        else:
            bucket["h"] = max(bucket["h"], t.price)
            bucket["l"] = min(bucket["l"], t.price)
            bucket["c"] = t.price
            bucket["v"] += t.vol

    def pop_closed_bars(self, symbol: str, now_minute: datetime) -> List[Bar]:
        """回傳所有「早於 now_minute」的封口 bar。"""
        out: List[Bar] = []
        buckets = self.state[symbol]
        for m in sorted(list(buckets.keys())):
            if m < now_minute:
                s = buckets.pop(m)
                out.append(Bar(symbol, m, s["o"], s["h"], s["l"], s["c"], int(s["v"])))
        return out
