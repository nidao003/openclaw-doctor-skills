#!/usr/bin/env python3
"""
OpenClaw 心跳监控脚本 (优化版)
定时检查 Gateway 状态，异常时自动修复
"""

import os
import sys
import time
import subprocess
import signal
from datetime import datetime
import urllib.request
import json

CHECK_INTERVAL = 60  # 检查间隔（秒）
MAX_FAILURES = 3  # 连续失败次数阈值

def check_gateway_health():
    """检查 Gateway 健康状态 - 使用 HTTP 请求"""
    try:
        req = urllib.request.Request("http://127.0.0.1:18789/health")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("status") == "live"
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

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

def fix_and_restart():
    """执行修复并重启"""
    fix_script = os.path.expanduser("~/dsl/openclaw-doctor/scripts/fix.py")
    cmd = f"python3 {fix_script}"
    code, stdout, stderr = run_command(cmd, timeout=180)
    return code == 0

def monitor():
    """心跳监控主循环"""
    failure_count = 0
    
    print(f"🔔 OpenClaw 心跳监控已启动 (检查间隔: {CHECK_INTERVAL}秒)")
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 使用 HTTP 健康检查
            if check_gateway_health():
                if failure_count > 0:
                    print(f"[{timestamp}] ✅ Gateway 状态恢复正常")
                    failure_count = 0
                # 每5次正常才打印，避免刷屏
                elif failure_count == 0:
                    print(f"[{timestamp}] ✅ Gateway 状态正常")
            else:
                failure_count += 1
                print(f"[{timestamp}] ❌ Gateway 异常 (连续失败: {failure_count}/{MAX_FAILURES})")
                
                if failure_count >= MAX_FAILURES:
                    print(f"🔧 触发自动修复...")
                    if fix_and_restart():
                        failure_count = 0
                        print(f"[{timestamp}] ✅ 修复成功")
                    else:
                        print(f"⚠️ 自动修复失败，请检查报告")
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n👋 心跳监控已停止")
        sys.exit(0)

if __name__ == "__main__":
    # 检查是否已有监控进程运行
    try:
        import psutil
        
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['pid'] != current_pid and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'openclaw-doctor/monitor.py' in cmdline:
                        print("⚠️ 监控进程已在运行中")
                        sys.exit(0)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        pass
    
    monitor()
