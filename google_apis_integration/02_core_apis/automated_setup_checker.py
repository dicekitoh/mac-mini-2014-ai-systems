#!/usr/bin/env python3
"""
自動セットアップ確認ツール
APIキー設定状況の自動チェックと準備完了確認
"""

import os
import sys
import json
from datetime import datetime

def print_setup_urls():
    """セットアップ用URLを表示"""
    print("🔗 Google Cloud Console セットアップURL")
    print("=" * 60)
    
    urls = {
        "1. Google Cloud Console": "https://console.cloud.google.com/",
        "2. 新規プロジェクト作成": "https://console.cloud.google.com/projectcreate",
        "3. 課金設定": "https://console.cloud.google.com/billing",
        "4. Geocoding API": "https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com",
        "5. Distance Matrix API": "https://console.cloud.google.com/apis/library/distance-matrix-backend.googleapis.com", 
        "6. Maps JavaScript API": "https://console.cloud.google.com/apis/library/maps-backend.googleapis.com",
        "7. APIキー作成": "https://console.cloud.google.com/apis/credentials",
        "8. 使用量監視": "https://console.cloud.google.com/apis/quotas"
    }
    
    for step, url in urls.items():
        print(f"{step}")
        print(f"   {url}")
        print()
    
    print("💡 手順:")
    print("1. 上記URLを順番に開いて設定完了")
    print("2. APIキーを取得")  
    print("3. 下記コマンドでAPIキーを設定")
    print("   export GOOGLE_MAPS_API_KEY='your_api_key_here'")
    print("4. このスクリプトを再実行して確認")

def check_environment():
    """環境設定チェック"""
    print("🔧 環境設定チェック")
    print("-" * 30)
    
    checks = []
    
    # APIキー確認
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if api_key:
        checks.append(f"✅ GOOGLE_MAPS_API_KEY: 設定済み ({len(api_key)}文字)")
        
        # 簡単な形式チェック
        if api_key.startswith('AIza') and len(api_key) == 39:
            checks.append("✅ APIキー形式: 正常（Google標準形式）")
        else:
            checks.append(f"⚠️ APIキー形式: 非標準（長さ:{len(api_key)}）")
    else:
        checks.append("❌ GOOGLE_MAPS_API_KEY: 未設定")
    
    # Python環境確認
    try:
        import googlemaps
        checks.append("✅ googlemaps ライブラリ: インストール済み")
    except ImportError:
        checks.append("❌ googlemaps ライブラリ: 未インストール")
    
    # pandas確認
    try:
        import pandas
        checks.append("✅ pandas ライブラリ: インストール済み")
    except ImportError:
        checks.append("❌ pandas ライブラリ: 未インストール")
    
    # CSVファイル確認
    csv_file = "/mnt/c/Users/itoh/OneDrive/Documents/nissan_accurate_132_20251125_142950.csv"
    if os.path.exists(csv_file):
        checks.append("✅ 日産CSVファイル: 存在確認済み")
    else:
        checks.append("❌ 日産CSVファイル: ファイルが見つかりません")
    
    for check in checks:
        print(check)
    
    return len([c for c in checks if c.startswith('✅')]), len(checks)

def test_api_connection():
    """API接続テスト"""
    print("\n🧪 API接続テスト")
    print("-" * 30)
    
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("❌ APIキーが設定されていません")
        return False
    
    try:
        import googlemaps
        client = googlemaps.Client(key=api_key)
        
        # Geocoding テスト
        print("📍 Geocodingテスト: 札幌駅")
        result = client.geocode("札幌駅")
        if result:
            location = result[0]['geometry']['location']
            print(f"✅ 成功: {result[0]['formatted_address']}")
            print(f"   座標: ({location['lat']:.6f}, {location['lng']:.6f})")
            
            # Distance Matrix テスト
            print("\n🚗 Distance Matrix テスト: 札幌駅 → 新千歳空港")
            matrix = client.distance_matrix(
                origins=["札幌駅"],
                destinations=["新千歳空港"],
                mode='driving',
                units='metric'
            )
            
            if matrix['status'] == 'OK':
                element = matrix['rows'][0]['elements'][0]
                if element['status'] == 'OK':
                    print(f"✅ 成功: {element['distance']['text']}, {element['duration']['text']}")
                    return True
                else:
                    print(f"❌ Distance Matrix エラー: {element['status']}")
            else:
                print(f"❌ Distance Matrix エラー: {matrix['status']}")
        else:
            print("❌ Geocoding結果なし")
    
    except Exception as e:
        print(f"❌ APIテストエラー: {e}")
    
    return False

def generate_ready_script():
    """準備完了スクリプト生成"""
    script_content = f"""#!/bin/bash
# Google Maps API 準備完了確認スクリプト
# 生成日時: {datetime.now().isoformat()}

echo "🚀 日産ディーラー距離計算システム 実行準備"
echo "=" * 50

# 環境確認
if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
    echo "❌ GOOGLE_MAPS_API_KEY環境変数が未設定です"
    echo "💡 以下のコマンドで設定してください:"
    echo "   export GOOGLE_MAPS_API_KEY='your_api_key_here'"
    exit 1
fi

echo "✅ GOOGLE_MAPS_API_KEY: 設定済み"

# 仮想環境確認
if [ -d "venv" ]; then
    echo "✅ Python仮想環境: 存在確認"
    source venv/bin/activate
else
    echo "⚠️ Python仮想環境が見つかりません"
fi

# 依存ライブラリ確認
python3 -c "import googlemaps, pandas; print('✅ 必要ライブラリ: 全て利用可能')" 2>/dev/null || {{
    echo "❌ 必要ライブラリが不足しています"
    echo "💡 以下のコマンドでインストール:"
    echo "   pip install googlemaps pandas"
    exit 1
}}

# 実行
echo ""
echo "🎯 準備完了！実際の距離計算を開始します..."
echo ""
python3 real_nissan_distance_calculator.py
"""
    
    with open('run_distance_calculation.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('run_distance_calculation.sh', 0o755)
    print("\n📄 実行スクリプト生成: run_distance_calculation.sh")

def main():
    """メイン実行"""
    print("🗺️ Google Maps API 自動セットアップ確認ツール")
    print("=" * 60)
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 環境チェック
    passed, total = check_environment()
    
    # 結果サマリー
    print(f"\n📊 チェック結果: {passed}/{total} 項目完了")
    
    if passed == total:
        print("\n🎉 全ての環境設定が完了しています！")
        
        # API接続テスト
        if test_api_connection():
            print("\n✅ API接続テストも成功しました")
            print("🚀 準備完了：実際の距離計算システムを実行できます")
            
            generate_ready_script()
            
            print("\n💡 次の手順:")
            print("1. ./run_distance_calculation.sh を実行")
            print("   または")
            print("2. python3 real_nissan_distance_calculator.py を直接実行")
        else:
            print("\n⚠️ API接続に問題があります")
            print("💡 Google Cloud Console でAPIキーと課金設定を確認してください")
    else:
        print(f"\n⚠️ {total - passed} 項目の設定が必要です")
        
        # 不足項目の場合、セットアップURLを表示
        print()
        print_setup_urls()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()