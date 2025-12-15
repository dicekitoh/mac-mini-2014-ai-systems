#!/usr/bin/env python3
"""
MacMini2014 Notifier Bot - MacMini2014サーバー専用版
@macmini2014_bot からのメッセージを受信・処理・ログ記録
完全にMacMini2014サーバー上で動作
"""

import requests
import json
import time
import logging
from datetime import datetime
import os
import sys

# ログ設定
LOG_FILE = '/home/fujinosuke/macmini2014_notifier_bot.log'
MESSAGE_LOG_DIR = '/home/fujinosuke/telegram_messages'

# ディレクトリ作成
os.makedirs(MESSAGE_LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MacMini2014NotifierBot:
    def __init__(self):
        self.bot_name = "MacMini2014 Notifier"
        self.bot_username = "@macmini2014_bot"
        self.token = "***REMOVED***"
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        
        # 設定ファイル
        self.offset_file = "/home/fujinosuke/telegram_bot_offset.txt"
        self.config_file = "/home/fujinosuke/telegram_bot_config.json"
        
        # 初期化
        self.last_update_id = self.load_offset()
        self.stats = {
            'start_time': datetime.now(),
            'messages_processed': 0,
            'last_message_time': None
        }
        
        logger.info(f"=== {self.bot_name} 初期化完了 ===")
        logger.info(f"Bot: {self.bot_username}")
        logger.info(f"サーバー: MacMini2014 (192.168.3.43)")
        logger.info(f"ログファイル: {LOG_FILE}")
        logger.info(f"メッセージ保存: {MESSAGE_LOG_DIR}")
        
    def load_offset(self):
        """最後に処理したアップデートIDを読み込み"""
        try:
            if os.path.exists(self.offset_file):
                with open(self.offset_file, 'r') as f:
                    offset = int(f.read().strip())
                    logger.info(f"前回のオフセット読み込み: {offset}")
                    return offset
        except Exception as e:
            logger.warning(f"オフセット読み込みエラー: {e}")
        return 0
    
    def save_offset(self, offset):
        """処理済みアップデートIDを保存"""
        try:
            with open(self.offset_file, 'w') as f:
                f.write(str(offset))
        except Exception as e:
            logger.error(f"オフセット保存エラー: {e}")
    
    def save_config(self):
        """設定とステータスを保存"""
        try:
            config = {
                'bot_name': self.bot_name,
                'bot_username': self.bot_username,
                'last_update_id': self.last_update_id,
                'stats': {
                    'start_time': self.stats['start_time'].isoformat(),
                    'messages_processed': self.stats['messages_processed'],
                    'last_message_time': self.stats['last_message_time'].isoformat() if self.stats['last_message_time'] else None
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"設定保存エラー: {e}")
    
    def test_connection(self):
        """Telegram API接続テスト"""
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                logger.info("✅ Telegram API接続成功")
                logger.info(f"  Bot名: {bot_info.get('first_name')}")
                logger.info(f"  ユーザー名: @{bot_info.get('username')}")
                logger.info(f"  Bot ID: {bot_info.get('id')}")
                return True
            else:
                logger.error(f"❌ API接続エラー: {data}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 接続テストエラー: {e}")
            return False
    
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
            user_info = message.get('from', {})
            user_name = user_info.get('first_name', 'Unknown')
            username = user_info.get('username', '')
            user_id = user_info.get('id', 'Unknown')
            text = message.get('text', '')
            message_date = datetime.fromtimestamp(message['date'])
            
            # 統計更新
            self.stats['messages_processed'] += 1
            self.stats['last_message_time'] = message_date
            
            # 詳細ログ記録
            logger.info("📨 新着メッセージ受信")
            logger.info(f"  送信者: {user_name} (@{username}) [ID: {user_id}]")
            logger.info(f"  日時: {message_date.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"  内容: {text}")
            logger.info(f"  Chat ID: {chat_id}")
            
            # メッセージをファイルに保存
            self.save_message_to_file(message_date, user_name, username, text, chat_id, user_id)
            
            # MacMini2014サーバー情報を含む自動応答
            response_text = f"🖥️ MacMini2014サーバーで受信確認\n📝 メッセージ: {text}\n⏰ 受信時刻: {datetime.now().strftime('%H:%M:%S')}\n📊 処理数: {self.stats['messages_processed']}"
            
            # 特定キーワードに対する特別応答
            if any(keyword in text.lower() for keyword in ['テスト', 'test', '確認', '状態']):
                self.send_reply(chat_id, response_text)
            elif 'システム' in text or 'サーバー' in text:
                system_info = self.get_system_info()
                self.send_reply(chat_id, f"🖥️ MacMini2014システム情報\n{system_info}")
            
        except Exception as e:
            logger.error(f"メッセージ処理エラー: {e}")
    
    def save_message_to_file(self, date, user_name, username, text, chat_id, user_id):
        """メッセージをファイルに保存"""
        try:
            # 日付別ログファイル
            date_str = date.strftime('%Y-%m-%d')
            log_file = os.path.join(MESSAGE_LOG_DIR, f"messages_{date_str}.log")
            
            # メッセージ情報をJSON形式で保存
            message_data = {
                'timestamp': date.isoformat(),
                'user_name': user_name,
                'username': username,
                'user_id': user_id,
                'chat_id': chat_id,
                'text': text,
                'processed_on_server': 'MacMini2014'
            }
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(message_data, ensure_ascii=False) + '\n')
                
            logger.debug(f"メッセージ保存完了: {log_file}")
            
        except Exception as e:
            logger.error(f"メッセージファイル保存エラー: {e}")
    
    def get_system_info(self):
        """MacMini2014システム情報を取得"""
        try:
            import subprocess
            
            # システム情報取得
            hostname = subprocess.check_output(['hostname'], text=True).strip()
            uptime = subprocess.check_output(['uptime'], text=True).strip()
            disk_usage = subprocess.check_output(['df', '-h', '/'], text=True).strip().split('\n')[1]
            
            return f"ホスト名: {hostname}\n稼働時間: {uptime}\nディスク: {disk_usage}"
            
        except Exception as e:
            return f"システム情報取得エラー: {e}"
    
    def send_reply(self, chat_id, text):
        """返信メッセージ送信"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"✅ 返信送信成功: {text[:50]}...")
            else:
                logger.error(f"❌ 返信送信失敗: {result}")
                
        except Exception as e:
            logger.error(f"返信送信エラー: {e}")
    
    def print_stats(self):
        """統計情報を表示"""
        uptime = datetime.now() - self.stats['start_time']
        logger.info("📊 統計情報")
        logger.info(f"  稼働時間: {uptime}")
        logger.info(f"  処理メッセージ数: {self.stats['messages_processed']}")
        logger.info(f"  最終メッセージ: {self.stats['last_message_time']}")
    
    def run(self):
        """メイン実行ループ"""
        logger.info(f"🚀 {self.bot_name} 受信システム開始")
        
        # 接続テスト
        if not self.test_connection():
            logger.error("❌ Telegram API接続に失敗しました")
            return False
        
        # メインループ
        try:
            while True:
                # 新着メッセージ取得
                updates = self.get_updates()
                
                if updates:
                    logger.info(f"📥 {len(updates)}件の新着メッセージを処理中...")
                    
                    for update in updates:
                        self.process_message(update)
                        self.last_update_id = update['update_id']
                    
                    # 処理済みオフセット保存
                    self.save_offset(self.last_update_id)
                    self.save_config()
                
                # 5分ごとに統計表示
                if int(time.time()) % 300 == 0:
                    self.print_stats()
                
                # 5秒待機
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("🛑 システム停止要求")
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"❌ 実行ループエラー: {e}")
            self.save_config()
            return False

def main():
    """メイン関数"""
    print("=" * 60)
    print("MacMini2014 Telegram Notifier Bot")
    print("@macmini2014_bot メッセージ受信システム")
    print("サーバー: MacMini2014 (192.168.3.43)")
    print("停止: Ctrl+C")
    print("=" * 60)
    
    # 引数処理
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            print("🔍 接続テストモード")
            bot = MacMini2014NotifierBot()
            success = bot.test_connection()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--stats':
            print("📊 統計情報表示")
            # 統計表示処理
            sys.exit(0)
    
    # 通常実行
    bot = MacMini2014NotifierBot()
    success = bot.run()
    
    print("\n" + "=" * 60)
    print("MacMini2014 Telegram Bot システム終了")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()