#!/usr/bin/env python3
"""
札幌から鹿児島までの公共交通機関ルート検索
Google Maps Directions APIを使用して複数のルートオプションを検索
"""

import os
import json
import requests
from datetime import datetime, timedelta
import sys
from typing import List, Dict, Any

class SapporoKagoshimaRouteSearch:
    def __init__(self, api_key: str):
        """
        初期化
        
        Args:
            api_key: Google Maps API キー
        """
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/directions/json"
        
    def search_routes(self, departure_time: datetime = None) -> List[Dict[str, Any]]:
        """
        札幌から鹿児島までのルートを検索
        
        Args:
            departure_time: 出発時刻（省略時は現在時刻）
            
        Returns:
            ルート情報のリスト
        """
        # 出発地と目的地
        origin = "札幌市"
        destination = "鹿児島市"
        
        # パラメータ設定
        params = {
            'origin': origin,
            'destination': destination,
            'mode': 'transit',
            'alternatives': 'true',
            'language': 'ja',
            'key': self.api_key
        }
        
        # 出発時刻の設定
        if departure_time:
            # UNIXタイムスタンプに変換
            timestamp = int(departure_time.timestamp())
            params['departure_time'] = timestamp
        
        try:
            # API呼び出し
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'OK':
                print(f"エラー: {data.get('status')}")
                if 'error_message' in data:
                    print(f"詳細: {data['error_message']}")
                return []
            
            return self._parse_routes(data['routes'])
            
        except requests.RequestException as e:
            print(f"API呼び出しエラー: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}")
            return []
    
    def _parse_routes(self, routes: List[Dict]) -> List[Dict[str, Any]]:
        """
        ルート情報をパース
        
        Args:
            routes: Google Maps APIからのルート情報
            
        Returns:
            パースされたルート情報
        """
        parsed_routes = []
        
        for i, route in enumerate(routes):
            route_info = {
                'route_number': i + 1,
                'summary': route.get('summary', ''),
                'total_duration': 0,
                'total_distance': 0,
                'transfers': 0,
                'steps': [],
                'has_flight': False
            }
            
            # 各レグ（区間）の情報を処理
            for leg in route['legs']:
                route_info['total_duration'] += leg['duration']['value']
                route_info['total_distance'] += leg['distance']['value']
                
                # 各ステップの情報を処理
                for step in leg['steps']:
                    step_info = self._parse_step(step)
                    route_info['steps'].append(step_info)
                    
                    # 乗り換え回数をカウント
                    if step.get('travel_mode') == 'TRANSIT':
                        route_info['transfers'] += 1
                        
                        # 飛行機利用の確認
                        if 'transit_details' in step:
                            vehicle_type = step['transit_details']['line'].get('vehicle', {}).get('type', '')
                            if vehicle_type == 'FLIGHT' or '航空' in step['transit_details']['line'].get('name', ''):
                                route_info['has_flight'] = True
            
            parsed_routes.append(route_info)
        
        return parsed_routes
    
    def _parse_step(self, step: Dict) -> Dict[str, Any]:
        """
        各ステップの情報をパース
        
        Args:
            step: ステップ情報
            
        Returns:
            パースされたステップ情報
        """
        step_info = {
            'mode': step.get('travel_mode', ''),
            'duration': step['duration']['value'],
            'distance': step['distance']['value'],
            'instructions': step.get('html_instructions', '').replace('<b>', '').replace('</b>', '')
        }
        
        # 公共交通機関の詳細情報
        if 'transit_details' in step:
            transit = step['transit_details']
            step_info['transit'] = {
                'departure_stop': transit['departure_stop']['name'],
                'arrival_stop': transit['arrival_stop']['name'],
                'departure_time': transit['departure_time'].get('text', ''),
                'arrival_time': transit['arrival_time'].get('text', ''),
                'line_name': transit['line']['name'],
                'line_short_name': transit['line'].get('short_name', ''),
                'vehicle_type': transit['line'].get('vehicle', {}).get('type', ''),
                'vehicle_name': transit['line'].get('vehicle', {}).get('name', ''),
                'num_stops': transit.get('num_stops', 0)
            }
        
        return step_info
    
    def format_duration(self, seconds: int) -> str:
        """
        秒数を時間形式に変換
        
        Args:
            seconds: 秒数
            
        Returns:
            フォーマットされた時間文字列
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}時間{minutes}分"
        else:
            return f"{minutes}分"
    
    def format_distance(self, meters: int) -> str:
        """
        メートルをキロメートル形式に変換
        
        Args:
            meters: メートル
            
        Returns:
            フォーマットされた距離文字列
        """
        km = meters / 1000
        return f"{km:.1f}km"
    
    def display_routes(self, routes: List[Dict[str, Any]]):
        """
        ルート情報を表示
        
        Args:
            routes: ルート情報のリスト
        """
        if not routes:
            print("ルートが見つかりませんでした。")
            return
        
        print("\n" + "="*80)
        print("🚄 札幌 → 鹿児島 公共交通機関ルート検索結果")
        print("="*80)
        
        for route in routes:
            print(f"\n【ルート {route['route_number']}】")
            if route['has_flight']:
                print("✈️  飛行機利用あり")
            
            print(f"所要時間: {self.format_duration(route['total_duration'])}")
            print(f"総距離: {self.format_distance(route['total_distance'])}")
            print(f"乗り換え回数: {route['transfers'] - 1}回")
            
            print("\n詳細ルート:")
            print("-" * 60)
            
            for i, step in enumerate(route['steps']):
                if step['mode'] == 'TRANSIT':
                    transit = step['transit']
                    print(f"\n{i+1}. 【{self._get_vehicle_emoji(transit['vehicle_type'])} {transit['line_name']}】")
                    if transit['line_short_name']:
                        print(f"   路線: {transit['line_short_name']}")
                    print(f"   乗車: {transit['departure_stop']} ({transit['departure_time']})")
                    print(f"   降車: {transit['arrival_stop']} ({transit['arrival_time']})")
                    print(f"   所要時間: {self.format_duration(step['duration'])}")
                    if transit['num_stops'] > 0:
                        print(f"   停車駅数: {transit['num_stops']}駅")
                elif step['mode'] == 'WALKING':
                    print(f"\n{i+1}. 🚶 徒歩")
                    print(f"   {step['instructions']}")
                    print(f"   所要時間: {self.format_duration(step['duration'])}")
                    print(f"   距離: {self.format_distance(step['distance'])}")
            
            print("\n" + "-" * 60)
    
    def _get_vehicle_emoji(self, vehicle_type: str) -> str:
        """
        交通機関の種類に応じた絵文字を返す
        
        Args:
            vehicle_type: 交通機関の種類
            
        Returns:
            絵文字
        """
        emoji_map = {
            'FLIGHT': '✈️',
            'TRAIN': '🚄',
            'SUBWAY': '🚇',
            'BUS': '🚌',
            'FERRY': '⛴️',
            'TRAM': '🚊',
            'RAIL': '🚆'
        }
        return emoji_map.get(vehicle_type, '🚊')


def load_api_key() -> str:
    """
    APIキーを読み込む
    
    Returns:
        APIキー
    """
    # 環境変数から読み込み
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    if api_key:
        return api_key
    
    # ファイルから読み込み
    key_file_paths = [
        'google_maps_api_key.txt',
        '.google_maps_api_key',
        os.path.expanduser('~/.google_maps_api_key')
    ]
    
    for path in key_file_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    api_key = f.read().strip()
                    if api_key:
                        return api_key
            except IOError:
                continue
    
    return None


def main():
    """メイン処理"""
    # APIキーの読み込み
    api_key = load_api_key()
    
    if not api_key:
        print("エラー: Google Maps APIキーが見つかりません。")
        print("\n以下のいずれかの方法でAPIキーを設定してください:")
        print("1. 環境変数 GOOGLE_MAPS_API_KEY を設定")
        print("2. カレントディレクトリに google_maps_api_key.txt を作成")
        print("3. ホームディレクトリに .google_maps_api_key を作成")
        sys.exit(1)
    
    # ルート検索インスタンスの作成
    searcher = SapporoKagoshimaRouteSearch(api_key)
    
    # 出発時刻の設定（オプション）
    # 例: 明日の朝8時に出発
    # departure_time = datetime.now() + timedelta(days=1)
    # departure_time = departure_time.replace(hour=8, minute=0, second=0, microsecond=0)
    
    # 現在時刻で検索
    print("札幌から鹿児島までのルートを検索中...")
    routes = searcher.search_routes()
    
    # 結果を表示
    searcher.display_routes(routes)
    
    # 料金情報の注意
    print("\n" + "="*80)
    print("💡 注意事項:")
    print("- 料金情報はGoogle Maps APIでは提供されないため、各交通機関の")
    print("  公式サイトで確認してください。")
    print("- 飛行機を利用する場合は、航空会社のサイトで料金をご確認ください。")
    print("- 時刻表は変更される可能性があるため、最新情報をご確認ください。")
    print("="*80)


if __name__ == "__main__":
    main()