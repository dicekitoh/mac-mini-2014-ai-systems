#\!/bin/bash
# 最終版メール送信スクリプト

echo "📧 メール送信システム v2.0"
echo "=========================="

if [ $# -ne 3 ]; then
    echo "使用方法: ./send_mail_final.sh <宛先> <件名> <本文>"
    exit 1
fi

TO_EMAIL=$1
SUBJECT=$2
BODY=$3

echo "📧 宛先: $TO_EMAIL"
echo "📝 件名: $SUBJECT"
echo "📄 本文: ${BODY:0:50}..."
echo ""

# 環境変数設定
export GMAIL_EMAIL="itoh@thinksblog.com"
export GMAIL_APP_PASSWORD="***REMOVED***"

echo "🚀 送信開始..."
python3 ~/projects/email_system/gmail_final.py "$TO_EMAIL" "$SUBJECT" "$BODY"
