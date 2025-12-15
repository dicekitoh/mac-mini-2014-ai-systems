#!/usr/bin/env python3
"""
実際のFAX送信システム - 真の送信版
FaxZero.com の実際のフォームを使った本物のFAX送信

MacMini2014サーバー用 - Claude経由専用
2025年6月10日 - 実際送信版
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from urllib.parse import urljoin
import re

# 仮想環境パス追加
sys.path.insert(0, '/home/fujinosuke/fax_venv/lib/python3.12/site-packages')

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError as e:
    print(f"❌ Selenium未インストール: {e}")
    sys.exit(1)

class RealFaxSender:
    def __init__(self):
        self.service_name = "実際のFAX送信システム"
        self.daily_limit = 5
        self.config_file = "/home/fujinosuke/real_fax_config.json"
        self.log_file = "/home/fujinosuke/real_fax_log.csv"
        
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
                    "last_date": datetime.now().strftime("%Y-%m-%d"),
                    "real_sent": 0
                }
                self.save_config()
        except Exception as e:
            print(f"❌ 設定エラー: {e}")
            self.config = {"daily_count": 0, "last_date": datetime.now().strftime("%Y-%m-%d"), "real_sent": 0}
    
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
    
    def setup_real_driver(self):
        """実際送信用WebDriver設定"""
        try:
            print("🔧 実際送信用ブラウザ起動中...")
            
            options = Options()
            # デバッグ用にヘッドレス無効
            # options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1280,720')
            options.add_argument('--user-data-dir=/tmp/chrome_real_fax_' + str(int(time.time())))
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
            
            service = Service('/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
            
            print("✅ ブラウザ起動完了")
            return driver
            
        except Exception as e:
            print(f"❌ WebDriver設定エラー: {e}")
            return None
    
    def convert_to_pdf(self, file_path):
        """テキストファイルをPDFに変換"""
        try:
            from fpdf import FPDF
            
            if file_path.lower().endswith('.pdf'):
                return file_path
            
            if file_path.lower().endswith('.txt'):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font('Arial', size=12)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        # ASCII文字のみ使用
                        clean_line = line.encode('ascii', 'ignore').decode('ascii')
                        pdf.cell(0, 10, clean_line.strip(), ln=True)
                
                pdf_path = file_path.replace('.txt', '_for_fax.pdf')
                pdf.output(pdf_path)
                print(f"✅ PDF変換完了: {pdf_path}")
                return pdf_path
            
            return file_path
            
        except Exception as e:
            print(f"❌ PDF変換エラー: {e}")
            return file_path
    
    def send_real_fax(self, fax_number, file_path):
        """実際のFAX送信実行"""
        self.reset_daily_count()
        
        if self.config["daily_count"] >= self.daily_limit:
            return False, f"❌ 日次上限到達 ({self.config['daily_count']}/{self.daily_limit})"
        
        if not os.path.exists(file_path):
            return False, f"❌ ファイル未発見: {file_path}"
        
        print(f"📤 実際のFAX送信開始...")
        print(f"📞 宛先: {fax_number}")
        print(f"📄 ファイル: {os.path.basename(file_path)}")
        print(f"⏰ 送信時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # PDF変換
        pdf_file = self.convert_to_pdf(file_path)
        
        driver = self.setup_real_driver()
        if not driver:
            return False, "❌ ブラウザ起動失敗"
        
        try:
            # FaxZero.comにアクセス
            print("\n🌐 FaxZero.com にアクセス中...")
            driver.get("https://faxzero.com")
            
            # ページ読み込み待機
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            print("✅ フォームページ読み込み完了")
            
            # 送信者情報入力
            print("\n👤 送信者情報入力中...")
            
            # 送信者名
            try:
                sender_name = driver.find_element(By.NAME, "sender_name")
                sender_name.clear()
                sender_name.send_keys("MacMini2014 System")
                print("✅ 送信者名入力完了")
            except NoSuchElementException:
                print("⚠️ 送信者名フィールドが見つかりません")
            
            # 送信者メール
            email_fields = ["sender_email", "email", "from_email"]
            for field in email_fields:
                try:
                    email_input = driver.find_element(By.NAME, field)
                    email_input.clear()
                    email_input.send_keys("test@example.com")
                    print(f"✅ メールアドレス入力完了: {field}")
                    break
                except NoSuchElementException:
                    continue
            
            # 送信者電話番号
            phone_fields = ["sender_phone", "phone", "from_phone"]
            for field in phone_fields:
                try:
                    phone_input = driver.find_element(By.NAME, field)
                    phone_input.clear()
                    phone_input.send_keys("0116887870")
                    print(f"✅ 電話番号入力完了: {field}")
                    break
                except NoSuchElementException:
                    continue
            
            # 受信者情報入力
            print("\n📞 受信者情報入力中...")
            
            # 受信者名
            try:
                recipient_name = driver.find_element(By.NAME, "recipient_name")
                recipient_name.clear()
                recipient_name.send_keys("Test Recipient")
                print("✅ 受信者名入力完了")
            except NoSuchElementException:
                print("⚠️ 受信者名フィールドが見つかりません")
            
            # FAX番号入力
            fax_fields = ["fax_number", "recipient_fax", "to_fax", "fax"]
            fax_entered = False
            
            for field in fax_fields:
                try:
                    fax_input = driver.find_element(By.NAME, field)
                    fax_input.clear()
                    
                    # 番号フォーマット
                    if fax_number.startswith("011"):
                        formatted_fax = fax_number[1:]  # 0を除去してUS形式に
                    else:
                        formatted_fax = fax_number
                    
                    fax_input.send_keys(formatted_fax)
                    print(f"✅ FAX番号入力完了: {formatted_fax}")
                    fax_entered = True
                    break
                except NoSuchElementException:
                    continue
            
            if not fax_entered:
                return False, "❌ FAX番号入力フィールドが見つかりません"
            
            # ファイルアップロード
            print(f"\n📎 ファイルアップロード中...")
            file_uploaded = False
            file_fields = ["file", "attachment", "document", "fax_file"]
            
            for field in file_fields:
                try:
                    file_input = driver.find_element(By.NAME, field)
                    file_input.send_keys(os.path.abspath(pdf_file))
                    print(f"✅ ファイルアップロード成功: {field}")
                    file_uploaded = True
                    break
                except NoSuchElementException:
                    continue
            
            if not file_uploaded:
                return False, "❌ ファイルアップロードフィールドが見つかりません"
            
            # フォーム確認
            print(f"\n🔍 送信前フォーム確認...")
            time.sleep(3)  # フォーム安定化
            
            # 無料送信ボタン検索・クリック
            print(f"\n📤 送信ボタン検索中...")
            send_button_found = False
            
            send_button_texts = [
                "Send Free Fax",
                "Send Fax",
                "Send",
                "Submit"
            ]
            
            for button_text in send_button_texts:
                try:
                    # テキストで検索
                    send_button = driver.find_element(By.XPATH, f"//input[@value='{button_text}']")
                    if send_button.is_displayed() and send_button.is_enabled():
                        print(f"✅ 送信ボタン発見: {button_text}")
                        print(f"📤 実際のFAX送信実行中...")
                        
                        # 実際のクリック
                        send_button.click()
                        send_button_found = True
                        break
                except NoSuchElementException:
                    continue
            
            if not send_button_found:
                # ボタンタイプでも検索
                try:
                    send_button = driver.find_element(By.XPATH, "//input[@type='submit']")
                    print("✅ Submit ボタン発見")
                    print(f"📤 実際のFAX送信実行中...")
                    send_button.click()
                    send_button_found = True
                except NoSuchElementException:
                    pass
            
            if not send_button_found:
                return False, "❌ 送信ボタンが見つかりません"
            
            # 送信結果待機
            print(f"\n⏳ 送信結果待機中...")
            
            try:
                # URL変化またはページ変化を待機
                WebDriverWait(driver, 60).until(
                    lambda d: d.current_url != "https://faxzero.com" or "success" in d.page_source.lower() or "sent" in d.page_source.lower()
                )
                
                time.sleep(5)  # 結果ページ安定化
                
                current_url = driver.current_url
                page_source = driver.page_source.lower()
                
                print(f"📄 結果URL: {current_url}")
                
                # 成功判定
                success_indicators = [
                    "success", "sent", "delivered", "transmitted",
                    "your fax has been sent", "confirmation"
                ]
                
                failure_indicators = [
                    "error", "failed", "invalid", "captcha",
                    "verify", "robot", "security"
                ]
                
                success_found = any(indicator in page_source for indicator in success_indicators)
                failure_found = any(indicator in page_source for indicator in failure_indicators)
                
                if success_found:
                    # 成功処理
                    self.config["daily_count"] += 1
                    self.config["real_sent"] += 1
                    self.save_config()
                    
                    self.log_real_fax(fax_number, file_path, "実際送信成功", current_url)
                    
                    return True, f"✅ 実際のFAX送信成功！ URL: {current_url}"
                
                elif failure_found:
                    self.log_real_fax(fax_number, file_path, "送信失敗", current_url)
                    return False, f"❌ FAX送信失敗 URL: {current_url}"
                
                else:
                    self.log_real_fax(fax_number, file_path, "結果不明", current_url)
                    return False, f"⚠️ 送信結果不明 URL: {current_url}"
                
            except TimeoutException:
                return False, "❌ 送信結果待機タイムアウト"
                
        except Exception as e:
            error_msg = f"送信エラー: {str(e)}"
            self.log_real_fax(fax_number, file_path, "システムエラー", error_msg)
            return False, f"❌ {error_msg}"
        
        finally:
            print(f"\n🔍 10秒後にブラウザを閉じます...")
            time.sleep(10)  # デバッグ用待機
            driver.quit()
    
    def log_real_fax(self, fax_number, file_path, status, details):
        """実際送信ログ記録"""
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
📈 実際送信数: {self.config["real_sent"]}
📅 対象日: {self.config["last_date"]}

📋 実際送信機能:
- FaxZero.com 実フォーム連携
- 自動フォーム入力
- 実際のファイルアップロード
- 真の送信ボタンクリック
- 送信結果確認

⚠️ 注意: これは実際にFAXが送信されます
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def main():
    """メイン実行"""
    fax_system = RealFaxSender()
    
    if len(sys.argv) == 1:
        print(fax_system.get_status())
        return
    
    if len(sys.argv) == 4 and sys.argv[1] == "send":
        fax_number = sys.argv[2]
        file_path = sys.argv[3]
        
        print("⚠️ 実際のFAX送信を行います。よろしいですか？")
        print("5秒後に開始...")
        time.sleep(5)
        
        success, message = fax_system.send_real_fax(fax_number, file_path)
        print(f"\n🎯 最終結果: {message}")
        return
    
    print("""
📠 実際のFAX送信システム使用方法:

⚠️ 実際送信:
~/fax_venv/bin/python3 real_fax_sender.py send 0116887873 test.txt

システム状況:
~/fax_venv/bin/python3 real_fax_sender.py
""")

if __name__ == "__main__":
    main()