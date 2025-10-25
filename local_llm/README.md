# Local LLM Chat UI

`local_llm` には、Ollama を利用したローカル LLM チャットのバックエンドとフロントエンドを収録しています。FastAPI (port 8000) と React (port 5173) を組み合わせ、ユーザーの入力に対してストリーミング表示で応答を返します。

## バックエンド (FastAPI)

- モジュール: `local_llm.backend`
- 起動方法: `python3 -m local_llm.backend`
- 使用ポート: `8000`
- 使用する環境変数
  - `OLLAMA_URL` (デフォルト: `http://127.0.0.1:11434`)
  - `OLLAMA_MODEL` (デフォルト: `llama3`)
- 主なエンドポイント
  - `POST /api/session` セッションを新規作成または再利用
  - `GET /api/session/{session_id}` セッション履歴の取得
  - `POST /api/chat` チャットの送信。テキストをストリーミングで返却

## フロントエンド (React + Vite)

- ディレクトリ: `local_llm/frontend`
- 使用ポート: `5173`
- セットアップ

```bash
cd local_llm/frontend
npm install
npm run dev
```

Vite の開発サーバーはバックエンドの `/api` を `http://localhost:8000` にプロキシするよう設定済みです。

## 使い方

1. Ollama サーバーを起動し、使用したいモデルを `OLLAMA_MODEL` に設定します。
2. 別ターミナルでバックエンドを起動: `python3 -m local_llm.backend`
3. フロントエンドで `npm run dev` を実行し、ブラウザで `http://localhost:5173` にアクセスします。
4. 入力欄にメッセージを入力し送信すると、応答がトークン単位でストリーミング表示されます。

