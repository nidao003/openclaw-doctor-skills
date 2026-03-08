# openclaw-doctor

自动修复 OpenClaw 配置错误的技能。

## 功能

### 1. 配置文件备份
- 每天自动备份 `~/.openclaw/openclaw.json` 到 `~/.openclaw/backups/`
- 备份文件名格式：`openclaw_config_YYYYMMDD_HHMMSS.json`
- 自动清理 10 天前的旧备份

### 2. 自动修复流程
```
1. 检查 Gateway 状态
   ↓
2. 执行 openclaw doctor --fix
   ↓ 失败
3. 恢复最新 JSON 备份
   ↓
4. 再次执行 openclaw doctor --fix
   ↓
5. 执行 openclaw gateway restart
   ↓
6. 等待 5 秒
   ↓
7. 检查日志 (openclaw logs)
   ↓
8. 检查状态 (openclaw status)
   ↓ 异常
9. 生成 MD 报告到桌面
```

### 3. 心跳监控（可选）
- 每 60 秒检查一次 Gateway 状态
- 连续 3 次检测失败 → 触发自动修复

## 文件结构
```
openclaw-doctor/
├── SKILL.md      # 技能说明
├── backup.py     # 配置文件备份
├── fix.py        # 自动修复脚本
├── monitor.py    # 心跳监控脚本
└── report.py     # 失败报告生成
```

## 使用方法

### 手动备份
```bash
python3 ~/.openclaw/skills/openclaw-doctor/backup.py
```

### 手动修复
```bash
python3 ~/.openclaw/skills/openclaw-doctor/fix.py
```

### 启动心跳监控（后台）
```bash
nohup python3 ~/.openclaw/skills/openclaw-doctor/monitor.py > /tmp/openclaw-monitor.log 2>&1 &
```

### 设置定时任务
```bash
# 每天凌晨2点自动备份
crontab -e
0 2 * * * python3 ~/.openclaw/skills/openclaw-doctor/backup.py
```

## 业务流程图

```
┌─────────────────────────────────────────────────────────────┐
│                      修复流程                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    成功    ┌─────────────┐    成功           │
│  │ 检查状态  │ ────────→ │doctor --fix │ ───────────────→  │
│  └──────────┘            └─────────────┘                   │
│      │                        │                            │
│      │ 异常                   │ 失败                       │
│      ↓                        ↓                            │
│  ┌──────────┐            ┌─────────────┐                   │
│  │ 开始修复 │            │ 恢复备份    │                   │
│  └──────────┘            └─────────────┘                   │
│                                │                            │
│                                ↓                            │
│                         ┌─────────────┐   成功              │
│                         │doctor --fix │ ───────────────→    │
│                         └─────────────┘                     │
│                                │                            │
│                                ↓                            │
│                         ┌─────────────┐                     │
│                         │  restart   │                     │
│                         └─────────────┘                     │
│                                │                            │
│                                ↓                            │
│                         ┌─────────────┐                     │
│                         │ 检查日志    │                     │
│                         └─────────────┘                     │
│                                │                            │
│                     ┌───────────┴───────────┐               │
│                     ↓                       ↓               │
│               正常/超时                   有错误            │
│                     ↓                       ↓               │
│               ┌─────────┐           ┌──────────┐           │
│               │ ✅ 成功  │           │ 生成报告 │           │
│               └─────────┘           └──────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 错误报告
当修复失败时，会在桌面生成报告文件：
- 文件名：`openclaw_fix_report_YYYYMMDD_HHMMSS.md`
- 内容包含：doctor 输出、restart 输出、日志、状态检查结果
