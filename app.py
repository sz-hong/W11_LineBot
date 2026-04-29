"""
股票小助手 LINE Bot
====================
查詢台股即時價格 + Gemini AI 分析 + 個人追蹤清單

技術棧：FastAPI + LINE Messaging API v3 + Google Gemini + twstock + SQLite
啟動方式：uvicorn app:app --reload
"""

import os
import re
import logging
import sqlite3
from contextlib import asynccontextmanager

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

# ========== 載入環境變數 ==========
load_dotenv()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ========== Logging 設定 ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ========== 資料庫初始化 ==========
DB_PATH = "stocks.db"


def init_db():
    """初始化 SQLite 資料庫，建立所需的 table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 使用者追蹤清單
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            stock_id TEXT NOT NULL,
            stock_name TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, stock_id)
        )
    """)

    # 查詢紀錄
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            stock_id TEXT NOT NULL,
            stock_name TEXT,
            query_type TEXT DEFAULT 'price',
            queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    logger.info("資料庫初始化完成")


# ========== Gemini AI 初始化 ==========
client = genai.Client(api_key=GEMINI_API_KEY)


# ========== LINE Bot 初始化 ==========
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)


# ========== FastAPI 應用 ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    init_db()
    logger.info("股票小助手 LINE Bot 已啟動 🚀")
    yield
    logger.info("股票小助手 LINE Bot 已關閉")


app = FastAPI(
    title="股票小助手 LINE Bot",
    description="查詢台股即時價格 + AI 分析 + 追蹤清單",
    version="1.0.0",
    lifespan=lifespan,
)


# ========== 工具函式 ==========

def find_stock_id(keyword: str) -> tuple[str, str] | None:
    """
    根據股票代號或名稱查找股票資訊

    Args:
        keyword: 股票代號（如 '2330'）或名稱（如 '台積電'）

    Returns:
        (stock_id, stock_name) 或 None
    """
    # 先嘗試直接用代號查詢
    if keyword in twstock.codes:
        return (keyword, twstock.codes[keyword].name)

    # 用名稱搜尋
    for code, stock in twstock.codes.items():
        if stock.name == keyword:
            return (code, stock.name)

    return None


def get_realtime_price(stock_id: str) -> dict | None:
    """
    取得台股即時報價

    Args:
        stock_id: 股票代號

    Returns:
        即時報價資料字典，或 None（查詢失敗時）
    """
    try:
        data = twstock.realtime.get(stock_id)
        if data.get("success"):
            return data
        else:
            logger.warning(f"即時報價查詢失敗: {stock_id}")
            return None
    except Exception as e:
        logger.error(f"即時報價查詢例外: {e}")
        return None


def format_stock_price(data: dict) -> str:
    """
    將即時報價資料格式化為友善的文字訊息

    Args:
        data: twstock.realtime.get() 回傳的資料

    Returns:
        格式化後的訊息字串
    """
    info = data.get("info", {})
    realtime = data.get("realtime", {})

    name = info.get("name", "未知")
    code = info.get("code", "----")
    time_str = info.get("time", "")

    # 取得價格資訊
    latest_price = realtime.get("latest_trade_price", "N/A")
    open_price = realtime.get("open", "N/A")
    high = realtime.get("high", "N/A")
    low = realtime.get("low", "N/A")
    volume = realtime.get("accumulate_trade_volume", "N/A")

    # 計算漲跌（與昨收比較）
    yesterday_close = data.get("realtime", {}).get("yesterday_close", None)
    change_str = ""
    if yesterday_close and latest_price and latest_price != "N/A":
        try:
            change = float(latest_price) - float(yesterday_close)
            change_pct = (change / float(yesterday_close)) * 100
            arrow = "📈" if change >= 0 else "📉"
            sign = "+" if change >= 0 else ""
            change_str = f"\n{arrow} 漲跌：{sign}{change:.2f}（{sign}{change_pct:.2f}%）"
        except (ValueError, ZeroDivisionError):
            change_str = ""

    msg = (
        f"📊 {name}（{code}）\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 即時價格：{latest_price}\n"
        f"📖 開盤價：{open_price}\n"
        f"⬆️ 最高：{high}\n"
        f"⬇️ 最低：{low}\n"
        f"📦 成交量：{volume}"
        f"{change_str}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🕐 更新時間：{time_str}"
    )
    return msg


