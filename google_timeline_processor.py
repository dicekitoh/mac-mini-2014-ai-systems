#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps Timeline JSONデータ処理ツール
エクスポートしたタイムラインデータを解析し、訪問先情報を抽出

使用方法:
1. GoogleマップアプリまたはGoogle TakeoutからJSONファイルをエクスポート
2. このスクリプトでJSONファイルを処理
"""

import json
import datetime
from typing import List, Dict, Any
import argparse

class GoogleTimelineProcessor:
    def __init__(self, json_file_path: str):
        """
        Google Timeline JSONファイルを読み込み
        
        Args:
            json_file_path: エクスポートしたJSONファイルのパス
        """
        self.json_file_path = json_file_path
        self.timeline_data = self._load_json()
        
    def _load_json(self) -> Dict[str, Any]:
        """JSONファイルを読み込み"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"エラー: ファイル {self.json_file_path} が見つかりません")
            return {}
        except json.JSONDecodeError:
            print(f"エラー: {self.json_file_path} はJSONファイルではありません")
            return {}
    
    def get_place_visits(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        訪問先リストを取得
        
        Args:
            start_date: 開始日 (YYYY-MM-DD形式)
            end_date: 終了日 (YYYY-MM-DD形式)
            
        Returns:
            訪問先情報のリスト
        """
        visits = []
        
        # 新形式（デバイスエクスポート）の場合
        if 'semanticSegments' in self.timeline_data:
            visits.extend(self._process_semantic_segments())
        
        # 旧形式（Google Takeout）の場合
        if 'timelineObjects' in self.timeline_data:
            visits.extend(self._process_timeline_objects())
        
        # 日付フィルタリング
        if start_date or end_date:
            visits = self._filter_by_date(visits, start_date, end_date)
        
        return sorted(visits, key=lambda x: x['timestamp'])
    
    def _process_semantic_segments(self) -> List[Dict[str, Any]]:
        """新形式のデータ処理"""
        visits = []
        
        for segment in self.timeline_data.get('semanticSegments', []):
            if 'visit' in segment:
                visit = segment['visit']
                location = visit.get('topCandidate', {})
                
                visit_info = {
                    'timestamp': self._parse_timestamp(segment.get('startTime')),
                    'place_name': location.get('placeId', 'Unknown'),
                    'address': location.get('semanticType', ''),
                    'coordinates': {
                        'lat': location.get('location', {}).get('latE7', 0) / 1e7,
                        'lng': location.get('location', {}).get('lngE7', 0) / 1e7
                    },
                    'duration_minutes': self._calculate_duration(
                        segment.get('startTime'), 
                        segment.get('endTime')
                    )
                }
                visits.append(visit_info)
        
        return visits
    
    def _process_timeline_objects(self) -> List[Dict[str, Any]]:
        """旧形式のデータ処理"""
        visits = []
        
        for obj in self.timeline_data.get('timelineObjects', []):
            if 'placeVisit' in obj:
                place_visit = obj['placeVisit']
                location = place_visit.get('location', {})
                
                visit_info = {
                    'timestamp': self._parse_timestamp(place_visit.get('duration', {}).get('startTimestamp')),
                    'place_name': location.get('name', 'Unknown'),
                    'address': location.get('address', ''),
                    'coordinates': {
                        'lat': location.get('latitudeE7', 0) / 1e7,
                        'lng': location.get('longitudeE7', 0) / 1e7
                    },
                    'duration_minutes': self._calculate_duration(
                        place_visit.get('duration', {}).get('startTimestamp'),
                        place_visit.get('duration', {}).get('endTimestamp')
                    )
                }
                visits.append(visit_info)
        
        return visits
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime.datetime:
        """タイムスタンプを解析"""
        if not timestamp_str:
            return datetime.datetime.min
        
        try:
            # ISO形式
            if 'T' in timestamp_str:
                return datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            # Unix timestamp
            else:
                return datetime.datetime.fromtimestamp(int(timestamp_str) / 1000)
        except:
            return datetime.datetime.min
    
    def _calculate_duration(self, start_time: str, end_time: str) -> int:
        """滞在時間を計算（分単位）"""
        try:
            start = self._parse_timestamp(start_time)
            end = self._parse_timestamp(end_time)
            return int((end - start).total_seconds() / 60)
        except:
            return 0
    
    def _filter_by_date(self, visits: List[Dict], start_date: str, end_date: str) -> List[Dict]:
        """日付範囲でフィルタリング"""
        filtered_visits = []
        
        for visit in visits:
            visit_date = visit['timestamp'].date()
            
            if start_date and visit_date < datetime.datetime.strptime(start_date, '%Y-%m-%d').date():
                continue
            if end_date and visit_date > datetime.datetime.strptime(end_date, '%Y-%m-%d').date():
                continue
                
            filtered_visits.append(visit)
        
        return filtered_visits
    
    def export_to_csv(self, visits: List[Dict], output_file: str):
        """CSV形式でエクスポート"""
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'place_name', 'address', 'latitude', 'longitude', 'duration_minutes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for visit in visits:
                writer.writerow({
                    'timestamp': visit['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'place_name': visit['place_name'],
                    'address': visit['address'],
                    'latitude': visit['coordinates']['lat'],
                    'longitude': visit['coordinates']['lng'],
                    'duration_minutes': visit['duration_minutes']
                })

def main():
    parser = argparse.ArgumentParser(description='Google Timeline JSONデータ処理ツール')
    parser.add_argument('json_file', help='エクスポートしたJSONファイルのパス')
    parser.add_argument('--start-date', help='開始日 (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='終了日 (YYYY-MM-DD)')
    parser.add_argument('--output-csv', help='CSV出力ファイル名')
    
    args = parser.parse_args()
    
    # Timeline処理
    processor = GoogleTimelineProcessor(args.json_file)
    visits = processor.get_place_visits(args.start_date, args.end_date)
    
    if not visits:
        print("訪問先データが見つかりませんでした")
        return
    
    print(f"取得した訪問先数: {len(visits)}")
    print("\n最近の訪問先:")
    
    for visit in visits[-5:]:  # 最新5件表示
        print(f"日時: {visit['timestamp'].strftime('%Y-%m-%d %H:%M')}")
        print(f"場所: {visit['place_name']}")
        print(f"住所: {visit['address']}")
        print(f"座標: {visit['coordinates']['lat']:.6f}, {visit['coordinates']['lng']:.6f}")
        print(f"滞在時間: {visit['duration_minutes']}分")
        print("-" * 50)
    
    # CSV出力
    if args.output_csv:
        processor.export_to_csv(visits, args.output_csv)
        print(f"\nCSVファイルに出力しました: {args.output_csv}")

if __name__ == "__main__":
    main()