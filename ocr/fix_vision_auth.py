#!/usr/bin/env python3
"""
Google Vision API 認証修正ツール
既存の認証にVision APIスコープを追加
"""

import os
import json
import pickle
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def check_current_auth():
    """現在の認証状況確認"""
    token_file = '/home/fujinosuke/google_contacts/token.pickle'
    
    if not os.path.exists(token_file):
        print("❌ 認証トークンファイルが見つかりません")
        return None
    
    try:
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        print("📋 現在の認証情報:")
        print(f"  有効: {creds.valid}")
        print(f"  期限切れ: {creds.expired}")
        print(f"  スコープ: {getattr(creds, 'scopes', 'N/A')}")
        
        if creds.expired and creds.refresh_token:
            print("🔄 トークン更新中...")
            creds.refresh(Request())
            
            # 更新されたトークンを保存
            with open(token_file, 'wb') as f:
                pickle.dump(creds, f)
            
            print("✅ トークン更新完了")
        
        return creds
        
    except Exception as e:
        print(f"❌ 認証確認エラー: {e}")
        return None

def test_vision_api_with_current_auth():
    """現在の認証でVision APIテスト"""
    creds = check_current_auth()
    if not creds:
        return False
    
    try:
        print("🔍 Vision APIテスト実行...")
        
        url = "https://vision.googleapis.com/v1/images:annotate"
        headers = {
            'Authorization': f'Bearer {creds.token}',
            'Content-Type': 'application/json'
        }
        
        # テスト画像（1x1白色PNG）
        test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        request_body = {
            'requests': [{
                'image': {'content': test_image},
                'features': [{'type': 'TEXT_DETECTION', 'maxResults': 1}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=request_body, timeout=30)
        
        print(f"📊 レスポンス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Vision API アクセス成功!")
            print(f"📄 結果: {json.dumps(result, indent=2)[:300]}...")
            return True
        else:
            print(f"❌ Vision API アクセス失敗")
            print(f"📄 エラー: {response.text}")
            
            # 403エラーの場合、スコープ不足の可能性
            if response.status_code == 403:
                error_data = response.json()
                if 'insufficient authentication scopes' in response.text.lower():
                    print("⚠️ 認証スコープが不足しています")
                    print("💡 解決方法: Google Cloud Consoleで適切なAPIアクセス権限を設定")
            
            return False
            
    except Exception as e:
        print(f"❌ Vision APIテストエラー: {e}")
        return False

def test_existing_image():
    """既存の受信画像でOCRテスト"""
    image_path = '/home/fujinosuke/telegram_images/telegram_image_6859639046_20250615_200032.jpg'
    
    if not os.path.exists(image_path):
        print(f"❌ 画像ファイルが見つかりません: {image_path}")
        return False
    
    creds = check_current_auth()
    if not creds:
        return False
    
    try:
        print(f"🔍 実画像OCRテスト: {os.path.basename(image_path)}")
        
        # 画像読み込み
        with open(image_path, 'rb') as f:
            image_content = f.read()
        
        import base64
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        url = "https://vision.googleapis.com/v1/images:annotate"
        headers = {
            'Authorization': f'Bearer {creds.token}',
            'Content-Type': 'application/json'
        }
        
        request_body = {
            'requests': [{
                'image': {'content': image_base64},
                'features': [
                    {'type': 'TEXT_DETECTION', 'maxResults': 50},
                    {'type': 'DOCUMENT_TEXT_DETECTION', 'maxResults': 50}
                ]
            }]
        }
        
        print("📡 Vision API呼び出し中...")
        response = requests.post(url, headers=headers, json=request_body, timeout=30)
        
        print(f"📊 レスポンス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # OCR結果解析
            if 'responses' in result and result['responses']:
                response_data = result['responses'][0]
                
                if 'textAnnotations' in response_data:
                    text_annotations = response_data['textAnnotations']
                    
                    if text_annotations:
                        full_text = text_annotations[0].get('description', '')
                        
                        print("🎉 OCR成功!")
                        print(f"📏 検出文字数: {len(full_text)}")
                        print(f"🔤 注釈数: {len(text_annotations)}")
                        print("\n📝 認識テキスト:")
                        print("-" * 40)
                        print(full_text[:500])
                        if len(full_text) > 500:
                            print(f"... (全{len(full_text)}文字)")
                        print("-" * 40)
                        
                        # 結果をファイルに保存
                        result_file = '/home/fujinosuke/ocr_test_result.json'
                        with open(result_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                'success': True,
                                'full_text': full_text,
                                'text_length': len(full_text),
                                'annotations_count': len(text_annotations),
                                'image_file': image_path
                            }, f, ensure_ascii=False, indent=2)
                        
                        print(f"📁 結果保存: {result_file}")
                        return True
                    else:
                        print("⚠️ テキストが検出されませんでした")
                else:
                    print("⚠️ テキスト注釈が見つかりません")
            else:
                print("⚠️ レスポンスデータが空です")
            
            return False
        else:
            print(f"❌ OCR処理失敗: {response.status_code}")
            print(f"📄 エラー: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OCRテストエラー: {e}")
        return False

def main():
    print("=" * 60)
    print("Google Vision API 認証修正・テストツール")
    print("=" * 60)
    
    # 1. 現在の認証確認
    print("🔍 Step 1: 現在の認証確認")
    if not check_current_auth():
        print("❌ 認証設定を修正してください")
        return
    
    # 2. Vision API基本テスト
    print("\n🔍 Step 2: Vision API基本テスト")
    if test_vision_api_with_current_auth():
        print("✅ Vision API認証成功")
        
        # 3. 実画像でOCRテスト
        print("\n🔍 Step 3: 受信画像OCRテスト")
        if test_existing_image():
            print("\n🎉 OCR処理完全成功!")
            print("📊 MacMini2014でのOCR精度確認が可能です")
        else:
            print("\n⚠️ 実画像OCRで問題が発生")
    else:
        print("❌ Vision API認証に問題があります")
        print("💡 Google Cloud Consoleで以下を確認してください:")
        print("  1. Vision APIが有効になっているか")
        print("  2. 適切なAPI権限が設定されているか")
        print("  3. 課金設定が有効になっているか")

if __name__ == "__main__":
    main()