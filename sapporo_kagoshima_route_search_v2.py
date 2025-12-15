#!/usr/bin/env python3
"""
札幌から鹿児島までの公共交通機関ルート検索システム (Routes API対応版)
Google Maps Routes API を使用
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
import time

class RouteSearcher:
    def __init__(self, api_key=None):
        """初期化"""
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            raise ValueError("Google Maps APIキーが設定されていません")
        
        # Routes API v1 エンドポイント
        self.base_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        
    def _get_api_key(self):
        """APIキーを取得（複数のソースから）"""
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
    
    def search_routes(self, origin="札幌市", destination="鹿児島市"):
        """ルート検索を実行"""
        print(f"🔍 {origin}から{destination}までのルートを検索中...")
        
        # リクエストヘッダー
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.legs.steps.transitDetails,routes.legs.steps.travelMode,routes.legs.steps.localizedValues,routes.legs.steps.startLocation,routes.legs.steps.endLocation'
        }
        
        # リクエストボディ
        request_body = {
            "origin": {
                "address": origin
            },
            "destination": {
                "address": destination
            },
            "travelMode": "TRANSIT",
            "computeAlternativeRoutes": True,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "ja",
            "regionCode": "JP"
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=request_body,
                timeout=30
            )
            
            print(f"📡 API応答ステータス: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self._display_routes(data, origin, destination)
                return data
            else:
                print(f"⚠️ APIエラー: {response.status_code}")
                print(f"エラー詳細: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏰ タイムアウトエラー: APIリクエストがタイムアウトしました")
            return None
        except requests.exceptions.RequestException as e:
            print(f"🚫 リクエストエラー: {e}")
            return None
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            return None
    
    def _display_routes(self, data, origin, destination):
        """ルート情報を表示"""
        if not data or 'routes' not in data:
            print("❌ ルートデータが見つかりません")
            return
        
        routes = data['routes']
        if not routes:
            print("❌ 利用可能なルートがありません")
            return
        
        print(f"\n🗺️ {origin} → {destination}")
        print("=" * 80)
        
        for i, route in enumerate(routes, 1):
            print(f"\n📍 ルート {i}:")
            print("-" * 40)
            
            # 基本情報
            duration = route.get('duration', {})
            distance = route.get('distanceMeters', 0)
            
            duration_text = self._format_duration(duration)
            distance_text = self._format_distance(distance)
            
            print(f"⏱️ 所要時間: {duration_text}")
            print(f"📏 総距離: {distance_text}")
            
            # 詳細な経路情報
            legs = route.get('legs', [])
            total_steps = sum(len(leg.get('steps', [])) for leg in legs)
            print(f"🔄 総ステップ数: {total_steps}")
            
            # 各区間の詳細
            step_count = 0
            for leg_idx, leg in enumerate(legs):
                steps = leg.get('steps', [])
                for step_idx, step in enumerate(steps):
                    step_count += 1
                    travel_mode = step.get('travelMode', 'UNKNOWN')
                    
                    # 移動手段の絵文字
                    mode_emoji = {
                        'TRANSIT': '🚇',
                        'WALKING': '🚶',
                        'DRIVING': '🚗',
                        'BICYCLING': '🚴',
                        'FLIGHT': '✈️'
                    }.get(travel_mode, '❓')
                    
                    print(f"  {step_count}. {mode_emoji} {travel_mode}")
                    
                    # 交通機関の詳細
                    transit_details = step.get('transitDetails', {})
                    if transit_details:
                        self._display_transit_details(transit_details)
        
        print("\n" + "=" * 80)
        self._display_usage_notes()
    
    def _display_transit_details(self, transit_details):
        """交通機関の詳細情報を表示"""
        stop_details = transit_details.get('stopDetails', {})
        arrival_stop = stop_details.get('arrivalStop', {})
        departure_stop = stop_details.get('departureStop', {})
        
        if departure_stop:
            dep_name = departure_stop.get('name', '不明')
            print(f"    🚏 出発: {dep_name}")
        
        if arrival_stop:
            arr_name = arrival_stop.get('name', '不明')
            print(f"    🏁 到着: {arr_name}")
        
        # 路線情報
        transit_line = transit_details.get('transitLine', {})
        if transit_line:
            line_name = transit_line.get('name', '不明')
            vehicle = transit_line.get('vehicle', {})
            vehicle_type = vehicle.get('type', 'UNKNOWN')
            
            vehicle_emoji = {
                'BUS': '🚌',
                'SUBWAY': '🚇',
                'TRAIN': '🚄',
                'TRAM': '🚋',
                'RAIL': '🚆',
                'FERRY': '⛴️',
                'CABLE_CAR': '🚠',
                'GONDOLA_LIFT': '🚡',
                'FUNICULAR': '🚞'
            }.get(vehicle_type, '🚐')
            
            print(f"    {vehicle_emoji} {line_name} ({vehicle_type})")
    
    def _format_duration(self, duration):
        """所要時間をフォーマット"""
        if not duration:
            return "不明"
        
        seconds = int(duration.get('seconds', 0))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}時間{minutes}分"
        else:
            return f"{minutes}分"
    
    def _format_distance(self, distance_meters):
        """距離をフォーマット"""
        if not distance_meters:
            return "不明"
        
        if distance_meters >= 1000:
            km = distance_meters / 1000
            return f"{km:.1f}km"
        else:
            return f"{distance_meters}m"
    
    def _display_usage_notes(self):
        """使用上の注意を表示"""
        print("\n💡 注意事項:")
        print("- 料金情報はAPIでは提供されません")
        print("- 飛行機利用の場合は航空会社サイトで料金確認してください")
        print("- 時刻表は変更される可能性があります")
        print("- 乗り換え時間や待ち時間を考慮してください")

def main():
    """メイン処理"""
    try:
        # RouteSearcherを初期化
        searcher = RouteSearcher()
        
        # 札幌から鹿児島までのルート検索
        result = searcher.search_routes("札幌市", "鹿児島市")
        
        if result:
            print("\n✅ ルート検索が完了しました")
        else:
            print("\n❌ ルート検索に失敗しました")
            
    except ValueError as e:
        print(f"❌ 設定エラー: {e}")
        print("\nAPIキーの設定方法:")
        print("1. 環境変数 GOOGLE_MAPS_API_KEY を設定")
        print("2. カレントディレクトリに google_maps_api_key.txt を作成")
        print("3. ホームディレクトリに .google_maps_api_key を作成")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()