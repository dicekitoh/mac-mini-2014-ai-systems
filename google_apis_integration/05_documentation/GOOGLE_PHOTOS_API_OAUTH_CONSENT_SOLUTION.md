# 🔧 Google Photos API OAuth同意画面設定ガイド

## 📋 問題確認
- **Photos Library API**: ✅ 有効化済み
- **認証トークン**: ✅ 4つのスコープで取得済み
- **接続エラー**: ❌ `Request had insufficient authentication scopes`

## 🔍 根本原因
**OAuth同意画面にPhotos Library APIスコープが未登録**

Google Cloud ConsoleでAPIは有効化されているが、OAuth同意画面でユーザーがPhotos APIスコープを承認する設定になっていない。

## 🛠️ 解決手順

### Step 1: OAuth同意画面アクセス
```
🌐 URL: https://console.cloud.google.com/apis/credentials/consent?project=civil-authority-462513-a9
```

### Step 2: アプリケーション編集
1. 「アプリを編集」ボタンをクリック
2. 基本設定を確認（変更不要）
3. 「保存して次へ」

### Step 3: スコープ追加（重要）
1. 「スコープを追加または削除」をクリック
2. 「機密でないスコープ」セクションで以下を追加:
   ```
   https://www.googleapis.com/auth/photoslibrary
   https://www.googleapis.com/auth/photoslibrary.readonly
   https://www.googleapis.com/auth/photoslibrary.sharing
   https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata
   ```
3. 「更新」をクリック
4. 「保存して次へ」

### Step 4: テストユーザー確認
1. 自分のGoogleアカウントがテストユーザーに追加されていることを確認
2. 未追加の場合は「テストユーザーを追加」で自分のメールアドレスを追加

### Step 5: 設定完了
1. 「概要に戻る」
2. 設定が保存されていることを確認

## 🔄 設定完了後の再認証

### 新しい認証トークン取得
```bash
# 古いトークンを削除
rm -f google_photos_token_*.pickle

# 新しい認証実行
python3 quick_auth_helper.py
```

### 接続テスト実行
```bash
# OAuth設定完了後のテスト
python3 -c "
import pickle
import requests

# 新しいトークンで接続テスト
with open('google_photos_token_*.pickle', 'rb') as f:
    creds = pickle.load(f)

headers = {'Authorization': f'Bearer {creds.token}'}
response = requests.get('https://photoslibrary.googleapis.com/v1/albums', headers=headers)

if response.status_code == 200:
    print('🎉 Google Photos API: 完全成功!')
    print(f'📸 アルバム数: {len(response.json().get(\"albums\", []))}')
else:
    print(f'❌ まだエラー: {response.status_code}')
"
```

## ⚡ 予想される成功結果

### OAuth設定完了後
```
🎉 Google Photos API authentication completed!
✅ Google Photos API connection test: SUCCESS

📊 Final Test Results:
✅ Albums API: SUCCESS - X albums
✅ Media Search: SUCCESS - Y items  
✅ API Client: SUCCESS - Z items

🎯 Success Rate: 3/3 tests passed
🎉 Google Photos API: FULLY CONNECTED!
```

## 💡 重要ポイント

1. **APIの有効化 ≠ OAuth同意画面設定**
2. **Photos Library APIスコープは手動追加が必要**
3. **設定完了後は必ず新しい認証トークン取得**
4. **テストユーザーとして自分を追加することを忘れずに**

## 📄 関連ファイル
- `quick_auth_helper.py` - 再認証ツール
- `google_photos_token_*.pickle` - 新認証トークン（設定後生成）

---
*作成者: Claude Code*  
*Google Photos API OAuth同意画面設定ガイド*  
*最終更新: 2025-12-13 14:20:00*