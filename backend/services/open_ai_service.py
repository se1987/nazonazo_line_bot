import openai
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# OpenAIを使用して謎とヒントを生成する関数
def generate_riddle_and_hint():
    prompt = "面白い謎を出題して、簡単なヒントを提供してください。"
    response = openai.Completion.create(
        engine="gpt-4o-mini",
        prompt=prompt,
        max_tokens=150
    )
    result = response['choices'][0]['text'].strip()
    return result
