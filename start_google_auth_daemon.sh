#!/bin/bash
"""
Google API認証24時間維持デーモン 起動スクリプト
"""

echo "🚀 Google API認証24時間維持デーモン 起動"
echo "=" * 50

# プロセス確認
DAEMON_PID=$(pgrep -f "google_auth_keepalive_system.py --daemon")

if [ ! -z "$DAEMON_PID" ]; then
    echo "⚠️  既にデーモンが実行中です (PID: $DAEMON_PID)"
    echo "停止する場合: kill $DAEMON_PID"
    exit 1
fi

# ログディレクトリ作成
mkdir -p /home/fujinosuke/logs

# デーモン起動
echo "🔄 デーモンを起動中..."
nohup python3 /home/fujinosuke/projects/google_auth_keepalive_system.py --daemon > /home/fujinosuke/logs/google_auth_daemon.log 2>&1 &

DAEMON_PID=$!
echo "✅ デーモン起動完了 (PID: $DAEMON_PID)"

# 起動確認
sleep 3
if kill -0 $DAEMON_PID 2>/dev/null; then
    echo "🎉 デーモンが正常に動作中"
    echo ""
    echo "📊 操作方法:"
    echo "  • 状態確認: ps aux | grep google_auth_keepalive"
    echo "  • ログ確認: tail -f /home/fujinosuke/logs/google_auth_daemon.log"
    echo "  • 停止方法: kill $DAEMON_PID"
    echo ""
    echo "📈 監視設定:"
    echo "  • 自動チェック: 30分間隔"
    echo "  • 自動更新: 期限6時間前"
    echo "  • メールアラート: 有効"
    echo "  • 失敗時再試行: 最大3回"
else
    echo "❌ デーモン起動に失敗しました"
    echo "ログを確認してください: cat /home/fujinosuke/logs/google_auth_daemon.log"
    exit 1
fi