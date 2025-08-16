from decimal import Decimal
class PositionManager:
    def __init__(self, order_executor, stop_loss_pct, trailing_stop_pct):
        """
        :param order_executor: 負責實際下單的執行器
        :param stop_loss_pct: 停損百分比 (如 0.02 代表 2%)
        :param trailing_stop_pct: 移動停利百分比 (如 0.05 代表 5%)
        """
        self.position = None  # 當前持倉狀態：'long' 或 'short'
        self.entry_price = None  # 進場價格
        self.highest_price = None  # 持倉期間的最高價（移動停利）
        self.lowest_price = None  # 持倉期間的最低價（移動停利）
        self.order_executor = order_executor
        # self.stop_loss_pct = stop_loss_pct
        # self.trailing_stop_pct = trailing_stop_pct
        self.stop_loss_pct = Decimal(stop_loss_pct)  # 改為 Decimal
        self.trailing_stop_pct = Decimal(trailing_stop_pct)  # 改為 Decimal

    def handle_signal(self, signal, contract, current_price):
        """
        根據策略信號進行管理，包括下單、停損、移動停利
        """
        if signal == "buy":
            self._open_position("Buy", contract, current_price)
        elif signal == "sell":
            self._open_position("Sell", contract, current_price)
        
        # 在已經有持倉的情況下，檢查是否達到停損或移動停利條件
        if self.position == "long" or self.position == "short":
            self._check_risk_management(contract, current_price)

    def _open_position(self, action, contract, current_price):
        """開啟新的倉位（買入或賣出）"""
        if self.position is None:
            self.order_executor.place_order(contract=contract, action=action, price=current_price)
            self.position = "long" if action == "Buy" else "short"
            self.entry_price = current_price
            self.highest_price = current_price  # 初始化移動停利的價格
            self.lowest_price = current_price
            print(f"[倉位開啟] 方向: {self.position}, 價格: {self.entry_price}")

    def _check_risk_management(self, contract, current_price):
        """
        檢查價格是否達到停損或移動停利條件，並進行平倉
        """
        stop_loss_triggered = False
        trailing_stop_triggered = False

        # 停損計算
        if self.position == "long":  # 多頭停損檢查
            if current_price <= self.entry_price * (1 - self.stop_loss_pct):
                stop_loss_triggered = True
        elif self.position == "short":  # 空頭停損檢查
            if current_price >= self.entry_price * (1 + self.stop_loss_pct):
                stop_loss_triggered = True

        # 移動停利計算（更新最高/最低價）
        if self.position == "long":
            if current_price > self.highest_price:
                self.highest_price = current_price
            elif current_price <= self.highest_price * (1 - self.trailing_stop_pct):
                trailing_stop_triggered = True
        elif self.position == "short":
            if current_price < self.lowest_price:
                self.lowest_price = current_price
            elif current_price >= self.lowest_price * (1 + self.trailing_stop_pct):
                trailing_stop_triggered = True

        # 執行平倉
        if stop_loss_triggered:
            print("[停損觸發] 平倉")
            self._close_position(contract, current_price)
        elif trailing_stop_triggered:
            print("[移動停利觸發] 平倉")
            self._close_position(contract, current_price)

    def _close_position(self, contract, current_price):
        """執行平倉操作"""
        action = "Sell" if self.position == "long" else "Buy"
        self.order_executor.place_order(contract=contract, action=action, price=current_price)
        print(f"[倉位平倉] 方向: {self.position}, 價格: {current_price}")
        self.position = None
        self.entry_price = None
        self.highest_price = None
        self.lowest_price = None