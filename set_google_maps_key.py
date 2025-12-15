#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps API キー設定（対話型なし版）
"""

import os
import json
from pathlib import Path

def set_api_key(api_key):
    """APIキーを設定"""
    print(f"🔑 APIキー設定中...")
    
    # 1. 環境変数設定
    bashrc_path = Path.home() / '.bashrc'
    export_line = f'\nexport GOOGLE_MAPS_API_KEY="{api_key}"'
    
    try:
        # 既存の設定を確認
        with open(bashrc_path, 'r') as f:
            content = f.read()
        
        if 'GOOGLE_MAPS_API_KEY' not in content:
            with open(bashrc_path, 'a') as f:
                f.write(export_line)
            print("✅ 環境変数を.bashrcに追加しました")
        else:
            print("ℹ️  環境変数は既に設定されています")
        
        # 現在のセッションにも設定
        os.environ['GOOGLE_MAPS_API_KEY'] = api_key
        
    except Exception as e:
        print(f"❌ 環境変数設定エラー: {e}")
        return False
    
    # 2. 設定ファイル保存
    config_path = Path('/home/fujinosuke/google_maps_config.json')
    config_data = {
        'google_maps_api_key': api_key,
        'project_name': 'Route Optimizer',
        'enabled_apis': [
            'Maps JavaScript API',
            'Geocoding API', 
            'Distance Matrix API',
            'Places API'
        ],
        'created_at': '2025-06-15'
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # パーミッション設定
        os.chmod(config_path, 0o600)
        
        print(f"✅ 設定ファイルに保存しました: {config_path}")
        
    except Exception as e:
        print(f"❌ 設定ファイル保存エラー: {e}")
        return False
    
    print("\n✅ Google Maps API キー設定完了!")
    print("\n📋 次のステップ:")
    print("1. 環境変数を有効化: source ~/.bashrc")
    print("2. テスト実行: python3 /home/fujinosuke/projects/route_optimizer_tsp.py")
    
    return True

# APIキーを設定
API_KEY = "***REMOVED***"

if __name__ == '__main__':
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ APIキーを設定してください")
        print("ファイルを編集: /home/fujinosuke/projects/set_google_maps_key.py")
        print("API_KEY = \"実際のAPIキー\" に変更")
    else:
        set_api_key(API_KEY)