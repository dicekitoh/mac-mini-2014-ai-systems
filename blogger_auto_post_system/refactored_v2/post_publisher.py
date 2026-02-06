#!/usr/bin/env python3
"""
PostPublisher - 投稿実行特化クラス
Gemini AI推奨：外部サービスとの通信、データ整形
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import BlogPost, PublishResult, Platform
from .authentication_manager import AuthenticationManager

class PostPublisher:
    """
    投稿実行クラス
    
    Gemini AI推奨機能：
    - プラットフォーム固有のAPI呼び出し
    - データ整形とバリデーション
    - エラーハンドリング
    """
    
    def __init__(self, auth_manager: AuthenticationManager = None):
        self.logger = logging.getLogger(__name__)
        self.auth_manager = auth_manager or AuthenticationManager()
        
        # サービス接続
        self.blogger_service = None
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """初期化 - 強化された認証処理"""
        try:
            self.logger.info("🔌 PostPublisher初期化開始")
            
            # 認証状態確認・自動修復
            credentials = await self._ensure_valid_credentials()
            if not credentials:
                self.logger.error("❌ 有効な認証情報を取得できませんでした")
                return False
            
            # Blogger APIサービス構築
            self.blogger_service = build('blogger', 'v3', credentials=credentials)
            
            # 接続テスト
            await self._test_connection()
            
            self.is_initialized = True
            self.logger.info("✅ PostPublisher初期化完了")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ PostPublisher初期化エラー: {e}")
            return False
    
    async def publish(self, post: BlogPost) -> PublishResult:
        """
        投稿実行
        Gemini推奨：プラットフォーム固有の処理
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            self.logger.info(f"📤 投稿実行開始: {post.title}")
            
            # プラットフォーム別処理
            if post.platform == Platform.BLOGGER.value:
                return await self._publish_to_blogger(post)
            else:
                return PublishResult(
                    success=False,
                    error=f"未対応のプラットフォーム: {post.platform}"
                )
                
        except Exception as e:
            self.logger.error(f"❌ 投稿実行エラー: {e}")
            return PublishResult(
                success=False,
                error=str(e)
            )
    
    async def _publish_to_blogger(self, post: BlogPost) -> PublishResult:
        """Blogger投稿処理"""
        try:
            # ブログID取得
            blog_id = await self._get_blog_id()
            if not blog_id:
                return PublishResult(
                    success=False,
                    error="ブログIDの取得に失敗"
                )
            
            # 投稿データ準備
            post_data = self._prepare_blogger_data(post)
            
            # Blogger API呼び出し
            self.logger.info("🚀 Blogger APIに投稿中...")
            
            request = self.blogger_service.posts().insert(
                blogId=blog_id,
                body=post_data
            )
            response = request.execute()
            
            # 結果処理
            post_id = response.get('id')
            post_url = response.get('url')
            published_date = response.get('published')
            
            self.logger.info(f"✅ Blogger投稿成功: {post_url}")
            
            return PublishResult(
                success=True,
                post_id=post_id,
                post_url=post_url,
                platform=Platform.BLOGGER.value,
                published_at=datetime.fromisoformat(published_date.replace('Z', '+00:00')) if published_date else datetime.now(),
                message="投稿が正常に公開されました"
            )
            
        except HttpError as e:
            error_message = f"Blogger API エラー: {e.resp.status} - {e.content.decode()}"
            self.logger.error(error_message)
            
            # 認証エラーの場合
            if e.resp.status == 401:
                return PublishResult(
                    success=False,
                    error=error_message,
                    requires_reauth=True
                )
            
            return PublishResult(
                success=False,
                error=error_message,
                platform=Platform.BLOGGER.value
            )
            
        except Exception as e:
            error_message = f"Blogger投稿エラー: {str(e)}"
            self.logger.error(error_message)
            return PublishResult(
                success=False,
                error=error_message,
                platform=Platform.BLOGGER.value
            )
    
    async def _get_blog_id(self) -> Optional[str]:
        """ブログID取得"""
        try:
            # ユーザーのブログ一覧取得
            blogs_result = self.blogger_service.blogs().listByUser(userId='self').execute()
            blogs = blogs_result.get('items', [])
            
            if not blogs:
                self.logger.error("ブログが見つかりません")
                return None
            
            # 最初のブログのIDを使用
            blog_id = blogs[0]['id']
            blog_name = blogs[0].get('name', 'Unknown')
            blog_url = blogs[0].get('url', 'Unknown')
            
            self.logger.info(f"📖 ブログ情報: {blog_name} ({blog_url})")
            return blog_id
            
        except Exception as e:
            self.logger.error(f"❌ ブログID取得エラー: {e}")
            return None
    
    def _prepare_blogger_data(self, post: BlogPost) -> Dict[str, Any]:
        """Blogger用データ準備"""
        post_data = {
            'title': post.title,
            'content': post.content
        }
        
        # ラベル追加
        if post.labels:
            post_data['labels'] = post.labels
        
        # 公開設定
        if post.publish_immediately:
            post_data['published'] = datetime.now().isoformat() + 'Z'
        
        # プラットフォーム固有設定適用
        blogger_settings = post.platform_settings.get('blogger', {})
        if blogger_settings:
            post_data.update(blogger_settings)
        
        return post_data
    
    async def _test_connection(self):
        """接続テスト"""
        try:
            self.logger.info("🔍 Blogger API接続テスト中...")
            
            # ユーザー情報取得で接続テスト
            blogs_result = self.blogger_service.blogs().listByUser(userId='self').execute()
            blogs = blogs_result.get('items', [])
            
            self.logger.info(f"✅ 接続テスト成功: {len(blogs)}個のブログを確認")
            
        except Exception as e:
            self.logger.error(f"❌ 接続テスト失敗: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """状態取得"""
        try:
            status = {
                'initialized': self.is_initialized,
                'service_available': self.blogger_service is not None,
                'platform_support': {
                    'blogger': True,
                    'wordpress': False,
                    'medium': False
                }
            }
            
            # サービスが利用可能な場合、追加情報取得
            if self.is_initialized and self.blogger_service:
                try:
                    blogs_result = self.blogger_service.blogs().listByUser(userId='self').execute()
                    blogs = blogs_result.get('items', [])
                    
                    status.update({
                        'connected_blogs': len(blogs),
                        'primary_blog': {
                            'name': blogs[0].get('name') if blogs else None,
                            'url': blogs[0].get('url') if blogs else None
                        } if blogs else None
                    })
                    
                except Exception as e:
                    status['connection_error'] = str(e)
            
            return status
            
        except Exception as e:
            return {'error': str(e)}
    
    async def preview_post(self, post: BlogPost) -> Dict[str, Any]:
        """投稿プレビュー（実際に投稿せずにデータ確認）"""
        try:
            preview_data = {}
            
            if post.platform == Platform.BLOGGER.value:
                preview_data = self._prepare_blogger_data(post)
            
            return {
                'success': True,
                'platform': post.platform,
                'preview_data': preview_data,
                'estimated_size': len(str(preview_data)),
                'validation': self._validate_post_data(post)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_post_data(self, post: BlogPost) -> Dict[str, Any]:
        """投稿データバリデーション"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 必須フィールドチェック
        if not post.title or not post.title.strip():
            validation_result['valid'] = False
            validation_result['errors'].append("タイトルが空です")
        
        if not post.content or not post.content.strip():
            validation_result['valid'] = False
            validation_result['errors'].append("コンテンツが空です")
        
        # 長さチェック
        if len(post.title) > 200:
            validation_result['warnings'].append("タイトルが長すぎる可能性があります")
        
        if len(post.content) < 100:
            validation_result['warnings'].append("コンテンツが短すぎる可能性があります")
        
        # ラベル数チェック
        if len(post.labels) > 20:
            validation_result['warnings'].append("ラベル数が多すぎる可能性があります")
        
        return validation_result
    
    async def _ensure_valid_credentials(self) -> Optional['Credentials']:
        """
        有効な認証情報を確保する強化メソッド
        自動修復・フォールバック処理を含む
        """
        try:
            self.logger.info("🔐 認証情報確保開始...")
            
            # Step 1: 現在の認証情報確認
            credentials = self.auth_manager.get_credentials()
            if credentials and not credentials.expired:
                self.logger.info("✅ 現在の認証情報は有効")
                return credentials
            
            # Step 2: 認証状態の詳細確認
            self.logger.info("🔍 認証状態詳細確認中...")
            auth_status = await self.auth_manager.check_auth_status()
            
            if auth_status.is_valid and not auth_status.needs_refresh:
                # 認証は有効だがget_credentials()で取得できない場合
                credentials = self.auth_manager.get_credentials()
                if credentials:
                    self.logger.info("✅ 認証状態確認により認証情報を取得")
                    return credentials
            
            # Step 3: リフレッシュが必要な場合は自動修復試行
            if auth_status.needs_refresh:
                self.logger.info("🔄 自動修復試行中...")
                repair_result = await self.auth_manager.auto_repair_auth()
                
                if repair_result:
                    credentials = self.auth_manager.get_credentials()
                    if credentials:
                        self.logger.info("✅ 自動修復成功")
                        return credentials
                else:
                    self.logger.warning("⚠️ 自動修復失敗")
            
            # Step 4: フォールバック - 認証不可の場合
            self.logger.error("❌ 有効な認証情報を取得できませんでした")
            self.logger.info("💡 新しい認証が必要です")
            
            # 認証URL生成（ログ出力のみ）
            try:
                auth_url = await self.auth_manager.generate_auth_url()
                self.logger.info(f"🔗 新しい認証URL: {auth_url}")
            except Exception as url_error:
                self.logger.error(f"❌ 認証URL生成エラー: {url_error}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ 認証情報確保エラー: {e}")
            return None