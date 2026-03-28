# DeckCrew

複数の自律 AI DJ が議論・交渉しながら、リアルタイムに音楽を生成・変化させるアプリケーション。

## 前提ツール

- [Node.js](https://nodejs.org/) v22 以上
- [Python](https://www.python.org/) 3.12 以上
- [uv](https://docs.astral.sh/uv/)（Python パッケージマネージャ）

## セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/hryk224/DeckCrew.git
cd DeckCrew

# 環境変数をコピー
cp .env.example .env
# 必要に応じて .env を編集（下記「環境変数」を参照）

# フロントエンドの依存をインストール
cd frontend
npm install
cd ..

# バックエンドの依存をインストール
cd backend
uv sync --extra dev
cd ..
```

## 開発

各サービスを別のターミナルで起動する:

```bash
# ターミナル 1: フロントエンド (http://localhost:3000)
cd frontend
npm run dev

# ターミナル 2: バックエンド (http://localhost:8000)
cd backend
uv run uvicorn deckcrew.main:app --reload --port 8000 --env-file ../.env
```

dev server の停止（WSL2 では `Ctrl+C` で子プロセスが残る場合がある）:

```bash
# フロントエンド停止（next-server と子プロセスを停止）
pkill -f "next-server" 2>/dev/null; pkill -f "next dev" 2>/dev/null

# バックエンド停止
pkill -f "uvicorn" 2>/dev/null

# ポート解放の確認
lsof -i :3000 -t 2>/dev/null && echo "3000 使用中" || echo "3000 空き"
lsof -i :8000 -t 2>/dev/null && echo "8000 使用中" || echo "8000 空き"
```

または、dev 管理スクリプトを使用:

```bash
npm run dev:start    # 両サーバーを起動（PID を .dev-pids/ に保存）
npm run dev:stop     # 保存した PID で停止
npm run dev:restart  # 停止 → 起動
npm run dev:status   # 実行状態を表示
```

### デザイン確認

バックエンドなしで固定 UI 状態を確認:

```bash
npm run dev:start
npm run dev:preview              # 利用可能なシナリオ一覧
npm run dev:preview build-major  # preview URL を表示
# 表示された URL をブラウザで開く
npm run dev:stop
```

バックエンドの疎通確認:

```bash
curl http://localhost:8000/health
# => {"status":"ok"}
```

## 環境変数

`.env.example` で定義。開発開始前に `.env` へコピーすること。

### Google API キー

Google API キー 1 つで音楽生成（Lyria Realtime）と DJ エージェント LLM（Gemini）の両方が動作する。未設定の場合は mock モード（API 呼び出しなし）で動作する。

| 変数名           | デフォルト | 説明                                   |
| ---------------- | ---------- | -------------------------------------- |
| `GOOGLE_API_KEY` | (空)       | Google API キー（Lyria + Gemini 共用） |

### 音楽生成

| 変数名          | デフォルト                  | 説明                                                       |
| --------------- | --------------------------- | ---------------------------------------------------------- |
| `MUSIC_BACKEND` | `mock`                      | `mock`: ローカル開発用、`lyria`: Lyria Realtime API 使用時 |
| `LYRIA_MODEL`   | `models/lyria-realtime-exp` | 音楽生成モデル                                             |

### エージェント LLM（上級者向けオーバーライド）

デフォルトでは `GOOGLE_API_KEY` を使って Gemini で DJ エージェントが動作する。以下を設定すると別の LLM プロバイダを使用できる。

| 変数名           | デフォルト | 説明                                          |
| ---------------- | ---------- | --------------------------------------------- |
| `LLM_API_KEY`    | (空)       | オーバーライド用 API キー                     |
| `LLM_BASE_URL`   | (空)       | オーバーライド用ベース URL                    |
| `LLM_MODEL_NAME` | (空)       | オーバーライド用モデル名（例: `gpt-4o-mini`） |

### サーバー / フロントエンド

| 変数名                | デフォルト                                    | 説明                                 |
| --------------------- | --------------------------------------------- | ------------------------------------ |
| `BACKEND_PORT`        | `8000`                                        | バックエンドサーバーのポート         |
| `CORS_ORIGINS`        | `http://localhost:3000,http://localhost:3001` | 許可オリジン（デプロイ時は変更必須） |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000`                       | バックエンド API の URL              |

## 設定ファイル

| ファイル                 | 役割                                               |
| ------------------------ | -------------------------------------------------- |
| `.npmrc`                 | npm セキュリティ設定（save-exact, ignore-scripts） |
| `.env.example`           | 環境変数テンプレート                               |
| `frontend/package.json`  | フロントエンドの依存とスクリプト                   |
| `backend/pyproject.toml` | バックエンドの依存とツール設定                     |

## ディレクトリ構成

```
DeckCrew/
├── frontend/       # Next.js UI
├── backend/        # Python API・エージェント実行環境
│   ├── src/
│   │   └── deckcrew/
│   │       ├── api/            # REST + SSE エンドポイント
│   │       ├── agent/          # DJ エージェント定義・実行
│   │       ├── orchestrator/   # Conductor・ターン制御
│   │       ├── music/          # Lyria Realtime API 連携
│   │       └── state/          # セッション状態管理
│   └── tests/
└── shared/         # 共通契約・型定義の置き場
```

### frontend/

ユーザー向けの Next.js アプリケーション。
セッション状態、会議ログ、採用結果の表示、およびユーザー入力の受付を担当する。

### backend/

API エンドポイント、エージェント制御、音楽生成制御、セッション状態を担当する Python バックエンド。

| パッケージ      | 責務                                                          |
| --------------- | ------------------------------------------------------------- |
| `api/`          | HTTP エンドポイント（REST: コマンド、SSE: 状態配信）          |
| `agent/`        | DJ エージェントの役割定義・プロンプト・提案生成               |
| `orchestrator/` | Conductor: 提案収集・統合・採用決定                           |
| `music/`        | Lyria Realtime API ラッパー（モック切替可能な抽象化）         |
| `state/`        | インメモリのセッション状態: mood, bpm, energy, texture, focus |

### shared/

フロントエンドとバックエンド間で共有する契約・型定義・スキーマの置き場候補（例: SSE イベント型）。

> 現時点では空。境界をまたぐ契約が発生した時点で追加する。
