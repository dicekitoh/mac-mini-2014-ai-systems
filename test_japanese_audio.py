#!/usr/bin/env python3
"""
日本語音声ファイルのテスト方法
"""

print("=== 日本語音声の文字起こしテスト ===\n")
print("日本語音声ファイルを用意する方法：")
print("1. スマートフォンのボイスレコーダーで録音")
print("   - 例：「今日は良い天気ですね」")
print("   - 形式：WAV、MP3、M4Aなど")
print()
print("2. 録音したファイルをPCに転送")
print()
print("3. 文字起こしを実行：")
print("   python google_speech_to_text.py 録音ファイル.wav")
print("   python google_speech_to_text.py 録音ファイル.mp3")
print()
print("4. 結果をファイルに保存する場合：")
print("   python google_speech_to_text.py 録音ファイル.wav --output 結果.txt")
print()
print("注意：日本語の場合は --language ja-JP がデフォルトなので指定不要です")