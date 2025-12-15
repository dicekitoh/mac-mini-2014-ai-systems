#!/usr/bin/env python3
"""
Google Docs API OAuth認証テストスクリプト
既存のOAuth credentials.jsonを使用
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

# 認証ファイルのパス
CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google_docs_token.pickle'

def authenticate():
    """OAuth認証を実行"""
    creds = None
    
    # 既存のトークンファイルがあれば読み込み
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 認証情報が無効または存在しない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ トークンをリフレッシュしました")
            except Exception as e:
                print(f"トークンリフレッシュエラー: {e}")
                creds = None
        
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                # ヘッドレス環境用の認証フロー
                flow.run_local_server(port=0, open_browser=False)
                creds = flow.credentials
                print("✅ 新しい認証情報を取得しました")
            except Exception as e:
                print(f"OAuth認証エラー: {e}")
                print("ヘッドレス環境での認証が困難です。")
                print("代替案: Google Colabまたは別の環境で認証を完了してください。")
                return None
        
        # トークンを保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
            print("✅ 認証トークンを保存しました")
    
    return creds

def create_services(credentials):
    """Google API サービスを作成"""
    try:
        docs_service = build('docs', 'v1', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)
        return docs_service, drive_service
    except Exception as e:
        print(f"サービス作成エラー: {e}")
        return None, None

def test_api_access(docs_service):
    """API接続テスト"""
    try:
        # テスト用の簡単なドキュメント作成
        document = {'title': 'API接続テスト'}
        doc = docs_service.documents().create(body=document).execute()
        doc_id = doc.get('documentId')
        
        print(f"✅ API接続テスト成功")
        print(f"   テストドキュメントID: {doc_id}")
        
        # 作成したテストドキュメントを削除（クリーンアップ）
        return doc_id
        
    except HttpError as error:
        print(f"❌ API接続テストエラー: {error}")
        if error.resp.status == 403:
            print("   権限エラー: Google Docs APIが有効になっていない可能性があります")
            print("   Google Cloud ConsoleでGoogle Docs APIを有効にしてください")
        return None

def create_sample_document(docs_service):
    """サンプルドキュメントを作成"""
    try:
        # ドキュメント作成
        document = {'title': '🚀 Google Docs API 連携テスト'}
        doc = docs_service.documents().create(body=document).execute()
        doc_id = doc.get('documentId')
        
        # コンテンツ追加
        sample_text = """Google Docs API 連携成功！

このドキュメントはMacMini2014のPythonスクリプトから作成されました。

機能テスト:
✅ ドキュメント作成
✅ テキスト挿入
✅ OAuth認証

作成日時: 2025年6月14日
環境: MacMini2014 Ubuntu 24.04
API: Google Docs API v1

次のステップ:
• 自動文書生成システム構築
• MarkdownからGoogle Docs変換
• 定期レポート自動作成

このテストが成功していれば、Google Docs APIの基本機能が利用可能です。
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
        
        print(f"✅ サンプルドキュメント作成成功")
        print(f"   URL: https://docs.google.com/document/d/{doc_id}/edit")
        
        return doc_id
        
    except HttpError as error:
        print(f"❌ ドキュメント作成エラー: {error}")
        return None

def main():
    """メイン処理"""
    print("🚀 Google Docs API OAuth認証テスト開始")
    print("=" * 60)
    
    # 認証
    credentials = authenticate()
    if not credentials:
        print("❌ 認証に失敗しました")
        return
    
    print("✅ 認証成功")
    
    # サービス作成
    docs_service, drive_service = create_services(credentials)
    if not docs_service:
        print("❌ サービス作成に失敗しました")
        return
    
    print("✅ Google Docs サービス作成成功")
    
    # API接続テスト
    test_doc_id = test_api_access(docs_service)
    if not test_doc_id:
        return
    
    # サンプルドキュメント作成
    sample_doc_id = create_sample_document(docs_service)
    
    if sample_doc_id:
        print("=" * 60)
        print("🎉 Google Docs API 連携完了!")
        print(f"📄 作成されたドキュメント:")
        print(f"   https://docs.google.com/document/d/{sample_doc_id}/edit")
        print("")
        print("💡 これでGoogle Docsの自動化が可能になりました:")
        print("   • 文書の自動生成")
        print("   • レポートの自動作成") 
        print("   • MarkdownからGoogle Docs変換")
        print("   • 定期タスクとの連携")

if __name__ == "__main__":
    main()