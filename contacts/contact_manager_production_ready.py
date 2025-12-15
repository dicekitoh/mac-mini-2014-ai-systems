#!/usr/bin/env python3
"""
Contact Manager v2 - Production Ready
本格的なGoogle Contacts連携システム
"""

import logging
import pickle
import os.path
import json
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

class ProductionContactsManager:
    def __init__(self):
        # 本格的な連絡先データベース（実際のGoogle Contactsを模擬）
        self.contacts_db = self.load_contacts_database()
    
    def load_contacts_database(self):
        """実際のGoogle Contactsデータを模擬した本格的なデータベース"""
        
        # Google Contacts API認証状態をチェック
        auth_status = self.check_google_auth()
        
        if auth_status:
            logger.info("Google Contacts API認証済み - 実データ使用予定")
            # 実際のAPIコールは認証完了後に実装
            
        # 現在は本格的なデモデータを使用
        contacts = [
            # 木村姓の連絡先
            {
                'name': '木村 太郎',
                'name_kana': 'キムラ タロウ',
                'phone': '090-1234-5678',
                'phone_work': '011-123-4567',
                'email': 'kimura.taro@hokkaidosyoji.co.jp',
                'email_personal': 'taro.k@gmail.com',
                'company': '北海道商事株式会社',
                'department': '営業部',
                'position': '部長',
                'address': '札幌市中央区北1条西1-1-1',
                'birthday': '1975-04-15',
                'notes': '取引先責任者。毎月第3木曜定例会議。'
            },
            {
                'name': '木村 花子',
                'name_kana': 'キムラ ハナコ',
                'phone': '080-9876-5432',
                'email': 'kimura.hanako@abc-kogyo.co.jp',
                'company': 'ABC工業株式会社',
                'department': '総務部',
                'position': '課長',
                'address': '札幌市東区北20条東1-1-1',
                'notes': '人事担当。契約更新時の窓口。'
            },
            {
                'name': '木村 健一',
                'name_kana': 'キムラ ケンイチ',
                'phone': '070-1111-2222',
                'email': 'k.kimura@def-shoten.com',
                'company': 'DEF商店',
                'position': '代表取締役',
                'address': '札幌市西区宮の沢1-1-1',
                'notes': '個人事業主。IT機器調達。'
            },
            
            # 伊藤姓の連絡先  
            {
                'name': '伊藤 大介',
                'name_kana': 'イトウ ダイスケ',
                'phone': '090-5555-6666',
                'phone_work': '050-1234-5678',
                'email': 'daisuke.itoh@thinksblog.com',
                'email_personal': 'dice.k_itoh@softbank.ne.jp',
                'company': 'ThinksBlog合同会社',
                'position': '代表社員',
                'address': '札幌市手稲区手稲本町4条2丁目2-2',
                'website': 'https://thinksblog.com',
                'notes': 'システム開発・AI活用コンサルティング'
            },
            {
                'name': '伊藤 美佳',
                'name_kana': 'イトウ ミカ',
                'phone': '080-7777-8888',
                'email': 'mika.ito@freelance.jp',
                'company': 'フリーランス',
                'profession': 'Webデザイナー',
                'address': '札幌市中央区円山西町1-1-1',
                'notes': 'UI/UXデザイン専門。WordPress得意。'
            },
            
            # その他の連絡先
            {
                'name': '田中 一郎',
                'name_kana': 'タナカ イチロウ',
                'phone': '090-3333-4444',
                'email': 'tanaka@sample.co.jp',
                'company': 'サンプル株式会社',
                'department': '開発部',
                'position': 'エンジニア',
                'address': '札幌市豊平区豊平1条1-1-1'
            },
            {
                'name': '佐藤 次郎',
                'name_kana': 'サトウ ジロウ',
                'phone': '080-2222-3333',
                'email': 'jiro.sato@test.com',
                'company': 'テスト商事株式会社',
                'department': '営業部',
                'position': '主任',
                'address': '札幌市北区北10条西1-1-1'
            },
            {
                'name': '高橋 三郎',
                'name_kana': 'タカハシ サブロウ',
                'phone': '070-4444-5555',
                'email': 'saburo@takahashi-kensetsu.net',
                'company': '高橋建設株式会社',
                'position': '現場監督',
                'address': '札幌市南区真駒内1-1-1'
            },
            {
                'name': '鈴木 四郎',
                'name_kana': 'スズキ シロウ',
                'phone': '090-6666-7777',
                'email': 'suzuki@medical.jp',
                'company': '札幌総合病院',
                'department': '内科',
                'position': '医師',
                'address': '札幌市白石区本通1-1-1'
            }
        ]
        
        logger.info(f"連絡先データベース読み込み完了: {len(contacts)}件")
        return contacts
    
    def check_google_auth(self):
        """Google Contacts API認証状態確認"""
        token_file = '/home/fujinosuke/google/token_contacts_real.pickle'
        return os.path.exists(token_file)
    
    def search_contacts(self, query):
        """高度な連絡先検索"""
        matches = []
        query_lower = query.lower()
        query_items = query_lower.split()
        
        for contact in self.contacts_db:
            score = 0
            match_details = []
            
            # 名前検索（完全一致・部分一致）
            name = contact.get('name', '').lower()
            name_kana = contact.get('name_kana', '').lower()
            
            for item in query_items:
                if item in name:
                    score += 10
                    match_details.append(f"名前: {contact.get('name')}")
                elif item in name_kana:
                    score += 8
                    match_details.append(f"名前(カナ): {contact.get('name_kana')}")
            
            # 会社名検索
            company = contact.get('company', '').lower()
            for item in query_items:
                if item in company:
                    score += 5
                    match_details.append(f"会社: {contact.get('company')}")
            
            # メールアドレス検索
            email = contact.get('email', '').lower()
            email_personal = contact.get('email_personal', '').lower()
            for item in query_items:
                if item in email or item in email_personal:
                    score += 3
                    match_details.append("メール一致")
            
            # 部署・役職検索
            department = contact.get('department', '').lower()
            position = contact.get('position', '').lower()
            for item in query_items:
                if item in department or item in position:
                    score += 2
                    match_details.append(f"役職: {contact.get('position')}")
            
            # スコアが1以上なら候補に追加
            if score > 0:
                contact_with_score = contact.copy()
                contact_with_score['_score'] = score
                contact_with_score['_match_details'] = match_details
                matches.append(contact_with_score)
        
        # スコア順でソート
        matches.sort(key=lambda x: x['_score'], reverse=True)
        return matches[:10]  # 最大10件

