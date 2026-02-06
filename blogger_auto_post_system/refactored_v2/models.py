#!/usr/bin/env python3
"""
Models - データ構造定義
Gemini AI推奨：型安全性と明確なデータ構造
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum

class Platform(Enum):
    """投稿プラットフォーム"""
    BLOGGER = "blogger"
    WORDPRESS = "wordpress"
    MEDIUM = "medium"

class PostStatus(Enum):
    """投稿状態"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class BlogPost:
    """ブログ投稿データ"""
    title: str
    content: str
    labels: List[str] = field(default_factory=list)
    platform: str = Platform.BLOGGER.value
    status: PostStatus = PostStatus.DRAFT
    
    # メタデータ
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    author: Optional[str] = None
    
    # 投稿設定
    publish_immediately: bool = True
    scheduled_time: Optional[datetime] = None
    
    # プラットフォーム固有設定
    platform_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初期化後の処理"""
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def update(self):
        """更新時刻更新"""
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'title': self.title,
            'content': self.content,
            'labels': self.labels,
            'platform': self.platform,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author': self.author,
            'publish_immediately': self.publish_immediately,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'platform_settings': self.platform_settings
        }

@dataclass
class PublishResult:
    """投稿結果"""
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None
    
    # 追加情報
    platform: Optional[str] = None
    published_at: Optional[datetime] = None
    
    # 認証関連
    requires_reauth: bool = False
    auth_url: Optional[str] = None
    
    # 再試行関連
    recovery_attempts: int = 0
    schedule_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'success': self.success,
            'post_id': self.post_id,
            'post_url': self.post_url,
            'error': self.error,
            'message': self.message,
            'platform': self.platform,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'requires_reauth': self.requires_reauth,
            'auth_url': self.auth_url,
            'recovery_attempts': self.recovery_attempts,
            'schedule_id': self.schedule_id
        }

@dataclass
class AuthStatus:
    """認証状態"""
    is_valid: bool
    expires_at: Optional[datetime] = None
    needs_refresh: bool = False
    error_message: Optional[str] = None
    user_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'is_valid': self.is_valid,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'needs_refresh': self.needs_refresh,
            'error_message': self.error_message,
            'user_info': self.user_info
        }

@dataclass
class ErrorInfo:
    """エラー情報"""
    error_type: str
    error_message: str
    occurred_at: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    
    # 復旧関連
    is_recoverable: bool = True
    suggested_action: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'error_type': self.error_type,
            'error_message': self.error_message,
            'occurred_at': self.occurred_at.isoformat(),
            'context': self.context,
            'stack_trace': self.stack_trace,
            'is_recoverable': self.is_recoverable,
            'suggested_action': self.suggested_action
        }

@dataclass
class RetryConfig:
    """再試行設定"""
    max_retries: int = 3
    retry_interval: int = 60  # 秒
    backoff_multiplier: float = 2.0
    max_retry_interval: int = 300  # 秒
    
    def get_retry_delay(self, attempt: int) -> int:
        """再試行間隔計算"""
        delay = self.retry_interval * (self.backoff_multiplier ** attempt)
        return min(int(delay), self.max_retry_interval)

@dataclass
class RecoveryResult:
    """復旧結果"""
    recovered: bool
    attempts: int
    final_result: Optional[PublishResult] = None
    final_error: Optional[str] = None
    recovery_log: List[str] = field(default_factory=list)
    
    def add_log(self, message: str):
        """ログ追加"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.recovery_log.append(f"[{timestamp}] {message}")

@dataclass
class ScheduledPost:
    """スケジュール済み投稿"""
    id: str
    post: BlogPost
    scheduled_time: datetime
    retry_config: RetryConfig
    
    # 状態
    status: PostStatus = PostStatus.SCHEDULED
    attempts: int = 0
    last_attempt: Optional[datetime] = None
    last_error: Optional[str] = None
    
    def update_attempt(self, error: Optional[str] = None):
        """試行回数更新"""
        self.attempts += 1
        self.last_attempt = datetime.now()
        self.last_error = error
        
        if error:
            self.status = PostStatus.FAILED if self.attempts >= self.retry_config.max_retries else PostStatus.RETRYING
        else:
            self.status = PostStatus.PUBLISHED
    
    def should_retry(self) -> bool:
        """再試行すべきか判定"""
        return (
            self.status in [PostStatus.FAILED, PostStatus.RETRYING] and
            self.attempts < self.retry_config.max_retries
        )
    
    def get_next_retry_time(self) -> datetime:
        """次回再試行時刻計算"""
        if not self.last_attempt:
            return datetime.now()
        
        delay = self.retry_config.get_retry_delay(self.attempts)
        return self.last_attempt + timedelta(seconds=delay)

@dataclass
class SystemStatus:
    """システム状態"""
    initialized: bool
    auth_status: AuthStatus
    publisher_ready: bool
    scheduler_active: bool
    error_handler_ready: bool
    
    # 統計情報
    total_posts: int = 0
    successful_posts: int = 0
    failed_posts: int = 0
    pending_posts: int = 0
    
    last_activity: Optional[datetime] = None
    
    def get_success_rate(self) -> float:
        """成功率計算"""
        if self.total_posts == 0:
            return 0.0
        return (self.successful_posts / self.total_posts) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'initialized': self.initialized,
            'auth_status': self.auth_status.to_dict(),
            'publisher_ready': self.publisher_ready,
            'scheduler_active': self.scheduler_active,
            'error_handler_ready': self.error_handler_ready,
            'total_posts': self.total_posts,
            'successful_posts': self.successful_posts,
            'failed_posts': self.failed_posts,
            'pending_posts': self.pending_posts,
            'success_rate': self.get_success_rate(),
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }

# ユーティリティ関数
def create_blog_post(title: str, 
                    content: str, 
                    labels: List[str] = None,
                    platform: Union[str, Platform] = Platform.BLOGGER) -> BlogPost:
    """BlogPost作成ヘルパー"""
    if isinstance(platform, Platform):
        platform = platform.value
    
    return BlogPost(
        title=title,
        content=content,
        labels=labels or [],
        platform=platform
    )

def create_publish_result(success: bool, 
                         post_id: str = None,
                         post_url: str = None,
                         error: str = None) -> PublishResult:
    """PublishResult作成ヘルパー"""
    return PublishResult(
        success=success,
        post_id=post_id,
        post_url=post_url,
        error=error,
        published_at=datetime.now() if success else None
    )