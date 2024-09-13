import os
import logging
from dotenv import load_dotenv
import requests


# 環境変数の読み込み
load_dotenv()

# ロギングの設定
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

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
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        logger.error(f"Failed to reply message: {response.status_code}, {response.text}")
    else:
        logger.info("Successfully replied message")