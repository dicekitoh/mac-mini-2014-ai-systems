#\!/bin/bash
# iPhone最適化 即座メール送信スクリプト

echo "📧 メール送信システム v2.0"
echo "=========================="

# 引数チェック
if [ $# -ne 3 ]; then
    echo "使用方法:"
    echo "./send_mail.sh <宛先> <件名> <本文>"
    echo ""
    echo "例:"
    echo "./send_mail.sh \"test@example.com\" \"テスト件名\" \"テスト本文\""
    exit 1
fi

TO_EMAIL=$1
SUBJECT=$2
BODY=$3

# 基本チェック
if [ -z "$TO_EMAIL" ] || [[ \! "$TO_EMAIL" =~ @ ]]; then
    echo "❌ 有効なメールアドレスを入力してください"
    exit 1
fi

if [ -z "$SUBJECT" ]; then
    echo "❌ 件名を入力してください"
    exit 1
fi

if [ -z "$BODY" ]; then
    echo "❌ 本文を入力してください"
    exit 1
fi

# 送信情報表示
echo "📧 宛先: $TO_EMAIL"
echo "📝 件名: $SUBJECT"
echo "📄 本文: ${BODY:0:50}$([ ${#BODY} -gt 50 ] && echo ...)"
echo ""

# メール送信実行
echo "🚀 送信開始..."
python3 ~/projects/email_system/gmail_smart_sender.py "$TO_EMAIL" "$SUBJECT" "$BODY"
