#\!/bin/bash

# Mac mini 2014 Google APIs統合起動スクリプト
# 作成日: 2025-12-15

echo "🚀 Mac mini Google APIs システム起動"
echo "======================================="

# 作業ディレクトリに移動
cd /home/fujinosuke/projects/google_apis_integration

# 仮想環境アクティベート
echo "🔧 Python仮想環境をアクティベート..."
source google_apis_venv/bin/activate

if [ $? -eq 0 ]; then
    echo "✅ 仮想環境アクティベート成功"
else
    echo "❌ 仮想環境アクティベート失敗"
    exit 1
fi

# 基本テスト実行
echo "🧪 Google APIs接続テスト実行..."
python google_apis_test.py

if [ $? -eq 0 ]; then
    echo "✅ Google APIs接続テスト: 成功"
    echo "💡 Google APIs接続システムが利用可能です"
    echo ""
    echo "📋 利用可能なコマンド:"
    echo "   python google_apis_test.py - 接続テスト"
    echo "   python main.py - メインシステム起動"
    echo ""
    echo "📁 プロジェクトディレクトリ: /home/fujinosuke/projects/google_apis_integration"
    echo "🌐 仮想環境: google_apis_venv"
else
    echo "❌ Google APIs接続テスト: 失敗" 
    echo "🔧 設定を確認してください"
    exit 1
fi

echo "🎉 Google APIs システム準備完了！"
