# Google Maps API 設定ガイド

## Google Cloud Console での API キー取得

### 1. Google Cloud Console にアクセス
https://console.cloud.google.com/

### 2. 新しいプロジェクト作成
- プロジェクト名: 「Route Optimizer」
- 組織: 個人用

### 3. 必要なAPI有効化
以下のAPIを有効にしてください：
- Maps JavaScript API
- Geocoding API
- Distance Matrix API
- Places API

### 4. 認証情報（API キー）作成
1. 「認証情報」→「認証情報を作成」→「API キー」
2. 作成されたAPI キーをコピー
3. セキュリティのため制限を設定：
   - IP アドレス制限
   - API 制限（上記4つのAPIのみ許可）

### 5. 請求アカウント設定
⚠️ **重要**: 無料枠（月$200相当）を利用するためには請求アカウントの設定が必要
- クレジットカード情報の登録が必要
- 月28,500回まで無料利用可能

## API キーの保存

### 方法1: 環境変数
```bash
export GOOGLE_MAPS_API_KEY="YOUR_API_KEY"
```

### 方法2: 設定ファイル作成
ファイル: `/home/fujinosuke/google_maps_config.json`
```json
{
  "google_maps_api_key": "YOUR_API_KEY"
}
```

### 方法3: システム設定に追加
```bash
echo 'export GOOGLE_MAPS_API_KEY="YOUR_API_KEY"' >> ~/.bashrc
source ~/.bashrc
```

## 無料枠での利用限度

### 月間無料枠
- **$200相当のクレジット**
- **Geocoding API**: 40,000リクエスト/月
- **Distance Matrix API**: 40,000要素/月  
- **Maps JavaScript API**: 28,500読み込み/月

### 1日あたりの目安
- Geocoding: 約1,300リクエスト/日
- Distance Matrix: 約1,300要素/日
- 通常利用であれば無料枠内で十分

## セキュリティ設定

### API キー制限（推奨）
1. **IP制限**: サーバーIPのみ許可
2. **API制限**: 必要なAPIのみ許可
3. **リファラー制限**: 特定のドメインのみ許可

### 監視設定
- 使用量アラートを設定
- 予算制限を設定（$10/月など）
- 異常なアクセスの監視

## トラブルシューティング

### REQUEST_DENIED エラー
- API キーが正しく設定されていない
- 請求アカウントが未設定
- 必要なAPIが有効化されていない
- IP制限にかかっている

### OVER_QUERY_LIMIT エラー  
- 1日の利用限度を超過
- リクエスト頻度が高すぎる
- 請求アカウントの問題

## 次のステップ

1. Google Cloud Console でプロジェクト作成
2. 請求アカウント設定（クレジットカード登録）  
3. 必要なAPI有効化
4. API キー作成・制限設定
5. ローカル環境にAPI キー保存
6. ルート最適化システムでテスト実行

## API キー取得後の設定例

```bash
# 環境変数設定
export GOOGLE_MAPS_API_KEY="AIzaSyExample123ABC"

# 設定ファイル作成
echo '{"google_maps_api_key": "AIzaSyExample123ABC"}' > /home/fujinosuke/google_maps_config.json

# テスト実行
python3 /home/fujinosuke/projects/route_optimizer_tsp.py
```