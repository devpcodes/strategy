# Strategy Framework（可替換策略｜即時行情 + 歷史資料｜自動下單）

本專案提供一個「**單一框架，多策略可替換**」的最小範例：

- **資料來源**
  - **MySQL**：歷史 K 線（或從 Tick 聚合）
  - **Redis**：即時 Tick（支援 *pub/sub* 或 *list* 累積 + 阻塞讀取）
- **策略熱插拔**：只要在 `config.py` 換策略名稱與參數即可
- **下單**：`broker/ShioajiBroker`（永豐 API），支援模擬/真實切換
- **Bar 生成**：內建 `BarBuilder`，可從 Tick 聚合 1min bar
- **回測/實盤**：`run_backtest.py` 與 `run_live.py` 共用同一策略介面

> 📌 請先在 `config.py` 填入你的連線設定與策略參數。

---

## 1) 安裝

```bash
pip install -r requirements.txt
```

## 2) 設定

編輯 `strategy/config.py`：
- `REDIS_URL`：你的 Redis URL
- `MYSQL_URL`：你的 MySQL 連線字串（SQLAlchemy 格式）
- `ACCOUNT_MODE`：`"paper"` 或 `"real"`
- `STRATEGY` 與 `STRATEGY_PARAMS`：要跑的策略與參數

## 3) 回測（僅歷史資料）

```bash
python -m strategy.run_backtest
python -m strategy.run_backtest --symbol TXF
```

## 4) 實盤（歷史暖機 + 連接 Redis 即時行情 → 觸發下單）

```bash
python -m strategy.run_live
```

> 實盤需要你的 Redis 有持續寫入 ticks：
> - **pub/sub**：發佈到 Channel，例如：`PUBLISH ticks:TXF '{"symbol":"TXF","timestamp":"2025-08-05T09:00:01","close":23123,"volume":1,"contract":"TXFH5"}'`
> - **list**：推進 `LPUSH ticks:TXF ...`，框架會用 `BRPOP` 方式阻塞讀取。

---

## 專案結構

```
strategy/
├─ config.py
├─ run_live.py
├─ run_backtest.py
├─ core/
│   ├─ events.py
│   ├─ datafeed.py
│   ├─ barbuilder.py
│   └─ registry.py
├─ storage/
│   ├─ mysql.py
│   └─ redis_client.py
├─ broker/
│   ├─ base.py
│   └─ shioaji_broker.py
├─ strategies/
│   ├─ base.py
│   └─ ma_crossover.py
├─ risk/
│   └─ rules.py
└─ utils/
    ├─ contracts.py
    └─ timeutil.py
```

---

## 注意事項
- 此範例著重於**架構**與**可替換性**，請依你實際的表結構調整 `storage/mysql.py` 的 SQL。
- 若你 Redis 的生產者是把 Tick 寫進 `list`（例如 `LPUSH ticks:TXF`），本框架會自動以 `BRPOP` 方式阻塞讀取。
- 若你用 `pub/sub`，請在 `config.py` 設定 `USE_PUBSUB=True`。

---

## 授權
MIT

## 啟動mysql和redis
docker-compose up
