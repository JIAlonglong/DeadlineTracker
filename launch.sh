#!/bin/bash
# Deadline Tracker 启动器
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true

if [ "$1" = "--app" ]; then
    python3 main.py --app
else
    python3 main.py --widget
fi
