#!/usr/bin/env python3
"""
OpenClaw 心跳监控脚本
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


def run_monitor(interval=300, max_failures=3):
    """运行心跳监控"""
    sys.stdout.reconfigure(line_buffering=True)

    CHECK_INTERVAL = interval
    MAX_FAILURES = max_failures
    LOG_DIR = os.path.expanduser("~/.openclaw/logs")
    LOG_FILE = os.path.join(LOG_DIR, "openclaw-monitor.log")
    MAX_DAYS = 3

    def setup_logging():
        os.makedirs(LOG_DIR, exist_ok=True)
        return LOG_FILE

    def rotate_logs():
        if not os.path.exists(LOG_FILE):
            return

        if os.path.getsize(LOG_FILE) > 10 * 1024 * 1024:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            archived = f"{LOG_FILE}.{timestamp}.gz"

            with open(LOG_FILE, 'rb') as f_in:
                with gzip.open(archived, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            open(LOG_FILE, 'w').close()
            log(f"📦 日志已归档: {archived}")

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
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"[{timestamp}] {msg}"

        with open(LOG_FILE, 'a') as f:
            f.write(line + "\n")

        print(line, flush=True)

    def get_gateway_error_logs(lines=20):
        gateway_log = os.path.expanduser("~/.openclaw/logs/gateway.log")
        if not os.path.exists(gateway_log):
            return "Gateway 日志文件不存在"

        try:
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
        proc_check_cmd = "ps aux | grep 'openclaw-gateway' | grep -v grep"
        proc_result = subprocess.run(proc_check_cmd, shell=True, capture_output=True, text=True)

        if proc_result.stdout:
            lines = proc_result.stdout.strip().split('\n')
            for line in lines:
                log(f"   进程: {line[:100]}")
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
        log("📋 记录当前 Gateway 错误日志:")
        error_logs = get_gateway_error_logs(30)
        for line in error_logs.strip().split('\n'):
            if line:
                log(f"   {line}")

        # 调用 fix 模块
        from openclaw_doctor.fix import run_fix as do_fix
        return do_fix()

    def monitor():
        setup_logging()
        failure_count = 0
        cooldown_after_fix = 0
        COOLDOWN_CHECKS = 1

        log("🔔 OpenClaw 心跳监控已启动")
        log(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log(f"📁 日志文件: {LOG_FILE}")
        log(f"📆 日志保留: {MAX_DAYS}天")
        log("-" * 50)

        rotate_logs()

        while True:
            if cooldown_after_fix > 0:
                cooldown_after_fix -= 1
                log(f"⏳ 修复冷却期 ({cooldown_after_fix}/{COOLDOWN_CHECKS})，跳过检查")
                time.sleep(CHECK_INTERVAL)
                continue

            if check_gateway_health():
                if failure_count > 0:
                    log(f"✅ Gateway 状态恢复正常")
                    failure_count = 0
                else:
                    log(f"✅ Gateway 状态正常")
            else:
                failure_count += 1
                log(f"❌ Gateway 异常 (连续失败: {failure_count}/{MAX_FAILURES})")

                log("📋 Gateway 错误日志:")
                error_logs = get_gateway_error_logs(20)
                for line in error_logs.strip().split('\n'):
                    if line:
                        log(f"   {line}")

                if failure_count >= MAX_FAILURES:
                    log(f"🔧 触发自动修复...")
                    if fix_and_restart():
                        failure_count = 0
                        cooldown_after_fix = COOLDOWN_CHECKS
                        log(f"✅ 修复成功，进入冷却期")
                    else:
                        log(f"⚠️ 自动修复失败，请检查报告")

            if datetime.now().minute == 0:
                rotate_logs()

            time.sleep(CHECK_INTERVAL)

    monitor()


if __name__ == "__main__":
    run_monitor()
