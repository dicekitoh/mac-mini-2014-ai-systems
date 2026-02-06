#!/usr/bin/env python3
"""
PostScheduler - スケジュール管理クラス
Gemini AI推奨：スケジュール管理と実行
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from .models import BlogPost, ScheduledPost, RetryConfig, PostStatus

class PostScheduler:
    """
    投稿スケジュール管理クラス
    
    Gemini AI推奨機能：
    - スケジュール投稿管理
    - 自動実行
    - 再試行制御
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scheduled_posts: Dict[str, ScheduledPost] = {}
        self.is_running = False
        self.scheduler_task = None
        
    async def initialize(self) -> bool:
        """初期化"""
        try:
            self.logger.info("📅 PostScheduler初期化開始")
            self.is_running = True
            
            # スケジューラータスク開始
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            self.logger.info("✅ PostScheduler初期化完了")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ PostScheduler初期化エラー: {e}")
            return False
    
    async def schedule_post(self, 
                           post: BlogPost, 
                           scheduled_time: datetime,
                           retry_config: Dict[str, Any] = None) -> str:
        """投稿スケジュール追加"""
        try:
            schedule_id = str(uuid.uuid4())
            
            retry_cfg = RetryConfig(
                max_retries=retry_config.get('max_retries', 3),
                retry_interval=retry_config.get('retry_interval', 60),
                auto_retry=retry_config.get('auto_retry', True)
            ) if retry_config else RetryConfig()
            
            scheduled_post = ScheduledPost(
                id=schedule_id,
                post=post,
                scheduled_time=scheduled_time,
                retry_config=retry_cfg
            )
            
            self.scheduled_posts[schedule_id] = scheduled_post
            
            self.logger.info(f"📅 投稿スケジュール追加: {schedule_id} at {scheduled_time}")
            return schedule_id
            
        except Exception as e:
            self.logger.error(f"❌ スケジュール追加エラー: {e}")
            raise
    
    async def _scheduler_loop(self):
        """スケジューラーループ"""
        try:
            while self.is_running:
                await self._check_scheduled_posts()
                await asyncio.sleep(30)  # 30秒間隔でチェック
                
        except Exception as e:
            self.logger.error(f"❌ スケジューラーループエラー: {e}")
    
    async def _check_scheduled_posts(self):
        """スケジュール済み投稿確認"""
        current_time = datetime.now()
        
        for schedule_id, scheduled_post in list(self.scheduled_posts.items()):
            if scheduled_post.scheduled_time <= current_time:
                # TODO: 実際の投稿実行はPublisherに委譲
                scheduled_post.update_attempt()
                self.logger.info(f"🚀 スケジュール投稿実行: {schedule_id}")
    
    async def get_status(self) -> Dict[str, Any]:
        """状態取得"""
        return {
            'initialized': self.is_running,
            'scheduled_count': len(self.scheduled_posts),
            'active_schedules': [
                {
                    'id': sp.id,
                    'title': sp.post.title,
                    'scheduled_time': sp.scheduled_time.isoformat(),
                    'status': sp.status.value
                }
                for sp in self.scheduled_posts.values()
            ]
        }
    
    async def cleanup(self):
        """クリーンアップ"""
        try:
            self.is_running = False
            if self.scheduler_task:
                self.scheduler_task.cancel()
                
        except Exception as e:
            self.logger.error(f"❌ PostSchedulerクリーンアップエラー: {e}")