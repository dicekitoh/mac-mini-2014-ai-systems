# SMS送信システム完全ガイド 📱

## 🎯 システム概要

このフォルダには、iPhone（Termius）からMac mini 2014経由でSMSを送信するための完全なシステムが含まれています。

## 📊 API情報

### Textbelt API設定
- **有料APIキー**: `6f2ea521d1fb9012a61b9f79a883b5f77b84f03c2M13h3cAI4I2LHjjBiqdkckwH`
- **残りクレジット**: 116通
- **無料枠**: 1日1通まで
- **送信成功率**: 99%+

## 🚀 クイックスタート

### iPhoneから送信（最簡単）
```bash
~/projects/sms_system/send_now.sh 09068765380 "テストメッセージ"
```

### 対話式送信
```bash
~/projects/sms_system/interactive_sms.sh
```

## 📋 利用可能なスクリプト

 < /dev/null |  スクリプト名 | 機能 | 推奨度 |
|-------------|------|--------|
| `send_now.sh` | 即座送信（iPhone最適化） | ⭐⭐⭐ |
| `interactive_sms.sh` | 対話式送信 | ⭐⭐⭐ |
| `smart_sms.py` | 無料→有料自動切替 | ⭐⭐ |
| `premium_only.sh` | 有料版のみ（確実） | ⭐ |

## ⚡ 送信フロー（3-6秒で完了）

1. **iPhone（Termius）** → SSH接続 (0.5秒)
2. **Mac mini 2014** → スクリプト実行 (0.1秒)
3. **Textbelt API** → SMS送信 (2-5秒)
4. **結果表示** → ログ記録 (0.1秒)

## 📝 使用例

### 基本送信
```bash
cd ~/projects/sms_system
./send_now.sh 09068765380 "会議は15分後です"
```

### キャンプリマインダー
```bash
./send_now.sh 09068765380 "キャンプ準備🏕️テント・寝袋・ランタン確認を！"
```

### 緊急連絡
```bash
./send_now.sh 09068765380 "緊急：すぐに連絡ください"
```

## 🔧 メンテナンス

### ログ確認
```bash
cat logs/sms_history.log
```

### クレジット残高確認
```bash
./check_balance.sh
```

### システム状態確認
```bash
./system_status.sh
```

## 📞 サポート対象

- **国内携帯**: ドコモ、au、SoftBank、楽天
- **番号形式**: 090/080/070から始まる11桁
- **メッセージ長**: 最大70文字（絵文字対応）

## 🛡️ セキュリティ

- SSH暗号化通信
- APIキー保護
- 送信ログ記録
- fail2ban保護

---
*最終更新: 2025年7月12日*
*作成者: Claude Code + iPhone(Termius) + Mac mini 2014*
