"""
Apple-style Deadline Tracker UI
macOS 原生设计风格 — 毛玻璃、侧边栏、圆角、系统配色
"""

import sys
from datetime import date, datetime, timedelta

from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter, QPainterPath, QBrush, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QScrollArea,
    QSizePolicy,
)

from conferences import CONFERENCES, CATEGORIES
from config_manager import load_config, save_config, add_tracked, remove_tracked, mark_synced
from apple_integration import add_calendar_event, add_reminder, get_calendar_list, get_reminder_lists


# ─── macOS 风格配色 ───
COLORS = {
    "bg": "#f5f5f7",
    "sidebar": "rgba(255,255,255,0.72)",
    "card": "#ffffff",
    "text": "#1d1d1f",
    "text_secondary": "#86868b",
    "accent": "#007aff",
    "accent_hover": "#0056b3",
    "red": "#ff3b30",
    "orange": "#ff9500",
    "yellow": "#ffcc00",
    "green": "#34c759",
    "border": "rgba(0,0,0,0.06)",
    "shadow": "rgba(0,0,0,0.08)",
    "sidebar_selected": "rgba(0,122,255,0.12)",
}

FONTS = {
    "title": ("SF Pro Display", 20, True),
    "subtitle": ("SF Pro Text", 13, False),
    "body": ("SF Pro Text", 13, False),
    "caption": ("SF Pro Text", 11, False),
    "number": ("SF Pro Display", 28, True),
}


