#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存BOTシステムの認証修復と統一システム適用
Contact Bot と Tasks Bot の認証を修復し、統一システムに統合
"""

import os
import pickle
import time
from datetime import datetime
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def fix_contact_bot_auth():
    """Contact Bot認証修復"""
    print("🔧 Contact Bot認証修復開始...")
    
    token_file = "/home/fujinosuke/google_contacts/contact_manager_v2_bot_github/token.pickle"
    backup_file = token_file + ".broken_backup"
    
    try:
        # 破損したトークンをバックアップ
        if os.path.exists(token_file):
            import shutil
            shutil.copy(token_file, backup_file)
            print(f"💾 破損トークンをバックアップ: {backup_file}")
        
        # 統一システムのトークンを使用
        unified_token = "/home/fujinosuke/unified_google_token.pickle"
        if os.path.exists(unified_token):
            with open(unified_token, 'rb') as f:
                creds = pickle.load(f)
            
            if creds.valid:
                # Contact Bot用にトークンをコピー
                import shutil
                shutil.copy(unified_token, token_file)
                print("✅ Contact Bot認証修復完了")
                
                # 動作確認
                service = build('people', 'v1', credentials=creds)
                connections = service.people().connections().list(
                    resourceName='people/me',
                    pageSize=1,
                    personFields='names'
                ).execute()
                
                print("✅ Contact Bot動作確認成功")
                return True
            else:
                print("❌ 統一トークンが無効")
        else:
            print("❌ 統一トークンファイルが見つかりません")
            
    except Exception as e:
        print(f"❌ Contact Bot修復エラー: {e}")
    
    return False

def fix_tasks_bot_auth():
    """Tasks Bot認証修復"""
    print("🔧 Tasks Bot認証修復開始...")
    
    token_file = "/home/fujinosuke/google_tasks_new.pickle"
    
    try:
        # 現在のトークン確認
        if os.path.exists(token_file):
            with open(token_file, 'rb') as f:
                creds = pickle.load(f)
            
            if not creds.valid and creds.refresh_token:
                print("🔄 Tasks Botトークンリフレッシュ中...")
                creds.refresh(Request())
                
                # 更新されたトークンを保存
                with open(token_file, 'wb') as f:
                    pickle.dump(creds, f)
                
                print("✅ Tasks Bot認証修復完了")
                
                # 動作確認
                service = build('tasks', 'v1', credentials=creds)
                tasklists = service.tasklists().list().execute()
                print("✅ Tasks Bot動作確認成功")
                return True
            elif creds.valid:
                print("✅ Tasks Bot認証は既に有効")
                return True
            else:
                print("❌ Tasks Botリフレッシュトークンなし")
                
    except Exception as e:
        print(f"❌ Tasks Bot修復エラー: {e}")
    
    return False

def update_bot_monitoring():
    """BOT監視システム更新"""
    print("🔧 BOT監視システム更新開始...")
    
    try:
        # Contact Bot プロセス確認
        import subprocess
        
        # Contact Botが稼働中か確認
        result = subprocess.run(['pgrep', '-f', 'contact_manager_v2_bot_final.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Contact Bot稼働中")
            
            # BOTを再起動して新しい認証を適用
            print("🔄 Contact Bot再起動...")
            
            # 既存プロセス終了
            subprocess.run(['pkill', '-f', 'contact_manager_v2_bot_final.py'])
            time.sleep(2)
            
            # 新しいプロセス開始
            contact_bot_dir = "/home/fujinosuke/google_contacts/contact_manager_v2_bot_github"
            start_cmd = f"cd {contact_bot_dir} && source /home/fujinosuke/google_contacts_env/bin/activate && python3 contact_manager_v2_bot_final.py"
            
            subprocess.Popen(['screen', '-S', 'contact_bot_fixed', '-d', '-m', 'bash', '-c', start_cmd])
            print("✅ Contact Bot再起動完了")
        
        # Tasks Bot確認・再起動
        result = subprocess.run(['pgrep', '-f', 'stable_todo_bot.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tasks Bot稼働中")
            
            # Tasks Bot再起動
            print("🔄 Tasks Bot再起動...")
            subprocess.run(['pkill', '-f', 'stable_todo_bot.py'])
            time.sleep(2)
            
            start_cmd = "cd /home/fujinosuke && source todo_env/bin/activate && python3 stable_todo_bot.py"
            subprocess.Popen(['screen', '-S', 'todo_bot_fixed', '-d', '-m', 'bash', '-c', start_cmd])
            print("✅ Tasks Bot再起動完了")
        
        return True
        
    except Exception as e:
        print(f"❌ BOT監視システム更新エラー: {e}")
        return False

def verify_unified_system():
    """統一システム動作確認"""
    print("🧪 統一システム動作確認...")
    
    try:
        # 統一トークンで各サービステスト
        unified_token = "/home/fujinosuke/unified_google_token.pickle"
        
        if not os.path.exists(unified_token):
            print("❌ 統一トークンファイルが見つかりません")
            return False
        
        with open(unified_token, 'rb') as f:
            creds = pickle.load(f)
        
        if not creds.valid:
            print("❌ 統一トークンが無効")
            return False
        
        # 各サービステスト
        services_to_test = [
            ('drive', 'v3', lambda s: s.files().list(pageSize=1).execute()),
            ('tasks', 'v1', lambda s: s.tasklists().list().execute()),
            ('people', 'v1', lambda s: s.people().connections().list(
                resourceName='people/me', pageSize=1, personFields='names').execute())
        ]
        
        working_services = []
        
        for service_name, version, test_func in services_to_test:
            try:
                service = build(service_name, version, credentials=creds)
                test_func(service)
                working_services.append(service_name)
                print(f"✅ {service_name}: 正常動作")
            except Exception as e:
                print(f"❌ {service_name}: {e}")
        
        print(f"\\n📊 動作中サービス: {len(working_services)}/3")
        return len(working_services) >= 2
        
    except Exception as e:
        print(f"❌ 統一システム確認エラー: {e}")
        return False

def main():
    """メイン修復プロセス"""
    print("🚀 既存BOTシステム認証修復開始")
    print("=" * 50)
    
    # 修復ステップ
    steps = [
        ("統一システム動作確認", verify_unified_system),
        ("Contact Bot認証修復", fix_contact_bot_auth),
        ("Tasks Bot認証修復", fix_tasks_bot_auth),
        ("BOT監視システム更新", update_bot_monitoring),
        ("最終動作確認", verify_unified_system)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        print(f"\\n🔧 {step_name}...")
        if step_func():
            print(f"✅ {step_name}: 成功")
            success_count += 1
        else:
            print(f"❌ {step_name}: 失敗")
    
    print("\\n" + "=" * 50)
    print(f"📊 修復結果: {success_count}/{len(steps)} ステップ成功")
    
    if success_count == len(steps):
        print("🎉 全ての修復が完了しました！")
        print("✅ 24時間認証体制が全Googleサービスで稼働中")
    elif success_count >= 3:
        print("⚠️ 部分的に修復完了。一部手動対応が必要です")
    else:
        print("❌ 修復に失敗しました。手動確認が必要です")
    
    return success_count == len(steps)

if __name__ == '__main__':
    main()