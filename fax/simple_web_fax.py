#!/usr/bin/env python3
"""
シンプルWEB自動化FAXシステム
FaxZero経由での無料FAX送信 (1日5通まで)

MacMini2014サーバー用 - Claude経由専用
2025年6月10日作成
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
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
except ImportError as e:
    print(f"❌ Selenium未インストール: {e}")
    sys.exit(1)

class SimpleFaxSystem:
    def __init__(self):
        self.service_name = "FaxZero自動化"
        self.daily_limit = 5
        self.config_file = "/home/fujinosuke/simple_fax_config.json"
        self.log_file = "/home/fujinosuke/simple_fax_log.csv"
        
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
        """WebDriver設定"""
        try:
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            
            # Selenium 4対応: Service使用
            service = Service('/snap/bin/chromium.chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            print(f"❌ WebDriver設定エラー: {e}")
            return None
    
    def send_fax_faxzero(self, fax_number, file_path):
        """FaxZero経由FAX送信"""
        self.reset_daily_count()
        
        if self.config["daily_count"] >= self.daily_limit:
            return False, f"❌ 日次上限到達 ({self.config['daily_count']}/{self.daily_limit})"
        
        if not os.path.exists(file_path):
            return False, f"❌ ファイル未発見: {file_path}"
        
        print(f"📤 FaxZero自動送信開始...")
        print(f"📞 宛先: {fax_number}")
        print(f"📄 ファイル: {os.path.basename(file_path)}")
        
        driver = self.setup_driver()
        if not driver:
            return False, "❌ ブラウザ起動失敗"
        
        try:
            # FaxZeroアクセス
            print("🌐 FaxZero.comにアクセス中...")
            driver.get("https://faxzero.com/fax_send.php")
            
            # ページ読み込み待機
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "fax_number"))
            )
            
            print("📝 フォーム入力中...")
            
            # FAX番号入力 (エリアコードと番号を分離)
            if fax_number.startswith("011"):
                area_code = "011"
                number = fax_number[3:]
            else:
                area_code = fax_number[:3]
                number = fax_number[3:]
            
            driver.find_element(By.NAME, "fax_number").send_keys(f"{area_code}-{number}")
            
            # 送信者情報
            driver.find_element(By.NAME, "sender_name").send_keys("MacMini2014 System")
            driver.find_element(By.NAME, "from_name").send_keys("Test Sender")
            
            # ファイルアップロード
            print("📎 ファイルアップロード中...")
            file_input = driver.find_element(By.NAME, "file")
            file_input.send_keys(os.path.abspath(file_path))
            
            # 送信ボタンを探す
            print("🔍 送信ボタンを探しています...")
            send_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Send Free Fax Now']"))
            )
            
            print("📤 FAX送信実行中...")
            send_button.click()
            
            # 結果待機 (最大60秒)
            print("⏳ 送信結果待機中...")
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 結果確認
            page_source = driver.page_source.lower()
            
            if "success" in page_source or "sent" in page_source or "delivered" in page_source:
                self.config["daily_count"] += 1
                self.save_config()
                self.log_fax(fax_number, file_path, "成功", "FaxZero送信完了")
                return True, "✅ FAX送信成功！"
            
            elif "captcha" in page_source or "verify" in page_source:
                self.log_fax(fax_number, file_path, "認証必要", "CAPTCHA認証が必要")
                return False, "❌ CAPTCHA認証が必要です"
            
            else:
                self.log_fax(fax_number, file_path, "失敗", "送信エラー")
                return False, "❌ FAX送信失敗"
                
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
📠 シンプルWEB自動化FAXシステム
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 サービス: {self.service_name}
🆓 料金: 完全無料
📊 今日の送信: {self.config["daily_count"]}/{self.daily_limit}
📅 対象日: {self.config["last_date"]}

📋 使用方法:
~/fax_venv/bin/python3 simple_web_fax.py send FAX番号 ファイルパス

⚠️ 注意事項:
- 1日5通まで無料送信可能
- CAPTCHA認証が必要な場合があります
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def main():
    """メイン実行"""
    fax_system = SimpleFaxSystem()
    
    if len(sys.argv) == 1:
        print(fax_system.get_status())
        return
    
    if len(sys.argv) == 4 and sys.argv[1] == "send":
        fax_number = sys.argv[2]
        file_path = sys.argv[3]
        
        success, message = fax_system.send_fax_faxzero(fax_number, file_path)
        print(message)
        return
    
    print("""
📠 使用方法:

FAX送信:
~/fax_venv/bin/python3 simple_web_fax.py send 0116887873 test.txt

システム状況:
~/fax_venv/bin/python3 simple_web_fax.py
""")

if __name__ == "__main__":
    main()