async def ai_analyze_stock(stock_id: str, stock_name: str, price_data: dict | None) -> str:
    """
    使用 Gemini AI 分析股票

    Args:
        stock_id: 股票代號
        stock_name: 股票名稱
        price_data: 即時報價資料（可選）

    Returns:
        AI 分析結果文字
    """
    # 組合 context 資訊
    context = f"股票代號：{stock_id}\n股票名稱：{stock_name}\n"

    if price_data and price_data.get("success"):
        realtime = price_data.get("realtime", {})
        context += (
            f"即時價格：{realtime.get('latest_trade_price', 'N/A')}\n"
            f"開盤價：{realtime.get('open', 'N/A')}\n"
            f"最高價：{realtime.get('high', 'N/A')}\n"
            f"最低價：{realtime.get('low', 'N/A')}\n"
            f"成交量：{realtime.get('accumulate_trade_volume', 'N/A')}\n"
        )

    prompt = f"""你是一位專業的台灣股票分析師。請根據以下股票資訊，提供簡短的分析建議。

{context}

請以繁體中文回覆，包含以下內容：
1. 📊 技術面簡析
2. 📋 基本面概述
3. 💡 投資建議

注意事項：
- 回覆控制在 300 字以內
- 請提醒投資人這只是 AI 分析，不構成投資建議
- 使用簡潔易懂的語言
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        result = f"🤖 AI 分析：{stock_name}（{stock_id}）\n"
        result += "━━━━━━━━━━━━━━━\n"
        result += response.text
        return result
    except Exception as e:
        logger.error(f"Gemini AI 分析失敗: {e}")
        return "⚠️ AI 分析暫時無法使用，請稍後再試。"


def log_query(user_id: str, stock_id: str, stock_name: str, query_type: str = "price"):
    """
    記錄使用者的查詢紀錄到資料庫

    Args:
        user_id: LINE 使用者 ID
        stock_id: 股票代號
        stock_name: 股票名稱
        query_type: 查詢類型（price / analysis）
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO query_log (user_id, stock_id, stock_name, query_type) VALUES (?, ?, ?, ?)",
            (user_id, stock_id, stock_name, query_type),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"記錄查詢紀錄失敗: {e}")


def add_to_watchlist(user_id: str, stock_id: str, stock_name: str) -> str:
    """
    將股票加入使用者的追蹤清單

    Args:
        user_id: LINE 使用者 ID
        stock_id: 股票代號
        stock_name: 股票名稱

    Returns:
        操作結果訊息
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO watchlist (user_id, stock_id, stock_name) VALUES (?, ?, ?)",
            (user_id, stock_id, stock_name),
        )
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return f"✅ 已將 {stock_name}（{stock_id}）加入追蹤清單！"
        else:
            conn.close()
            return f"ℹ️ {stock_name}（{stock_id}）已在追蹤清單中。"
    except Exception as e:
        logger.error(f"加入追蹤清單失敗: {e}")
        return "⚠️ 加入追蹤清單失敗，請稍後再試。"


def remove_from_watchlist(user_id: str, stock_id: str) -> str:
    """
    從使用者的追蹤清單移除股票

    Args:
        user_id: LINE 使用者 ID
        stock_id: 股票代號

    Returns:
        操作結果訊息
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM watchlist WHERE user_id = ? AND stock_id = ?",
            (user_id, stock_id),
        )
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return f"✅ 已將 {stock_id} 從追蹤清單移除。"
        else:
            conn.close()
            return f"ℹ️ {stock_id} 不在追蹤清單中。"
    except Exception as e:
        logger.error(f"移除追蹤清單失敗: {e}")
        return "⚠️ 移除追蹤清單失敗，請稍後再試。"


def get_watchlist(user_id: str) -> str:
    """
    取得使用者的追蹤清單

    Args:
        user_id: LINE 使用者 ID

    Returns:
        追蹤清單訊息
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT stock_id, stock_name, added_at FROM watchlist WHERE user_id = ? ORDER BY added_at DESC",
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "📋 你的追蹤清單是空的。\n\n輸入「追蹤 <股票代號>」來新增股票！"

        msg = "📋 我的追蹤清單\n━━━━━━━━━━━━━━━\n"
        for i, (sid, sname, added) in enumerate(rows, 1):
            msg += f"{i}. {sname}（{sid}）\n"
        msg += f"━━━━━━━━━━━━━━━\n共 {len(rows)} 檔股票"
        return msg

    except Exception as e:
        logger.error(f"取得追蹤清單失敗: {e}")
        return "⚠️ 無法取得追蹤清單，請稍後再試。"


def get_help_message() -> str:
    """回傳使用說明訊息"""
    return (
        "📖 股票小助手 使用說明\n"
        "━━━━━━━━━━━━━━━\n"
        "📊 查詢股價\n"
        "  → 查詢 2330\n"
        "  → 查詢 台積電\n"
        "\n"
        "🤖 AI 分析\n"
        "  → 分析 2330\n"
        "  → 分析 台積電\n"
        "\n"
        "⭐ 追蹤清單\n"
        "  → 追蹤 2330\n"
        "  → 取消追蹤 2330\n"
        "  → 我的清單\n"
        "\n"
        "❓ 其他\n"
        "  → 幫助 / help\n"
        "━━━━━━━━━━━━━━━\n"
        "💬 也可以直接輸入任何股票相關問題，\n"
        "AI 會盡力回答！"
    )


async def handle_general_chat(text: str) -> str:
    """
    處理一般對話，交給 Gemini 以股票助手角色回覆

    Args:
        text: 使用者輸入的文字

    Returns:
        AI 回覆文字
    """
    prompt = f"""你是一位友善的台灣股票小助手 LINE Bot。
