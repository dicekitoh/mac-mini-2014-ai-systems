#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
巡回セールスマン問題 (TSP) による最短ルート最適化システム
Google Maps API連携による実距離ベース最適化
"""

import requests
import json
import time
import itertools
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import os
from datetime import datetime, timedelta

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Location:
    """位置情報クラス"""
    name: str
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    place_id: Optional[str] = None

@dataclass
class RouteSegment:
    """ルート区間情報"""
    from_location: Location
    to_location: Location
    distance_km: float
    duration_minutes: int
    distance_matrix_data: Optional[Dict] = None

class GoogleMapsRouteOptimizer:
    """Google Maps API連携最短ルート最適化"""
    
    def __init__(self, api_key: str = None):
        """
        初期化
        Args:
            api_key: Google Maps API キー（Noneの場合は環境変数から取得）
        """
        self.api_key = api_key or self._get_api_key()
        self.cache_file = '/tmp/route_cache.pickle'
        self.cache = self._load_cache()
        
        # API制限対策
        self.requests_per_second = 50  # Google Maps API制限
        self.last_request_time = 0
        
    def _get_api_key(self) -> str:
        """Google Maps API キー取得"""
        # 複数のソースからAPI キーを取得
        api_sources = [
            # 環境変数
            lambda: os.getenv('GOOGLE_MAPS_API_KEY'),
            lambda: os.getenv('GOOGLE_API_KEY'),
            
            # 設定ファイル
            lambda: self._read_config_file('/home/fujinosuke/google_maps_config.json'),
            lambda: self._read_config_file('/home/fujinosuke/projects/google_auth/google_api_keys.json'),
            
            # デフォルトキー（テスト用）
            lambda: "***REMOVED***"  # 制限付きテストキー
        ]
        
        for get_key in api_sources:
            try:
                key = get_key()
                if key:
                    logger.info(f"✅ Google Maps API キー取得成功")
                    return key
            except Exception as e:
                logger.debug(f"API キー取得試行エラー: {e}")
        
        raise ValueError("Google Maps API キーが見つかりません")
    
    def _read_config_file(self, filepath: str) -> Optional[str]:
        """設定ファイルからAPIキー読み込み"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    config = json.load(f)
                return config.get('google_maps_api_key') or config.get('api_key')
        except Exception:
            pass
        return None
    
    def _load_cache(self) -> Dict:
        """距離行列キャッシュ読み込み"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            logger.warning(f"キャッシュ読み込みエラー: {e}")
        return {}
    
    def _save_cache(self):
        """距離行列キャッシュ保存"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            logger.warning(f"キャッシュ保存エラー: {e}")
    
    def _rate_limit(self):
        """API レート制限"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def geocode_address(self, address: str) -> Optional[Location]:
        """住所から緯度経度取得"""
        cache_key = f"geocode:{address}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        self._rate_limit()
        
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': self.api_key,
            'language': 'ja',
            'region': 'jp'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                location = Location(
                    name=address,
                    address=result['formatted_address'],
                    lat=result['geometry']['location']['lat'],
                    lng=result['geometry']['location']['lng'],
                    place_id=result.get('place_id')
                )
                
                self.cache[cache_key] = location
                self._save_cache()
                return location
            else:
                logger.error(f"Geocoding失敗: {address} - {data.get('status')}")
                
        except Exception as e:
            logger.error(f"Geocoding エラー: {address} - {e}")
        
        return None
    
    def get_distance_matrix(self, locations: List[Location]) -> Dict[Tuple[int, int], RouteSegment]:
        """距離行列取得"""
        if len(locations) < 2:
            return {}
        
        # キャッシュキー生成
        location_keys = [f"{loc.lat},{loc.lng}" for loc in locations]
        cache_key = f"matrix:{'|'.join(sorted(location_keys))}"
        
        if cache_key in self.cache:
            logger.info("✅ 距離行列キャッシュから取得")
            return self.cache[cache_key]
        
        distance_matrix = {}
        
        # Google Maps Distance Matrix API の制限に対応（最大25地点）
        max_locations_per_request = 25
        
        if len(locations) <= max_locations_per_request:
            distance_matrix = self._get_distance_matrix_batch(locations, locations)
        else:
            # 大量地点の場合は分割処理
            logger.info(f"大量地点({len(locations)}地点)のため分割処理を実行")
            distance_matrix = self._get_distance_matrix_large(locations)
        
        self.cache[cache_key] = distance_matrix
        self._save_cache()
        
        return distance_matrix
    
    def _get_distance_matrix_batch(self, origins: List[Location], destinations: List[Location]) -> Dict[Tuple[int, int], RouteSegment]:
        """バッチ処理で距離行列取得"""
        self._rate_limit()
        
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        
        origin_coords = [f"{loc.lat},{loc.lng}" for loc in origins]
        dest_coords = [f"{loc.lat},{loc.lng}" for loc in destinations]
        
        params = {
            'origins': '|'.join(origin_coords),
            'destinations': '|'.join(dest_coords),
            'key': self.api_key,
            'units': 'metric',
            'mode': 'driving',
            'avoid': 'tolls',  # 有料道路回避（オプション）
            'language': 'ja'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'OK':
                logger.error(f"Distance Matrix API エラー: {data['status']}")
                return {}
            
            distance_matrix = {}
            
            for i, origin in enumerate(origins):
                for j, destination in enumerate(destinations):
                    if i < len(data['rows']) and j < len(data['rows'][i]['elements']):
                        element = data['rows'][i]['elements'][j]
                        
                        if element['status'] == 'OK':
                            distance_km = element['distance']['value'] / 1000.0
                            duration_minutes = element['duration']['value'] / 60.0
                            
                            segment = RouteSegment(
                                from_location=origin,
                                to_location=destination,
                                distance_km=distance_km,
                                duration_minutes=int(duration_minutes),
                                distance_matrix_data=element
                            )
                            
                            distance_matrix[(i, j)] = segment
            
            logger.info(f"✅ 距離行列取得完了: {len(distance_matrix)}区間")
            return distance_matrix
            
        except Exception as e:
            logger.error(f"Distance Matrix API エラー: {e}")
            return {}
    
    def _get_distance_matrix_large(self, locations: List[Location]) -> Dict[Tuple[int, int], RouteSegment]:
        """大量地点対応距離行列取得"""
        # 実装簡略化のため、現在は分割処理をスキップ
        # 実際の運用では、25地点ずつに分割してAPI呼び出し
        logger.warning("⚠️ 大量地点処理は簡略化実装です")
        return self._get_distance_matrix_batch(locations, locations)
    
    def solve_tsp_nearest_neighbor(self, locations: List[Location], start_index: int = 0) -> Tuple[List[int], float]:
        """最近傍法によるTSP解法（高速、近似解）"""
        distance_matrix = self.get_distance_matrix(locations)
        
        if not distance_matrix:
            return list(range(len(locations))), 0.0
        
        n = len(locations)
        unvisited = set(range(n))
        current = start_index
        route = [current]
        unvisited.remove(current)
        total_distance = 0.0
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix.get((current, x), RouteSegment(None, None, float('inf'), 0)).distance_km)
            
            segment = distance_matrix.get((current, nearest))
            if segment:
                total_distance += segment.distance_km
            
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # 開始点に戻る
        if distance_matrix.get((current, start_index)):
            total_distance += distance_matrix[(current, start_index)].distance_km
        
        return route, total_distance
    
    def solve_tsp_brute_force(self, locations: List[Location], start_index: int = 0) -> Tuple[List[int], float]:
        """総当たり法によるTSP解法（最適解、小規模のみ）"""
        if len(locations) > 10:
            logger.warning("⚠️ 地点数が多すぎます。最近傍法を使用します。")
            return self.solve_tsp_nearest_neighbor(locations, start_index)
        
        distance_matrix = self.get_distance_matrix(locations)
        
        if not distance_matrix:
            return list(range(len(locations))), 0.0
        
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
    
    def solve_tsp_genetic_algorithm(self, locations: List[Location], start_index: int = 0, 
                                  population_size: int = 100, generations: int = 500) -> Tuple[List[int], float]:
        """遺伝的アルゴリズムによるTSP解法（中規模対応）"""
        distance_matrix = self.get_distance_matrix(locations)
        
        if not distance_matrix:
            return list(range(len(locations))), 0.0
        
        n = len(locations)
        if n <= 10:
            return self.solve_tsp_brute_force(locations, start_index)
        
        # 簡易遺伝的アルゴリズム実装
        def create_individual():
            cities = [i for i in range(n) if i != start_index]
            np.random.shuffle(cities)
            return [start_index] + cities
        
        def fitness(individual):
            return 1 / (1 + self._calculate_route_distance(individual, distance_matrix))
        
        def crossover(parent1, parent2):
            # 部分写像交叉 (PMX) の簡易版
            size = len(parent1)
            start, end = sorted(np.random.choice(size, 2, replace=False))
            child = [-1] * size
            child[start:end] = parent1[start:end]
            
            for i in range(size):
                if child[i] == -1:
                    for gene in parent2:
                        if gene not in child:
                            child[i] = gene
                            break
            return child
        
        def mutate(individual, mutation_rate=0.01):
            if np.random.random() < mutation_rate:
                i, j = np.random.choice(len(individual), 2, replace=False)
                individual[i], individual[j] = individual[j], individual[i]
            return individual
        
        # 初期個体群生成
        population = [create_individual() for _ in range(population_size)]
        
        for generation in range(generations):
            # 適応度計算
            fitness_scores = [fitness(ind) for ind in population]
            
            # 選択・交叉・突然変異
            new_population = []
            for _ in range(population_size):
                # トーナメント選択
                parent1 = population[np.argmax(np.random.choice(fitness_scores, 3))]
                parent2 = population[np.argmax(np.random.choice(fitness_scores, 3))]
                
                child = crossover(parent1, parent2)
                child = mutate(child)
                new_population.append(child)
            
            population = new_population
        
        # 最良個体選択
        fitness_scores = [fitness(ind) for ind in population]
        best_individual = population[np.argmax(fitness_scores)]
        best_distance = self._calculate_route_distance(best_individual, distance_matrix)
        
        return best_individual, best_distance
    
    def _calculate_route_distance(self, route: List[int], distance_matrix: Dict[Tuple[int, int], RouteSegment]) -> float:
        """ルート総距離計算"""
        total_distance = 0.0
        
        for i in range(len(route)):
            next_i = (i + 1) % len(route)
            segment = distance_matrix.get((route[i], route[next_i]))
            if segment:
                total_distance += segment.distance_km
            else:
                return float('inf')  # 無効なルート
        
        return total_distance
    
    def optimize_route(self, addresses: List[str], start_address: str = None, 
                      algorithm: str = 'auto') -> Dict:
        """
        ルート最適化メイン関数
        
        Args:
            addresses: 訪問先住所リスト
            start_address: 開始地点住所（Noneの場合は最初の住所）
            algorithm: 'auto', 'nearest_neighbor', 'brute_force', 'genetic'
        
        Returns:
            最適化結果辞書
        """
        logger.info(f"🚀 ルート最適化開始: {len(addresses)}地点")
        
        # ジオコーディング（並列処理）
        locations = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.geocode_address, addr): addr for addr in addresses}
            
            for future in as_completed(futures):
                addr = futures[future]
                try:
                    location = future.result()
                    if location:
                        locations.append(location)
                    else:
                        logger.error(f"❌ ジオコーディング失敗: {addr}")
                except Exception as e:
                    logger.error(f"❌ ジオコーディング エラー: {addr} - {e}")
        
        if len(locations) < 2:
            return {"error": "有効な住所が2地点未満です"}
        
        logger.info(f"✅ ジオコーディング完了: {len(locations)}地点")
        
        # 開始地点決定
        start_index = 0
        if start_address:
            for i, loc in enumerate(locations):
                if start_address in loc.address or start_address in loc.name:
                    start_index = i
                    break
        
        # アルゴリズム選択
        if algorithm == 'auto':
            if len(locations) <= 8:
                algorithm = 'brute_force'
            elif len(locations) <= 20:
                algorithm = 'genetic'
            else:
                algorithm = 'nearest_neighbor'
        
        logger.info(f"🧮 アルゴリズム: {algorithm}")
        
        # TSP解法実行
        start_time = time.time()
        
        if algorithm == 'brute_force':
            optimal_route, total_distance = self.solve_tsp_brute_force(locations, start_index)
        elif algorithm == 'genetic':
            optimal_route, total_distance = self.solve_tsp_genetic_algorithm(locations, start_index)
        else:  # nearest_neighbor
            optimal_route, total_distance = self.solve_tsp_nearest_neighbor(locations, start_index)
        
        optimization_time = time.time() - start_time
        
        # 結果生成
        optimized_locations = [locations[i] for i in optimal_route]
        
        # 詳細ルート情報生成
        distance_matrix = self.get_distance_matrix(locations)
        route_segments = []
        total_duration = 0
        
        for i in range(len(optimal_route)):
            next_i = (i + 1) % len(optimal_route)
            segment = distance_matrix.get((optimal_route[i], optimal_route[next_i]))
            if segment:
                route_segments.append({
                    'from': segment.from_location.address,
                    'to': segment.to_location.address,
                    'distance_km': round(segment.distance_km, 2),
                    'duration_minutes': segment.duration_minutes
                })
                total_duration += segment.duration_minutes
        
        result = {
            'success': True,
            'algorithm': algorithm,
            'optimization_time_seconds': round(optimization_time, 2),
            'total_locations': len(locations),
            'total_distance_km': round(total_distance, 2),
            'total_duration_minutes': total_duration,
            'total_duration_hours': round(total_duration / 60, 1),
            'optimized_route': [
                {
                    'order': i + 1,
                    'name': loc.name,
                    'address': loc.address,
                    'lat': loc.lat,
                    'lng': loc.lng
                } for i, loc in enumerate(optimized_locations)
            ],
            'route_segments': route_segments,
            'google_maps_url': self._generate_google_maps_url(optimized_locations)
        }
        
        logger.info(f"✅ 最適化完了: {total_distance:.2f}km, {total_duration}分")
        
        return result
    
    def _generate_google_maps_url(self, locations: List[Location]) -> str:
        """Google Maps URL生成"""
        if len(locations) < 2:
            return ""
        
        base_url = "https://www.google.com/maps/dir/"
        waypoints = []
        
        for loc in locations:
            if loc.lat and loc.lng:
                waypoints.append(f"{loc.lat},{loc.lng}")
            else:
                waypoints.append(loc.address.replace(' ', '+'))
        
        return base_url + '/'.join(waypoints)

def main():
    """メイン実行関数"""
    print("🗺️ Google Maps API連携 最短ルート最適化システム")
    print("=" * 60)
    
    # サンプル住所（札幌市内）
    sample_addresses = [
        "札幌市中央区大通西3丁目",  # 大通公園
        "札幌市中央区北5条西2丁目",  # 札幌駅
        "札幌市白石区菊水元町5条1丁目",  # サッポロビール園
        "札幌市豊平区羊ケ丘1番",  # 羊ヶ丘展望台
        "札幌市南区藻岩山",  # 藻岩山
        "札幌市手稲区手稲本町2条2丁目"  # 手稲駅
    ]
    
    try:
        optimizer = GoogleMapsRouteOptimizer()
        
        print("📍 訪問地点:")
        for i, addr in enumerate(sample_addresses, 1):
            print(f"  {i}. {addr}")
        
        print("\n🚀 最適化実行中...")
        result = optimizer.optimize_route(
            addresses=sample_addresses,
            start_address="札幌市中央区大通西3丁目",
            algorithm='auto'
        )
        
        if result.get('success'):
            print(f"\n✅ 最適化完了!")
            print(f"アルゴリズム: {result['algorithm']}")
            print(f"総距離: {result['total_distance_km']}km")
            print(f"総時間: {result['total_duration_hours']}時間")
            print(f"計算時間: {result['optimization_time_seconds']}秒")
            
            print("\n📍 最適ルート:")
            for location in result['optimized_route']:
                print(f"  {location['order']}. {location['address']}")
            
            print(f"\n🗺️ Google Maps: {result['google_maps_url']}")
            
            # 詳細ルート情報
            print("\n🛣️ ルート詳細:")
            for segment in result['route_segments']:
                print(f"  {segment['from']} → {segment['to']}")
                print(f"    距離: {segment['distance_km']}km, 時間: {segment['duration_minutes']}分")
        
        else:
            print(f"❌ エラー: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ システムエラー: {e}")
        logger.error(f"システムエラー: {e}", exc_info=True)

if __name__ == '__main__':
    main()