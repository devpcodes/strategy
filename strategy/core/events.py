# -*- coding: utf-8 -*-
"""事件資料結構：Tick / Bar / Signal。

以 dataclass 表示，讓策略與資料流之間傳遞結構化資料。
"""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Tick:
    symbol: str
    ts: datetime
    price: float
    vol: int
    contract: str

@dataclass
class Bar:
    symbol: str
    ts: datetime
    o: float
    h: float
    l: float
    c: float
    v: int

@dataclass
class Signal:
    symbol: str
    side: str      # 'BUY' / 'SELL'
    qty: int
    reason: str = ""
