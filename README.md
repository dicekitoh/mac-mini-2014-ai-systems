# MacMini2014 統一プロジェクト環境

**作成日**: 2025年6月15日  
**目的**: 全ての作業とAPI連携をMacMini2014に統一集約

## 📁 ディレクトリ構造

```
~/projects/
├── google_auth/          # Google認証システム統一管理
│   ├── *.pickle         # 認証トークンファイル群
│   ├── *_auth*.py       # 認証関連スクリプト
│   └── google_unified_auth_system.py  # メイン統一認証システム
├── documentation/       # プロジェクト文書・レポート
│   ├── google_auth_project_final_report.md
│   ├── project_completion_summary.txt
│   └── save_to_gdocs.py
├── scripts/            # 共通実行スクリプト
│   ├── system_status_checker.py
│   ├── weather_alert_*.py
│   └── final_fax_system.py
└── backups/           # バックアップファイル
```

## 🎯 統一方針

### 作業環境
- **中央システム**: MacMini2014 (`ssh -p 2222 fujinosuke@126.217.45.148`)
- **入力ツール**: Windows 11 Laptop Studio（SSH経由でMacMini2014にアクセス）
- **全作業実行**: MacMini2014上で実行
- **API連携**: MacMini2014から直接実行

### 接続方法
```bash
# 外部からの標準接続
sshpass -p ***REMOVED*** ssh -p 2222 fujinosuke@126.217.45.148

# プロジェクトディレクトリへ移動
cd ~/projects/
```

## 📊 統一済みシステム

### ✅ Google認証システム
- **場所**: `~/projects/google_auth/`
- **統一トークン**: `unified_google_token.pickle`
- **24時間認証維持**: 自動リフレッシュ機能

### ✅ システム監視
- **スクリプト**: `~/projects/scripts/system_status_checker.py`
- **実行**: `python3 ~/projects/scripts/system_status_checker.py`

### ✅ API連携
- **Google APIs**: 全てMacMini2014から実行
- **LINEWORKS**: MacMini2014ベース
- **その他連携**: 統一環境で実行

## 🔧 利用方法

### 1. 作業開始
```bash
ssh -p 2222 fujinosuke@126.217.45.148
cd ~/projects/
```

### 2. Google認証確認
```bash
cd ~/projects/google_auth/
python3 google_unified_auth_system.py
```

### 3. システム状況確認
```bash
python3 ~/projects/scripts/system_status_checker.py
```

## 🎉 統一完了

Windows 11 Laptop Studioは入力ツールとして機能し、
全ての実際の作業・API連携・データ保存はMacMini2014で実行される
完全統一環境が完成しました。

**中央集約**: MacMini2014  
**作業方針**: SSH経由での直接作業  
**データ統一**: ~/projects/ 配下で一元管理
