# -*- coding: utf-8 -*-
"""Broker 抽象層：統一下單介面，便於替換券商。"""
from abc import ABC, abstractmethod
from strategy.core.events import Signal

class Broker(ABC):
    @abstractmethod
    def submit(self, signal: Signal) -> None:
        """接收交易訊號並送單。"""
        ...
