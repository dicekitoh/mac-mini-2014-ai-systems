#\!/usr/bin/env python3
import os
import fcntl
import time
import logging
from pathlib import Path

class TelegramAPIManager:
    def __init__(self, lock_dir='/tmp/telegram_locks'):
        self.lock_dir = Path(lock_dir)
        self.lock_dir.mkdir(exist_ok=True)
        self.lock_file = None
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        logger = logging.getLogger('TelegramAPIManager')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def acquire_lock(self, bot_name, timeout=30):
        lock_path = self.lock_dir / f'{bot_name}.lock'
        
        try:
            self.lock_file = open(lock_path, 'w')
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX  < /dev/null |  fcntl.LOCK_NB)
                    self.lock_file.write(f'{bot_name}:{os.getpid()}:{time.time()}\n')
                    self.lock_file.flush()
                    self.logger.info(f'Lock acquired for {bot_name}')
                    return True
                except IOError:
                    time.sleep(1)
            
            self.logger.error(f'Failed to acquire lock for {bot_name}')
            return False
            
        except Exception as e:
            self.logger.error(f'Error acquiring lock: {e}')
            return False
    
    def release_lock(self, bot_name):
        if self.lock_file:
            try:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                self.lock_file.close()
                self.logger.info(f'Lock released for {bot_name}')
            except Exception as e:
                self.logger.error(f'Error releasing lock: {e}')
    
    def list_active_bots(self):
        active_bots = []
        for lock_file in self.lock_dir.glob('*.lock'):
            try:
                with open(lock_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        parts = content.split(':')
                        if len(parts) >= 3:
                            bot_name, pid, timestamp = parts[0], parts[1], parts[2]
                            try:
                                os.kill(int(pid), 0)
                                active_bots.append({
                                    'name': bot_name,
                                    'pid': pid,
                                    'started': float(timestamp)
                                })
                            except OSError:
                                lock_file.unlink()
            except Exception as e:
                self.logger.warning(f'Error reading lock file: {e}')
        
        return active_bots

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print('Usage: python3 telegram_api_manager.py <command>')
        sys.exit(1)
    
    manager = TelegramAPIManager()
    command = sys.argv[1]
    
    if command == 'list':
        active_bots = manager.list_active_bots()
        if active_bots:
            print('Active Telegram Bots:')
            for bot in active_bots:
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bot['started']))
                print(f'  - {bot["name"]} (PID: {bot["pid"]}, Started: {start_time})')
        else:
            print('No active Telegram Bots')
    elif command == 'cleanup':
        manager.list_active_bots()
        print('Lock files cleaned up')
