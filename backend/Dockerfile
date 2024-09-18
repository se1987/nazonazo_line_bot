# Pythonのベースイメージを指定
FROM python:3.10

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
