# VS Code Remote SSH 簡単セットアップガイド

## 🎯 概要
Windows 11のVS CodeでMacMini2014に直接接続して、快適な開発環境を構築

## 🚀 簡単3ステップ

### ステップ1: 拡張機能インストール
1. **VS Code起動**
2. **拡張機能タブ** (`Ctrl+Shift+X`)
3. **「Remote - SSH」** (Microsoft製) をインストール

### ステップ2: SSH設定
1. **VS Code** で `Ctrl+Shift+P`
2. **「Remote-SSH: Open SSH Configuration File」**
3. **以下を追加**:
```
Host macmini2014
    HostName 126.217.45.148
    Port 2222
    User fujinosuke
    PreferredAuthentications password
```

### ステップ3: 接続
1. **VS Code** で `Ctrl+Shift+P`
2. **「Remote-SSH: Connect to Host」**
3. **「macmini2014」** を選択
4. **パスワード**: `***REMOVED***`
5. **フォルダー開く**: `/home/fujinosuke/projects`

## ✅ 完了！

これで**Windows 11のVS Code**で**MacMini2014のファイル**を直接編集・実行できます。

### 接続確認方法
- 左下に「SSH: macmini2014」表示
- ターミナルでMacMini2014のコマンド実行可能
- ファイル編集が直接MacMini2014に反映

## 📋 毎日の使用方法
1. VS Code起動
2. `Ctrl+Shift+P` → 「Remote-SSH: Connect to Host」
3. 「macmini2014」選択 → パスワード入力
4. 作業開始！