使用者傳了以下訊息，請用繁體中文簡短回覆（200 字以內）。
如果是股票相關問題就回答，如果不是就友善地引導他使用股票功能。

使用者訊息：{text}

提示使用者可以輸入「幫助」查看所有功能。"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini 一般對話失敗: {e}")
        return "抱歉，我暫時無法回覆。請輸入「幫助」查看可用功能！"


# ========== LINE Webhook 路由 ==========

@app.post("/callback")
async def callback(request: Request):
    """LINE Webhook 接收端點"""
    # 取得簽名
    signature = request.headers.get("X-Line-Signature", "")

    # 取得請求 body
    body = await request.body()
    body_str = body.decode("utf-8")

    logger.info(f"收到 Webhook 請求")

    # 驗證簽名並處理事件
    try:
        handler.handle(body_str, signature)
    except InvalidSignatureError:
        logger.error("簽名驗證失敗")
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
async def handle_message(event: MessageEvent):
    """
    處理使用者傳送的文字訊息

    根據指令前綴分派到不同的處理函式：
    - 查詢 → 股價查詢
    - 分析 → AI 分析
    - 追蹤 → 加入追蹤清單
    - 取消追蹤 → 移除追蹤清單
    - 我的清單 → 顯示追蹤清單
    - 幫助/help → 使用說明
    - 其他 → 一般 AI 對話
    """
    user_id = event.source.user_id
    text = event.message.text.strip()

    logger.info(f"使用者 {user_id} 傳送：{text}")

    reply_text = ""

    # --- 查詢股價 ---
    if text.startswith("查詢"):
        keyword = text.replace("查詢", "").strip()
        if not keyword:
            reply_text = "請輸入股票代號或名稱，例如：查詢 2330"
        else:
            result = find_stock_id(keyword)
            if result:
                stock_id, stock_name = result
                price_data = get_realtime_price(stock_id)
                if price_data:
                    reply_text = format_stock_price(price_data)
                    log_query(user_id, stock_id, stock_name, "price")
                else:
                    reply_text = f"⚠️ 無法取得 {stock_name}（{stock_id}）的即時報價，可能非交易時段。"
            else:
                reply_text = f"❌ 找不到「{keyword}」對應的股票，請確認代號或名稱是否正確。"

    # --- AI 分析 ---
    elif text.startswith("分析"):
        keyword = text.replace("分析", "").strip()
        if not keyword:
            reply_text = "請輸入股票代號或名稱，例如：分析 2330"
        else:
            result = find_stock_id(keyword)
            if result:
                stock_id, stock_name = result
                price_data = get_realtime_price(stock_id)
                reply_text = await ai_analyze_stock(stock_id, stock_name, price_data)
                log_query(user_id, stock_id, stock_name, "analysis")
            else:
                reply_text = f"❌ 找不到「{keyword}」對應的股票，請確認代號或名稱是否正確。"

    # --- 取消追蹤（必須在「追蹤」之前判斷） ---
    elif text.startswith("取消追蹤"):
        keyword = text.replace("取消追蹤", "").strip()
        if not keyword:
            reply_text = "請輸入股票代號，例如：取消追蹤 2330"
        else:
            result = find_stock_id(keyword)
            if result:
                stock_id, stock_name = result
                reply_text = remove_from_watchlist(user_id, stock_id)
            else:
                reply_text = remove_from_watchlist(user_id, keyword)

    # --- 追蹤 ---
    elif text.startswith("追蹤"):
        keyword = text.replace("追蹤", "").strip()
        if not keyword:
            reply_text = "請輸入股票代號，例如：追蹤 2330"
        else:
            result = find_stock_id(keyword)
            if result:
                stock_id, stock_name = result
                reply_text = add_to_watchlist(user_id, stock_id, stock_name)
            else:
                reply_text = f"❌ 找不到「{keyword}」對應的股票，請確認代號或名稱是否正確。"

    # --- 我的清單 ---
    elif text in ["我的清單", "清單", "自選股"]:
        reply_text = get_watchlist(user_id)

    # --- 使用說明 ---
    elif text.lower() in ["幫助", "help", "說明", "指令"]:
        reply_text = get_help_message()

    # --- 一般對話（交給 Gemini） ---
    else:
        reply_text = await handle_general_chat(text)

    # 回覆訊息
    try:
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )
        logger.info(f"已回覆使用者 {user_id}")
    except Exception as e:
        logger.error(f"回覆訊息失敗: {e}")


# ========== 健康檢查 ==========

@app.get("/")
async def root():
    """健康檢查端點"""
    return {"status": "ok", "message": "股票小助手 LINE Bot 運行中 🚀"}
