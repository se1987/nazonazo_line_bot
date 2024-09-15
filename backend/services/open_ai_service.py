from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
from utils.line_message_api import handle_difficulty_selection_with_hint_button, send_start_message

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='♦️♦️ %(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 問題とその正解を保存する辞書
riddle_store = {}

# ユーザーの回答を判定する関数
def check_user_answer(user_id, user_answer, reply_token, user_message):
    try:
        # ユーザーIDに紐づいた問題と答えを取得
        riddle = riddle_store.get(user_id)
        if not riddle:
            return "まだ問題が出題されていません。"

        # 正解をチェック
        correct_answer = riddle["answer"]
        if user_answer.strip() == correct_answer:
            send_start_message(user_id)  # 正解時に次のメッセージを送信
            return "おめでとう！正解です！"
        else:
            handle_difficulty_selection_with_hint_button(reply_token, user_message, user_id)
            return "残念！もう一度考えてみてください。"
    except Exception as e:
        logger.error(f"Failed to check answer: {e}")
        return "回答の確認中にエラーが発生しました。"

