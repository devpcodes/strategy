# -*- coding: utf-8 -*-
"""最小可用策略：均線黃金交叉/死亡交叉。

- 以 `short` / `long` 兩條移動平均作為判斷
- 當短均線上穿長均線 → 發出 BUY
- 當短均線下穿長均線 → 發出 SELL
"""
from collections import deque
from typing import Dict, List, Optional
from strategy.strategies.base import Strategy
from strategy.core.events import Bar, Signal

class MaCross(Strategy):
    def __init__(self, short: int = 5, long: int = 20, qty: int = 1):
        assert short > 0 and long > 0 and short < long, "short/long 需為正整數，且 short < long"
        self.short = short
        self.long = long
        self.qty = qty
        self.buf: Dict[str, Dict] = {}

    def on_start(self, symbols: List[str], warmup_bars: Dict[str, List[Bar]]) -> None:
        for s in symbols:
            dq_s, dq_l = deque(maxlen=self.short), deque(maxlen=self.long)
            for b in warmup_bars.get(s, []):
                dq_s.append(b.c); dq_l.append(b.c)
            self.buf[s] = {"dq_s": dq_s, "dq_l": dq_l, "pos": 0}

    def on_bar(self, bar: Bar) -> Optional[Signal]:
        st = self.buf[bar.symbol]
        st["dq_s"].append(bar.c)
        st["dq_l"].append(bar.c)
        if len(st["dq_l"]) < self.long:
            return None
        ma_s = sum(st["dq_s"]) / len(st["dq_s"])
        ma_l = sum(st["dq_l"]) / len(st["dq_l"])
        pos = st["pos"]

        if ma_s > ma_l and pos <= 0:
            st["pos"] = 1
            return Signal(bar.symbol, "BUY", self.qty, "MA golden cross")
        if ma_s < ma_l and pos >= 0:
            st["pos"] = -1
            return Signal(bar.symbol, "SELL", self.qty, "MA death cross")
        return None

    def on_stop(self) -> None:
        pass

# 由 registry 透過此名稱載入
StrategyClass = MaCross
