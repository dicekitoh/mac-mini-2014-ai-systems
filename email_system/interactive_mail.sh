#\!/bin/bash
# 対話式メール送信スクリプト

echo "📧 対話式メール送信システム"
echo "=========================="

# 宛先入力
echo -n "📧 宛先メールアドレス: "
read TO_EMAIL

# 件名入力
echo -n "📝 件名: "
read SUBJECT

# 本文入力
echo "📄 本文を入力してください（終了は空行でEnter）:"
BODY=""
while IFS= read -r line; do
    if [ -z "$line" ]; then
        break
    fi
    if [ -z "$BODY" ]; then
        BODY="$line"
    else
        BODY="$BODY"$n"$line"
    fi
done

# 確認
echo ""
echo "=== 送信確認 ==="
echo "宛先: $TO_EMAIL"
echo "件名: $SUBJECT"
echo "本文: ${BODY:0:100}$([ ${#BODY} -gt 100 ] && echo ...)"
echo ""

echo -n "送信しますか？ (y/n): "
read CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    echo "🚀 送信中..."
    python3 ~/projects/email_system/gmail_smart_sender.py "$TO_EMAIL" "$SUBJECT" "$BODY"
else
    echo "❌ 送信をキャンセルしました"
fi
