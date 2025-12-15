# Google Maps Timeline データ取得ガイド

## 概要
GoogleマップのタイムラインAPIは存在しないため、データをエクスポートして処理する方法を説明します。

## データ取得方法

### 1. スマートフォンアプリからエクスポート（推奨）
1. Googleマップアプリを開く
2. プロフィール写真をタップ
3. 「タイムライン」を選択
4. 右上の「...」メニューから「設定」
5. 「タイムラインデータをエクスポート」を選択
6. JSON形式でダウンロード

### 2. Google Takeout
1. https://takeout.google.com/ にアクセス
2. 「選択をすべて解除」をクリック
3. 「ロケーション履歴」を選択
4. 「次のステップ」→「エクスポートを作成」
5. JSON形式でダウンロード

## 使用方法

### 基本的な使用例
```bash
# 全データを表示
python3 google_timeline_processor.py timeline.json

# 期間指定
python3 google_timeline_processor.py timeline.json --start-date 2024-01-01 --end-date 2024-12-31

# CSV出力
python3 google_timeline_processor.py timeline.json --output-csv visits.csv
```

### Python プログラム内での使用
```python
from google_timeline_processor import GoogleTimelineProcessor

# Timeline処理
processor = GoogleTimelineProcessor('timeline.json')

# 2024年の訪問先を取得
visits = processor.get_place_visits('2024-01-01', '2024-12-31')

# 訪問先情報を表示
for visit in visits:
    print(f"場所: {visit['place_name']}")
    print(f"日時: {visit['timestamp']}")
    print(f"座標: {visit['coordinates']}")
    print(f"滞在時間: {visit['duration_minutes']}分")
```

## データ形式

### 取得できる情報
- 訪問日時
- 場所名
- 住所
- 座標（緯度・経度）
- 滞在時間

### 出力例
```json
{
  "timestamp": "2024-06-15T10:30:00+09:00",
  "place_name": "○○駅",
  "address": "札幌市中央区...",
  "coordinates": {
    "lat": 43.0642,
    "lng": 141.3469
  },
  "duration_minutes": 15
}
```

## 注意事項

### プライバシーとセキュリティ
- 位置情報は非常にセンシティブなデータです
- ローカルでの処理を推奨
- 必要に応じてデータを定期的に削除

### データの制限
- 公式APIが存在しないため、手動エクスポートが必要
- リアルタイム取得は不可能
- データ形式は予告なく変更される可能性

### 2024年の変更点
- 12月2日以降、Web版タイムラインは廃止
- データはデバイス内に保存（クラウド保存廃止）
- 新しいエクスポート形式に対応

## トラブルシューティング

### JSONファイルが読み込めない場合
1. ファイルが正しいJSON形式かチェック
2. 文字エンコーディング（UTF-8）を確認
3. ファイルサイズが大きすぎる場合は分割

### データが見つからない場合
1. 位置情報が有効になっているか確認
2. タイムライン機能が有効になっているか確認
3. 対象期間にデータが存在するか確認

## その他のツール

### オープンソースプロジェクト
- [google-maps-timeline-viewer](https://github.com/kurupted/google-maps-timeline-viewer)
- [TimelineExtractor](https://github.com/Stadly/TimelineExtractor)
- [GoogleTimelineMapper](https://github.com/ryangriggs/GoogleTimelineMapper)

これらのツールも併用することで、より詳細な分析が可能です。