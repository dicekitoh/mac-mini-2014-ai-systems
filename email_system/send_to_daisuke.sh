#\!/bin/bash
# 伊藤大輔さん専用メール送信スクリプト

echo "📧 伊藤大輔さん宛メール送信"
echo "========================="

# 固定宛先
TO_EMAIL="itoh@thinksblog.com"  # 実際のメールアドレスに変更してください

# 引数チェック
if [ $# -eq 0 ]; then
    echo -n "📝 件名: "
    read SUBJECT
    echo -n "📄 本文: "
    read BODY
elif [ $# -eq 1 ]; then
    SUBJECT=$1
    echo -n "📄 本文: "
    read BODY
else
    SUBJECT=$1
    BODY=$2
fi

# 確認
echo ""
echo "📧 宛先: $TO_EMAIL (伊藤大輔さん)"
echo "📝 件名: $SUBJECT"
echo "📄 本文: $BODY"
echo ""

echo -n "送信しますか？ (y/n): "
read CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    echo "🚀 送信中..."
    python3 ~/projects/email_system/gmail_smart_sender.py "$TO_EMAIL" "$SUBJECT" "$BODY"
else
    echo "❌ 送信をキャンセルしました"
fi
