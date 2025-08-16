# API 配置
API_KEY = "4NSQiDsG9EmgY9TcRZaNx7ZTpfMLa5PQkHzpPgCkiqmL"
SECRET_KEY = "87aFuVCZW9gtNin1v713mcTqNRqUHpvED86v4VqXTABN"
SIMULATION_MODE = True  # 模擬模式 (True: 模擬交易, False: 真實交易)
CA_PATH="C:/Users/011455/Downloads/Sinopac (57).pfx"
CA_PASSWD="C121134291"
CA_PERSON_ID="C121134291"
STRATEGY_PARAMS = {
    "short_window": 5,  # 短期均線窗口
    "long_window": 20,  # 長期均線窗口
}

# Redis 配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# MySQL 配置
MYSQL_URL = "mysql+pymysql://trader:traderpass@localhost:3307/market"