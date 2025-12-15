#\!/usr/bin/env python3
"""
安全なTodo Bot起動システム
プロセス重複を確実に防止
"""
import subprocess
import sys
import time
import signal
import os

def is_bot_running():
    """Todo Botが稼働中かチェック"""
    try:
        result = subprocess.run(['pgrep', '-f', 'stable_todo_bot.py'], 
                              capture_output=True, text=True)
        return bool(result.stdout.strip())
    except:
        return False

def stop_existing_bots():
    """既存のTodo Botを安全に停止"""
    print('Stopping existing Todo Bot processes...')
    
    # screenセッションを終了
    subprocess.run(['screen', '-S', 'todo_bot_fixed', '-X', 'quit'], 
                  capture_output=True)
    subprocess.run(['screen', '-S', 'todo_bot', '-X', 'quit'], 
                  capture_output=True)
    
    # プロセスを検索して終了
    try:
        result = subprocess.run(['pgrep', '-f', 'stable_todo_bot.py'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f'Terminated PID {pid}')
                except:
                    pass
    except:
        pass
    
    # 確実に停止するまで待機
    for _ in range(10):
        if not is_bot_running():
            break
        time.sleep(1)
    
    print('All Todo Bot processes stopped')

def start_single_bot():
    """単一のTodo Botを起動"""
    if is_bot_running():
        print('Todo Bot is already running. Stopping first...')
        stop_existing_bots()
    
    print('Starting single Todo Bot instance...')
    
    # 新しいscreenセッションで起動
    cmd = [
        'screen', '-S', 'todo_bot_safe', '-d', '-m', 'bash', '-c',
        'cd ~ && source todo_env/bin/activate && python3 stable_todo_bot.py > bot_safe.log 2>&1'
    ]
    
    subprocess.run(cmd)
    
    # 起動確認
    time.sleep(3)
    if is_bot_running():
        print('✅ Todo Bot started successfully (single instance)')
        return True
    else:
        print('❌ Failed to start Todo Bot')
        return False

def show_status():
    """Bot状況を表示"""
    print('=== Todo Bot Status ===')
    
    if is_bot_running():
        try:
            result = subprocess.run(['pgrep', '-f', 'stable_todo_bot.py'], 
                                  capture_output=True, text=True)
            pids = result.stdout.strip().split('\n')
            print(f'🟢 Todo Bot running (PIDs: {pids})')
            
            # screenセッション確認
            screen_result = subprocess.run(['screen', '-ls'], 
                                         capture_output=True, text=True)
            if 'todo_bot' in screen_result.stdout:
                print('📺 Screen session active')
            
        except:
            print('🟢 Todo Bot running')
    else:
        print('🔴 Todo Bot not running')

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 safe_todo_bot_starter.py <command>')
        print('Commands: start, stop, restart, status')
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'start':
        start_single_bot()
    elif command == 'stop':
        stop_existing_bots()
    elif command == 'restart':
        stop_existing_bots()
        time.sleep(2)
        start_single_bot()
    elif command == 'status':
        show_status()
    else:
        print(f'Unknown command: {command}')

if __name__ == '__main__':
    main()
