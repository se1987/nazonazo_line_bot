from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
import MeCab
import re

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='♦️♦️ %(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MeCabのインスタンス作成（辞書を指定）
mecab = MeCab.Tagger("-Ochasen")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 問題とその正解を保存する辞書
riddle_store = {}

# OpenAI APIを使って謎を生成する関数
def generate_riddle(difficulty, user_id):
    logger.debug(f"generate_riddle関数が呼び出されました")

    # 難易度に応じたプロンプトを作成
    prompt = f"""
    あなたは優れた創造力と論理的思考力を持ち、ユーモア溢れるなぞなぞクリエイターです。次のステップに従い、ユーザーに楽しさと驚きを与えるなぞなぞを作成してください。

    # お願い
    適切な難易度に応じたなぞなぞを一問生成してください。

    # 目的
    ユーザーに楽しさと驚きを与えるなぞなぞで楽しんでもらうため。

    # 情報
    - 今、ユーザーが選んだ難易度は「{difficulty}」です。難易度に応じて1問なぞなぞを作成し、答えも一緒に提供してください。難易度の種類は以下の３通りです。
        - 簡単: 簡単で直感的に解ける問題。
        - 普通: 少し考える必要がある問題。
        - 難しい: 深く考えさせる問題。

    ### 出題例
    #### 難易度が簡単の場合:
    1. 「お肉を焼くのが得意な数字ってなぁに？」
    - 答え: 「10」
    2. 「パンはパンでも食べられないパンは何？」
    - 答え: 「フライパン」
    3. 「お風呂に入ると小さくなっちゃうものは何？」
    - 答え: 「せっけん」

    #### 難易度が普通の場合:
    1. 「おしりに「う」をつけると少なくなっちゃう野菜は何？」
    - 答え: 「へちま」
    2. 「いろの中で　あいだに「の」を入れると　茶色に変わるものは？」
    - 答え: 「きいろ」
    3. 「【小〇　大〇　〇苗　納〇】〇に共通して入る漢字は何？」
    - 答え: 「豆」

    #### 難易度が難しいの場合:
    1. 「りんごの隣りにりんごをおくと２倍になります。あるものの隣りに同じあるものを置くと1000分の１になります。あるものって何？」
    - 答え: 「m」
    2. 「【あなたは天国に行けるかな？】天国に住む天使は正直者　地獄に住む悪魔は嘘つき　ただし見た目は全く同じ　さて天国と地獄の分かれ道　天使か悪魔かわからない一人が立っている　あなたは１つだけ質問ができる　なんと質問すれば天国へ行けるかな？」
    - 答え: 「あなたが住んでいる場所は　どっちにありますか？」
    3. 「風邪をひいた子どもとかけて　牧場の家畜とときます　そのこころは？」
    - 答え: 「はなたれています」

    # ルール:
    - 問題は150文字以内で簡単な文章にしてください。
    - ヒントは生成せずに、問題と回答だけを出力してください。

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
    あなたは優れた創造力と論理的思考力を持ち、ユーモア溢れるなぞなぞクリエイターです。
    今、ユーザーが選んだ難易度は「{difficulty}」です。
    以下の問題に対して、ヒントを生成してください。
    
    - 問題: {question}
    - 解答: {answer}

    ユーザーが「ヒント」を要求したので、次のフローに従いヒントを提供してください。

    - 問題「{question}」に応じたヒントを1つ提供してください。
    - ヒントは、{answer}を使わずに、解答の手がかりになるヒントを1つ生成してください。

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
            temperature=0.7, #調整必要
            max_tokens=50  # 生成されるテキストの最大トークン数
        )
        # 生成されたテキスト（ヒント）を返す
        return response.choices[0].message.content.strip()
    except Exception as e:
        # エラーが発生した場合はログを出力し、エラーメッセージを返す
        logger.error(f"ヒントの生成に失敗しました: {e}")
        return "ヒントの生成に失敗しました。"

# ユーザーの回答を形態素解析して正規化する関数
def normalize_answer_mecab(answer):
    # 形態素解析して単語ごとに分解
    node = mecab.parseToNode(answer)
    words = []
    while node:
        word = node.surface  # 分解された単語を取得
        words.append(word)
        node = node.next
    # 単語を繋げて一つの正規化された文字列を返す
    return ''.join(words).lower()

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


        # ユーザーの回答を形態素解析で正規化
        user_answer_normalized = normalize_answer_mecab(user_answer)
        logger.debug(f"clean_correct_answer:{user_answer_normalized}を取得しました")

        # 正解の答えも形態素解析で正規化
        correct_answer_normalized = normalize_answer_mecab(correct_answer)
        logger.debug(f"clean_correct_answer:{correct_answer_normalized}を取得しました")

        # # カギカッコを削除して比較 (大文字・小文字も無視)
        # clean_correct_answer = correct_answer.strip().replace("「", "").replace("」", "").lower()
        # logger.debug(f"clean_correct_answer:{clean_correct_answer}を取得しました")

        if user_answer_normalized.strip() == correct_answer_normalized:
            logger.debug(f"correct_answer:{user_answer.strip()}を取得しました")
            return "おめでとう！正解です！"
        elif user_answer.strip() == "降参":
            return f"正解は『{correct_answer_normalized}』でした！"
        else:
            return "残念！もう一度考えてみてください。"
    except Exception as e:
        logger.error(f"Failed to check answer: {e}")
        return "回答の確認中にエラーが発生しました。"

