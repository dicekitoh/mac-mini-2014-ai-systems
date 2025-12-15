#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10地点テスト - Google Maps API ルート最適化
実際の営業訪問を想定したテストケース
"""

import os
import sys
sys.path.append('/home/fujinosuke/projects')

from route_optimizer_tsp import GoogleMapsRouteOptimizer
import time

def test_10_locations():
    """10地点の訪問先最適化テスト"""
    print("🚗 10地点訪問ルート最適化テスト")
    print("=" * 70)
    print("📋 シナリオ: 札幌市内の主要施設・企業を巡回訪問")
    print()
    
    # 実際の訪問先を想定した10地点
    test_addresses = [
        # 1. スタート地点（オフィス）
        "札幌市中央区大通西3丁目 札幌大通ビル",
        
        # 2-3. 官公庁エリア
        "札幌市役所",
        "北海道庁",
        
        # 4-5. 商業施設
        "イオンモール札幌平岡",
        "札幌ステラプレイス",
        
        # 6-7. 医療・教育機関
        "北海道大学病院",
        "札幌医科大学",
        
        # 8-9. 観光・文化施設
        "札幌ドーム",
        "北海道立近代美術館",
        
        # 10. 郊外の施設
        "新千歳空港"
    ]
    
    print("📍 訪問先リスト:")
    for i, addr in enumerate(test_addresses, 1):
        print(f"  {i:2d}. {addr}")
    
    # 最適化実行
    optimizer = GoogleMapsRouteOptimizer()
    
    print("\n🚀 ルート最適化実行中...")
    start_time = time.time()
    
    result = optimizer.optimize_route(
        addresses=test_addresses,
        start_address="札幌市中央区大通西3丁目",  # オフィスから出発
        algorithm='auto'  # 10地点なので遺伝的アルゴリズムが選択される
    )
    
    execution_time = time.time() - start_time
    
    if result.get('success'):
        print(f"\n✅ 最適化完了! (実行時間: {execution_time:.1f}秒)")
        print("\n" + "=" * 70)
        print("📊 最適化結果サマリー")
        print("=" * 70)
        print(f"使用アルゴリズム: {result['algorithm']}")
        print(f"総走行距離: {result['total_distance_km']} km")
        print(f"総所要時間: {result['total_duration_hours']} 時間 ({result['total_duration_minutes']}分)")
        print(f"訪問地点数: {result['total_locations']} 地点")
        
        # 時間別内訳
        driving_time = result['total_duration_minutes']
        visit_time_per_location = 30  # 各地点30分滞在と仮定
        total_visit_time = visit_time_per_location * (len(test_addresses) - 1)  # 最初の地点除く
        total_time = driving_time + total_visit_time
        
        print(f"\n⏱️ 時間内訳:")
        print(f"  移動時間: {driving_time}分 ({round(driving_time/60, 1)}時間)")
        print(f"  訪問時間: {total_visit_time}分 (30分 × {len(test_addresses)-1}箇所)")
        print(f"  合計時間: {total_time}分 ({round(total_time/60, 1)}時間)")
        
        # 最適ルート表示
        print("\n📍 最適訪問順序:")
        print("-" * 70)
        for i, location in enumerate(result['optimized_route']):
            address_short = location['address'].split('、')[1] if '、' in location['address'] else location['address']
            print(f"{location['order']:2d}. {location['name']}")
            print(f"    住所: {address_short}")
            if i < len(result['optimized_route']) - 1:
                print(f"    ↓")
        
        # 詳細ルート情報
        print("\n🛣️ 区間別詳細:")
        print("-" * 70)
        total_distance = 0
        total_time = 0
        for i, segment in enumerate(result['route_segments'], 1):
            print(f"区間{i:2d}: {segment['from']}")
            print(f"      → {segment['to']}")
            print(f"      距離: {segment['distance_km']}km / 時間: {segment['duration_minutes']}分")
            total_distance += segment['distance_km']
            total_time += segment['duration_minutes']
            if i < len(result['route_segments']):
                print()
        
        # 効率性分析
        print("\n📈 効率性分析:")
        print("-" * 70)
        avg_speed = result['total_distance_km'] / (result['total_duration_minutes'] / 60)
        print(f"平均移動速度: {avg_speed:.1f} km/h")
        print(f"1地点あたり平均移動時間: {result['total_duration_minutes'] / len(test_addresses):.1f}分")
        print(f"1kmあたり平均所要時間: {result['total_duration_minutes'] / result['total_distance_km']:.1f}分")
        
        # Google Maps URL
        print(f"\n🗺️ Google Maps で確認:")
        print(result['google_maps_url'][:100] + "...")
        
        # 実用性評価
        print("\n💡 実用性評価:")
        print("-" * 70)
        if total_time <= 480:  # 8時間以内
            print("✅ 1日で訪問可能（8時間以内）")
        else:
            days_needed = (total_time - 1) // 480 + 1
            print(f"⚠️  {days_needed}日に分けて訪問することを推奨")
            print(f"   または、訪問時間を短縮する必要があります")
        
        # コスト試算
        fuel_consumption = 10  # 10km/L と仮定
        fuel_price = 170  # 170円/L と仮定
        fuel_cost = (result['total_distance_km'] / fuel_consumption) * fuel_price
        print(f"\n💰 概算燃料費: {int(fuel_cost):,}円")
        print(f"   (燃費10km/L、ガソリン170円/Lで計算)")
        
    else:
        print(f"\n❌ エラー: {result.get('error')}")

if __name__ == '__main__':
    test_10_locations()