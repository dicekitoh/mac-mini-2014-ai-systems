#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TODO BOT監視・自動復旧システム

import os
import time
import subprocess
import logging
from datetime import datetime
import psutil
import requests

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('todo_bot_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TodoBotMonitor:
    """TODO BOT監視・自動復旧クラス"""
    
    def __init__(self):
        self.bot_script = "local_todo_bot.py"
        self.bot_token = "***REMOVED***"
        self.max_retries = 3
        self.retry_delay = 30
        self.health_check_interval = 60
        
    def is_bot_running(self):
        """BOTプロセスが実行中か確認"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info.get('cmdline', [])
                if cmdline and self.bot_script in '.join(cmdline):
                    return True, proc.info['pid']
            return False, None
        except Exception as e:
            logger.error(f"プロセス確認エラー: {e}")
            return False, None
    
    def check_bot_health(self):
        """BOTの健全性チェック（Telegram API接続テスト）"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                logger.info("Telegram API接続: 正常")
                return True
            else:
                logger.error(f"Telegram API接続エラー: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"健全性チェックエラー: {e}")
            return False
    
    def start_bot(self):
        """BOTを起動"""
        try:
            cmd = f"source ~/todo_env/bin/activate && nohup python3 ~/{self.bot_script} > local_todo_bot.log 2>&1 &"
            subprocess.run(cmd, shell=True, executable='/bin/bash')
            time.sleep(5)  # 起動待機
            
            running, pid = self.is_bot_running()
            if running:
                logger.info(f"BOT起動成功 (PID: {pid})")
                return True
            else:
                logger.error("BOT起動失敗")
                return False
        except Exception as e:
            logger.error(f"BOT起動エラー: {e}")
            return False
    
    def stop_bot(self):
        """BOTを停止"""
        try:
            running, pid = self.is_bot_running()
            if running and pid:
                os.kill(pid, 9)
                logger.info(f"BOT停止 (PID: {pid})")
                time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"BOT停止エラー: {e}")
            return False
    
    def restart_bot(self):
        """BOTを再起動"""
        logger.info("BOT再起動開始")
        self.stop_bot()
        return self.start_bot()
    
    def monitor_loop(self):
        """監視ループ"""
        logger.info("TODO BOT監視システム起動")
        consecutive_failures = 0
        
        while True:
            try:
                running, pid = self.is_bot_running()
                
                if not running:
                    logger.warning("BOTが停止しています")
                    consecutive_failures += 1
                    
                    if consecutive_failures <= self.max_retries:
                        logger.info(f"自動復旧試行 {consecutive_failures}/{self.max_retries}")
                        if self.start_bot():
                            consecutive_failures = 0
                            logger.info("自動復旧成功")
                        else:
                            logger.error("自動復旧失敗")
                            time.sleep(self.retry_delay)
                    else:
                        logger.critical(f"自動復旧失敗: 最大試行回数({self.max_retries})超過")
                        # 管理者への通知機能をここに追加可能
                        time.sleep(300)  # 5分待機後に再試行
                        consecutive_failures = 0
                else:
                    # BOTは実行中
                    if consecutive_failures > 0:
                        consecutive_failures = 0
                    
                    # 健全性チェック
                    if not self.check_bot_health():
                        logger.warning("BOT健全性チェック失敗 - 再起動します")
                        self.restart_bot()
                
                time.sleep(self.health_check_interval)
                
            except KeyboardInterrupt:
                logger.info("監視システム停止")
                break
            except Exception as e:
                logger.error(f"監視エラー: {e}")
                time.sleep(30)

def main():
    """メイン関数"""
    monitor = TodoBotMonitor()
    
    # 初回起動チェック
    running, pid = monitor.is_bot_running()
    if not running:
        logger.info("BOTが起動していません - 起動します")
        monitor.start_bot()
    else:
        logger.info(f"BOTは既に実行中です (PID: {pid})")
    
    # 監視開始
    monitor.monitor_loop()

if __name__ == '__main__':
    main()
