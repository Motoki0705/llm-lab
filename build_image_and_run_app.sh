#!/bin/bash

# LLM-jp-3.1-1.8b-instruct4 実行スクリプト

set -e

# 色付きの出力用関数
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

# Dockerがインストールされているかチェック
if ! command -v docker &> /dev/null; then
    print_error "Dockerがインストールされていません。"
    print_info "Dockerをインストールしてから再度実行してください。"
    exit 1
fi

# Dockerが実行中かチェック
if ! docker info &> /dev/null; then
    print_error "Dockerデーモンが実行されていません。"
    print_info "Dockerを起動してから再度実行してください。"
    exit 1
fi

# イメージ名とコンテナ名
IMAGE_NAME="llm-jp-3.1-1.8b-instruct4"
CONTAINER_NAME="llm-jp-chat"

print_info "LLM-jp-3.1-1.8b-instruct4 Docker環境を構築・実行します"

# 既存のコンテナが実行中の場合は停止
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    print_info "既存のコンテナを停止します..."
    docker stop "$CONTAINER_NAME"
fi

# 既存のコンテナを削除
if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
    print_info "既存のコンテナを削除します..."
    docker rm "$CONTAINER_NAME"
fi

# Dockerイメージをビルド
print_info "Dockerイメージをビルドします..."
docker build -t "$IMAGE_NAME" .

if [ $? -ne 0 ]; then
    print_error "Dockerイメージのビルドに失敗しました"
    exit 1
fi

print_success "Dockerイメージのビルドが完了しました"

# GPUサポートの確認
GPU_ARGS=""
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    print_info "NVIDIA GPUが検出されました。GPU サポートを有効にします。"
    if docker info 2>/dev/null | grep -q "nvidia"; then
        GPU_ARGS="--gpus all"
    else
        print_info "nvidia-docker が設定されていない可能性があります。CPUモードで実行します。"
    fi
else
    print_info "GPUが検出されませんでした。CPUモードで実行します。"
fi

# コンテナを実行
print_info "コンテナを起動します..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p 8000:8000 \
    $GPU_ARGS \
    --restart unless-stopped \
    "$IMAGE_NAME"

if [ $? -ne 0 ]; then
    print_error "コンテナの起動に失敗しました"
    exit 1
fi

print_success "コンテナが正常に起動しました"

# 起動完了を待つ
print_info "サーバーの起動を待っています..."
for i in {1..30}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        break
    fi
    sleep 2
done

# 最終確認
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    print_success "サーバーが正常に起動しました！"
    print_info "以下のURLでアクセスできます:"
    echo "  http://localhost:8000"
    echo ""
    print_info "コンテナのログを確認するには:"
    echo "  docker logs $CONTAINER_NAME"
    echo ""
    print_info "コンテナを停止するには:"
    echo "  docker stop $CONTAINER_NAME"
else
    print_error "サーバーの起動に失敗しました"
    print_info "ログを確認してください:"
    echo "  docker logs $CONTAINER_NAME"
    exit 1
fi