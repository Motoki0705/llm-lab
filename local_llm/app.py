#!/usr/bin/env python3
"""
LLM-jp-3.1-1.8b-instruct4 モデルを使用したチャットアプリケーション
"""

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatHandler(BaseHTTPRequestHandler):
    def __init__(self, *args: Any, model: AutoModelForCausalLM, tokenizer: AutoTokenizer, **kwargs: Any) -> None:
        self.model = model
        self.tokenizer = tokenizer
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        """GETリクエストの処理(シンプルなWebUI)"""
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>LLM-jp-3.1-1.8b-instruct4 Chat</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
                    .user-message { background-color: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 5px; }
                    .bot-message { background-color: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 5px; }
                    input[type="text"] { width: 70%; padding: 10px; }
                    button { padding: 10px 20px; margin-left: 10px; }
                </style>
            </head>
            <body>
                <h1>LLM-jp-3.1-1.8b-instruct4 Chat</h1>
                <div id="chat-container" class="chat-container"></div>
                <input type="text" id="user-input" placeholder="質問を入力してください..." onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">送信</button>

                <script>
                    function sendMessage() {
                        const input = document.getElementById('user-input');
                        const message = input.value.trim();
                        if (!message) return;

                        const container = document.getElementById('chat-container');
                        container.innerHTML += '<div class="user-message"><strong>あなた:</strong> ' + message + '</div>';

                        fetch('/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({message: message})
                        })
                        .then(response => response.json())
                        .then(data => {
                            container.innerHTML += '<div class="bot-message"><strong>Bot:</strong> ' + data.response + '</div>';
                            container.scrollTop = container.scrollHeight;
                        })
                        .catch(error => {
                            container.innerHTML += '<div class="bot-message"><strong>Error:</strong> ' + error + '</div>';
                        });

                        input.value = '';
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        """POSTリクエストの処理(チャット機能)"""
        if self.path == "/chat":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode("utf-8"))
                user_message = data.get("message", "")

                if not user_message:
                    self.send_error(400, "メッセージが空です")
                    return

                # チャット形式でメッセージを構築
                chat = [
                    {
                        "role": "system",
                        "content": "以下は、タスクを説明する指示です。要求を適切に満たす応答を書きなさい。",
                    },
                    {"role": "user", "content": user_message},
                ]

                # トークナイズと生成
                tokenized_input = self.tokenizer.apply_chat_template(
                    chat, add_generation_prompt=True, tokenize=True, return_tensors="pt"
                ).to(self.model.device)

                with torch.no_grad():
                    output = self.model.generate(
                        tokenized_input,
                        max_new_tokens=100,
                        do_sample=True,
                        top_p=0.95,
                        temperature=0.7,
                        repetition_penalty=1.05,
                    )[0]

                # レスポンスをデコード
                full_response = self.tokenizer.decode(output, skip_special_tokens=True)

                # ユーザーの入力部分を除去して、モデルの返答のみを抽出
                response_start = full_response.find("assistant\n\n") + len("assistant\n\n")
                if response_start > len("assistant\n\n") - 1:
                    bot_response = full_response[response_start:].strip()
                else:
                    bot_response = full_response.strip()

                # JSON形式でレスポンスを返す
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()

                response_data = {"response": bot_response}
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))

            except Exception as e:
                logger.exception("エラーが発生しました。")
                self.send_error(500, f"内部サーバーエラー: {e!s}")
        else:
            self.send_error(404)


def load_model() -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """モデルとトークナイザーを読み込む"""
    logger.info("モデルとトークナイザーを読み込み中...")

    model_name = "llm-jp/llm-jp-3.1-1.8b-instruct4"

    # トークナイザーの読み込み
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # モデルの読み込み
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.bfloat16)

    logger.info("モデルとトークナイザーの読み込みが完了しました")
    return model, tokenizer


def main() -> None:
    """メイン関数"""
    logger.info("LLM-jp-3.1-1.8b-instruct4 チャットサーバーを開始します...")

    # モデルとトークナイザーを読み込み
    model, tokenizer = load_model()

    # HTTPサーバーを開始
    def handler(*args: Any, **kwargs: Any) -> None:
        ChatHandler(*args, model=model, tokenizer=tokenizer, **kwargs)

    server = HTTPServer(("127.0.0.1", 8000), handler)
    logger.info("サーバーがポート8000で開始されました")
    logger.info("http://localhost:8000 にアクセスしてください")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("サーバーを停止します...")
        server.shutdown()


if __name__ == "__main__":
    main()
