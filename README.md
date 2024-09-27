# nazonazo_line_bot

![logo](https://github.com/user-attachments/assets/83bb9165-d0f6-40a5-8746-aa48c45b6876)

![image](https://img.shields.io/badge/Line-00C300?style=for-the-badge&logo=line&logoColor=white)
![image](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)
![image](https://img.shields.io/badge/ChatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
![image](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![image](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

## 概要

なぞなぞ（論理パズル）を出してくれる LINE bot です。
子どもたちが、遠出をするときの車中で手軽に遊べるように、作成しました。

## 機能

- スタートと送信する
- 難易度を選択（簡単・普通・難しい）
- AI が難易度に合わせたなぞなぞを一問出力
- ヒントと送信すると、ヒントが出る
- 回答を送信したら正解不正解の結果をフィードバック
- 「降参」と送信すると答えと解説が表示される

## 使用技術

- バックエンド: Python (FastAPI)
- 開発環境: Docker, GitHub
- デプロイ環境: Google Cloud Run
- 外部 API:
  - LINE Messaging API
  - OpenAI API (GPT-4o-mini モデルを使用)
