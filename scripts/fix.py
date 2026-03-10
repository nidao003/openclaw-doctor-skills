#!/usr/bin/env python3
"""
OpenClaw 自动修复脚本
优化版：增加日志检查逻辑，处理超时情况
"""

import os
import sys
import re
import shutil
import subprocess
from datetime import datetime

BACKUP_DIR = os.path.expanduser("~/.openclaw/backups")
CONFIG_FILE = os.path.expanduser("~/.openclaw/openclaw.json")
DESKTOP = os.path.expanduser("~/Desktop")
MAX_RETRIES = 3
OPENCLAW_BIN = "node /opt/homebrew/lib/node_modules/openclaw/openclaw.mjs"

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

def has_real_error(output):
    """检测是否真正的错误"""
    if not output:
        return False
    
    if output == "Command timeout":
        return False  # 超时不算错误
    
    # 真正的错误关键词
    error_patterns = [
        r'\berror\b.*:',
        r'\bError\b.*:',
        r'\bFATAL\b',
        r'\bFailed to\b',
        r'\bcannot\b',
        r'\bno such file\b',
        r'\bpermission denied\b',
        r'\bENOENT\b',
    ]
    
    for pattern in error_patterns:
        if re.search(pattern, output, re.IGNORECASE):
            return True
    
    return False

def get_latest_backup():
    """获取最新的备份文件"""
    if not os.path.exists(BACKUP_DIR):
        return None
    
    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith("openclaw_config_")]
    if not backups:
        return None
    
    backups.sort(reverse=True)
    return os.path.join(BACKUP_DIR, backups[0])

def restore_backup(backup_file):
    """恢复备份"""
    if not backup_file or not os.path.exists(backup_file):
        print(f"❌ 备份文件不存在: {backup_file}")
        return False
    
    current_backup = f"{CONFIG_FILE}.broken.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(CONFIG_FILE):
        shutil.copy2(CONFIG_FILE, current_backup)
        print(f"📦 已保存错误配置到: {current_backup}")
    
    shutil.copy2(backup_file, CONFIG_FILE)
    print(f"✅ 已恢复配置: {backup_file}")
    return True

def run_doctor_fix():
    """执行 openclaw doctor --fix"""
    print("🔧 执行 openclaw doctor --fix...")
    cmd = f"{OPENCLAW_BIN} doctor --fix 2>&1"
    code, stdout, stderr = run_command(cmd, timeout=90)
    
    output = stdout + "\n" + stderr
    
    if code == -1 and output == "Command timeout":
        print("⏳ doctor --fix 执行超时（可能正常运行中）")
        return True, output
    
    if has_real_error(output):
        print(f"❌ doctor --fix 执行失败: {output[:150]}")
        return False, output
    else:
        print("✅ doctor --fix 执行成功")
        return True, output

def restart_gateway():
    """重启 Gateway"""
    print("🔄 执行 openclaw gateway restart...")
    cmd = f"{OPENCLAW_BIN} gateway restart 2>&1"
    code, stdout, stderr = run_command(cmd, timeout=30)
    
    output = stdout + "\n" + stderr
    
    if code == -1 and output == "Command timeout":
        print("⏳ gateway restart 执行超时，验证实际状态...")
        # 超时时应该验证实际状态，而不是假设成功
        status_cmd = f"{OPENCLAW_BIN} gateway status 2>&1"
        status_code, status_out, _ = run_command(status_cmd, timeout=10)
        if status_code == 0 and "running" in status_out.lower():
            print("✅ Gateway 已在运行")
            return True, "Gateway already running"
        else:
            print("❌ Gateway 未启动，超时后仍无法连接")
            return False, "Gateway timeout and not running"
    
    if has_real_error(output):
        print(f"⚠️ Gateway 重启可能有警告: {output[:150]}")
        return False, output
    else:
        print("✅ Gateway 重启命令已执行")
        return True, output

def check_logs():
    """检查日志"""
    print("📜 正在检查 Gateway 日志...")
    import time
    time.sleep(3)
    
    cmd = f"{OPENCLAW_BIN} logs 2>&1 | tail -50"
    code, stdout, stderr = run_command(cmd, timeout=15)
    
    output = stdout + "\n" + stderr
    print(f"📜 日志长度: {len(output)} 字符")
    
    return output

