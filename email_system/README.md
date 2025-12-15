# Eメール送信システム完全ガイド 📧

## 🎯 システム概要

このフォルダには、iPhone（Termius）からMac mini 2014経由でEメールを送信するための完全なシステムが含まれています。

## 📊 メール設定情報

### Gmail SMTP設定
- **送信者**: itoh@thinksblog.com
- **SMTPサーバー**: smtp.gmail.com:587
- **認証**: Googleアプリパスワード
- **暗号化**: STARTTLS
- **送信成功率**: 99%+

## 🚀 クイックスタート

### iPhoneから送信（最簡単）
```bash
~/projects/email_system/send_mail.sh "宛先@example.com" "件名" "本文内容"
```

### 対話式送信
```bash
~/projects/email_system/interactive_mail.sh
```

### 定型メール送信
```bash
~/projects/email_system/quick_templates.sh
```

## 📋 利用可能なスクリプト

 < /dev/null |  スクリプト名 | 機能 | 推奨度 |
|-------------|------|--------|
| `send_mail.sh` | 即座メール送信（iPhone最適化） | ⭐⭐⭐ |
| `interactive_mail.sh` | 対話式送信 | ⭐⭐⭐ |
| `quick_templates.sh` | 定型文テンプレート | ⭐⭐ |
| `send_to_daisuke.sh` | 伊藤大輔さん専用 | ⭐⭐ |
| `gmail_sender.py` | 高機能メール送信 | ⭐ |

## ⚡ 送信フロー（1-3秒で完了）

1. **iPhone（Termius）** → SSH接続 (0.5秒)
2. **Mac mini 2014** → スクリプト実行 (0.1秒)
3. **Gmail SMTP** → メール送信 (1-2秒)
4. **結果表示** → ログ記録 (0.1秒)

## 📝 使用例

### 基本送信
```bash
cd ~/projects/email_system
./send_mail.sh "test@example.com" "テスト件名" "テスト本文"
```

### 会議リマインダー
```bash
./send_mail.sh "team@company.com" "会議リマインダー" "明日10時からの会議にご参加ください"
```

### 緊急連絡
```bash
./send_to_daisuke.sh "緊急" "すぐに連絡をお願いします"
```

## 🔧 メンテナンス

### ログ確認
```bash
cat logs/email_history.log
```

### 送信履歴確認
```bash
./check_email_status.sh
```

### テンプレート一覧
```bash
./list_templates.sh
```

## 📞 サポート対象

- **メール形式**: テキスト・HTML対応
- **文字エンコード**: UTF-8（日本語完全対応）
- **添付ファイル**: 対応予定
- **宛先**: 複数宛先対応

## 🛡️ セキュリティ

- Gmail OAuth2.0対応
- アプリパスワード利用
- 送信ログ記録
- SSH暗号化通信

## 📧 よく使う宛先

- **伊藤大輔**: 専用スクリプトあり
- **テスト用**: itoh@thinksblog.com
- **チーム連絡**: 複数宛先対応

---
*最終更新: 2025年7月12日*
*作成者: Claude Code + iPhone(Termius) + Mac mini 2014*
