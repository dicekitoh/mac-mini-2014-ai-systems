#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Google Calendar Manager - Google Calendar API連携システム

import logging
import pickle
import os
from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Googleカレンダーのスコープ
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarManager:
    def __init__(self, credentials_file='/home/rootmax/macmini2014_mount/new_credentials.json',
                 token_file='/home/fujinosuke/google_calendar.pickle'):
        """Google Calendar API管理クラス"""
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self._init_google_service()
    
    def _init_google_service(self):
        """Google Calendar APIサービスを初期化"""
        creds = None
        
        # トークンファイルが存在する場合は読み込む
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # 有効な認証情報がない場合は新規取得
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("トークンの有効期限切れ。リフレッシュ中...")
                creds.refresh(Request())
            else:
                logger.info("新規認証フロー開始...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # トークンを保存
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            logger.info("認証完了")
        
        try:
            service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar API初期化成功")
            return service
        except Exception as e:
            logger.error(f"Google Calendar API初期化エラー: {e}")
            return None
    
    def add_work_schedule(self, date, shift_type, calendar_id='primary'):
        """勤務予定をカレンダーに追加"""
        if not self.service:
            logger.error("Google Calendar APIが初期化されていません")
            return None
        
        # 勤務タイプに基づいて時間を設定
        shift_times = {
            '明け': {'start': '00:00', 'end': '09:00', 'summary': '明け勤務'},
            '夜勤': {'start': '17:00', 'end': '09:00', 'summary': '夜勤', 'next_day': True},
            '日勤': {'start': '09:00', 'end': '17:00', 'summary': '日勤'},
            '遅番': {'start': '13:00', 'end': '21:00', 'summary': '遅番'},
            'B勤務': {'start': '08:00', 'end': '16:00', 'summary': 'B勤務'},
            '休み': {'all_day': True, 'summary': '休み'},
            '有休': {'all_day': True, 'summary': '有給休暇'}
        }
        
        if shift_type not in shift_times:
            logger.error(f"未知の勤務タイプ: {shift_type}")
            return None
        
        shift_info = shift_times[shift_type]
        event = {
            'summary': f'清水理沙子: {shift_info["summary"]}',
            'description': f'6月勤務予定 - {shift_type}'
        }
        
        if shift_info.get('all_day'):
            # 終日イベント
            event['start'] = {'date': date.strftime('%Y-%m-%d')}
            event['end'] = {'date': date.strftime('%Y-%m-%d')}
        else:
            # 時間指定イベント
            start_time = datetime.strptime(f"{date.strftime('%Y-%m-%d')} {shift_info['start']}", '%Y-%m-%d %H:%M')
            if shift_info.get('next_day'):
                # 夜勤の場合、終了時刻は翌日
                end_time = datetime.strptime(f"{(date + timedelta(days=1)).strftime('%Y-%m-%d')} {shift_info['end']}", '%Y-%m-%d %H:%M')
            else:
                end_time = datetime.strptime(f"{date.strftime('%Y-%m-%d')} {shift_info['end']}", '%Y-%m-%d %H:%M')
            
            event['start'] = {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Tokyo'}
            event['end'] = {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Tokyo'}
        
        try:
            event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            logger.info(f'イベント作成: {event.get("htmlLink")}')
            return event
        except HttpError as error:
            logger.error(f'イベント作成エラー: {error}')
            return None
    
    def add_june_schedule(self):
        """6月の勤務予定を一括追加"""
        # 6月の勤務データ
        schedule = ['明け', '有休', '有休', '日勤', '休み', '夜勤', '明け', '休み', 
                   '遅番', '夜勤', '明け', '休み', '日勤', '遅番', '休み', '夜勤', 
                   '明け', '休み', '休み', '夜勤', '明け', '休み', '日勤', 'B勤務', 
                   '夜勤', '明け', '休み', 'B勤務', '日勤', '休み']
        
        # 2025年6月1日から開始
        start_date = datetime(2025, 6, 1)
        
        success_count = 0
        for i, shift in enumerate(schedule):
            current_date = start_date + timedelta(days=i)
            result = self.add_work_schedule(current_date, shift)
            if result:
                success_count += 1
                logger.info(f"{current_date.strftime('%Y-%m-%d')}: {shift} - 追加成功")
            else:
                logger.error(f"{current_date.strftime('%Y-%m-%d')}: {shift} - 追加失敗")
        
        logger.info(f"完了: {success_count}/{len(schedule)} イベントを追加しました")
        return success_count

if __name__ == "__main__":
    logger.info("Google Calendar Manager - 6月勤務予定追加開始")
    
    # Google Calendar APIの初期化
    manager = GoogleCalendarManager()
    
    if manager.service:
        # 6月の勤務予定を追加
        manager.add_june_schedule()
    else:
        logger.error("Google Calendar APIの初期化に失敗しました")