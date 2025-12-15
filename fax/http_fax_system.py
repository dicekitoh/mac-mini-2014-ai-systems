#!/usr/bin/env python3
"""
HTTP リクエスト式FAX送信システム
Seleniumの代替として直接HTTPでFAXサービスにアクセス

MacMini2014サーバー用 - Claude経由専用
2025年6月10日実装版
"""

import sys
import os
import json
import time
import requests
from datetime import datetime

class HttpFaxSystem:
    def __init__(self):
        self.service_name = "HTTP直接FAX送信"
        self.daily_limit = 5
        self.config_file = "/home/fujinosuke/http_fax_config.json"
        self.log_file = "/home/fujinosuke/http_fax_log.csv"
        
        self.load_config()
    
    def load_config(self):
        """設定読み込み"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "daily_count": 0,
                    "last_date": datetime.now().strftime("%Y-%m-%d")
                }
                self.save_config()
        except Exception as e:
            print(f"❌ 設定エラー: {e}")
            self.config = {"daily_count": 0, "last_date": datetime.now().strftime("%Y-%m-%d")}
    
    def save_config(self):
        """設定保存"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
    
    def reset_daily_count(self):
        """日次リセット"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.config["last_date"] != today:
            self.config["daily_count"] = 0
            self.config["last_date"] = today
            self.save_config()
    
    def test_fax_zero_connection(self):
        """FaxZero.com接続テスト"""
        try:
            print("🌐 FaxZero.com 接続テスト中...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get('https://faxzero.com', headers=headers, timeout=15)
            
            if response.status_code == 200:
                print("✅ FaxZero.com 接続成功")
                
                # ページ内容確認
                content = response.text.lower()
                if 'fax' in content and 'send' in content:
                    print("✅ FAX送信ページ確認")
                    return True, "接続成功"
                else:
                    return False, "FAXページではない"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"接続エラー: {str(e)}"
    
    def send_http_fax(self, fax_number, file_path):
        """HTTP方式でFAX送信テスト"""
        self.reset_daily_count()
        
        if self.config["daily_count"] >= self.daily_limit:
            return False, f"❌ 日次上限到達 ({self.config['daily_count']}/{self.daily_limit})"
        
        if not os.path.exists(file_path):
            return False, f"❌ ファイル未発見: {file_path}"
        
        print(f"📤 HTTP直接FAX送信テスト開始...")
        print(f"📞 宛先: {fax_number}")
        print(f"📄 ファイル: {os.path.basename(file_path)} ({os.path.getsize(file_path)} bytes)")
        
        # 接続テスト
        connection_success, connection_msg = self.test_fax_zero_connection()
        if not connection_success:
            return False, f"❌ 接続失敗: {connection_msg}"
        
        try:
            # ファイル内容読み込み
            print("📄 ファイル内容確認中...")
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            print(f"📝 ファイル内容プレビュー:")
            print("-" * 40)
            print(file_content[:200] + "..." if len(file_content) > 200 else file_content)
            print("-" * 40)
            
            # 実際のHTTP送信は複雑（CSRF、CAPTCHA等）のため
            # 今回は接続確認とファイル処理の成功として記録
            print("📤 FAX送信処理中...")
            time.sleep(3)  # 処理時間のシミュレーション
            
            # 成功として記録
            self.config["daily_count"] += 1
            self.save_config()
            self.log_fax(fax_number, file_path, "HTTP接続成功", f"ファイル:{len(file_content)}文字")
            
            return True, "✅ HTTP接続・ファイル処理成功（実際のFAX送信は次版で実装）"
            
        except Exception as e:
            error_msg = f"処理エラー: {str(e)}"
            self.log_fax(fax_number, file_path, "エラー", error_msg)
            return False, f"❌ {error_msg}"
    
    def log_fax(self, fax_number, file_path, status, details):
        """ログ記録"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp},{fax_number},{os.path.basename(file_path)},{status},{details}\n"
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"⚠️ ログエラー: {e}")
    
    def get_status(self):
        """状況表示"""
        self.reset_daily_count()
        
        return f"""
📠 HTTP直接FAX送信システム
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 サービス: {self.service_name}
🆓 料金: 完全無料 (接続テスト)
📊 今日の送信: {self.config["daily_count"]}/{self.daily_limit}
📅 対象日: {self.config["last_date"]}

📋 機能:
- FaxZero.com 直接HTTP接続
- ファイル内容確認
- 送信処理シミュレーション

使用方法:
~/fax_venv/bin/python3 http_fax_system.py send FAX番号 ファイルパス
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def main():
    """メイン実行"""
    fax_system = HttpFaxSystem()
    
    if len(sys.argv) == 1:
        print(fax_system.get_status())
        return
    
    if len(sys.argv) == 4 and sys.argv[1] == "send":
        fax_number = sys.argv[2]
        file_path = sys.argv[3]
        
        success, message = fax_system.send_http_fax(fax_number, file_path)
        print(message)
        return
    
    print("""
📠 HTTP直接FAX送信システム使用方法:

FAX送信:
~/fax_venv/bin/python3 http_fax_system.py send 0116887873 test.txt

システム状況:
~/fax_venv/bin/python3 http_fax_system.py
""")

if __name__ == "__main__":
    main()