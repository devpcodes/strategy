# -*- coding: utf-8 -*-
"""策略介面。所有策略需實作此介面供主程式呼叫。"""

from typing import Dict, List, Optional
from strategy.core.events import Bar, Signal

class Strategy:
    def on_start(self, symbols: List[str], warmup_bars: Dict[str, List[Bar]]) -> None:
        """初始化（在回填完歷史 bar 後被呼叫）。"""
        ...

    def on_bar(self, bar: Bar) -> Optional[Signal]:
        """每當有一根新 bar（封口）產生時被呼叫，回傳交易訊號或 None。"""
        ...

    def on_stop(self) -> None:
        """策略結束時被呼叫。"""
        ...
