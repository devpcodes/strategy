class BaseStrategy:
    def __init__(self):
        pass

    def generate_signal(self, market_data):
        """生成交易信號的邏輯
        返回: 製定的信號 ('buy', 'sell', 'hold')
        """
        raise NotImplementedError("策略基類需實現此方法")