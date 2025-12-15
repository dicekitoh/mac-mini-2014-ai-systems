#!/usr/bin/env python3
"""
Google Photos 枚数調査システム
Photos Picker API + Drive API による写真総数分析
"""

import pickle
import requests
from googleapiclient.discovery import build
from datetime import datetime
import json

def test_photos_picker_api_limitations():
    """Photos Picker API の制限テスト"""
    print('🔍 Photos Picker API 機能制限分析')
    print('=' * 50)
    
    # 実際の成功データ分析
    try:
        with open('/home/rootmax/data/01_json-configs/system-configs/photo_picker_media_success.json', 'r') as f:
            picker_data = json.load(f)
        
        photo_count = len(picker_data.get('mediaItems', []))
        print(f'📊 Picker API取得実績: {photo_count}枚')
        
        if photo_count > 0:
            sample_photo = picker_data['mediaItems'][0]
            print(f'📷 サンプル: {sample_photo.get("mediaFile", {}).get("filename", "Unknown")}')
            print(f'📅 撮影日: {sample_photo.get("createTime", "Unknown")[:10]}')
    except Exception as e:
        print(f'❌ Picker APIデータ読み込みエラー: {e}')
    
    print('\n💡 Photos Picker API の本質:')
    print('❌ 全写真の自動カウント: 不可能')
    print('❌ バックグラウンド一覧取得: 不可能') 
    print('✅ ユーザー選択写真: 完璧に動作')
    print('✅ 高品質ダウンロード: 完璧に動作')
    
    return False  # 写真総数取得は不可能

def test_drive_api_photo_count():
    """Drive API で写真枚数調査"""
    print('\n🧪 Drive API 写真枚数調査')
    print('=' * 50)
    
    # 既存トークン読み込み
    token_files = [
        '/home/rootmax/03_google_19_apis_connection_system/google_api_complete_token.pkl',
        '/home/rootmax/google_api_complete_token.pkl'
    ]
    
    creds = None
    for token_file in token_files:
        try:
            with open(token_file, 'rb') as f:
                creds = pickle.load(f)
                print(f'✅ 認証トークン読み込み: {token_file}')
                break
        except:
            continue
    
    if not creds:
        print('❌ 利用可能な認証トークンが見つかりません')
        return 0
    
    try:
        # Drive API で画像ファイル検索
        service = build('drive', 'v3', credentials=creds)
        
        print('🔍 Google Drive内画像ファイル検索中...')
        
        # 画像ファイル検索クエリ
        query = "mimeType contains 'image/'"
        
        results = service.files().list(
            q=query,
            pageSize=1000,
            fields="nextPageToken, files(id, name, size, createdTime, mimeType)"
        ).execute()
        
        items = results.get('files', [])
        total_count = len(items)
        
        print(f'📊 Google Drive内画像ファイル: {total_count}枚')
        
        if total_count > 0:
            # ファイル種別分析
            mime_types = {}
            total_size = 0
            
            for item in items[:10]:  # 最初の10件を詳細表示
                mime_type = item.get('mimeType', 'unknown')
                mime_types[mime_type] = mime_types.get(mime_type, 0) + 1
                
                size = int(item.get('size', 0)) if item.get('size') else 0
                total_size += size
                
                if len(mime_types) <= 5:  # 最初の5件のみ詳細表示
                    print(f'   📷 {item.get("name", "Unknown")[:30]} - {mime_type}')
            
            print(f'📊 ファイル種別分布:')
            for mime_type, count in list(mime_types.items())[:5]:
                print(f'   {mime_type}: {count}枚')
            
            print(f'💾 総容量: {total_size / (1024*1024):.2f} MB')
            
        return total_count
        
    except Exception as e:
        print(f'❌ Drive API エラー: {e}')
        return 0

def analyze_alternative_approaches():
    """代替アプローチの分析"""
    print('\n🔄 写真枚数調査の代替アプローチ')
    print('=' * 50)
    
    approaches = {
        'Photos Picker API': {
            'status': '❌ 総数カウント不可',
            'reason': 'ユーザー手動選択のみ',
            'usecase': 'ユーザー選択写真の高品質取得'
        },
        'Drive API': {
            'status': '✅ 一部可能',
            'reason': 'Drive保存画像のみ',
            'usecase': 'Drive内画像ファイル数'
        },
        'Gmail API': {
            'status': '✅ 可能',
            'reason': 'Gmail添付画像',
            'usecase': 'メール添付写真数'
        },
        'Google Takeout': {
            'status': '🔧 手動',
            'reason': 'データエクスポート',
            'usecase': '全データ一括取得'
        }
    }
    
    for approach, details in approaches.items():
        print(f'{details["status"]} {approach}')
        print(f'   理由: {details["reason"]}')
        print(f'   用途: {details["usecase"]}')
        print()
    
    print('💡 結論:')
    print('Google Photos内の写真総数を完全に取得する')
    print('APIベースの方法は現在存在しません。')
    print()
    print('📋 推奨アプローチ:')
    print('1. Drive API: Drive保存写真数')
    print('2. Photos Picker: ユーザー選択写真の詳細分析')
    print('3. Gmail API: 添付写真の統計')

def main():
    """メイン実行"""
    print('🎯 Google Photos 枚数調査システム')
    print('=' * 60)
    print(f'実行日時: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # Photos Picker API制限確認
    picker_possible = test_photos_picker_api_limitations()
    
    # Drive API写真調査
    drive_count = test_drive_api_photo_count()
    
    # 代替アプローチ分析
    analyze_alternative_approaches()
    
    print('\n🏆 最終結果:')
    print('=' * 60)
    print(f'Photos Picker API: 写真総数取得は不可能')
    print(f'Drive API画像ファイル: {drive_count}枚検出')
    print(f'推奨: Photos Picker APIをユーザー選択写真用に活用')
    
    return {
        'photos_picker_total_count': False,
        'drive_api_image_count': drive_count,
        'recommendation': 'Use Photos Picker for user-selected photos only'
    }

if __name__ == "__main__":
    result = main()
    print(f'\n📊 分析完了: {result}')