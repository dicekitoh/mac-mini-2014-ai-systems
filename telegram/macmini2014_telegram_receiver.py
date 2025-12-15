#!/usr/bin/env python3
"""
MacMini2014 Notifier Bot メッセージ受信システム
@macmini2014_bot からのメッセージを受信・処理
"""

import requests
import json
import time
import logging
from datetime import datetime
import os

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/fujinosuke/macmini2014_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MacMini2014TelegramBot:
    def __init__(self):
        self.token = "***REMOVED***"
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.offset_file = "/home/fujinosuke/telegram_offset.txt"
        self.last_update_id = self.load_offset()
        
    def load_offset(self):
        """最後に処理したアップデートIDを読み込み"""
        try:
            if os.path.exists(self.offset_file):
                with open(self.offset_file, 'r') as f:
                    return int(f.read().strip())
        except:
            pass
        return 0
    
    def save_offset(self, offset):
        """処理済みアップデートIDを保存"""
        try:
            with open(self.offset_file, 'w') as f:
                f.write(str(offset))
        except Exception as e:
            logger.error(f"オフセット保存エラー: {e}")
    
    def get_updates(self):
        """新しいメッセージを取得"""
        try:
            url = f"{self.api_url}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 10,
                'limit': 100
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data.get('ok'):
                return data.get('result', [])
            else:
                logger.error(f"API エラー: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API リクエストエラー: {e}")
            return []
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return []
    
    def process_message(self, update):
        """メッセージを処理"""
        try:
            message = update.get('message')
            if not message:
                return
            
            # メッセージ情報取得
            chat_id = message['chat']['id']
            user_name = message.get('from', {}).get('first_name', 'Unknown')
            user_id = message.get('from', {}).get('id', 'Unknown')
            text = message.get('text', '')
            message_date = datetime.fromtimestamp(message['date'])
            
            # メッセージログ記録
            logger.info(f"新着メッセージ受信:")
            logger.info(f"  送信者: {user_name} (ID: {user_id})")
            logger.info(f"  日時: {message_date}")
            logger.info(f"  内容: {text}")
            logger.info(f"  Chat ID: {chat_id}")
            
            # メッセージをファイルに保存
            self.save_message_to_file(message_date, user_name, text, chat_id)
            
            # 自動応答（オプション）
            if "テスト" in text:
                self.send_reply(chat_id, f"📱 MacMini2014で受信確認: {text}")
            
        except Exception as e:
            logger.error(f"メッセージ処理エラー: {e}")
    
    def save_message_to_file(self, date, user_name, text, chat_id):
        """メッセージをファイルに保存"""
        try:
            log_file = f"/home/fujinosuke/telegram_messages_{date.strftime('%Y-%m-%d')}.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{date.isoformat()} | {user_name} | {chat_id} | {text}\n")
        except Exception as e:
            logger.error(f"メッセージファイル保存エラー: {e}")
    
    def send_reply(self, chat_id, text):
        """返信メッセージ送信"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.json().get('ok'):
                logger.info(f"返信送信成功: {text}")
            else:
                logger.error(f"返信送信失敗: {response.text}")
                
        except Exception as e:
            logger.error(f"返信送信エラー: {e}")
    
    def run(self):
        """メイン実行ループ"""
        logger.info("MacMini2014 Telegram Bot 受信システム開始")
        logger.info(f"Bot: @macmini2014_bot")
        
        while True:
            try:
                # 新着メッセージ取得
                updates = self.get_updates()
                
                if updates:
                    logger.info(f"{len(updates)}件の新着メッセージを処理中...")
                    
                    for update in updates:
                        self.process_message(update)
                        self.last_update_id = update['update_id']
                    
                    # 処理済みオフセット保存
                    self.save_offset(self.last_update_id)
                
                # 5秒待機
                time.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("システム停止")
                break
            except Exception as e:
                logger.error(f"実行ループエラー: {e}")
                time.sleep(10)

def main():
    """メイン関数"""
    print("MacMini2014 Telegram Bot 受信システム")
    print("Bot: @macmini2014_bot")
    print("停止: Ctrl+C")
    print("-" * 50)
    
    bot = MacMini2014TelegramBot()
    bot.run()

if __name__ == "__main__":
    main()