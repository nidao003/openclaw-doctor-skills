#!/usr/bin/env python3
"""
OpenClaw 心跳监控脚本 (优化版)
定时检查 Gateway 状态，异常时自动修复
支持日志轮转，保留3天日志
"""

import os
import sys
import time
import gzip
import shutil
from datetime import datetime, timedelta
import urllib.request
import json
import subprocess

# 强制输出刷新
sys.stdout.reconfigure(line_buffering=True)

CHECK_INTERVAL = 300  # 检查间隔（5分钟）
MAX_FAILURES = 3    # 连续失败次数阈值
LOG_DIR = os.path.expanduser("~/.openclaw/logs")
LOG_FILE = os.path.join(LOG_DIR, "openclaw-monitor.log")
MAX_DAYS = 3        # 日志保留天数

def setup_logging():
    """设置日志目录和文件"""
    os.makedirs(LOG_DIR, exist_ok=True)
    return LOG_FILE

def rotate_logs():
    """日志轮转，保留指定天数的日志"""
    if not os.path.exists(LOG_FILE):
        return
    
    # 检查主日志文件大小，超过10MB则轮转
    if os.path.getsize(LOG_FILE) > 10 * 1024 * 1024:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archived = f"{LOG_FILE}.{timestamp}.gz"
        
        with open(LOG_FILE, 'rb') as f_in:
            with gzip.open(archived, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 清空主日志
        open(LOG_FILE, 'w').close()
        log(f"📦 日志已归档: {archived}")
    
    # 删除过期日志
    cutoff = datetime.now() - timedelta(days=MAX_DAYS)
    log_dir = os.path.dirname(LOG_FILE)
    
    for f in os.listdir(log_dir):
        if f.startswith("openclaw-monitor.log.") and f.endswith(".gz"):
            fpath = os.path.join(log_dir, f)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                if mtime < cutoff:
                    os.remove(fpath)
                    log(f"🗑️ 删除过期日志: {f}")
            except:
                pass

def log(msg):
    """写入日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    
    # 写入文件
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")
    
    # 打印到控制台
    print(line, flush=True)

def get_gateway_error_logs(lines=20):
    """获取 Gateway 错误日志"""
    gateway_log = os.path.expanduser("~/.openclaw/logs/gateway.log")
    if not os.path.exists(gateway_log):
        return "Gateway 日志文件不存在"
    
    try:
        # 读取最后几行错误日志
        result = subprocess.run(
            f"tail -n {lines} {gateway_log} | grep -i 'error\\|fail\\|crash' | tail -10",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.stdout else "无错误日志"
    except Exception as e:
        return f"读取失败: {e}"

def check_gateway_health():
    """检查 Gateway 健康状态"""
    # 先检查 Gateway 进程是否存在
    proc_check_cmd = "ps aux | grep 'openclaw-gateway' | grep -v grep"
    proc_result = subprocess.run(proc_check_cmd, shell=True, capture_output=True, text=True)
    
    # 记录进程状态
    if proc_result.stdout:
        # 提取 PID 和内存信息
        lines = proc_result.stdout.strip().split('\n')
        for line in lines:
            log(f"   进程: {line[:100]}")  # 记录进程详情
    else:
        log("   ⚠️ 未找到 openclaw-gateway 进程")
    
    try:
        req = urllib.request.Request("http://127.0.0.1:18789/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            status = data.get("status")
            log(f"   HTTP 状态: {status}")
            return status == "live"
    except Exception as e:
        log(f"   HTTP 检查失败: {e}")
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
    log("📋 记录当前 Gateway 错误日志:")
    error_logs = get_gateway_error_logs(30)
    for line in error_logs.strip().split('\n'):
        if line:
            log(f"   {line}")
    
    fix_script = os.path.expanduser("~/.openclaw/workspace/skills/openclaw-doctor/scripts/fix.py")
    cmd = f"python3 {fix_script}"
    code, stdout, stderr = run_command(cmd, timeout=180)
    return code == 0

def monitor():
    """心跳监控主循环"""
    setup_logging()
    failure_count = 0
    cooldown_after_fix = 0  # 修复后的冷却期（跳过检查次数）
    COOLDOWN_CHECKS = 1  # 修复后跳过 1 次检查（5分钟）
    
    log("🔔 OpenClaw 心跳监控已启动")
    log(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"📁 日志文件: {LOG_FILE}")
    log(f"📆 日志保留: {MAX_DAYS}天")
    log("-" * 50)
    
    # 启动时清理一次过期日志
    rotate_logs()
    
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 修复冷却期：跳过检查，让 Gateway 有时间稳定
        if cooldown_after_fix > 0:
            cooldown_after_fix -= 1
            log(f"⏳ 修复冷却期 ({cooldown_after_fix}/{COOLDOWN_CHECKS})，跳过检查")
            time.sleep(CHECK_INTERVAL)
            continue
        
        # 使用 HTTP 健康检查
        if check_gateway_health():
            if failure_count > 0:
                log(f"✅ Gateway 状态恢复正常")
                failure_count = 0
            else:
                log(f"✅ Gateway 状态正常")
        else:
            failure_count += 1
            log(f"❌ Gateway 异常 (连续失败: {failure_count}/{MAX_FAILURES})")
            
            # 记录错误日志
            log("📋 Gateway 错误日志:")
            error_logs = get_gateway_error_logs(20)
            for line in error_logs.strip().split('\n'):
                if line:
                    log(f"   {line}")
            
            if failure_count >= MAX_FAILURES:
                log(f"🔧 触发自动修复...")
                if fix_and_restart():
                    failure_count = 0
                    cooldown_after_fix = COOLDOWN_CHECKS  # 设置修复冷却期
                    log(f"✅ 修复成功，进入冷却期")
                else:
                    log(f"⚠️ 自动修复失败，请检查报告")
        
        # 每小时清理一次过期日志
        if datetime.now().minute == 0:
            rotate_logs()
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
