#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Contact Manager v2 Bot with Auto-Recovery
認証エラーの自動復旧機能を備えた改良版
"""

import logging
import pickle
import os
import subprocess
import time
from datetime import datetime
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('improved_contact_manager_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 設定
TOKEN = '7900018084:AAF0UvIwnRlBLEx_R9NX7Sld6msbInXoKZE'
TOKEN_FILE = 'token.pickle'
BACKUP_TOKEN_FILE = 'token.pickle.backup'
SCOPES = ['https://www.googleapis.com/auth/contacts']
MAX_RETRY_ATTEMPTS = 3

class ImprovedContactManager:
    def __init__(self):
        self.creds = None
        self.service = None
        self.last_refresh_time = datetime.now()
        self.authenticate()
    
    def authenticate(self):
        """Google認証（改良版：バックアップ対応）"""
        try:
            # メインのトークンファイルをチェック
            if not os.path.exists(TOKEN_FILE):
                logger.warning(f"Token file {TOKEN_FILE} not found")
                # バックアップから復元を試みる
                if os.path.exists(BACKUP_TOKEN_FILE):
                    logger.info("Restoring from backup token")
                    subprocess.run(['cp', BACKUP_TOKEN_FILE, TOKEN_FILE])
                else:
                    logger.error("No backup token available")
                    return False
            
            # バックアップ作成（存在する場合）
            if os.path.exists(TOKEN_FILE) and not os.path.exists(BACKUP_TOKEN_FILE):
                subprocess.run(['cp', TOKEN_FILE, BACKUP_TOKEN_FILE])
                logger.info("Created token backup")
            
            with open(TOKEN_FILE, 'rb') as token:
                self.creds = pickle.load(token)
            
            # 有効期限チェックと自動リフレッシュ
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("Token expired, refreshing...")
                self.creds.refresh(Request())
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.creds, token)
                logger.info("Token refreshed successfully")
                self.last_refresh_time = datetime.now()
            
            self.service = build('people', 'v1', credentials=self.creds)
            return True
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def execute_with_retry(self, func, *args, **kwargs):
        """API呼び出しをリトライ機能付きで実行"""
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e)
                if '401' in error_str or 'unauthorized' in error_str.lower():
                    logger.warning(f"Authentication error on attempt {attempt + 1}, refreshing token...")
                    # トークンを強制リフレッシュ
                    try:
                        self.creds.refresh(Request())
                        with open(TOKEN_FILE, 'wb') as token:
                            pickle.dump(self.creds, token)
                        self.service = build('people', 'v1', credentials=self.creds)
                        logger.info("Token refreshed, retrying...")
                        continue
                    except Exception as refresh_error:
                        logger.error(f"Token refresh failed: {refresh_error}")
                        if attempt == MAX_RETRY_ATTEMPTS - 1:
                            raise
                else:
                    logger.error(f"API error on attempt {attempt + 1}: {e}")
                    if attempt == MAX_RETRY_ATTEMPTS - 1:
                        raise
                time.sleep(1)  # 次の試行前に少し待機
        
        raise Exception("Max retry attempts reached")
    
    def search_contacts(self, query, max_results=10):
        """連絡先を検索（リトライ機能付き）"""
        def _search():
            results = self.service.people().searchContacts(
                query=query,
                readMask='names,phoneNumbers,emailAddresses,organizations',
                pageSize=max_results
            ).execute()
            return results.get('results', [])
        
        return self.execute_with_retry(_search)
    
    def create_contact(self, contact_data):
        """連絡先を作成（リトライ機能付き）"""
        def _create():
            result = self.service.people().createContact(body=contact_data).execute()
            return result
        
        return self.execute_with_retry(_create)
    
    def update_contact(self, resource_name, contact_data, update_fields):
        """連絡先を更新（リトライ機能付き）"""
        def _update():
            result = self.service.people().updateContact(
                resourceName=resource_name,
                body=contact_data,
                updatePersonFields=update_fields
            ).execute()
            return result
        
        return self.execute_with_retry(_update)
    
    def delete_contact(self, resource_name):
        """連絡先を削除（リトライ機能付き）"""
        def _delete():
            self.service.people().deleteContact(resourceName=resource_name).execute()
            return True
        
        return self.execute_with_retry(_delete)

# グローバルインスタンス
contact_manager = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """スタートコマンド"""
    await update.message.reply_text(
        "📱 Contact Manager v2 Bot (改良版) へようこそ！\n\n"
        "コマンド一覧:\n"
        "/search <名前> - 連絡先を検索\n"
        "/add - 新しい連絡先を追加\n"
        "/help - ヘルプを表示\n\n"
        "検索したい名前を直接送信することもできます。"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """テキストメッセージを処理"""
    global contact_manager
    
    if not contact_manager:
        contact_manager = ImprovedContactManager()
        if not contact_manager.creds:
            await update.message.reply_text("❌ 認証エラーが発生しました。管理者に連絡してください。")
            return
    
    query = update.message.text.strip()
    if not query:
        return
    
    await update.message.reply_text(f"🔍 「{query}」を検索中...")
    
    try:
        # 連絡先を検索
        results = contact_manager.search_contacts(query)
        
        if not results:
            await update.message.reply_text(f"❌ 「{query}」に一致する連絡先が見つかりませんでした。")
            return
        
        # 結果を表示
        for i, result in enumerate(results[:5]):  # 最大5件まで表示
            person = result.get('person', {})
            names = person.get('names', [])
            phones = person.get('phoneNumbers', [])
            emails = person.get('emailAddresses', [])
            orgs = person.get('organizations', [])
            
            name = names[0].get('displayName', '名前なし') if names else '名前なし'
            
            message = f"👤 **{name}**\n"
            
            if phones:
                message += "📞 電話番号:\n"
                for phone in phones:
                    message += f"  • {phone.get('value', 'N/A')}\n"
            
            if emails:
                message += "📧 メール:\n"
                for email in emails:
                    message += f"  • {email.get('value', 'N/A')}\n"
            
            if orgs:
                message += "🏢 組織:\n"
                for org in orgs:
                    message += f"  • {org.get('name', 'N/A')}\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text(
            f"❌ 検索中にエラーが発生しました。\n"
            f"エラー: {str(e)}\n\n"
            f"自動復旧を試みています..."
        )
        # 再認証を試みる
        contact_manager.authenticate()

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """エラーハンドリング"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """メイン実行関数"""
    global contact_manager
    
    logger.info("Starting Improved Contact Manager v2 Bot...")
    
    # Contact Managerの初期化
    contact_manager = ImprovedContactManager()
    if not contact_manager.creds:
        logger.error("Failed to initialize Contact Manager")
        return
    
    # アプリケーション作成
    application = Application.builder().token(TOKEN).build()
    
    # ハンドラー追加
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Bot開始
    logger.info("Bot is ready to receive messages")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()