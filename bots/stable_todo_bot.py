#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stable Telegram Google TODO Bot - トークン自動更新版

import logging
import pickle
import os
import requests
import time
import threading
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google.auth.transport.requests import Request

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stable_todo_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 設定
TOKEN = '***REMOVED***'
GOOGLE_TOKEN_FILE = '/home/fujinosuke/google_tasks_new.pickle'
TOKEN_REFRESH_INTERVAL = 3000  # 50分（1時間のトークン有効期限に対して余裕を持たせる）

class StableTodoManager:
    def __init__(self, token_file=GOOGLE_TOKEN_FILE):
        """安定版Google Tasks API管理クラス"""
        self.token_file = token_file
        self.creds = None
        self.last_refresh_time = None
        self._refresh_lock = threading.Lock()
        self._load_and_refresh_credentials()
        
        # 定期リフレッシュスレッドを開始
        self._start_refresh_thread()
    
    def _load_and_refresh_credentials(self):
        """認証情報を読み込み、必要に応じてリフレッシュ"""
        with self._refresh_lock:
            try:
                if not os.path.exists(self.token_file):
                    logger.error(f"認証ファイル {self.token_file} が見つかりません")
                    return False
                    
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
                
                # 常にリフレッシュして最新の状態にする
                if self.creds and self.creds.refresh_token:
                    logger.info("トークンをリフレッシュしています...")
                    self.creds.refresh(Request())
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(self.creds, token)
                    self.last_refresh_time = datetime.now()
                    logger.info(f"トークンリフレッシュ完了: {self.last_refresh_time}")
                    return True
                    
                return self.creds is not None
                
            except Exception as e:
                logger.error(f"認証情報の読み込み/リフレッシュエラー: {e}")
                return False
    
    def _start_refresh_thread(self):
        """定期的なトークンリフレッシュのスレッドを開始"""
        def refresh_loop():
            while True:
                time.sleep(TOKEN_REFRESH_INTERVAL)
                logger.info("定期トークンリフレッシュを実行...")
                self._load_and_refresh_credentials()
        
        refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        refresh_thread.start()
        logger.info(f"トークン自動リフレッシュスレッド開始（間隔: {TOKEN_REFRESH_INTERVAL}秒）")
    
    def _make_api_request_with_retry(self, url, method='GET', data=None, retry_count=0):
        """API リクエストを実行（自動リトライ機能付き）"""
        try:
            if not self.creds:
                logger.error("認証情報が利用できません")
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
            elif response.status_code == 401 and retry_count < 3:
                # 認証エラーの場合、トークンをリフレッシュして再試行
                logger.warning(f"認証エラー検出（401）、トークンリフレッシュして再試行... (試行 {retry_count + 1}/3)")
                if self._load_and_refresh_credentials():
                    time.sleep(1)  # 少し待機
                    return self._make_api_request_with_retry(url, method, data, retry_count + 1)
                else:
                    logger.error("トークンリフレッシュに失敗しました")
                    return None
            else:
                logger.error(f"API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API リクエストエラー: {e}")
            if retry_count < 3:
                logger.info(f"再試行します... (試行 {retry_count + 1}/3)")
                time.sleep(2)
                return self._make_api_request_with_retry(url, method, data, retry_count + 1)
            return None
    
    def get_task_lists(self):
        """タスクリスト一覧を取得"""
        result = self._make_api_request_with_retry(
            'https://www.googleapis.com/tasks/v1/users/@me/lists'
        )
        if result:
            return result.get('items', [])
        return []
    
    def add_task(self, title):
        """新しいタスクを追加"""
        task_lists = self.get_task_lists()
        if not task_lists:
            logger.error("タスクリストが取得できませんでした")
            return None
            
        tasklist_id = task_lists[0]['id']
        task = {'title': title}
        url = f'https://www.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks'
        return self._make_api_request_with_retry(url, method='POST', data=task)

# グローバルTODO Managerインスタンス
todo_manager = None

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """全メッセージを処理（即TODO登録）"""
    global todo_manager
    
    try:
        # メッセージテキストを取得
        text = update.message.text.strip()
        
        if not text:
            await update.message.reply_text("❌ 空のメッセージはTODOに追加できません。")
            return
        
        # 処理中メッセージを送信
        processing_msg = await update.message.reply_text(f"⏳ 処理中...")
        
        # Google Tasksに追加
        result = todo_manager.add_task(text)
        
        if result:
            # 成功メッセージ
            await processing_msg.edit_text(
                f"✅ TODOに追加しました\n\n"
                f"📝 {text}\n\n"
                f"🔗 https://tasks.google.com\n"
                f"⏰ {datetime.now().strftime('%H:%M:%S')}"
            )
            logger.info(f"TODO追加成功: {text}")
        else:
            # 失敗メッセージ
            await processing_msg.edit_text(
                f"❌ TODO追加に失敗しました\n\n"
                f"📝 {text}\n\n"
                f"🔧 自動復旧を試みましたが失敗しました。\n"
                f"管理者に連絡してください。"
            )
            logger.error(f"TODO追加失敗: {text}")
            
    except Exception as e:
        logger.error(f"メッセージ処理エラー: {e}")
        await update.message.reply_text(
            f"❌ システムエラーが発生しました。\n"
            f"エラー詳細: {str(e)[:100]}..."
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """エラーハンドリング"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """安定版BOT起動"""
    global todo_manager
    
    logger.info("=== Stable Google Todo Bot 起動開始 ===")
    
    # TODO Manager初期化
    todo_manager = StableTodoManager()
    if not todo_manager.creds:
        logger.error("Google認証の初期化に失敗しました。終了します。")
        return
    
    logger.info("✅ Google Tasks API認証成功")
    logger.info(f"✅ 自動リフレッシュ間隔: {TOKEN_REFRESH_INTERVAL}秒")
    logger.info("✅ エラー時自動リトライ: 有効（最大3回）")
    
    # Telegram Bot初期化
    application = Application.builder().token(TOKEN).build()
    
    # ハンドラー追加
    application.add_handler(MessageHandler(filters.TEXT, handle_all_messages))
    application.add_error_handler(error_handler)
    
    logger.info("=== Stable TODO Bot 起動完了 ===")
    logger.info("📱 メッセージを受信待機中...")
    logger.info("🔄 トークンは自動的に更新されます")
    
    # Bot実行
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()