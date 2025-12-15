#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Enhanced Local Storage Telegram TODO Bot - 一覧・削除機能付き

import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

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
            # 最大IDを取得
            max_id = max([t['id'] for t in self.todos], default=0)
            todo = {
                "id": max_id + 1,
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
    
    def get_todos(self, user_id=None, limit=10, include_completed=False):
        """TODOリストを取得"""
        todos = self.todos
        if user_id:
            todos = [t for t in todos if t['user_id'] == user_id]
        
        if not include_completed:
            todos = [t for t in todos if not t.get('completed', False)]
        
        return sorted(todos, key=lambda x: x['created_at'], reverse=True)[:limit]
    
    def delete_todo(self, todo_id, user_id):
        """TODOを削除"""
        try:
            for i, todo in enumerate(self.todos):
                if todo['id'] == todo_id and todo['user_id'] == user_id:
                    deleted = self.todos.pop(i)
                    if self._save_todos():
                        logger.info(f"TODO削除成功: {deleted['text']}")
                        return True, deleted['text']
            return False, None
        except Exception as e:
            logger.error(f"TODO削除エラー: {e}")
            return False, None
    
    def complete_todo(self, todo_id, user_id):
        """TODOを完了にする"""
        for todo in self.todos:
            if todo['id'] == todo_id and todo['user_id'] == user_id:
                todo['completed'] = True
                todo['completed_at'] = datetime.now().isoformat()
                if self._save_todos():
                    return True, todo['text']
        return False, None

# グローバルインスタンス
todo_manager = LocalTodoManager()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """スタートコマンド"""
    await update.message.reply_text(
        "👋 TODO BOTへようこそ！\n\n"
        "📝 **使い方**:\n"
        "• メッセージ送信 → TODO追加\n"
        "• /list → TODO一覧表示\n"
        "• /delete → TODO削除メニュー\n"
        "• /done → TODO完了メニュー\n"
        "• /all → 完了済み含む全TODO表示",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """メッセージハンドラー"""
    try:
        user = update.effective_user
        message = update.message
        text = message.text.strip()
        
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
        todos = todo_manager.get_todos(user.id, limit=20)
        
        if not todos:
            await update.message.reply_text("📝 TODOリストは空です")
            return
        
        message = "📋 **あなたのTODOリスト**:\n\n"
        for i, todo in enumerate(todos, 1):
            created = datetime.fromisoformat(todo['created_at'])
            message += f"{i}. {todo['text']}\n   📅 {created.strftime('%m/%d %H:%M')}\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"リスト表示エラー: {e}")
        await update.message.reply_text("❌ エラーが発生しました")

async def delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """削除メニューを表示"""
    try:
        user = update.effective_user
        todos = todo_manager.get_todos(user.id, limit=10)
        
        if not todos:
            await update.message.reply_text("📝 削除するTODOがありません")
            return
        
        keyboard = []
        for todo in todos:
            text = todo['text'][:30] + "..." if len(todo['text']) > 30 else todo['text']
            callback_data = f"delete_{todo['id']}"
            keyboard.append([InlineKeyboardButton(f"🗑 {text}", callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("❌ キャンセル", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🗑 **削除するTODOを選択してください**:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"削除メニューエラー: {e}")
        await update.message.reply_text("❌ エラーが発生しました")

async def done_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """完了メニューを表示"""
    try:
        user = update.effective_user
        todos = todo_manager.get_todos(user.id, limit=10)
        
        if not todos:
            await update.message.reply_text("📝 完了するTODOがありません")
            return
        
        keyboard = []
        for todo in todos:
            text = todo['text'][:30] + "..." if len(todo['text']) > 30 else todo['text']
            callback_data = f"done_{todo['id']}"
            keyboard.append([InlineKeyboardButton(f"✅ {text}", callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("❌ キャンセル", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ **完了するTODOを選択してください**:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"完了メニューエラー: {e}")
        await update.message.reply_text("❌ エラーが発生しました")

async def all_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """完了済み含む全TODO表示"""
    try:
        user = update.effective_user
        todos = todo_manager.get_todos(user.id, limit=30, include_completed=True)
        
        if not todos:
            await update.message.reply_text("📝 TODOリストは空です")
            return
        
        active = [t for t in todos if not t.get('completed', False)]
        completed = [t for t in todos if t.get('completed', False)]
        
        message = "📋 **全TODOリスト**:\n\n"
        
        if active:
            message += "**📌 未完了**:\n"
            for todo in active[:10]:
                created = datetime.fromisoformat(todo['created_at'])
                message += f"• {todo['text']}\n  {created.strftime('%m/%d %H:%M')}\n"
        
        if completed:
            message += "\n**✅ 完了済み**:\n"
            for todo in completed[:10]:
                completed_at = datetime.fromisoformat(todo['completed_at'])
                message += f"• <s>{todo['text']}</s>\n  {completed_at.strftime('%m/%d %H:%M')}完了\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"全TODO表示エラー: {e}")
        await update.message.reply_text("❌ エラーが発生しました")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ボタンコールバック処理"""
    query = update.callback_query
    await query.answer()
    
    try:
        user = query.from_user
        data = query.data
        
        if data == "cancel":
            await query.edit_message_text("❌ キャンセルしました")
            return
        
        if data.startswith("delete_"):
            todo_id = int(data.replace("delete_", ""))
            success, text = todo_manager.delete_todo(todo_id, user.id)
            if success:
                await query.edit_message_text(f"🗑 削除しました: {text}")
            else:
                await query.edit_message_text("❌ 削除に失敗しました")
        
        elif data.startswith("done_"):
            todo_id = int(data.replace("done_", ""))
            success, text = todo_manager.complete_todo(todo_id, user.id)
            if success:
                await query.edit_message_text(f"✅ 完了しました: {text}")
            else:
                await query.edit_message_text("❌ 完了処理に失敗しました")
                
    except Exception as e:
        logger.error(f"ボタン処理エラー: {e}")
        await query.edit_message_text("❌ エラーが発生しました")

def main():
    """メイン関数"""
    try:
        # アプリケーション作成
        application = Application.builder().token(TOKEN).build()
        
        # ハンドラー登録
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("list", list_todos))
        application.add_handler(CommandHandler("delete", delete_menu))
        application.add_handler(CommandHandler("done", done_menu))
        application.add_handler(CommandHandler("all", all_todos))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # 起動
        logger.info("Enhanced TODO BOT起動")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"起動エラー: {e}")

if __name__ == '__main__':
    main()
