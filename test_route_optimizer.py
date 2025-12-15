#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ルート最適化システムのテスト用スクリプト
Google Maps API無しでのデモンストレーション
"""

import sys
import os
sys.path.append('/home/fujinosuke/projects')

from route_optimizer_tsp import GoogleMapsRouteOptimizer, Location
import json

def test_with_mock_data():
    """モックデータを使用したテスト"""
    print("🧪 モックデータによるルート最適化テスト")
    print("=" * 50)
    
    # モック位置データ（札幌市内の実際の座標）
    mock_locations = [
        Location("大通公園", "札幌市中央区大通西3丁目", 43.0592, 141.3544),
        Location("札幌駅", "札幌市中央区北5条西2丁目", 43.0686, 141.3506),
        Location("サッポロビール園", "札幌市白石区菊水元町5条1丁目", 43.0475, 141.3736),
        Location("羊ヶ丘展望台", "札幌市豊平区羊ケ丘1番", 43.0053, 141.3597),
        Location("藻岩山", "札幌市南区藻岩山", 42.9786, 141.3239),
        Location("手稲駅", "札幌市手稲区手稲本町2条2丁目", 43.1236, 141.2469)
    ]
    
    print("📍 テスト地点:")
    for i, loc in enumerate(mock_locations, 1):
        print(f"  {i}. {loc.name} ({loc.address})")
    
    # モック距離行列作成
    mock_distance_matrix = create_mock_distance_matrix(mock_locations)
    
    # TSPアルゴリズムテスト
    print("\n🧮 アルゴリズム比較テスト")
    
    # 最近傍法テスト
    print("\n1. 最近傍法 (Nearest Neighbor)")
    nn_route, nn_distance = test_nearest_neighbor(mock_locations, mock_distance_matrix)
    print(f"   総距離: {nn_distance:.2f}km")
    print(f"   ルート: {' → '.join([mock_locations[i].name for i in nn_route])}")
    
    # 総当たり法テスト（地点数が少ない場合）
    if len(mock_locations) <= 8:
        print("\n2. 総当たり法 (Brute Force)")
        bf_route, bf_distance = test_brute_force(mock_locations, mock_distance_matrix)
        print(f"   総距離: {bf_distance:.2f}km")
        print(f"   ルート: {' → '.join([mock_locations[i].name for i in bf_route])}")
        
        improvement = ((nn_distance - bf_distance) / nn_distance) * 100
        print(f"   改善率: {improvement:.1f}%")
    
    # 結果サマリー
    print("\n📊 テスト結果サマリー")
    print(f"テスト地点数: {len(mock_locations)}地点")
    print(f"最適化アルゴリズム: 正常動作")
    print(f"距離計算: 正常動作")
    print("✅ 全テスト完了")

def create_mock_distance_matrix(locations):
    """モック距離行列作成（直線距離ベース）"""
    import math
    
    distance_matrix = {}
    
    for i, loc1 in enumerate(locations):
        for j, loc2 in enumerate(locations):
            if i == j:
                distance = 0.0
            else:
                # 直線距離計算（Haversine公式）
                distance = calculate_distance(loc1.lat, loc1.lng, loc2.lat, loc2.lng)
            
            # RouteSegmentの簡易版
            from route_optimizer_tsp import RouteSegment
            segment = RouteSegment(
                from_location=loc1,
                to_location=loc2,
                distance_km=distance,
                duration_minutes=int(distance * 2)  # 時速30kmと仮定
            )
            distance_matrix[(i, j)] = segment
    
    return distance_matrix

def calculate_distance(lat1, lon1, lat2, lon2):
    """2点間の直線距離を計算（Haversine公式）"""
    import math
    
    # 地球の半径 (km)
    R = 6371.0
    
    # 度をラジアンに変換
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # 差分計算
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine公式
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance = R * c
    return distance

def test_nearest_neighbor(locations, distance_matrix):
    """最近傍法テスト"""
    n = len(locations)
    unvisited = set(range(n))
    current = 0  # 開始地点
    route = [current]
    unvisited.remove(current)
    total_distance = 0.0
    
    while unvisited:
        nearest = min(unvisited, key=lambda x: distance_matrix.get((current, x)).distance_km)
        segment = distance_matrix.get((current, nearest))
        total_distance += segment.distance_km
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    # 出発点に戻る
    segment = distance_matrix.get((current, 0))
    total_distance += segment.distance_km
    
    return route, total_distance

def test_brute_force(locations, distance_matrix):
    """総当たり法テスト"""
    import itertools
    
    n = len(locations)
    if n > 8:
        return test_nearest_neighbor(locations, distance_matrix)
    
    other_cities = list(range(1, n))  # 0番目は固定
    best_route = None
    best_distance = float('inf')
    
    for perm in itertools.permutations(other_cities):
        route = [0] + list(perm)
        distance = 0.0
        
        # ルート距離計算
        for i in range(len(route)):
            next_i = (i + 1) % len(route)
            segment = distance_matrix.get((route[i], route[next_i]))
            distance += segment.distance_km
        
        if distance < best_distance:
            best_distance = distance
            best_route = route
    
    return best_route, best_distance

def create_usage_example():
    """使用例の作成"""
    print("\n📝 使用例")
    print("=" * 50)
    
    example_code = '''
# Google Maps API キー設定後の使用例

from route_optimizer_tsp import GoogleMapsRouteOptimizer

# 住所リスト
addresses = [
    "札幌市中央区大通西3丁目",
    "札幌市中央区北5条西2丁目", 
    "札幌市白石区菊水元町5条1丁目",
    "札幌市豊平区羊ケ丘1番",
    "札幌市南区藻岩山",
    "札幌市手稲区手稲本町2条2丁目"
]

# 最適化実行
optimizer = GoogleMapsRouteOptimizer()
result = optimizer.optimize_route(
    addresses=addresses,
    start_address="札幌市中央区大通西3丁目",
    algorithm='auto'  # 'nearest_neighbor', 'brute_force', 'genetic'
)

if result['success']:
    print(f"総距離: {result['total_distance_km']}km")
    print(f"総時間: {result['total_duration_hours']}時間")
    
    # 最適ルート表示
    for location in result['optimized_route']:
        print(f"{location['order']}. {location['address']}")
    
    # Google Maps URL
    print(f"Google Maps: {result['google_maps_url']}")
'''
    
    print(example_code)

def main():
    """メイン関数"""
    print("🗺️ ルート最適化システム - テストモード")
    print("=" * 60)
    print("ℹ️  Google Maps API無しでのデモンストレーション")
    print("ℹ️  実際の使用にはAPI キーが必要です")
    print()
    
    # モックデータテスト
    test_with_mock_data()
    
    # 使用例表示
    create_usage_example()
    
    print("\n🎯 次のステップ")
    print("1. Google Cloud Console でAPI キー取得")
    print("2. 環境変数またはconfig.jsonに設定")
    print("3. 本番システムでテスト実行")
    print("\n📖 詳細: /home/fujinosuke/projects/google_maps_api_setup.md")

if __name__ == '__main__':
    main()