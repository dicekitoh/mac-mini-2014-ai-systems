#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプル版 ルート最適化システム
座標を直接入力してTSPアルゴリズムで最適化
"""

import itertools
import math
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class Location:
    """位置情報クラス"""
    name: str
    lat: float
    lng: float

class SimpleRouteOptimizer:
    """シンプルなルート最適化システム"""
    
    def __init__(self):
        pass
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """2点間の直線距離を計算（Haversine公式）"""
        R = 6371.0  # 地球の半径 (km)
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def create_distance_matrix(self, locations: List[Location]) -> List[List[float]]:
        """距離行列作成"""
        n = len(locations)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    distance = self.calculate_distance(
                        locations[i].lat, locations[i].lng,
                        locations[j].lat, locations[j].lng
                    )
                    matrix[i][j] = distance
        
        return matrix
    
    def solve_tsp_nearest_neighbor(self, locations: List[Location], start_index: int = 0) -> Tuple[List[int], float]:
        """最近傍法によるTSP解法"""
        distance_matrix = self.create_distance_matrix(locations)
        
        n = len(locations)
        unvisited = set(range(n))
        current = start_index
        route = [current]
        unvisited.remove(current)
        total_distance = 0.0
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            total_distance += distance_matrix[current][nearest]
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # 開始点に戻る
        total_distance += distance_matrix[current][start_index]
        
        return route, total_distance
    
    def solve_tsp_brute_force(self, locations: List[Location], start_index: int = 0) -> Tuple[List[int], float]:
        """総当たり法によるTSP解法（小規模のみ）"""
        if len(locations) > 10:
            print("⚠️ 地点数が多すぎます。最近傍法を使用します。")
            return self.solve_tsp_nearest_neighbor(locations, start_index)
        
        distance_matrix = self.create_distance_matrix(locations)
        
        n = len(locations)
        other_cities = [i for i in range(n) if i != start_index]
        
        best_route = None
        best_distance = float('inf')
        
        for perm in itertools.permutations(other_cities):
            route = [start_index] + list(perm)
            distance = self._calculate_route_distance(route, distance_matrix)
            
            if distance < best_distance:
                best_distance = distance
                best_route = route
        
        return best_route or [start_index], best_distance
    
    def _calculate_route_distance(self, route: List[int], distance_matrix: List[List[float]]) -> float:
        """ルート総距離計算"""
        total_distance = 0.0
        
        for i in range(len(route)):
            next_i = (i + 1) % len(route)
            total_distance += distance_matrix[route[i]][route[next_i]]
        
        return total_distance
    
    def optimize_route(self, locations: List[Location], start_location_name: str = None, algorithm: str = 'auto') -> dict:
        """
        ルート最適化メイン関数
        
        Args:
            locations: 位置情報リスト
            start_location_name: 開始地点名
            algorithm: 'auto', 'nearest_neighbor', 'brute_force'
        
        Returns:
            最適化結果辞書
        """
        if len(locations) < 2:
            return {"error": "地点数が2未満です"}
        
        # 開始地点決定
        start_index = 0
        if start_location_name:
            for i, loc in enumerate(locations):
                if start_location_name in loc.name:
                    start_index = i
                    break
        
        # アルゴリズム選択
        if algorithm == 'auto':
            algorithm = 'brute_force' if len(locations) <= 8 else 'nearest_neighbor'
        
        # TSP解法実行
        if algorithm == 'brute_force':
            optimal_route, total_distance = self.solve_tsp_brute_force(locations, start_index)
        else:  # nearest_neighbor
            optimal_route, total_distance = self.solve_tsp_nearest_neighbor(locations, start_index)
        
        # 結果生成
        optimized_locations = [locations[i] for i in optimal_route]
        
        # ルート詳細生成
        distance_matrix = self.create_distance_matrix(locations)
        route_segments = []
        
        for i in range(len(optimal_route)):
            next_i = (i + 1) % len(optimal_route)
            from_loc = locations[optimal_route[i]]
            to_loc = locations[optimal_route[next_i]]
            distance = distance_matrix[optimal_route[i]][optimal_route[next_i]]
            
            route_segments.append({
                'from': from_loc.name,
                'to': to_loc.name,
                'distance_km': round(distance, 2),
                'duration_minutes': int(distance * 2.5)  # 時速24kmと仮定
            })
        
        result = {
            'success': True,
            'algorithm': algorithm,
            'total_locations': len(locations),
            'total_distance_km': round(total_distance, 2),
            'total_duration_minutes': sum(seg['duration_minutes'] for seg in route_segments),
            'optimized_route': [
                {
                    'order': i + 1,
                    'name': loc.name,
                    'lat': loc.lat,
                    'lng': loc.lng
                } for i, loc in enumerate(optimized_locations)
            ],
            'route_segments': route_segments,
            'google_maps_url': self._generate_google_maps_url(optimized_locations)
        }
        
        return result
    
    def _generate_google_maps_url(self, locations: List[Location]) -> str:
        """Google Maps URL生成"""
        if len(locations) < 2:
            return ""
        
        waypoints = []
        for loc in locations:
            waypoints.append(f"{loc.lat},{loc.lng}")
        
        base_url = "https://www.google.com/maps/dir/"
        return base_url + '/'.join(waypoints)

def main():
    """メイン実行関数"""
    print("🗺️ シンプル版 最短ルート最適化システム")
    print("📍 座標直接入力でのルート最適化")
    print("=" * 60)
    
    # 札幌市内の実際の座標データ
    test_locations = [
        Location("大通公園", 43.0592, 141.3544),
        Location("札幌駅", 43.0686, 141.3506),
        Location("サッポロビール園", 43.0475, 141.3736),
        Location("羊ヶ丘展望台", 43.0053, 141.3597),
        Location("手稲駅", 43.1236, 141.2469),
        Location("新千歳空港", 42.7747, 141.6920)
    ]
    
    print("📍 テスト地点:")
    for i, loc in enumerate(test_locations, 1):
        print(f"  {i}. {loc.name} ({loc.lat}, {loc.lng})")
    
    optimizer = SimpleRouteOptimizer()
    
    print("\n🧮 アルゴリズム比較")
    
    # 最近傍法
    print("\n1. 最近傍法 (Nearest Neighbor)")
    result_nn = optimizer.optimize_route(
        locations=test_locations,
        start_location_name="大通公園",
        algorithm='nearest_neighbor'
    )
    
    if result_nn['success']:
        print(f"   総距離: {result_nn['total_distance_km']}km")
        print(f"   総時間: {round(result_nn['total_duration_minutes']/60, 1)}時間")
        route_names = [loc['name'] for loc in result_nn['optimized_route']]
        print(f"   ルート: {' → '.join(route_names)}")
    
    # 総当たり法
    print("\n2. 総当たり法 (Brute Force)")
    result_bf = optimizer.optimize_route(
        locations=test_locations,
        start_location_name="大通公園",
        algorithm='brute_force'
    )
    
    if result_bf['success']:
        print(f"   総距離: {result_bf['total_distance_km']}km")
        print(f"   総時間: {round(result_bf['total_duration_minutes']/60, 1)}時間")
        route_names = [loc['name'] for loc in result_bf['optimized_route']]
        print(f"   ルート: {' → '.join(route_names)}")
        
        # 改善率計算
        if result_nn['total_distance_km'] > 0:
            improvement = ((result_nn['total_distance_km'] - result_bf['total_distance_km']) / result_nn['total_distance_km']) * 100
            print(f"   改善率: {improvement:.1f}%")
    
    # 詳細ルート表示
    print("\n🛣️ 最適ルート詳細 (総当たり法):")
    for segment in result_bf['route_segments']:
        print(f"  {segment['from']} → {segment['to']}")
        print(f"    距離: {segment['distance_km']}km, 時間: {segment['duration_minutes']}分")
    
    print(f"\n🗺️ Google Maps URL:")
    print(result_bf['google_maps_url'])
    
    print("\n✅ テスト完了")
    print("\n🎯 使用方法:")
    print("from route_optimizer_simple import SimpleRouteOptimizer, Location")
    print("locations = [Location('名前', 緯度, 経度), ...]")
    print("optimizer = SimpleRouteOptimizer()")
    print("result = optimizer.optimize_route(locations)")

if __name__ == '__main__':
    main()