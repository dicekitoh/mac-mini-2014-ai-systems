#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Takeout タイムラインデータ処理ツール
ダウンロードしたJSONファイルから訪問地を抽出してルート最適化
"""

import json
import sys
import os
from datetime import datetime, timedelta
from collections import Counter
sys.path.append('/home/fujinosuke/projects')
from easy_route_optimizer import optimize_my_route

def process_timeline_data(json_file_path, days_back=30, min_visits=2):
    """
    Google Takeout のタイムラインデータを処理
    
    Args:
        json_file_path: Takeoutからダウンロードしたjsonファイルパス
        days_back: 過去何日分のデータを対象にするか
        min_visits: 最小訪問回数（頻繁に訪問した場所のみ抽出）
    
    Returns:
        訪問地リストと最適化結果
    """
    print("📍 Google タイムラインデータ解析中...")
    
    if not os.path.exists(json_file_path):
        print(f"❌ ファイルが見つかりません: {json_file_path}")
        return None
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            timeline_data = json.load(f)
    except Exception as e:
        print(f"❌ JSONファイル読み込みエラー: {e}")
        return None
    
    # 期間設定
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    visited_places = []
    place_counter = Counter()
    
    # タイムラインデータの解析
    if 'timelineObjects' in timeline_data:
        for item in timeline_data['timelineObjects']:
            if 'placeVisit' in item:
                place_visit = item['placeVisit']
                
                # 訪問日時チェック
                if 'duration' in place_visit:
                    start_time = place_visit['duration'].get('startTimestamp')
                    if start_time:
                        visit_date = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        if visit_date < cutoff_date:
                            continue
                
                # 場所情報取得
                if 'location' in place_visit:
                    location = place_visit['location']
                    
                    # 場所名取得
                    place_name = location.get('name', '不明な場所')
                    address = location.get('address', '')
                    
                    # 座標取得
                    lat = location.get('latitudeE7', 0) / 1e7
                    lng = location.get('longitudeE7', 0) / 1e7
                    
                    if place_name != '不明な場所' and lat != 0 and lng != 0:
                        place_info = {
                            'name': place_name,
                            'address': address,
                            'lat': lat,
                            'lng': lng,
                            'visit_date': visit_date.strftime('%Y-%m-%d') if 'visit_date' in locals() else 'unknown'
                        }
                        
                        visited_places.append(place_info)
                        place_counter[place_name] += 1
    
    # 頻繁に訪問した場所を抽出
    frequent_places = [name for name, count in place_counter.items() if count >= min_visits]
    
    print(f"✅ 解析完了: {len(visited_places)}件の訪問記録")
    print(f"📊 頻繁に訪問した場所: {len(frequent_places)}箇所")
    
    # 頻繁に訪問した場所の詳細表示
    print(f"\n📍 よく訪問する場所 (最低{min_visits}回以上):")
    for i, (place, count) in enumerate(place_counter.most_common(10), 1):
        if count >= min_visits:
            print(f"  {i:2d}. {place} ({count}回)")
    
    # ルート最適化用の住所リスト作成
    optimization_addresses = []
    unique_places = {}
    
    for place in visited_places:
        if place['name'] in frequent_places and place['name'] not in unique_places:
            if place['address']:
                optimization_addresses.append(place['address'])
            else:
                optimization_addresses.append(f"{place['name']} ({place['lat']}, {place['lng']})")
            unique_places[place['name']] = place
    
    return {
        'all_visits': visited_places,
        'frequent_places': frequent_places,
        'place_counts': dict(place_counter),
        'optimization_addresses': optimization_addresses[:10]  # 最大10箇所
    }

def optimize_from_timeline(json_file_path, days_back=30, min_visits=2):
    """タイムラインデータから最適ルートを計算"""
    
    result = process_timeline_data(json_file_path, days_back, min_visits)
    
    if not result or len(result['optimization_addresses']) < 2:
        print("❌ 最適化に十分なデータがありません")
        return None
    
    print(f"\n🚀 {len(result['optimization_addresses'])}箇所の最適ルートを計算中...")
    
    # ルート最適化実行
    optimization_result = optimize_my_route(
        addresses=result['optimization_addresses'],
        save_result=True
    )
    
    return {
        'timeline_analysis': result,
        'route_optimization': optimization_result
    }

def create_sample_instructions():
    """Google Takeout でのデータ取得手順を表示"""
    print("""
📥 Google Takeout でタイムラインデータを取得する手順:

1. https://takeout.google.com/ にアクセス
2. 「データを選択」で「マップ（マイマップ）」を選択
3. または「ロケーション履歴」を選択
4. 「マイアクティビティ」も有用です
5. エクスポート形式: JSON
6. ダウンロード後、以下のコマンドで処理:

   python3 timeline_data_processor.py /path/to/timeline.json

📋 使用例:
   # 過去30日、最低2回訪問した場所を対象
   optimize_from_timeline('timeline.json', days_back=30, min_visits=2)
   
   # 過去7日、1回でも訪問した場所を対象  
   optimize_from_timeline('timeline.json', days_back=7, min_visits=1)
""")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        optimize_from_timeline(json_file)
    else:
        create_sample_instructions()