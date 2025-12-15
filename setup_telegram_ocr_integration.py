#!/usr/bin/env python3
"""
Telegram BOTにOCR機能を統合するセットアップスクリプト
"""

import os
import shutil

def setup_telegram_ocr_integration():
    """Telegram BOTにOCR機能を統合"""
    
    print("🔧 Telegram BOT OCR統合セットアップ")
    print("="*50)
    
    # 必要なディレクトリを作成
    directories = [
        "/tmp/received_images",
        "/tmp/processed_images", 
        "/tmp/ocr_results"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 ディレクトリ作成: {directory}")
    
    # Contact Manager BOTのパスを確認
    bot_path = "/home/fujinosuke/google_contacts/contact_manager_v2_bot_github"
    
    if os.path.exists(bot_path):
        print(f"✅ Contact Manager BOT発見: {bot_path}")
        
        # OCR統合用の設定ファイルを作成
        config_content = '''
# OCR統合設定
OCR_ENABLED = True
WATCH_DIRECTORY = "/tmp/received_images"
PROCESSED_DIRECTORY = "/tmp/processed_images"
OCR_SCRIPT_PATH = "/home/fujinosuke/projects/google_vision_ocr_test.py"
GOOGLE_CLOUD_API_KEY = "***REMOVED***"

# 画像受信時のOCR自動実行
AUTO_OCR_ON_IMAGE_RECEIVE = True
AUTO_ROTATION_CORRECTION = True
'''
        
        config_file = os.path.join(bot_path, "ocr_config.py")
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print(f"📝 OCR設定ファイル作成: {config_file}")
        
        # 簡単なTelegram OCR統合スクリプトを作成
        telegram_ocr_script = '''#!/usr/bin/env python3
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
'''
        
        telegram_script_path = "/home/fujinosuke/projects/telegram_ocr_integration.py"
        with open(telegram_script_path, 'w') as f:
            f.write(telegram_ocr_script)
        
        os.chmod(telegram_script_path, 0o755)
        print(f"📱 Telegram OCR統合スクリプト作成: {telegram_script_path}")
        
    else:
        print(f"❌ Contact Manager BOTが見つかりません: {bot_path}")
    
    # 手動テスト用の簡単なファイル配置スクリプト
    manual_test_script = '''#!/usr/bin/env python3
"""
手動テスト用: ファイルを受信フォルダに配置
"""

import sys
import shutil
import os
from datetime import datetime

if len(sys.argv) > 1:
    source_file = sys.argv[1]
    if os.path.exists(source_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"manual_{timestamp}_{os.path.basename(source_file)}"
        destination = f"/tmp/received_images/{filename}"
        
        shutil.copy2(source_file, destination)
        print(f"✅ ファイルを受信フォルダに配置: {destination}")
        print(f"OCRファイル受信システムが自動的に処理します")
    else:
        print(f"❌ ファイルが見つかりません: {source_file}")
else:
    print("使用方法: python3 manual_file_drop.py <画像ファイルパス>")
'''
    
    manual_script_path = "/home/fujinosuke/projects/manual_file_drop.py"
    with open(manual_script_path, 'w') as f:
        f.write(manual_test_script)
    
    os.chmod(manual_script_path, 0o755)
    print(f"🛠️ 手動テストスクリプト作成: {manual_script_path}")
    
    print(f"\n🎉 セットアップ完了!")
    print(f"\n📋 使用方法:")
    print(f"1. OCRファイル受信システム起動:")
    print(f"   python3 /home/fujinosuke/projects/ocr_file_receiver.py")
    print(f"")
    print(f"2. 手動でファイルをテスト:")
    print(f"   python3 /home/fujinosuke/projects/manual_file_drop.py <画像ファイル>")
    print(f"")
    print(f"3. Telegram BOTから画像を送信すると自動OCR処理が実行されます")

if __name__ == "__main__":
    setup_telegram_ocr_integration()