# Pythonのベースイメージを指定
FROM python:3.10

# 必要なパッケージのインストール（mecabとmecab-ipadicの依存関係を追加）
RUN apt-get update && apt-get install -y \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    && apt-get clean

# 作業ディレクトリを設定
WORKDIR /app

# PYTHONPATH 環境変数を設定
ENV PYTHONPATH=/app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# ポートを指定
EXPOSE 8000

# アプリケーションを起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
