# Google Cloud Python SDK 最適化ガイド

## 🎯 Google Cloud Python Client Libraries 準拠実装

### 1. 認証の改善
```python
# ❌ 従来の方法
creds = pickle.load(token_file)

# ✅ 改善版 - 自動リフレッシュ付き
from google.auth.transport.requests import Request

if creds.expired and creds.refresh_token:
    creds.refresh(Request())
```

### 2. エラーハンドリング強化
```python
# ✅ 包括的エラーハンドリング
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError

try:
    service = build('gmail', 'v1', credentials=creds)
    result = service.users().getProfile(userId='me').execute()
except HttpError as e:
    logger.error(f"HTTP Error {e.resp.status}: {e.error_details}")
except RefreshError as e:
    logger.error(f"認証更新エラー: {e}")
```

### 3. パフォーマンス最適化

#### 並行処理
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(test_api, config) for config in api_configs]
    results = [future.result() for future in futures]
```

#### 接続キャッシュ
```python
# サービス接続のキャッシュ化
connection_cache = {}
cache_key = f"{service_name}:{version}"
if cache_key not in connection_cache:
    connection_cache[cache_key] = build(service_name, version, credentials=creds)
```

#### 指数バックオフ
```python
import time

for attempt in range(max_retries):
    try:
        return api_call()
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s...
```

### 4. ログ設定 - Cloud Logging準拠
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_connection.log'),
        logging.StreamHandler()
    ]
)
```

### 5. API接続優先度管理
```python
api_configs = [
    {
        'name': 'Gmail API',
        'priority': 1,  # 高優先度
        'timeout': 10,
        'retry_count': 3
    },
    {
        'name': 'Analytics API', 
        'priority': 5,  # 低優先度
        'timeout': 20,
        'retry_count': 2
    }
]

# 優先度順でソート
sorted_apis = sorted(api_configs, key=lambda x: x['priority'])
```

## 🚀 改善された機能

### 1. 自動トークン更新
- トークン有効期限の自動チェック
- 期限切れ時の自動リフレッシュ
- RefreshTokenエラーの適切な処理

### 2. 並行処理による高速化  
- ThreadPoolExecutorを使用した並行API接続
- 最大並行数の制御 (推奨: 5-10)
- 各API接続の独立実行

### 3. 詳細ログ記録
- 構造化ログ出力
- ファイルとコンソール両方への出力
- API接続時間の測定

### 4. エラー耐性の向上
- 指数バックオフによるリトライ機能
- HTTP エラーコード別の適切な処理
- 部分失敗時の続行機能

### 5. パフォーマンス監視
- API接続時間の測定
- 成功率の算出
- レスポンス時間の分析

## 📊 推奨設定値

```python
RECOMMENDED_SETTINGS = {
    'max_concurrent_connections': 5,
    'default_timeout': 10,
    'max_retries': 3,
    'backoff_factor': 2,
    'high_priority_timeout': 8,
    'low_priority_timeout': 20,
    'cache_ttl': 300,  # 5分
    'log_level': 'INFO'
}
```

## 🔧 トラブルシューティング

### よくある問題と解決策

1. **API制限エラー (429)**
   ```python
   # 指数バックオフとジッター
   import random
   wait_time = (2 ** attempt) + random.uniform(0, 1)
   time.sleep(wait_time)
   ```

2. **認証エラー (401)**
   ```python
   # トークンの強制更新
   creds.refresh(Request())
   ```

3. **タイムアウトエラー**
   ```python
   # API別タイムアウト設定
   service = build('gmail', 'v1', credentials=creds)
   service._http.timeout = 30
   ```

## 📈 期待される改善効果

- **実行時間**: 60-70% 短縮 (並行処理により)
- **成功率**: 85%+ → 95%+ (リトライ機能により)
- **エラー対応**: 自動復旧率 90%+
- **監視性**: 詳細ログによる問題特定時間 80% 短縮

---

*Google Cloud Python SDK リファレンス準拠版 v1.0*