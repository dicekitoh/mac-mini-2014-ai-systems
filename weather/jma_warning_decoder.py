#!/usr/bin/env python3
"""
気象庁APIの警報コードを実際の警報名に変換
"""

import requests
import json

def decode_jma_warnings():
    """警報コードをデコードして実際の警報名を表示"""
    
    # 警報・注意報コード対応表
    warning_codes = {
        '1': '大雨警報',
        '2': '洪水警報', 
        '3': '暴風警報',
        '4': '暴風雪警報',
        '5': '大雪警報',
        '6': '波浪警報',
        '7': '高潮警報',
        '10': '大雨注意報',
        '11': '洪水注意報',
        '12': '強風注意報', 
        '13': '風雪注意報',
        '14': '大雪注意報',
        '15': '波浪注意報',
        '16': '高潮注意報',
        '17': '雷注意報',
        '18': '濃霧注意報',  # ←これが重要！
        '19': '乾燥注意報',
        '20': '濃霧注意報',  # ←コード20も濃霧注意報
        '21': 'なだれ注意報',
        '22': '着氷注意報',
        '23': '着雪注意報',
        '24': '融雪注意報',
        '25': '霜注意報',
        '26': '低温注意報'
    }
    
    session = requests.Session()
    area_codes = {
        '016000': '石狩地方',
        '015000': '空知地方'
    }
    
    print("🌤️  気象庁API警報デコーダー")
    print("=" * 40)
    
    for area_code, area_name in area_codes.items():
        print(f"\n📍 {area_name} 警報・注意報デコード結果")
        
        api_url = f"https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json"
        
        try:
            response = session.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 発表時刻
            report_time = data.get('reportDatetime', '不明')
            print(f"  🕐 発表時刻: {report_time}")
            
            # 警報をデコード
            all_warnings = {}
            total_count = 0
            
            for area_type in data.get('areaTypes', []):
                for area in area_type.get('areas', []):
                    area_name_detail = area.get('name', '不明')
                    
                    for warning in area.get('warnings', []):
                        warning_code = str(warning.get('code', '不明'))
                        warning_status = warning.get('status', '不明')
                        
                        # コードを警報名に変換
                        warning_name = warning_codes.get(warning_code, f'不明(コード:{warning_code})')
                        
                        if warning_name not in all_warnings:
                            all_warnings[warning_name] = {'発表': 0, '解除': 0, 'その他': 0}
                        
                        if warning_status == '発表':
                            all_warnings[warning_name]['発表'] += 1
                        elif warning_status == '解除':
                            all_warnings[warning_name]['解除'] += 1
                        else:
                            all_warnings[warning_name]['その他'] += 1
                        
                        total_count += 1
            
            print(f"  📊 総件数: {total_count}件")
            print(f"  📋 警報・注意報別集計:")
            
            for warning_name, counts in sorted(all_warnings.items()):
                total_this_warning = sum(counts.values())
                status_detail = []
                if counts['発表'] > 0:
                    status_detail.append(f"発表{counts['発表']}件")
                if counts['解除'] > 0:
                    status_detail.append(f"解除{counts['解除']}件")
                if counts['その他'] > 0:
                    status_detail.append(f"その他{counts['その他']}件")
                
                status_str = "、".join(status_detail)
                print(f"    🔸 {warning_name}: {total_this_warning}件 ({status_str})")
            
            # 濃霧注意報を特別表示
            fog_warnings = [k for k in all_warnings.keys() if '濃霧' in k]
            if fog_warnings:
                print(f"  🌫️  濃霧注意報状況:")
                for fog_warning in fog_warnings:
                    counts = all_warnings[fog_warning]
                    if counts['発表'] > 0:
                        print(f"    ✅ {fog_warning}: 発表中 ({counts['発表']}件)")
                    else:
                        print(f"    ❌ {fog_warning}: 発表なし")
            else:
                print(f"  🌫️  濃霧注意報: 検出されず")
            
        except Exception as e:
            print(f"  ❌ エラー: {str(e)}")

if __name__ == "__main__":
    decode_jma_warnings()