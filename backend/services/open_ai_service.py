from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
import random

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
    prompts = [
        # プロンプト1: 論理パズル
        f"""
        あなたは優れた論理的思考力を持つパズルクリエイターです。次のステップに従い、答えが１単語もしくは数字で表現される論理パズルを作成してください。ただし、答えは単なる計算ではなく、ステップごとの論理的な判断を伴う問題にしてください。

        # お願い
        - ユーザーが論理的な思考力を駆使し、複数のステップや選択肢を考える必要のある問題を作成してください。
        - 問題の答えは必ず１単語もしくは数字で表現できるようにし、移動や手順、順序を考える問題にしてください。
        - なぜそのような答えになるのか解説も提示してください。

        # 目的
        ユーザーが考える楽しみを感じ、論理的に考えるプロセスを楽しめるような問題を作成してください。パズルの解答に至るまでに、選択肢を考慮するステップが含まれるようにしてください。

        # 情報
        今、ユーザーが選んだ難易度は「{difficulty}」です。難易度に応じて、以下のようなパズル問題を作成し、答えも1つの単語もしくは数字で提供してください。

        - 簡単: 初心者向けのシンプルな問題
        - 普通: 中級者向けの少し難しい問題
        - 難しい: 上級者向けの複雑な問題

        # 出題例
        - 問題: 「やぎ、狼、キャベツ、人間を、2つまでしか乗せられない船で川を渡らせたい。船を漕げるのは人間のみで、狼とやぎを同時に残すと、やぎが食べられてしまう。やぎとキャベツを同時に残すと、キャベツが食べられてしまう。全員を無事に川の向こうへ運ぶための最小の移動回数は何回ですか？」
        - 答え: 7
        - 解説:
                この問題は「やぎ、狼、キャベツ問題」としてよく知られているパズルです。条件を守りながら全員を無事に川の向こう岸に運ぶための戦略を考える必要があります。ポイントは、やぎと狼、やぎとキャベツを一緒に残さないようにすることです。
                以下が解法の手順です。

                1. **最初の移動**: 人間はやぎを船に乗せて向こう岸に渡します。
                2. **戻り**: 人間だけが船でこちら岸に戻ります。
                3. **次の移動**: 人間は狼を船に乗せて向こう岸に渡します。
                4. **やぎを戻す**: 人間はやぎを船に乗せてこちら岸に戻ります。
                5. **キャベツを渡す**: 人間はキャベツを船に乗せて向こう岸に渡します。
                6. **戻り**: 人間だけが船でこちら岸に戻ります。
                7. **やぎを渡す**: 最後に人間はやぎを船に乗せて向こう岸に渡します。

                これで全員が無事に向こう岸に渡ることができ、最小の移動回数は**7回**となります。

        # ルール:
        - 問題は論理的なステップを必要とし、答えは必ず1つの単語もしくは数字で表現できるようにしてください。
        - 計算問題を出題することは控え、論理的思考力が必要な問題を生成してください。
        - 問題は500文字以内で簡潔に表現してください。
        - 問題の末尾に（ひらがなか数字で答えてね）という言葉を追加してください。
        - 答えが漢字の場合は、ひらがなに変換してください。

        # 出力
        出題は以下のフォーマットに従ってください：
        - 問題: xxx
        - 答え: yyy
        - 解説: zzz
        """,

        # プロンプト2: 言葉遊び
        f"""
        あなたは創造的な言葉遊びの達人です。次のステップに従い、答えが１単語で表現される言葉遊びの問題を作成してください。

        # お願い
        - ユーザーが言葉の多義性や音の類似性を活用して考える必要のある問題を作成してください。
        - 問題の答えは必ず１単語で表現できるようにしてください。
        - なぜそのような答えになるのか解説も提示してください。

        # 目的
        ユーザーが言葉の面白さや奥深さを感じ、創造的に考えるプロセスを楽しめるような問題を作成してください。

        # 情報
        今、ユーザーが選んだ難易度は「{difficulty}」です。難易度に応じて、以下のような言葉遊び問題を作成してください。

        - 簡単: 初心者向けのシンプルな言葉遊び
        - 普通: 中級者向けの少し複雑な言葉遊び
        - 難しい: 上級者向けの高度な言葉遊び

        # 出題例
        - 問題: 「海では泳いで空では飛ぶのはなーんだ？」
        - 答え: 「たこ」
        - 解説:  海の蛸と空を舞う凧

        # ルール:
        - 問題は言葉の創造的な解釈を必要とし、答えは必ず1つの単語で表現できるようにしてください。
        - 問題は100文字以内で簡潔に表現してください。
        - 答えが漢字の場合は、ひらがなに変換してください。

        # 出力
        出題は以下のフォーマットに従ってください：
        - 問題: xxx
        - 答え: yyy
        - 解説: zzz
        """,

        # プロンプト3: 共通漢字クイズ
        f"""
        あなたは言葉遊びの達人です。次のステップに従い、答えが漢字一文字で表現される共通点パズル問題を作成してください。

        # お願い
        - ユーザーが3〜4つの熟語に共通する文字を導き出す必要のある問題を作成してください。
        - 問題の答えは必ず漢字一文字で表現できるようにしてください。
        - 答えとなる文字は問題文中では〇で表示してください。

        # 情報
        今、ユーザーが選んだ難易度は「{difficulty}」です。難易度に応じて、以下のような状況推理問題を作成してください。

        - 簡単: 小学生でもわかる簡単な2字熟語の問題
        - 普通: 中学生向けの少し難しい2字熟語の問題
        - 難しい: 高校生向けの難しい2字熟語の問題

        # 出題例
        ## 1.
        - 問題「【小〇 大〇 〇苗 納〇】〇に共通して入る漢字一文字は何？」
        - 答え: 「豆」
        - 解説: 小豆（あずき）、大豆（だいず）、豆苗（とうみょう）、納豆（なっとう）

        # ルール:
        - 問題は、共通する漢字を含む3〜4つの二字熟語を表示し、必ず答えが漢字一文字で表現できるようにしてください。
        - 問題は50文字以内で簡潔に表現してください。
        - 答えとなる漢字は問題文中では〇で表示してください。

        # 出力
        出題は以下のフォーマットに従ってください：
        - 問題: xxx
        - 答え: yyy
        - 解説: zzz
        """,

        # プロンプト4: 虫食いクイズ
        f"""
        あなたは言葉遊びの達人です。次のステップに従い、答えがひらがな一文字で表現される穴埋め問題を作成してください。

        # お願い
        - ユーザーが1単語内のひらがな一文字を導き出す必要のある問題を作成してください。
        - 問題の答えは必ずひらがな一文字で表現できるようにしてください。
        - 答えとなる文字は問題文中では〇で表示してください。

        # 情報
        今、ユーザーが選んだ難易度は「{difficulty}」です。難易度に応じて、以下のような状況推理問題を作成してください。

        - 簡単: 小学生でもわかる言葉の問題
        - 普通: 中学生向けの少し難しい言葉の問題
        - 難しい: 高校生向けの難しい言葉の問題

        # 出題例
        - 問題「【か〇ら〇しゃ】〇に共通して入るひらがな一文字は何？」
        - 答え: 「ん」
        - 解説: かんらんしゃ

        # ルール:
        - 問題は1つの単語をひらがなで表示し、必ず答えがひらがな一文字で表現できるようにしてください。
        - 問題は50文字以内で簡潔に表現してください。
        - 答えとなるひらがな一文字は問題文中では〇で表示してください。
        - 答えとなるひらがな一文字が問題の中に複数ある場合は、それら全てを〇で表示してください。

        # 出力
        出題は以下のフォーマットに従ってください：
        - 問題: xxx
        - 答え: yyy
        - 解説: zzz
        """
    ]

    # ランダムにプロンプトを選択
    prompt = random.choice(prompts)
    logger.debug(f"選択されたプロンプト: {prompt[:50]}...")  # プロンプトの最初の50文字をログに記録

    try:
        logger.debug(f"generate_riddle関数が{difficulty}の謎の生成を開始しました")
        # GPT-4にリクエストを送信
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "あなたは優れた論理的思考力を持つパズルクリエイターです。"},
                {"role": "user","content": prompt,}
            ],
            model="gpt-4o-mini",  # GPT-4のモデルを指定
            max_tokens=500,  # 生成されるテキストの最大トークン数
            temperature=0.8,  # 調整必要
            top_p=0.9,
            n=1
        )
        # レスポンスを処理
        generated_text = response.choices[0].message.content.strip()
        logger.debug(f"generated_text:{generated_text}を生成しました")

        # 問題と答えをパース (問題部分と答え部分を分ける)
        # 問題と答えが正しいフォーマットで含まれているかを確認
        if "問題:" in generated_text and "答え:" in generated_text and "解説:" in generated_text:
            question, answer_part = generated_text.split("答え:", 1)
            answer, explanation = answer_part.split("解説:", 1)
            question = question.replace("問題:", "").strip()
            answer = answer.strip()
            logger.debug(f"question:{question}を生成しました")
            logger.debug(f"answer:{answer}を生成しました")
            logger.debug(f"explanation:{explanation}を生成しました")

            # 問題と答えをユーザーIDに紐づけて保存
            riddle_store[user_id] = {
                "question": question,
                "answer": answer,
                "explanation": explanation
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
    explanation = riddle["explanation"]
    logger.debug(f"question:{question},answer:{answer}を取得しました")

    # 難易度に応じたプロンプトを作成
    prompt = f"""
    以下の問題に対して、ヒントを生成してください。
    
    - 問題: {question}
    - 解答: {answer}
    - 解説: {explanation}

    # お願い
    ユーザーが「ヒント」を要求したので、次のフローに従いヒントを提供してください。

    # ルール
    - 問題「{question}」に応じたヒントを1つ提供してください。
    - ヒントは、{answer}という言葉は使わず、{explanation}に沿った内容から手掛かりになるヒントを生成してください。

    # 出力
    ヒントの出力は以下のフォーマットに従ってください：
    - 100文字以内の簡潔な文章で出力してください。
    """
    
    try:
        # GPT-4にリクエストを送信
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "あなたは優れた創造力と論理的思考力を持ち、ユーモア溢れるなぞなぞクリエイターです。"},
                {"role": "user","content": prompt,}
            ],
            model="gpt-4o-mini",  # GPT-4のモデルを指定
            max_tokens=100,  # 生成されるテキストの最大トークン数
            temperature=0.7, #調整必要
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

        # 解説を取得
        correct_explanation = riddle["explanation"]
        logger.debug(f"correct_answer:{correct_explanation}を取得しました")

        # カギカッコ、ハイフン、改行を削除し、大文字小文字を無視
        clean_correct_answer = (
            correct_answer.strip()
            .replace("「", "")
            .replace("」", "")
            .replace("-", "")
            .replace("\n", "")
            .replace("\r", "")
            .lower()
        )
        logger.debug(f"clean_correct_answer:{clean_correct_answer}を取得しました")

        if user_answer.strip() == clean_correct_answer:
            logger.debug(f"correct_answer:{user_answer.strip()}を取得しました")
            return f"おめでとう！正解です！"
        elif user_answer.strip() == "降参":
            return f"正解は『{clean_correct_answer}』でした！ \n解説: {correct_explanation}"
        else:
            return "残念！もう一度考えてみてください。"
    except Exception as e:
        logger.error(f"Failed to check answer: {e}")
        return "回答の確認中にエラーが発生しました。"

