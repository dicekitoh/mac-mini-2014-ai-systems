#!/usr/bin/env python3
"""
SSH経由でのAqua Voice音声入力システム
ネットワーク経由でPulseAudioから音声を取得し、Aqua Voice APIで音声認識
"""

import os
import subprocess
import tempfile
import time
import json
import requests
from typing import Optional, Dict, Any

class AquaVoiceSSHInput:
    def __init__(self, api_key: Optional[str] = None):
        """
        初期化
        :param api_key: Aqua Voice API Key (環境変数 AQUA_VOICE_API_KEY からも取得可能)
        """
        self.api_key = api_key or os.getenv('AQUA_VOICE_API_KEY')
        self.pulse_server = 'tcp:127.0.0.1:4713'
        
        # PulseAudio環境変数設定
        os.environ['PULSE_SERVER'] = self.pulse_server
        
    def setup_pulse_network(self) -> bool:
        """PulseAudioネットワークモジュール設定"""
        try:
            # TCPモジュール有効化確認
            result = subprocess.run(['pactl', 'list', 'modules'], 
                                 capture_output=True, text=True)
            if 'module-native-protocol-tcp' not in result.stdout:
                print("PulseAudioネットワークモジュールを有効化中...")
                subprocess.run(['pactl', 'load-module', 'module-native-protocol-tcp', 
                              'auth-ip-acl=127.0.0.1', 'port=4713'], check=True)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"PulseAudio設定エラー: {e}")
            return False
    
    def check_audio_sources(self) -> Dict[str, Any]:
        """利用可能な音声ソース確認"""
        try:
            result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                                  capture_output=True, text=True, check=True)
            
            sources = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        sources.append({
                            'id': parts[0],
                            'name': parts[1],
                            'driver': parts[2] if len(parts) > 2 else 'unknown'
                        })
            
            return {'success': True, 'sources': sources}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': str(e)}
    
    def record_audio(self, duration: int = 5, source: str = 'auto_null.monitor') -> Optional[str]:
        """
        SSH経由でPulseAudio音声録音
        :param duration: 録音秒数
        :param source: 音声ソース名
        :return: 録音ファイルパス (成功時) or None (失敗時)
        """
        try:
            # 一時ファイル作成
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            print(f"音声録音開始... ({duration}秒間)")
            
            # timeoutで録音時間制限
            cmd = [
                'timeout', f'{duration}s',
                'parecord',
                '--device', source,
                '--format=s16le',
                '--rate=44100',
                '--channels=1',
                tmp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # timeoutによる終了は正常 (exit code 124)
            if result.returncode in [0, 124] and os.path.exists(tmp_path):
                file_size = os.path.getsize(tmp_path)
                print(f"録音完了: {tmp_path} ({file_size} bytes)")
                return tmp_path if file_size > 44 else None  # WAVヘッダ分を考慮
            else:
                print(f"録音失敗: exit code {result.returncode}")
                if result.stderr:
                    print(f"エラー: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"録音例外エラー: {e}")
            return None
    
    def send_to_aquavoice(self, audio_file: str) -> Optional[Dict[str, Any]]:
        """
        Aqua Voice APIに音声ファイル送信 (仮実装)
        実際のAPIエンドポイントとパラメータは要確認
        """
        if not self.api_key:
            return {'error': 'API key not provided'}
        
        # 仮のAPIエンドポイント
        api_url = 'https://api.withaqua.com/v1/speech-to-text'
        
        try:
            with open(audio_file, 'rb') as f:
                files = {'audio': f}
                headers = {'Authorization': f'Bearer {self.api_key}'}
                
                print("Aqua Voice APIに送信中...")
                response = requests.post(api_url, files=files, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {'error': f'API Error: {response.status_code}'}
                    
        except requests.RequestException as e:
            return {'error': f'Request failed: {e}'}
        except Exception as e:
            return {'error': f'Unexpected error: {e}'}
    
    def voice_input_session(self, duration: int = 5) -> Dict[str, Any]:
        """音声入力セッション実行"""
        print("=== Aqua Voice SSH音声入力セッション ===")
        
        # 1. PulseAudio設定確認
        if not self.setup_pulse_network():
            return {'success': False, 'error': 'PulseAudio setup failed'}
        
        # 2. 音声ソース確認
        sources_info = self.check_audio_sources()
        if not sources_info['success']:
            return {'success': False, 'error': 'Audio sources check failed'}
        
        print(f"利用可能な音声ソース: {len(sources_info['sources'])}個")
        for source in sources_info['sources']:
            print(f"  - {source['name']} ({source['driver']})")
        
        # 3. 音声録音
        if not sources_info['sources']:
            return {'success': False, 'error': 'No audio sources available'}
        
        source_name = sources_info['sources'][0]['name']
        audio_file = self.record_audio(duration, source_name)
        
        if not audio_file:
            return {'success': False, 'error': 'Audio recording failed'}
        
        # 4. Aqua Voice API送信 (仮実装)
        api_result = self.send_to_aquavoice(audio_file)
        
        # 5. 一時ファイル削除
        try:
            os.unlink(audio_file)
        except:
            pass
        
        return {
            'success': True,
            'audio_sources': len(sources_info['sources']),
            'api_result': api_result
        }

def main():
    """メイン実行"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SSH経由Aqua Voice音声入力')
    parser.add_argument('--duration', type=int, default=5, help='録音秒数 (default: 5)')
    parser.add_argument('--api-key', help='Aqua Voice API Key')
    
    args = parser.parse_args()
    
    # 音声入力システム初期化
    voice_input = AquaVoiceSSHInput(api_key=args.api_key)
    
    # 音声入力セッション実行
    result = voice_input.voice_input_session(duration=args.duration)
    
    # 結果出力
    print("\n=== セッション結果 ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return 0 if result['success'] else 1

if __name__ == "__main__":
    exit(main())