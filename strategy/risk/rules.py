# -*- coding: utf-8 -*-
"""風控規則骨架（可在 submit 前檢查）。"""
from strategy.core.events import Signal

def max_qty(signal: Signal, max_lots: int = 2) -> bool:
    """限制單筆最大口數。回傳 True 表示通過風控。"""
    return signal.qty <= max_lots
