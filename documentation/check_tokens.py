#\!/usr/bin/env python3
import pickle
import os
from datetime import datetime

print("📊 現在のトークン状況確認")
print("=" * 40)

token_files = [
    "unified_google_token.pickle",
    "google_tasks_new.pickle", 
    "token_drive.pickle",
    "google_docs_token.pickle",
    "token_persistent.pickle"
]

valid_tokens = []

for token_file in token_files:
    if os.path.exists(token_file):
        try:
            with open(token_file, "rb") as f:
                creds = pickle.load(f)
            
            print(f"\n📋 {token_file}:")
            print(f"   有効性: {Valid if creds.valid else Invalid}")
            
            if hasattr(creds, "scopes") and creds.scopes:
                print(f"   スコープ数: {len(creds.scopes)}")
                scopes = [scope.split("/")[-1] for scope in creds.scopes]
                scope_preview = ", ".join(scopes[:3])
                if len(scopes) > 3:
                    scope_preview += "..."
                print(f"   スコープ: {scope_preview}")
                
                if creds.valid:
                    valid_tokens.append((token_file, len(creds.scopes), creds))
            else:
                print(f"   スコープ: なし")
        except Exception as e:
            print(f"   エラー: {e}")
    else:
        print(f"\n❌ {token_file}: ファイルなし")

print(f"\n📈 有効なトークン数: {len(valid_tokens)}")
if valid_tokens:
    best = max(valid_tokens, key=lambda x: x[1])
    print(f"🎯 最多スコープトークン: {best[0]} ({best[1]}スコープ)")
    
    # 最適なトークンを統一システムにコピー
    import shutil
    if best[0] \!= "unified_google_token.pickle":
        backup_file = f"unified_google_token.pickle.backup_{datetime.now().strftime(%Y%m%d_%H%M%S)}"
        if os.path.exists("unified_google_token.pickle"):
            shutil.copy("unified_google_token.pickle", backup_file)
            print(f"💾 バックアップ作成: {backup_file}")
        
        shutil.copy(best[0], "unified_google_token.pickle")
        print(f"✅ 最適トークンを統一システムに適用")
    else:
        print("✅ 統一システムが既に最適です")
        
    # Drive権限確認
    best_creds = best[2]
    has_drive = any("drive" in scope for scope in best_creds.scopes)
    print(f"📁 Drive権限: {あり if has_drive else なし}")
    
else:
    print("❌ 有効なトークンが見つかりません")
