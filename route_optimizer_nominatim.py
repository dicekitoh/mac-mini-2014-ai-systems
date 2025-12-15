#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
無料API版 ルート最適化システム
OpenStreetMap Nominatim API使用
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

class OpenStreetMapRouteOptimizer:
    """OpenStreetMap Nominatim API使用のルート最適化システム"""
    
    def __init__(self):
        """初期化"""
        self.nominatim_base_url = "https://nominatim.openstreetmap.org/search"
        self.osrm_base_url = "http://router.project-osrm.org/table/v1/driving"
        self.cache_file = '/tmp/nominatim_cache.pickle'
        self.cache = self._load_cache()
        
        # レート制限対策
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Nominatim: 1秒間隔
        
        # User-Agentの設定（Nominatim要求）
        self.headers = {
            'User-Agent': 'RouteOptimizer/1.0 (Sapporo, Hokkaido; route-optimizer@example.com)',
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8'
        }
        
    def _load_cache(self) -> Dict:
        """キャッシュ読み込み"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            logger.warning(f"キャッシュ読み込みエラー: {e}")
        return {}
    
    def _save_cache(self):
        """キャッシュ保存"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            logger.warning(f"キャッシュ保存エラー: {e}")
    
    def _rate_limit(self):
        """レート制限"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _convert_address_for_search(self, address: str) -> str:
        """日本語住所を検索用に変換"""
        # 簡易変換マップ
        conversion_map = {
            '札幌市': 'Sapporo',
            '中央区': 'Chuo-ku',
            '手稲区': 'Teine-ku',
            '白石区': 'Shiroishi-ku',
            '豊平区': 'Toyohira-ku',
            '南区': 'Minami-ku',
            '北区': 'Kita-ku',
            '大通': 'Odori',
            '手稲本町': 'Teinehoncho',
            '菊水元町': 'Kikusui-motomachi',
            '羊ケ丘': 'Hitsujigaoka',
            '藻岩山': 'Moiwayama',
            '条': '-jo',
            '丁目': '-chome',
            '番': '-ban'
        }
        
        converted = address
        for jp, en in conversion_map.items():
            converted = converted.replace(jp, en)
        
        # 数字は保持
        return converted
    
    def geocode_address(self, address: str) -> Optional[Location]:
        """住所をジオコーディング（Nominatim使用）"""
        cache_key = f"nominatim:{address}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        self._rate_limit()
        
        # 日本語住所をローマ字変換（簡易版）
        search_query = self._convert_address_for_search(address)
        
        params = {
            'q': search_query,
            'format': 'json',
            'addressdetails': 1,
            'limit': 3,  # 複数候補取得
            'countrycodes': 'jp',  # 日本に限定
            'accept-language': 'en'  # 英語で検索
        }
        
        try:
            # UTF-8エンコーディング対応
            session = requests.Session()
            session.headers.update(self.headers)
            
            response = session.get(
                self.nominatim_base_url, 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                location = Location(
                    name=address,
                    address=result.get('display_name', address),
                    lat=float(result['lat']),
                    lng=float(result['lon']),
                    place_id=result.get('place_id')
                )
                
                self.cache[cache_key] = location
                self._save_cache()
                logger.info(f"✅ ジオコーディング成功: {address}")
                return location
            else:
                logger.error(f"❌ ジオコーディング失敗: {address} - 結果なし")
                
        except Exception as e:
            logger.error(f"❌ ジオコーディング エラー: {address} - {e}")
        
        return None
    
    def get_distance_matrix_osrm(self, locations: List[Location]) -> Dict[Tuple[int, int], RouteSegment]:
        """OSRM APIを使用して距離行列取得"""
        if len(locations) < 2:
            return {}
        
        # キャッシュキー生成
        location_keys = [f"{loc.lat},{loc.lng}" for loc in locations]
        cache_key = f"osrm_matrix:{'|'.join(sorted(location_keys))}"
        
        if cache_key in self.cache:
            logger.info("✅ 距離行列キャッシュから取得")
            return self.cache[cache_key]
        
        # OSRM Table Service APIを使用
        coordinates = ';'.join([f"{loc.lng},{loc.lat}" for loc in locations])
        url = f"{self.osrm_base_url}/{coordinates}"
        
        params = {
            'annotations': 'distance,duration'
        }
        
        try:
            self._rate_limit()
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] != 'Ok':
                logger.error(f"OSRM API エラー: {data['code']}")
                return self._fallback_distance_matrix(locations)
            
            distance_matrix = {}
            distances = data['distances']  # メートル単位
            durations = data['durations']  # 秒単位
            
            for i, origin in enumerate(locations):
                for j, destination in enumerate(locations):
                    if i < len(distances) and j < len(distances[i]):
                        distance_km = distances[i][j] / 1000.0
                        duration_minutes = durations[i][j] / 60.0
                        
                        segment = RouteSegment(
                            from_location=origin,
                            to_location=destination,
                            distance_km=distance_km,
                            duration_minutes=int(duration_minutes)
                        )
                        
                        distance_matrix[(i, j)] = segment
            
            logger.info(f"✅ OSRM距離行列取得完了: {len(distance_matrix)}区間")
            self.cache[cache_key] = distance_matrix
            self._save_cache()
            return distance_matrix
            
        except Exception as e:
            logger.error(f"OSRM API エラー: {e}")
            return self._fallback_distance_matrix(locations)
    
    def _fallback_distance_matrix(self, locations: List[Location]) -> Dict[Tuple[int, int], RouteSegment]:
        """フォールバック: 直線距離で距離行列作成"""
        logger.info("🔄 フォールバック: 直線距離で距離行列作成")
        
        distance_matrix = {}
        
        for i, loc1 in enumerate(locations):
            for j, loc2 in enumerate(locations):
                if i == j:
                    distance = 0.0
                else:
                    distance = self._calculate_haversine_distance(
                        loc1.lat, loc1.lng, loc2.lat, loc2.lng
                    )
                
                segment = RouteSegment(
                    from_location=loc1,
                    to_location=loc2,
                    distance_km=distance,
                    duration_minutes=int(distance * 2.5)  # 時速24kmと仮定
                )
                distance_matrix[(i, j)] = segment
        
        return distance_matrix
    
    def _calculate_haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine公式による直線距離計算"""
        import math
        
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
    
    def solve_tsp_nearest_neighbor(self, locations: List[Location], start_index: int = 0) -> Tuple[List[int], float]:
        """最近傍法によるTSP解法"""
        distance_matrix = self.get_distance_matrix_osrm(locations)
        
        if not distance_matrix:
            return list(range(len(locations))), 0.0
        
        n = len(locations)
        unvisited = set(range(n))
        current = start_index
        route = [current]
        unvisited.remove(current)
        total_distance = 0.0
        
        while unvisited:
            nearest = min(
                unvisited, 
                key=lambda x: distance_matrix.get((current, x), RouteSegment(None, None, float('inf'), 0)).distance_km
            )
            
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
        """総当たり法によるTSP解法（小規模のみ）"""
        if len(locations) > 8:
            logger.warning("⚠️ 地点数が多すぎます。最近傍法を使用します。")
            return self.solve_tsp_nearest_neighbor(locations, start_index)
        
        distance_matrix = self.get_distance_matrix_osrm(locations)
        
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
    
    def _calculate_route_distance(self, route: List[int], distance_matrix: Dict[Tuple[int, int], RouteSegment]) -> float:
        """ルート総距離計算"""
        total_distance = 0.0
        
        for i in range(len(route)):
            next_i = (i + 1) % len(route)
            segment = distance_matrix.get((route[i], route[next_i]))
            if segment:
                total_distance += segment.distance_km
            else:
                return float('inf')
        
        return total_distance
    
    def optimize_route(self, addresses: List[str], start_address: str = None, 
                      algorithm: str = 'auto') -> Dict:
        """
        ルート最適化メイン関数
        
        Args:
            addresses: 訪問先住所リスト
            start_address: 開始地点住所
            algorithm: 'auto', 'nearest_neighbor', 'brute_force'
        
        Returns:
            最適化結果辞書
        """
        logger.info(f"🚀 無料API版 ルート最適化開始: {len(addresses)}地点")
        
        # ジオコーディング（逐次処理・レート制限対応）
        locations = []
        
        for addr in addresses:
            location = self.geocode_address(addr)
            if location:
                locations.append(location)
            else:
                logger.error(f"❌ ジオコーディング失敗: {addr}")
        
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
            algorithm = 'brute_force' if len(locations) <= 6 else 'nearest_neighbor'
        
        logger.info(f"🧮 アルゴリズム: {algorithm}")
        
        # TSP解法実行
        start_time = time.time()
        
        if algorithm == 'brute_force':
            optimal_route, total_distance = self.solve_tsp_brute_force(locations, start_index)
        else:  # nearest_neighbor
            optimal_route, total_distance = self.solve_tsp_nearest_neighbor(locations, start_index)
        
        optimization_time = time.time() - start_time
        
        # 結果生成
        optimized_locations = [locations[i] for i in optimal_route]
        
        # 詳細ルート情報生成
        distance_matrix = self.get_distance_matrix_osrm(locations)
        route_segments = []
        total_duration = 0
        
        for i in range(len(optimal_route)):
            next_i = (i + 1) % len(optimal_route)
            segment = distance_matrix.get((optimal_route[i], optimal_route[next_i]))
            if segment:
                route_segments.append({
                    'from': segment.from_location.name,
                    'to': segment.to_location.name,
                    'distance_km': round(segment.distance_km, 2),
                    'duration_minutes': segment.duration_minutes
                })
                total_duration += segment.duration_minutes
        
        result = {
            'success': True,
            'api_used': 'OpenStreetMap (Nominatim + OSRM)',
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
            'openstreetmap_url': self._generate_openstreetmap_url(optimized_locations)
        }
        
        logger.info(f"✅ 最適化完了: {total_distance:.2f}km, {total_duration}分")
        
        return result
    
    def _generate_openstreetmap_url(self, locations: List[Location]) -> str:
        """OpenStreetMap URL生成"""
        if len(locations) < 2:
            return ""
        
        # 最初の地点を中心にした地図URL
        first_loc = locations[0]
        zoom = 12
        base_url = f"https://www.openstreetmap.org/?mlat={first_loc.lat}&mlon={first_loc.lng}&zoom={zoom}"
        
        return base_url

