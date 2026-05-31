#!/usr/bin/env python3
"""
Deadline Tracker — 会议截稿日期管理器
支持两种模式：
  --widget   桌面小组件模式（默认）
  --app      完整应用窗口
"""

import sys
import os
import argparse

# 确保项目路径在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import get_upcoming


def print_banner():
    """启动横幅"""
    banner = """
╔═══════════════════════════════════════════════════════╗
║         📅  Deadline Tracker  v1.1                    ║
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
    parser = argparse.ArgumentParser(description="Deadline Tracker")
    parser.add_argument("--app", action="store_true", help="启动完整应用窗口")
    parser.add_argument("--widget", action="store_true", default=True, help="启动桌面小组件（默认）")
    args = parser.parse_args()

    print_banner()
    check_upcoming()

    if args.app:
        print("🚀 正在启动完整应用...")
        from ui_main import main as app_main
        app_main()
    else:
        print("🧩 正在启动桌面小组件...")
        from widget import main as widget_main
        widget_main()
