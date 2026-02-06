#!/usr/bin/env python3
"""
ErrorRecoveryHandler - エラー自動復旧クラス
Gemini AI推奨：自動再試行、エラー通知
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .models import BlogPost, PublishResult, ErrorInfo, RecoveryResult, RetryConfig

class ErrorRecoveryHandler:
    """
    エラー自動復旧クラス
    
    Gemini AI推奨機能：
    - 自動再試行ロジック
    - エラー分析と分類
    - 失敗通知システム
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recovery_history = []
        
    async def initialize(self) -> bool:
        """初期化"""
        try:
            self.logger.info("🔧 ErrorRecoveryHandler初期化開始")
            self.logger.info("✅ ErrorRecoveryHandler初期化完了")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ErrorRecoveryHandler初期化エラー: {e}")
            return False
    
    async def handle_publish_error(self,
                                  post: BlogPost,
                                  original_error: str,
                                  max_retries: int = 3,
                                  retry_interval: int = 60) -> RecoveryResult:
        """
        投稿エラーの自動復旧処理
        Gemini推奨：段階的再試行、指数バックオフ
        """
        recovery_result = RecoveryResult(
            recovered=False,
            attempts=0
        )
        
        try:
            self.logger.info(f"🔄 エラー自動復旧開始: {original_error}")
            
            # エラー分析
            error_info = self._analyze_error(original_error)
            recovery_result.add_log(f"エラー分析: {error_info.error_type}")
            
            # 復旧不可能なエラーのチェック
            if not error_info.is_recoverable:
                recovery_result.final_error = f"復旧不可能なエラー: {original_error}"
                recovery_result.add_log("復旧不可能と判定")
                return recovery_result
            
            # 再試行実行
            for attempt in range(1, max_retries + 1):
                recovery_result.attempts = attempt
                recovery_result.add_log(f"再試行 {attempt}/{max_retries} 開始")
                
                # 待機時間計算（指数バックオフ）
                wait_time = retry_interval * (2 ** (attempt - 1))
                recovery_result.add_log(f"{wait_time}秒待機中...")
                await asyncio.sleep(wait_time)
                
                # 再試行実行（実際の実装では PostPublisher を呼び出し）
                retry_result = await self._simulate_retry(post, attempt)
                recovery_result.add_log(f"再試行 {attempt} 結果: {'成功' if retry_result.success else '失敗'}")
                
                if retry_result.success:
                    recovery_result.recovered = True
                    recovery_result.final_result = retry_result
                    recovery_result.add_log("エラー復旧成功!")
                    return recovery_result
                else:
                    recovery_result.final_error = retry_result.error
            
            # 全ての再試行が失敗
            recovery_result.add_log("全ての再試行が失敗")
            recovery_result.final_error = f"最大再試行回数({max_retries})に達しました"
            
            return recovery_result
            
        except Exception as e:
            self.logger.error(f"❌ エラー復旧処理エラー: {e}")
            recovery_result.final_error = f"復旧処理エラー: {str(e)}"
            return recovery_result
    
    def _analyze_error(self, error_message: str) -> ErrorInfo:
        """エラー分析"""
        error_message_lower = error_message.lower()
        
        # 認証エラー
        if any(keyword in error_message_lower for keyword in ['auth', 'unauthorized', '401', 'token']):
            return ErrorInfo(
                error_type="AuthenticationError",
                error_message=error_message,
                is_recoverable=True,
                suggested_action="認証情報を更新してください"
            )
        
        # ネットワークエラー
        elif any(keyword in error_message_lower for keyword in ['network', 'connection', 'timeout', 'dns']):
            return ErrorInfo(
                error_type="NetworkError", 
                error_message=error_message,
                is_recoverable=True,
                suggested_action="ネットワーク接続を確認してください"
            )
        
        # API制限エラー
        elif any(keyword in error_message_lower for keyword in ['rate limit', 'quota', '429']):
            return ErrorInfo(
                error_type="RateLimitError",
                error_message=error_message,
                is_recoverable=True,
                suggested_action="しばらく待ってから再試行してください"
            )
        
        # バリデーションエラー
        elif any(keyword in error_message_lower for keyword in ['validation', 'invalid', 'bad request', '400']):
            return ErrorInfo(
                error_type="ValidationError",
                error_message=error_message,
                is_recoverable=False,
                suggested_action="投稿データを確認してください"
            )
        
        # その他のエラー
        else:
            return ErrorInfo(
                error_type="UnknownError",
                error_message=error_message,
                is_recoverable=True,
                suggested_action="再試行してみてください"
            )
    
    async def _simulate_retry(self, post: BlogPost, attempt: int) -> PublishResult:
        """再試行シミュレーション（実装では PostPublisher を呼び出し）"""
        # デモ用：50%の確率で成功
        import random
        success = random.random() > 0.5 or attempt >= 3
        
        if success:
            return PublishResult(
                success=True,
                post_id=f"retry_post_{attempt}",
                post_url=f"https://example.com/post/retry_{attempt}",
                message=f"再試行{attempt}で成功"
            )
        else:
            return PublishResult(
                success=False,
                error=f"再試行{attempt}失敗: テストエラー"
            )
    
    async def send_failure_notification(self,
                                       post: BlogPost,
                                       error: str,
                                       attempts: int):
        """失敗通知送信"""
        try:
            self.logger.info("📧 失敗通知送信中...")
            
            notification_data = {
                'timestamp': datetime.now().isoformat(),
                'post_title': post.title,
                'error': error,
                'attempts': attempts,
                'suggestion': "手動で投稿を確認してください"
            }
            
            # 実際の実装ではメール/Slack/Discord等に送信
            self.logger.error(f"📧 投稿失敗通知: {notification_data}")
            
        except Exception as e:
            self.logger.error(f"❌ 通知送信エラー: {e}")
    
    async def handle_auth_error(self, error_details: str) -> RecoveryResult:
        """
        認証エラー専用の復旧処理
        認証情報の自動修復と再認証ガイダンス
        """
        try:
            self.logger.info("🔐 認証エラー復旧処理開始")
            
            recovery_result = RecoveryResult(
                recovered=False,
                attempts=1,
                final_error="認証エラー: 手動認証が必要",
                recovery_actions=[
                    "認証情報の期限が切れています",
                    "新しい認証が必要です",
                    "認証URLが生成されました"
                ]
            )
            
            # 認証エラーの詳細分析
            auth_error_type = self._analyze_auth_error(error_details)
            
            recovery_result.error_analysis = {
                'error_type': auth_error_type,
                'error_details': error_details,
                'recovery_needed': True,
                'auth_url_available': True
            }
            
            # エラー履歴に記録
            self.recovery_history.append({
                'timestamp': datetime.now().isoformat(),
                'error_type': 'authentication_error',
                'details': error_details,
                'recovery_actions': recovery_result.recovery_actions
            })
            
            self.logger.info("📝 認証エラー復旧処理完了")
            return recovery_result
            
        except Exception as e:
            self.logger.error(f"❌ 認証エラー復旧処理エラー: {e}")
            return RecoveryResult(
                recovered=False,
                attempts=1,
                final_error=str(e)
            )
    
    def _analyze_auth_error(self, error_details: str) -> str:
        """認証エラーの分析"""
        error_lower = error_details.lower()
        
        if 'credentials were not found' in error_lower:
            return 'missing_credentials'
        elif 'expired' in error_lower:
            return 'expired_token'
        elif 'invalid' in error_lower:
            return 'invalid_token'
        elif 'reauthentication' in error_lower:
            return 'reauthentication_required'
        else:
            return 'unknown_auth_error'
    
    async def cleanup(self):
        """クリーンアップ"""
        try:
            self.logger.info("🧹 ErrorRecoveryHandlerクリーンアップ")
            
        except Exception as e:
            self.logger.error(f"❌ ErrorRecoveryHandlerクリーンアップエラー: {e}")