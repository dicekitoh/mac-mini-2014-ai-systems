#!/usr/bin/env python3
"""
シンプル音声コマンドツール
音声ファイルからコマンドを認識して実行

使用方法:
1. 音声を録音してファイルに保存
2. python3 simple_voice_command.py <音声ファイル>
"""

import os
import sys
import argparse
import subprocess
from google.cloud import speech
import io

class SimpleVoiceCommand:
    def __init__(self):
        self.client = speech.SpeechClient()
        
    def transcribe_command(self, audio_path):
        """音声ファイルをコマンドとして文字起こし"""
        try:
            with io.open(audio_path, 'rb') as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=self._get_encoding(audio_path),
                language_code='ja-JP',
                enable_automatic_punctuation=False,
                model='command_and_search',
            )
            
            response = self.client.recognize(config=config, audio=audio)
            
            if response.results:
                return response.results[0].alternatives[0].transcript
            else:
                return None
                
        except Exception as e:
            print(f"音声認識エラー: {e}")
            return None
            
    def _get_encoding(self, file_path):
        """ファイル拡張子から音声エンコーディングを判定"""
        ext = os.path.splitext(file_path)[1].lower()
        
        encoding_map = {
            '.wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            '.mp3': speech.RecognitionConfig.AudioEncoding.MP3,
            '.flac': speech.RecognitionConfig.AudioEncoding.FLAC,
            '.m4a': speech.RecognitionConfig.AudioEncoding.MP3,
        }
        
        return encoding_map.get(ext, speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED)
        
    def execute_command(self, command_text):
        """認識されたテキストをコマンドとして実行"""
        if not command_text:
            print("コマンドが認識されませんでした")
            return
            
        print(f"認識されたコマンド: {command_text}")
        
        # 安全のため確認プロンプト
        response = input("このコマンドを実行しますか? (y/N): ")
        if response.lower() in ['y', 'yes']:
            try:
                result = subprocess.run(
                    command_text, 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                
                if result.stdout:
                    print("出力:")
                    print(result.stdout)
                if result.stderr:
                    print("エラー:")
                    print(result.stderr)
                    
            except Exception as e:
                print(f"コマンド実行エラー: {e}")
        else:
            print("コマンド実行をキャンセルしました")

def main():
    parser = argparse.ArgumentParser(description='音声ファイルからコマンドを認識・実行')
    parser.add_argument('audio_file', help='音声ファイルのパス')
    
    args = parser.parse_args()
    
    # ファイル存在確認
    if not os.path.exists(args.audio_file):
        print(f"エラー: 音声ファイルが見つかりません: {args.audio_file}")
        sys.exit(1)
        
    # 認証確認
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        print("エラー: GOOGLE_APPLICATION_CREDENTIALS環境変数が設定されていません")
        sys.exit(1)
        
    # 音声コマンド実行
    voice_command = SimpleVoiceCommand()
    command_text = voice_command.transcribe_command(args.audio_file)
    voice_command.execute_command(command_text)

if __name__ == '__main__':
    main()