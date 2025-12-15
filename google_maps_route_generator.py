#!/usr/bin/env python3
"""
札幌市立高校訪問ルート - GoogleマップURL生成
"""

import urllib.parse

def generate_google_maps_route():
    """
    札幌市立高校の効率的訪問ルートのGoogleマップURLを生成
    """
    
    # 訪問順序（推奨北回りルート）
    locations = [
        "札幌市手稲区手稲本町4条2丁目2-2",  # スタート地点
        "札幌市北区新川5条14丁目1-1",        # 新川高校
        "札幌市中央区旭ヶ丘6丁目5-18",       # 旭丘高校
        "札幌市中央区北2条西11丁目",         # 大通高校
        "札幌市豊平区平岸5条18丁目1番2号",   # 平岸高校
        "札幌市清田区北野3条4丁目6-1",       # 清田高校
        "札幌市南区川沿3条2丁目1番1号",      # 藻岩高校
        "札幌市南区石山1条2丁目10-1"         # 啓北商業高校
    ]
    
    school_names = [
        "手稲スタート地点",
        "市立札幌新川高等学校",
        "市立札幌旭丘高等学校", 
        "市立札幌大通高等学校",
        "市立札幌平岸高等学校",
        "市立札幌清田高等学校",
        "市立札幌藻岩高等学校",
        "市立札幌啓北商業高等学校"
    ]
    
    print("=== 札幌市立高校訪問ルート - GoogleマップURL ===\n")
    
    # 1. 全ルートを一度に表示するURL
    origin = locations[0]
    destination = locations[-1]
    waypoints = locations[1:-1]  # 中間地点
    
    # URLエンコード
    origin_encoded = urllib.parse.quote(origin)
    destination_encoded = urllib.parse.quote(destination)
    waypoints_encoded = urllib.parse.quote('|'.join(waypoints))
    
    full_route_url = (
        f"https://www.google.com/maps/dir/"
        f"{origin_encoded}/"
        f"{destination_encoded}/"
        f"data=!3m1!4b1!4m20!4m19!1m5!1m1!1s0x0:0x0!2m2!1d0!2d0"
        f"!1m5!1m1!1s0x0:0x0!2m2!1d0!2d0"
        f"!2m1!2b1!3e0"
    )
    
    # より簡単な方法：検索ベースのURL
    search_url = "https://www.google.com/maps/dir/" + "/".join([urllib.parse.quote(loc) for loc in locations])
    
    print("【方法1: 全ルートを一度に表示】")
    print("以下のURLをブラウザで開いてください：")
    print(f"{search_url}")
    print()
    
    # 2. 各区間ごとのURL
    print("【方法2: 各区間ごとのルート】")
    print("より詳細な確認が必要な場合は、以下のURLを順番に開いてください：\n")
    
    for i in range(len(locations) - 1):
        start = locations[i]
        end = locations[i + 1]
        start_name = school_names[i]
        end_name = school_names[i + 1]
        
        segment_url = f"https://www.google.com/maps/dir/{urllib.parse.quote(start)}/{urllib.parse.quote(end)}"
        
        print(f"{i+1}. {start_name} → {end_name}")
        print(f"   {segment_url}")
        print()
    
    # 3. 各学校の個別URL
    print("【方法3: 各学校の個別位置確認】")
    print("各学校の詳細位置を確認したい場合：\n")
    
    for i, (location, name) in enumerate(zip(locations, school_names), 1):
        if i == 1:  # スタート地点はスキップ
            continue
        individual_url = f"https://www.google.com/maps/search/{urllib.parse.quote(location)}"
        print(f"{i-1}. {name}")
        print(f"   {individual_url}")
        print()
    
    # 4. モバイル用の短縮URL生成情報
    print("【モバイル用】")
    print("スマートフォンで使用する場合は、GoogleマップアプリでQRコードを読み取るか、")
    print("上記URLをメールで自分に送信してください。")
    print()
    
    # 5. 代替手段
    print("【代替手段】")
    print("もしURLが長すぎて開けない場合は、以下の手順をお試しください：")
    print("1. Googleマップを開く")
    print("2. 「ルート検索」をクリック")
    print("3. 以下の住所を順番に入力：")
    print()
    
    for i, (location, name) in enumerate(zip(locations, school_names)):
        if i == 0:
            print(f"   出発地: {location} ({name})")
        elif i == len(locations) - 1:
            print(f"   目的地: {location} ({name})")
        else:
            print(f"   経由地{i}: {location} ({name})")
    
    return search_url

def main():
    """メイン処理"""
    url = generate_google_maps_route()
    
    print("\n" + "="*60)
    print("【メインURL（コピーしてブラウザで開いてください）】")
    print(url)
    print("="*60)
    
    # ファイルにも保存
    with open('/home/fujinosuke/projects/sapporo_schools_route_urls.txt', 'w', encoding='utf-8') as f:
        f.write("札幌市立高校訪問ルート - GoogleマップURL\n")
        f.write("="*50 + "\n\n")
        f.write("メインURL:\n")
        f.write(url + "\n\n")
        f.write("使用方法:\n")
        f.write("1. 上記URLをコピーしてブラウザで開く\n")
        f.write("2. Googleマップアプリで開く\n")
        f.write("3. ルート検索で各住所を順番に入力\n")
    
    print("\nURLファイルを保存しました: /home/fujinosuke/projects/sapporo_schools_route_urls.txt")

if __name__ == "__main__":
    main()