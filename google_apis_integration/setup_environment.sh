#!/bin/bash

# Google 19 APIs接続システム - 環境自動セットアップスクリプト
# 作成日: 2025-12-15
# 目的: 依存関係の自動インストールと環境検証

echo "🚀 Google 19 APIs接続システム 環境セットアップ開始"
echo "=================================================="

# スクリプトディレクトリに移動
SCRIPT_DIR="/home/rootmax/03_google_19_apis_connection_system"
cd "$SCRIPT_DIR"

echo "📁 作業ディレクトリ: $SCRIPT_DIR"

# 仮想環境の確認・作成
if [ ! -d "venv" ]; then
    echo "🔧 仮想環境を作成中..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo "✅ 仮想環境作成完了"
    else
        echo "❌ 仮想環境作成失敗"
        exit 1
    fi
else
    echo "✅ 仮想環境確認済み"
fi

# 仮想環境アクティベート
echo "🔄 仮想環境アクティベート中..."
source venv/bin/activate

# pipアップデート
echo "📦 pip アップデート中..."
./venv/bin/python3 -m pip install --upgrade pip

# 依存関係インストール
echo "📦 依存関係インストール中..."
if [ -f "requirements.txt" ]; then
    ./venv/bin/python3 -m pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ 依存関係インストール完了"
    else
        echo "❌ 依存関係インストール失敗"
        exit 1
    fi
else
    echo "⚠️ requirements.txt が見つかりません。個別インストール実行..."
    ./venv/bin/python3 -m pip install google-api-python-client google-auth-oauthlib
fi

# インストール済みパッケージ確認
echo ""
echo "📋 インストール済みパッケージ確認:"
./venv/bin/python3 -m pip list | grep -E "(google|auth|api)"

# 認証ファイル確認
echo ""
echo "🔍 認証ファイル確認:"
if [ -f "01_authentication/credentials.json" ]; then
    echo "✅ credentials.json 存在"
else
    echo "❌ credentials.json が見つかりません"
fi

# トークンファイル確認
TOKEN_FILES=$(find 01_authentication/ -name "*token*.pickle" 2>/dev/null | wc -l)
if [ $TOKEN_FILES -gt 0 ]; then
    echo "✅ トークンファイル $TOKEN_FILES 個確認"
else
    echo "⚠️ トークンファイルが見つかりません"
fi

echo ""
echo "🎯 環境セットアップ完了"
echo "=================================================="
echo "📝 次のステップ:"
echo "   1. 認証システム実行: ./venv/bin/python3 auto_auth_system.py"
echo "   2. メインシステム実行: ./venv/bin/python3 main.py"
echo "   3. API直接テスト: ./venv/bin/python3 02_core_apis/test_19_google_apis.py"

echo ""
echo "🚨 注意事項:"
echo "   - WSL2環境では対話式認証に制限があります"
echo "   - ブラウザ認証が必要な場合は auto_auth_system.py のガイドに従ってください"
echo "   - 全ての認証が完了すると自動で19種類のAPIテストが実行されます"