#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Telegram Google TODO Manager Bot

import logging
import pickle
import os
import requests
import json
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from google.auth.transport.requests import Request

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_todo_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 設定
TOKEN = '***REMOVED***'
GOOGLE_TOKEN_FILE = '/home/fujinosuke/google_tasks_new.pickle'

class GoogleTodoManager:
    def __init__(self, token_file=GOOGLE_TOKEN_FILE):
        """Google Tasks API管理クラス"""
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
                logger.info("トークンをリフレッシュ中...")
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
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
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
    
    def get_tasks(self, tasklist_id=None):
        """タスク一覧を取得"""
        if not tasklist_id:
            task_lists = self.get_task_lists()
            if not task_lists:
                return []
            tasklist_id = task_lists[0]['id']
        
        url = f'https://www.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks'
        result = self._make_api_request(url)
        if result:
            return result.get('items', [])
        return []
    
    def add_task(self, title, notes='', tasklist_id=None):
        """新しいタスクを追加"""
        if not tasklist_id:
            task_lists = self.get_task_lists()
            if not task_lists:
                return None
            tasklist_id = task_lists[0]['id']
        
        task = {'title': title, 'notes': notes}
        url = f'https://www.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks'
        return self._make_api_request(url, method='POST', data=task)
    
    def complete_task(self, task_id, tasklist_id=None):
        """タスクを完了にする"""
        if not tasklist_id:
            task_lists = self.get_task_lists()
            if not task_lists:
                return False
            tasklist_id = task_lists[0]['id']
        
        task = {'id': task_id, 'status': 'completed'}
        url = f'https://www.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks/{task_id}'
        result = self._make_api_request(url, method='PUT', data=task)
        return result is not None
    
    def delete_task(self, task_id, tasklist_id=None):
        """タスクを削除"""
        if not tasklist_id:
            task_lists = self.get_task_lists()
            if not task_lists:
                return False
            tasklist_id = task_lists[0]['id']
        
        url = f'https://www.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks/{task_id}'
        result = self._make_api_request(url, method='DELETE')
        return result is not None