class SidebarButton(QPushButton):
    """macOS 风格侧边栏按钮"""
    def __init__(self, icon_text, label, parent=None):
        super().__init__(parent)
        self.setText(f"  {icon_text}  {label}")
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                color: #1d1d1f;
                font-size: 13px;
                text-align: left;
                padding: 0 12px;
            }
            QPushButton:hover {
                background: rgba(0,0,0,0.04);
            }
            QPushButton:checked {
                background: rgba(0,122,255,0.12);
                color: #007aff;
                font-weight: 500;
            }
        """)


class StatCard(QFrame):
    """macOS 风格统计卡片"""
    def __init__(self, title, value, color="#007aff", parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 80)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(2)

        val = QLabel(str(value))
        val.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold; font-family: SF Pro Display;")
        layout.addWidget(val)

        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        layout.addWidget(lbl)


class DeadlineItem(QFrame):
    """macOS 风格截稿日期行"""
    def __init__(self, name, deadline, days_left, synced=False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['card']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
            QFrame:hover {{
                border: 1px solid rgba(0,122,255,0.2);
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # 状态指示
        if days_left <= 7:
            dot_color = COLORS["red"]
            urgency = "紧急"
        elif days_left <= 14:
            dot_color = COLORS["orange"]
            urgency = f"{days_left}天"
        elif days_left <= 30:
            dot_color = COLORS["yellow"]
            urgency = f"{days_left}天"
        else:
            dot_color = COLORS["green"]
            urgency = f"{days_left}天"

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {dot_color}; font-size: 10px;")
        dot.setFixedWidth(12)
        layout.addWidget(dot)

        # 会议名
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px; font-weight: 500;")
        layout.addWidget(name_lbl, 1)

        # 倒计时
        days_lbl = QLabel(urgency)
        days_lbl.setStyleSheet(f"color: {dot_color}; font-size: 13px; font-weight: 600;")
        days_lbl.setFixedWidth(50)
        days_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(days_lbl)

        # 截稿日期
        date_lbl = QLabel(deadline)
        date_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        date_lbl.setFixedWidth(90)
        layout.addWidget(date_lbl)

        # 同步状态
        sync_lbl = QLabel("✓" if synced else "")
        sync_lbl.setStyleSheet(f"color: {COLORS['green'] if synced else COLORS['text_secondary']}; font-size: 14px;")
        sync_lbl.setFixedWidth(20)
        sync_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sync_lbl)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deadline Tracker")
        self.setMinimumSize(960, 640)
        self.setStyleSheet(f"background: {COLORS['bg']};")
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ─── 侧边栏 ───
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['sidebar']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(4)

        # App 标题
        app_title = QLabel("📅 Deadline")
        app_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1d1d1f; padding: 0 4px 8px 4px;")
        sidebar_layout.addWidget(app_title)

        sidebar_layout.addSpacing(8)

        # 侧边栏按钮
        self.sidebar_buttons = []
        pages = [
            ("📋", "已追踪"),
            ("🔍", "会议库"),
            ("➕", "添加会议"),
            ("⚙️", "设置"),
        ]
        for icon, label in pages:
            btn = SidebarButton(icon, label)
            btn.clicked.connect(lambda checked, b=btn: self._on_sidebar_click(b))
            sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        sidebar_layout.addStretch()

        # 底部版本
        ver = QLabel("v1.1")
        ver.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; padding: 4px;")
        sidebar_layout.addWidget(ver)

        main_layout.addWidget(sidebar)

        # ─── 内容区 ───
        content = QWidget()
        content.setStyleSheet(f"background: {COLORS['bg']};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        # 添加页面
        self.stack.addWidget(self._build_tracked_page())
        self.stack.addWidget(self._build_browse_page())
        self.stack.addWidget(self._build_add_page())
        self.stack.addWidget(self._build_settings_page())

        main_layout.addWidget(content)

        # 默认选中第一个
        self.sidebar_buttons[0].setChecked(True)

    def _on_sidebar_click(self, clicked_btn):
        for i, btn in enumerate(self.sidebar_buttons):
            if btn == clicked_btn:
                btn.setChecked(True)
                self.stack.setCurrentIndex(i)
            else:
                btn.setChecked(False)

    # ─────────────── 页面构建 ───────────────
    def _build_tracked_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # 标题
        title = QLabel("已追踪的会议")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1d1d1f;")
        layout.addWidget(title)

        # 统计卡片
        stats = QHBoxLayout()
        stats.setSpacing(12)
        self.card_total = StatCard("追踪中", "0", COLORS["accent"])
        self.card_urgent = StatCard("紧急", "0", COLORS["red"])
        self.card_synced = StatCard("已同步", "0", COLORS["green"])
        stats.addWidget(self.card_total)
        stats.addWidget(self.card_urgent)
        stats.addWidget(self.card_synced)
        stats.addStretch()
        layout.addLayout(stats)

        # 按钮栏
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        self.btn_sync = QPushButton("☁️  同步到日历")
        self.btn_sync.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background: {COLORS['accent_hover']}; }}
        """)
        self.btn_sync.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sync.clicked.connect(self._sync_all)
        btn_bar.addWidget(self.btn_sync)

        btn_remove = QPushButton("移除选中")
        btn_remove.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['red']};
                border: 1px solid {COLORS['red']};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background: rgba(255,59,48,0.08); }}
        """)
        btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_remove.clicked.connect(self._remove_selected)
        btn_bar.addWidget(btn_remove)

        btn_bar.addStretch()
        layout.addLayout(btn_bar)

        # 列表滚动区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.tracked_container = QWidget()
        self.tracked_layout = QVBoxLayout(self.tracked_container)
        self.tracked_layout.setSpacing(4)
        self.tracked_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.tracked_container)
        layout.addWidget(scroll)

        return page

    def _build_browse_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("会议库")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1d1d1f;")
        layout.addWidget(title)

        # 搜索和筛选
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(12)

        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("🔍 搜索会议...")
        self.edit_search.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: {COLORS['text']};
            }}
            QLineEdit:focus {{ border: 1px solid {COLORS['accent']}; }}
        """)
        self.edit_search.textChanged.connect(self._filter_browse)
        filter_bar.addWidget(self.edit_search, 2)

        self.combo_cat = QComboBox()
        self.combo_cat.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: {COLORS['text']};
            }}
        """)
        self.combo_cat.addItem("全部分类")
        self.combo_cat.addItems(CATEGORIES)
        self.combo_cat.currentTextChanged.connect(self._filter_browse)
        filter_bar.addWidget(self.combo_cat, 1)

        layout.addLayout(filter_bar)

        # 会议列表
        self.table_browse = QTableWidget()
        self.table_browse.setColumnCount(4)
        self.table_browse.setHorizontalHeaderLabels(["缩写", "全称", "分类", ""])
        self.table_browse.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_browse.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_browse.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_browse.setStyleSheet(f"""
            QTableWidget {{
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                gridline-color: {COLORS['border']};
                font-size: 13px;
                color: {COLORS['text']};
            }}
            QHeaderView::section {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                padding: 8px;
                font-weight: 600;
                color: {COLORS['text_secondary']};
            }}
        """)
        layout.addWidget(self.table_browse)

        return page

    def _build_add_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("添加会议")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1d1d1f;")
        layout.addWidget(title)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        form = QFormLayout(card)
        form.setContentsMargins(24, 24, 24, 24)
        form.setSpacing(16)

        input_style = f"""
            QLineEdit, QDateEdit, QTextEdit {{
                background: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                color: {COLORS['text']};
            }}
            QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {{
                border: 1px solid {COLORS['accent']};
            }}
        """
        label_style = f"color: {COLORS['text']}; font-size: 13px; font-weight: 500;"

        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("例: NeurIPS 2026")
        self.edit_name.setStyleSheet(input_style)
        lbl = QLabel("会议名称")
        lbl.setStyleSheet(label_style)
        form.addRow(lbl, self.edit_name)

        self.edit_abbr = QLineEdit()
        self.edit_abbr.setPlaceholderText("例: NeurIPS")
        self.edit_abbr.setStyleSheet(input_style)
        lbl = QLabel("缩写")
        lbl.setStyleSheet(label_style)
        form.addRow(lbl, self.edit_abbr)

        self.date_deadline = QDateEdit()
        self.date_deadline.setCalendarPopup(True)
        self.date_deadline.setDate(QDate.currentDate().addMonths(3))
        self.date_deadline.setStyleSheet(input_style)
        lbl = QLabel("截稿日期")
        lbl.setStyleSheet(label_style)
        form.addRow(lbl, self.date_deadline)

        self.edit_note = QTextEdit()
        self.edit_note.setPlaceholderText("备注（可选）")
        self.edit_note.setMaximumHeight(80)
        self.edit_note.setStyleSheet(input_style)
        lbl = QLabel("备注")
        lbl.setStyleSheet(label_style)
        form.addRow(lbl, self.edit_note)

        layout.addWidget(card)

        btn_add = QPushButton("➕  添加到追踪")
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background: {COLORS['accent_hover']}; }}
        """)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._add_custom)
        layout.addWidget(btn_add)

        layout.addStretch()
        return page

    def _build_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("设置")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1d1d1f;")
        layout.addWidget(title)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        form = QFormLayout(card)
        form.setContentsMargins(24, 24, 24, 24)
        form.setSpacing(16)

        input_style = f"""
            QComboBox, QSpinBox {{
                background: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                color: {COLORS['text']};
            }}
        """
        label_style = f"color: {COLORS['text']}; font-size: 13px; font-weight: 500;"

        self.combo_calendar = QComboBox()
        self.combo_calendar.setEditable(True)
        self.combo_calendar.setStyleSheet(input_style)
        try:
            self.combo_calendar.addItems(get_calendar_list())
        except Exception:
            self.combo_calendar.addItem("个人")
        lbl = QLabel("日历")
        lbl.setStyleSheet(label_style)
        form.addRow(lbl, self.combo_calendar)

        self.combo_reminders = QComboBox()
        self.combo_reminders.setEditable(True)
        self.combo_reminders.setStyleSheet(input_style)
        try:
            self.combo_reminders.addItems(get_reminder_lists())
        except Exception:
            self.combo_reminders.addItem("提醒")
        lbl = QLabel("提醒列表")
        lbl.setStyleSheet(label_style)
        form.addRow(lbl, self.combo_reminders)

        self.spin_alert = QSpinBox()
        self.spin_alert.setRange(1, 180)
        self.spin_alert.setValue(30)
        self.spin_alert.setSuffix(" 天")
        self.spin_alert.setStyleSheet(input_style)
        lbl = QLabel("提前提醒")
        lbl.setStyleSheet(label_style)
        form.addRow(lbl, self.spin_alert)

        self.chk_auto = QCheckBox("添加时自动同步")
        self.chk_auto.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px;")
        form.addRow("", self.chk_auto)

        layout.addWidget(card)

        btn_save = QPushButton("💾  保存设置")
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background: {COLORS['accent_hover']}; }}
        """)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._save_settings)
        layout.addWidget(btn_save)

        layout.addStretch()
        return page

    # ─────────────── 数据加载 ───────────────
    def _load_data(self):
        self.config = load_config()
        self._refresh_tracked()
        self._fill_browse()
        self._load_settings()

    def _refresh_tracked(self):
        self.config = load_config()
        tracked = self.config.get("tracked", [])
        today = date.today()

        # 清空
        while self.tracked_layout.count():
            item = self.tracked_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        urgent = 0
        synced = 0
        for i, t in enumerate(tracked):
            d = datetime.strptime(t["deadline"], "%Y-%m-%d").date()
            days_left = (d - today).days
            if days_left <= 7:
                urgent += 1
            if t.get("synced"):
                synced += 1
            item_widget = DeadlineItem(t["name"], t["deadline"], days_left, t.get("synced", False))
            self.tracked_layout.addWidget(item_widget)

        self.tracked_layout.addStretch()

        # 更新统计
        self.card_total.findChild(QLabel).setText(str(len(tracked)))
        self.card_urgent.findChild(QLabel).setText(str(urgent))
        self.card_synced.findChild(QLabel).setText(str(synced))

    def _fill_browse(self):
        items = list(CONFERENCES.items())
        self._browse_data = items
        self._populate_browse(items)

    def _populate_browse(self, items):
        self.table_browse.setRowCount(len(items))
        for i, (abbr, info) in enumerate(items):
            self.table_browse.setItem(i, 0, QTableWidgetItem(abbr))
            self.table_browse.setItem(i, 1, QTableWidgetItem(info["full_name"]))
            self.table_browse.setItem(i, 2, QTableWidgetItem(info["category"]))

            btn = QPushButton("追踪")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['accent']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-size: 12px;
                }}
                QPushButton:hover {{ background: {COLORS['accent_hover']}; }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, a=abbr: self._add_from_browse(a))
            self.table_browse.setCellWidget(i, 3, btn)

    def _filter_browse(self):
        cat = self.combo_cat.currentText()
        search = self.edit_search.text().lower()
        filtered = [
            (a, v) for a, v in self._browse_data
            if (cat == "全部分类" or v["category"] == cat)
            and (not search or search in a.lower() or search in v["full_name"].lower())
        ]
        self._populate_browse(filtered)

    def _load_settings(self):
        settings = self.config.get("settings", {})
        self.spin_alert.setValue(settings.get("alert_days_before", 30))
        self.chk_auto.setChecked(settings.get("auto_sync", False))
        cal = settings.get("calendar_name", "个人")
        idx = self.combo_calendar.findText(cal)
        if idx >= 0:
            self.combo_calendar.setCurrentIndex(idx)
        rem = settings.get("reminder_list", "提醒")
        idx = self.combo_reminders.findText(rem)
        if idx >= 0:
            self.combo_reminders.setCurrentIndex(idx)

    def _save_settings(self):
        self.config["settings"] = {
            "calendar_name": self.combo_calendar.currentText(),
            "reminder_list": self.combo_reminders.currentText(),
            "alert_days_before": self.spin_alert.value(),
            "auto_sync": self.chk_auto.isChecked(),
        }
        save_config(self.config)
        QMessageBox.information(self, "保存成功", "设置已保存 ✅")

    # ─────────────── 操作 ───────────────
    def _add_from_browse(self, abbr):
        conf = CONFERENCES[abbr]
        if not conf["rounds"]:
            QMessageBox.information(self, "滚动投稿", f"{abbr} 是滚动投稿期刊，没有固定截稿日期。")
            return
        added = 0
        for r in conf["rounds"]:
            add_tracked(f"{abbr} ({r['year']}) — {r['note']}", r["deadline"].strftime("%Y-%m-%d"), conf["full_name"])
            added += 1
        if self.chk_auto.isChecked():
            self._sync_latest(added)
        self._refresh_tracked()
        QMessageBox.information(self, "已添加", f"已添加 {abbr} 的 {added} 个截稿日期 ✅")

    def _add_custom(self):
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "缺少信息", "请输入会议名称")
            return
        deadline = self.date_deadline.date().toPyDate().strftime("%Y-%m-%d")
        note = self.edit_note.toPlainText().strip()
        add_tracked(name, deadline, note)
        if self.chk_auto.isChecked():
            self._sync_latest(1)
        self.edit_name.clear()
        self.edit_abbr.clear()
        self.edit_note.clear()
        self._refresh_tracked()
        QMessageBox.information(self, "已添加", f"已添加 {name} ✅")

    def _remove_selected(self):
        # 简化：移除最后一个
        config = load_config()
        if config["tracked"]:
            remove_tracked(len(config["tracked"]) - 1)
            self._refresh_tracked()

    def _sync_all(self):
        tracked = self.config.get("tracked", [])
        to_sync = [(i, t) for i, t in enumerate(tracked) if not t.get("synced")]
        if not to_sync:
            QMessageBox.information(self, "无需同步", "所有会议都已同步 ✅")
            return
        cal = self.combo_calendar.currentText()
        rem = self.combo_reminders.currentText()
        alert_days = self.spin_alert.value()
        success = 0
        for i, item in to_sync:
            d = datetime.strptime(item["deadline"], "%Y-%m-%d").date()
            ok1 = add_calendar_event(item["name"], d, item.get("note", ""), calendar_name=cal, alert_days_before=alert_days)
            ok2 = add_reminder(f"截稿: {item['name']}", d - timedelta(days=alert_days), f"距离 {item['name']} 截稿还有 {alert_days} 天", list_name=rem)
            if ok1 and ok2:
                mark_synced(i)
                success += 1
        self._refresh_tracked()
        QMessageBox.information(self, "同步完成", f"已同步 {success}/{len(to_sync)} 个会议 ✅")

    def _sync_latest(self, count):
        self.config = load_config()
        tracked = self.config.get("tracked", [])
        cal = self.combo_calendar.currentText()
        rem = self.combo_reminders.currentText()
        alert_days = self.spin_alert.value()
        for item in tracked[-count:]:
            d = datetime.strptime(item["deadline"], "%Y-%m-%d").date()
            add_calendar_event(item["name"], d, item.get("note", ""), calendar_name=cal, alert_days_before=alert_days)
            add_reminder(f"截稿: {item['name']}", d - timedelta(days=alert_days), f"距离 {item['name']} 截稿还有 {alert_days} 天", list_name=rem)
            item["synced"] = True
        save_config(self.config)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DeadlineTracker")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
