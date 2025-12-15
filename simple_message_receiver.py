#!/usr/bin/env python3
"""
シンプルなメッセージ受信テスト
MacMini2014 Notifier BOTからのメッセージを手動で処理
"""

import os
import sys
from datetime import datetime

def process_message(message_text):
    """受信したメッセージを処理"""
    print("📱 MacMini2014 Notifier BOTからのメッセージ受信")
    print("="*60)
    print(f"⏰ 受信時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📝 メッセージ内容:")
    print("-"*60)
    print(message_text)
    print("-"*60)
    
    # 文字数統計
    char_count = len(message_text)
    line_count = len(message_text.split('\n'))
    word_count = len(message_text.split())
    
    print(f"\n📊 統計情報:")
    print(f"  文字数: {char_count}")
    print(f"  行数: {line_count}")
    print(f"  単語数: {word_count}")
    
    # 日本語文字の検出
    japanese_chars = sum(1 for char in message_text if 
                       '\u3040' <= char <= '\u309F' or  # ひらがな
                       '\u30A0' <= char <= '\u30FF' or  # カタカナ  
                       '\u4E00' <= char <= '\u9FAF')    # 漢字
    
    if japanese_chars > 0:
        print(f"  日本語文字数: {japanese_chars}")
        print(f"  日本語率: {japanese_chars/char_count*100:.1f}%")
    
    # ファイルに保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"/tmp/notifier_message_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"MacMini2014 Notifier BOT メッセージ\n")
        f.write(f"受信時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n")
        f.write(message_text)
    
    print(f"\n💾 メッセージを保存: {filename}")
    print("\n✅ メッセージ処理完了!")

def main():
    """メイン処理"""
    print("📱 MacMini2014 Notifier BOT メッセージ受信テスト")
    print("="*60)
    
    if len(sys.argv) > 1:
        # コマンドライン引数からメッセージを取得
        message = " ".join(sys.argv[1:])
        process_message(message)
    else:
        # 対話式でメッセージを入力
        print("MacMini2014 Notifier BOTから受信したメッセージを入力してください")
        print("(複数行の場合は、最後に空行を入力してください)")
        print()
        
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        
        if lines:
            message = "\n".join(lines)
            process_message(message)
        else:
            print("❌ メッセージが入力されませんでした")

if __name__ == "__main__":
    main()