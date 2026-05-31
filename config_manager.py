"""
用户配置管理：保存/加载已追踪的会议、提醒设置等
"""

import json
import os
from datetime import date, datetime
from pathlib import Path

CONFIG_DIR = Path.home() / ".deadline_tracker"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _default_config():
    return {
        "tracked": [],       # 用户添加的会议 [{name, deadline, note, synced}]
        "settings": {
            "calendar_name": "默认",
            "reminder_list": "提醒事项",
            "alert_days_before": 30,
            "auto_sync": False,
        },
    }


def _ensure_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    _ensure_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return _default_config()


def save_config(config: dict):
    _ensure_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2, default=str)


def add_tracked(name: str, deadline: str, note: str = ""):
    """添加一个要追踪的会议"""
    config = load_config()
    config["tracked"].append(
        {
            "name": name,
            "deadline": deadline,  # YYYY-MM-DD
            "note": note,
            "synced": False,
        }
    )
    save_config(config)


def remove_tracked(index: int):
    config = load_config()
    if 0 <= index < len(config["tracked"]):
        config["tracked"].pop(index)
        save_config(config)


def mark_synced(index: int):
    config = load_config()
    if 0 <= index < len(config["tracked"]):
        config["tracked"][index]["synced"] = True
        save_config(config)


def get_upcoming(days: int = 90) -> list:
    """获取未来 N 天内的截稿日期"""
    today = date.today()
    config = load_config()
    upcoming = []
    for item in config["tracked"]:
        try:
            d = datetime.strptime(item["deadline"], "%Y-%m-%d").date()
            delta = (d - today).days
            if 0 <= delta <= days:
                upcoming.append({**item, "days_left": delta, "date_obj": d})
        except ValueError:
            continue
    upcoming.sort(key=lambda x: x["days_left"])
    return upcoming
