#!/usr/bin/env python3
"""
OpenClaw Doctor CLI 入口
提供命令行界面：monitor, fix, backup, report
"""

import os
import sys
import click

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from openclaw_doctor.monitor import run_monitor
from openclaw_doctor.fix import run_fix
from openclaw_doctor.backup import run_backup_cli
from openclaw_doctor.report import run_report


@click.group()
@click.version_option(version="0.1.0")
def main():
    """OpenClaw Doctor - 自动修复和监控工具"""
    pass


@main.command()
@click.option("--interval", default=300, help="检查间隔（秒），默认 300 秒")
@click.option("--max-failures", default=3, help="连续失败次数阈值，默认 3 次")
def monitor(interval, max_failures):
    """启动心跳监控"""
    run_monitor(interval=interval, max_failures=max_failures)


@main.command()
def fix():
    """执行自动修复"""
    run_fix()


@main.command()
@click.option("--output", default=None, help="输出路径")
def backup(output):
    """备份配置文件"""
    run_backup_cli(output=output)


@main.command()
@click.option("--output", default=None, help="报告输出路径")
def report(output):
    """生成故障报告"""
    run_report(output=output)


if __name__ == "__main__":
    main()