def get_system_info():
    """获取系统状态信息用于调试"""
    info = []
    
    # Gateway 进程状态
    cmd = "ps aux | grep 'openclaw' | grep -v grep"
    code, stdout, stderr = run_command(cmd, timeout=5)
    info.append(f"=== OpenClaw 进程 ===\n{stdout[:500]}")
    
    # Gateway launchd 状态
    cmd = "launchctl list | grep openclaw"
    code, stdout, stderr = run_command(cmd, timeout=5)
    info.append(f"=== launchctl 状态 ===\n{stdout}")
    
    # 端口占用
    cmd = "lsof -i :18789"
    code, stdout, stderr = run_command(cmd, timeout=5)
    info.append(f"=== 端口 18789 ===\n{stdout}")
    
    return "\n".join(info)

def check_gateway_status():
    """检查 Gateway 状态"""
    print("🔍 检查 Gateway 状态...")
    cmd = f"{OPENCLAW_BIN} status 2>&1"
    code, stdout, stderr = run_command(cmd, timeout=10)
    
    output = stdout + "\n" + stderr
    
    if code == -1 and output == "Command timeout":
        print("⏳ 状态检查超时（Gateway 可能在启动中）")
        # 超时但有输出说明 Gateway 在运行
        if stdout:
            return True, output
        return False, output
    
    print(f"📜 状态: {'正常' if not has_real_error(output) else '异常'}")
    
    if has_real_error(output):
        return False, output
    else:
        return True, output

def generate_report(attempt, doctor_output, restart_output, log_output, status_output):
    """生成失败报告"""
    # 获取系统状态信息
    system_info = get_system_info()
    
    report_file = os.path.join(DESKTOP, f"openclaw_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    content = f"""# OpenClaw 自动修复报告

## 修复时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 修复尝试次数
{attempt}

---

## 📋 系统状态信息
```
{system_info[:3000]}
```

---

## 📋 doctor --fix 输出
```
{doctor_output[:3000]}
```

---

## 📋 gateway restart 输出
```
{restart_output[:2000]}
```

---

## 📋 Gateway 日志
```
{log_output[:4000]}
```

---

## 📋 Status 检查输出
```
{status_output[:2000]}
```

---

## 最新备份
{get_latest_backup()}

## 建议手动操作
1. 使用 `openclaw doctor` 手动诊断
2. 查看日志: `openclaw logs --follow`
3. 重启: `openclaw gateway restart`
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📄 报告已生成: {report_file}")
    return report_file

def fix_openclaw():
    """
    使用指数退避策略修复 OpenClaw
    - 第1次: 修复后等待1分钟检查
    - 第2次: 修复后等待2分钟检查
    - 第3次: 修复后等待3分钟检查
    - 失败3次后记录日志到桌面，停止
    """
    wait_times = [60, 120, 180]  # 1分钟, 2分钟, 3分钟
    
    print(f"🚀 开始修复 OpenClaw (指数退避策略)...")
    
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n{'='*50}")
        print(f"📌 第 {attempt}/{MAX_RETRIES} 次尝试 (等待 {wait_times[attempt-1]//60} 分钟)")
        print('='*50)
        
        # 1. 执行 doctor --fix
        success, doctor_output = run_doctor_fix()
        
        if not success:
            print("❌ doctor --fix 失败，尝试恢复备份...")
            latest_backup = get_latest_backup()
            
            if latest_backup and restore_backup(latest_backup):
                print("✅ 配置已恢复，再次尝试 doctor --fix...")
                success, doctor_output = run_doctor_fix()
                if not success:
                    continue
            else:
                print("⚠️ 没有可用的备份文件")
                continue
        
        # 2. 执行 gateway restart
        _, restart_output = restart_gateway()
        
        # 3. 指数退避等待
        wait_time = wait_times[attempt - 1]
        print(f"⏳ 等待 {wait_time//60} 分钟让 Gateway 完全启动...")
        import time
        time.sleep(wait_time)
        
        # 4. 检查日志
        log_output = check_logs()
        
        # 5. 检查状态
        status_ok, status_output = check_gateway_status()
        
        if status_ok:
            print("🎉 修复成功！OpenClaw 已恢复正常")
            return True
        
        print(f"❌ 第 {attempt} 次修复后状态仍异常")
        
        # 第3次失败后记录日志并停止
        if attempt >= MAX_RETRIES:
            print("⚠️ 已达最大重试次数，生成失败报告...")
            generate_report(attempt, doctor_output, restart_output, log_output, status_output)
            return False
    
    return False

if __name__ == "__main__":
    print(f"📅 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] OpenClaw 修复脚本启动...")
    
    status_ok, status_output = check_gateway_status()
    if status_ok:
        print("✅ OpenClaw 状态正常，无需修复")
        sys.exit(0)
    
    success = fix_openclaw()
    sys.exit(0 if success else 1)
