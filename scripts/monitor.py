#!/usr/bin/env python3
"""
OpenClaw 心跳监控脚本 (修复版)
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

# 强制输出刷新
sys.stdout.reconfigure(line_buffering=True)

CHECK_INTERVAL = 60  # 检查间隔（秒）
MAX_FAILURES = 3  # 连续失败次数阈值

def check_gateway_health():
    """检查 Gateway 健康状态 - 使用 HTTP 请求"""
    try:
        req = urllib.request.Request("http://127.0.0.1:18789/health")
        with urllib.request.urlopen(req, timeout=5) as response:
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
    
    print(f"🔔 OpenClaw 心跳监控已启动 (检查间隔: {CHECK_INTERVAL}秒)", flush=True)
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print("-" * 50, flush=True)
    
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 使用 HTTP 健康检查
        if check_gateway_health():
            if failure_count > 0:
                print(f"[{timestamp}] ✅ Gateway 状态恢复正常", flush=True)
                failure_count = 0
            else:
                print(f"[{timestamp}] ✅ Gateway 状态正常", flush=True)
        else:
            failure_count += 1
            print(f"[{timestamp}] ❌ Gateway 异常 (连续失败: {failure_count}/{MAX_FAILURES})", flush=True)
            
            if failure_count >= MAX_FAILURES:
                print(f"🔧 触发自动修复...", flush=True)
                if fix_and_restart():
                    failure_count = 0
                    print(f"[{timestamp}] ✅ 修复成功", flush=True)
                else:
                    print(f"⚠️ 自动修复失败，请检查报告", flush=True)
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # 检查是否已有监控进程运行 (跳过检查，避免冲突)
    monitor()
