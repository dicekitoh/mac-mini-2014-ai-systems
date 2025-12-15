#\!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google APIs接続テストスクリプト (Mac mini 2014版)
簡単なGoogle APIs接続確認
"""

import os
import sys
import json
from pathlib import Path

def check_credentials():
    """認証情報の確認"""
    print("🔐 Google APIs認証情報確認")
    print("=" * 50)
    
    credentials_path = "01_authentication/credentials.json"
    if os.path.exists(credentials_path):
        print("✅ credentials.json 確認済み")
        try:
            with open(credentials_path, 'r') as f:
                creds = json.load(f)
                if 'installed' in creds:
                    print(f"  📋 プロジェクトID: {creds['installed'].get('project_id', 'N/A')}")
                    print(f"  🔑 クライアントID: {creds['installed'].get('client_id', 'N/A')[:20]}...")
                    print("✅ 認証情報形式: 正常")
                else:
                    print("⚠️ 認証情報形式が不正です")
            return True
        except Exception as e:
            print(f"❌ 認証情報読み込みエラー: {e}")
            return False
    else:
        print("❌ credentials.json が見つかりません")
        return False

def check_google_apis():
    """Google APIライブラリの確認"""
    print("\n📚 Google APIライブラリ確認")
    print("=" * 50)
    
    libraries = [
        ("google.auth", "Google認証"),
        ("google.oauth2", "OAuth2認証"), 
        ("googleapiclient", "Google APIクライアント"),
        ("google_auth_oauthlib", "OAuth認証ヘルパー")
    ]
    
    all_installed = True
    for lib, desc in libraries:
        try:
            __import__(lib)
            print(f"✅ {lib} - {desc}")
        except ImportError:
            print(f"❌ {lib} - {desc} (未インストール)")
            all_installed = False
    
    return all_installed

def test_basic_auth():
    """基本的な認証テスト"""
    print("\n🧪 基本認証テスト")
    print("=" * 50)
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        print("✅ Google認証ライブラリ: 正常")
        
        # スコープ定義
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/calendar.readonly'
        ]
        
        print(f"🎯 テスト用スコープ: {len(SCOPES)}個設定")
        print("  - Gmail読み取り権限")
        print("  - Calendar読み取り権限")
        
        # 認証フロー作成テスト
        flow = InstalledAppFlow.from_client_secrets_file(
            "01_authentication/credentials.json", SCOPES
        )
        print("✅ 認証フロー作成: 成功")
        print("💡 実際の認証には手動でブラウザアクセスが必要です")
        
        return True
        
    except Exception as e:
        print(f"❌ 認証テストエラー: {e}")
        return False

def main():
    """メイン実行"""
    print("🚀 Mac mini 2014 - Google APIs接続テスト")
    print("=" * 60)
    print(f"📅 実行日時: Mon Dec 15 13:22:03 JST 2025")
    print(f"💻 実行環境: Mac mini 2014 (Ubuntu)")
    print()
    
    # 1. 認証情報確認
    creds_ok = check_credentials()
    
    # 2. ライブラリ確認  
    libs_ok = check_google_apis()
    
    # 3. 基本認証テスト
    auth_ok = test_basic_auth()
    
    # 結果サマリー
    print("\n📊 テスト結果サマリー")
    print("=" * 50)
    print(f"🔐 認証情報: {'✅ OK' if creds_ok else '❌ NG'}")
    print(f"📚 ライブラリ: {'✅ OK' if libs_ok else '❌ NG'}") 
    print(f"🧪 認証テスト: {'✅ OK' if auth_ok else '❌ NG'}")
    
    if all([creds_ok, libs_ok, auth_ok]):
        print("\n🎉 Google APIs接続準備完了！")
        print("💡 次のステップ: 実際のAPI呼び出しテスト")
        return True
    else:
        print("\n⚠️ いくつかの問題があります")
        print("🔧 上記のエラーを修正してから再実行してください")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
