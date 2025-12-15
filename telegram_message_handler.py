#!/usr/bin/env python3
"""
Telegram BOTメッセージハンドラー
受信したメッセージを指定フォルダに保存
"""

import os
import sys
import json
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio
import logging

# ロギング設定
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# BOT設定
BOT_TOKEN = "7900018084:AAF0UvIwnRlBLEx_R9NX7Sld6msbInXoKZE"  # Contact Manager BOTトークン
RECEIVED_MESSAGES_DIR = "/tmp/received_messages"
RECEIVED_IMAGES_DIR = "/tmp/received_images"

# ディレクトリ作成
os.makedirs(RECEIVED_MESSAGES_DIR, exist_ok=True)
os.makedirs(RECEIVED_IMAGES_DIR, exist_ok=True)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """テキストメッセージを処理"""
    try:
        message = update.message
        text = message.text
        user = message.from_user
        
        # メッセージ情報を記録
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"telegram_msg_{user.id}_{timestamp}.txt"
        filepath = os.path.join(RECEIVED_MESSAGES_DIR, filename)
        
        # メッセージ内容を保存
        message_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user.id,
            "username": user.username or user.first_name,
            "text": text,
            "chat_id": message.chat_id,
            "message_id": message.message_id
        }
        
        # テキストファイルとして保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # メタデータも保存
        metadata_file = filepath.replace('.txt', '_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(message_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📥 テキストメッセージ受信: {filename}")
        
        # ユーザーに確認メッセージを送信
        await message.reply_text(
            f"✅ メッセージを受信しました\n"
            f"📝 文字数: {len(text)}\n"
            f"📁 保存先: {filename}\n"
            f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # 日本語文字の検出
        japanese_chars = sum(1 for char in text if 
                           '\u3040' <= char <= '\u309F' or  # ひらがな
                           '\u30A0' <= char <= '\u30FF' or  # カタカナ
                           '\u4E00' <= char <= '\u9FAF')    # 漢字
        
        if japanese_chars > 0:
            await message.reply_text(
                f"📊 日本語文字数: {japanese_chars}\n"
                f"📊 日本語率: {japanese_chars/len(text)*100:.1f}%"
            )
        
    except Exception as e:
        logger.error(f"エラー: {e}")
        await message.reply_text(f"❌ エラーが発生しました: {str(e)}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """画像を処理"""
    try:
        message = update.message
        user = message.from_user
        
        # 最大サイズの写真を取得
        photo = message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        # ファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"telegram_img_{user.id}_{timestamp}.jpg"
        filepath = os.path.join(RECEIVED_IMAGES_DIR, filename)
        
        # 画像をダウンロード
        await file.download_to_drive(filepath)
        
        logger.info(f"📷 画像受信: {filename}")
        
        # ユーザーに確認メッセージを送信
        await message.reply_text(
            f"✅ 画像を受信しました\n"
            f"📷 ファイル: {filename}\n"
            f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🔍 OCR処理が自動的に開始されます..."
        )
        
    except Exception as e:
        logger.error(f"画像処理エラー: {e}")
        await message.reply_text(f"❌ 画像処理エラー: {str(e)}")

async def main() -> None:
    """メイン処理"""
    # アプリケーションを作成
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ハンドラーを追加
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    logger.info("🤖 Telegram メッセージハンドラー起動")
    logger.info(f"📁 テキスト保存先: {RECEIVED_MESSAGES_DIR}")
    logger.info(f"📁 画像保存先: {RECEIVED_IMAGES_DIR}")
    
    # BOT開始
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())