#!/usr/bin/env python3
"""
Google Speech-to-Text API 簡易テストスクリプト
APIの動作確認用
"""

import os
import io
from google.cloud import speech

def create_test_audio():
    """テスト用の音声データを作成（実際には使用できません）"""
    print("テスト用音声ファイルを準備してください。")
    print("例: test_audio.wav")
    print("\n音声ファイルの録音方法:")
    print("1. スマートフォンのボイスレコーダーアプリで録音")
    print("2. PCのマイクで録音")
    print("3. 既存の音声ファイルを使用")
    return None

def test_speech_api():
    """Speech-to-Text APIの接続テスト"""
    try:
        # 認証確認
        if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
            print("警告: GOOGLE_APPLICATION_CREDENTIALS環境変数が設定されていません")
            print("認証ファイルのパスを設定してください:")
            print("export GOOGLE_APPLICATION_CREDENTIALS='path/to/credentials.json'")
            return False
        
        # クライアント作成テスト
        client = speech.SpeechClient()
        print("✓ Google Cloud Speech-to-Text クライアントの作成に成功")
        
        # API接続テスト（短い音声データでテスト）
        # 実際の音声ファイルがある場合のテストコード
        test_file = "test_audio.wav"
        if os.path.exists(test_file):
            print(f"\nテストファイル '{test_file}' を使用して文字起こしをテスト...")
            
            with io.open(test_file, 'rb') as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code='ja-JP',
            )
            
            response = client.recognize(config=config, audio=audio)
            
            if response.results:
                print("✓ 文字起こし成功!")
                for result in response.results:
                    print(f"認識結果: {result.alternatives[0].transcript}")
            else:
                print("✓ APIは動作していますが、音声が認識されませんでした")
        else:
            print(f"\nテストファイル '{test_file}' が見つかりません")
            print("実際の音声ファイルでテストするには、音声ファイルを準備してください")
        
        return True
        
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        return False

def main():
    print("=== Google Speech-to-Text API テスト ===\n")
    
    # API接続テスト
    if test_speech_api():
        print("\n✓ APIの基本的な接続は成功しています")
        print("\n次のステップ:")
        print("1. 音声ファイルを準備")
        print("2. python google_speech_to_text.py <音声ファイル> を実行")
    else:
        print("\n✗ APIの接続に失敗しました")
        print("\nトラブルシューティング:")
        print("1. Google Cloud Consoleで Speech-to-Text APIが有効か確認")
        print("2. 認証ファイルが正しく設定されているか確認")
        print("3. google_speech_to_text_setup.md を参照")

if __name__ == '__main__':
    main()