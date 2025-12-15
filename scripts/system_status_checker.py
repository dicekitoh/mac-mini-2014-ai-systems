#!/usr/bin/env python3
"""
MacMini2014 システム状況確認スクリプト
即座に運用状況を一覧表示
"""
import subprocess
import json
import os
from datetime import datetime

def run_command(cmd):
    """コマンドを実行して結果を返す"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "エラー"

def check_service_status(service_name):
    """サービスの状態を確認"""
    status = run_command(f"systemctl is-active {service_name}")
    return "🟢" if status == "active" else "🔴"

def main():
    print("=" * 60)
    print(f"MacMini2014 システム状況レポート")
    print(f"確認日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 基本サービス
    print("\n【基本サービス】")
    services = ["nginx", "php8.3-fpm", "ssh", "fail2ban"]
    for service in services:
        status = check_service_status(service)
        print(f"{status} {service}")
    
    # 稼働中のカスタムプロセス
    print("\n【カスタムプロセス】")
    
    # backup_monitor確認
    backup_check = run_command("ps aux | grep -v grep | grep backup_monitor.py")
    if backup_check:
        print("🟢 Google Drive バックアップモニター")
    else:
        print("🔴 Google Drive バックアップモニター")
    
    # Contact Manager Bot確認
    contact_bot = run_command("ps aux | grep -v grep | grep contact_manager_v2_bot")
    if contact_bot:
        print("🟢 Contact Manager v2 Bot")
    else:
        print("🔴 Contact Manager v2 Bot")
    
    # API連携状況
    print("\n【API連携状況】")
    
    # Google API認証ファイル確認
    google_apis = {
        "Google Drive API": "/home/fujinosuke/credentials_drive.json",
        "Google Contacts API": "/home/fujinosuke/google_contacts/credentials.json",
        "Google Tasks API": "/home/fujinosuke/google_tasks_new.pickle"
    }
    
    for api_name, auth_file in google_apis.items():
        if os.path.exists(auth_file):
            print(f"🟢 {api_name}")
        else:
            print(f"🔴 {api_name}")
    
    # LINEWORKS API確認
    if os.path.exists("/home/fujinosuke/lineworks/private_20250529134836.key"):
        print("🟢 LINEWORKS API")
    else:
        print("🔴 LINEWORKS API")
    
    # Cron実行予定
    print("\n【定期実行タスク】")
    cron_jobs = run_command("crontab -l 2>/dev/null | grep -v '#' | grep -v '^\s*$'")
    if cron_jobs:
        for job in cron_jobs.split('\n'):
            if "weather_alert" in job:
                print("⏰ 気象警報通知 - 毎朝5:30")
            elif "start_bot_permanent" in job:
                print("⏰ Contact Manager Bot - 起動時自動開始")
    
    # ディスク使用状況
    print("\n【ディスク使用状況】")
    disk_usage = run_command("df -h / | tail -1 | awk '{print $5}'")
    print(f"ディスク使用率: {disk_usage}")
    
    # バックアップサイズ
    backup_size = run_command("du -sh /home/fujinosuke/google_drive_backup 2>/dev/null | cut -f1")
    if backup_size:
        print(f"Google Driveバックアップ: {backup_size}")
    
    # ネットワーク情報
    print("\n【ネットワーク情報】")
    local_ip = run_command("hostname -I | awk '{print $1}'")
    print(f"ローカルIP: {local_ip}")
    
    # Web APIエンドポイント
    print("\n【Web APIエンドポイント】")
    api_files = run_command("ls -1 /var/www/html/*.php 2>/dev/null | grep -E '(api|reservation)' | xargs -n1 basename")
    if api_files:
        for api in api_files.split('\n'):
            if api:
                print(f"📡 /{api}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()