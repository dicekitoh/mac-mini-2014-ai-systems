# Google APIs 有効化推奨順序

## 用途別推奨

### 📄 一般的なOCR（写真・スクリーンショット等）
**Cloud Vision API のみ** を有効化
- 最もコストパフォーマンスが良い
- 日本語・英語対応
- 手書き文字にも対応

### 📋 ビジネス文書・フォーム・表の処理
**両方とも** を有効化
1. Cloud Vision API（基本OCR用）
2. Cloud Document AI API（構造化文書用）

### 💰 コスト重視
**Cloud Vision API のみ**
- Document AI APIは高機能だが高コスト

## 推奨設定（段階的）

### Phase 1: 基本OCR
```
✅ Cloud Vision API
❌ Cloud Document AI API
❌ ARCore API（不要）
```

### Phase 2: 高精度文書処理
```
✅ Cloud Vision API  
✅ Cloud Document AI API
❌ ARCore API（不要）
```

## 料金比較（概算）

- **Vision API**: $1.50/1000回 (TEXT_DETECTION)
- **Document AI API**: $0.05/ページ (一般プロセッサー)

## 結論

**まずは Cloud Vision API のみ有効化** することを推奨。
必要に応じて後からDocument AI APIを追加可能。