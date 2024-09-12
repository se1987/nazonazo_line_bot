from fastapi import FastAPI, Request
from backend.services.line_bot_service import reply_message
from backend.services.open_ai_service import generate_riddle_and_hint
import os
import logging
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# サーバー起動確認
@app.get("/")
async def read_root():
    return {"message": "LINE bot is running!"}

# LINE Webhookエンドポイント
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get('events', [])
    
    for event in events:
        if event['type'] == 'message' and event['message']['type'] == 'text':
            reply_token = event['replyToken']
            user_message = event['message']['text']

            if user_message == "謎謎出して":
                riddle_and_hint = generate_riddle_and_hint()  # 謎とヒントを生成
                reply_message(reply_token, f"問題とヒント: {riddle_and_hint}")
            else:
                reply_message(reply_token, "回答を入力してください。")

    return {"status": "ok"}
