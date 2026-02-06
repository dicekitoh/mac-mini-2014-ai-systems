#!/usr/bin/env python3
"""
BlogPostingService - ファサードパターン
Gemini AI提案アーキテクチャによるメイン処理クラス
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from .authentication_manager import AuthenticationManager
from .post_publisher import PostPublisher
from .post_scheduler import PostScheduler
from .error_recovery_handler import ErrorRecoveryHandler
from .models import BlogPost, PublishResult, AuthStatus

@dataclass
class PublishConfig:
    """投稿設定"""
    platform: str = "blogger"
    auto_retry: bool = True
    max_retries: int = 3
    retry_interval: int = 60  # 秒
    schedule_time: Optional[datetime] = None

class BlogPostingService:
    """
    ブログ投稿サービス - ファサード

    Gemini AI提案：
    - 認証、投稿、エラー回復を抽象化
    - ワンクリック即時投稿の実現
    - エラー自動回復機能
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 依存コンポーネントの初期化
        self.auth_manager = AuthenticationManager()
        self.publisher = PostPublisher()
        self.scheduler = PostScheduler()
        self.error_handler = ErrorRecoveryHandler()

        # 状態管理
        self.is_initialized = False
        self.last_auth_check = None

    async def initialize(self) -> bool:
        """サービス初期化"""
        try:
            self.logger.info("🚀 BlogPostingService初期化開始")

            # 認証状態確認
            auth_status = await self.auth_manager.check_auth_status()
            if not auth_status.is_valid:
                self.logger.warning("認証が必要です")
                return False

            # コンポーネント依存解決
            await self.publisher.initialize()
            await self.scheduler.initialize()
            await self.error_handler.initialize()

            self.is_initialized = True
            self.last_auth_check = datetime.now()

            self.logger.info("✅ BlogPostingService初期化完了")
            return True

        except Exception as e:
            self.logger.error(f"❌ 初期化エラー: {e}")
            return False

    async def quick_setup(self) -> Dict[str, Any]:
        """クイックセットアップ - 認証から投稿準備までを一括"""
        setup_result = {
            'success': False,
            'auth_url': None,
            'ready_to_post': False,
            'message': ''
        }

        try:
            self.logger.info("① クイックセットアップ実行")

            # 認証状態確認
            auth_status = await self.auth_manager.check_auth_status()

            if not auth_status.is_valid:
                # 認証URL発行
                auth_url = await self.auth_manager.generate_auth_url()
                setup_result.update({
                    'auth_url': auth_url,
                    'message': '認証が必要です。URLにアクセスして認証してください。'
                })
                return setup_result

            # 初期化処理
            init_success = await self.initialize()
            if init_success:
                setup_result.update({
                    'success': True,
                    'ready_to_post': True,
                    'message': 'セットアップ完了：投稿準備OKです。'
                })
            else:
                setup_result['message'] = 'セットアップに失敗しました。'

            return setup_result

        except Exception as e:
            self.logger.error(f"❌ クイックセットアップエラー: {e}")
            setup_result['message'] = f'エラー: {str(e)}'
            return setup_result

    async def interactive_auth_setup(self) -> bool:
        """
        Handles the authentication interactively. If authentication is required,
        it provides the URL, waits for the user to get the code, and processes it.
        """
        auth_status = await self.auth_manager.check_auth_status()
        # Try to auto-repair first if refresh token is available
        if auth_status.needs_refresh:
            print("🔄 Token has expired, attempting to refresh automatically...")
            repaired = await self.auth_manager.auto_repair_auth()
            if repaired:
                print("✅ Token refreshed successfully.")
                auth_status = await self.auth_manager.check_auth_status() # Re-check status
            else:
                print("❌ Automatic refresh failed.")

        if auth_status.is_valid and not auth_status.needs_refresh:
            print("✅ Authentication is valid.")
            return await self.initialize()

        # If still not valid, start the full interactive flow
        try:
            auth_url = await self.auth_manager.generate_auth_url()
            print("\n❗️ Authentication is required.")
            print(f"   1. Open this URL in your browser:\n      {auth_url}\n")
            print("   2. Authorize the application.")
            print("   3. Copy the authorization code you receive.")

            auth_code = input(">>> Paste the authorization code here and press Enter: ")

            print("\n🔄 Processing authorization code...")
            success = await self.auth_manager.process_auth_code(auth_code.strip())

            if success:
                print("✅ Authentication successful!")
                return await self.initialize()
            else:
                print("❌ Authentication failed. Please check the code and try again.")
                return False

        except Exception as e:
            self.logger.error(f"Error during interactive setup: {e}")
            print(f"❌ An error occurred during setup: {e}")
            return False

    async def one_click_post(self,
                           title: str,
                           content: str,
                           labels: List[str] = None,
                           config: PublishConfig = None) -> PublishResult:
        """
        ワンクリック即時投稿
        Gemini提案：引数設定により柔軟性を担保しつつ投稿処理
        """
        if not self.is_initialized:
            await self.initialize()

        config = config or PublishConfig()
        labels = labels or []

        post = BlogPost(
            title=title,
            content=content,
            labels=labels,
            platform=config.platform
        )

        try:
            self.logger.info(f"▶️ ワンクリック投稿実行: {title}")

            # 即時投稿 or スケジュール投稿
            if config.schedule_time:
                return await self._schedule_post(post, config)
            else:
                return await self._publish_now(post, config)

        except Exception as e:
            self.logger.error(f"❌ ワンクリック投稿エラー: {e}")
            return PublishResult(
                success=False,
                error=str(e),
                post_id=None,
                post_url=None
            )

    async def _publish_now(self, post: BlogPost, config: PublishConfig) -> PublishResult:
        """即時投稿処理"""
        try:
            # 認証再確認
            auth_status = await self.auth_manager.check_auth_status()
            if not auth_status.is_valid:
                # 自動認証修復試行
                repair_success = await self.auth_manager.auto_repair_auth()
                if not repair_success:
                    return PublishResult(
                        success=False,
                        error="認証エラー: 認証修復に失敗",
                        requires_reauth=True
                    )

            # 投稿処理
            result = await self.publisher.publish(post)

            if result.success:
                self.logger.info(f"✅ 投稿成功: {result.post_url}")
                return result
            else:
                # 認証エラーの場合は特別処理
                if result.requires_reauth or 'credentials' in str(result.error).lower():
                    auth_recovery = await self.error_handler.handle_auth_error(str(result.error))
                    return PublishResult(
                        success=False,
                        error=auth_recovery.final_error,
                        requires_reauth=True,
                        recovery_attempts=auth_recovery.attempts
                    )

                # その他のエラーは通常自動回復
                if config.auto_retry:
                    return await self._handle_publish_error(post, config, result)
                return result

        except Exception as e:
            self.logger.error(f"❌ 投稿処理エラー: {e}")
            return PublishResult(
                success=False,
                error=str(e)
            )

    async def _schedule_post(self, post: BlogPost, config: PublishConfig) -> PublishResult:
        """スケジュール投稿"""
        try:
            schedule_id = await self.scheduler.schedule_post(
                post,
                config.schedule_time,
                retry_config={
                    'auto_retry': config.auto_retry,
                    'max_retries': config.max_retries,
                    'retry_interval': config.retry_interval
                }
            )

            return PublishResult(
                success=True,
                message=f"投稿をスケジュール予約: {config.schedule_time}",
                schedule_id=schedule_id
            )

        except Exception as e:
            self.logger.error(f"❌ スケジュール投稿エラー: {e}")
            return PublishResult(
                success=False,
                error=str(e)
            )

    async def _handle_publish_error(self,
                                   post: BlogPost,
                                   config: PublishConfig,
                                   original_result: PublishResult) -> PublishResult:
        """
        エラー自動回復処理
        Gemini提案：指数バックオフ、試行回数上限、最終的な通知
        """
        try:
            self.logger.info("‼️ エラー自動回復実行")

            # エラーハンドラに委譲
            recovery_result = await self.error_handler.handle_publish_error(
                post=post,
                original_error=original_result.error,
                max_retries=config.max_retries,
                retry_interval=config.retry_interval
            )

            if recovery_result.recovered:
                self.logger.info("✅ エラー自動回復成功")
                return recovery_result.final_result
            else:
                self.logger.error(f"❌ エラー自動回復失敗: {recovery_result.final_error}")

                # 失敗通知
                await self.error_handler.send_failure_notification(
                    post=post,
                    error=recovery_result.final_error,
                    attempts=recovery_result.attempts
                )

                return PublishResult(
                    success=False,
                    error=recovery_result.final_error,
                    recovery_attempts=recovery_result.attempts
                )

        except Exception as e:
            self.logger.error(f"❌ エラーハンドリング失敗: {e}")
            return PublishResult(
                success=False,
                error=f'回復処理エラー: {str(e)}'
            )

    async def get_status(self) -> Dict[str, Any]:
        """システム状態取得"""
        try:
            auth_status = await self.auth_manager.get_status()
            publisher_status = await self.publisher.get_status()
            scheduler_status = await self.scheduler.get_status()

            return {
                'initialized': self.is_initialized,
                'auth_status': auth_status,
                'publisher_status': publisher_status,
                'scheduler_status': scheduler_status,
                'last_auth_check': self.last_auth_check.isoformat() if self.last_auth_check else None
            }

        except Exception as e:
            self.logger.error(f"❌ 状態取得エラー: {e}")
            return {'error': str(e)}

    async def cleanup(self):
        """リソースクリーンアップ"""
        try:
            self.logger.info("🧹 BlogPostingServiceクリーンアップ")

            if hasattr(self, 'scheduler'):
                await self.scheduler.cleanup()
            if hasattr(self, 'error_handler'):
                await self.error_handler.cleanup()

            self.is_initialized = False

        except Exception as e:
            self.logger.error(f"❌ クリーンアップエラー: {e}")

#使いやすいファクトリー関数
async def create_blog_service() -> "BlogPostingService":
    """ブログサービス作成 - ファクトリー関数"""
    service = BlogPostingService()
    await service.initialize()
    return service
