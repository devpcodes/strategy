# -*- coding: utf-8 -*-
"""策略載入器：依名稱動態 import 策略。"""
from importlib import import_module

def load_strategy(name: str, params: dict):
    mod = import_module(f"strategy.strategies.{name}")
    # 規範：策略模組內需暴露 `StrategyClass` 或指定名稱
    cls = getattr(mod, "StrategyClass")
    return cls(**params)
