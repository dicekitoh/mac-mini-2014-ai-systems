# Google Cloud Speech-to-Text API セットアップガイド

## 1. Google Cloud プロジェクトの準備

### 1.1 Google Cloud Consoleでプロジェクト作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新規プロジェクトを作成または既存プロジェクトを選択

### 1.2 Speech-to-Text APIを有効化
```bash
# CLIを使用する場合
gcloud services enable speech.googleapis.com

# または、Consoleから:
# APIとサービス > ライブラリ > "Cloud Speech-to-Text API"を検索 > 有効化
```

## 2. 認証設定

### 2.1 サービスアカウントの作成
1. Google Cloud Console > IAMと管理 > サービスアカウント
2. 「サービスアカウントを作成」をクリック
3. 名前を入力（例: speech-to-text-service）
4. ロール: 「Cloud Speech 管理者」を選択
5. JSONキーを作成してダウンロード

### 2.2 認証ファイルの配置
```bash
# 認証ファイルを安全な場所に配置
mkdir -p ~/google_auth
mv ~/Downloads/your-project-xxxxx.json ~/google_auth/speech_credentials.json

# 環境変数に設定
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/google_auth/speech_credentials.json"

# .bashrcに追加（永続化）
echo 'export GOOGLE_APPLICATION_CREDENTIALS="$HOME/google_auth/speech_credentials.json"' >> ~/.bashrc
```

## 3. 必要なライブラリのインストール

```bash
# Python環境の準備
pip install google-cloud-speech

# 音声ファイル処理用（オプション）
pip install pydub  # 音声形式変換用
sudo apt-get install ffmpeg  # 音声処理用
```

## 4. 使用方法

### 基本的な使用
```bash
# 日本語音声の文字起こし
python google_speech_to_text.py audio.wav

# 英語音声の文字起こし
python google_speech_to_text.py audio.mp3 --language en-US

# 結果をファイルに保存
python google_speech_to_text.py audio.wav --output transcript.txt

# 認証ファイルを指定
python google_speech_to_text.py audio.wav --credentials ~/google_auth/speech_credentials.json
```

### サポートされる音声形式
- WAV（推奨）
- MP3
- FLAC
- M4A
- OPUS

### 言語コードの例
- 日本語: `ja-JP`
- 英語（米国）: `en-US`
- 英語（英国）: `en-GB`
- 中国語: `zh-CN`
- 韓国語: `ko-KR`

## 5. 料金について

### 無料枠
- 月60分まで無料

### 有料料金（2024年時点）
- 標準モデル: $0.024/分（約1.5円/分）
- 拡張モデル: $0.036/分（約2.3円/分）

## 6. トラブルシューティング

### 認証エラーの場合
```bash
# 認証ファイルの確認
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# gcloud CLIでの認証（代替方法）
gcloud auth application-default login
```

### 音声フォーマットエラーの場合
```bash
# ffmpegで変換
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
```

### APIが有効になっていない場合
```bash
# APIの有効化確認
gcloud services list --enabled | grep speech
```

## 7. 高度な使用方法

### 長時間音声の処理
長時間音声（1分以上）の場合は、Google Cloud Storageを使用：

```python
# GCSにアップロード後
converter = SpeechToTextConverter()
result = converter.transcribe_long_file('gs://your-bucket/audio.wav')
```

### リアルタイム音声認識
マイクからの音声をリアルタイムで認識する場合は、ストリーミング認識APIを使用します。

## 8. セキュリティ注意事項

- 認証JSONファイルは絶対に公開リポジトリにコミットしない
- `.gitignore`に認証ファイルを追加
- 本番環境では環境変数やSecret Managerを使用