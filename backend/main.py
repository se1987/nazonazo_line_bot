from fastapi import FastAPI, Request
from services.line_bot_service import send_start_message, handle_difficulty_selection, send_hint, reply_message, send_difficulty_selection_message
from services.open_ai_service import check_user_answer
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
        if event['type'] == 'follow':  # ユーザーが初めて友だち追加した時
            user_id = event['source']['userId']
            send_start_message(user_id)

        elif event['type'] == 'message' and event['message']['type'] == 'text':
            user_id = event['source']['userId']  # LINEユーザーのIDを取得
            reply_token = event['replyToken']  # リプライするためのトークン
            user_message = event['message']['text']  # ユーザーからのメッセージを取得

            # 「スタート」メッセージが送信された場合、難易度選択ボタンを表示
            if user_message == "スタート":
                send_difficulty_selection_message(reply_token)
            # 難易度が選択された場合、対応する謎を出題
            elif user_message in ["簡単", "普通", "難しい"]:
                handle_difficulty_selection(reply_token, user_message, user_id)
            # ヒントが要求された場合、ヒントを表示
            elif user_message == "ヒント":
                send_hint(reply_token, user_message)
            else:
                # 「もう一度」が送信された場合、最初にスタートボタンを表示
                if user_message == "もう一度":
                    send_difficulty_selection_message(reply_token)
                else:
                    # 回答メッセージが送信された場合、回答処理を行う
                    result_message = check_user_answer(user_id, user_message)  # ユーザーIDに基づいて回答を判定
                    reply_message(reply_token, result_message)  # 判定結果を送信

    return {"status": "ok"}