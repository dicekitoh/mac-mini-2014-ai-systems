#!/usr/bin/env python3
"""
MacMini2014 OCR Bot - 画像OCR機能付きTelegramボット
@macmini2014_bot で受信した画像をGoogle Vision APIでOCR処理
"""

import requests
import json
import time
import logging
import os
import base64
from datetime import datetime
from pathlib import Path
import pickle
from typing import Dict, Any, Optional

# Google API関連
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# ログ設定
LOG_FILE = '/home/fujinosuke/macmini2014_ocr_bot.log'
IMAGES_DIR = '/home/fujinosuke/telegram_images'
OCR_RESULTS_DIR = '/home/fujinosuke/ocr_results'

# ディレクトリ作成
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(OCR_RESULTS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MacMini2014OCRBot:
    def __init__(self):
        self.bot_name = "MacMini2014 OCR Bot"
        self.bot_username = "@macmini2014_bot"
        self.token = "***REMOVED***"
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        
        # Google Vision API設定
        self.credentials_file = '/home/fujinosuke/google_contacts/credentials.json'
        self.token_file = '/home/fujinosuke/google_contacts/token.pickle'
        self.scopes = [
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/cloud-vision'
        ]
        
        # 設定ファイル
        self.offset_file = "/home/fujinosuke/telegram_ocr_bot_offset.txt"
        self.last_update_id = self.load_offset()
        
        # 統計
        self.stats = {
            'start_time': datetime.now(),
            'messages_processed': 0,
            'images_processed': 0,
            'ocr_success': 0,
            'ocr_failed': 0
        }
        
        logger.info(f"=== {self.bot_name} 初期化完了 ===")
        logger.info(f"Bot: {self.bot_username}")
        logger.info(f"画像保存: {IMAGES_DIR}")
        logger.info(f"OCR結果: {OCR_RESULTS_DIR}")
    
    def load_offset(self):
        """最後に処理したアップデートIDを読み込み"""
        try:
            if os.path.exists(self.offset_file):
                with open(self.offset_file, 'r') as f:
                    return int(f.read().strip())
        except:
            pass
        return 0
    
    def save_offset(self, offset):
        """処理済みアップデートIDを保存"""
        try:
            with open(self.offset_file, 'w') as f:
                f.write(str(offset))
        except Exception as e:
            logger.error(f"オフセット保存エラー: {e}")
    
    def authenticate_google(self):
        """Google API認証"""
        creds = None
        
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Google認証トークン更新中...")
                creds.refresh(Request())
            else:
                logger.info("🔑 Google認証が必要です")
                return None
            
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        logger.info("✅ Google API認証成功")
        return creds
    
    def get_updates(self):
        """新しいメッセージを取得"""
        try:
            url = f"{self.api_url}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 10,
                'limit': 100
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data.get('ok'):
                return data.get('result', [])
            else:
                logger.error(f"API エラー: {data}")
                return []
                
        except Exception as e:
            logger.error(f"メッセージ取得エラー: {e}")
            return []
    
    def download_image(self, file_id: str, chat_id: int) -> Optional[str]:
        """Telegram画像をダウンロード"""
        try:
            # ファイル情報取得
            url = f"{self.api_url}/getFile"
            params = {'file_id': file_id}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            file_info = response.json()
            if not file_info.get('ok'):
                logger.error(f"ファイル情報取得失敗: {file_info}")
                return None
            
            file_path = file_info['result']['file_path']
            file_size = file_info['result'].get('file_size', 0)
            
            # ファイルダウンロード
            download_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
            
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            # ローカルファイル保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_extension = Path(file_path).suffix or '.jpg'
            local_filename = f"telegram_image_{chat_id}_{timestamp}{file_extension}"
            local_path = os.path.join(IMAGES_DIR, local_filename)
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"📥 画像ダウンロード完了: {local_filename} ({file_size} bytes)")
            return local_path
            
        except Exception as e:
            logger.error(f"画像ダウンロードエラー: {e}")
            return None
    
    def ocr_image(self, image_path: str) -> Dict[str, Any]:
        """Google Vision APIでOCR処理"""
        try:
            start_time = datetime.now()
            
            # 画像読み込み
            with open(image_path, 'rb') as image_file:
                image_content = image_file.read()
            
            # Base64エンコード
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            # Vision API直接呼び出し（認証問題回避）
            url = "https://vision.googleapis.com/v1/images:annotate"
            headers = {'Content-Type': 'application/json'}
            
            request_body = {
                'requests': [{
                    'image': {'content': image_base64},
                    'features': [
                        {'type': 'TEXT_DETECTION', 'maxResults': 50},
                        {'type': 'DOCUMENT_TEXT_DETECTION', 'maxResults': 50}
                    ]
                }]
            }
            
            # 認証取得
            creds = self.authenticate_google()
            if not creds:
                return {
                    'success': False,
                    'error': 'Google認証が必要です',
                    'processing_time': 0
                }
            
            # 認証ヘッダー追加
            headers['Authorization'] = f'Bearer {creds.token}'
            
            # API実行
            response = requests.post(url, headers=headers, json=request_body, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 結果解析
            ocr_result = self.parse_ocr_response(result, image_path, processing_time)
            
            logger.info(f"✅ OCR処理完了: {Path(image_path).name}")
            logger.info(f"⏱️ 処理時間: {processing_time:.2f}秒")
            
            if ocr_result['success']:
                self.stats['ocr_success'] += 1
                logger.info(f"📝 認識テキスト長: {len(ocr_result.get('full_text', ''))}文字")
            else:
                self.stats['ocr_failed'] += 1
            
            return ocr_result
            
        except Exception as e:
            logger.error(f"OCR処理エラー: {e}")
            self.stats['ocr_failed'] += 1
            return {
                'success': False,
                'error': str(e),
                'processing_time': 0
            }
    
    def parse_ocr_response(self, response: Dict, image_path: str, processing_time: float) -> Dict[str, Any]:
        """OCRレスポンス解析"""
        try:
            if 'responses' not in response or not response['responses']:
                return {
                    'success': False,
                    'error': 'Empty response',
                    'processing_time': processing_time
                }
            
            response_data = response['responses'][0]
            
            if 'error' in response_data:
                return {
                    'success': False,
                    'error': response_data['error'],
                    'processing_time': processing_time
                }
            
            # テキスト抽出
            full_text = ""
            text_annotations = response_data.get('textAnnotations', [])
            
            if text_annotations:
                full_text = text_annotations[0].get('description', '')
            
            # 詳細情報抽出
            word_count = len(full_text.split()) if full_text else 0
            line_count = len(full_text.splitlines()) if full_text else 0
            
            result = {
                'success': True,
                'image_path': image_path,
                'processing_time': processing_time,
                'full_text': full_text,
                'text_length': len(full_text),
                'word_count': word_count,
                'line_count': line_count,
                'total_annotations': len(text_annotations),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"OCRレスポンス解析エラー: {e}")
            return {
                'success': False,
                'error': f'Response parsing error: {e}',
                'processing_time': processing_time
            }
    
    def save_ocr_result(self, result: Dict[str, Any], chat_id: int):
        """OCR結果をファイルに保存"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = os.path.join(OCR_RESULTS_DIR, f"ocr_result_{chat_id}_{timestamp}.json")
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📁 OCR結果保存: {os.path.basename(result_file)}")
            
        except Exception as e:
            logger.error(f"OCR結果保存エラー: {e}")
    
    def send_reply(self, chat_id: int, text: str):
        """返信メッセージ送信"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"✅ 返信送信成功")
            else:
                logger.error(f"❌ 返信送信失敗: {result}")
                
        except Exception as e:
            logger.error(f"返信送信エラー: {e}")
    
    def process_message(self, update):
        """メッセージ処理"""
        try:
            message = update.get('message')
            if not message:
                return
            
            chat_id = message['chat']['id']
            user_info = message.get('from', {})
            user_name = user_info.get('first_name', 'Unknown')
            
            self.stats['messages_processed'] += 1
            
            # 画像メッセージチェック
            if 'photo' in message:
                self.process_image_message(message, chat_id, user_name)
            elif 'document' in message:
                # 文書ファイルの場合
                doc = message['document']
                if doc.get('mime_type', '').startswith('image/'):
                    self.process_document_image(message, chat_id, user_name)
                else:
                    self.send_reply(chat_id, "📄 画像ファイルのみ対応しています")
            else:
                # テキストメッセージ
                text = message.get('text', '')
                if text:
                    logger.info(f"📨 テキストメッセージ: {text}")
                    self.send_reply(chat_id, f"📱 MacMini2014で受信確認\n💬 画像を送信するとOCR処理します")
            
        except Exception as e:
            logger.error(f"メッセージ処理エラー: {e}")
    
    def process_image_message(self, message, chat_id: int, user_name: str):
        """画像メッセージ処理"""
        try:
            photos = message['photo']
            # 最大サイズの画像を選択
            largest_photo = max(photos, key=lambda x: x.get('file_size', 0))
            file_id = largest_photo['file_id']
            file_size = largest_photo.get('file_size', 0)
            
            logger.info(f"📸 画像受信: {user_name} (サイズ: {file_size} bytes)")
            
            # 画像ダウンロード
            image_path = self.download_image(file_id, chat_id)
            if not image_path:
                self.send_reply(chat_id, "❌ 画像ダウンロードに失敗しました")
                return
            
            self.stats['images_processed'] += 1
            
            # OCR処理実行
            self.send_reply(chat_id, "🔍 OCR処理を開始します...")
            
            ocr_result = self.ocr_image(image_path)
            
            # 結果保存
            self.save_ocr_result(ocr_result, chat_id)
            
            # 結果を返信
            if ocr_result['success']:
                text = ocr_result['full_text']
                response = f"✅ OCR処理完了\n"
                response += f"⏱️ 処理時間: {ocr_result['processing_time']:.2f}秒\n"
                response += f"📏 文字数: {ocr_result['text_length']}\n"
                response += f"🔤 単語数: {ocr_result['word_count']}\n"
                response += f"📄 行数: {ocr_result['line_count']}\n\n"
                response += f"📝 認識テキスト:\n{text[:1000]}"
                
                if len(text) > 1000:
                    response += f"\n\n... (全{len(text)}文字)"
            else:
                response = f"❌ OCR処理失敗\n"
                response += f"エラー: {ocr_result['error']}"
            
            self.send_reply(chat_id, response)
            
        except Exception as e:
            logger.error(f"画像メッセージ処理エラー: {e}")
            self.send_reply(chat_id, f"❌ 処理エラー: {str(e)}")
    
    def process_document_image(self, message, chat_id: int, user_name: str):
        """文書画像処理"""
        try:
            document = message['document']
            file_id = document['file_id']
            file_name = document.get('file_name', 'unknown')
            file_size = document.get('file_size', 0)
            
            logger.info(f"📎 文書画像受信: {user_name} ({file_name}, {file_size} bytes)")
            
            # 画像ダウンロード
            image_path = self.download_image(file_id, chat_id)
            if not image_path:
                self.send_reply(chat_id, "❌ ファイルダウンロードに失敗しました")
                return
            
            self.stats['images_processed'] += 1
            
            # OCR処理
            self.send_reply(chat_id, f"🔍 {file_name} のOCR処理中...")
            
            ocr_result = self.ocr_image(image_path)
            self.save_ocr_result(ocr_result, chat_id)
            
            # 結果返信
            if ocr_result['success']:
                text = ocr_result['full_text']
                response = f"✅ OCR完了: {file_name}\n"
                response += f"📝 認識テキスト:\n{text[:1500]}"
                if len(text) > 1500:
                    response += f"\n\n... (全{len(text)}文字)"
            else:
                response = f"❌ OCR失敗: {file_name}\nエラー: {ocr_result['error']}"
            
            self.send_reply(chat_id, response)
            
        except Exception as e:
            logger.error(f"文書画像処理エラー: {e}")
            self.send_reply(chat_id, f"❌ 処理エラー: {str(e)}")
    
    def print_stats(self):
        """統計情報表示"""
        uptime = datetime.now() - self.stats['start_time']
        logger.info("📊 OCR Bot 統計")
        logger.info(f"  稼働時間: {uptime}")
        logger.info(f"  メッセージ処理: {self.stats['messages_processed']}")
        logger.info(f"  画像処理: {self.stats['images_processed']}")
        logger.info(f"  OCR成功: {self.stats['ocr_success']}")
        logger.info(f"  OCR失敗: {self.stats['ocr_failed']}")
    
    def run(self):
        """メイン実行ループ"""
        logger.info(f"🚀 {self.bot_name} 開始")
        
        try:
            while True:
                # 新着メッセージ取得
                updates = self.get_updates()
                
                if updates:
                    logger.info(f"📥 {len(updates)}件の新着メッセージを処理中...")
                    
                    for update in updates:
                        self.process_message(update)
                        self.last_update_id = update['update_id']
                    
                    # オフセット保存
                    self.save_offset(self.last_update_id)
                
                # 5分ごとに統計表示
                if int(time.time()) % 300 == 0:
                    self.print_stats()
                
                # 5秒待機
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("🛑 システム停止")
            return True
        except Exception as e:
            logger.error(f"❌ 実行エラー: {e}")
            return False

def main():
    print("=" * 60)
    print("MacMini2014 OCR Bot")
    print("画像OCR機能付きTelegramボット")
    print("Bot: @macmini2014_bot")
    print("停止: Ctrl+C")
    print("=" * 60)
    
    bot = MacMini2014OCRBot()
    success = bot.run()
    
    print("\n" + "=" * 60)
    print("MacMini2014 OCR Bot システム終了")
    print("=" * 60)

if __name__ == "__main__":
    main()