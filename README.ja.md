# DeckCrew

複数の自律 AI DJ が議論・交渉しながら、リアルタイムに音楽を生成・変化させるアプリケーション。

## 特徴

- **AI DJ 会議** — 3 体の DJ エージェント（Groove / Harmony / Crowd）がリアルタイムで提案・議論・交渉して音楽の方向性を決定
- **Lyria Realtime** — Google の音楽生成 API がターンごとに進化するライブ音声をストリーミング
- **Critic & Audience** — 仮想の評価者とペルソナベースのリスナーがセットに反応し、判断に影響を与える

## クイックスタート

![Node.js](https://img.shields.io/badge/Node.js-22%2B-339933?logo=node.js&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9)

```bash
git clone https://github.com/hryk224/DeckCrew.git
cd DeckCrew

cp .env.example .env
# .env に GOOGLE_API_KEY を設定（Lyria 音楽生成と Gemini LLM の両方に使用）

cd frontend && npm install && cd ..
cd backend && uv sync && cd ..

npm run dev:start
# http://localhost:3000 を開く → ▶ Play
```

## 環境変数

`.env.example` を `.env` にコピーして使用。推奨設定に必要なキーは 1 つだけ:

**`GOOGLE_API_KEY`** — Lyria 音楽生成と Gemini LLM の両方に使用。

未設定の場合は mock モード（音声なし・ルールベースエージェント）で動作する。その他のオプションは `.env.example` を参照。

## 既知の制約

- **音声は単一クライアント** — 音声 WebSocket は 1 つのブラウザタブにストリーミングされる。複数タブでは音声チャンクが分割される。
- **認証なし** — Memory と Session API に認証レイヤーはない。ローカル単一ユーザー利用を前提としている。
- **mock モード** — `GOOGLE_API_KEY` 未設定時、エージェントはルールベースで音声は再生されない。
- **Lyria Realtime** — 実験的 API。アイドル時に接続が切れることがあるが、バックエンドが自動再接続する。
