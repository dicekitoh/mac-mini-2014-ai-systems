#\!/usr/bin/env python3
"""
Telegram Bot管理システム
Docker + API排他制御でBot競合を防止
"""
import subprocess
import sys
import time
import os
from telegram_api_manager import TelegramAPIManager

class BotManager:
    def __init__(self):
        self.api_manager = TelegramAPIManager()
        self.docker_compose_path = os.path.expanduser('~/docker_bots')
    
    def start_todo_bot(self):
        """Todo Botを安全に起動"""
        print('Starting Todo Bot with API lock protection...')
        
        # API排他制御
        if not self.api_manager.acquire_lock('todo_bot', timeout=10):
            print('Error: Todo Bot is already running or lock acquisition failed')
            return False
        
        try:
            # Docker Composeで起動
            result = subprocess.run([
                'docker', 'compose', 'up', '-d', 'todo_bot'
            ], cwd=self.docker_compose_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print('Todo Bot started successfully in Docker container')
                return True
            else:
                print(f'Failed to start Todo Bot: {result.stderr}')
                self.api_manager.release_lock('todo_bot')
                return False
                
        except Exception as e:
            print(f'Error starting Todo Bot: {e}')
            self.api_manager.release_lock('todo_bot')
            return False
    
    def stop_todo_bot(self):
        """Todo Botを停止"""
        print('Stopping Todo Bot...')
        
        try:
            # Docker Composeで停止
            subprocess.run([
                'docker', 'compose', 'stop', 'todo_bot'
            ], cwd=self.docker_compose_path)
            
            # ロック解放
            self.api_manager.release_lock('todo_bot')
            print('Todo Bot stopped successfully')
            
        except Exception as e:
            print(f'Error stopping Todo Bot: {e}')
    
    def status(self):
        """Bot状況を表示"""
        print('=== Telegram Bot Status ===')
        
        # アクティブなBotをリスト
        active_bots = self.api_manager.list_active_bots()
        if active_bots:
            for bot in active_bots:
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bot['started']))
                print(f'🟢 {bot["name"]} (PID: {bot["pid"]}, Started: {start_time})')
        else:
            print('🔴 No active Telegram Bots')
        
        # Docker状況
        try:
            result = subprocess.run([
                'docker', 'compose', 'ps'
            ], cwd=self.docker_compose_path, capture_output=True, text=True)
            
            if result.stdout:
                print('\n=== Docker Container Status ===')
                print(result.stdout)
        except:
            pass
    
    def restart_todo_bot(self):
        """Todo Botを再起動"""
        self.stop_todo_bot()
        time.sleep(2)
        return self.start_todo_bot()
    
    def cleanup(self):
        """システムクリーンアップ"""
        print('Cleaning up Bot system...')
        
        # Docker停止
        try:
            subprocess.run(['docker', 'compose', 'down'], cwd=self.docker_compose_path)
        except:
            pass
        
        # ロッククリーンアップ
        self.api_manager.list_active_bots()  # 無効なロック削除
        print('Cleanup completed')

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 bot_manager.py <command>')
        print('Commands: start, stop, restart, status, cleanup')
        sys.exit(1)
    
    manager = BotManager()
    command = sys.argv[1]
    
    if command == 'start':
        manager.start_todo_bot()
    elif command == 'stop':
        manager.stop_todo_bot()
    elif command == 'restart':
        manager.restart_todo_bot()
    elif command == 'status':
        manager.status()
    elif command == 'cleanup':
        manager.cleanup()
    else:
        print(f'Unknown command: {command}')

if __name__ == '__main__':
    main()
