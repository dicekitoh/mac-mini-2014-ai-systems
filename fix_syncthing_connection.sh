#!/bin/bash

echo "Syncthing接続問題の修正スクリプト"

# 1. 現在の設定を確認
echo "現在のリッスンアドレス設定:"
grep -A2 "listenAddress" ~/.local/state/syncthing/config.xml

# 2. IPv4とIPv6両方でリッスンするように修正
echo "設定を修正中..."
sed -i 's|<listenAddress>tcp://0.0.0.0:22000</listenAddress>|<listenAddress>tcp://0.0.0.0:22000</listenAddress>|' ~/.local/state/syncthing/config.xml
sed -i 's|<listenAddress>quic://0.0.0.0:22000</listenAddress>|<listenAddress>quic://0.0.0.0:22000</listenAddress>|' ~/.local/state/syncthing/config.xml

# デフォルトに戻す（これが正しい設定）
sed -i 's|<listenAddress>tcp://0.0.0.0:22000</listenAddress>|<listenAddress>default</listenAddress>|' ~/.local/state/syncthing/config.xml
sed -i '/<listenAddress>quic:\/\/0.0.0.0:22000<\/listenAddress>/d' ~/.local/state/syncthing/config.xml

# 3. Syncthingを再起動
echo "Syncthingを再起動中..."
systemctl --user restart syncthing

echo "5秒待機中..."
sleep 5

# 4. ポート状態を確認
echo "ポート22000の状態:"
netstat -tuln | grep 22000

echo "修正完了！"