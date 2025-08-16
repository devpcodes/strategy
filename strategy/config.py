# -*- coding: utf-8 -*-

from typing import List

# ============== Redis ==============
# Redis 連線字串（db=0），你也可改成 "redis://:password@host:6379/0"
REDIS_URL: str = "redis://localhost:6379/0"

# Redis tick 來源設定：
# 1) 若 USE_PUBSUB=True → 透過 Pub/Sub 訂閱 pattern
# 2) 若 USE_PUBSUB=False → 透過阻塞式 BRPOP 從 list 取出（keys 為列表）
USE_PUBSUB: bool = False
REDIS_PATTERNS: List[str] = ["ticks:*"]   # Pub/Sub 時使用的 Pattern
REDIS_LIST_KEYS: List[str] = ["ticks:TXF", "ticks:MXF"]  # List 模式使用

# ============== MySQL ==============
# 以 SQLAlchemy URL 格式指定資料庫。注意 MySQL 8 預設認證是 caching_sha2_password。
# 若 pymysql 連線報 cryptography 相關錯誤，請：pip install cryptography
MYSQL_URL: str = "mysql+pymysql://trader:traderpass@localhost:3307/market"

# MySQL 中的表名（以你的實際情況調整）
TABLE_TXF: str = "ticks_TXF"
TABLE_MXF: str = "ticks_MXF"

# ============== 商品與 bar 設定 ==============
# 交易商品（用來決定讀哪張表 & Redis key）
SYMBOLS: List[str] = ["TXF", "MXF"]

# bar 週期（'1min'、'5s' 等 Pandas 支援的 resample 字串）
BAR_FRAME: str = "1min"

# 實盤啟動時，從歷史讀取多少根 bar 作為暖機（供均線、指標初始化）
WARMUP_BARS: int = 800

# ============== 策略 ==============
# 指定要載入的策略模組（對應 strategies/<name>.py）
STRATEGY: str = "ma_crossover"
STRATEGY_PARAMS = {
    "short": 5,    # 短均線
    "long": 20,    # 長均線
    "qty": 1       # 下單口數
}

# ============== 下單（Shioaji） ==============
# 'paper' 模式使用模擬交易；'real' 模式請自行確認風控！
ACCOUNT_MODE: str = "paper"

# 你的 API Key / Secret 請填在此（示例值請改掉）
API_KEY = "4NSQiDsG9EmgY9TcRZaNx7ZTpfMLa5PQkHzpPgCkiqmL"
SECRET_KEY = "87aFuVCZW9gtNin1v713mcTqNRqUHpvED86v4VqXTABN"
