# OpenClaw Doctor 🩺

自动修复 OpenClaw 配置错误的技能。

## 功能

- 🔧 自动修复 Gateway 配置问题
- 💾 自动备份配置文件
- 📊 心跳监控服务状态
- 📝 生成故障报告

## 安装

```bash
git clone https://github.com/nidao003/openclaw-doctor-skills.git ~/.openclaw/skills/openclaw-doctor
```

或使用 SSH：

```bash
git clone git@github.com:nidao003/openclaw-doctor-skills.git ~/.openclaw/skills/openclaw-doctor
```

## 快速使用

```bash
# 手动备份
python3 ~/.openclaw/skills/openclaw-doctor/scripts/backup.py

# 手动修复
python3 ~/.openclaw/skills/openclaw-doctor/scripts/fix.py

# 启动心跳监控（后台）
nohup python3 ~/.openclaw/skills/openclaw-doctor/scripts/monitor.py > /tmp/openclaw-monitor.log 2>&1 &
```

## 文档

详细使用说明请参阅 [references/README.md](references/README.md)

## GitHub

https://github.com/nidao003/openclaw-doctor-skills
