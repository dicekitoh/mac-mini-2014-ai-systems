#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Google TODO Manager - Google Tasks API連携システム

import logging
import pickle
import os
from datetime import datetime, timezone
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleTodoManager:
    def __init__(self, token_file='/home/fujinosuke/google_tasks_new.pickle'):
        """Google Tasks API管理クラス"""
        self.token_file = token_file
        self.service = self._init_google_service()
    
    def _init_google_service(self):
        """Google Tasks APIサービスを初期化"""
        try:
            if not os.path.exists(self.token_file):
                logger.error(f"認証ファイル {self.token_file} が見つかりません")
                return None
                
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
            
            if creds and creds.expired and creds.refresh_token:
                logger.info("トークンの有効期限切れ。リフレッシュ中...")
                creds.refresh(Request())
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                logger.info("トークンのリフレッシュ完了")
            
            service = build('tasks', 'v1', credentials=creds)
            logger.info("Google Tasks API初期化成功")
            return service
        except Exception as e:
            logger.error(f"Google Tasks API初期化エラー: {e}")
            return None
    
    def authenticate(self):
        """Google Tasks API認証テスト"""
        try:
            if not self.service:
                self.service = self._init_google_service()
                if not self.service:
                    return False
            
            # APIテスト実行
            result = self.service.tasklists().list().execute()
            logger.info("Google Tasks API認証成功")
            return True
        except Exception as e:
            logger.error(f"Google Tasks API認証エラー: {e}")
            return False
    
    def get_task_lists(self):
        """タスクリスト一覧を取得"""
        try:
            if not self.service:
                logger.error("サービス未初期化")
                return []
            
            result = self.service.tasklists().list().execute()
            task_lists = result.get('items', [])
            
            formatted_lists = []
            for task_list in task_lists:
                formatted_lists.append({
                    'id': task_list.get('id'),
                    'title': task_list.get('title'),
                    'updated': task_list.get('updated')
                })
            
            logger.info(f"タスクリスト取得: {len(formatted_lists)}件")
            return formatted_lists
            
        except Exception as e:
            logger.error(f"タスクリスト取得エラー: {e}")
            return []
    
    def get_tasks(self, tasklist_id=None):
        """タスク一覧を取得"""
        try:
            if not self.service:
                logger.error("サービス未初期化")
                return []
            
            # デフォルトタスクリストを使用
            if not tasklist_id:
                task_lists = self.get_task_lists()
                if not task_lists:
                    logger.error("タスクリストが見つかりません")
                    return []
                tasklist_id = task_lists[0]['id']
            
            result = self.service.tasks().list(tasklist=tasklist_id).execute()
            tasks = result.get('items', [])
            
            formatted_tasks = []
            for task in tasks:
                formatted_tasks.append({
                    'id': task.get('id'),
                    'title': task.get('title'),
                    'notes': task.get('notes', ''),
                    'status': task.get('status'),
                    'due': task.get('due'),
                    'completed': task.get('completed'),
                    'updated': task.get('updated')
                })
            
            logger.info(f"タスク取得: {len(formatted_tasks)}件")
            return formatted_tasks
            
        except Exception as e:
            logger.error(f"タスク取得エラー: {e}")
            return []
    
    def add_task(self, title, notes='', due_date=None, tasklist_id=None):
        """新しいタスクを追加"""
        try:
            if not self.service:
                logger.error("サービス未初期化")
                return None
            
            # デフォルトタスクリストを使用
            if not tasklist_id:
                task_lists = self.get_task_lists()
                if not task_lists:
                    logger.error("タスクリストが見つかりません")
                    return None
                tasklist_id = task_lists[0]['id']
            
            task = {
                'title': title,
                'notes': notes
            }
            
            if due_date:
                task['due'] = due_date
            
            result = self.service.tasks().insert(
                tasklist=tasklist_id,
                body=task
            ).execute()
            
            logger.info(f"タスク追加成功: {title}")
            return result
            
        except Exception as e:
            logger.error(f"タスク追加エラー: {e}")
            return None
    
    def complete_task(self, task_id, tasklist_id=None):
        """タスクを完了にする"""
        try:
            if not self.service:
                logger.error("サービス未初期化")
                return False
            
            # デフォルトタスクリストを使用
            if not tasklist_id:
                task_lists = self.get_task_lists()
                if not task_lists:
                    logger.error("タスクリストが見つかりません")
                    return False
                tasklist_id = task_lists[0]['id']
            
            task = {
                'id': task_id,
                'status': 'completed'
            }
            
            result = self.service.tasks().update(
                tasklist=tasklist_id,
                task=task_id,
                body=task
            ).execute()
            
            logger.info(f"タスク完了: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"タスク完了エラー: {e}")
            return False
    
    def delete_task(self, task_id, tasklist_id=None):
        """タスクを削除"""
        try:
            if not self.service:
                logger.error("サービス未初期化")
                return False
            
            # デフォルトタスクリストを使用
            if not tasklist_id:
                task_lists = self.get_task_lists()
                if not task_lists:
                    logger.error("タスクリストが見つかりません")
                    return False
                tasklist_id = task_lists[0]['id']
            
            self.service.tasks().delete(
                tasklist=tasklist_id,
                task=task_id
            ).execute()
            
            logger.info(f"タスク削除: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"タスク削除エラー: {e}")
            return False

def main():
    """メイン実行部分 - テストコード"""
    print("Google TODO Manager テスト実行")
    
    # マネージャー初期化
    todo_manager = GoogleTodoManager()
    
    # 認証テスト
    if not todo_manager.authenticate():
        print("❌ Google認証に失敗しました")
        return
    
    print("✅ Google Tasks API認証成功")
    
    # タスクリスト一覧表示
    print("\n📋 タスクリスト一覧:")
    task_lists = todo_manager.get_task_lists()
    for i, task_list in enumerate(task_lists, 1):
        print(f"{i}. {task_list['title']} (ID: {task_list['id']})")
    
    if not task_lists:
        print("タスクリストが見つかりません")
        return
    
    # 最初のタスクリストのタスク一覧表示
    default_list_id = task_lists[0]['id']
    print(f"\n📝 タスク一覧 ({task_lists[0]['title']}):")
    tasks = todo_manager.get_tasks(default_list_id)
    
    if not tasks:
        print("タスクがありません")
    else:
        for i, task in enumerate(tasks, 1):
            status_emoji = "✅" if task['status'] == 'completed' else "⏳"
            print(f"{i}. {status_emoji} {task['title']}")
            if task['notes']:
                print(f"   メモ: {task['notes']}")
            if task['due']:
                print(f"   期限: {task['due']}")
    
    # テストタスク追加
    print("\n➕ テストタスク追加中...")
    test_task = todo_manager.add_task(
        title="Claude TODOテスト",
        notes="Google Tasks API連携テスト"
    )
    
    if test_task:
        print("✅ テストタスク追加成功")
        print(f"タスクID: {test_task['id']}")
    else:
        print("❌ テストタスク追加失敗")

if __name__ == '__main__':
    main()