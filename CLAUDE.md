# Claude Code プロジェクト設定

## 環境情報
- ホスト: macmini2014 (Mac mini 2014 / Ubuntu 24.04)
- ユーザー: fujinosuke
- IP: 192.168.3.43

## 作業完了時の通知設定

**重要**: 作業完了後、以下のメールアドレスに結果を送信すること

- 宛先: dice.k_itoh@softbank.ne.jp
- 送信元: itoh@thinksblog.com

### メール送信方法（Pythonコード）
```python
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_completion_report(subject, body):
    sender_email = os.environ.get('GMAIL_ADDRESS')
    sender_password = os.environ.get('GMAIL_APP_PASSWORD')
    to_email = os.environ.get('NOTIFICATION_EMAIL')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = f'[Mac mini] {subject}'
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
```

## Git運用ルール
- **変更後は毎回プッシュすること**（portalサブモジュール → 親リポジトリの順）
- portal: `master`ブランチ → `origin/master`
- 親リポジトリ: `main`ブランチ → `origin/main`

## プロジェクト構成
- ~/projects/ - メインプロジェクトディレクトリ
- ~/scripts/ - スクリプト類
- ~/logs/ - ログファイル
- ~/docs/ - ドキュメント
- ~/google_auth/ - Google APIトークン
