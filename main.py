#!/usr/bin/env python3
"""
Deadline Tracker — 会议截稿日期管理器
主入口：启动菜单栏常驻 + 桌面窗口
"""

import sys
import os
import threading
import signal

# 确保项目路径在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_main import main as ui_main
from config_manager import load_config, get_upcoming


def print_banner():
    """启动横幅"""
    banner = """
╔═══════════════════════════════════════════════════════╗
║         📅  Deadline Tracker  v1.0                    ║
║    CS / Robotics / AI 会议截稿日期管理器              ║
╚═══════════════════════════════════════════════════════╝
"""
    print(banner)


def check_upcoming():
    """启动时检查近期截止日期"""
    upcoming = get_upcoming(days=60)
    if upcoming:
        print("⚠️  近期截稿日期提醒:")
        for item in upcoming:
            days = item["days_left"]
            urgency = "🔴" if days <= 7 else "🟡" if days <= 30 else "🟢"
            print(f"   {urgency} {item['name']} — 还有 {days} 天")
        print()


if __name__ == "__main__":
    print_banner()
    check_upcoming()
    print("🚀 正在启动桌面界面...")
    ui_main()
