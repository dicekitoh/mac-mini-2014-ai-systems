#!/usr/bin/env python3
"""
Chrome同期無効化ツール
Preferencesファイルを直接編集して同期を停止
"""

import json
import shutil
import subprocess
import time
from datetime import datetime

class ChromeSyncDisabler:
    def __init__(self):
        self.preferences_file = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data/Default/Preferences"
        self.backup_file = f"{self.preferences_file}.sync_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def force_kill_chrome(self):
        """Chrome完全強制終了"""
        print("🛑 Chrome完全強制終了中...")
        
        commands = [
            'taskkill /F /IM chrome.exe /T',
            'taskkill /F /IM msedge.exe /T',
            'timeout /t 5'
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, cwd="/mnt/c", capture_output=True, timeout=10)
            except:
                pass
        
        print("✅ Chrome強制終了完了")

    def disable_sync(self):
        """同期設定を無効化"""
        try:
            # バックアップ作成
            shutil.copy2(self.preferences_file, self.backup_file)
            print(f"💾 バックアップ作成: {self.backup_file}")
            
            # 設定ファイル読み込み
            with open(self.preferences_file, 'r', encoding='utf-8') as f:
                preferences = json.load(f)
            
            # 同期関連設定を無効化
            modifications = []
            
            # アカウント情報をクリア
            if 'account_info' in preferences:
                preferences['account_info'] = []
                modifications.append("アカウント情報をクリア")
            
            # 同期設定を無効化
            if 'sync' not in preferences:
                preferences['sync'] = {}
            
            sync_settings = {
                'suppress_sync_promo': True,
                'keep_everything_synced': False,
                'sync_everything': False,
                'sync_bookmarks': False,
                'sync_preferences': False,
                'sync_tabs': False,
                'sync_passwords': False,
                'sync_autofill': False,
                'sync_themes': False,
                'sync_extensions': False,
                'sync_apps': False,
                'sync_reading_list': False,
                'sync_sessions': False
            }
            
            for key, value in sync_settings.items():
                preferences['sync'][key] = value
                modifications.append(f"sync.{key} = {value}")
            
            # サインイン関連を無効化
            if 'signin' not in preferences:
                preferences['signin'] = {}
            
            signin_settings = {
                'allowed': False,
                'allowed_on_next_startup': False
            }
            
            for key, value in signin_settings.items():
                preferences['signin'][key] = value
                modifications.append(f"signin.{key} = {value}")
            
            # ファイル書き込み
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, ensure_ascii=False, indent=2)
            
            print("✅ 同期設定を無効化しました")
            print("📋 変更内容:")
            for mod in modifications:
                print(f"  - {mod}")
            
            return True
            
        except Exception as e:
            print(f"❌ 同期無効化エラー: {e}")
            return False

def main():
    print("🔒 Chrome同期無効化ツール")
    print("=" * 40)
    
    disabler = ChromeSyncDisabler()
    
    # Chrome強制終了
    disabler.force_kill_chrome()
    
    # 5秒待機
    print("⏳ 5秒待機中...")
    time.sleep(5)
    
    # 同期無効化
    if disabler.disable_sync():
        print(f"\n🎉 同期無効化完了！")
        print(f"\n🔄 次の手順:")
        print(f"1. Chromeを起動")
        print(f"2. chrome://settings/syncSetup で同期がオフになっていることを確認")
        print(f"3. ブックマーク整理作業を実行")
        print(f"\n⚠️ 注意: 今後はローカルのブックマークのみ使用されます")
    else:
        print(f"\n❌ 同期無効化失敗")

if __name__ == "__main__":
    main()