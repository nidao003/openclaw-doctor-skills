#!/usr/bin/env python3
"""
OpenClaw 配置文件备份脚本
每天执行一次，保留 10 天备份
"""

import os
import shutil
import json
from datetime import datetime, timedelta

BACKUP_DIR = os.path.expanduser("~/.openclaw/backups")
CONFIG_FILE = os.path.expanduser("~/.openclaw/openclaw.json")
RETENTION_DAYS = 10

def backup_config():
    """备份配置文件"""
    # 确保备份目录存在
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"openclaw_config_{timestamp}.json")
    
    # 复制配置文件
    if os.path.exists(CONFIG_FILE):
        shutil.copy2(CONFIG_FILE, backup_file)
        print(f"✅ 备份成功: {backup_file}")
    else:
        print(f"❌ 配置文件不存在: {CONFIG_FILE}")
        return False
    
    # 清理旧备份
    cleanup_old_backups()
    
    return True

def cleanup_old_backups():
    """清理超过 10 天的备份"""
    if not os.path.exists(BACKUP_DIR):
        return
    
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    
    for filename in os.listdir(BACKUP_DIR):
        if not filename.startswith("openclaw_config_"):
            continue
        
        filepath = os.path.join(BACKUP_DIR, filename)
        if os.path.isfile(filepath):
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if mtime < cutoff_date:
                os.remove(filepath)
                print(f"🗑️ 已清理旧备份: {filename}")

def get_latest_backup():
    """获取最新的备份文件"""
    if not os.path.exists(BACKUP_DIR):
        return None
    
    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith("openclaw_config_")]
    if not backups:
        return None
    
    backups.sort(reverse=True)
    return os.path.join(BACKUP_DIR, backups[0])

if __name__ == "__main__":
    print(f"📅 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始备份 OpenClaw 配置...")
    backup_config()
    print(f"📅 备份完成，最新备份: {get_latest_backup()}")
