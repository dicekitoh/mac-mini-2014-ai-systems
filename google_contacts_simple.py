#\!/usr/bin/env python3
"""
Google Contacts API 簡易接続システム
iPhone(Termius)対応版
"""

import sys
import json
import pickle
import os
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def load_credentials():
    """認証情報を読み込み"""
    token_file = "/home/fujinosuke/unified_oauth_token_new.pickle"
    
    if not os.path.exists(token_file):
        print("❌ 認証ファイルが見つかりません")
        return None
    
    try:
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
        
        # 認証が有効かチェック
        if creds and creds.valid:
            print("✅ 認証情報有効")
            return creds
        elif creds and creds.expired and creds.refresh_token:
            print("🔄 認証トークンをリフレッシュ中...")
            creds.refresh(Request())
            
            # 更新された認証情報を保存
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)
            
            print("✅ 認証トークンリフレッシュ成功")
            return creds
        else:
            print("❌ 認証情報が無効です")
            return None
            
    except Exception as e:
        print(f"❌ 認証エラー: {str(e)}")
        return None

def search_contacts(service, query):
    """連絡先検索"""
    try:
        # 連絡先取得
        results = service.people().connections().list(
            resourceName="people/me",
            pageSize=100,
            personFields="names,emailAddresses,phoneNumbers"
        ).execute()
        
        connections = results.get("connections", [])
        
        if not connections:
            print("📞 連絡先が見つかりませんでした")
            return
        
        print(f"📊 総連絡先数: {len(connections)}件")
        
        # 検索実行
        matches = []
        for person in connections:
            names = person.get("names", [])
            if names:
                display_name = names[0].get("'displayName'", "")
                if query.lower() in display_name.lower():
                    matches.append(person)
        
        print(f"🔍 検索結果: {len(matches)}件")
        
        # 結果表示
        for i, person in enumerate(matches[:10], 1):
            print(f"\n--- 連絡先 {i} ---")
            
            # 名前
            names = person.get("names", [])
            if names:
                print(f"名前: {names[0].get('displayName', N/A)}")
            
            # メールアドレス
            emails = person.get("emailAddresses", [])
            if emails:
                for email in emails[:2]:
                    print(f"メール: {email.get(value, N/A)}")
            
            # 電話番号
            phones = person.get("phoneNumbers", [])
            if phones:
                for phone in phones[:2]:
                    print(f"電話: {phone.get(value, N/A)}")
        
        if len(matches) > 10:
            print(f"\n... 他 {len(matches) - 10}件")
            
    except Exception as e:
        print(f"❌ 検索エラー: {str(e)}")

def main():
    print("📱 Google Contacts API 簡易接続")
    print("=" * 35)
    
    if len(sys.argv) != 2:
        print("使用方法: python3 google_contacts_simple.py <検索名>")
        print("例: python3 google_contacts_simple.py 伊藤")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # 認証
    creds = load_credentials()
    if not creds:
        print("💡 認証が必要です。Webブラウザでの認証設定を確認してください。")
        sys.exit(1)
    
    # API接続
    try:
        service = build("people", "v1", credentials=creds)
        print("✅ Google People API接続成功")
        
        # 検索実行
        search_contacts(service, query)
        
    except Exception as e:
        print(f"❌ API接続エラー: {str(e)}")

if __name__ == "__main__":
    main()
