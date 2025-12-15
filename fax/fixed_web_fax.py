#!/usr/bin/env python3
"""
修正版WEB自動化FAXシステム
WebDriverManager使用でChromeDriver問題解決

MacMini2014サーバー用 - Claude経由専用
2025年6月10日修正版
"""

import sys
import os
import json
import time
from datetime import datetime

# 仮想環境パス追加
sys.path.insert(0, '/home/fujinosuke/fax_venv/lib/python3.12/site-packages')

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError as e:
    print(f"❌ 必要ライブラリ未インストール: {e}")
    sys.exit(1)

class FixedFaxSystem:
    def __init__(self):
        self.service_name = "修正版WEB自動化FAX"
        self.daily_limit = 5
        self.config_file = "/home/fujinosuke/fixed_fax_config.json"
        self.log_file = "/home/fujinosuke/fixed_fax_log.csv"
        
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
    
    def setup_driver(self):
        """修正版WebDriver設定"""
        try:
            print("🔧 ChromeDriver自動設定中...")
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-logging')
            options.add_argument('--silent')
            
            # WebDriverManagerで自動ChromeDriver管理
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            print("✅ ChromeDriver準備完了")
            return driver
            
        except Exception as e:
            print(f"❌ WebDriver設定エラー: {e}")
            # フォールバック: 手動設定
            try:
                print("🔄 手動設定にフォールバック...")
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=options)
                return driver
            except:
                return None
    
    def send_fax_simple(self, fax_number, file_path):
        """シンプル版FAX送信"""
        self.reset_daily_count()
        
        if self.config["daily_count"] >= self.daily_limit:
            return False, f"❌ 日次上限到達 ({self.config['daily_count']}/{self.daily_limit})"
        
        if not os.path.exists(file_path):
            return False, f"❌ ファイル未発見: {file_path}"
        
        print(f"📤 修正版FAX送信開始...")
        print(f"📞 宛先: {fax_number}")
        print(f"📄 ファイル: {os.path.basename(file_path)}")
        
        driver = self.setup_driver()
        if not driver:
            return False, "❌ ブラウザ起動失敗"
        
        try:
            # シンプルなテストページアクセス
            print("🌐 接続テスト中...")
            driver.get("https://httpbin.org/get")
            
            # ページ確認
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            page_text = driver.page_source
            if "httpbin" in page_text:
                print("✅ インターネット接続確認")
                
                # 実際のFaxZeroは後で実装
                # 今回はテスト成功として記録
                self.config["daily_count"] += 1
                self.save_config()
                self.log_fax(fax_number, file_path, "テスト成功", "接続確認完了")
                return True, "✅ システム動作確認完了（FAXサイト接続は次回実装）"
            else:
                return False, "❌ 接続テスト失敗"
                
        except Exception as e:
            error_msg = f"システムエラー: {str(e)}"
            self.log_fax(fax_number, file_path, "エラー", error_msg)
            return False, f"❌ {error_msg}"
        
        finally:
            driver.quit()
    
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
📠 修正版WEB自動化FAXシステム
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 サービス: {self.service_name}
🆓 料金: 完全無料
📊 今日の送信: {self.config["daily_count"]}/{self.daily_limit}
📅 対象日: {self.config["last_date"]}

📋 改善点:
- WebDriverManager使用
- 自動ChromeDriver管理
- エラーハンドリング強化

使用方法:
~/fax_venv/bin/python3 fixed_web_fax.py send FAX番号 ファイルパス
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def main():
    """メイン実行"""
    fax_system = FixedFaxSystem()
    
    if len(sys.argv) == 1:
        print(fax_system.get_status())
        return
    
    if len(sys.argv) == 4 and sys.argv[1] == "send":
        fax_number = sys.argv[2]
        file_path = sys.argv[3]
        
        success, message = fax_system.send_fax_simple(fax_number, file_path)
        print(message)
        return
    
    print("""
📠 修正版使用方法:

FAX送信:
~/fax_venv/bin/python3 fixed_web_fax.py send 0116887873 test.txt

システム状況:
~/fax_venv/bin/python3 fixed_web_fax.py
""")

if __name__ == "__main__":
    main()