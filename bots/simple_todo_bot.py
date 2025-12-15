#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Simple Telegram Google TODO Bot - 入力即登録版

import logging
import pickle
import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google.auth.transport.requests import Request

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_todo_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 設定
TOKEN = '***REMOVED***'
GOOGLE_TOKEN_FILE = '/home/fujinosuke/google_tasks_new.pickle'

class SimpleTodoManager:
    def __init__(self, token_file=GOOGLE_TOKEN_FILE):
        """シンプルGoogle Tasks API管理クラス"""
        self.token_file = token_file
        self.creds = self._load_credentials()
    
    def _load_credentials(self):
        """認証情報を読み込み"""
        try:
            if not os.path.exists(self.token_file):
                logger.error(f"認証ファイル {self.token_file} が見つかりません")
                return None
                
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
            
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            return creds
        except Exception as e:
            logger.error(f"認証情報読み込みエラー: {e}")
            return None
    
    def _make_api_request(self, url, method='GET', data=None):
        """API リクエストを実行"""
        try:
            if not self.creds:
                return None
            
            headers = {
                'Authorization': f'Bearer {self.creds.token}',
                'Content-Type': 'application/json'
            }
            
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API リクエストエラー: {e}")
            return None
    
    def get_task_lists(self):
        """タスクリスト一覧を取得"""
        result = self._make_api_request('https://www.googleapis.com/tasks/v1/users/@me/lists')
        if result:
            return result.get('items', [])
        return []
    
    def add_task(self, title):
        """新しいタスクを追加"""
        task_lists = self.get_task_lists()
        if not task_lists:
            return None
            
        tasklist_id = task_lists[0]['id']
        task = {'title': title}
        url = f'https://www.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks'
        return self._make_api_request(url, method='POST', data=task)

# TODO Managerインスタンス
todo_manager = SimpleTodoManager()

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """全メッセージを処理（即TODO登録）"""
    try:
        # メッセージテキストを取得
        text = update.message.text.strip()
        
        if not text:
            await update.message.reply_text("❌ 空のメッセージはTODOに追加できません。")
            return
        
        # Google Tasksに追加
        result = todo_manager.add_task(text)
        
        if result:
            # 成功メッセージ
            await update.message.reply_text(f"✅ TODOに追加しました\n\n📝 {text}\n\n🔗 https://tasks.google.com")
            logger.info(f"TODO追加成功: {text}")
        else:
            # 失敗メッセージ
            await update.message.reply_text(f"❌ TODO追加に失敗しました\n\n📝 {text}")
            logger.error(f"TODO追加失敗: {text}")
            
    except Exception as e:
        logger.error(f"メッセージ処理エラー: {e}")
        await update.message.reply_text("❌ エラーが発生しました。しばらく後でお試しください。")

def main():
    """BOT起動"""
    # Google認証確認
    if not todo_manager.creds:
        logger.error("Google認証に失敗しました。終了します。")
        return
    
    logger.info("Google Tasks API認証成功")
    
    # Telegram Bot初期化
    application = Application.builder().token(TOKEN).build()
    
    # 全てのテキストメッセージを処理（コマンドも含む）
    application.add_handler(MessageHandler(filters.TEXT, handle_all_messages))
    
    logger.info("Simple TODO Bot を起動します...")
    logger.info("入力されたテキストは全てTODOとして登録されます")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()