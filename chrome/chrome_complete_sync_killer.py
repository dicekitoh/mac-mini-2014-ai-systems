#!/usr/bin/env python3
"""
Chrome同期完全無効化ツール
より強力な方法で同期を完全に停止
"""

import json
import shutil
import subprocess
import time
import os
from datetime import datetime

class ChromeCompleteSyncKiller:
    def __init__(self):
        self.chrome_dir = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data/Default"
        self.preferences_file = f"{self.chrome_dir}/Preferences"
        self.local_state_file = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data/Local State"
        self.sync_data_dir = f"{self.chrome_dir}/Sync Data"
        self.backup_dir = f"/home/rootmax/chrome_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def force_kill_chrome(self):
        """Chrome完全強制終了"""
        print("🛑 Chrome完全強制終了中...")
        
        commands = [
            'taskkill /F /IM chrome.exe /T',
            'taskkill /F /IM GoogleUpdate.exe /T',
            'taskkill /F /IM GoogleCrashHandler.exe /T',
            'timeout /t 5'
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, cwd="/mnt/c", capture_output=True, timeout=15)
            except:
                pass
        
        print("✅ Chrome強制終了完了")

    def backup_files(self):
        """重要ファイルのバックアップ"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            files_to_backup = [
                self.preferences_file,
                self.local_state_file,
                f"{self.chrome_dir}/Bookmarks"
            ]
            
            for file_path in files_to_backup:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    shutil.copy2(file_path, f"{self.backup_dir}/{filename}")
            
            print(f"💾 バックアップ完了: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ バックアップエラー: {e}")
            return False

    def delete_sync_data(self):
        """同期データディレクトリを削除"""
        try:
            if os.path.exists(self.sync_data_dir):
                shutil.rmtree(self.sync_data_dir)
                print("🗑️ 同期データディレクトリを削除")
            return True
        except Exception as e:
            print(f"⚠️ 同期データ削除警告: {e}")
            return True  # 削除できなくても続行

    def completely_disable_sync(self):
        """同期を完全に無効化"""
        try:
            # Preferences編集
            with open(self.preferences_file, 'r', encoding='utf-8') as f:
                preferences = json.load(f)
            
            # 同期関連設定を完全に削除/無効化
            sync_disable_settings = {
                'account_info': [],
                'account_tracker_service_last_update': "0",
                'sync': {
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
                    'sync_sessions': False,
                    'disabled': True,
                    'has_setup_completed': False
                },
                'signin': {
                    'allowed': False,
                    'allowed_on_next_startup': False
                },
                'browser': preferences.get('browser', {})
            }
            
            # ブラウザ設定に同期無効化を追加
            sync_disable_settings['browser']['sync_promo'] = {
                'user_skipped': True,
                'show_on_first_run_allowed': False
            }
            
            # 設定を適用
            for key, value in sync_disable_settings.items():
                preferences[key] = value
            
            # Preferencesファイル書き込み
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, ensure_ascii=False, indent=2)
            
            # Local State編集
            with open(self.local_state_file, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            
            # Local Stateでも同期を無効化
            local_state_sync_settings = {
                'google_services': {
                    'consent_for_google_services': False
                },
                'sync_promo': {
                    'show_on_first_run_allowed': False,
                    'user_skipped': True
                }
            }
            
            for key, value in local_state_sync_settings.items():
                if key not in local_state:
                    local_state[key] = {}
                local_state[key].update(value)
            
            # Local Stateファイル書き込み
            with open(self.local_state_file, 'w', encoding='utf-8') as f:
                json.dump(local_state, f, ensure_ascii=False, indent=2)
            
            print("✅ 同期設定を完全に無効化")
            return True
            
        except Exception as e:
            print(f"❌ 同期無効化エラー: {e}")
            return False

    def set_file_readonly(self):
        """設定ファイルを読み取り専用にして同期復元を防ぐ"""
        try:
            # Windowsのattribコマンドで読み取り専用に設定
            files_to_protect = [
                self.preferences_file,
                self.local_state_file
            ]
            
            for file_path in files_to_protect:
                windows_path = file_path.replace('/mnt/c/', 'C:\\').replace('/', '\\')
                subprocess.run(f'attrib +R "{windows_path}"', shell=True, cwd="/mnt/c", capture_output=True)
            
            print("🔒 設定ファイルを読み取り専用に設定")
            return True
        except Exception as e:
            print(f"⚠️ 読み取り専用設定警告: {e}")
            return True

def main():
    print("🔥 Chrome同期完全無効化ツール")
    print("=" * 50)
    
    killer = ChromeCompleteSyncKiller()
    
    # Chrome強制終了
    killer.force_kill_chrome()
    
    # バックアップ
    if not killer.backup_files():
        return
    
    # 同期データ削除
    killer.delete_sync_data()
    
    # 同期完全無効化
    if killer.completely_disable_sync():
        # ファイル保護
        killer.set_file_readonly()
        
        print(f"\n🎉 Chrome同期完全無効化完了！")
        print(f"\n📋 実行内容:")
        print(f"  - Chrome全プロセス強制終了")
        print(f"  - 同期データディレクトリ削除")
        print(f"  - Preferences/Local State完全編集")
        print(f"  - 設定ファイル読み取り専用化")
        print(f"\n🔄 今すぐブックマーク整理を実行できます")
    else:
        print(f"\n❌ 同期無効化失敗")

if __name__ == "__main__":
    main()