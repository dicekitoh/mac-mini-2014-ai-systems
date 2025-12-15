#!/usr/bin/env python3
"""
MacMini2014 Notifier BOT テキストメッセージ受信テストシステム
"""

import os
import time
from datetime import datetime
import json

class TextMessageReceiver:
    def __init__(self):
        self.watch_directory = "/tmp/received_messages"  # メッセージ受信フォルダ
        self.processed_directory = "/tmp/processed_messages"  # 処理済みフォルダ
        
        # ディレクトリを作成
        os.makedirs(self.watch_directory, exist_ok=True)
        os.makedirs(self.processed_directory, exist_ok=True)
        
        print(f"📱 テキストメッセージ受信システム起動")
        print(f"📁 受信フォルダ: {self.watch_directory}")
        print(f"📁 処理済みフォルダ: {self.processed_directory}")
    
    def process_text_message(self, message_file):
        """テキストメッセージを処理"""
        try:
            message_path = os.path.join(self.watch_directory, message_file)
            
            print(f"\n📥 新しいメッセージを受信: {message_file}")
            
            # メッセージ内容を読み取り
            with open(message_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"⏰ 受信時刻: {timestamp}")
            print(f"📝 メッセージ内容:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            
            # メッセージ分析
            char_count = len(content)
            line_count = len(content.split('\n'))
            word_count = len(content.split())
            
            print(f"📊 統計情報:")
            print(f"  文字数: {char_count}")
            print(f"  行数: {line_count}")
            print(f"  単語数: {word_count}")
            
            # 日本語文字の検出
            japanese_chars = sum(1 for char in content if '\u3040' <= char <= '\u309F' or  # ひらがな
                                                        '\u30A0' <= char <= '\u30FF' or  # カタカナ
                                                        '\u4E00' <= char <= '\u9FAF')    # 漢字
            
            if japanese_chars > 0:
                print(f"  日本語文字数: {japanese_chars}")
                print(f"  日本語率: {japanese_chars/char_count*100:.1f}%")
            
            # 処理結果をログファイルに保存
            log_entry = {
                "timestamp": timestamp,
                "filename": message_file,
                "content": content,
                "stats": {
                    "char_count": char_count,
                    "line_count": line_count,
                    "word_count": word_count,
                    "japanese_chars": japanese_chars
                }
            }
            
            log_file = f"/tmp/message_log_{datetime.now().strftime('%Y%m%d')}.json"
            
            # 既存のログを読み込み
            logs = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except:
                    logs = []
            
            logs.append(log_entry)
            
            # ログを保存
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            print(f"💾 ログ保存: {log_file}")
            
            # 処理済みフォルダに移動
            processed_path = os.path.join(self.processed_directory, message_file)
            import shutil
            shutil.move(message_path, processed_path)
            print(f"📁 メッセージを処理済みフォルダに移動: {processed_path}")
            
            print(f"✅ メッセージ処理完了!")
            
            return True
            
        except Exception as e:
            print(f"❌ メッセージ処理エラー: {e}")
            return False
    
    def process_new_messages(self):
        """新しいメッセージを処理"""
        try:
            files = os.listdir(self.watch_directory)
            message_files = [f for f in files if f.endswith('.txt') or f.endswith('.msg')]
            
            for message_file in message_files:
                self.process_text_message(message_file)
                
        except Exception as e:
            print(f"❌ ファイル処理エラー: {e}")
    
    def watch_for_messages(self, interval=3):
        """メッセージ監視ループ"""
        print(f"\n👀 メッセージ監視開始（{interval}秒間隔）")
        print(f"テキストファイルを {self.watch_directory} に配置してください")
        
        try:
            while True:
                self.process_new_messages()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n⏹️ メッセージ監視を停止しました")

def create_test_message(content):
    """テスト用のメッセージファイルを作成"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"test_message_{timestamp}.txt"
    filepath = f"/tmp/received_messages/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📝 テストメッセージ作成: {filepath}")
    return filepath

def main():
    """メイン処理"""
    print("📱 MacMini2014 テキストメッセージ受信テスト")
    print("="*60)
    
    import sys
    
    if len(sys.argv) > 1:
        # テストメッセージを作成
        test_content = " ".join(sys.argv[1:])
        create_test_message(test_content)
        print("\n3秒後に処理を開始します...")
        time.sleep(3)
    
    receiver = TextMessageReceiver()
    
    print(f"\n📋 使用方法:")
    print(f"1. MacMini2014 Notifier BOTからテキストメッセージを送信")
    print(f"2. または手動でテキストファイルを {receiver.watch_directory} に配置")
    print(f"3. 自動的にメッセージが解析されます")
    
    # メッセージ監視開始
    receiver.watch_for_messages()

if __name__ == "__main__":
    main()