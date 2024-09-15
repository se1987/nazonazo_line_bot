import os
import logging
from dotenv import load_dotenv
from utils.open_ai_api import generate_hint
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

if LINE_CHANNEL_ACCESS_TOKEN is None:
    logger.error("LINE_CHANNEL_ACCESS_TOKENが読み込まれていません")
if LINE_CHANNEL_SECRET is None:
    logger.error("LINE_CHANNEL_SECRETが読み込まれていません")

try:
    # LINE Bot APIクライアントの初期化
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(LINE_CHANNEL_SECRET)
    logger.info(f"line_bot_api: {line_bot_api}")
    logger.info(f"handler: {handler}")
except Exception as e:
    logger.error(f"LINE Bot APIの初期化に失敗しました: {e}")

# 難易度選択ボタンを表示する関数
def send_difficulty_selection_message(reply_token):
    if line_bot_api is None:
        logger.error("LINE Bot APIが初期化されていません")
        return
    
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
