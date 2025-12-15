#\!/bin/bash
# 定型メールテンプレート送信スクリプト

echo "📧 定型メールテンプレート"
echo "======================="

echo "利用可能なテンプレート:"
echo "1) 会議リマインダー"
echo "2) 作業完了報告"
echo "3) 確認依頼"
echo "4) お疲れ様メール"
echo "5) テストメール"
echo "6) カスタム"

echo -n "テンプレート番号を選択 (1-6): "
read TEMPLATE_NUM

# 宛先入力
echo -n "📧 宛先メールアドレス: "
read TO_EMAIL

case $TEMPLATE_NUM in
    1)
        SUBJECT="会議リマインダー"
        BODY="お疲れ様です。明日の会議についてリマインダーをお送りします。

日時: [日時を入力してください]
場所: [場所を入力してください]
議題: [議題を入力してください]

よろしくお願いいたします。"
        ;;
    2)
        SUBJECT="作業完了報告"
        BODY="お疲れ様です。

以下の作業が完了しましたのでご報告いたします。

作業内容: [作業内容]
完了時刻: $(date +%Y年%m月%d日 %H時%M分)

何かご不明な点がございましたらお知らせください。"
        ;;
    3)
        SUBJECT="確認依頼"
        BODY="お疲れ様です。

以下についてご確認をお願いいたします。

確認事項: [確認したい内容]

お忙しい中恐れ入りますが、よろしくお願いいたします。"
        ;;
    4)
        SUBJECT="お疲れ様でした"
        BODY="本日もお疲れ様でした。

[今日の作業内容や感想]

明日もよろしくお願いいたします。"
        ;;
    5)
        SUBJECT="テストメール"
        BODY="これはテストメールです。

送信日時: $(date +%Y年%m月%d日 %H時%M分)
送信者: iPhone(Termius) + Mac mini 2014"
        ;;
    6)
        echo -n "📝 件名: "
        read SUBJECT
        echo "📄 本文を入力してください:"
        read BODY
        ;;
    *)
        echo "❌ 無効な選択です"
        exit 1
        ;;
esac

# 確認・送信
echo ""
echo "=== 送信確認 ==="
echo "宛先: $TO_EMAIL"
echo "件名: $SUBJECT"
echo "本文: ${BODY:0:100}..."
echo ""

echo -n "送信しますか？ (y/n): "
read CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    echo "🚀 送信中..."
    python3 ~/projects/email_system/gmail_smart_sender.py "$TO_EMAIL" "$SUBJECT" "$BODY"
else
    echo "❌ 送信をキャンセルしました"
fi
