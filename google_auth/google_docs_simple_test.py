#!/usr/bin/env python3
"""
Google Docs API 簡易テスト
新しい認証情報でGoogle Docs APIアクセスを試行
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 設定
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google_docs_new_token.pickle'

def check_existing_auth():
    """既存の認証状況を確認"""
    print("📋 既存認証状況確認:")
    
    # credentials.json確認
    if os.path.exists(CREDENTIALS_FILE):
        print(f"✅ OAuth設定ファイル: {CREDENTIALS_FILE}")
        try:
            import json
            with open(CREDENTIALS_FILE, 'r') as f:
                creds_data = json.load(f)
                if 'installed' in creds_data:
                    print("   形式: デスクトップアプリケーション用OAuth")
                elif 'web' in creds_data:
                    print("   形式: Webアプリケーション用OAuth")
                else:
                    print("   形式: 不明")
        except Exception as e:
            print(f"   読み込みエラー: {e}")
    else:
        print(f"❌ OAuth設定ファイルなし: {CREDENTIALS_FILE}")
    
    # 既存トークン確認
    token_files = [
        '/home/fujinosuke/google/token_contacts_real.pickle',
        '/home/fujinosuke/google_docs_token.pickle',
        TOKEN_FILE
    ]
    
    for token_file in token_files:
        if os.path.exists(token_file):
            try:
                with open(token_file, 'rb') as f:
                    creds = pickle.load(f)
                    scopes = getattr(creds, 'scopes', ['スコープ不明'])
                    valid = creds.valid if hasattr(creds, 'valid') else '不明'
                    print(f"✅ トークンファイル: {token_file}")
                    print(f"   有効性: {valid}")
                    print(f"   スコープ: {scopes}")
            except Exception as e:
                print(f"❌ トークン読み込みエラー {token_file}: {e}")

def test_api_without_auth():
    """認証なしでAPIの基本情報を確認"""
    print("\n🔍 Google Docs API基本情報確認:")
    try:
        # APIが有効かどうかの簡易チェック
        from googleapiclient.discovery import build
        service = build('docs', 'v1', developerKey='dummy')  # ダミーキー
        print("✅ Google Docs APIライブラリは正常にインポート可能")
    except Exception as e:
        print(f"❌ APIライブラリエラー: {e}")

def create_auth_instructions():
    """認証設定手順を表示"""
    print("\n📝 Google Docs API認証設定手順:")
    print("=" * 50)
    print("1. Google Cloud Console (https://console.cloud.google.com) にアクセス")
    print("2. プロジェクトを選択または作成")
    print("3. 「APIs & Services」→ 「Library」")
    print("4. 「Google Docs API」を検索して有効化")
    print("5. 「Google Drive API」も有効化（必要）")
    print("6. 「APIs & Services」→ 「Credentials」")
    print("7. 「CREATE CREDENTIALS」→ 「OAuth 2.0 Client IDs」")
    print("8. Application type: 「Desktop application」")
    print("9. JSONファイルをダウンロード")
    print("10. ファイルを ~/google/credentials.json に配置")
    print("=" * 50)
    
    print("\n🔧 代替案 - サービスアカウント認証:")
    print("1. 「CREATE CREDENTIALS」→ 「Service account」")
    print("2. サービスアカウント作成")
    print("3. 「Keys」→ 「ADD KEY」→ 「Create new key」→ 「JSON」")
    print("4. JSONファイルを ~/google_docs_service_key.json に配置")
    print("5. サービスアカウント版スクリプトを使用")

def main():
    """メイン処理"""
    print("🚀 Google Docs API 環境確認")
    print("=" * 50)
    
    # 既存認証確認
    check_existing_auth()
    
    # API基本確認
    test_api_without_auth()
    
    # 設定手順表示
    create_auth_instructions()
    
    print("\n💡 次のステップ:")
    print("1. Google Cloud Consoleで適切な認証情報を設定")
    print("2. 認証ファイルをMacMini2014に配置")
    print("3. 認証付きテストスクリプトを実行")
    
    print("\n📁 現在の環境:")
    print(f"   作業ディレクトリ: {os.getcwd()}")
    print(f"   Python環境: Google Docs API仮想環境")
    print(f"   必要ライブラリ: インストール済み")

if __name__ == "__main__":
    main()