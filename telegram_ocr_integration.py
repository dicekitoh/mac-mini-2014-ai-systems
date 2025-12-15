#!/usr/bin/env python3
"""
Telegram BOT OCR統合スクリプト
画像受信時に自動OCR処理を実行
"""

import os
import sys
import subprocess
from datetime import datetime

def process_telegram_image(image_path, chat_id=None):
    """Telegram経由で受信した画像をOCR処理"""
    
    print(f"📱 Telegram画像を受信: {image_path}")
    
    # 受信画像フォルダにコピー
    watch_dir = "/tmp/received_images"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"telegram_{timestamp}_{os.path.basename(image_path)}"
    destination = os.path.join(watch_dir, filename)
    
    try:
        import shutil
        shutil.copy2(image_path, destination)
        print(f"📁 画像をコピー: {destination}")
        
        # OCR処理スクリプトを実行
        env = os.environ.copy()
        env['GOOGLE_CLOUD_API_KEY'] = "***REMOVED***"
        
        result = subprocess.run([
            'python3', '/home/fujinosuke/projects/ocr_file_receiver.py'
        ], env=env, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ OCR処理完了")
            return True
        else:
            print(f"❌ OCR処理失敗")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_telegram_image(sys.argv[1])
    else:
        print("使用方法: python3 telegram_ocr_integration.py <画像ファイルパス>")
