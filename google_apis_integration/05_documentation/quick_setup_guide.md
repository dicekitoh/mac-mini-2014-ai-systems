# 🗺️ Google Maps API実用版セットアップガイド

## 📋 必要な準備

### 1. Google Cloud Console セットアップ

1. **Google Cloud Console** にアクセス
   - https://console.cloud.google.com/

2. **新規プロジェクト作成**
   - 「プロジェクトの選択」→「新しいプロジェクト」
   - プロジェクト名: `nissan-distance-calculator`（任意）

3. **必要なAPI有効化**
   ```
   - Maps JavaScript API
   - Geocoding API  
   - Distance Matrix API
   ```
   ナビゲーション: APIとサービス > ライブラリ

4. **APIキー作成**
   - APIとサービス > 認証情報 
   - 「認証情報を作成」> 「APIキー」
   - 生成されたAPIキーをコピーして保存

5. **課金設定（重要！）**
   - 課金 > 課金アカウントを作成
   - クレジットカード登録必須
   - 毎月$200の無料クレジットあり

## 💰 コスト見積もり

### 今回の計算（132店舗）でのAPI使用量:
- **Geocoding API**: 133リクエスト（基点1 + ディーラー132）
- **Distance Matrix API**: 132リクエスト
- **合計**: 約265リクエスト
- **推定コスト**: 約$1.5-2.0

### API料金（2024年版）:
- Geocoding API: $5/1,000リクエスト
- Distance Matrix API: $5-10/1,000リクエスト（交通手段によって異なる）

## 🚀 実行手順

### 1. 環境設定
```bash
# APIキー設定
export GOOGLE_MAPS_API_KEY='your_actual_api_key_here'

# 仮想環境確認
source venv/bin/activate
```

### 2. テスト実行（推奨）
```bash
# セットアップ確認
python3 setup_maps_api.py

# または直接テスト
python3 -c "
import googlemaps
client = googlemaps.Client(key='your_api_key')
result = client.geocode('東京駅')
print('✅ API動作確認OK' if result else '❌ API動作不良')
"
```

### 3. 本実行
```bash
python3 real_nissan_distance_calculator.py
```

## ⏱️ 実行時間とパフォーマンス

### 予想実行時間:
- **132店舗**: 約5-8分（APIレート制限のため1秒間隔で実行）
- **プログレス表示**: リアルタイム進捗確認可能
- **中断・再開**: 可能（キャッシュ機能搭載）

### 最適化機能:
- **キャッシュシステム**: 重複計算防止
- **レート制限**: API制限遵守（50req/分）
- **エラーハンドリング**: ネットワーク障害対応
- **複数形式出力**: CSV/JSON/テキストレポート

## 📊 出力結果

### 生成ファイル:
1. **詳細CSV**: `real_nissan_distance_YYYYMMDD_HHMMSS.csv`
2. **JSON結果**: `real_nissan_distance_YYYYMMDD_HHMMSS.json`  
3. **サマリー**: `real_nissan_distance_YYYYMMDD_HHMMSS_summary.txt`

### 結果内容:
- 基点からの距離（km）
- 所要時間（分）
- 交通ルート詳細
- 座標情報
- 住所正規化結果
- 最寄り店舗ランキング
- 統計データ（平均・中央値等）

## ⚠️ 注意事項

### APIキー管理:
- **絶対にGitにコミットしない**
- 環境変数またはローカルファイルで管理
- 不要になったらAPIキーを削除

### コスト管理:
- Google Cloud Console で使用量監視
- 予算アラート設定推奨
- テスト実行で料金確認

### エラー対策:
- ネットワーク接続確認
- APIキー権限確認
- 課金状態確認

## 🔧 トラブルシューティング

### よくあるエラー:

1. **"API key not valid"**
   ```
   → APIキーの確認
   → API有効化状況確認
   ```

2. **"REQUEST_DENIED"**
   ```
   → 課金設定確認
   → API制限設定確認
   ```

3. **"OVER_QUERY_LIMIT"**
   ```
   → 1秒間隔で再実行（自動実装済み）
   → APIプランのアップグレード検討
   ```

### デバッグコマンド:
```bash
# API状態確認
curl "https://maps.googleapis.com/maps/api/geocode/json?address=東京駅&key=YOUR_API_KEY"

# ログ確認
python3 real_nissan_distance_calculator.py 2>&1 | tee debug.log
```

## ✅ 実行準備チェックリスト

- [ ] Google Cloud Project作成済み
- [ ] Maps JavaScript API有効化済み
- [ ] Geocoding API有効化済み
- [ ] Distance Matrix API有効化済み
- [ ] APIキー作成済み
- [ ] 課金設定完了済み
- [ ] GOOGLE_MAPS_API_KEY環境変数設定済み
- [ ] CSVファイルパス確認済み
- [ ] 実行時間確保（5-10分）

---

**🚀 準備完了後、`python3 real_nissan_distance_calculator.py` で実行開始！**