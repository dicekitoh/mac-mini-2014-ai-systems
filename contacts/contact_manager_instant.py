#!/usr/bin/env python3
"""
Contact Manager v2 - Instant Search Version
Google Contacts連携検索BOT - 即座検索対応
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# BOT設定
BOT_TOKEN = "7900018084:AAF0UvIwnRlBLEx_R9NX7Sld6msbInXoKZE"
BOT_NAME = "Contact Manager v2"

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContactManagerBot:
    def __init__(self, token):
        self.token = token
        self.user_states = {}
        
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """startコマンドの処理"""
        welcome_message = "📞 連絡先検索BOT\n「検索したい」で連絡先検索"
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
        user_name = update.effective_user.first_name or "ユーザー"
        
        # Google Contacts連携は今後実装
        # 現在はデモデータとして動作
        
        # デモ検索結果
        demo_results = [
            {
                'name': f'{query}太郎',
                'phone': '090-1234-5678',
                'email': f'{query.lower()}@example.com',
                'company': 'サンプル株式会社'
            },
            {
                'name': f'{query}花子',
                'phone': '080-9876-5432', 
                'email': f'{query.lower()}.hanako@company.co.jp',
                'company': 'テスト商事'
            }
        ]
        
        if len(query) < 1:
            error_message = "❌ 検索キーワードが短すぎます。もう一度入力してください。"
            await update.message.reply_text(error_message)
            return
            
        result_message = f"🔍 {query} - {len(demo_results)}件\n\n"
        
        for i, contact in enumerate(demo_results, 1):
            result_message += f"👤 {contact['name']}\n📱 {contact['phone']}\n\n"
        
        await update.message.reply_text(result_message)
        
        # 状態をリセット
        if user_id in self.user_states:
            del self.user_states[user_id]
            
        logger.info(f"Contact search by {user_id}: {query}")
        
    async def handle_search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """検索コマンド処理"""
        await self.handle_search_request(update, context)
        
    async def handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ヘルプ表示"""
        help_message = "📖 「検索したい」で連絡先検索"
        
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
        elif any(keyword in text_lower for keyword in instant_keywords):
            # 即座に検索実行
            await self.handle_search_query(update, context, text)
        else:
            default_message = "❓ 「検索したい」と送信してください"
            
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
    logger.info(f"📞 {BOT_NAME} starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()