#!/usr/bin/env python3
"""
OpenClaw 修复失败报告生成脚本
"""

import os
from datetime import datetime

DESKTOP = os.path.expanduser("~/Desktop")
BACKUP_DIR = os.path.expanduser("~/.openclaw/backups")

def get_latest_backup():
    """获取最新的备份文件"""
    if not os.path.exists(BACKUP_DIR):
        return None
    
    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith("openclaw_config_")]
    if not backups:
        return None
    
    backups.sort(reverse=True)
    return os.path.join(BACKUP_DIR, backups[0])

def generate_report(error_details=None):
    """生成失败报告"""
    report_file = os.path.join(DESKTOP, f"openclaw_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    content = f"""# OpenClaw 自动修复报告

## 修复时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 状态
❌ 自动修复失败，需要手动处理

## 错误详情
{error_details or "自动修复已达到最大重试次数"}

## 最新备份
{get_latest_backup()}

## 手动修复步骤

### 1. 检查配置文件语法
```bash
cat ~/.openclaw/openclaw.json | python3 -m json.tool
```

### 2. 恢复备份配置
```bash
# 查看备份列表
ls -la ~/.openclaw/backups/

# 恢复最新备份
cp ~/.openclaw/backups/openclaw_config_*.json ~/.openclaw/openclaw.json
```

### 3. 运行诊断
```bash
openclaw doctor
```

### 4. 重启服务
```bash
openclaw gateway restart
```

## 相关信息
- 备份目录: {BACKUP_DIR}
- 配置文件: ~/.openclaw/openclaw.json
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📄 报告已生成: {report_file}")
    return report_file

if __name__ == "__main__":
    generate_report()
