# LLM-jp-3.1-1.8b-instruct4 Docker環境

このリポジトリは、[LLM-jp-3.1-1.8b-instruct4](https://huggingface.co/llm-jp/llm-jp-3.1-1.8b-instruct4)モデルをDocker環境で簡単に実行するためのセットアップです。

## 📋 概要

LLM-jp-3.1-1.8b-instruct4は、国立情報学研究所の大規模言語モデル研究開発センターによって開発された日本語言語モデルです。このモデルは指示応答能力が強化されており、日本語での高品質な対話が可能です。

## 🚀 クイックスタート

### 必要な環境

- Docker
- Docker Compose（オプション）
- 推奨: NVIDIA GPU + nvidia-docker（GPU加速用）

### 1. リポジトリのクローン

```bash
git clone <このリポジトリのURL>
cd llm-jp-3.1-1.8b-instruct4-docker
```

### 2. 実行権限の付与

```bash
chmod +x run.sh
```

### 3. 実行

```bash
./run.sh
```

スクリプトが自動的に以下を実行します：
- Dockerイメージのビルド
- コンテナの起動
- Webサーバーの開始

### 4. アクセス

ブラウザで以下のURLにアクセスしてください：
```
http://localhost:8000
```

## 📁 ファイル構成

```
.
├── Dockerfile          # Docker環境の定義
├── app.py              # メインアプリケーション
├── requirements.txt    # Pythonライブラリの依存関係
├── run.sh             # 実行スクリプト
└── README.md          # このファイル
```

## 🖥️ 使用方法

### Web UI

1. ブラウザで `http://localhost:8000` にアクセス
2. テキストボックスに質問を入力
3. 「送信」ボタンをクリックまたはEnterキーを押す
4. モデルからの回答が表示されます

### API利用

POSTリクエストでプログラマティックに利用することも可能です：

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "自然言語処理とは何ですか？"}'
```

## ⚙️ 設定オプション

### GPU使用

NVIDIA GPUがある場合、自動的に検出してGPU加速が有効になります。手動でCPUモードで実行したい場合は、`run.sh`を編集してください。

### モデルパラメータの調整

`app.py`の以下の部分でモデルの生成パラメータを調整できます：

```python
output = self.model.generate(
    tokenized_input,
    max_new_tokens=100,        # 最大生成トークン数
    do_sample=True,           # サンプリングの有効/無効
    top_p=0.95,              # Top-p サンプリング
    temperature=0.7,          # 温度パラメータ
    repetition_penalty=1.05,  # 反復ペナルティ
)
```

## 🔧 トラブルシューティング

### コンテナが起動しない

```bash
# ログを確認
docker logs llm-jp-chat

# コンテナの状態を確認
docker ps -a
```

### メモリ不足エラー

1.8Bパラメータのモデルは約4-8GBのメモリを必要とします。利用可能なメモリを確認してください：

```bash
# システムメモリの確認
free -h

# GPUメモリの確認（GPU使用時）
nvidia-smi
```

### ポート競合

ポート8000が使用中の場合、`run.sh`と`Dockerfile`のポート設定を変更してください。

## 📊 システム要件

### 最小要件
- CPU: 4コア以上
- メモリ: 8GB以上
- ストレージ: 10GB以上の空き容量

### 推奨要件
- CPU: 8コア以上
- メモリ: 16GB以上
- GPU: NVIDIA GPU（4GB VRAM以上）
- ストレージ: 20GB以上の空き容量

## 🛠️ 開発

### カスタマイズ

`app.py`を編集してアプリケーションをカスタマイズできます：

- チャット履歴の保存
- 異なるプロンプトテンプレートの使用
- 複数の会話セッションのサポート
- REST APIの拡張

### 依存関係の更新

新しいライブラリを追加する場合は、`requirements.txt`を更新してから再ビルドしてください：

```bash
docker build -t llm-jp-3.1-1.8b-instruct4 .
```

## 📝 注意事項

1. **初回実行時**: モデルのダウンロードに時間がかかります（約3-4GB）
2. **ライセンス**: モデルのライセンスを確認してください
3. **商用利用**: 商用利用については元のモデルのライセンスを確認してください
4. **安全性**: このモデルは研究開発の初期段階であり、人間の意図や安全性の考慮に合わせて調整されていません

## 🔗 関連リンク

- [LLM-jp-3.1-1.8b-instruct4 モデルページ](https://huggingface.co/llm-jp/llm-jp-3.1-1.8b-instruct4)
- [LLM-jp プロジェクト](https://llm-jp.nii.ac.jp/)
- [国立情報学研究所](https://www.nii.ac.jp/)

## 🤝 コントリビューション

バグ報告や機能要求がある場合は、Issueを作成してください。プルリクエストも歓迎します。

## 📄 ライセンス

このDockerセットアップはMITライセンスの下で提供されます。ただし、使用するモデル（LLM-jp-3.1-1.8b-instruct4）には別のライセンスが適用される場合があります。

# local-llm

[![Release](https://img.shields.io/github/v/release/motoki/local-llm)](https://img.shields.io/github/v/release/motoki/local-llm)
[![Build status](https://img.shields.io/github/actions/workflow/status/motoki/local-llm/main.yml?branch=main)](https://github.com/motoki/local-llm/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/motoki/local-llm/branch/main/graph/badge.svg)](https://codecov.io/gh/motoki/local-llm)
[![Commit activity](https://img.shields.io/github/commit-activity/m/motoki/local-llm)](https://img.shields.io/github/commit-activity/m/motoki/local-llm)
[![License](https://img.shields.io/github/license/motoki/local-llm)](https://img.shields.io/github/license/motoki/local-llm)

This is a template repository for Python projects that use Poetry for their dependency management.

- **Github repository**: <https://github.com/motoki/local-llm/>
- **Documentation** <https://motoki.github.io/local-llm/>

## Getting started with your project

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:motoki/local-llm.git
git push -u origin main
```

Finally, install the environment and the pre-commit hooks with

```bash
make install
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPI or Artifactory, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
#
