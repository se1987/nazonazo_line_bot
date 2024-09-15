from openai import OpenAI
import os
import logging
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='♦️♦️ %(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 問題とその正解を保存する辞書
riddle_store = {}

# OpenAI APIを使って謎を生成する関数
def generate_riddle(difficulty, user_id):
    logger.debug(f"generate_riddle関数が呼び出されました")

    # 難易度に応じたプロンプトを作成
    prompt = f"""
    あなたは、難易度に応じたなぞなぞを出題するプロフェッショナルです。
    今、ユーザーが選んだ難易度は「{difficulty}」です。
    ユーザーに次のフローに従い、なぞなぞを出題してください。

    - 難易度「{difficulty}」のなぞなぞを1問出題してください。
    - ユーザーが答えを入力し、正解かどうか判定できるように、答えも準備してください。

    ### 出題例
    - 簡単: 「パンはパンでも食べられないパンは何？」
    - 普通: 「歩くのに、足を使わないのは何？」
    - 難しい: 「目がたくさんあるのに、見ることができないものは何？」

    難易度に適したなぞなぞを生成してください。
    出題は以下のフォーマットに従ってください：
    - 問題: xxx
    - 答え: yyy
    """
    
    logger.debug(f"prompt:{prompt}")

    try:
        logger.debug(f"generate_riddle関数が{difficulty}の謎の生成を開始しました")
        # GPT-4にリクエストを送信
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o-mini",  # GPT-4のモデルを指定
            temperature=0.7,  # 調整必要
            max_tokens=150  # 生成されるテキストの最大トークン数
        )
        # レスポンスを処理
        generated_text = response.choices[0].message.content.strip()
        logger.debug(f"generated_text:{generated_text}を生成しました")

        # 問題と答えをパース (問題部分と答え部分を分ける)
        # 問題と答えが正しいフォーマットで含まれているかを確認
        if "問題:" in generated_text and "答え:" in generated_text:
            question, answer = generated_text.split("答え:")
            question = question.replace("問題:", "").strip()
            answer = answer.strip()
            logger.debug(f"question:{question}を生成しました")
            logger.debug(f"answer:{answer}を生成しました")

            # 問題と答えをユーザーIDに紐づけて保存
            riddle_store[user_id] = {
                "question": question,
                "answer": answer
            }

            logger.debug(f"riddle_storeに保存: {user_id} -> {riddle_store[user_id]}")
            return question
        else:
            # フォーマットが不正な場合のエラーハンドリング
            logger.error(f"謎の生成に失敗しました。フォーマットが正しくありません: {generated_text}")
            return "謎の生成に失敗しました。フォーマットが正しくありません。"

    except Exception as e:
        # エラーが発生した場合はログを出力し、エラーメッセージを返す
        logger.error(f"謎の生成に失敗しました: {e}")
        return "謎の生成に失敗しました。"
    
# OpenAI APIを使ってヒントを生成する関数
def generate_hint(difficulty):
    # 難易度に応じたプロンプトを作成
    prompt = f"""
    あなたは、難易度に応じたなぞなぞのヒントを提供するプロフェッショナルです。
    今、ユーザーが選んだ難易度は「{difficulty}」です。
    ユーザーが「ヒント」を要求したので、次のフローに従いヒントを提供してください。

    - 難易度「{difficulty}」に応じたヒントを1つ提供してください。
    - あまり答えに近づきすぎないが、解答の手がかりになるヒントを生成してください。

    ### 出題例
    - 簡単: 「料理に使います。」
    - 普通: 「とても遅い動きです。」
    - 難しい: 「人間ではありません。」
    """
    
    try:
        # GPT-4にリクエストを送信
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o-mini",  # GPT-4のモデルを指定
            temperature=0.7, #調整必要
            max_tokens=50  # 生成されるテキストの最大トークン数
        )
        # 生成されたテキスト（ヒント）を返す
        return response.choices[0].message.content.strip()
    except Exception as e:
        # エラーが発生した場合はログを出力し、エラーメッセージを返す
        logger.error(f"ヒントの生成に失敗しました: {e}")
        return "ヒントの生成に失敗しました。"

# ユーザーの回答を判定する関数
def check_user_answer(user_id, user_answer):
    logger.debug(f"check_user_answer関数が呼び出されました:{user_answer}と回答が送信されました")
    try:
        # ユーザーIDに紐づいた問題と答えを取得
        riddle = riddle_store.get(user_id)
        logger.debug(f"riddle:{riddle}を取得しました")
        if not riddle:
            return "まだ問題が出題されていません。"

        # 正解をチェック
        correct_answer = riddle["answer"]
        logger.debug(f"correct_answer:{correct_answer}を取得しました")
        if user_answer.strip() == correct_answer:
            logger.debug(f"correct_answer:{user_answer.strip()}を取得しました")
            return "おめでとう！正解です！"
        else:
            return "残念！もう一度考えてみてください。"
    except Exception as e:
        logger.error(f"Failed to check answer: {e}")
        return "回答の確認中にエラーが発生しました。"

