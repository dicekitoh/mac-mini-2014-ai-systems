# ルート最適化システム 使用ガイド

## 🔧 システム状態

### API接続状態
- **Google Maps APIキー**: ✅ 設定済み（永続的に保存）
- **環境変数**: `GOOGLE_MAPS_API_KEY` 
- **設定ファイル**: `/home/fujinosuke/google_maps_config.json`
- **利用可能API**: Geocoding, Distance Matrix, Places, Maps JavaScript

### 無料枠
- 月間 $200 相当（約28,500リクエスト）
- 現在のAPIキー: `***REMOVED***`

## 📝 基本的な使い方

### 1. Python内で使用
```python
from route_optimizer_tsp import GoogleMapsRouteOptimizer

# 最適化実行
optimizer = GoogleMapsRouteOptimizer()
result = optimizer.optimize_route([
    "住所1",
    "住所2", 
    "住所3"
])
```

### 2. 簡単実行スクリプト
```bash
# 新規作成した簡単実行ツール
python3 /home/fujinosuke/projects/easy_route_optimizer.py

# カスタム住所での実行例
python3 -c "
from easy_route_optimizer import optimize_my_route
addresses = ['札幌駅', '小樽駅', '千歳駅']
optimize_my_route(addresses)
"
```

### 3. テスト実行
```bash
# 6地点サンプル
python3 /home/fujinosuke/projects/route_optimizer_tsp.py

# 10地点ビジネステスト  
python3 /home/fujinosuke/projects/test_10_locations.py
```

## 🎯 実用例

### 配送ルート最適化
```python
delivery_addresses = [
    "配送センター 札幌市白石区",
    "〒001-0001 札幌市北区北1条",
    "〒002-0002 札幌市北区北2条", 
    # ... 配送先住所
]

result = optimizer.optimize_route(
    addresses=delivery_addresses,
    start_address="配送センター",
    algorithm='auto'  # 地点数に応じて自動選択
)
```

### 営業訪問ルート
```python
from easy_route_optimizer import optimize_my_route

clients = [
    "株式会社A 札幌市中央区",
    "株式会社B 札幌市北区",
    "株式会社C 札幌市東区"
]

# 結果をファイルに保存
optimize_my_route(clients, save_result=True)
```

## 🔍 利用可能な機能

### アルゴリズム選択
- `'auto'`: 自動選択（推奨）
- `'brute_force'`: 総当たり法（8地点以下で最適解）
- `'nearest_neighbor'`: 最近傍法（高速）
- `'genetic'`: 遺伝的アルゴリズム（10-20地点向け）

### 取得できる情報
- `total_distance_km`: 総走行距離
- `total_duration_hours`: 総所要時間
- `optimized_route`: 最適訪問順序
- `route_segments`: 区間別詳細
- `google_maps_url`: 確認用URL

## ⚠️ 注意事項

1. **APIキーの管理**
   - 既に設定済みなので追加設定不要
   - 他人と共有しない

2. **利用制限**
   - 月28,500リクエストまで無料
   - キャッシュ機能により同じルートは高速化

3. **住所の書き方**
   - 日本語OK: "札幌駅"
   - 郵便番号OK: "〒060-0001"
   - ランドマークOK: "新千歳空港"

## 🆘 トラブルシューティング

### APIキーエラーの場合
```bash
# 環境変数確認
echo $GOOGLE_MAPS_API_KEY

# 再設定が必要な場合
source ~/.bashrc
```

### モジュールが見つからない場合
```bash
# パスを追加
export PYTHONPATH=$PYTHONPATH:/home/fujinosuke/projects
```

## 📞 サポート

何か問題があれば、エラーメッセージと一緒にお知らせください。
すぐに対応方法をご案内します。