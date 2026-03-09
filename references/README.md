# OpenClaw Doctor 详细文档

## 概述

OpenClaw Doctor 是一个用于监控和自动修复 OpenClaw 配置问题的工具。它能够：
- 自动备份配置文件
- 检测 Gateway 状态异常
- 自动执行修复流程
- 生成问题报告

## 功能特性

### 🔧 自动修复

自动修复流程：
1. 检查 Gateway 状态
2. 执行 `openclaw doctor --fix` 自动修复
3. 失败时自动恢复配置文件
4. 重启 Gateway 服务
5. 验证修复结果

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
git clone https://github.com/nidao003/openclaw-doctor-skills.git ~/.openclaw/skills/openclaw-doctor
```

或使用 SSH：

```bash
git clone git@github.com:nidao003/openclaw-doctor-skills.git ~/.openclaw/skills/openclaw-doctor
```

### 方式二：使用 OpenClaw Skill 管理器

```bash
openclaw skill install openclaw-doctor
```

## 使用方法

### 手动备份配置

```bash
python3 ~/.openclaw/skills/openclaw-doctor/scripts/backup.py
```

### 手动执行修复

```bash
python3 ~/.openclaw/skills/openclaw-doctor/scripts/fix.py
```

### 启动心跳监控（后台运行）

```bash
nohup python3 ~/.openclaw/skills/openclaw-doctor/scripts/monitor.py > /tmp/openclaw-monitor.log 2>&1 &
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
0 2 * * * python3 ~/.openclaw/skills/openclaw-doctor/scripts/backup.py >> /tmp/openclaw-backup.log 2>&1
```

### 自动修复检查（每小时）

```
0 * * * * python3 ~/.openclaw/skills/openclaw-doctor/scripts/fix.py >> /tmp/openclaw-fix.log 2>&1
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 技能元数据（安装、依赖、触发条件） |
| `scripts/backup.py` | 配置文件备份脚本 |
| `scripts/fix.py` | 自动修复脚本 |
| `scripts/monitor.py` | 心跳监控脚本 |
| `scripts/report.py` | 失败报告生成脚本 |
| `references/README.md` | 详细使用说明（本文件） |

## 输出日志

- 备份日志：`/tmp/openclaw-backup.log`
- 修复日志：`/tmp/openclaw-fix.log`
- 监控日志：`/tmp/openclaw-monitor.log`
- 失败报告：`~/Desktop/openclaw_fix_report_*.md`

## 故障排除

### 修复失败怎么办？

1. 检查日志：`tail -f /tmp/openclaw-fix.log`
2. 查看失败报告：`ls ~/Desktop/openclaw_fix_report_*.md`
3. 手动检查状态：`openclaw status`
4. 手动重启：`openclaw gateway restart`

### 监控进程消失了？

```bash
# 重新启动监控
nohup python3 ~/.openclaw/skills/openclaw-doctor/scripts/monitor.py > /tmp/openclaw-monitor.log 2>&1 &
```

## 相关链接

- GitHub 仓库：https://github.com/nidao003/openclaw-doctor-skills
- OpenClaw 官网：https://docs.openclaw.ai

## 许可证

MIT License
