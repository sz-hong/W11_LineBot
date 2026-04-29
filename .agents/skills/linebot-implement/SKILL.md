---
name: linebot-implement
description: 產出股票 LINE Bot 主程式（app.py），整合 FastAPI + LINE Messaging API + Gemini AI + twstock + SQLite
---

## 💡 核心能力

- **LINE Bot 後端開發**：使用 FastAPI 建立 LINE Webhook 伺服器
- **股票資料查詢**：整合 twstock 取得台股即時/歷史價格
- **AI 分析**：呼叫 Gemini API 對股票進行智慧分析
- **資料持久化**：使用 SQLite 儲存使用者追蹤清單與查詢紀錄
- **訊息格式化**：將股價與分析結果以清晰格式回覆使用者

## 🎯 適用場景

- 需要建立一個股票查詢與分析的 LINE Bot
- 需要整合多個 API（LINE、Gemini、twstock）的後端程式
- 需要產出可以直接 `uvicorn app:app --reload` 執行的 `app.py`

## 📋 技術棧規範

| 項目 | 技術 | 版本 |
|------|------|------|
| Web 框架 | FastAPI | 最新版 |
| ASGI 伺服器 | uvicorn | 最新版 |
| LINE SDK | line-bot-sdk | v3.x（使用 `linebot.v3` 模組） |
| AI 模型 | google-genai | 最新版（Gemini 2.0 Flash） |
| 台股查詢 | twstock | 最新版 |
| 資料庫 | SQLite3 | Python 內建 |
| 環境變數 | python-dotenv | 最新版 |

## ⚠️ 注意事項（重要規則）

### 1. 環境變數管理
- **必須**從 `.env` 檔案讀取所有敏感資訊
- 需要的環境變數：
  - `LINE_CHANNEL_SECRET`：LINE Channel Secret
  - `LINE_CHANNEL_ACCESS_TOKEN`：LINE Channel Access Token
  - `GEMINI_API_KEY`：Google Gemini API Key
- 使用 `python-dotenv` 的 `load_dotenv()` 在程式最開頭載入
- **絕對不能**在程式碼中寫死任何 token

### 2. LINE Bot SDK v3 正確用法
- 匯入路徑必須使用 `linebot.v3` 開頭：
  ```python
  from linebot.v3 import WebhookHandler
  from linebot.v3.messaging import (
      Configuration,
      AsyncApiClient,
      AsyncMessagingApi,
      ReplyMessageRequest,
      TextMessage,
  )
  from linebot.v3.webhooks import MessageEvent, TextMessageContent
  ```
- 使用 `AsyncMessagingApi` 搭配 FastAPI 的 async handler
- Webhook 驗證使用 `WebhookHandler`
- 回覆訊息使用 `ReplyMessageRequest` + `TextMessage`

### 3. FastAPI 路由設計
- `POST /callback`：LINE Webhook endpoint
- 使用 `Request` 物件取得 raw body 進行簽名驗證
- 回傳 "OK" 即可（LINE 不需要特殊回傳）

### 4. 股票查詢邏輯
- 使用 `twstock` 查詢台股
- 先用 `twstock.codes` 查詢股票名稱對應的代號
- 再用 `twstock.realtime.get()` 取得即時報價
- 處理查無此股票的情況，回覆友善提示
- 股價資訊顯示：股票名稱、即時價格、漲跌、漲跌幅、成交量

### 5. Gemini AI 分析
- 使用 `google-genai` 套件（新版 SDK）
- 使用 `genai.Client(api_key=...)` 初始化
- 呼叫 `client.models.generate_content(model="gemini-2.0-flash", contents=...)`
- Prompt 設計要求：
  - 角色設定為「專業股票分析師」
  - 提供股票代號、名稱、即時價格等資訊作為 context
  - 要求分析包含：技術面、基本面、建議
  - 要求回覆以繁體中文
  - 限制回覆長度在 500 字以內
- **必須**加上 `try/except` 錯誤處理

### 6. SQLite 資料庫設計
- 資料庫檔案：`stocks.db`
- 啟動時自動建立 table（`CREATE TABLE IF NOT EXISTS`）
- Table 設計：

```sql
-- 使用者追蹤清單
CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    stock_id TEXT NOT NULL,
    stock_name TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, stock_id)
);

-- 查詢紀錄
CREATE TABLE IF NOT EXISTS query_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    stock_id TEXT NOT NULL,
    stock_name TEXT,
    query_type TEXT DEFAULT 'price',
    queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7. 訊息處理邏輯（指令設計）
- 使用者輸入以下格式觸發不同功能：
  - `查詢 <股票代號或名稱>`：查詢即時股價
  - `分析 <股票代號或名稱>`：AI 分析該股票
  - `追蹤 <股票代號>`：加入追蹤清單
  - `取消追蹤 <股票代號>`：從追蹤清單移除
  - `我的清單`：顯示追蹤清單
  - `幫助` 或 `help`：顯示使用說明
- 其他文字直接交給 Gemini 以股票助手角色回覆

### 8. 錯誤處理
- 所有外部 API 呼叫都要 `try/except`
- 股票代號不存在時回覆提示
- Gemini API 失敗時回覆「AI 分析暫時無法使用」
- LINE SDK 錯誤用 logging 記錄

### 9. 程式碼風格
- 所有函式加上中文 docstring
- 重要邏輯加上中文註解
- 使用 `logging` 模組記錄執行日誌
- 單一檔案 `app.py`，不拆分模組

## 📝 使用範例

### 範例 1：產出完整 LINE Bot 主程式

**用戶輸入**：
> 請根據 linebot-implement Skill 產出一個股票 LINE Bot 的 app.py

**技能輸出**：
產出完整的 `app.py`，包含：

```python
"""
股票 LINE Bot — 查詢台股即時價格 + AI 分析 + 追蹤清單
技術棧：FastAPI + LINE Messaging API v3 + Gemini + twstock + SQLite
"""

import os
import logging
import sqlite3
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from google import genai
import twstock
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    AsyncApiClient,
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

# 載入環境變數
load_dotenv()

# ... 完整的程式碼實作 ...
```

## 📊 輸出格式

產出的 `app.py` 必須：
1. 是一個**完整的、可直接執行**的 Python 檔案
2. 不需要任何修改就能用 `uvicorn app:app --reload` 啟動
3. 包含所有必要的 import、初始化、路由、處理函式
4. 環境變數透過 `.env` 檔案設定

## 🔗 相關技能

- [prd](../prd/SKILL.md)：定義產品需求
- [commit](../commit/SKILL.md)：產出 commit message
- [architecture](../architecture/SKILL.md)：系統架構設計

## 💡 提示

- 先確認 LINE Developers Console 已建立 Messaging API Channel
- 確認 Google AI Studio 已取得 Gemini API Key
- 本地測試需要 ngrok 將 localhost 暴露為 https URL
- Webhook URL 格式：`https://<ngrok-url>/callback`
