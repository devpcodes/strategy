from collections import deque
from strategy.base_strategy import BaseStrategy

class MovingAverageCrossoverStrategy(BaseStrategy):
    def __init__(self, short_window, long_window):
        self.short_window = short_window
        self.long_window = long_window
        self.prices = deque(maxlen=self.long_window)  # 用 deque 儲存價格歷史數據

    def generate_signal(self, market_data):
        self.prices.append(market_data["close"])  # 加入最新收盤價
        if len(self.prices) < self.long_window:
            return "hold"  # 如果數據不足，保持觀望

        ma_short = sum(list(self.prices)[-self.short_window:]) / self.short_window
        ma_long = sum(self.prices) / self.long_window

        if ma_short > ma_long:
            return "buy"
        elif ma_short < ma_long:
            return "sell"
        else:
            return "hold"


