#!/bin/bash
"""
Google API認証24時間維持システム セットアップスクリプト
systemdサービスとcronジョブの自動設定
"""

echo "🚀 Google API認証24時間維持システム セットアップ開始"
echo "=" * 60

# 変数設定
SERVICE_NAME="google-auth-keepalive"
SCRIPT_PATH="/home/fujinosuke/projects/google_auth_keepalive_system.py"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
USER_NAME="fujinosuke"
WORK_DIR="/home/fujinosuke/projects"

# 1. systemdサービスファイル作成
echo "📋 1. systemdサービスファイル作成"
sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Google API Authentication Keep-Alive System
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$WORK_DIR
Environment=PYTHONPATH=$WORK_DIR
ExecStart=/usr/bin/python3 $SCRIPT_PATH --daemon
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=google-auth-keepalive

# セキュリティ設定
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=/home/fujinosuke
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "✅ systemdサービスファイル作成完了: $SERVICE_FILE"

# 2. systemd設定
echo "📋 2. systemd設定"
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
echo "✅ systemdサービス有効化完了"

# 3. cron設定（30分ごとのバックアップチェック）
echo "📋 3. cron設定"
CRON_JOB="*/30 * * * * /usr/bin/python3 $SCRIPT_PATH --check >> /home/fujinosuke/logs/google_auth_cron.log 2>&1"

# 既存のcronエントリをチェック
if crontab -l 2>/dev/null | grep -q "google_auth_keepalive_system.py"; then
    echo "⚠️  既存のcronジョブが見つかりました"
else
    # 新しいcronジョブを追加
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ cronジョブ追加完了（30分間隔）"
fi

# 4. ログディレクトリ確認
echo "📋 4. ログディレクトリ確認"
mkdir -p /home/fujinosuke/logs
chown $USER_NAME:$USER_NAME /home/fujinosuke/logs
echo "✅ ログディレクトリ準備完了"

# 5. 設定ファイル確認
echo "📋 5. 設定ファイル確認"
if [ ! -f "/home/fujinosuke/projects/google_auth_config.json" ]; then
    python3 $SCRIPT_PATH --check > /dev/null 2>&1
    echo "✅ 設定ファイル自動生成完了"
else
    echo "✅ 設定ファイル既存確認"
fi

# 6. 権限設定
echo "📋 6. 権限設定"
chmod +x $SCRIPT_PATH
chown $USER_NAME:$USER_NAME $SCRIPT_PATH
echo "✅ 権限設定完了"

# 7. テスト実行
echo "📋 7. テスト実行"
if python3 $SCRIPT_PATH --check; then
    echo "✅ テスト実行成功"
else
    echo "❌ テスト実行失敗"
    exit 1
fi

echo ""
echo "🎉 Google API認証24時間維持システム セットアップ完了！"
echo "=" * 60
echo ""
echo "📊 運用方法:"
echo "  🔴 デーモン開始: sudo systemctl start $SERVICE_NAME"
echo "  🟢 デーモン停止: sudo systemctl stop $SERVICE_NAME"
echo "  📋 状態確認:   sudo systemctl status $SERVICE_NAME"
echo "  📊 ログ確認:   journalctl -u $SERVICE_NAME -f"
echo "  🔄 手動チェック: python3 $SCRIPT_PATH --check"
echo ""
echo "📈 監視設定:"
echo "  • systemdデーモン: 24時間監視・自動再起動"
echo "  • cronバックアップ: 30分間隔でチェック"
echo "  • メールアラート: 設定済み (itoh@thinksblog.com)"
echo "  • ログ保存: /home/fujinosuke/logs/"
echo ""
echo "🚀 デーモンを開始するには:"
echo "  sudo systemctl start $SERVICE_NAME"