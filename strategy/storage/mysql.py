# -*- coding: utf-8 -*-
"""MySQL 讀取歷史資料的簡單封裝。

> 依你的資料表實際結構調整 SQL。
> 假設表 `ticks_MXF/ticks_TXF` 已是「分鐘 K」，若是 Tick 表，請拉出後自行 resample。
"""
import pandas as pd
from sqlalchemy import create_engine, text
from strategy.config import MYSQL_URL, TABLE_MXF, TABLE_TXF

_engine = create_engine(MYSQL_URL, pool_pre_ping=True)

def _table_of(symbol: str) -> str:
    return TABLE_MXF if symbol.startswith("MXF") else TABLE_TXF

def load_history(symbol: str, limit_bars: int = 800, frame: str = "1min") -> pd.DataFrame:
    table = _table_of(symbol)
    sql = text(f"""
        SELECT timestamp AS ts, `open` AS o, `high` AS h, `low` AS l, `close` AS c, `volume` AS v
        FROM {table}
        WHERE contract LIKE :like_symbol
        ORDER BY timestamp DESC
        LIMIT :limit_rows
    """ )
    with _engine.begin() as conn:
        df = pd.read_sql(sql, conn, params={"like_symbol": f"{symbol}%", "limit_rows": int(limit_bars)})
    df = df.sort_values("ts").reset_index(drop=True)
    # 若 frame 不是 1min，可在此以 pandas resample 調整；本版本先直接回傳
    return df
