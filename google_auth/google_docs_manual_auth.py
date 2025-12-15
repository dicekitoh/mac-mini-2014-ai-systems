#!/usr/bin/env python3
"""
Google Docs API 手動認証スクリプト
既存のcredentials.jsonを使用してGoogle Docsスコープで認証
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
    'https://www.googleapis.com/auth/drive.file'
]

CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google_docs_manual_token.pickle'

def manual_auth_flow():
    """手動認証フローを実行"""
    print("🔐 Google Docs API 手動認証開始")
    print("=" * 50)
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ 認証ファイルが見つかりません: {CREDENTIALS_FILE}")
        return None
    
    try:
        # OAuth認証フロー
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        
        # 認証URLを生成（ブラウザを開かない）
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print("📋 認証手順:")
        print("1. 以下のURLをブラウザで開いてください:")
        print(f"   {auth_url}")
        print("")
        print("2. Googleアカウントでログイン")
        print("3. 権限を許可")
        print("4. 表示された認証コードをコピー")
        print("5. この画面に認証コードを入力")
        print("=" * 50)
        
        # 認証コードの入力を求める
        auth_code = input("認証コード: ").strip()
        
        if not auth_code:
            print("❌ 認証コードが入力されませんでした")
            return None
        
        # 認証コードを使用してトークンを取得
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # トークンを保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)
        
        print("✅ 認証完了！トークンを保存しました")
        return credentials
        
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        return None

def test_docs_api(credentials):
    """Google Docs APIをテスト"""
    try:
        # サービス構築
        docs_service = build('docs', 'v1', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)
        
        print("\n🧪 Google Docs API テスト開始")
        
        # テストドキュメント作成
        document = {
            'title': '🚀 Google Docs API 接続成功テスト'
        }
        
        doc = docs_service.documents().create(body=document).execute()
        doc_id = doc.get('documentId')
        
        print(f"✅ ドキュメント作成成功")
        print(f"   ドキュメントID: {doc_id}")
        
        # テキスト挿入
        sample_text = """Google Docs API 接続成功！

MacMini2014からGoogle Docsへの接続が確立されました。

✅ 接続テスト: 成功
✅ ドキュメント作成: 成功
✅ テキスト挿入: 成功

これで以下の機能が利用可能になりました:
• 自動レポート生成
• MarkdownからGoogle Docs変換
• テンプレートベースの文書作成
• リアルタイム共同編集
• 定期タスクとの連携

接続日時: 2025年6月14日
環境: MacMini2014 (Ubuntu 24.04)
API: Google Docs API v1

🎉 Google Docs自動化システム準備完了！
"""
        
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': sample_text
                }
            }
        ]
        
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()
        
        print(f"✅ テキスト挿入成功")
        
        # ドキュメントURL表示
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        print(f"\n📄 作成されたドキュメント:")
        print(f"   {doc_url}")
        
        # ドキュメントを公開設定（任意）
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            drive_service.permissions().create(
                fileId=doc_id, body=permission).execute()
            print("✅ ドキュメントを公開設定にしました")
        except:
            print("ℹ️  ドキュメントは非公開のままです")
        
        return doc_id
        
    except HttpError as error:
        print(f"❌ API テストエラー: {error}")
        if error.resp.status == 403:
            print("   Google Cloud ConsoleでGoogle Docs APIが有効になっているか確認してください")
        return None

def main():
    """メイン処理"""
    print("🚀 Google Docs API 手動認証・実行")
    print("=" * 60)
    
    # 既存のトークンをチェック
    credentials = None
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)
            
            if credentials and credentials.valid:
                print("✅ 既存の有効な認証情報を発見")
            elif credentials and credentials.expired and credentials.refresh_token:
                print("🔄 認証情報をリフレッシュ中...")
                credentials.refresh(Request())
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(credentials, token)
                print("✅ 認証情報をリフレッシュしました")
            else:
                credentials = None
        except:
            credentials = None
    
    # 新しい認証が必要な場合
    if not credentials:
        credentials = manual_auth_flow()
    
    if not credentials:
        print("❌ 認証に失敗しました")
        return
    
    # Google Docs API テスト実行
    doc_id = test_docs_api(credentials)
    
    if doc_id:
        print("\n" + "=" * 60)
        print("🎉 Google Docs API 実行成功！")
        print(f"📄 作成ドキュメント: https://docs.google.com/document/d/{doc_id}/edit")
        print("\n💡 これで以下が可能になりました:")
        print("   • Pythonから直接Google Docsを操作")
        print("   • 自動レポート生成システム")
        print("   • MarkdownからGoogle Docs変換")
        print("   • 定期タスクでの文書自動生成")
    else:
        print("❌ Google Docs API実行に失敗しました")

if __name__ == "__main__":
    main()