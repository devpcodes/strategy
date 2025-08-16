import shioaji as sj
import time
import redis
import json
class TickHandler:
    def __init__(self, api):
        """初始化 TickHandler，並接收全局的 Shioaji API 實例"""
        self.api = api  # 共用的 API 實例（由主程式注入）
        self.is_subscribed = False  # 用於追踪當前是否訂閱行情中
        # # 連接 Redis
        # self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    # 
    def subscribe_to_market(self, contract_code, strategy, position_manager):
        """
        訂閱期貨即時行情
        :param contract_code: 要訂閱的期貨合約代碼
        :param strategy: 策略實例，用於生成交易信號
        :param position_manager: 倉位管理器，用於執行交易邏輯
        """
        try:
            # 獲取期貨合約對象
            contract = self.api.Contracts.Futures.TXF.get(contract_code)
            if not contract:
                raise ValueError(f"無效的合約代碼: {contract_code}")

            # 定義回調函數，用於處理行情數據
            def on_tick(exchange, tick):
                try:
                    market_data = tick  # 獲取即時數據
                    signal = strategy.generate_signal(market_data)  # 策略生成信號
                    position_manager.handle_signal(signal, contract, tick.close)  # 執行倉位管理

                    # tick_data = {
                    #     "symbol": tick.code,
                    #     "timestamp": tick.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    #     "open": float(tick.open),
                    #     "high": float(tick.high),
                    #     "low": float(tick.low),
                    #     "close": float(tick.close),
                    #     "volume": tick.volume
                    # }
                    # # 存到 Redis List
                    # self.r.lpush(f"ticks:{tick.code}", json.dumps(tick_data))
                    print(f"[行情更新] 商品代碼: {tick.code}, 價格: {tick.close}, 成交量: {tick.volume},日期：{tick.datetime}, detail: {tick}")
                except Exception as e:
                    print(f"[回調錯誤] {e}")  # 防止回調崩潰影響系統的運行

            # 設置回調函數
            self.api.quote.set_on_tick_fop_v1_callback(on_tick)

            # 開始訂閱行情數據
            self.api.quote.subscribe(
                contract=contract,
                quote_type=sj.constant.QuoteType.Tick,  # 訂閱逐筆行情
                version=sj.constant.QuoteVersion.v1    # 使用版本 v1
            )
            self.is_subscribed = True
            print(f"[行情訂閱成功] 合約: {contract_code}")
        except Exception as e:
            print(f"[訂閱失敗] 發生錯誤: {e}")
            self.is_subscribed = False

    def unsubscribe_from_market(self, contract_code):
        """
        取消訂閱期貨行情
        :param contract_code: 要取消訂閱的期貨合約代碼
        """
        if not self.is_subscribed:
            print(f"[取消訂閱失敗] 尚未訂閱行情: {contract_code}")
            return

        try:
            # 獲取期貨合約對象
            contract = self.api.Contracts.Futures.TXF.get(contract_code)
            if not contract:
                raise ValueError(f"[取消訂閱錯誤] 找不到合約: {contract_code}")

            # 執行取消訂閱
            self.api.quote.unsubscribe(
                contract=contract,
                quote_type=sj.constant.QuoteType.Tick,
                version=sj.constant.QuoteVersion.v1
            )
            self.is_subscribed = False
            print(f"[取消訂閱成功] 合約: {contract_code}")
        except Exception as e:
            print(f"[取消訂閱失敗] 發生錯誤: {e}")

    # strategy, position_manager,
    def monitor_and_reconnect(self, contract_code, strategy, position_manager):
        """
        監控行情訂閱情況，若斷開則自動重新訂閱
        :param contract_code: 要訂閱的期貨合約代碼
        :param strategy: 策略實例
        :param position_manager: 倉位管理器
        :param interval: 檢查是否需要重新訂閱的時間間隔（秒）
        """
        while True:
            try:
                if not self.is_subscribed:
                    print(f"[重新訂閱] 合約: {contract_code}")
                    self.subscribe_to_market(contract_code, strategy, position_manager)#
                time.sleep(10)  # 每隔 interval 秒檢查一次
            except Exception as e:
                print(f"[監控錯誤] {e}")
                time.sleep(5)  # 若發生異常則等待 5 秒後重試