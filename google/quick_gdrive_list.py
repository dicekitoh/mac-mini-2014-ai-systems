#\!/usr/bin/env python3
import os
import subprocess
import json

def check_rclone():
    """rcloneの設定を確認"""
    try:
        # rclone設定を確認
        result = subprocess.run(['rclone', 'config', 'dump'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            config = json.loads(result.stdout)
            print('rclone設定:')
            for remote, settings in config.items():
                print(f'- {remote}: {settings.get("type", "不明")}')
                if 'client_id' in settings:
                    print(f'  Client ID: {settings["client_id"][:20]}...')
        else:
            print('rclone設定の読み込みエラー')
            
    except Exception as e:
        print(f'エラー: {e}')

def try_gdrive_access():
    """Google Driveへのアクセスを試行"""
    print('\nGoogle Driveアクセス試行中...')
    
    # 利用可能なリモートを確認
    remotes = ['googledrive:', 'e:']
    
    for remote in remotes:
        print(f'\n{remote} を試しています...')
        try:
            # ファイル数を確認（認証不要な操作）
            result = subprocess.run(['rclone', 'size', remote], 
                                  capture_output=True, text=True,
                                  timeout=10)
            
            if 'Failed to create file system' in result.stderr:
                print(f'{remote} は認証が必要です')
                
                # 認証URL生成を試みる
                auth_result = subprocess.run(['rclone', 'config', 'reconnect', remote.rstrip(':')],
                                           capture_output=True, text=True)
                if 'http' in auth_result.stderr:
                    # URLを抽出
                    for line in auth_result.stderr.split('\n'):
                        if 'http' in line:
                            print(f'認証URL: {line.strip()}')
                            break
            else:
                print(f'{remote} アクセス成功！')
                print(result.stdout)
                
                # ファイル一覧を表示
                list_result = subprocess.run(['rclone', 'ls', remote, '--max-depth', '1'],
                                           capture_output=True, text=True)
                if list_result.returncode == 0:
                    print('\nファイル一覧:')
                    lines = list_result.stdout.strip().split('\n')[:10]
                    for line in lines:
                        print(line)
                    if len(lines) == 10:
                        print('... (他のファイルは省略)')
                    
        except subprocess.TimeoutExpired:
            print(f'{remote} タイムアウト')
        except Exception as e:
            print(f'{remote} エラー: {e}')

def main():
    print('=== Google Drive アクセステスト ===\n')
    
    # rclone設定確認
    check_rclone()
    
    # アクセス試行
    try_gdrive_access()
    
    print('\n\n既存の認証情報:')
    print('- Google Contacts API: 動作中')
    print('- Google Calendar API: 設定済み')
    print('- Google Tasks API: 設定済み')
    print('\nGoogle Drive APIを使用するには認証が必要です。')

if __name__ == '__main__':
    main()
