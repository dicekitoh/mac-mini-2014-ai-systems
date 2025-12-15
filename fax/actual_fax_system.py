#!/usr/bin/env python3
"""
実際のFAX送信システム
FaxZero.com経由での実際のFAX送信テスト

MacMini2014サーバー用 - Claude経由専用
2025年6月10日実装版
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
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError as e:
    print(f"❌ 必要ライブラリ未インストール: {e}")
    sys.exit(1)

class ActualFaxSystem:
    def __init__(self):
        self.service_name = "実際のFAX送信システム"
        self.daily_limit = 5
        self.config_file = "/home/fujinosuke/actual_fax_config.json"
        self.log_file = "/home/fujinosuke/actual_fax_log.csv"
        
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
        """実際送信用WebDriver設定"""
        try:
            print("🔧 実際送信用ブラウザ起動中...")
            
            options = Options()
            options.add_argument('--headless')  # ヘッドレスモードに戻す
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1280,720')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--user-data-dir=/tmp/chrome_user_data_' + str(int(time.time())))
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
            
            # 手動設定（確実な方法）
            service = Service('/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
            
            print("✅ ブラウザ起動完了")
            return driver
            
        except Exception as e:
            print(f"❌ WebDriver設定エラー: {e}")
            return None
    
    def send_actual_fax(self, fax_number, file_path):
        """実際のFAX送信実行"""
        self.reset_daily_count()
        
        if self.config["daily_count"] >= self.daily_limit:
            return False, f"❌ 日次上限到達 ({self.config['daily_count']}/{self.daily_limit})"
        
        if not os.path.exists(file_path):
            return False, f"❌ ファイル未発見: {file_path}"
        
        print(f"📤 実際のFAX送信開始...")
        print(f"📞 宛先: {fax_number}")
        print(f"📄 ファイル: {os.path.basename(file_path)} ({os.path.getsize(file_path)} bytes)")
        
        driver = self.setup_driver()
        if not driver:
            return False, "❌ ブラウザ起動失敗"
        
        try:
            # FaxZero.comにアクセス
            print("🌐 FaxZero.com にアクセス中...")
            driver.get("https://faxzero.com/fax_send.php")
            
            # ページ読み込み待機
            print("⏳ ページ読み込み待機中...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            print("📝 フォーム要素を確認中...")
            
            # FAX番号入力（複数の可能性を試行）
            fax_input_found = False
            possible_fax_selectors = [
                "fax_number",
                "number", 
                "phone",
                "to_number"
            ]
            
            for selector in possible_fax_selectors:
                try:
                    fax_input = driver.find_element(By.NAME, selector)
                    print(f"✅ FAX番号入力欄発見: {selector}")
                    
                    # 番号をフォーマット（エリアコード + 番号）
                    if fax_number.startswith("011"):
                        formatted_number = f"011-{fax_number[3:]}"
                    else:
                        formatted_number = fax_number
                    
                    fax_input.clear()
                    fax_input.send_keys(formatted_number)
                    fax_input_found = True
                    break
                except NoSuchElementException:
                    continue
            
            if not fax_input_found:
                return False, "❌ FAX番号入力欄が見つかりません"
            
            # 送信者情報入力
            print("👤 送信者情報入力中...")
            sender_fields = {
                "sender_name": "MacMini2014 System",
                "from_name": "Test Sender", 
                "your_email": "test@example.com",
                "sender_email": "test@example.com"
            }
            
            for field_name, value in sender_fields.items():
                try:
                    field = driver.find_element(By.NAME, field_name)
                    field.clear()
                    field.send_keys(value)
                    print(f"✅ {field_name}: {value}")
                except NoSuchElementException:
                    print(f"⚠️ {field_name} フィールドなし")
                    continue
            
            # ファイルアップロード
            print("📎 ファイルアップロード中...")
            file_selectors = ["file", "document", "attachment"]
            file_uploaded = False
            
            for selector in file_selectors:
                try:
                    file_input = driver.find_element(By.NAME, selector)
                    file_input.send_keys(os.path.abspath(file_path))
                    print(f"✅ ファイルアップロード成功: {selector}")
                    file_uploaded = True
                    break
                except NoSuchElementException:
                    continue
            
            if not file_uploaded:
                return False, "❌ ファイルアップロード欄が見つかりません"
            
            # 送信前の確認
            print("🔍 送信ボタンを探しています...")
            time.sleep(2)  # フォーム安定化待機
            
            # 送信ボタン検索
            send_button_found = False
            send_selectors = [
                "//input[@type='submit']",
                "//button[@type='submit']", 
                "//input[@value='Send']",
                "//input[@value='Send Free Fax']",
                "//button[contains(text(), 'Send')]"
            ]
            
            for selector in send_selectors:
                try:
                    send_button = driver.find_element(By.XPATH, selector)
                    if send_button.is_displayed() and send_button.is_enabled():
                        print(f"✅ 送信ボタン発見: {selector}")
                        
                        # 実際の送信実行
                        print("📤 FAX送信実行中...")
                        send_button.click()
                        send_button_found = True
                        break
                except NoSuchElementException:
                    continue
            
            if not send_button_found:
                return False, "❌ 送信ボタンが見つかりません"
            
            # 送信結果待機
            print("⏳ 送信結果待機中（最大90秒）...")
            
            try:
                # 結果ページの待機
                WebDriverWait(driver, 90).until(
                    lambda d: "faxzero.com" in d.current_url and d.current_url != "https://faxzero.com/fax_send.php"
                )
                
                # 結果確認
                time.sleep(5)  # ページ安定化
                page_source = driver.page_source.lower()
                current_url = driver.current_url
                
                print(f"📄 結果ページURL: {current_url}")
                
                # 成功判定
                success_indicators = [
                    "success", "sent", "delivered", "queued", 
                    "your fax has been sent", "transmission complete"
                ]
                
                failure_indicators = [
                    "error", "failed", "invalid", "captcha", 
                    "verify", "robot", "security check"
                ]
                
                success_found = any(indicator in page_source for indicator in success_indicators)
                failure_found = any(indicator in page_source for indicator in failure_indicators)
                
                if success_found:
                    self.config["daily_count"] += 1
                    self.save_config()
                    self.log_fax(fax_number, file_path, "送信成功", f"URL: {current_url}")
                    return True, "✅ 実際のFAX送信成功！"
                
                elif failure_found:
                    self.log_fax(fax_number, file_path, "送信失敗", f"エラーページ: {current_url}")
                    return False, "❌ FAX送信エラーが発生しました"
                
                else:
                    self.log_fax(fax_number, file_path, "結果不明", f"URL: {current_url}")
                    return False, f"⚠️ 送信結果が不明です（URL: {current_url}）"
                
            except TimeoutException:
                return False, "❌ 送信結果の取得がタイムアウトしました"
                
        except Exception as e:
            error_msg = f"システムエラー: {str(e)}"
            self.log_fax(fax_number, file_path, "システムエラー", error_msg)
            return False, f"❌ {error_msg}"
        
        finally:
            # デバッグ用: 5秒待機してからブラウザを閉じる
            print("🔍 5秒後にブラウザを閉じます...")
            time.sleep(5)
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
📠 実際のFAX送信システム
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 サービス: {self.service_name}
🆓 料金: 完全無料 (FaxZero.com)
📊 今日の送信: {self.config["daily_count"]}/{self.daily_limit}
📅 対象日: {self.config["last_date"]}

📋 機能:
- 実際のFaxZero.com連携
- 自動フォーム入力
- ファイルアップロード
- 送信結果判定

使用方法:
~/fax_venv/bin/python3 actual_fax_system.py send FAX番号 ファイルパス
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def main():
    """メイン実行"""
    fax_system = ActualFaxSystem()
    
    if len(sys.argv) == 1:
        print(fax_system.get_status())
        return
    
    if len(sys.argv) == 4 and sys.argv[1] == "send":
        fax_number = sys.argv[2]
        file_path = sys.argv[3]
        
        success, message = fax_system.send_actual_fax(fax_number, file_path)
        print(message)
        return
    
    print("""
📠 実際のFAX送信システム使用方法:

FAX送信:
~/fax_venv/bin/python3 actual_fax_system.py send 0116887873 test.txt

システム状況:
~/fax_venv/bin/python3 actual_fax_system.py
""")

if __name__ == "__main__":
    main()