def main():
    """メイン実行関数"""
    print("🗺️ 無料API版 最短ルート最適化システム")
    print("📡 OpenStreetMap (Nominatim + OSRM) 使用")
    print("=" * 60)
    
    # テスト用住所（札幌市内）
    test_addresses = [
        "札幌市中央区大通西3丁目",  # 大通公園
        "札幌市中央区北5条西2丁目",  # 札幌駅
        "札幌市白石区菊水元町5条1丁目",  # サッポロビール園
        "札幌市手稲区手稲本町2条2丁目"  # 手稲駅
    ]
    
    print("📍 テスト地点:")
    for i, addr in enumerate(test_addresses, 1):
        print(f"  {i}. {addr}")
    
    try:
        optimizer = OpenStreetMapRouteOptimizer()
        
        print("\n🚀 最適化実行中...")
        result = optimizer.optimize_route(
            addresses=test_addresses,
            start_address="札幌市中央区大通西3丁目",
            algorithm='auto'
        )
        
        if result.get('success'):
            print(f"\n✅ 最適化完了!")
            print(f"使用API: {result['api_used']}")
            print(f"アルゴリズム: {result['algorithm']}")
            print(f"総距離: {result['total_distance_km']}km")
            print(f"総時間: {result['total_duration_hours']}時間")
            print(f"計算時間: {result['optimization_time_seconds']}秒")
            
            print("\n📍 最適ルート:")
            for location in result['optimized_route']:
                print(f"  {location['order']}. {location['name']}")
            
            print(f"\n🗺️ OpenStreetMap: {result['openstreetmap_url']}")
            
            if result['route_segments']:
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