# VS Code Remote SSH設定ガイド

**作成日**: 2025年6月15日  
**対象**: Windows 11 Laptop Studio → MacMini2014  
**目的**: VS CodeでMacMini2014に直接リモート接続して開発

## 🎯 VS Code Remote SSHとは？

VS CodeをMacMini2014上で直接実行しているかのように使える機能です。
- Windows 11のVS Codeの見た目
- MacMini2014のファイルシステムに直接アクセス
- MacMini2014上でコマンド実行
- 拡張機能もリモート環境で動作

## 📋 前提条件

### Windows 11側
- VS Code インストール済み
- OpenSSH クライアント有効（通常デフォルトでインストール済み）

### MacMini2014側  
- SSH サーバー稼働中 ✅（確認済み）
- 開発環境準備済み ✅（Python, Node.js等）

## 🚀 設定手順

### ステップ1: VS Code拡張機能インストール

1. **VS Code起動**
2. **拡張機能タブ** (`Ctrl+Shift+X`) を開く
3. **「Remote - SSH」** を検索
4. **Microsoft製の「Remote - SSH」** をインストール
   - 発行者: Microsoft
   - 拡張機能ID: ms-vscode-remote.remote-ssh

### ステップ2: SSH設定ファイル作成

1. **VS Codeでコマンドパレット** (`Ctrl+Shift+P`) 開く
2. **「Remote-SSH: Open SSH Configuration File」** を選択
3. **ユーザー設定ファイル** を選択:
   ```
   C:\Users\[ユーザー名]\.ssh\config
   ```
4. **以下の設定を追加**:
   ```
   Host macmini2014
       HostName 126.217.45.148
       Port 2222
       User fujinosuke
       PreferredAuthentications password
   ```

### ステップ3: リモート接続

1. **VS Codeでコマンドパレット** (`Ctrl+Shift+P`) 開く
2. **「Remote-SSH: Connect to Host」** を選択
3. **「macmini2014」** を選択
4. **パスワード入力**: `***REMOVED***`
5. **新しいVS Codeウィンドウ** が開く（MacMini2014に接続済み）

### ステップ4: 作業ディレクトリを開く

1. **ファイル** → **フォルダーを開く**
2. **`/home/fujinosuke/projects`** を入力
3. **OK** クリック
4. **MacMini2014のプロジェクトフォルダ** がVS Codeで開く

## 📁 VS Code Remote SSH使用例

### 接続後の画面表示
- **左下**: 「SSH: macmini2014」と表示
- **エクスプローラー**: MacMini2014のファイル構造
- **ターミナル**: MacMini2014のbashターミナル

### ターミナル使用
1. **表示** → **ターミナル** (`Ctrl+Shift+``)
2. **MacMini2014のターミナル** が開く
3. **直接コマンド実行可能**:
   ```bash
   cd ~/projects/
   python3 scripts/system_status_checker.py
   ```

## 🔧 拡張機能インストール（リモート環境）

MacMini2014側にも拡張機能をインストール可能:

### Python開発
- **Python** (Microsoft)
- **Pylance** (Microsoft)

### その他便利な拡張機能
- **GitLens** — Git supercharged
- **Bracket Pair Colorizer**
- **Auto Rename Tag**

## 💡 便利な機能

### 1. ファイル編集
- **MacMini2014のファイル** をWindows 11のVS Codeで直接編集
- **自動保存** でリアルタイム同期

### 2. ターミナル操作
- **VS Code内ターミナル** でMacMini2014のコマンド実行
- **複数ターミナル** 同時使用可能

### 3. デバッグ
- **VS Codeデバッガー** でMacMini2014上のコード直接デバッグ
- **ブレークポイント** 設定可能

### 4. Git統合
- **VS Code Git機能** でMacMini2014のリポジトリ操作
- **コミット、プッシュ** 等すべてVS Code内で完結

## 🎯 作業フロー例

### 毎日の作業開始
1. **VS Code起動**
2. **Ctrl+Shift+P** → **「Remote-SSH: Connect to Host」**
3. **「macmini2014」** 選択
4. **パスワード**: `***REMOVED***`
5. **フォルダー開く**: `/home/fujinosuke/projects`
6. **作業開始**

### プロジェクト作業
```bash
# VS Code内ターミナルで
cd ~/projects/google_auth/
python3 google_unified_auth_system.py

# ファイル編集もVS Code内で直接
# 保存すると自動的にMacMini2014に反映
```

## 🔐 SSH鍵認証設定（オプション）

パスワード入力を省略したい場合:

### 1. Windows側でSSH鍵生成
```powershell
ssh-keygen -t rsa -b 4096 -f %USERPROFILE%\.ssh\macmini2014_key
```

### 2. SSH設定ファイル更新
```
Host macmini2014
    HostName 126.217.45.148
    Port 2222
    User fujinosuke
    IdentityFile ~/.ssh/macmini2014_key
    PreferredAuthentications publickey
```

### 3. 公開鍵をMacMini2014にコピー
```powershell
type %USERPROFILE%\.ssh\macmini2014_key.pub  < /dev/null |  ssh -p 2222 fujinosuke@126.217.45.148 "cat >> ~/.ssh/authorized_keys"
```

## 🛠️ トラブルシューティング

### 接続できない場合
1. **SSH設定確認**: `~/.ssh/config` ファイル確認
2. **ネットワーク確認**: PowerShellで `ping 126.217.45.148`
3. **VS Code再起動**

### パスワード認証が効かない場合
```
Host macmini2014
    HostName 126.217.45.148
    Port 2222
    User fujinosuke
    PreferredAuthentications password
    PubkeyAuthentication no
```

## 🎉 VS Code Remote SSHの利点

### 統一された開発環境
- **Windows 11の使いやすいVS Code UI**
- **MacMini2014の実行環境**
- **ファイル同期問題の完全解消**

### 効率性
- **環境切り替え不要**
- **ファイルコピー不要**
- **直接編集・実行**

### 機能性
- **デバッグ機能**
- **Git統合**
- **拡張機能活用**

---

**これにより、Windows 11 Laptop Studioの快適なVS Code環境で、MacMini2014の全機能を直接使用できます！**
