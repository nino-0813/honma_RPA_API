#!/bin/bash

# RPA APIサーバー起動スクリプト

cd "$(dirname "$0")"

echo "=========================================="
echo "RPA APIサーバーを起動します"
echo "=========================================="

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "仮想環境が見つかりません。作成します..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
echo "仮想環境をアクティベートしています..."
source venv/bin/activate

# 依存関係のインストール
echo "依存関係をインストールしています..."
pip install --upgrade pip
pip install -r requirements.txt

# .envファイルの確認
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️ 警告: .envファイルが見つかりません。"
    echo "以下の内容で.envファイルを作成してください："
    echo ""
    echo "SUPABASE_URL=https://your-project.supabase.co"
    echo "SUPABASE_KEY=your-supabase-anon-key"
    echo ""
    echo "続行しますか？ (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "セットアップを中止しました。"
        exit 1
    fi
fi

# ChromeDriverの確認
if ! command -v chromedriver &> /dev/null; then
    echo ""
    echo "⚠️ 警告: ChromeDriverが見つかりません。"
    echo "macOSの場合: brew install chromedriver"
    echo "または https://chromedriver.chromium.org/downloads からダウンロードしてください"
    echo ""
fi

# FastAPIサーバーを起動
echo ""
echo "=========================================="
echo "FastAPIサーバーを起動します..."
echo "URL: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "=========================================="
echo ""

uvicorn main:app --reload --port 8000 --host 0.0.0.0

