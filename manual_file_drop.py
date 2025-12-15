#!/usr/bin/env python3
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
