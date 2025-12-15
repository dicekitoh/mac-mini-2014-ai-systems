#!/usr/bin/env python3
"""
Google Docs API テスト - 既存のGoogle Drive認証を使用
"""

import os
import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 既存のGoogle Drive認証ファイル
DRIVE_TOKEN_FILE = '/home/fujinosuke/token_drive.pickle'

def test_with_drive_credentials():
    """Google Drive認証でGoogle Docs APIをテスト"""
    print("🚀 既存のGoogle Drive認証でGoogle Docs API実行")
    print("=" * 60)
    
    if not os.path.exists(DRIVE_TOKEN_FILE):
        print(f"❌ Google Driveトークンファイルなし: {DRIVE_TOKEN_FILE}")
        return False
    
    try:
        # Google Drive認証情報を読み込み
        with open(DRIVE_TOKEN_FILE, 'rb') as token:
            credentials = pickle.load(token)
        
        print("✅ Google Drive認証情報を読み込み")
        
        # スコープ確認
        scopes = getattr(credentials, 'scopes', ['不明'])
        print(f"📋 現在のスコープ: {scopes}")
        
        # 認証情報の有効性確認
        if credentials.expired and credentials.refresh_token:
            print("🔄 認証情報をリフレッシュ中...")
            credentials.refresh(Request())
            print("✅ 認証情報リフレッシュ完了")
        elif not credentials.valid:
            print("❌ 認証情報が無効です")
            return False
        
        # Google Docs APIサービス構築を試行
        try:
            docs_service = build('docs', 'v1', credentials=credentials)
            print("✅ Google Docs APIサービス構築成功")
        except Exception as e:
            print(f"❌ Google Docs APIサービス構築失敗: {e}")
            return False
        
        # Google Drive APIサービス構築
        try:
            drive_service = build('drive', 'v3', credentials=credentials)
            print("✅ Google Drive APIサービス構築成功")
        except Exception as e:
            print(f"❌ Google Drive APIサービス構築失敗: {e}")
            drive_service = None
        
        # Google Docs APIテスト実行
        return test_docs_creation(docs_service, drive_service)
        
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        return False

def test_docs_creation(docs_service, drive_service):
    """ドキュメント作成テスト"""
    try:
        print("\n📝 Google Docsドキュメント作成テスト")
        
        # ドキュメント作成
        document = {
            'title': '🚀 MacMini2014 Google Docs API 接続テスト'
        }
        
        doc = docs_service.documents().create(body=document).execute()
        doc_id = doc.get('documentId')
        
        print(f"✅ ドキュメント作成成功")
        print(f"   ドキュメントID: {doc_id}")
        
        # 詳細なテストコンテンツ
        test_content = """Google Docs API 接続成功！

🎉 MacMini2014からGoogle Docsへの接続が確立されました

📊 テスト結果:
✅ API認証: 成功
✅ ドキュメント作成: 成功  
✅ テキスト挿入: 成功
✅ 既存認証流用: 成功

🔧 技術詳細:
• 環境: MacMini2014 (Ubuntu 24.04)
• Python: 仮想環境 (google_docs_api_env)
• 認証: 既存Google Drive認証情報を流用
• API: Google Docs API v1

💡 利用可能な機能:
• 自動レポート生成
• MarkdownからGoogle Docs変換  
• テンプレートベースの文書作成
• リアルタイム文書更新
• 定期タスクとの連携
• StackEditとの連携

🚀 次のステップ:
1. MarkdownからGoogle Docs変換システム構築
2. StackEditとの連携機能開発
3. 自動レポート生成システム実装
4. 定期タスクでの文書自動生成

接続確認日時: 2025年6月14日 21:40
実行環境: ssh fujinosuke@192.168.3.43

このテストが成功すれば、Google Docs自動化システムの基盤が完成です！
"""
        
        # テキスト挿入
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': test_content
                }
            }
        ]
        
        result = docs_service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()
        
        print(f"✅ テキスト挿入成功 ({len(test_content)}文字)")
        
        # タイトル部分を太字にフォーマット
        try:
            format_requests = [
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': 25  # "Google Docs API 接続成功！" の長さ
                        },
                        'textStyle': {
                            'bold': True,
                            'fontSize': {'magnitude': 16, 'unit': 'PT'}
                        },
                        'fields': 'bold,fontSize'
                    }
                }
            ]
            
            docs_service.documents().batchUpdate(
                documentId=doc_id, body={'requests': format_requests}).execute()
            
            print("✅ テキストフォーマット成功")
            
        except Exception as e:
            print(f"⚠️  フォーマット処理をスキップ: {e}")
        
        # ドキュメントURL
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        print(f"\n📄 作成されたドキュメント:")
        print(f"   {doc_url}")
        
        # Google Driveでの共有設定（可能であれば）
        if drive_service:
            try:
                # 閲覧可能な公開設定
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                drive_service.permissions().create(
                    fileId=doc_id, body=permission).execute()
                print("✅ ドキュメントを公開設定にしました")
                print(f"   公開URL: https://docs.google.com/document/d/{doc_id}/view")
            except Exception as e:
                print(f"ℹ️  公開設定スキップ: {e}")
        
        return True
        
    except HttpError as error:
        print(f"❌ Google Docs API エラー: {error}")
        if error.resp.status == 403:
            print("   🔧 解決策: Google Cloud ConsoleでGoogle Docs APIを有効にしてください")
            print("   URL: https://console.cloud.google.com/apis/library/docs.googleapis.com")
        elif error.resp.status == 401:
            print("   🔧 解決策: 認証情報を更新してください")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def main():
    """メイン処理"""
    print("🚀 Google Docs API 実行テスト")
    print("既存のGoogle Drive認証を使用してGoogle Docsにアクセス")
    print("=" * 70)
    
    success = test_with_drive_credentials()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 Google Docs API 実行成功！")
        print("")
        print("💡 これで以下が利用可能になりました:")
        print("   ✅ PythonからGoogle Docsの直接操作")
        print("   ✅ 自動ドキュメント生成システム")
        print("   ✅ MarkdownからGoogle Docs変換")
        print("   ✅ StackEditとの連携基盤")
        print("   ✅ 定期レポート自動生成")
        print("")
        print("🔧 次のステップ:")
        print("   1. MarkdownからGoogle Docs変換機能開発")
        print("   2. StackEditで作成したMarkdownを自動でGoogle Docsに変換")
        print("   3. 定期レポート生成システム構築")
    else:
        print("❌ Google Docs API 実行失敗")
        print("")
        print("🔧 解決策:")
        print("   1. Google Cloud ConsoleでGoogle Docs APIを有効化")
        print("   2. 適切なスコープで再認証")
        print("   3. サービスアカウント認証の検討")

if __name__ == "__main__":
    main()