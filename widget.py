"""
桌面小组件 — 类似 macOS 天气/日期组件风格
置顶、无边框、半透明、紧凑显示近期截稿日期
"""

import sys
from datetime import date, datetime
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QLinearGradient
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
)

from config_manager import load_config, get_upcoming


class DeadlineWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_pos = QPoint()
        self._init_window()
        self._init_ui()
        self._refresh()
        # 每分钟刷新一次
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(60000)

    def _init_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(280)
        self.move(100, 100)

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 主卡片容器
        self.card = QWidget()
        self.card.setObjectName("card")
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(16, 14, 16, 14)
        self.card_layout.setSpacing(6)

        # 标题栏
        header = QLabel("📅 Deadline")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_layout.addWidget(header)

        # 分隔线
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.1);")
        self.card_layout.addWidget(sep)

        # 内容区 — 动态添加
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(4)
        self.card_layout.addLayout(self.content_layout)

        # 底部提示
        self.footer = QLabel("拖动移动 · 双击刷新")
        self.footer.setObjectName("footer")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_layout.addWidget(self.footer)

        self.layout.addWidget(self.card)

        # 阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        self.card.setGraphicsEffect(shadow)

        self.setStyleSheet(self._style())

    def _style(self):
        return """
        #card {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(30, 30, 50, 0.92),
                stop:1 rgba(40, 40, 65, 0.92));
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        #header {
            font-size: 16px;
            font-weight: bold;
            color: #f5e0dc;
            padding: 2px 0;
        }
        #footer {
            font-size: 10px;
            color: rgba(255,255,255,0.3);
            padding-top: 4px;
        }
        .deadline-item {
            background: rgba(255,255,255,0.04);
            border-radius: 8px;
            padding: 6px 10px;
            margin: 1px 0;
        }
        """

    def _refresh(self):
        # 清空旧内容
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        upcoming = get_upcoming(days=90)

        if not upcoming:
            empty = QLabel("暂无追踪的会议\n去主程序添加一下吧~")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 12px; padding: 16px 0;")
            self.content_layout.addWidget(empty)
            return

        for item in upcoming[:6]:  # 最多显示 6 条
            days = item["days_left"]
            name = item["name"]

            # 截断过长的名字
            if len(name) > 20:
                name = name[:18] + "…"

            # 颜色和图标
            if days <= 7:
                color = "#f38ba8"
                icon = "🔴"
                urgency = "紧急"
            elif days <= 14:
                color = "#fab387"
                icon = "🟠"
                urgency = f"{days}天"
            elif days <= 30:
                color = "#f9e2af"
                icon = "🟡"
                urgency = f"{days}天"
            else:
                color = "#a6e3a1"
                icon = "🟢"
                urgency = f"{days}天"

            row = QLabel(
                f'{icon}  <span style="color:{color};font-weight:bold;">{urgency}</span>'
                f'  <span style="color:#cdd6f4;">{name}</span>'
            )
            row.setTextFormat(Qt.TextFormat.RichText)
            row.setProperty("class", "deadline-item")
            row.setStyleSheet(
                "background: rgba(255,255,255,0.04); border-radius: 8px; "
                "padding: 6px 10px; font-size: 12px;"
            )
            self.content_layout.addWidget(row)

        # 调整窗口高度
        self.adjustSize()

    # ─── 拖动 ───
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        self._refresh()

    # ─── 右键退出 ───
    def contextMenuEvent(self, event):
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction("🔄 刷新", self._refresh)
        menu.addAction("❌ 退出", QApplication.quit)
        menu.exec(event.globalPos())


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DeadlineWidget")
    widget = DeadlineWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
