# -*- coding: utf-8 -*-
"""
BacktestEngine：把策略 on_bar 的 Signal 轉成部位、交易、損益與績效統計。
假設：
- 訊號 side ∈ {"BUY","SELL"}，表示目標方向（多/空，一次全量反手或進場）
- 以當根 bar 的收盤價成交（實務可加入滑價 / 手續費）
- 每個 symbol 獨立管理部位；qty 來自 Signal.qty
- 期貨乘數（每跳點價值）從 config.MULTIPLIER 取得
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Iterable
import pandas as pd
import numpy as np
from strategy.core.events import Bar, Signal
from strategy.config import STRATEGY_PARAMS

# 期貨乘數（可移到 config.py）
MULTIPLIER: Dict[str, int] = {
    "TXF": 200,   # 台指期
    "MXF": 50,    # 小台指期
}

SLIPPAGE = 0.0   # 每口滑價（點）
FEE_PER_CONTRACT = 0.0  # 單口手續費（以貨幣計）

@dataclass
class Position:
    side: int = 0          # 1=多, -1=空, 0=空手
    qty: int = 0
    avg_price: float = 0.0

@dataclass
class Trade:
    symbol: str
    side: str              # "LONG"/"SHORT"
    qty: int
    entry_ts: pd.Timestamp
    entry_price: float
    exit_ts: pd.Timestamp
    exit_price: float
    pnl: float
    bars_held: int

class BacktestEngine:
    def __init__(self, start_cash: float = 1_000_000.0):
        self.start_cash = float(start_cash)
        self.equity = self.start_cash
        self.positions: Dict[str, Position] = {}
        self.last_close: Dict[str, float] = {}
        self.trades: List[Trade] = []
        self.equity_records: List[Dict] = []

    def _mult(self, symbol: str) -> float:
        # 依商品前綴選乘數
        for k, v in MULTIPLIER.items():
            if symbol.startswith(k):
                return float(v)
        return 1.0

    def on_bar(self, bar: Bar, signal: Optional[Signal]) -> None:
        """處理一根 bar：先計算持有部位的浮損益，再依訊號調整部位並記錄交易。"""
        sym = bar.symbol
        mult = self._mult(sym)

        # --- 浮損益（上一根收盤到本根收盤）
        prev_close = self.last_close.get(sym)
        if prev_close is not None:
            pos = self.positions.get(sym, Position())
            dprice = (bar.c - prev_close)
            self.equity += pos.side * pos.qty * dprice * mult
        self.last_close[sym] = bar.c  # 更新 close

        # --- 有訊號就調整目標部位（反手/進出場）
        if signal:
            target_side = 1 if signal.side.upper() == "BUY" else -1
            qty = int(signal.qty or STRATEGY_PARAMS.get("qty", 1))
            fill_price = bar.c + (SLIPPAGE * target_side)
            fee = FEE_PER_CONTRACT * qty

            cur = self.positions.get(sym, Position())
            # 目標與現況不同 → 先平倉再反手
            if cur.side != 0 and cur.side != target_side:
                # 平掉舊部位
                pnl = (fill_price - cur.avg_price) * (cur.side) * cur.qty * self._mult(sym) * -1
                pnl -= FEE_PER_CONTRACT * cur.qty
                self.equity += pnl
                self.trades[-1].exit_ts = bar.ts
                self.trades[-1].exit_price = fill_price
                self.trades[-1].pnl = pnl
                # 清空
                cur = Position()

            # 進新倉/加碼成目標（簡化為整體設定成 target）
            if target_side != 0:
                # 開立新交易紀錄（先暫存，出場時補 exit 與 pnl）
                self.trades.append(Trade(
                    symbol=sym,
                    side="LONG" if target_side == 1 else "SHORT",
                    qty=qty,
                    entry_ts=bar.ts,
                    entry_price=fill_price,
                    exit_ts=pd.NaT, exit_price=np.nan,
                    pnl=0.0, bars_held=0
                ))
                self.equity -= fee
                self.positions[sym] = Position(side=target_side, qty=qty, avg_price=fill_price)
            else:
                # 目標空手 → 若目前有倉，平倉
                if cur.side != 0:
                    pnl = (fill_price - cur.avg_price) * (cur.side) * cur.qty * self._mult(sym) * -1
                    pnl -= FEE_PER_CONTRACT * cur.qty
                    self.equity += pnl
                    self.trades[-1].exit_ts = bar.ts
                    self.trades[-1].exit_price = fill_price
                    self.trades[-1].pnl = pnl
                    self.positions[sym] = Position()

        # --- 記錄 equity（用於後續統計）
        self.equity_records.append({"ts": bar.ts, "equity": self.equity})

    def close_all(self, ts: pd.Timestamp):
        """回測結束時以最後價格結算所有部位。"""
        for sym, pos in list(self.positions.items()):
            if pos.side == 0:
                continue
            last_c = self.last_close.get(sym)
            if last_c is None:
                continue
            mult = self._mult(sym)
            pnl = (last_c - pos.avg_price) * (pos.side) * pos.qty * mult * -1
            pnl -= FEE_PER_CONTRACT * pos.qty
            self.equity += pnl
            self.trades[-1].exit_ts = ts
            self.trades[-1].exit_price = last_c
            self.trades[-1].pnl = pnl
            self.positions[sym] = Position()

    # ---------------- 統計輸出 ----------------
    def results(self) -> Dict:
        eq = pd.DataFrame(self.equity_records).drop_duplicates("ts").set_index("ts").sort_index()
        eq["ret"] = eq["equity"].pct_change().fillna(0.0)

        # 以日頻統計 Sharpe / 年化
        daily = eq["equity"].resample("1D").last().dropna()
        daily_ret = daily.pct_change().dropna()
        sharpe = (daily_ret.mean() / (daily_ret.std() + 1e-12)) * np.sqrt(252) if len(daily_ret) > 0 else 0.0

        # 最大回撤
        roll_max = eq["equity"].cummax()
        dd = eq["equity"] / roll_max - 1.0
        max_dd = dd.min() if len(dd) else 0.0

        # 交易統計
        trades_df = pd.DataFrame([t.__dict__ for t in self.trades])
        win_rate = float((trades_df["pnl"] > 0).mean()) if len(trades_df) else 0.0
        avg_pnl = float(trades_df["pnl"].mean()) if len(trades_df) else 0.0
        total_pnl = float(trades_df["pnl"].sum()) if len(trades_df) else 0.0

        return {
            "start_cash": self.start_cash,
            "end_equity": float(eq["equity"].iloc[-1]) if len(eq) else self.start_cash,
            "total_return": float(eq["equity"].iloc[-1] / self.start_cash - 1.0) if len(eq) else 0.0,
            "sharpe_daily": float(sharpe),
            "max_drawdown": float(max_dd),
            "num_trades": int(len(trades_df)),
            "win_rate": float(win_rate),
            "avg_trade_pnl": float(avg_pnl),
            "total_trade_pnl": float(total_pnl),
            "equity_df": eq.reset_index(),
            "trades_df": trades_df,
        }
