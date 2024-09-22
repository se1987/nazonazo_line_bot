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
    次のステップに従い、なぞなぞを作成してください。

    # お願い
    ユーザーが考える楽しみを感じられるよう、比喩的でクリエイティブな表現を使用して、簡単に答えが思い浮かばないような工夫をしてください。

    # 目的
    ユーザーに楽しさと驚きを与えるなぞなぞで、解くために発想を働かせる必要がある問題を作成してください。

    # 情報
    今、ユーザーが選んだ難易度は「{difficulty}」です。難易度に応じて1問なぞなぞを作成し、答えも一緒に提供してください。

    # ルール:
    - ヒントは生成せずに、問題と答えを出力してください。
    - 問題は150文字以内で簡単な文章にしてください。
    - 答えは1単語のみ出力し、ひらがなに変換してください。

    # 出力
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
                {"role": "system", "content": "あなたは優れた創造力と論理的思考力を持ち、ユーモア溢れるなぞなぞクリエイターです。"},
                {"role": "user","content": prompt,}
            ],
            model="gpt-4o-mini",  # GPT-4のモデルを指定
            max_tokens=150,  # 生成されるテキストの最大トークン数
            temperature=0.85,  # 調整必要
            top_p=0.9,
            n=1
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
def generate_hint(difficulty, user_id):
    logger.debug(f"generate_hint関数が呼び出されました")

    # ユーザーIDに紐づいた問題と答えを取得
    riddle = riddle_store.get(user_id)
    # 問題が存在しない場合の処理
    if not riddle:
        logger.error(f"ユーザーID: {user_id} に対する問題が見つかりません")
        return "まだ問題が出題されていません。"

    logger.debug(f"riddle:{riddle}を取得しました")
    question = riddle["question"]
    answer = riddle["answer"]
    logger.debug(f"question:{question},answer:{answer}を取得しました")

    # 難易度に応じたプロンプトを作成
    prompt = f"""
    以下の問題に対して、ヒントを生成してください。
    
    - 問題: {question}
    - 解答: {answer}

    # お願い
    ユーザーが「ヒント」を要求したので、次のフローに従いヒントを提供してください。

    # ルール
    - 問題「{question}」に応じたヒントを1つ提供してください。
    - ヒントは、{answer}という言葉は使わずに、{answer}の手がかりになるヒントを1つ生成してください。

    # 出力
    ヒントの出力は以下のフォーマットに従ってください：
    - 50文字以内の簡潔な文章で出力してください。
    """
    
    try:
        # GPT-4にリクエストを送信
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "あなたは優れた創造力と論理的思考力を持ち、ユーモア溢れるなぞなぞクリエイターです。"},
                {"role": "user","content": prompt,}
            ],
            model="gpt-4o-mini",  # GPT-4のモデルを指定
            max_tokens=50,  # 生成されるテキストの最大トークン数
            temperature=0.65, #調整必要
            top_p=0.9,
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

        # カギカッコを削除して比較 (大文字・小文字も無視)
        clean_correct_answer = correct_answer.strip().replace("「", "").replace("」", "").lower()
        logger.debug(f"clean_correct_answer:{clean_correct_answer}を取得しました")

        if user_answer.strip() == clean_correct_answer:
            logger.debug(f"correct_answer:{user_answer.strip()}を取得しました")
            return "おめでとう！正解です！"
        elif user_answer.strip() == "降参":
            return f"正解は『{clean_correct_answer}』でした！"
        else:
            return "残念！もう一度考えてみてください。"
    except Exception as e:
        logger.error(f"Failed to check answer: {e}")
        return "回答の確認中にエラーが発生しました。"

