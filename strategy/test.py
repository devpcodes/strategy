import shioaji as sj
import pandas as pd
# print(sj.__version__)
TickFOPv1 = sj.TickFOPv1
Exchange = sj.Exchange
api = sj.Shioaji(simulation=False) # 模擬模式
accounts = api.login(
    api_key="4NSQiDsG9EmgY9TcRZaNx7ZTpfMLa5PQkHzpPgCkiqmL",     # 請修改此處
    secret_key="87aFuVCZW9gtNin1v713mcTqNRqUHpvED86v4VqXTABN"   # 請修改此處
)
api.activate_ca(
    ca_path="C:/Users/011455/Downloads/Sinopac (57).pfx",
    ca_passwd="C121134291",
    person_id="C121134291",
)

# print(accounts)
# contract = api.Contracts.Stocks.TSE["2890"]
# # 證券委託單 - 請修改此處
# order = api.Order(
#     price=18,                                       # 價格
#     quantity=1,                                     # 數量
#     action=sj.constant.Action.Buy,                  # 買賣別
#     price_type=sj.constant.StockPriceType.LMT,      # 委託價格類別
#     order_type=sj.constant.OrderType.ROD,           # 委託條件
#     account=api.stock_account                       # 下單帳號
# )

# # 下單
# trade = api.place_order(contract, order)
# print(trade)

contract = min(
    [
        x for x in api.Contracts.Futures.MXF 
        if x.code[-2:] not in ["R1", "R2"]
    ],
    key=lambda x: x.delivery_date
)
print(contract)

# 即時行情
# api.quote.subscribe(
#     api.Contracts.Futures.TXF['TXF202508'],
#     quote_type = sj.constant.QuoteType.Tick,
#     version = sj.constant.QuoteVersion.v1,
# )

# def quote_callback(exchange:Exchange, tick:TickFOPv1):
#     print(f"Exchange: {exchange}, Tick: {tick}")

# api.quote.set_on_tick_fop_v1_callback(quote_callback)

# 保持程式運行
# try:
#     while True:
#         pass
# except KeyboardInterrupt:
#     print("退出時取消訂閱")
# finally:
#     api.logout()


# 歷史k
kbars = api.kbars(
    contract=api.Contracts.Futures.TXF.TXFR1,
    start="2025-07-28", 
    end="2025-07-28", 
)
print(kbars)

# 行情快照
# contracts = [api.Contracts.Futures.MXF['MXF202508']]
# snapshots = api.snapshots(contracts)
# print(snapshots)

# 查未平倉損益
# positions = api.list_positions(api.futopt_account)
# df = pd.DataFrame(s.__dict__ for s in positions)
# print(df)

# 期貨委託單 - 請修改此處
# order = api.Order(
#     action=sj.constant.Action.Buy,                   # 買賣別
#     price=15000,                                     # 價格
#     quantity=1,                                      # 數量
#     price_type=sj.constant.FuturesPriceType.LMT,     # 委託價格類別
#     order_type=sj.constant.OrderType.ROD,            # 委託條件
#     octype=sj.constant.FuturesOCType.Auto,           # 倉別
#     account=api.futopt_account                       # 下單帳號
# )    
# 下單
# trade = api.place_order(contract, order)
# api.update_status(api.futopt_account)
# print(trade)