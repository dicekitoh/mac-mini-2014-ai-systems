#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Google Todo Bot with Auto-Recovery
認証エラーの自動復旧機能を備えた改良版
"""

import logging
import pickle
import os
import subprocess
import time
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google.auth.transport.requests import Request
import asyncio

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('improved_todo_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 設定
TOKEN = '***REMOVED***'
GOOGLE_TOKEN_FILE = '/home/fujinosuke/google_tasks_new.pickle'
BACKUP_TOKEN_FILE = '/home/fujinosuke/google_tasks_token.pickle'
MAX_RETRY_ATTEMPTS = 3

class ImprovedTodoManager:
    def __init__(self, token_file=GOOGLE_TOKEN_FILE):
        """改良版Google Tasks API管理クラス"""
        self.token_file = token_file
        self.backup_file = BACKUP_TOKEN_FILE
        self.creds = self._load_credentials()
        self.last_refresh_time = datetime.now()
    
    def _load_credentials(self):
        """認証情報を読み込み（バックアップ対応）"""
        try:
            # メインのトークンファイルをチェック
            if not os.path.exists(self.token_file):
                logger.warning(f"Token file {self.token_file} not found")
                # バックアップから復元を試みる
                if os.path.exists(self.backup_file):
                    logger.info("Restoring from backup token")
                    subprocess.run(['cp', self.backup_file, self.token_file])
                else:
                    logger.error("No backup token available")
                    return None
                    
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
            
            # 有効期限チェックと自動リフレッシュ
            if creds and creds.expired and creds.refresh_token:
                logger.info("Token expired, refreshing...")
                creds.refresh(Request())
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                logger.info("Token refreshed successfully")
                self.last_refresh_time = datetime.now()
            
            return creds
            
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return None
    
    def add_todo_with_retry(self, title, retry_count=0):
        """TODOを追加（リトライ機能付き）"""
        try:
            if not self.creds:
                self.creds = self._load_credentials()
                if not self.creds:
                    return False, "認証情報が利用できません"
            
            # Google Tasks APIへのリクエスト
            url = 'https://tasks.googleapis.com/tasks/v1/lists/@default/tasks'
            headers = {
                'Authorization': f'Bearer {self.creds.token}',
                'Content-Type': 'application/json'
            }
            data = {'title': title}
            
            import requests
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"TODO added successfully: {title}")
                return True, "TODO追加成功"
            elif response.status_code == 401 and retry_count < MAX_RETRY_ATTEMPTS:
                # 認証エラーの場合、トークンをリフレッシュして再試行
                logger.warning("Authentication error, attempting token refresh...")
                self.creds = self._load_credentials()
                if self.creds:
                    # 強制的にリフレッシュ
                    try:
                        self.creds.refresh(Request())
                        with open(self.token_file, 'wb') as token:
                            pickle.dump(self.creds, token)
                        logger.info("Force refresh completed")
                        return self.add_todo_with_retry(title, retry_count + 1)
                    except Exception as e:
                        logger.error(f"Force refresh failed: {e}")
                        return False, f"トークンリフレッシュ失敗: {e}"
                else:
                    return False, "認証情報の再読み込みに失敗"
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            logger.error(f"Error adding TODO: {e}")
            return False, f"エラー: {str(e)}"

# Telegramハンドラー
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """メッセージを受信してTODOを追加"""
    message_text = update.message.text.strip()
    user = update.effective_user
    
    logger.info(f"Received message from {user.username}: {message_text}")
    
    # TODOマネージャーのインスタンス作成
    todo_manager = ImprovedTodoManager()
    
    # TODO追加（リトライ機能付き）
    success, message = todo_manager.add_todo_with_retry(message_text)
    
    if success:
        await update.message.reply_text(f"✅ TODO追加完了\n\n📝 {message_text}")
    else:
        await update.message.reply_text(
            f"❌ TODO追加に失敗しました\n\n"
            f"📝 {message_text}\n\n"
            f"エラー: {message}"
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """エラーハンドリング"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """メイン実行関数"""
    logger.info("Starting Improved Google Todo Bot...")
    
    # アプリケーション作成
    application = Application.builder().token(TOKEN).build()
    
    # ハンドラー追加
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Bot開始
    logger.info("Bot is ready to receive messages")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()