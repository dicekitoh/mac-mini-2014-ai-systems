#!/usr/bin/env python3
"""
天気監視システム状況確認スクリプト
"""
import os
import subprocess
import json
from datetime import datetime

def check_monitoring_status():
    """監視システムの状況確認"""
    print("🌤️ 天気Discord通知システム状況確認")
    print("=" * 50)
    
    # プロセス状況確認
    try:
        result = subprocess.run(
            ["pgrep", "-f", "weather_discord_notifier.py"], 
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"✅ 監視システム稼働中 (PID: {', '.join(pids)})")
        else:
            print("⏹️ 監視システム停止中")
    except:
        print("❓ プロセス確認エラー")
    
    # PIDファイル確認
    pid_file = "/home/fujinosuke/weather_monitor.pid"
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid = f.read().strip()
            print(f"📝 記録されたPID: {pid}")
        except:
            print("❌ PIDファイル読み取りエラー")
    else:
        print("📝 PIDファイルなし")
    
    # ログファイル確認
    log_file = "/home/fujinosuke/weather_monitoring.log"
    if os.path.exists(log_file):
        try:
            stat = os.stat(log_file)
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            print(f"📄 ログファイル: {size}バイト (最終更新: {modified.strftime('%Y-%m-%d %H:%M:%S')})")
            
            # 最新のログ行を表示
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"📋 最新ログ: {lines[-1].strip()}")
        except:
            print("❌ ログファイル確認エラー")
    else:
        print("📄 ログファイルなし")
    
    # 通知履歴確認
    notify_file = "/home/fujinosuke/weather_notifications_sent.json"
    if os.path.exists(notify_file):
        try:
            with open(notify_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            hot_days = len(data.get("hot_days", []))
            rainy_days = len(data.get("rainy_mornings", []))
            print(f"📊 通知送信履歴: 暑い日{hot_days}件、雨の朝{rainy_days}件")
        except:
            print("❌ 通知履歴確認エラー")
    else:
        print("📊 通知履歴なし")
    
    # 日次サマリー確認
    summary_file = "/home/fujinosuke/daily_summary_sent.txt"
    if os.path.exists(summary_file):
        try:
            with open(summary_file, 'r') as f:
                last_date = f.read().strip()
            print(f"📅 最後のサマリー: {last_date}")
        except:
            print("❌ サマリー履歴確認エラー")
    else:
        print("📅 サマリー履歴なし")
    
    print("\n" + "=" * 50)
    print("💡 使用方法:")
    print("  🚀 開始: bash /home/fujinosuke/start_weather_monitoring.sh")
    print("  🛑 停止: bash /home/fujinosuke/stop_weather_monitoring.sh")
    print("  📊 状況: python3 /home/fujinosuke/weather_monitoring_status.py")
    print("  📋 ログ: tail -f /home/fujinosuke/weather_monitoring.log")

if __name__ == "__main__":
    check_monitoring_status()