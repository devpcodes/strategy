from config import API_KEY, SECRET_KEY, STRATEGY_PARAMS
from data.tick_handler import TickHandler
from trading.position_manager import PositionManager
from trading.order_executor import OrderExecutor
from strategy.ma_crossover import MovingAverageCrossoverStrategy
import shioaji as sj
import time

def main():
    # 全局初始化 API
    api = sj.Shioaji(simulation=True)
    api.login(api_key=API_KEY, secret_key=SECRET_KEY)
    contract = min(
        [
            x for x in api.Contracts.Futures.TXF 
            if x.code[-2:] not in ["R1", "R2"]
        ],
        key=lambda x: x.delivery_date
    )

    print("[API] 登錄成功！")
    print(contract)

    # 初始化模組
    order_executor = OrderExecutor(api=api)
    position_manager = PositionManager(
        order_executor=order_executor,
        stop_loss_pct=0.02,  # 停損 2%
        trailing_stop_pct=0.05  # 移動停利 5%
    )
    strategy = MovingAverageCrossoverStrategy(
        short_window=STRATEGY_PARAMS["short_window"],
        long_window=STRATEGY_PARAMS["long_window"]
    )

    tick_handler = TickHandler(api=api)
    
    try:
        # 啟動監控與行情訂閱
        tick_handler.monitor_and_reconnect(
            contract_code=contract.symbol,
            strategy=strategy,
            position_manager=position_manager
        )
    except KeyboardInterrupt:
        print("[用戶中止運行]")
        tick_handler.unsubscribe_from_market(contract.symbol)
    finally:
        api.logout()
        print("[系統退出] API 已登出")

if __name__ == "__main__":
    main()