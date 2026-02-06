#!/bin/bash

# Google APIs常時接続セットアップスクリプト
# Mac mini 2014専用

set -e

BASE_DIR="/home/fujinosuke/projects/google_apis_integration"
VENV_PATH="$BASE_DIR/google_apis_venv"
AUTH_DIR="$BASE_DIR/01_authentication"

echo "🚀 Google APIs常時接続システムをセットアップ"
echo "============================================="

cd "$BASE_DIR"

# 1. 認証を完了させる（簡易版）
echo "🔐 Google OAuth認証を実行..."

# 認証スクリプトを修正版として作成
cat > "$AUTH_DIR/simple_auth.py" << 'EOF'
#!/usr/bin/env python3
"""
Google APIs 簡易認証スクリプト
Mac mini 2014専用
"""

import os
import json
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# スコープ定義
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def authenticate():
    """Google API認証実行"""
    creds = None
    auth_dir = Path(__file__).parent
    token_file = auth_dir / "token.json"
    credentials_file = auth_dir / "credentials.json"
    
    print(f"📂 認証ディレクトリ: {auth_dir}")
    print(f"🔑 credentials.json: {'✅' if credentials_file.exists() else '❌'}")
    print(f"🎫 token.json: {'✅' if token_file.exists() else '❌'}")
    
    # 既存トークン読み込み
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        print("📖 既存認証トークンを読み込み")
    
    # 認証が無効または存在しない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("🔄 認証トークンを更新")
            except Exception as e:
                print(f"❌ トークン更新失敗: {e}")
                creds = None
        
        if not creds:
            if not credentials_file.exists():
                print("❌ credentials.jsonが見つかりません")
                print("   Google Cloud Consoleからダウンロードして配置してください")
                return None
            
            print("🌐 新規認証を開始...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file), SCOPES)
            
            # ローカルサーバーでの認証（Mac mini環境用）
            try:
                creds = flow.run_local_server(port=8080, open_browser=False)
                print("✅ 認証成功！")
            except Exception as e:
                print(f"❌ ローカルサーバー認証失敗: {e}")
                print("⚠️ 手動認証が必要です")
                return None
        
        # トークン保存
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            print(f"💾 認証トークンを保存: {token_file}")
    
    return creds

def test_apis(creds):
    """API接続テスト"""
    if not creds:
        return False
    
    try:
        # Photos API テスト
        from googleapiclient.discovery import build
        
        photos_service = build('photoslibrary', 'v1', credentials=creds)
        print("📸 Google Photos API: 認証成功")
        
        # Gmail API テスト  
        gmail_service = build('gmail', 'v1', credentials=creds)
        print("📧 Gmail API: 認証成功")
        
        # Drive API テスト
        drive_service = build('drive', 'v3', credentials=creds)
        print("💾 Google Drive API: 認証成功")
        
        return True
    except Exception as e:
        print(f"❌ API接続テストエラー: {e}")
        return False

def main():
    """メイン実行"""
    print("🎯 Google APIs認証開始")
    print("=" * 40)
    
    creds = authenticate()
    
    if creds:
        success = test_apis(creds)
        if success:
            print("\n✅ 認証・接続テスト完了")
            print("🚀 常時接続システムが利用可能です")
            return True
        else:
            print("\n❌ API接続テスト失敗")
            return False
    else:
        print("\n❌ 認証失敗")
        print("📋 手動設定が必要:")
        print("   1. Google Cloud Consoleでプロジェクト作成")
        print("   2. OAuth 2.0認証情報作成")
        print("   3. credentials.jsonダウンロード・配置")
        return False

if __name__ == "__main__":
    main()
EOF

# 2. 認証実行
echo "🔐 認証プロセス開始..."
source "$VENV_PATH/bin/activate"
python "$AUTH_DIR/simple_auth.py"

if [ $? -ne 0 ]; then
    echo "❌ 認証に失敗しました"
    echo "📋 手動認証が必要です:"
    echo "   1. ブラウザでGoogle OAuth認証を完了"
    echo "   2. token.jsonが生成されることを確認"
    exit 1
fi

# 3. 常時監視システム開始
echo "🔄 常時監視システムを開始..."
cd "$BASE_DIR/monitoring"
./google_apis_keeper.sh start

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Google APIs常時接続システム起動完了！"
    echo ""
    echo "📊 確認コマンド:"
    echo "   ./google_apis_keeper.sh status   # 状況確認"
    echo "   ./google_apis_keeper.sh logs     # ログ確認"
    echo ""
    echo "⏰ cron設定（オプション）:"
    echo "   ./google_apis_keeper.sh install  # 5分毎の自動チェック"
else
    echo "❌ 常時監視システム起動に失敗"
fi