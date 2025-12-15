#\!/usr/bin/env python3
# Google Tasks API接続テスト

import pickle
import os
import requests
from google.auth.transport.requests import Request

TOKEN_FILE = 'google_tasks_new.pickle'

def test_connection():
    """既存のトークンでAPI接続をテスト"""
    try:
        # トークンファイルを確認
        if not os.path.exists(TOKEN_FILE):
            print(f"❌ トークンファイルが見つかりません: {TOKEN_FILE}")
            return False
        
        # トークンを読み込み
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
        
        print(f"✅ トークンファイル読み込み成功")
        print(f"  - 有効期限: {creds.expiry if hasattr(creds, 'expiry') else '不明'}")
        print(f"  - トークン有効: {creds.valid if hasattr(creds, 'valid') else '不明'}")
        
        # トークンをリフレッシュ
        if hasattr(creds, 'expired') and creds.expired and hasattr(creds, 'refresh_token') and creds.refresh_token:
            print("トークンの有効期限が切れています。リフレッシュを試みます...")
            try:
                creds.refresh(Request())
                print("✅ トークンのリフレッシュ成功")
                
                # リフレッシュ後のトークンを保存
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"❌ トークンリフレッシュ失敗: {e}")
                return False
        
        # API接続テスト
        headers = {
            'Authorization': f'Bearer {creds.token}',
            'Content-Type': 'application/json'
        }
        
        # タスクリスト取得
        response = requests.get(
            'https://www.googleapis.com/tasks/v1/users/@me/lists',
            headers=headers
        )
        
        if response.status_code == 200:
            lists = response.json().get('items', [])
            print(f"\n✅ API接続成功！")
            print(f"📋 タスクリスト数: {len(lists)}")
            for task_list in lists[:3]:
                print(f"  - {task_list.get('title', '無題')} (ID: {task_list.get('id', 'N/A')})")
            
            # 最初のリストのタスクを取得
            if lists:
                list_id = lists[0]['id']
                tasks_response = requests.get(
                    f'https://www.googleapis.com/tasks/v1/lists/{list_id}/tasks',
                    headers=headers
                )
                if tasks_response.status_code == 200:
                    tasks = tasks_response.json().get('items', [])
                    print(f"\n📝 {lists[0]['title']}のタスク数: {len(tasks)}")
                    for task in tasks[:5]:
                        print(f"  - {task.get('title', '無題')}")
            
            return True
        else:
            print(f"\n❌ API接続失敗: {response.status_code}")
            print(f"エラー: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Google Tasks API 接続テスト")
    print("=" * 50)
    test_connection()
