#!/usr/bin/env python3
"""
Contact Manager v2 - Google Contacts Real Data Version
Google Contacts連携検索BOT - 実データ対応
"""

import logging
import pickle
import os.path
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# BOT設定
BOT_TOKEN = "7900018084:AAF0UvIwnRlBLEx_R9NX7Sld6msbInXoKZE"
BOT_NAME = "Contact Manager v2"

# Google Contacts API設定
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts.pickle'

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleContactsManager:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Google Contacts API認証"""
        creds = None
        
        # トークンファイルが存在する場合はロード
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # 認証が無効または存在しない場合は再認証
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # トークンを保存
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('people', 'v1', credentials=creds)
        logger.info("Google Contacts API認証成功")
    
    def search_contacts(self, query):
        """連絡先検索"""
        try:
            # Google Contacts から連絡先を取得
            results = self.service.people().connections().list(
                resourceName='people/me',
                pageSize=1000,
                personFields='names,phoneNumbers,emailAddresses,organizations'
            ).execute()
            
            connections = results.get('connections', [])
            matches = []
            
            # クエリにマッチする連絡先を検索
            query_lower = query.lower()
            for person in connections:
                names = person.get('names', [])
                for name in names:
                    display_name = name.get('displayName', '')
                    if query_lower in display_name.lower():
                        # 連絡先情報を整理
                        contact_info = {
                            'name': display_name,
                            'phone': '',
                            'email': '',
                            'company': ''
                        }
                        
                        # 電話番号取得
                        phones = person.get('phoneNumbers', [])
                        if phones:
                            contact_info['phone'] = phones[0].get('value', '')
                        
                        # メールアドレス取得
                        emails = person.get('emailAddresses', [])
                        if emails:
                            contact_info['email'] = emails[0].get('value', '')
                        
                        # 会社情報取得
                        orgs = person.get('organizations', [])
                        if orgs:
                            contact_info['company'] = orgs[0].get('name', '')
                        
                        matches.append(contact_info)
                        break
            
            return matches[:10]  # 最大10件まで
            
        except Exception as e:
            logger.error(f"Google Contacts検索エラー: {e}")
            return []

class ContactManagerBot:
    def __init__(self, token):
        self.token = token
        self.user_states = {}
        self.google_contacts = GoogleContactsManager()
        
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """startコマンドの処理"""
        welcome_message = "📞 Google Contacts検索BOT\n「検索したい」で連絡先検索"
        await update.message.reply_text(welcome_message)
        
    async def handle_search_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """検索リクエスト処理"""
        user_id = update.effective_user.id
        self.user_states[user_id] = 'waiting_search_query'
        
        request_message = "🔍 検索したい名前を入力してください"
        await update.message.reply_text(request_message)
        
    async def handle_search_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query):
        """検索クエリ処理"""
        user_id = update.effective_user.id
        
        # Google Contactsから検索
        contacts = self.google_contacts.search_contacts(query)
        
        if not contacts:
            result_message = f"🔍 {query} - 0件\n\n❌ 該当する連絡先が見つかりませんでした"
        else:
            result_message = f"🔍 {query} - {len(contacts)}件\n\n"
            
            for i, contact in enumerate(contacts, 1):
                result_message += f"👤 {contact['name']}\n"
                if contact['phone']:
                    result_message += f"📱 {contact['phone']}\n"
                if contact['email']:
                    result_message += f"📧 {contact['email']}\n"
                if contact['company']:
                    result_message += f"🏢 {contact['company']}\n"
                result_message += "\n"
        
        await update.message.reply_text(result_message)
        
        # 状態をリセット
        if user_id in self.user_states:
            del self.user_states[user_id]
            
        logger.info(f"Google Contacts search by {user_id}: {query} - {len(contacts)}件")
        
    async def handle_search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """検索コマンド処理"""
        await self.handle_search_request(update, context)
        
    async def handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ヘルプ表示"""
        help_message = "📖 Google Contactsから連絡先検索\n「検索したい」で開始"
        await update.message.reply_text(help_message)
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """メッセージ処理"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        text_lower = text.lower()
        
        # 状態確認
        if user_id in self.user_states and self.user_states[user_id] == 'waiting_search_query':
            await self.handle_search_query(update, context, text)
            return
        
        # 即座検索キーワード
        instant_keywords = ['木村', 'きむら', 'kimura', '田中', 'たなか', 'tanaka', '佐藤', 'さとう', 'sato']
        
        # キーワード判定
        if any(keyword in text_lower for keyword in ['検索したい', 'contact', '連絡先']):
            await self.handle_search_request(update, context)
        elif any(keyword in text_lower for keyword in instant_keywords) or len(text) >= 2:
            # 即座に検索実行（2文字以上なら検索）
            await self.handle_search_query(update, context, text)
        else:
            default_message = "❓ 名前を入力してください"
            await update.message.reply_text(default_message)

def main():
    """メイン関数"""
    bot = ContactManagerBot(BOT_TOKEN)
    
    # アプリケーション作成
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ハンドラー追加
    application.add_handler(CommandHandler("start", bot.handle_start))
    application.add_handler(CommandHandler("search", bot.handle_search_command))
    application.add_handler(CommandHandler("help", bot.handle_help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # BOT開始
    logger.info(f"📞 {BOT_NAME} starting with Google Contacts integration...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()