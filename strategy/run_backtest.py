# -*- coding: utf-8 -*-
"""
回測主程式（含統計 + 單一商品平倉權益曲線輸出）：
1) 從 MySQL 讀取每個 symbol 的歷史 bar
2) 依時間排序逐根餵給策略
3) 由 BacktestEngine 轉換訊號為部位/交易/損益
4) 輸出 trades.csv、equity.csv，並在終端列印「中文」統計摘要
5) 依參數 --symbol (TXF/MXF) 產出「平倉權益曲線」(CSV + PNG)，預設 MXF
"""
import argparse
from pathlib import Path
import pandas as pd

from strategy.config import SYMBOLS, BAR_FRAME, STRATEGY, STRATEGY_PARAMS
from strategy.storage.mysql import load_history
from strategy.core.registry import load_strategy
from strategy.core.events import Bar
from strategy.core.backtester import BacktestEngine

OUT_DIR = Path("backtest_out")

def main():
    # 參數：選擇要輸出的平倉權益曲線商品（預設 MXF）
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="MXF", help="個別商品（TXF 或 MXF），預設 MXF")
    args = parser.parse_args()
    single_symbol = args.symbol.upper()

    # 1) 載入歷史資料
    history = {s: load_history(s, limit_bars=5000, frame=BAR_FRAME) for s in SYMBOLS}
    bars = []
    for s, df in history.items():
        bars.extend([Bar(s, r.ts, r.o, r.h, r.l, r.c, int(r.v)) for r in df.itertuples()])
    bars.sort(key=lambda b: (b.ts, b.symbol))

    # 2) 載入策略
    strat = load_strategy(STRATEGY, STRATEGY_PARAMS)
    strat.on_start(SYMBOLS, {s: [] for s in SYMBOLS})

    # 3) 回測引擎
    engine = BacktestEngine(start_cash=1_000_000)

    # 逐根 Bar 跑策略與回測
    for b in bars:
        sig = strat.on_bar(b)
        engine.on_bar(b, sig)

    # 結束結算
    if bars:
        engine.close_all(bars[-1].ts)

    # 4) 統計與輸出（整體）
    res = engine.results()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    res["trades_df"].to_csv(OUT_DIR / "trades.csv", index=False, encoding="utf-8-sig")
    res["equity_df"].to_csv(OUT_DIR / "equity.csv", index=False, encoding="utf-8-sig")

    # 5) 中文摘要（整體）
    print("=== 回測摘要（整體） ===")
    print(f"初始資金        : {res['start_cash']:.2f}")
    print(f"最終資產        : {res['end_equity']:.2f}")
    print(f"總報酬率        : {res['total_return']*100:.2f}%")
    print(f"夏普比率(日)    : {res['sharpe_daily']:.3f}")
    print(f"最大回撤        : {res['max_drawdown']*100:.2f}%")
    print(f"交易次數        : {res['num_trades']}")
    print(f"勝率            : {res['win_rate']*100:.2f}%")
    print(f"平均單筆損益    : {res['avg_trade_pnl']:.2f}")
    print(f"總交易損益      : {res['total_trade_pnl']:.2f}")
    print(f"檔案已儲存      : {OUT_DIR/'trades.csv'}, {OUT_DIR/'equity.csv'}")

    # 6) 產出「單一商品」平倉權益曲線（只計入已平倉的實現損益）
    trades_df_all = res["trades_df"].copy()
    if trades_df_all.empty:
        print("沒有任何交易紀錄，無法產出個別商品結果。")
        return

    sub = trades_df_all[
        trades_df_all["symbol"].astype(str).str.startswith(single_symbol)
    ].dropna(subset=["exit_ts"]).copy()

    if sub.empty:
        print(f"沒有 {single_symbol} 的已平倉交易，無法產出個別商品結果。")
        return

    sub["exit_ts"] = pd.to_datetime(sub["exit_ts"])
    sub.sort_values("exit_ts", inplace=True)

    # 單商品統計（以「實現損益」為基礎）
    num_trades = int(len(sub))
    win_rate   = float((sub["pnl"] > 0).mean()) * 100.0
    avg_pnl    = float(sub["pnl"].mean())
    total_pnl  = float(sub["pnl"].sum())

    # 平倉權益曲線：
    #   realized_pnl：以 0 為基準的單商品累積損益
    #   equity_from_start：加上整體初始資金後的權益口徑
    sub["cum_realized"] = sub["pnl"].cumsum()
    single_eq = sub.loc[:, ["exit_ts", "cum_realized"]].rename(
        columns={"exit_ts": "ts", "cum_realized": "realized_pnl"}
    )
    single_eq["equity_from_start"] = res["start_cash"] + single_eq["realized_pnl"]

    # 匯出單商品檔案
    out_trades_csv = OUT_DIR / f"trades_{single_symbol.lower()}.csv"
    out_eq_csv     = OUT_DIR / f"equity_{single_symbol.lower()}.csv"
    sub.to_csv(out_trades_csv, index=False, encoding="utf-8-sig")
    single_eq.to_csv(out_eq_csv, index=False, encoding="utf-8-sig")

    # 繪圖（若未安裝 matplotlib，仍會輸出 CSV）
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 4))
        # 預設畫「單商品累積損益（基準=0）」；若想畫 equity_from_start，改下一行 y 值即可
        plt.plot(single_eq["ts"], single_eq["realized_pnl"])
        plt.title(f"{single_symbol} 平倉權益曲線（單商品累積損益，基準=0）")
        plt.xlabel("時間"); plt.ylabel("累積損益")
        plt.tight_layout()
        out_png = OUT_DIR / f"equity_{single_symbol.lower()}.png"
        plt.savefig(out_png, dpi=150)
        # 若要顯示圖形：plt.show()
        print(f"已輸出 {single_symbol} 個別結果：{out_trades_csv}、{out_eq_csv}、{out_png}")
    except Exception:
        print(f"已輸出 {single_symbol} 個別結果：{out_trades_csv}、{out_eq_csv}（如需 PNG，請安裝 matplotlib）")

    # 終端列印單商品摘要（中文）
    print("=== 個別商品回測摘要 ===")
    print(f"商品            : {single_symbol}")
    print(f"交易次數        : {num_trades}")
    print(f"勝率            : {win_rate:.2f}%")
    print(f"平均單筆損益    : {avg_pnl:.2f}")
    print(f"總交易損益      : {total_pnl:.2f}")

if __name__ == "__main__":
    main()
