#!/usr/bin/env python3
"""
札幌から鹿児島までの交通ルート情報システム
Google Maps API + 静的データを組み合わせた実用版
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta

class RouteInfoSystem:
    def __init__(self, api_key=None):
        """初期化"""
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            raise ValueError("Google Maps APIキーが設定されていません")
        
        # APIエンドポイント
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.distance_matrix_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        
    def _get_api_key(self):
        """APIキーを取得"""
        sources = [
            lambda: os.environ.get('GOOGLE_MAPS_API_KEY'),
            lambda: self._read_file('google_maps_api_key.txt'),
            lambda: self._read_file('~/.google_maps_api_key'),
            lambda: self._read_file('/home/fujinosuke/google_maps_config.json', json_key='api_key'),
        ]
        
        for source in sources:
            try:
                key = source()
                if key and key.strip():
                    return key.strip()
            except Exception:
                continue
        return None
    
    def _read_file(self, filepath, json_key=None):
        """ファイルからAPIキーを読み込み"""
        try:
            expanded_path = os.path.expanduser(filepath)
            with open(expanded_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if json_key:
                    data = json.loads(content)
                    return data.get(json_key)
                return content
        except Exception:
            return None
    
    def get_location_info(self, address):
        """住所から座標を取得"""
        params = {
            'address': address,
            'key': self.api_key,
            'language': 'ja',
            'region': 'jp'
        }
        
        try:
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK' and data['results']:
                    result = data['results'][0]
                    location = result['geometry']['location']
                    return {
                        'address': result['formatted_address'],
                        'lat': location['lat'],
                        'lng': location['lng']
                    }
            return None
        except Exception as e:
            print(f"❌ 位置情報取得エラー: {e}")
            return None
    
    def get_distance_info(self, origin, destination):
        """距離と時間情報を取得"""
        params = {
            'origins': origin,
            'destinations': destination,
            'key': self.api_key,
            'language': 'ja',
            'units': 'metric',
            'mode': 'transit'
        }
        
        try:
            response = requests.get(self.distance_matrix_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK' and data['rows']:
                    element = data['rows'][0]['elements'][0]
                    if element['status'] == 'OK':
                        return {
                            'distance': element.get('distance', {}),
                            'duration': element.get('duration', {}),
                            'status': 'OK'
                        }
            return {'status': 'FAILED'}
        except Exception as e:
            print(f"❌ 距離情報取得エラー: {e}")
            return {'status': 'ERROR'}
    
    def get_route_recommendations(self):
        """札幌-鹿児島間のルート推奨情報"""
        return {
            'flight_routes': [
                {
                    'name': '✈️ 最短ルート（飛行機利用）',
                    'description': '新千歳空港 → 鹿児島空港',
                    'duration': '約2時間',
                    'total_time': '約4-5時間（空港アクセス含む）',
                    'price_range': '15,000円 - 40,000円',
                    'details': [
                        '🚌 札幌市内 → 新千歳空港（バス約60分、1,100円）',
                        '✈️ 新千歳空港 → 鹿児島空港（約2時間、JAL/ANA）',
                        '🚌 鹿児島空港 → 鹿児島市内（バス約40分、600円）'
                    ],
                    'airlines': ['JAL', 'ANA'],
                    'frequency': '1日6-8便程度'
                }
            ],
            'train_routes': [
                {
                    'name': '🚄 新幹線ルート',
                    'description': '札幌 → 東京 → 鹿児島中央',
                    'duration': '約12-14時間',
                    'price_range': '30,000円 - 45,000円',
                    'details': [
                        '🚄 札幌 → 東京（北海道新幹線・東北新幹線、約4時間）',
                        '🚄 東京 → 鹿児島中央（東海道・山陽・九州新幹線、約7-8時間）'
                    ],
                    'advantages': ['快適性', '荷物制限なし', '天候に左右されにくい'],
                    'note': '乗り換えは東京駅または上野駅'
                }
            ],
            'bus_routes': [
                {
                    'name': '🚌 高速バス＋フェリー',
                    'description': '青森まで高速バス、フェリーで本州へ',
                    'duration': '約20-24時間',
                    'price_range': '15,000円 - 25,000円',
                    'details': [
                        '🚌 札幌 → 青森（高速バス、約8時間、8,000円程度）',
                        '⛴️ 青森 → 本州（フェリー利用）',
                        '🚌 本州各地 → 鹿児島（高速バス継続）'
                    ],
                    'advantages': ['最安値', '夜行便利用で宿泊費節約'],
                    'note': '体力が必要、長時間移動'
                }
            ]
        }
    
    def display_comprehensive_route_info(self, origin="札幌市", destination="鹿児島市"):
        """包括的なルート情報を表示"""
        print(f"🗾 {origin} → {destination} 交通ルート案内")
        print("=" * 80)
        
        # 位置情報取得
        print("📍 位置情報を取得中...")
        origin_info = self.get_location_info(origin)
        dest_info = self.get_location_info(destination)
        
        if origin_info and dest_info:
            print(f"出発地: {origin_info['address']}")
            print(f"目的地: {dest_info['address']}")
            
            # 直線距離計算
            distance_km = self._calculate_distance(
                origin_info['lat'], origin_info['lng'],
                dest_info['lat'], dest_info['lng']
            )
            print(f"📏 直線距離: 約{distance_km:.0f}km")
        
        # ルート推奨情報表示
        recommendations = self.get_route_recommendations()
        
        print(f"\n🎯 推奨ルート")
        print("-" * 50)
        
        # 飛行機ルート
        for route in recommendations['flight_routes']:
            self._display_route_details(route)
        
        # 新幹線ルート
        for route in recommendations['train_routes']:
            self._display_route_details(route)
        
        # バスルート
        for route in recommendations['bus_routes']:
            self._display_route_details(route)
        
        # 実用情報
        self._display_practical_info()
    
    def _display_route_details(self, route):
        """ルート詳細を表示"""
        print(f"\n{route['name']}")
        print(f"概要: {route['description']}")
        print(f"⏱️ 所要時間: {route['duration']}")
        if 'total_time' in route:
            print(f"⏱️ 総移動時間: {route['total_time']}")
        print(f"💰 料金目安: {route['price_range']}")
        
        print("📋 詳細ルート:")
        for i, detail in enumerate(route['details'], 1):
            print(f"  {i}. {detail}")
        
        if 'advantages' in route:
            print(f"✅ メリット: {', '.join(route['advantages'])}")
        
        if 'note' in route:
            print(f"📝 注意: {route['note']}")
        
        print("-" * 40)
    
    def _calculate_distance(self, lat1, lng1, lat2, lng2):
        """緯度経度から直線距離を計算（ハーバーサイン公式）"""
        import math
        
        R = 6371  # 地球の半径 (km)
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _display_practical_info(self):
        """実用的な追加情報を表示"""
        print("\n💡 実用情報")
        print("=" * 50)
        
        info_sections = {
            "🕐 最適出発時間": [
                "飛行機: 朝便（7-9時）または夕便（17-19時）が便数多い",
                "新幹線: 朝6-8時出発で当日到着可能",
                "高速バス: 夜行便利用で翌朝到着"
            ],
            "🎫 予約のコツ": [
                "飛行機: 早期予約で最大50%割引あり",
                "新幹線: JR九州レールパス等の割引切符活用",
                "バス: 平日利用で料金安く"
            ],
            "🧳 荷物について": [
                "飛行機: 重量制限あり（エコノミー23kg）",
                "新幹線: 大型荷物は事前予約必要",
                "バス: トランク利用可能、重量制限は緩い"
            ],
            "🌦️ 季節考慮": [
                "冬期: 飛行機が最も安定（雪による遅延少ない）",
                "夏期: 新幹線が快適（エアコン完備）",
                "春・秋: バス旅も快適な季節"
            ]
        }
        
        for section, items in info_sections.items():
            print(f"\n{section}")
            for item in items:
                print(f"  • {item}")
        
        print(f"\n📞 予約・問い合わせ先")
        contacts = {
            "JAL": "0570-025-071",
            "ANA": "0570-029-222", 
            "JR北海道": "011-222-7111",
            "JR九州": "050-3786-1717"
        }
        
        for company, phone in contacts.items():
            print(f"  • {company}: {phone}")

def main():
    """メイン処理"""
    try:
        system = RouteInfoSystem()
        system.display_comprehensive_route_info("札幌市", "鹿児島市")
        
    except ValueError as e:
        print(f"❌ 設定エラー: {e}")
        print("\nAPIキーの設定方法:")
        print("1. 環境変数 GOOGLE_MAPS_API_KEY を設定")
        print("2. google_maps_api_key.txt ファイルに保存")
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()