# Google TODO Managerインスタンス
todo_manager = GoogleTodoManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """開始コマンド"""
    welcome_text = (
        "🎯 **Google TODO Manager Bot**\n\n"
        "Google Tasksと連携したTODO管理BOTです！\n\n"
        "📋 **コマンド一覧:**\n"
        "/list - TODOリストを表示\n"
        "/add <タスク名> - 新しいタスクを追加\n"
        "/done - 完了済みタスクを表示\n"
        "/help - ヘルプを表示\n\n"
        "✨ **使い方:**\n"
        "• メッセージを送信するだけでタスクを追加できます\n"
        "• ボタンをタップしてタスクを完了・削除\n"
        "• Googleタスクとリアルタイム同期"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ヘルプコマンド"""
    help_text = (
        "🎯 **Google TODO Manager Bot ヘルプ**\n\n"
        "**基本コマンド:**\n"
        "• `/list` - 現在のTODOリストを表示\n"
        "• `/add タスク名` - 新しいタスクを追加\n"
        "• `/done` - 完了済みタスクを表示\n\n"
        "**簡単操作:**\n"
        "• テキストメッセージを送信 → 自動でタスク追加\n"
        "• リスト表示時のボタン → タスク完了・削除\n\n"
        "**特徴:**\n"
        "✅ Googleタスクとリアルタイム同期\n"
        "✅ 複数のタスクリスト対応\n"
        "✅ タスクの詳細メモ対応\n"
        "✅ 完了・削除・復元機能"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """TODOリストを表示"""
    try:
        tasks = todo_manager.get_tasks()
        
        if not tasks:
            await update.message.reply_text("📝 現在TODOリストは空です。\n\n新しいタスクを追加するには `/add タスク名` またはメッセージを送信してください。")
            return
        
        # 未完了タスクのみ表示
        pending_tasks = [task for task in tasks if task.get('status') != 'completed']
        
        if not pending_tasks:
            await update.message.reply_text("🎉 すべてのタスクが完了しています！\n\n完了済みタスクを確認するには `/done` を使用してください。")
            return
        
        text = f"📋 **TODOリスト** ({len(pending_tasks)}件)\n\n"
        keyboard = []
        
        for i, task in enumerate(pending_tasks[:10], 1):  # 最大10件表示
            title = task.get('title', '無題')
            task_id = task.get('id')
            
            # タスク情報表示
            text += f"{i}. ⏳ {title}\n"
            if task.get('notes'):
                text += f"   📝 {task['notes'][:50]}{'...' if len(task['notes']) > 50 else ''}\n"
            if task.get('due'):
                text += f"   📅 期限: {task['due'][:10]}\n"
            text += "\n"
            
            # インラインキーボード作成
            keyboard.append([
                InlineKeyboardButton(f"✅ 完了 ({i})", callback_data=f"complete_{task_id}"),
                InlineKeyboardButton(f"🗑 削除 ({i})", callback_data=f"delete_{task_id}")
            ])
        
        if len(pending_tasks) > 10:
            text += f"... 他 {len(pending_tasks) - 10} 件\n"
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"リスト表示エラー: {e}")
        await update.message.reply_text("❌ TODOリストの取得に失敗しました。しばらく後でお試しください。")

async def add_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """タスク追加コマンド"""
    if not context.args:
        await update.message.reply_text("使用方法: `/add タスク名`\n\n例: `/add 食料品を買う`")
        return
    
    title = ' '.join(context.args)
    await add_task_helper(update, title)

async def add_task_helper(update: Update, title: str):
    """タスク追加ヘルパー"""
    try:
        # タスクを追加
        result = todo_manager.add_task(title)
        
        if result:
            await update.message.reply_text(f"✅ タスクを追加しました！\n\n📝 **{title}**\n\n現在のリストを確認するには `/list` を使用してください。")
            logger.info(f"タスク追加成功: {title}")
        else:
            await update.message.reply_text("❌ タスクの追加に失敗しました。しばらく後でお試しください。")
            logger.error(f"タスク追加失敗: {title}")
            
    except Exception as e:
        logger.error(f"タスク追加エラー: {e}")
        await update.message.reply_text("❌ タスクの追加中にエラーが発生しました。")

async def done_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """完了済みタスクを表示"""
    try:
        tasks = todo_manager.get_tasks()
        completed_tasks = [task for task in tasks if task.get('status') == 'completed']
        
        if not completed_tasks:
            await update.message.reply_text("📝 完了済みタスクはありません。")
            return
        
        text = f"✅ **完了済みタスク** ({len(completed_tasks)}件)\n\n"
        
        for i, task in enumerate(completed_tasks[:10], 1):
            title = task.get('title', '無題')
            completed_date = task.get('completed', '')[:10] if task.get('completed') else '不明'
            text += f"{i}. ✅ {title}\n"
            text += f"   🗓 完了日: {completed_date}\n\n"
        
        if len(completed_tasks) > 10:
            text += f"... 他 {len(completed_tasks) - 10} 件\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"完了タスク表示エラー: {e}")
        await update.message.reply_text("❌ 完了済みタスクの取得に失敗しました。")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """通常メッセージの処理（自動タスク追加）"""
    text = update.message.text.strip()
    
    # コマンドでない場合はタスクとして追加
    if not text.startswith('/'):
        await add_task_helper(update, text)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ボタンコールバック処理"""
    query = update.callback_query
    await query.answer()
    
    try:
        action, task_id = query.data.split('_', 1)
        
        if action == 'complete':
            # タスク完了
            success = todo_manager.complete_task(task_id)
            if success:
                await query.edit_message_text("✅ タスクを完了しました！")
                logger.info(f"タスク完了: {task_id}")
            else:
                await query.edit_message_text("❌ タスクの完了に失敗しました。")
                logger.error(f"タスク完了失敗: {task_id}")
        
        elif action == 'delete':
            # タスク削除
            success = todo_manager.delete_task(task_id)
            if success:
                await query.edit_message_text("🗑 タスクを削除しました。")
                logger.info(f"タスク削除: {task_id}")
            else:
                await query.edit_message_text("❌ タスクの削除に失敗しました。")
                logger.error(f"タスク削除失敗: {task_id}")
        
    except Exception as e:
        logger.error(f"ボタンコールバックエラー: {e}")
        await query.edit_message_text("❌ 操作中にエラーが発生しました。")

def main():
    """BOT起動"""
    # Google認証確認
    if not todo_manager.creds:
        logger.error("Google認証に失敗しました。終了します。")
        return
    
    logger.info("Google Tasks API認証成功")
    
    # Telegram Bot初期化
    application = Application.builder().token(TOKEN).build()
    
    # ハンドラー登録
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("add", add_task_command))
    application.add_handler(CommandHandler("done", done_tasks))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Telegram Google TODO Manager Bot を起動します...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()