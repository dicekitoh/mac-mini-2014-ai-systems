#!/usr/bin/env python3
"""
気象庁WebサイトからHTML内の発表時刻と警報詳細を簡易抽出
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

def extract_jma_web_details():
    """気象庁Webサイトから詳細情報を抽出"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    area_codes = {
        '016000': '石狩地方',
        '015000': '空知地方'
    }
    
    print("🌤️  気象庁Web発表時刻・警報詳細抽出")
    print("=" * 40)
    
    for area_code, area_name in area_codes.items():
        print(f"\n📍 {area_name} 抽出中...")
        
        url = f"https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code={area_code}"
        
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            full_text = soup.get_text()
            
            print(f"  📄 ページタイトル: {soup.title.get_text(strip=True) if soup.title else '不明'}")
            
            # 発表時刻を検索
            time_patterns = [
                r'(\d{4})年(\d{1,2})月(\d{1,2})日(\d{1,2})時(\d{1,2})分発表',
                r'(\d{1,2})月(\d{1,2})日(\d{1,2})時(\d{1,2})分発表',
                r'(\d{1,2})月(\d{1,2})日(\d{1,2})時(\d{1,2})分',
                r'(\d{1,2})日(\d{1,2})時(\d{1,2})分発表',
                r'(\d{1,2})時(\d{1,2})分発表'
            ]
            
            found_times = []
            for pattern in time_patterns:
                matches = re.findall(pattern, full_text)
                for match in matches:
                    if isinstance(match, tuple):
                        time_str = ''.join(str(x) for x in match)
                    else:
                        time_str = str(match)
                    found_times.append(time_str)
            
            if found_times:
                print(f"  🕐 発表時刻検出: {len(found_times)}件")
                for i, time_str in enumerate(found_times[:5]):
                    print(f"    {i+1}. {time_str}")
            else:
                print(f"  🕐 発表時刻: 検出されず")
            
            # 警報・注意報キーワード検索
            warning_keywords = ['濃霧警報', '濃霧注意報', '暴風警報', '暴風注意報', '大雨警報', '大雨注意報', 
                              '強風注意報', '雷注意報', '乾燥注意報', '低温注意報']
            
            found_warnings = []
            for keyword in warning_keywords:
                if keyword in full_text:
                    # キーワード前後の文脈を取得
                    pattern = f'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
                    matches = re.findall(pattern, full_text)
                    for match in matches:
                        found_warnings.append({
                            'keyword': keyword,
                            'context': match.strip()
                        })
            
            if found_warnings:
                print(f"  ⚠️  警報・注意報検出: {len(found_warnings)}件")
                for i, warning in enumerate(found_warnings[:3]):
                    print(f"    {i+1}. {warning['keyword']}")
                    print(f"       文脈: {warning['context'][:80]}...")
            else:
                print(f"  ⚠️  警報・注意報: 特定の警報は検出されず")
            
            # 石狩・空知関連文章を検索
            area_patterns = [
                f'{area_name}[^。]*警報[^。]*',
                f'{area_name}[^。]*注意報[^。]*',
                f'[^。]*{area_name}[^。]*発表[^。]*'
            ]
            
            area_mentions = []
            for pattern in area_patterns:
                matches = re.findall(pattern, full_text)
                area_mentions.extend(matches)
            
            if area_mentions:
                print(f"  🏮 {area_name}関連情報: {len(area_mentions)}件")
                for i, mention in enumerate(area_mentions[:2]):
                    print(f"    {i+1}. {mention[:100]}...")
            else:
                print(f"  🏮 {area_name}関連情報: 検出されず")
            
            # ページ内の全体的な警報・注意報キーワード数
            total_warning_count = full_text.count('警報') + full_text.count('注意報')
            total_time_count = full_text.count('発表') + full_text.count('時') + full_text.count('分')
            
            print(f"  📊 統計: 警報関連キーワード {total_warning_count}件, 時刻関連 {total_time_count}件")
            
        except Exception as e:
            print(f"  ❌ エラー: {str(e)}")

if __name__ == "__main__":
    extract_jma_web_details()