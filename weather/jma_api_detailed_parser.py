#!/usr/bin/env python3
"""
気象庁APIから警報・注意報の詳細を正確に解析
警報名を適切にデコードして表示
"""

import requests
import json
from datetime import datetime

def parse_jma_api_details():
    """APIから詳細な警報・注意報情報を解析"""
    
    session = requests.Session()
    area_codes = {
        '016000': '石狩地方',
        '015000': '空知地方'
    }
    
    print("🌤️  気象庁API詳細解析システム")
    print("=" * 40)
    
    for area_code, area_name in area_codes.items():
        print(f"\n📍 {area_name} ({area_code}) API詳細解析")
        
        api_url = f"https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json"
        
        try:
            response = session.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 発表時刻
            report_time = data.get('reportDatetime', '不明')
            print(f"  🕐 API発表時刻: {report_time}")
            
            # 各地域の警報を詳細解析
            area_types = data.get('areaTypes', [])
            total_warnings = 0
            warning_details = []
            
            for area_type in area_types:
                area_type_name = area_type.get('name', '不明')
                areas = area_type.get('areas', [])
                
                print(f"  📂 地域タイプ: {area_type_name}")
                
                for area in areas:
                    area_name_detail = area.get('name', '不明')
                    area_code_detail = area.get('code', '不明')
                    warnings = area.get('warnings', [])
                    
                    if warnings:
                        print(f"    🏮 地域: {area_name_detail} (コード: {area_code_detail})")
                        
                        for warning in warnings:
                            warning_name = warning.get('name', '不明')
                            warning_code = warning.get('code', '不明')
                            warning_status = warning.get('status', '不明')
                            
                            warning_details.append({
                                'area_name': area_name_detail,
                                'area_code': area_code_detail,
                                'warning_name': warning_name,
                                'warning_code': warning_code,
                                'status': warning_status
                            })
                            
                            total_warnings += 1
                            print(f"      ⚠️  {warning_name} (コード: {warning_code}, 状態: {warning_status})")
            
            print(f"  📊 総警報・注意報数: {total_warnings}件")
            
            # 濃霧注意報を特別検索
            fog_warnings = [w for w in warning_details if '濃霧' in w['warning_name']]
            if fog_warnings:
                print(f"  🌫️  濃霧関連: {len(fog_warnings)}件")
                for fog in fog_warnings:
                    print(f"    - {fog['area_name']}: {fog['warning_name']} ({fog['status']})")
            else:
                print(f"  🌫️  濃霧関連: なし")
            
            # 警報名一覧（重複除去）
            unique_warnings = list(set([w['warning_name'] for w in warning_details]))
            print(f"  📋 発表中の警報・注意報種類: {len(unique_warnings)}種類")
            for warning_type in sorted(unique_warnings):
                count = len([w for w in warning_details if w['warning_name'] == warning_type])
                print(f"    - {warning_type}: {count}件")
            
        except Exception as e:
            print(f"  ❌ エラー: {str(e)}")

if __name__ == "__main__":
    parse_jma_api_details()