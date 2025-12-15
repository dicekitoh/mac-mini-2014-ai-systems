#!/usr/bin/env python3
"""
Google Cloud Speech-to-Text API 音声文字起こしツール
音声ファイルをテキストに変換します

必要なライブラリ:
pip install google-cloud-speech

使用方法:
python google_speech_to_text.py <音声ファイルパス> [--language ja-JP]
"""

import os
import sys
import argparse
from google.cloud import speech
import io

class SpeechToTextConverter:
    def __init__(self, credentials_path=None):
        """
        初期化
        
        Args:
            credentials_path: Google Cloud認証JSONファイルのパス
        """
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        self.client = speech.SpeechClient()
    
    def transcribe_file(self, audio_path, language_code='ja-JP'):
        """
        音声ファイルを文字起こし
        
        Args:
            audio_path: 音声ファイルのパス
            language_code: 言語コード（デフォルト: 日本語）
        
        Returns:
            文字起こし結果のテキスト
        """
        # 音声ファイルを読み込み
        with io.open(audio_path, 'rb') as audio_file:
            content = audio_file.read()
        
        # 音声データを設定
        audio = speech.RecognitionAudio(content=content)
        
        # 認識設定
        config = speech.RecognitionConfig(
            encoding=self._get_encoding(audio_path),
            sample_rate_hertz=self._get_sample_rate(audio_path),
            language_code=language_code,
            enable_automatic_punctuation=True,  # 句読点自動挿入
            model='latest_long',  # 長時間音声用モデル
        )
        
        # Speech-to-Text API実行
        print(f"音声ファイルを処理中: {audio_path}")
        response = self.client.recognize(config=config, audio=audio)
        
        # 結果を結合
        transcripts = []
        for result in response.results:
            transcripts.append(result.alternatives[0].transcript)
        
        return '\n'.join(transcripts)
    
    def transcribe_long_file(self, audio_uri, language_code='ja-JP'):
        """
        長時間音声ファイルの文字起こし（GCS URI使用）
        
        Args:
            audio_uri: Google Cloud Storage上の音声ファイルURI
            language_code: 言語コード
        
        Returns:
            文字起こし結果のテキスト
        """
        audio = speech.RecognitionAudio(uri=audio_uri)
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        
        # 長時間音声用の非同期処理
        operation = self.client.long_running_recognize(config=config, audio=audio)
        
        print("長時間音声を処理中...")
        response = operation.result(timeout=300)
        
        transcripts = []
        for result in response.results:
            transcripts.append(result.alternatives[0].transcript)
        
        return '\n'.join(transcripts)
    
    def _get_encoding(self, file_path):
        """ファイル拡張子から音声エンコーディングを判定"""
        ext = os.path.splitext(file_path)[1].lower()
        
        encoding_map = {
            '.wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            '.mp3': speech.RecognitionConfig.AudioEncoding.MP3,
            '.flac': speech.RecognitionConfig.AudioEncoding.FLAC,
            '.m4a': speech.RecognitionConfig.AudioEncoding.MP3,
            '.opus': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        }
        
        return encoding_map.get(ext, speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED)
    
    def _get_sample_rate(self, file_path):
        """音声ファイルのサンプルレートを取得（簡易版）"""
        # WAVファイルの場合は自動検出を使用
        # 他の形式はNoneを返して自動検出させる
        return None  # 自動検出


def main():
    parser = argparse.ArgumentParser(description='Google Speech-to-Text 音声文字起こしツール')
    parser.add_argument('audio_file', help='音声ファイルのパス')
    parser.add_argument('--language', '-l', default='ja-JP', help='言語コード（デフォルト: ja-JP）')
    parser.add_argument('--credentials', '-c', help='Google Cloud認証JSONファイルのパス')
    parser.add_argument('--output', '-o', help='出力ファイルパス（指定しない場合は標準出力）')
    
    args = parser.parse_args()
    
    # ファイル存在確認
    if not os.path.exists(args.audio_file):
        print(f"エラー: 音声ファイルが見つかりません: {args.audio_file}")
        sys.exit(1)
    
    try:
        # 文字起こし実行
        converter = SpeechToTextConverter(args.credentials)
        result = converter.transcribe_file(args.audio_file, args.language)
        
        # 結果出力
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"文字起こし結果を保存しました: {args.output}")
        else:
            print("\n=== 文字起こし結果 ===")
            print(result)
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()