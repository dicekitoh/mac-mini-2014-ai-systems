#!/usr/bin/env python3
"""
Google API認証更新システム
期限切れのトークンを自動更新
"""

import pickle
import os
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

print("🔄 Google API認証更新システム")
print("=" * 50)

# 更新対象のトークンファイル
token_files = [
    "/home/fujinosuke/projects/google_auth/unified_google_token.pickle",
    "/home/fujinosuke/google_contacts/token.pickle",
    "/home/fujinosuke/projects/google_auth/token_drive.pickle",
    "/home/fujinosuke/projects/google_auth/google_docs_token.pickle",
    "/home/fujinosuke/projects/google_auth/token_persistent.pickle",
    "/home/fujinosuke/google/token_contacts_real.pickle",
    "/home/fujinosuke/google_contacts/contact_manager_v2_bot_github/token.pickle"
]

refreshed_count = 0
error_count = 0

for token_path in token_files:
    token_name = os.path.basename(token_path)
    print(f"\n🔐 {token_name}")
    
    if not os.path.exists(token_path):
        print(f"   ❌ ファイルが存在しません")
        continue
    
    try:
        # トークン読み込み
        with open(token_path, "rb") as f:
            creds = pickle.load(f)
        
        # 現在の状態確認
        is_valid = creds.valid if hasattr(creds, 'valid') else False
        is_expired = creds.expired if hasattr(creds, 'expired') else True
        has_refresh = hasattr(creds, 'refresh_token') and creds.refresh_token
        
        print(f"   有効性: {'✅' if is_valid else '❌'}")
        print(f"   期限: {'✅' if not is_expired else '❌ 期限切れ'}")
        print(f"   更新トークン: {'✅' if has_refresh else '❌'}")
        
        # 更新が必要で可能な場合
        if not is_valid and has_refresh:
            print(f"   🔄 更新を試行中...")
            
            # バックアップ作成
            backup_path = f"{token_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_path, "wb") as f:
                pickle.dump(creds, f)
            print(f"   💾 バックアップ: {os.path.basename(backup_path)}")
            
            # トークン更新
            try:
                creds.refresh(Request())
                
                # 更新されたトークンを保存
                with open(token_path, "wb") as f:
                    pickle.dump(creds, f)
                
                print(f"   ✅ 更新成功!")
                refreshed_count += 1
                
            except Exception as refresh_error:
                print(f"   ❌ 更新失敗: {str(refresh_error)[:50]}...")
                error_count += 1
                
        elif is_valid:
            print(f"   ✅ 更新不要（既に有効）")
        else:
            print(f"   ⚠️  更新不可（更新トークンなし）")
            error_count += 1
            
    except Exception as e:
        print(f"   ❌ 処理エラー: {str(e)[:50]}...")
        error_count += 1

# 結果サマリー
print(f"\n" + "=" * 50)
print(f"📊 更新結果サマリー")
print(f"=" * 50)
print(f"✅ 更新成功: {refreshed_count}件")
print(f"❌ エラー: {error_count}件")
print(f"📁 処理対象: {len(token_files)}件")

if refreshed_count > 0:
    print(f"\n🎉 {refreshed_count}個のトークンが正常に更新されました")
else:
    print(f"\n⚠️  更新されたトークンはありません")

print(f"\n🔄 処理完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")