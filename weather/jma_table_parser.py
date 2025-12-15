#!/usr/bin/env python3
"""
気象庁警報・注意報の表データを直接パース
一次細分区域別の表形式データを解析
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def parse_jma_warning_table():
    """気象庁の警報・注意報表を直接パース"""
    
    # 全国警報・注意報ページ
    url = "https://www.jma.go.jp/bosai/warning/"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print("🌤️  気象庁警報・注意報表パーサー")
    print("=" * 40)
    
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        full_text = soup.get_text()
        
        # 発表時刻を検索
        time_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日(\d{1,2})時(\d{1,2})分発表'
        time_match = re.search(time_pattern, full_text)
        
        if time_match:
            pub_time = f"{time_match.group(1)}年{time_match.group(2)}月{time_match.group(3)}日{time_match.group(4)}時{time_match.group(5)}分発表"
            print(f"🕐 発表時刻: {pub_time}")
        else:
            print(f"🕐 発表時刻: 検出されず")
        
        # 石狩・空知地方の情報を検索
        target_areas = ['石狩地方', '空知地方']
        
        for area in target_areas:
            print(f"\n📍 {area} 検索中...")
            
            # 地方名の行を検索
            area_pattern = f'{area}.*?(?=北海道|$)'
            area_match = re.search(area_pattern, full_text, re.DOTALL)
            
            if area_match:
                area_text = area_match.group()
                print(f"  🔍 該当テキスト: {area_text[:200]}...")
                
                # 注意報・警報キーワード検索
                warning_types = {
                    '大雨': '大雨',
                    '洪水': '洪水', 
                    '暴風': '暴風',
                    '強風': '強風',
                    '波浪': '波浪',
                    '雷': '雷',
                    '濃霧': '濃霧',
                    '霜': '霜',
                    '注': '注意報',
                    '警': '警報'
                }
                
                found_warnings = []
                for keyword, full_name in warning_types.items():
                    if keyword in area_text:
                        found_warnings.append(full_name)
                
                if found_warnings:
                    print(f"  ⚠️  検出された警報・注意報:")
                    for warning in found_warnings:
                        print(f"    - {warning}")
                else:
                    print(f"  ℹ️  警報・注意報なし")
            else:
                print(f"  ❌ {area}の情報が見つかりません")
        
        # ページ全体から北海道関連の警報情報を抽出
        print(f"\n🗾 北海道全体の警報・注意報情報:")
        hokkaido_pattern = r'北海道[^地方]*地方.*?(?=北海道|$)'
        hokkaido_matches = re.findall(hokkaido_pattern, full_text)
        
        for i, match in enumerate(hokkaido_matches[:15]):  # 最初の15件
            if '石狩' in match or '空知' in match:
                print(f"  🎯 関連情報 {i+1}: {match[:100]}...")
        
        # 表形式データの検索
        print(f"\n📊 表データ構造解析:")
        tables = soup.find_all('table')
        print(f"  テーブル数: {len(tables)}")
        
        for i, table in enumerate(tables[:3]):
            rows = table.find_all('tr')
            print(f"  テーブル{i+1}: {len(rows)}行")
            
            for j, row in enumerate(rows[:5]):
                cells = row.find_all(['td', 'th'])
                row_text = ' | '.join([cell.get_text(strip=True) for cell in cells])
                if '石狩' in row_text or '空知' in row_text or '濃霧' in row_text:
                    print(f"    関連行{j+1}: {row_text}")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

if __name__ == "__main__":
    parse_jma_warning_table()