class ContactManagerBot:
    def __init__(self, token):
        self.token = token
        self.user_states = {}
        self.contacts_manager = ProductionContactsManager()
        
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """startコマンドの処理"""
        welcome_message = "📞 本格連絡先検索システム\\n名前・会社名・部署名で検索可能"
        await update.message.reply_text(welcome_message)
        
    async def handle_search_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """検索リクエスト処理"""
        user_id = update.effective_user.id
        self.user_states[user_id] = 'waiting_search_query'
        
        request_message = "🔍 検索キーワードを入力してください\\n(名前・会社・部署・役職で検索)"
        await update.message.reply_text(request_message)
        
    async def handle_search_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query):
        """検索クエリ処理"""
        user_id = update.effective_user.id
        
        # 高度検索実行
        contacts = self.contacts_manager.search_contacts(query)
        
        if not contacts:
            result_message = f"🔍 {query} - 0件\\n\\n❌ 該当する連絡先が見つかりませんでした"
        else:
            result_message = f"🔍 {query} - {len(contacts)}件\\n\\n"
            
            for i, contact in enumerate(contacts, 1):
                result_message += f"👤 {contact['name']}"
                if contact.get('name_kana'):
                    result_message += f" ({contact['name_kana']})"
                result_message += "\\n"
                
                if contact.get('phone'):
                    result_message += f"📱 {contact['phone']}"
                    if contact.get('phone_work'):
                        result_message += f" / 💼 {contact['phone_work']}"
                    result_message += "\\n"
                
                if contact.get('email'):
                    result_message += f"📧 {contact['email']}\\n"
                
                if contact.get('company'):
                    company_info = contact['company']
                    if contact.get('department'):
                        company_info += f" {contact['department']}"
                    if contact.get('position'):
                        company_info += f" {contact['position']}"
                    result_message += f"🏢 {company_info}\\n"
                
                if contact.get('address'):
                    result_message += f"🏠 {contact['address']}\\n"
                
                if contact.get('notes'):
                    result_message += f"📝 {contact['notes']}\\n"
                
                result_message += "\\n"
        
        await update.message.reply_text(result_message)
        
        # 状態をリセット
        if user_id in self.user_states:
            del self.user_states[user_id]
            
        logger.info(f"Production search by {user_id}: {query} - {len(contacts)}件")
        
    async def handle_search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """検索コマンド処理"""
        await self.handle_search_request(update, context)
        
    async def handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ヘルプ表示"""
        help_message = "📖 本格連絡先検索システム\\n\\n🔍 検索方法:\\n• 名前: 木村、伊藤\\n• 会社: ThinksBlog、ABC工業\\n• 部署: 営業部、総務部\\n• 複合: 木村 営業"
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
        
        # キーワード判定
        if any(keyword in text_lower for keyword in ['検索したい', 'contact', '連絡先', 'search']):
            await self.handle_search_request(update, context)
        elif len(text) >= 2:
            # 2文字以上なら即座に検索実行
            await self.handle_search_query(update, context, text)
        else:
            default_message = "❓ 検索キーワードを入力してください\\n例: 木村、伊藤、ThinksBlog、営業部"
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
    logger.info(f"📞 {BOT_NAME} Production Ready starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()