#!/bin/bash
# Aqua Voice SSH音声入力セットアップスクリプト

echo "=== Aqua Voice SSH音声入力セットアップ ==="

# 1. 必要パッケージインストール確認
echo "依存パッケージ確認中..."
python3 -c "import requests" 2>/dev/null || {
    echo "requestsパッケージをインストール中..."
    pip3 install requests
}

# 2. PulseAudioネットワークモジュール有効化
echo "PulseAudioネットワークモジュール設定中..."
if ! pactl list modules | grep -q "module-native-protocol-tcp"; then
    pactl load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1 port=4713
    echo "✅ TCPモジュール有効化完了"
else
    echo "✅ TCPモジュール既に有効"
fi

# 3. 音声デバイス状況確認
echo "音声デバイス状況:"
pactl list sources short

# 4. テスト実行
echo "音声録音テスト実行中..."
python3 aquavoice_ssh_input.py --duration 2

echo ""
echo "=== セットアップ完了 ==="
echo "使用方法:"
echo "  基本: python3 aquavoice_ssh_input.py"
echo "  API Key指定: python3 aquavoice_ssh_input.py --api-key YOUR_KEY"
echo "  録音時間指定: python3 aquavoice_ssh_input.py --duration 10"