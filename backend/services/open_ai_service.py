import openai
import os
import logging
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='♦️♦️ %(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# OpenAI APIを使って謎を生成する関数
def generate_riddle(difficulty):
    # プロンプトを作成
    prompt = f"Generate a {difficulty} level riddle for a quiz game."
    
    try:
        # GPT-4にリクエストを送信
        response = openai.Completion.create(
            model="gpt-4o-mini",  # GPT-4のモデルを指定
            prompt=prompt,
            max_tokens=100  # 生成されるテキストの最大トークン数
        )
        # 生成されたテキスト（謎）を返す
        return response.choices[0].text.strip()
    except Exception as e:
        # エラーが発生した場合はログを出力し、エラーメッセージを返す
        logger.error(f"Failed to generate riddle: {e}")
        return "謎の生成に失敗しました。"
        
# OpenAI APIを使ってヒントを生成する関数
def generate_hint(difficulty):
    # プロンプトを作成
    prompt = f"Generate a hint for a {difficulty} level riddle in a quiz game."
    
    try:
        # GPT-4にリクエストを送信
        response = openai.Completion.create(
            model="gpt-4o-mini",  # GPT-4のモデルを指定
            prompt=prompt,
            max_tokens=50  # 生成されるテキストの最大トークン数
        )
        # 生成されたテキスト（ヒント）を返す
        return response.choices[0].text.strip()
    except Exception as e:
        # エラーが発生した場合はログを出力し、エラーメッセージを返す
        logger.error(f"Failed to generate hint: {e}")
        return "ヒントの生成に失敗しました。"
    