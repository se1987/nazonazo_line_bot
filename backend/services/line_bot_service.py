import os
import logging
from dotenv import load_dotenv
from services.open_ai_service import generate_riddle, generate_hint
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TemplateSendMessage, ButtonsTemplate, MessageAction,TextSendMessage

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='♦️♦️ %(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 環境変数からLINE APIのチャンネルトークンを取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET=os.getenv("LINE_CHANNEL_SECRET")

# LINE Bot APIクライアントの初期化
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# スタートメッセージを送信し、難易度選択ボタンを表示する関数
def send_start_message(reply_token):
    message = TemplateSendMessage(
        alt_text='難易度を選択してください',  # LINEがボタン表示をサポートしていない環境用の代替テキスト
        template=ButtonsTemplate(
            title='謎解きゲーム',  # メッセージのタイトル
            text='難易度を選択してください',  # メッセージの説明テキスト
            actions=[
                MessageAction(label='簡単', text='簡単'),  # 「簡単」ボタンが押されたときのアクション
                MessageAction(label='普通', text='普通'),  # 「普通」ボタンが押されたときのアクション
                MessageAction(label='難しい', text='難しい')  # 「難しい」ボタンが押されたときのアクション
            ]
        )
    )
    # LINE APIを使って、ユーザーにメッセージを返信
    line_bot_api.reply_message(reply_token, message)

# 難易度が選択された後に、対応する謎を出題し、ヒントボタンを表示する関数
def handle_difficulty_selection(reply_token, difficulty):
    riddle = generate_riddle(difficulty)  # 難易度に基づいた謎を生成
    # 謎をユーザーに送信
    line_bot_api.reply_message(reply_token, TextSendMessage(text=f"{difficulty}の謎: {riddle}"))

    # ヒントボタンをユーザーに表示
    hint_button = TemplateSendMessage(
        alt_text='ヒント',  # LINEがボタン表示をサポートしていない環境用の代替テキスト
        template=ButtonsTemplate(
            title='ヒントが必要ですか？',  # ボタンのタイトル
            text='ヒントが必要な場合は以下を押してください',  # ボタンの説明テキスト
            actions=[MessageAction(label='ヒント', text='ヒント')]  # 「ヒント」ボタンが押されたときのアクション
        )
    )
    # LINE APIを使ってヒントボタンを送信
    line_bot_api.push_message(reply_token, hint_button)

# ヒントボタンが押された際に、対応するヒントを表示する関数
def send_hint(reply_token, difficulty):
    hint = generate_hint(difficulty)  # 難易度に基づいたヒントを生成
    # ヒントをユーザーに送信
    line_bot_api.reply_message(reply_token, TextSendMessage(text=f"ヒント: {hint}"))

# LINEメッセージを送信する関数
def reply_message(reply_token, text):
    try:
        # テキストメッセージを作成
        message = TextSendMessage(text=text)
        # LINE APIにリプライメッセージを送信
        line_bot_api.reply_message(reply_token, message)
        logger.info("メッセージの送信に成功しました。")
    except Exception as e:
        logger.error(f"メッセージ送信に失敗しました: {e}")
