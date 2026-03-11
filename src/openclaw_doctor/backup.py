#!/usr/bin/env python3
"""
OpenClaw 配置文件备份脚本
"""

import os
import shutil
import subprocess
from datetime import datetime

BACKUP_DIR = os.path.expanduser("~/.openclaw/backups")
CONFIG_FILE = os.path.expanduser("~/.openclaw/openclaw.json")


def run_command(cmd, timeout=30):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            executable="/bin/zsh"
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "Command timeout", "Command timeout"
    except Exception as e:
        return -1, "", str(e)


def run_backup():
    """执行备份"""
    print("📦 开始备份 OpenClaw 配置文件...")

    # 创建备份目录
    os.makedirs(BACKUP_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        print(f"❌ 配置文件不存在: {CONFIG_FILE}")
        return False

    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"openclaw_config_{timestamp}.json")

    try:
        # 复制配置文件
        shutil.copy2(CONFIG_FILE, backup_file)
        print(f"✅ 配置文件已备份到: {backup_file}")

        # 清理旧备份（保留最近 10 个）
        backups = sorted([
            f for f in os.listdir(BACKUP_DIR)
            if f.startswith("openclaw_config_")
        ], reverse=True)

        if len(backups) > 10:
            for old_backup in backups[10:]:
                old_path = os.path.join(BACKUP_DIR, old_backup)
                os.remove(old_path)
                print(f"🗑️ 已删除旧备份: {old_backup}")

        return True

    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False


def run_backup_cli(output=None):
    """CLI 入口"""
    if output:
        # 自定义输出路径备份
        if os.path.exists(CONFIG_FILE):
            shutil.copy2(CONFIG_FILE, output)
            print(f"✅ 配置文件已备份到: {output}")
            return True
        else:
            print(f"❌ 配置文件不存在: {CONFIG_FILE}")
            return False
    else:
        return run_backup()


if __name__ == "__main__":
    run_backup()
