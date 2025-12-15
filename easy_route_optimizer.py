#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡単ルート最適化ツール
住所を入力するだけで最適ルートを計算
"""

import sys
sys.path.append('/home/fujinosuke/projects')
from route_optimizer_tsp import GoogleMapsRouteOptimizer

def optimize_my_route(addresses, start_address=None, save_result=False):
    """
    シンプルなルート最適化関数
    
    Args:
        addresses: 住所のリスト
        start_address: 開始地点（省略時は最初の住所）
        save_result: 結果をファイルに保存するか
    
    Returns:
        最適化結果
    """
    print("🗺️ ルート最適化実行中...")
    
    optimizer = GoogleMapsRouteOptimizer()
    result = optimizer.optimize_route(
        addresses=addresses,
        start_address=start_address,
        algorithm='auto'
    )
    
    if result.get('success'):
        print("\n✅ 最適化完了!")
        print(f"総距離: {result['total_distance_km']}km")
        print(f"総時間: {result['total_duration_hours']}時間")
        
        print("\n📍 最適ルート:")
        for loc in result['optimized_route']:
            print(f"{loc['order']}. {loc['name']}")
        
        print(f"\n🗺️ Google Maps URL:")
        print(result['google_maps_url'])
        
        if save_result:
            import json
            from datetime import datetime
            filename = f"route_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n💾 結果を保存しました: {filename}")
        
        return result
    else:
        print(f"❌ エラー: {result.get('error')}")
        return None

# 使用例
if __name__ == '__main__':
    # サンプル1: 観光ルート
    print("=== 観光ルート最適化サンプル ===")
    tourist_spots = [
        "札幌時計台",
        "札幌テレビ塔", 
        "北海道神宮",
        "白い恋人パーク",
        "札幌ビール博物館"
    ]
    optimize_my_route(tourist_spots)
    
    print("\n" + "="*50 + "\n")
    
    # サンプル2: ビジネス訪問
    print("=== ビジネス訪問ルート最適化サンプル ===")
    business_visits = [
        "札幌駅北口",  # オフィス
        "札幌市役所",
        "北海道経済センター",
        "札幌商工会議所",
        "JRタワー"
    ]
    optimize_my_route(business_visits, start_address="札幌駅北口", save_result=True)