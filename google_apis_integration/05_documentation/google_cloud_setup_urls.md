# 🔧 Google Cloud Console セットアップURL集

## 📋 必要な作業手順とURL

### 1. Google Cloud Console メインページ
**URL**: https://console.cloud.google.com/

**作業内容**:
- Googleアカウントでログイン
- 新規プロジェクト作成または既存プロジェクト選択

---

### 2. 新規プロジェクト作成
**URL**: https://console.cloud.google.com/projectcreate

**設定内容**:
- プロジェクト名: `nissan-distance-calculator` （推奨）
- 組織: なし（個人使用の場合）
- 場所: なし

---

### 3. 課金設定（最重要）
**URL**: https://console.cloud.google.com/billing

**必須作業**:
- 課金アカウントの作成
- クレジットカード情報登録
- 課金の有効化

⚠️ **重要**: 課金設定なしではAPIが動作しません

---

### 4. 必要なAPI有効化

#### 4-1. Geocoding API
**URL**: https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com

**作業**: 「有効にする」ボタンをクリック

#### 4-2. Distance Matrix API  
**URL**: https://console.cloud.google.com/apis/library/distance-matrix-backend.googleapis.com

**作業**: 「有効にする」ボタンをクリック

#### 4-3. Maps JavaScript API
**URL**: https://console.cloud.google.com/apis/library/maps-backend.googleapis.com

**作業**: 「有効にする」ボタンをクリック

---

### 5. APIキー作成
**URL**: https://console.cloud.google.com/apis/credentials

**作業手順**:
1. 「認証情報を作成」をクリック
2. 「APIキー」を選択
3. 生成されたAPIキーをコピー
4. （推奨）APIキーの制限を設定

---

### 6. APIキー制限設定（推奨）
**URL**: https://console.cloud.google.com/apis/credentials

**制限設定**:
- アプリケーション制限: なし
- API制限: 
  - Geocoding API
  - Distance Matrix API
  - Maps JavaScript API

---

### 7. 課金とクォータ監視
**URL**: https://console.cloud.google.com/apis/quotas

**確認項目**:
- Geocoding API クォータ状況
- Distance Matrix API クォータ状況
- 使用量アラート設定

---

### 8. 使用量とコスト監視
**URL**: https://console.cloud.google.com/billing/reports

**設定推奨**:
- 予算アラート作成
- 日次使用量レポート有効化

---

## 🔑 APIキー取得後の設定

```bash
# 環境変数設定
export GOOGLE_MAPS_API_KEY='ここに取得したAPIキーを入力'

# 永続化（推奨）
echo 'export GOOGLE_MAPS_API_KEY="ここに取得したAPIキーを入力"' >> ~/.bashrc
source ~/.bashrc
```

## 📊 コスト見積もり

| API | 使用量 | 料金 |
|-----|--------|------|
| Geocoding API | 133リクエスト | 約$0.67 |
| Distance Matrix API | 132リクエスト | 約$0.66-1.32 |
| **合計** | **265リクエスト** | **約$1.33-1.99** |

毎月$200の無料クレジットがあるため、実質無料で実行可能です。

## ✅ 設定完了確認

全て設定完了後、以下のコマンドでAPIが動作するか確認:

```bash
curl "https://maps.googleapis.com/maps/api/geocode/json?address=東京駅&key=YOUR_API_KEY"
```

正常に住所データが返ってくれば設定完了です。

---

**🚀 設定完了後、APIキーを教えていただければ、すぐに実際のデータで距離計算を実行できます！**