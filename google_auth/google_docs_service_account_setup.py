#!/usr/bin/env python3
"""
Google Docs API サービスアカウント認証セットアップガイド
権限問題を回避するための代替手順
"""

import json
import os
from datetime import datetime

def create_service_account_guide():
    """サービスアカウント作成ガイドを表示"""
    print("🔧 Google Docs API サービスアカウント認証設定ガイド")
    print("=" * 70)
    print("現在のプロジェクト権限が不足しているため、新しいアプローチを使用します。")
    print("")
    
    print("📋 方法1: 新しいGoogle Cloudプロジェクト作成")
    print("-" * 50)
    print("1. https://console.cloud.google.com/ にアクセス")
    print("2. 左上の「プロジェクト選択」をクリック")
    print("3. 「新しいプロジェクト」をクリック")
    print("4. プロジェクト名: 'macmini2014-docs-api' (任意)")
    print("5. 「作成」をクリック")
    print("6. 新しいプロジェクトを選択")
    print("")
    
    print("📋 方法2: サービスアカウント作成 (推奨)")
    print("-" * 50)
    print("1. 「IAM と管理」→「サービスアカウント」")
    print("2. 「サービスアカウントを作成」")
    print("3. 名前: 'macmini2014-docs-service'")
    print("4. 説明: 'MacMini2014 Google Docs API access'")
    print("5. 「作成して続行」")
    print("6. ロール: 「編集者」または「オーナー」を選択")
    print("7. 「続行」→「完了」")
    print("")
    
    print("📋 方法3: JSONキー作成")
    print("-" * 50)
    print("1. 作成したサービスアカウントをクリック")
    print("2. 「キー」タブ")
    print("3. 「キーを追加」→「新しいキーを作成」")
    print("4. 「JSON」を選択")
    print("5. 「作成」→ JSONファイルをダウンロード")
    print("")
    
    print("📋 方法4: API有効化")
    print("-" * 50)
    print("1. 「APIとサービス」→「ライブラリ」")
    print("2. 「Google Docs API」を検索")
    print("3. 「有効にする」をクリック")
    print("4. 「Google Drive API」も有効にする")
    print("")
    
    print("📋 方法5: ファイル配置")
    print("-" * 50)
    print("1. ダウンロードしたJSONファイルをリネーム:")
    print("   service-account-key.json")
    print("2. MacMini2014に配置:")
    print("   scp service-account-key.json fujinosuke@192.168.3.43:~/google_docs_service_key.json")
    print("")

def create_alternative_oauth_guide():
    """OAuth認証の代替手順"""
    print("🔄 代替案: 個人アカウントでのOAuth認証")
    print("=" * 70)
    print("現在のプロジェクトではなく、個人のGoogleアカウントで新しいプロジェクトを作成:")
    print("")
    print("1. 個人のGoogleアカウントでGoogle Cloud Consoleにログイン")
    print("2. 新しいプロジェクトを作成")
    print("3. OAuth 2.0認証情報を作成")
    print("4. アプリケーションタイプ: 「デスクトップアプリケーション」")
    print("5. credentials.jsonをダウンロード")
    print("6. MacMini2014に配置")
    print("")

def test_current_environment():
    """現在の環境をテスト"""
    print("🧪 現在の環境テスト")
    print("=" * 70)
    
    # 既存ファイル確認
    files_to_check = [
        '/home/fujinosuke/google/credentials.json',
        '/home/fujinosuke/credentials_drive.json',
        '/home/fujinosuke/token_drive.pickle',
        '/home/fujinosuke/google_docs_service_key.json'
    ]
    
    print("📁 既存認証ファイル確認:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                size = os.path.getsize(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"✅ {file_path} ({size}バイト, {mtime.strftime('%Y-%m-%d %H:%M')})")
                
                # JSONファイルの内容確認
                if file_path.endswith('.json'):
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if 'type' in data:
                                print(f"   タイプ: {data['type']}")
                            if 'client_id' in data:
                                print(f"   クライアントID: {data['client_id'][:20]}...")
                            if 'project_id' in data:
                                print(f"   プロジェクトID: {data['project_id']}")
                    except:
                        print("   (JSON解析エラー)")
            except:
                print(f"❌ {file_path} (アクセスエラー)")
        else:
            print(f"❌ {file_path} (ファイルなし)")
    
    print("\n🔧 推奨アクション:")
    print("1. 新しいGoogle Cloudプロジェクトでサービスアカウント作成")
    print("2. JSONキーファイルをMacMini2014に配置")
    print("3. Google Docs API有効化")
    print("4. テストスクリプト実行")

def create_quick_test_script():
    """クイックテスト用スクリプトを作成"""
    script_content = '''#!/usr/bin/env python3
"""
Google Docs API クイックテスト
サービスアカウント認証用
"""

import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY_FILE = '/home/fujinosuke/google_docs_service_key.json'
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

def quick_test():
    if not os.path.exists(KEY_FILE):
        print(f"❌ サービスアカウントキーファイルが必要: {KEY_FILE}")
        return False
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            KEY_FILE, scopes=SCOPES)
        
        docs_service = build('docs', 'v1', credentials=credentials)
        
        # 簡単なドキュメント作成テスト
        doc = docs_service.documents().create(
            body={'title': 'テスト成功！'}).execute()
        
        print(f"✅ 成功! ドキュメントID: {doc['documentId']}")
        print(f"URL: https://docs.google.com/document/d/{doc['documentId']}/edit")
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    quick_test()
'''
    
    with open('/home/fujinosuke/google_docs_quick_test.py', 'w') as f:
        f.write(script_content)
    
    print("📝 クイックテストスクリプトを作成しました:")
    print("   /home/fujinosuke/google_docs_quick_test.py")

def main():
    """メイン処理"""
    print("🚀 Google Docs API トラブルシューティング")
    print("プロジェクト権限不足の解決方法")
    print("=" * 80)
    
    create_service_account_guide()
    print("\n")
    create_alternative_oauth_guide()
    print("\n")
    test_current_environment()
    print("\n")
    
    try:
        create_quick_test_script()
    except:
        print("📝 クイックテストスクリプト作成をスキップ")
    
    print("\n" + "=" * 80)
    print("🎯 最も簡単な解決方法:")
    print("1. 個人Googleアカウントで新しいプロジェクト作成")
    print("2. サービスアカウント + JSONキー作成")
    print("3. Google Docs API有効化")
    print("4. キーファイルをMacMini2014に配置")
    print("5. クイックテスト実行")

if __name__ == "__main__":
    main()