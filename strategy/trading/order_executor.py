import shioaji as sj

class OrderExecutor:
    def __init__(self, api):
        """接收共享的 API 實例"""
        self.api = api
        
    def place_order(self, contract, action, price, quantity=1):
        """執行下單"""
        order = self.api.Order(
            action=action,
            price=price,
            quantity=quantity,
            price_type=sj.constant.FuturesPriceType.LMT,     # 委託價格類別
            order_type=sj.constant.OrderType.ROD, 
        )
        trade = self.api.place_order(contract, order)
        print(f"[交易執行] 操作: {action}, 價格: {price}, 結果: {trade}")

