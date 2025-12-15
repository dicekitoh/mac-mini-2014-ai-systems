#!/bin/bash

echo "Gmail送信設定スクリプト"
echo "======================"
echo ""
echo "このスクリプトはGmail送信に必要な環境変数を設定します。"
echo ""
echo "必要な情報："
echo "1. Gmailアドレス"
echo "2. Gmailアプリパスワード（2段階認証を有効にして取得）"
echo ""
echo "アプリパスワードの取得方法："
echo "1. Googleアカウントにログイン"
echo "2. セキュリティ設定 → 2段階認証を有効化"
echo "3. アプリパスワードを生成"
echo ""

read -p "Gmailアドレスを入力してください: " gmail_email
read -s -p "Gmailアプリパスワードを入力してください: " gmail_password
echo ""

# 環境変数を.envファイルに保存
cat > /home/fujinosuke/projects/mail/.env << EOF
export GMAIL_EMAIL="$gmail_email"
export GMAIL_APP_PASSWORD="$gmail_password"
EOF

echo ""
echo "✅ 設定を保存しました"
echo ""
echo "使用方法："
echo "1. source /home/fujinosuke/projects/mail/.env"
echo "2. python3 /home/fujinosuke/projects/mail/gmail_sender.py"