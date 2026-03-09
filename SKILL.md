---
name: openclaw-doctor
description: '自动修复 OpenClaw 配置错误的技能。用于：(1) 自动备份和恢复配置文件，(2) 检测并修复 Gateway 状态异常，(3) 心跳监控 OpenClaw 服务状态，(4) 生成故障报告。当用户提到 OpenClaw 配置出错、Gateway 启动失败、服务异常、自动修复时使用此技能。'
metadata:
  {
    "openclaw":
      {
        "emoji": "🩺",
        "requires": { "bins": ["openclaw"], "anyBins": ["python3", "python"] },
        "install":
          [
            {
              "id": "clone",
              "kind": "git",
              "url": "https://github.com/nidao003/openclaw-doctor-skills.git",
              "label": "克隆 openclaw-doctor 技能",
            },
          ],
      },
  }
---

# OpenClaw Doctor 🩺

自动修复 OpenClaw 配置错误的技能。

## 快速使用

```bash
# 手动备份
python3 ~/.openclaw/skills/openclaw-doctor/scripts/backup.py

# 手动修复
python3 ~/.openclaw/skills/openclaw-doctor/scripts/fix.py

# 启动心跳监控（后台）
nohup python3 ~/.openclaw/skills/openclaw-doctor/scripts/monitor.py > /tmp/openclaw-monitor.log 2>&1 &
```

## 文件结构

```
openclaw-doctor/
├── SKILL.md           # 技能元数据（本文件）
├── README.md          # 详细使用说明 → 参见 references/
├── scripts/           # 可执行脚本
│   ├── backup.py      # 配置文件备份
│   ├── fix.py         # 自动修复
│   ├── monitor.py     # 心跳监控
│   └── report.py      # 失败报告生成
└── references/        # 参考文档
    └── README.md      # 完整文档
```

## 定时任务

```bash
# 每天凌晨2点自动备份
crontab -e
0 2 * * * python3 ~/.openclaw/skills/openclaw-doctor/scripts/backup.py >> /tmp/openclaw-backup.log 2>&1
```

## 输出日志

- 备份：`/tmp/openclaw-backup.log`
- 修复：`/tmp/openclaw-fix.log`
- 监控：`/tmp/openclaw-monitor.log`
- 报告：`~/Desktop/openclaw_fix_report_*.md`
