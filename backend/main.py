import openai
from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = FastAPI()

# サーバー起動確認
@app.get("/")
async def read_root():
    return {"message": "LINE bot is running!"}

# LINEメッセージのリプライ関数
def reply_message(reply_token, text):
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': text}]
    }
    requests.post(url, headers=headers, json=data)

# OpenAIを使用して謎とヒントを生成する関数
def generate_riddle_and_hint():
    prompt = "面白い謎を出題して、簡単なヒントを提供してください。"
    response = openai.Completion.create(
        engine="gpt-4",  # GPT-4モデル
        prompt=prompt,
        max_tokens=150
    )
    result = response['choices'][0]['text'].strip()
    return result

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
