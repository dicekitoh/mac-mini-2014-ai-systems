#!/usr/bin/env python3
"""
テスト用の音声ファイルを作成（サンプルテキストから）
実際の音声ファイルの代わりに、テスト用のダミーWAVファイルを作成
"""

import struct
import wave

def create_test_wav(filename="test_audio.wav", duration=3, sample_rate=16000):
    """
    テスト用の簡単なWAVファイルを作成
    （無音の音声ファイル）
    """
    # WAVファイルのパラメータ
    channels = 1  # モノラル
    sample_width = 2  # 16ビット
    
    # サンプル数
    n_samples = duration * sample_rate
    
    # 無音のデータを作成（実際には少しノイズを入れる）
    samples = []
    for i in range(n_samples):
        # 非常に小さな振幅のサイン波（ほぼ無音）
        value = int(10 * (i % 100) / 100)
        samples.append(struct.pack('<h', value))
    
    # WAVファイルとして保存
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(samples))
    
    print(f"テスト用WAVファイルを作成しました: {filename}")
    print(f"- 長さ: {duration}秒")
    print(f"- サンプルレート: {sample_rate}Hz")
    print(f"- チャンネル: モノラル")
    print("\n注意: これは無音に近いテストファイルです。")
    print("実際の音声認識テストには、音声が含まれるファイルを使用してください。")

if __name__ == "__main__":
    create_test_wav()