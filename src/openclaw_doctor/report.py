#!/usr/bin/env python3
"""
OpenClaw 故障报告生成脚本
"""

import os
import subprocess
from datetime import datetime

DESKTOP = os.path.expanduser("~/Desktop")
OPENCLAW_BIN = "openclaw"


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


def get_system_info():
    """获取系统状态信息"""
    info = []

    cmd = "ps aux | grep 'openclaw' | grep -v grep"
    code, stdout, stderr = run_command(cmd, timeout=5)
    info.append(f"=== OpenClaw 进程 ===\n{stdout[:2000]}")

    cmd = "launchctl list | grep openclaw"
    code, stdout, stderr = run_command(cmd, timeout=5)
    info.append(f"=== launchctl 状态 ===\n{stdout}")

    cmd = "lsof -i :18789"
    code, stdout, stderr = run_command(cmd, timeout=5)
    info.append(f"=== 端口 18789 ===\n{stdout}")

    return "\n".join(info)


def get_gateway_status():
    """获取 Gateway 状态"""
    cmd = f"{OPENCLAW_BIN} gateway probe 2>&1"
    code, stdout, stderr = run_command(cmd, timeout=15)
    return stdout + "\n" + stderr


def get_openclaw_status():
    """获取 OpenClaw 状态"""
    cmd = f"{OPENCLAW_BIN} status 2>&1"
    code, stdout, stderr = run_command(cmd, timeout=15)
    return stdout + "\n" + stderr


def get_recent_logs(lines=100):
    """获取最近的日志"""
    cmd = f"tail -n {lines} ~/.openclaw/logs/gateway.log 2>/dev/null || echo '日志文件不存在'"
    code, stdout, stderr = run_command(cmd, timeout=10)
    return stdout


def run_report(output=None):
    """生成故障报告"""
    print("📄 正在生成故障报告...")

    # 确定输出路径
    if output is None:
        output = os.path.join(DESKTOP, f"openclaw_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    # 收集信息
    system_info = get_system_info()
    gateway_status = get_gateway_status()
    openclaw_status = get_openclaw_status()
    recent_logs = get_recent_logs()

    # 生成报告
    content = f"""# OpenClaw 故障诊断报告

## 生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📋 系统状态信息
```
{system_info}
```

---

## 📋 Gateway 状态
```
{gateway_status}
```

---

## 📋 OpenClaw 状态
```
{openclaw_status}
```

---

## 📋 最近日志 (100 行)
```
{recent_logs[-4000:]}
```

---

## 建议操作
1. 查看完整日志: `openclaw logs --follow`
2. 运行诊断: `openclaw doctor`
3. 重启 Gateway: `openclaw daemon restart`
"""

    try:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 报告已生成: {output}")
        return True
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        return False


if __name__ == "__main__":
    run_report()
