# OpenClaw Doctor 🩺

OpenClaw 配置自动修复和心跳监控工具。

## 功能

- 🔧 自动修复 Gateway 配置问题
- 💾 自动备份配置文件
- 📊 心跳监控服务状态
- 📝 生成故障报告

## 安装

```bash
# 克隆项目
git clone https://github.com/nidao003/openclaw-doctor-skills.git
cd openclaw-doctor-skills

# 安装（开发模式）
pip install -e .

# 或安装到系统
pip install .
```

## 使用方法

```bash
# 备份配置
openclaw-doctor backup

# 执行修复
openclaw-doctor fix

# 生成故障报告
openclaw-doctor report

# 启动心跳监控（后台）
nohup openclaw-doctor monitor > /tmp/openclaw-doctor.log 2>&1 &

# 或使用 Python 模块方式
python3.11 -m openclaw_doctor.cli monitor
```

## 命令行选项

| 命令 | 说明 |
|------|------|
| `backup` | 备份配置文件到 ~/.openclaw/backups |
| `fix` | 执行自动修复（指数退避重试） |
| `report` | 生成故障诊断报告到桌面 |
| `monitor` | 启动心跳监控（默认 5 分钟间隔） |

### monitor 选项

```bash
openclaw-doctor monitor --interval 300 --max-failures 3
```

- `--interval`: 检查间隔（秒），默认 300 秒
- `--max-failures`: 连续失败次数阈值，默认 3 次

## 配置

工具会自动使用以下路径：
- OpenClaw 配置: `~/.openclaw/openclaw.json`
- 备份目录: `~/.openclaw/backups`
- 日志目录: `~/.openclaw/logs`

## 依赖

- Python 3.10+
- click >= 8.0.0

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest
```

## License

MIT
