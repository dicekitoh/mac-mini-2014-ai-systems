#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存の24時間認証体制分析スクリプト
"""

import pickle
import os
from datetime import datetime

def analyze_existing_auth():
    """既存の認証システム分析"""
    
    print("=== 既存24時間認証体制の調査 ===")
    
    # 調査対象のトークンファイル
    token_files = [
        ("/home/fujinosuke/google_contacts/contact_manager_v2_bot_github/token.pickle", "Contact Bot"),
        ("/home/fujinosuke/google_tasks_new.pickle", "Tasks Bot"),
        ("/home/fujinosuke/token_drive.pickle", "Drive API"),
        ("/home/fujinosuke/google/token_contacts_real.pickle", "Contacts API")
    ]
    
    for token_file, service_name in token_files:
        print(f"\n🔍 {service_name} 認証情報:")
        print(f"   ファイル: {token_file}")
        
        if not os.path.exists(token_file):
            print("   ❌ ファイルなし")
            continue
            
        try:
            with open(token_file, "rb") as f:
                creds = pickle.load(f)
            
            print(f"   有効性: {'✅ Valid' if creds.valid else '❌ Invalid'}")
            
            if hasattr(creds, 'expiry') and creds.expiry:
                time_until_expiry = creds.expiry - datetime.utcnow()
                hours_until_expiry = time_until_expiry.total_seconds() / 3600
                print(f"   有効期限: {creds.expiry}")
                print(f"   残り時間: {hours_until_expiry:.1f}時間")
                
                if hours_until_expiry > 0:
                    print("   🟢 期限内")
                else:
                    print("   🔴 期限切れ")
            else:
                print("   有効期限: 無制限または不明")
            
            print(f"   リフレッシュトークン: {'✅ あり' if creds.refresh_token else '❌ なし'}")
            
            if hasattr(creds, 'scopes') and creds.scopes:
                print(f"   スコープ数: {len(creds.scopes)}個")
                for scope in creds.scopes:
                    scope_name = scope.split('/')[-1]
                    print(f"     - {scope_name}")
            else:
                print("   スコープ: 不明")
                
        except Exception as e:
            print(f"   ❌ エラー: {e}")
    
    # 自動リフレッシュシステムの確認
    print("\n=== 自動リフレッシュシステム確認 ===")
    
    refresh_scripts = [
        "/home/fujinosuke/stable_todo_bot.py",
        "/home/fujinosuke/todo_bot_token_monitor.py",
        "/home/fujinosuke/google_contacts/contact_manager_v2_bot_github/contact_manager_v2_bot_final.py"
    ]
    
    for script in refresh_scripts:
        if os.path.exists(script):
            print(f"✅ {os.path.basename(script)}: 存在")
            
            # ファイルの更新日時確認
            mtime = os.path.getmtime(script)
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   更新日時: {mtime_str}")
        else:
            print(f"❌ {os.path.basename(script)}: なし")

if __name__ == '__main__':
    analyze_existing_auth()