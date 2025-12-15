# MacMini2014 SSH接続完全ガイド

**作成日**: 2025年6月15日  
**対象**: Windows 11 Laptop Studio → MacMini2014

## 📋 接続情報

### 基本接続設定
- **IPアドレス**: 126.217.45.148
- **ポート**: 2222
- **ユーザー名**: fujinosuke  
- **パスワード**: ***REMOVED***

### 接続先確認
- **ホスト名**: MacMini2014
- **OS**: Ubuntu 24.04.2 LTS
- **作業ディレクトリ**: /home/fujinosuke/projects/

## 🔧 接続方法

### 1. Windows PowerShell/コマンドプロンプトから
```cmd
ssh -p 2222 fujinosuke@126.217.45.148
```
パスワード入力: `***REMOVED***`

### 2. Windows Subsystem for Linux (WSL) Ubuntu から
```bash
ssh -p 2222 fujinosuke@126.217.45.148
```
パスワード入力: `***REMOVED***`

### 3. パスワード自動入力（推奨）
```bash
sshpass -p '***REMOVED***' ssh -p 2222 fujinosuke@126.217.45.148
```

## 🚀 接続手順（ステップバイステップ）

### ステップ1: 接続開始
1. Windows 11でPowerShellまたはWSL Ubuntuを起動
2. 以下のコマンドを入力:
```bash
ssh -p 2222 fujinosuke@126.217.45.148
```

### ステップ2: パスワード入力
```
Password: ***REMOVED***
```
（パスワードは表示されませんが入力されています）

### ステップ3: 接続成功確認
接続成功すると以下のような表示が出ます:
```
Welcome to Ubuntu 24.04.2 LTS (GNU/Linux 5.15.167.4-microsoft-standard-WSL2 x86_64)
fujinosuke@macmini2014:~$
```

### ステップ4: 作業ディレクトリに移動
```bash
cd ~/projects/
```

## 🔐 SSH鍵認証設定（オプション）

パスワード入力を省略したい場合:

### 1. SSH鍵生成（Windows側）
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/macmini2014_key
```

### 2. 公開鍵をMacMini2014にコピー
```bash
ssh-copy-id -i ~/.ssh/macmini2014_key.pub -p 2222 fujinosuke@126.217.45.148
```

### 3. 鍵を使用した接続
```bash
ssh -i ~/.ssh/macmini2014_key -p 2222 fujinosuke@126.217.45.148
```

## 🛠️ トラブルシューティング

### 接続できない場合

1. **ネットワーク確認**
```bash
ping 126.217.45.148
```

2. **ポート確認**
```bash
telnet 126.217.45.148 2222
```

3. **別の接続方法（IPv6）**
```bash
ssh fujinosuke@2400:2413:9402:db00::100
```

### よくあるエラー

#### エラー: "Connection refused"
- MacMini2014のSSHサービスが停止している可能性
- IPアドレスが変更された可能性

#### エラー: "Permission denied"
- パスワードが間違っている
- ユーザー名が間違っている

#### エラー: "Network unreachable"
- インターネット接続の問題
- IPv4接続の問題（IPv6で試してみる）

## 📱 モバイルからの接続

### iPhone/Android用SSHアプリ
- **Termius**: 推奨SSHクライアント
- **接続設定**: 同じ情報を入力

## 🔄 接続確認スクリプト

接続テスト用:
```bash
# 接続テスト
ssh -p 2222 fujinosuke@126.217.45.148 'echo "接続成功！現在時刻: $(date)"'
```

## 📋 クイックリファレンス

### 基本接続
```bash
ssh -p 2222 fujinosuke@126.217.45.148
```

### 自動パスワード接続
```bash
sshpass -p '***REMOVED***' ssh -p 2222 fujinosuke@126.217.45.148
```

### ファイルコピー（SCP）
```bash
# ローカル → MacMini2014
scp -P 2222 local_file.txt fujinosuke@126.217.45.148:~/

# MacMini2014 → ローカル  
scp -P 2222 fujinosuke@126.217.45.148:~/remote_file.txt ./
```

### 作業開始テンプレート
```bash
ssh -p 2222 fujinosuke@126.217.45.148
cd ~/projects/
python3 scripts/system_status_checker.py
```

## 🎯 覚えるべき基本コマンド

1. **接続**: `ssh -p 2222 fujinosuke@126.217.45.148`
2. **プロジェクト移動**: `cd ~/projects/`  
3. **システム確認**: `python3 scripts/system_status_checker.py`
4. **切断**: `exit` または `Ctrl+D`

## 📞 緊急時の代替接続

### IPv6接続
```bash
ssh fujinosuke@2400:2413:9402:db00::100
```

### ローカルネットワーク（同一ネットワーク内）
```bash
ssh fujinosuke@192.168.3.43
```

## 🎉 接続成功後の確認事項

1. 現在のディレクトリ確認: `pwd`
2. プロジェクト構造確認: `ls ~/projects/`
3. システム状況確認: `python3 ~/projects/scripts/system_status_checker.py`

---

**重要**: このガイドを保存して、いつでも参照できるようにしてください。