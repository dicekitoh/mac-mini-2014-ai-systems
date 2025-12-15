#!/usr/bin/env python3
import os
import subprocess
import time

def test_network_audio():
    """ネットワーク経由でのPulseAudio音声録音テスト"""
    
    # 環境変数設定
    os.environ['PULSE_SERVER'] = 'tcp:127.0.0.1:4713'
    
    print("ネットワーク経由PulseAudio接続テスト開始")
    
    # 利用可能なソース一覧
    try:
        result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                              capture_output=True, text=True, check=True)
        print("利用可能な音声ソース:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ソース一覧取得エラー: {e}")
        return False
    
    # 5秒間の音声録音テスト
    output_file = "network_audio_test.wav"
    
    try:
        print(f"5秒間の音声録音を開始... ({output_file})")
        cmd = ['timeout', '5s', 'parecord', '--format=s16le', '--rate=44100', '--channels=1', output_file]
        subprocess.run(cmd, check=True)
        
        print(f"録音完了: {output_file}")
        
        # ファイルサイズ確認
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"ファイルサイズ: {file_size} bytes")
            return file_size > 0
        else:
            print("録音ファイルが作成されませんでした")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"録音エラー: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("録音タイムアウト")
        return False

if __name__ == "__main__":
    success = test_network_audio()
    print(f"テスト結果: {'成功' if success else '失敗'}")