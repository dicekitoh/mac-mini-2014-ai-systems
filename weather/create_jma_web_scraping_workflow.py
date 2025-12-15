#\!/usr/bin/env python3
import requests
import json

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMmVjNzhiNy1mNmUyLTQwZmYtYWY3NS1iMDU3YzhmNmNiZjMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzUwNjUwNzY3LCJleHAiOjE3NTMxNTY4MDB9.WPeUVnd30MT4BiuMt_CaWXvWOhW6e_Cs8cBw3DOuNBo"
BASE_URL = "http://localhost:5678/api/v1"

headers = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

# 既存ワークフローID
workflow_id = "d8QYhyj7Xi4O0lbk"

# Webスクレイピング用ワークフローデータ
workflow_update = {
    "name": "札幌市警報・注意報Webスクレイピング",
    "nodes": [
        {
            "parameters": {},
            "id": "manual-trigger-1",
            "name": "Manual Trigger",
            "type": "n8n-nodes-base.manualTrigger", 
            "typeVersion": 1,
            "position": [240, 300]
        },
        {
            "parameters": {
                "url": "https://www.jma.go.jp/bosai/warning/data/warning/011000.json",
                "options": {
                    "timeout": 15000,
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                }
            },
            "id": "http-request-jma-warning",
            "name": "気象庁警報データ取得",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [460, 300]
        },
        {
            "parameters": {
                "jsCode": "// 札幌市の警報・注意報情報を抽出・整形\nconst data = $input.first().json;\n\n// 現在時刻\nconst now = new Date();\nconst formatDate = (date) => {\n  const year = date.getFullYear();\n  const month = String(date.getMonth() + 1).padStart(2, 0);\n  const day = String(date.getDate()).padStart(2, 0);\n  const hour = String(date.getHours()).padStart(2, 0);\n  const minute = String(date.getMinutes()).padStart(2, 0);\n  return `${year}年${month}月${day}日${hour}時${minute}分`;\n};\n\nlet result = {\n  取得日時: formatDate(now),\n  地域: 札幌市,\n  警報・注意報: 情報なし,\n  発表状況: 正常取得,\n  データソース: 気象庁API\n};\n\ntry {\n  if (data && data.areaTypes) {\n    // エリアタイプから札幌市を検索\n    for (const areaType of data.areaTypes) {\n      if (areaType.areas) {\n        for (const area of areaType.areas) {\n          if (area.name && area.name.includes(札幌)) {\n            const warnings = [];\n            \n            // 警報・注意報コードを取得\n            if (area.warnings && area.warnings.length > 0) {\n              area.warnings.forEach(warning => {\n                if (warning.status) {\n                  warnings.push(`${warning.name || 不明}(${warning.status})`);\n                }\n              });\n            }\n            \n            result.警報・注意報 = warnings.length > 0 ? warnings.join(, ) : 発表なし;\n            result.発表状況 = area.publishTime || 時刻不明;\n            break;\n          }\n        }\n      }\n    }\n  }\n  \n  // データが空の場合のフォールバック\n  if (result.警報・注意報 === 情報なし) {\n    result.警報・注意報 = データ構造確認が必要;\n    result.rawData = JSON.stringify(data).substring(0, 500) + ...;\n  }\n  \n} catch (error) {\n  result.エラー = error.message;\n  result.警報・注意報 = データ解析エラー;\n}\n\nreturn result;"
            },
            "id": "code-extract-sapporo-warnings",
            "name": "札幌市警報・注意報抽出",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [680, 300]
        }
    ],
    "connections": {
        "Manual Trigger": {
            "main": [
                [
                    {
                        "node": "気象庁警報データ取得",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "気象庁警報データ取得": {
            "main": [
                [
                    {
                        "node": "札幌市警報・注意報抽出", 
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    },
    "settings": {}
}

print("札幌市警報・注意報Webスクレイピングワークフロー更新中...")

try:
    # ワークフロー更新
    response = requests.put(f"{BASE_URL}/workflows/{workflow_id}",
                          json=workflow_update,
                          headers=headers)
    
    print(f"ステータス: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("成功\! 気象庁Webスクレイピングワークフロー完成\!")
        print(f"ワークフロー名: {result[name]}")
        print(f"ノード数: {len(result[nodes])}")
        print("\nワークフロー構成:")
        for i, node in enumerate(result[nodes], 1):
            print(f"  {i}. {node[name]} ({node[type]})")
        
        print(f"\n✅ ワークフローID: {workflow_id}")
        print("📝 処理内容:")
        print("   1. Manual Trigger - 手動実行")
        print("   2. HTTP Request - 気象庁API呼び出し")
        print("   3. Code - 札幌市データ抽出・整形")
        
    else:
        print(f"❌ エラー: {response.text}")
        
except Exception as e:
    print(f"❌ 例外: {e}")

print(f"\n🌐 Web UI確認: http://192.168.3.43:5678")
print("▶️  実行方法: ワークフローを開いて「Test workflow」ボタンをクリック")
