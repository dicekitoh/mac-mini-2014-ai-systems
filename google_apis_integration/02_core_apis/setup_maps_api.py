#!/usr/bin/env python3
"""
Google Maps API セットアップガイド
APIキー設定とテスト実行スクリプト
"""

import os
import sys
from real_nissan_distance_calculator import RealNissanDistanceCalculator

def check_api_setup():
    """API設定状況の確認"""
    print("🔧 Google Maps API セットアップ確認")
    print("=" * 50)
    
    # 環境変数チェック
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if api_key:
        print(f"✅ GOOGLE_MAPS_API_KEY環境変数: 設定済み (長さ: {len(api_key)}文字)")
        
        # 簡単なテスト
        try:
            import googlemaps
            client = googlemaps.Client(key=api_key)
            
            # 簡単なジオコーディングテスト
            test_result = client.geocode("東京駅")
            if test_result:
                print("✅ APIキー検証: 正常動作")
                return True
            else:
                print("❌ APIキー検証: ジオコーディングが失敗")
                return False
                
        except Exception as e:
            print(f"❌ APIキー検証エラー: {e}")
            return False
    else:
        print("❌ GOOGLE_MAPS_API_KEY環境変数: 未設定")
        print_setup_instructions()
        return False

def print_setup_instructions():
    """セットアップ手順を表示"""
    print("\n📋 Google Maps API セットアップ手順:")
    print("-" * 50)
    print("1. Google Cloud Console にアクセス")
    print("   https://console.cloud.google.com/")
    print()
    print("2. 新規プロジェクト作成または既存プロジェクト選択")
    print()
    print("3. Maps JavaScript API を有効化")
    print("   - APIとサービス > ライブラリ")
    print("   - 'Maps JavaScript API' を検索して有効化")
    print("   - 'Geocoding API' も有効化") 
    print("   - 'Distance Matrix API' も有効化")
    print()
    print("4. APIキー作成")
    print("   - APIとサービス > 認証情報")
    print("   - '認証情報を作成' > 'APIキー'")
    print("   - 作成されたAPIキーをコピー")
    print()
    print("5. 環境変数設定")
    print("   export GOOGLE_MAPS_API_KEY='your_api_key_here'")
    print()
    print("6. 課金設定（重要！）")
    print("   - Google Cloud Console で課金を有効化")
    print("   - Maps API は従量課金制です")
    print("   - 毎月200ドルの無料クレジットあり")
    print()
    print("⚠️ 注意: API制限とコスト管理")
    print("   - Geocoding API: $5/1000リクエスト")
    print("   - Distance Matrix API: $5-10/1000リクエスト")
    print("   - 今回の132店舗計算で約264リクエスト（約$1.3程度）")

def interactive_setup():
    """対話式セットアップ"""
    print("\n🔧 対話式APIキー設定")
    print("-" * 30)
    
    api_key = input("Google Maps APIキーを入力してください: ").strip()
    
    if not api_key:
        print("❌ APIキーが入力されませんでした")
        return False
    
    # 環境変数として設定（現在のセッションのみ）
    os.environ['GOOGLE_MAPS_API_KEY'] = api_key
    
    # テスト実行
    print("🧪 APIキーをテスト中...")
    try:
        import googlemaps
        client = googlemaps.Client(key=api_key)
        
        # 札幌のテスト
        test_result = client.geocode("北海道札幌市白石区北郷2405番地")
        if test_result:
            print("✅ APIキー検証成功!")
            print(f"   テスト住所: {test_result[0]['formatted_address']}")
            
            # .envファイルに保存オプション
            save_choice = input("\n💾 APIキーを.envファイルに保存しますか？ (y/N): ").strip().lower()
            if save_choice in ['y', 'yes']:
                with open('.env', 'w') as f:
                    f.write(f"GOOGLE_MAPS_API_KEY={api_key}\n")
                print("✅ .envファイルに保存しました")
                print("💡 次回実行時は 'source .env' でロードしてください")
            
            return True
        else:
            print("❌ APIキー検証失敗: ジオコーディングできませんでした")
            return False
            
    except Exception as e:
        print(f"❌ APIキー検証エラー: {e}")
        return False

def run_test_calculation():
    """テスト計算実行"""
    print("\n🧪 テスト距離計算実行")
    print("-" * 30)
    
    if not check_api_setup():
        return
    
    csv_file = "/mnt/c/Users/itoh/OneDrive/Documents/nissan_accurate_132_20251125_142950.csv"
    base_address = "北海道札幌市白石区北郷2405番地"
    
    try:
        calculator = RealNissanDistanceCalculator(csv_file, base_address)
        
        # CSVデータ読み込み
        if not calculator.load_csv_data():
            print("❌ CSVファイルの読み込みに失敗しました")
            return
        
        # 最初の5店舗のみでテスト
        print("🧪 最初の5店舗でテスト計算を実行します...")
        test_dealers = calculator.dealers_data[:5]
        
        for i, dealer in enumerate(test_dealers):
            print(f"[{i+1}/5] {dealer['store_name']} をテスト中...")
            
            result = calculator.calculate_distance(
                base_address,
                dealer['address'],
                mode='driving'
            )
            
            if result['status'] == 'success':
                print(f"✅ 成功: {result['distance_km']:.2f}km ({result['duration_text']})")
            else:
                print(f"❌ 失敗: {result['status']}")
        
        print("\n✅ テスト完了! 実際の計算準備が整いました")
        
        # フル計算の選択肢
        full_calc = input("\n🚀 全132店舗の計算を実行しますか？ (y/N): ").strip().lower()
        if full_calc in ['y', 'yes']:
            print("🚀 フル計算を開始します...")
            os.system("python3 real_nissan_distance_calculator.py")
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")

def main():
    """メイン実行"""
    print("🗺️ Google Maps API セットアップ・テストツール")
    print("=" * 60)
    
    # メニュー表示
    while True:
        print("\n📋 メニュー:")
        print("1. API設定状況確認")
        print("2. セットアップ手順表示") 
        print("3. 対話式APIキー設定")
        print("4. テスト計算実行")
        print("5. 終了")
        
        choice = input("\n選択してください (1-5): ").strip()
        
        if choice == '1':
            check_api_setup()
        elif choice == '2':
            print_setup_instructions()
        elif choice == '3':
            interactive_setup()
        elif choice == '4':
            run_test_calculation()
        elif choice == '5':
            print("👋 セットアップツールを終了します")
            break
        else:
            print("❌ 無効な選択です。1-5を入力してください。")

if __name__ == "__main__":
    main()