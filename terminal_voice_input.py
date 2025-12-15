#!/usr/bin/env python3
"""
ターミナル音声入力ツール
リアルタイム音声認識でコマンドを入力できます

必要なライブラリ:
pip install google-cloud-speech pyaudio keyboard

使用方法:
python3 terminal_voice_input.py
"""

import os
import sys
import threading
import queue
import time
import subprocess
import signal
from google.cloud import speech
import pyaudio
import keyboard

class TerminalVoiceInput:
    def __init__(self):
        self.client = speech.SpeechClient()
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.is_running = True
        
        # 音声設定
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        
    def audio_callback(self, in_data, frame_count, time_info, status):
        """音声データをキューに追加"""
        if self.is_recording:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
        
    def start_recording(self):
        """音声録音開始"""
        print("🎤 音声入力開始... (Spaceキーで終了)")
        self.is_recording = True
        self.audio_queue = queue.Queue()
        
    def stop_recording(self):
        """音声録音終了"""
        print("🛑 音声入力終了")
        self.is_recording = False
        
    def process_audio(self):
        """音声データを処理してテキストに変換"""
        if self.audio_queue.empty():
            return ""
            
        # キューから音声データを取得
        audio_data = b''
        while not self.audio_queue.empty():
            try:
                chunk = self.audio_queue.get_nowait()
                audio_data += chunk
            except queue.Empty:
                break
                
        if not audio_data:
            return ""
            
        try:
            # Google Speech-to-Text API設定
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate,
                language_code='ja-JP',
                enable_automatic_punctuation=False,
                model='command_and_search',  # コマンド認識用モデル
            )
            
            # 音声認識実行
            response = self.client.recognize(config=config, audio=audio)
            
            # 結果を取得
            if response.results:
                return response.results[0].alternatives[0].transcript
            else:
                return ""
                
        except Exception as e:
            print(f"音声認識エラー: {e}")
            return ""
            
    def execute_command(self, text):
        """認識されたテキストをコマンドとして実行"""
        if not text.strip():
            return
            
        print(f"認識されたコマンド: {text}")
        
        # 確認プロンプト
        response = input("このコマンドを実行しますか? (y/N): ")
        if response.lower() in ['y', 'yes']:
            try:
                subprocess.run(text, shell=True, check=False)
            except Exception as e:
                print(f"コマンド実行エラー: {e}")
        else:
            print("コマンド実行をキャンセルしました")
            
    def run(self):
        """メインループ"""
        # PyAudio初期化
        p = pyaudio.PyAudio()
        
        try:
            # 音声ストリーム開始
            stream = p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self.audio_callback
            )
            
            stream.start_stream()
            
            print("=== ターミナル音声入力システム ===")
            print("操作方法:")
            print("- Spaceキーを押している間、音声を録音")
            print("- Spaceキーを離すと音声認識を実行")
            print("- 'q'キーで終了")
            print()
            
            # キーボードイベント処理
            keyboard.on_press_key('space', lambda _: self.start_recording())
            keyboard.on_release_key('space', lambda _: self._on_space_release())
            
            # メインループ
            while self.is_running:
                try:
                    if keyboard.is_pressed('q'):
                        break
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            print(f"エラー: {e}")
        finally:
            # クリーンアップ
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()
            print("\n音声入力システムを終了しました")
            
    def _on_space_release(self):
        """Spaceキー離した時の処理"""
        if self.is_recording:
            self.stop_recording()
            
            # 少し待ってから音声処理
            time.sleep(0.5)
            text = self.process_audio()
            
            if text:
                self.execute_command(text)
            else:
                print("音声が認識されませんでした")

def main():
    # 依存関係チェック
    try:
        import pyaudio
        import keyboard
    except ImportError as e:
        print(f"必要なライブラリがインストールされていません: {e}")
        print("以下のコマンドでインストールしてください:")
        print("pip install pyaudio keyboard")
        sys.exit(1)
        
    # 認証確認
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        print("エラー: GOOGLE_APPLICATION_CREDENTIALS環境変数が設定されていません")
        print("認証ファイルのパスを設定してください:")
        print("export GOOGLE_APPLICATION_CREDENTIALS='path/to/credentials.json'")
        sys.exit(1)
        
    # 音声入力システム開始
    voice_input = TerminalVoiceInput()
    
    def signal_handler(sig, frame):
        voice_input.is_running = False
        
    signal.signal(signal.SIGINT, signal_handler)
    voice_input.run()

if __name__ == '__main__':
    main()