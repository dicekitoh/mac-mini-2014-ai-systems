#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Local Storage Telegram TODO Bot - Google API不要版

import logging
import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('local_todo_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 設定
TOKEN = '***REMOVED***'
TODO_FILE = 'local_todos.json'

class LocalTodoManager:
    """ローカルストレージベースのTODO管理クラス"""
    
    def __init__(self, todo_file=TODO_FILE):
        self.todo_file = todo_file
        self.todos = self._load_todos()
    
    def _load_todos(self):
        """TODOリストをファイルから読み込み"""
        try:
            if os.path.exists(self.todo_file):
                with open(self.todo_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"TODO読み込みエラー: {e}")
            return []
    
    def _save_todos(self):
        """TODOリストをファイルに保存"""
        try:
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"TODO保存エラー: {e}")
            return False
    
    def add_todo(self, text, user_id, username=None):
        """新しいTODOを追加"""
        try:
            todo = {
                "id": len(self.todos) + 1,
                "text": text,
                "created_at": datetime.now().isoformat(),
                "user_id": user_id,
                "username": username,
                "completed": False
            }
            self.todos.append(todo)
            if self._save_todos():
                logger.info(f"TODO追加成功: {text}")
                return True
            return False
        except Exception as e:
            logger.error(f"TODO追加エラー: {e}")
            return False
    
    def get_todos(self, user_id=None, limit=10):
        """TODOリストを取得"""
        todos = self.todos
        if user_id:
            todos = [t for t in todos if t['user_id'] == user_id]
        
        # 未完了のTODOのみ、新しい順に取得
        active_todos = [t for t in todos if not t.get('completed', False)]
        return sorted(active_todos, key=lambda x: x['created_at'], reverse=True)[:limit]
    
    def complete_todo(self, todo_id):
        """TODOを完了にする"""
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['completed'] = True
                todo['completed_at'] = datetime.now().isoformat()
                self._save_todos()
                return True
        return False

# グローバルインスタンス
todo_manager = LocalTodoManager()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """メッセージハンドラー"""
    try:
        user = update.effective_user
        message = update.message
        text = message.text.strip()
        
        # /startコマンドは無視
        if text.startswith('/start'):
            await message.reply_text(
                "👋 TODOボットへようこそ！\n"
                "メッセージを送信するとTODOとして登録されます。\n"
                "/list - TODOリストを表示"
            )
            return
        
        # TODOを追加
        if todo_manager.add_todo(text, user.id, user.username):
            await message.reply_text(f"✅ TODO追加しました: {text}")
            logger.info(f"TODO追加成功: {text} (ユーザー: {user.username})")
        else:
            await message.reply_text("❌ TODO追加に失敗しました")
            logger.error(f"TODO追加失敗: {text}")
            
    except Exception as e:
        logger.error(f"メッセージ処理エラー: {e}")
        await update.message.reply_text("❌ エラーが発生しました")

async def list_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """TODOリストを表示"""
    try:
        user = update.effective_user
        todos = todo_manager.get_todos(user.id)
        
        if not todos:
            await update.message.reply_text("📝 TODOリストは空です")
            return
        
        message = "📋 あなたのTODOリスト:\n\n"
        for i, todo in enumerate(todos, 1):
            created = datetime.fromisoformat(todo['created_at'])
            message += f"{i}. {todo['text']} ({created.strftime('%m/%d %H:%M')})\n"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"リスト表示エラー: {e}")
        await update.message.reply_text("❌ エラーが発生しました")

def main():
    """メイン関数"""
    try:
        # アプリケーション作成
        application = Application.builder().token(TOKEN).build()
        
        # ハンドラー登録
        application.add_handler(CommandHandler("start", handle_message))
        application.add_handler(CommandHandler("list", list_todos))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # 起動
        logger.info("ローカルTODOボット起動")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"起動エラー: {e}")

if __name__ == '__main__':
    main()
