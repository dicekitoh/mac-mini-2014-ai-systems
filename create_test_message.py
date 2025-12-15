#!/usr/bin/env python3
"""
テスト用メッセージファイル作成
"""

import os
from datetime import datetime

# ディレクトリを作成
os.makedirs("/tmp/received_messages", exist_ok=True)

# テストメッセージを作成
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"bot_message_{timestamp}.txt"
filepath = f"/tmp/received_messages/{filename}"

test_message = """MacMini2014 Notifier BOTからのテストメッセージです。

このメッセージが正しく受信・解析されるかをテストしています。

内容：
- 日本語テキストの認識
- 英語 English text recognition
- 数字 1234567890
- 記号 !@#$%^&*()

複雑な文章：
「これは日本語OCRシステムのテストです」
『MacMini2014での高精度処理』
※正常に動作することを確認※

テスト完了時刻: """ + datetime.now().strftime('%Y年%m月%d日 %H時%M分%S秒')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(test_message)

print(f"✅ テストメッセージを作成しました: {filepath}")
print(f"📝 内容:")
print("-" * 50)
print(test_message)
print("-" * 50)
print(f"\nテキストメッセージ受信システムが自動的に処理します。")