# -*- coding: utf-8 -*-
"""實盤主程式：
1) 從 MySQL 回填歷史 bar 作為暖機
2) 連接 Redis 即時 tick，聚合成 bar（封口後）
3) 每根 bar 餵給策略 → 產生交易訊號 → 呼叫 Broker 送單
"""
from strategy.config import SYMBOLS, BAR_FRAME, WARMUP_BARS, STRATEGY, STRATEGY_PARAMS
from strategy.core.datafeed import HybridFeed
from strategy.core.registry import load_strategy
from strategy.broker.shioaji_broker import ShioajiBroker

def main():
    feed = HybridFeed(SYMBOLS, WARMUP_BARS, BAR_FRAME)
    warm = feed.warmup_bars()

    strat = load_strategy(STRATEGY, STRATEGY_PARAMS)
    strat.on_start(SYMBOLS, warm)

    broker = ShioajiBroker()

    print("[LIVE] 啟動，等待即時行情...")
    for bar in feed.stream_bars():
        sig = strat.on_bar(bar)
        if sig:
            broker.submit(sig)

if __name__ == "__main__":
    main()
