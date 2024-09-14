from fastapi import FastAPI, Request
from services.line_bot_service import send_start_message, handle_difficulty_selection, send_hint, reply_message
import os
import logging
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='♦️♦️ %(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# サーバー起動確認
@app.get("/")
async def read_root():
    return {"message": "LINE bot is running!"}

# Webhookのエンドポイント設定
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()  # リクエストのボディをJSON形式で取得
    events = body.get('events', [])  # イベント情報を取得
    
    # 各イベントを処理
    for event in events:
        if event['type'] == 'message' and event['message']['type'] == 'text':
            reply_token = event['replyToken']  # リプライするためのトークン
            user_message = event['message']['text']  # ユーザーからのメッセージを取得

            # 「謎謎出して」が送信された場合、難易度選択メッセージを表示
            if user_message == "謎謎出して":
                send_start_message(reply_token)
            # 難易度が選択された場合、対応する謎を出題
            elif user_message in ["簡単", "普通", "難しい"]:
                handle_difficulty_selection(reply_token, user_message)
            # ヒントが要求された場合、ヒントを表示
            elif user_message == "ヒント":
                send_hint(reply_token, user_message)
            else:
                # 回答メッセージが送信された場合、回答処理を行う
                reply_message(reply_token, "回答を入力してください。")

    return {"status": "ok"}