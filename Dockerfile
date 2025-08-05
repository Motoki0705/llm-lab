# =================================================================
# 1. ベースステージ (開発と本番で共通の環境)
# =================================================================
# NVIDIA公式のCUDA/cuDNNイメージをベースにする
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04 as base

# APT実行時の対話を無効化し、Python 3.11をインストール
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git \
    curl \
    gnupg \
    software-properties-common \
    python3.11 \
    python3-pip \
    python3.11-venv \
    && rm -rf /var/lib/apt/lists/* \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Node.jsのLTS版をインストール
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# 環境変数 (Poetry, pip, Hugging Face)
ENV POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=on \
    HF_HOME=/app/hf_cache

# Poetryのインストール
RUN pip install "poetry==$POETRY_VERSION"

# 作業ディレクトリとキャッシュディレクトリの作成
WORKDIR /app
RUN mkdir -p $HF_HOME


# =================================================================
# 2. 開発用ステージ (development)
# =================================================================
FROM base as development

# 依存関係ファイルを先にコピーしてキャッシュを活用
COPY poetry.lock pyproject.toml /app/

# 開発ツールも含め、すべての依存関係をインストール
RUN poetry install --no-interaction --no-ansi

# プロジェクトの全ファイルをコピー
COPY . /app/

# 開発時はJupyter Labを起動する（例）
EXPOSE 8888
CMD [ "poetry", "run", "jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--port=8888" ]


# =================================================================
# 3. 本番用ステージ (production)
# =================================================================
FROM base as production

# 依存関係ファイルを先にコピーしてキャッシュを活用
COPY poetry.lock pyproject.toml /app/

# 本番に必要なライブラリのみをインストール (--no-dev)
RUN poetry install --no-interaction --no-ansi --no-dev

# アプリケーションコードとモデルのみをコピー
COPY ./app /app/app/
COPY ./models /app/models/

# APIサーバーのポートを公開
EXPOSE 8000

# 本番時はAPIサーバーを起動する
CMD [ "poetry", "run", "python", "app/main.py" ]
