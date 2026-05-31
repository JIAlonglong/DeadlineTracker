"""
Apple Calendar & Reminders 集成模块
通过 osascript 调用 macOS 原生 Calendar 和 Reminders
"""

import subprocess
from datetime import date, timedelta


def add_calendar_event(
    title: str,
    event_date: date,
    notes: str = "",
    calendar_name: str = "默认",
    alert_days_before: int = 30,
) -> bool:
    """在 Apple Calendar 中创建事件"""
    # 创建截止日事件
    event_date_str = event_date.strftime("%Y-%m-%d")
    end_date_str = (event_date + timedelta(days=1)).strftime("%Y-%m-%d")

    # 构建 AppleScript
    script = f'''
tell application "Calendar"
    tell calendar "{calendar_name}"
        make new event with properties {{
            summary: "{_escape(title)}",
            start date: date "{event_date_str}",
            end date: date "{end_date_str}",
            allday event: true,
            description: "{_escape(notes)}"
        }}
    end tell
end tell
'''

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            # 如果指定日历不存在，尝试用默认日历
            script_fallback = script.replace(
                f'tell calendar "{calendar_name}"',
                'tell calendar 1',
            )
            subprocess.run(
                ["osascript", "-e", script_fallback],
                capture_output=True,
                text=True,
                timeout=15,
                check=True,
            )
    except Exception as e:
        print(f"Calendar error: {e}")
        return False

    # 添加提前提醒事件（截止前1个月）
    reminder_date = event_date - timedelta(days=alert_days_before)
    reminder_date_str = reminder_date.strftime("%Y-%m-%d")
    reminder_end_str = (reminder_date + timedelta(days=1)).strftime("%Y-%m-%d")

    reminder_script = f'''
tell application "Calendar"
    tell calendar "{calendar_name}"
        make new event with properties {{
            summary: "⏰ 准备投稿: {_escape(title)}",
            start date: date "{reminder_date_str}",
            end date: date "{reminder_end_str}",
            allday event: true,
            description: "距离截稿还有 {alert_days_before} 天，请开始准备！\\n\\n{_escape(notes)}"
        }}
    end tell
end tell
'''
    try:
        subprocess.run(
            ["osascript", "-e", reminder_script],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as e:
        print(f"Reminder calendar event error: {e}")

    return True


def add_reminder(
    title: str,
    due_date: date,
    notes: str = "",
    list_name: str = "提醒事项",
) -> bool:
    """在 Apple Reminders 中创建提醒"""
    due_date_str = due_date.strftime("%Y-%m-%d")

    script = f'''
tell application "Reminders"
    tell list "{list_name}"
        make new reminder with properties {{
            name: "{_escape(title)}",
            due date: date "{due_date_str}",
            body: "{_escape(notes)}"
        }}
    end tell
end tell
'''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            # fallback to default list
            script_fallback = script.replace(
                f'tell list "{list_name}"', "tell list 1"
            )
            subprocess.run(
                ["osascript", "-e", script_fallback],
                capture_output=True,
                text=True,
                timeout=15,
                check=True,
            )
    except Exception as e:
        print(f"Reminders error: {e}")
        return False
    return True


def get_calendar_list() -> list:
    """获取所有日历名称"""
    script = '''
tell application "Calendar"
    set calNames to {}
    repeat with c in calendars
        set end of calNames to name of c
    end repeat
    return calNames
end tell
'''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        names = [n.strip() for n in result.stdout.strip().split(",")]
        return [n for n in names if n]
    except Exception:
        return ["个人"]


def get_reminder_lists() -> list:
    """获取所有提醒事项列表名称"""
    script = '''
tell application "Reminders"
    set listNames to {}
    repeat with l in lists
        set end of listNames to name of l
    end repeat
    return listNames
end tell
'''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        names = [n.strip() for n in result.stdout.strip().split(",")]
        return [n for n in names if n]
    except Exception:
        return ["提醒"]


def _escape(s: str) -> str:
    """转义 AppleScript 字符串中的特殊字符"""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


if __name__ == "__main__":
    # 测试
    print("Calendars:", get_calendar_list())
    print("Reminder lists:", get_reminder_lists())
