#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps API キー設定スクリプト
取得したAPIキーを安全に保存・設定
"""

import os
import json
import subprocess
from pathlib import Path

def setup_google_maps_api():
    """Google Maps API キーの設定"""
    print("🗺️ Google Maps API 設定ツール")
    print("=" * 50)
    
    # APIキー入力
    print("\n📝 Google Cloud Console で取得したAPIキーを入力してください")
    print("例: AIzaSyBOti4mM-6x9WDnZIjIeyEduZOeGt1234")
    api_key = input("\nAPIキー: ").strip()
    
    if not api_key or len(api_key) < 20:
        print("❌ 有効なAPIキーを入力してください")
        return False
    
    # 設定方法選択
    print("\n📦 設定方法を選択してください:")
    print("1. 環境変数に設定（推奨）")
    print("2. 設定ファイルに保存")
    print("3. 両方に設定")
    
    choice = input("\n選択 (1-3): ").strip()
    
    success = False
    
    # 環境変数設定
    if choice in ['1', '3']:
        bashrc_path = Path.home() / '.bashrc'
        export_line = f'\nexport GOOGLE_MAPS_API_KEY="{api_key}"'
        
        try:
            # .bashrcに追記
            with open(bashrc_path, 'a') as f:
                f.write(export_line)
            
            # 現在のセッションにも設定
            os.environ['GOOGLE_MAPS_API_KEY'] = api_key
            
            print("✅ 環境変数に設定しました")
            print("   次回ログイン時から自動的に有効になります")
            print("   今すぐ有効にする場合: source ~/.bashrc")
            success = True
        except Exception as e:
            print(f"❌ 環境変数設定エラー: {e}")
    
    # 設定ファイル保存
    if choice in ['2', '3']:
        config_path = Path('/home/fujinosuke/google_maps_config.json')
        config_data = {
            'google_maps_api_key': api_key,
            'project_name': 'Route Optimizer',
            'enabled_apis': [
                'Maps JavaScript API',
                'Geocoding API', 
                'Distance Matrix API',
                'Places API'
            ]
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # パーミッション設定（読み取り専用）
            os.chmod(config_path, 0o600)
            
            print(f"✅ 設定ファイルに保存しました: {config_path}")
            success = True
        except Exception as e:
            print(f"❌ 設定ファイル保存エラー: {e}")
    
    return success

def test_api_key():
    """APIキーのテスト"""
    print("\n🧪 APIキーをテストしています...")
    
    # テスト用スクリプト実行
    test_script = '/home/fujinosuke/projects/route_optimizer_tsp.py'
    
    if os.path.exists(test_script):
        try:
            # 環境変数を再読み込みして実行
            result = subprocess.run(
                ['python3', test_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if 'REQUEST_DENIED' in result.stderr:
                print("⚠️  APIキーは設定されましたが、以下を確認してください:")
                print("   1. 請求アカウントが有効か")
                print("   2. 必要なAPIが有効化されているか")
                print("   3. APIキーの制限設定が適切か")
            elif 'ルート最適化' in result.stdout:
                print("✅ APIキーが正常に動作しています!")
            else:
                print("⚠️  テスト結果を確認してください")
                
        except Exception as e:
            print(f"テストエラー: {e}")
    
def show_next_steps():
    """次のステップ表示"""
    print("\n📋 次のステップ:")
    print("1. 環境変数を有効化: source ~/.bashrc")
    print("2. テスト実行:")
    print("   python3 /home/fujinosuke/projects/route_optimizer_tsp.py")
    print("\n3. 本番利用:")
    print("""
from route_optimizer_tsp import GoogleMapsRouteOptimizer

addresses = [
    "札幌市中央区大通西3丁目",
    "札幌市中央区北5条西2丁目",
    # ... 他の住所
]

optimizer = GoogleMapsRouteOptimizer()
result = optimizer.optimize_route(addresses)
print(f"最適ルート距離: {result['total_distance_km']}km")
""")

def main():
    """メイン関数"""
    if setup_google_maps_api():
        test_api_key()
        show_next_steps()
        print("\n✅ 設定完了!")
    else:
        print("\n❌ 設定に失敗しました")
        print("Google Cloud Console でAPIキーを取得してください:")
        print("https://console.cloud.google.com/")

if __name__ == '__main__':
    main()