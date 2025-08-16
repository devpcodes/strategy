# -*- coding: utf-8 -*-
"""Shioaji Broker：範例版（示意）。

> 實際送單前請務必做好風控！
"""
from typing import Optional
from strategy.broker.base import Broker
from strategy.core.events import Signal
from strategy.config import API_KEY, SECRET_KEY, ACCOUNT_MODE

try:
    import shioaji as sj
except Exception as e:  # 允許在未安裝 shioaji 的環境下仍可匯入模組
    sj = None

class ShioajiBroker(Broker):
    def __init__(self):
        if sj is None:
            raise RuntimeError("請先安裝 shioaji：pip install shioaji")
        self.api = sj.Shioaji(simulation=True)
        self.api.login(api_key=API_KEY, secret_key=SECRET_KEY)
        # TODO: 依你的合約/帳戶初始化，例如 self.account = self.api.futopt_account

    def submit(self, signal: Signal) -> None:
        # TODO: 依照你的商品與下單邏輯轉為 Shioaji 訂單
        # 這裡先示範打印（避免在範例專案裡誤下真單）
        print(f"[BROKER] submit: {signal.side} {signal.symbol} x{signal.qty} ({signal.reason})")
        # e.g. self.api.place_order(contract, order)

# 供外部直接使用
BrokerClass = ShioajiBroker
