# OpenClaw Doctor

自动修复 OpenClaw 配置错误的工具，确保 Gateway 服务稳定运行。

## 概述

OpenClaw Doctor 是一个用于监控和自动修复 OpenClaw 配置问题的工具。它能够：
- 自动备份配置文件
- 检测 Gateway 状态异常
- 自动执行修复流程
- 生成问题报告

## 功能特性

### 🔧 自动修复
- 检查 Gateway 状态
- 执行 `openclaw doctor --fix` 自动修复
- 失败时自动恢复配置文件
- 重启 Gateway 服务

### 💾 配置文件备份
- 每天自动备份 `~/.openclaw/openclaw.json`
- 保留最近 10 天的备份
- 支持手动备份

### 📊 心跳监控（可选）
- 每 60 秒检测 Gateway 状态
- 连续 3 次失败自动触发修复

### 📝 报告生成
- 修复失败时自动生成 Markdown 报告
- 包含日志、状态、检查结果

## 安装

### 方式一：克隆仓库

```bash
git clone git@github.com:nidao003/openclaw-doctor.git ~/.openclaw/skills/openclaw-doctor
```

### 方式二：手动复制

```bash
# 复制文件
cp -r openclaw-doctor/ ~/.openclaw/skills/

# 验证安装
ls ~/.openclaw/skills/openclaw-doctor/
```

## 使用方法

### 手动备份配置

```bash
python3 ~/.openclaw/skills/openclaw-doctor/backup.py
```

### 手动执行修复

```bash
python3 ~/.openclaw/skills/openclaw-doctor/fix.py
```

### 启动心跳监控（后台运行）

```bash
nohup python3 ~/.openclaw/skills/openclaw-doctor/monitor.py > /tmp/openclaw-monitor.log 2>&1 &
echo $!  # 记录进程ID
```

### 停止心跳监控

```bash
# 查找进程
ps aux | grep monitor.py

# 终止进程
kill <PID>
```

### 查看监控日志

```bash
tail -f /tmp/openclaw-monitor.log
```

## 定时任务

### 自动备份（每天凌晨2点）

```bash
crontab -e
```

添加以下行：

```
0 2 * * * python3 ~/.openclaw/skills/openclaw-doctor/backup.py >> /tmp/openclaw-backup.log 2>&1
```

### 自动修复检查（每小时）

```
0 * * * * python3 ~/.openclaw/skills/openclaw-doctor/fix.py >> /tmp/openclaw-fix.log 2>&1
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `backup.py` | 配置文件备份脚本 |
| `fix.py` | 自动修复脚本 |
| `monitor.py` | 心跳监控脚本 |
| `report.py` | 失败报告生成脚本 |
| `SKILL.md` | 技能详细说明 |

## 输出日志

- 备份日志：`/tmp/openclaw-backup.log`
- 修复日志：`/tmp/openclaw-fix.log`
- 监控日志：`/tmp/openclaw-monitor.log`
- 失败报告：`~/Desktop/openclaw_fix_report_*.md`

## 依赖

- Python 3.7+
- OpenClaw 已安装并配置
- `openclaw` 命令行工具

## 许可证

MIT License
