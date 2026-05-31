"""
PyQt6 配置界面：管理会议、添加/删除、同步到日历和提醒事项
"""

import sys
from datetime import date, datetime, timedelta

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
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
    QSplitter,
)

from conferences import CONFERENCES, CATEGORIES
from config_manager import load_config, save_config, add_tracked, remove_tracked, mark_synced
from apple_integration import add_calendar_event, add_reminder, get_calendar_list, get_reminder_lists


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📅 Deadline Tracker — 会议截稿日期管理")
        self.setMinimumSize(900, 650)
        self.setStyleSheet(self._style())
        self._init_ui()
        self._load_data()

    def _style(self):
        return """
        QMainWindow {
            background-color: #1e1e2e;
        }
        QTabWidget::pane {
            border: 1px solid #45475a;
            border-radius: 6px;
            background-color: #1e1e2e;
        }
        QTabBar::tab {
            background: #313244;
            color: #cdd6f4;
            padding: 8px 20px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: #45475a;
            color: #f5e0dc;
        }
        QTableWidget {
            background-color: #181825;
            color: #cdd6f4;
            gridline-color: #313244;
            border: none;
            font-size: 13px;
        }
        QTableWidget::item:selected {
            background-color: #45475a;
        }
        QHeaderView::section {
            background-color: #313244;
            color: #f5e0dc;
            padding: 6px;
            border: none;
            font-weight: bold;
        }
        QPushButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #74c7ec;
        }
        QPushButton:pressed {
            background-color: #89dceb;
        }
        QPushButton#danger {
            background-color: #f38ba8;
        }
        QPushButton#danger:hover {
            background-color: #eba0ac;
        }
        QPushButton#sync {
            background-color: #a6e3a1;
        }
        QPushButton#sync:hover {
            background-color: #94e2d5;
        }
        QLabel {
            color: #cdd6f4;
            font-size: 13px;
        }
        QLabel#title {
            font-size: 18px;
            font-weight: bold;
            color: #f5e0dc;
        }
        QLabel#subtitle {
            font-size: 14px;
            color: #a6adc8;
        }
        QLineEdit, QDateEdit, QComboBox, QSpinBox, QTextEdit {
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 4px;
            padding: 6px;
            font-size: 13px;
        }
        QGroupBox {
            border: 1px solid #45475a;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 15px;
            color: #f5e0dc;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px;
        }
        QCheckBox {
            color: #cdd6f4;
            font-size: 13px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        """

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)

        # 标题
        title = QLabel("📅 会议截稿日期追踪器")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("CS / 机器人学 / AI 顶会和期刊 · 自动同步日历和提醒事项")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Tab 控件
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: 已追踪的会议
        self.tabs.addTab(self._build_tracked_tab(), "📋 已追踪")
        # Tab 2: 浏览会议库
        self.tabs.addTab(self._build_browse_tab(), "🔍 会议库")
        # Tab 3: 手动添加
        self.tabs.addTab(self._build_add_tab(), "➕ 添加会议")
        # Tab 4: 设置
        self.tabs.addTab(self._build_settings_tab(), "⚙️ 设置")

    # ─────────────── Tab 1: 已追踪 ───────────────
    def _build_tracked_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        btn_bar = QHBoxLayout()
        self.btn_sync = QPushButton("☁️  同步到日历 & 提醒事项")
        self.btn_sync.setObjectName("sync")
        self.btn_sync.clicked.connect(self._sync_all)
        btn_bar.addWidget(self.btn_sync)

        btn_refresh = QPushButton("🔄 刷新")
        btn_refresh.clicked.connect(self._load_data)
        btn_bar.addWidget(btn_refresh)

        btn_remove = QPushButton("🗑️  移除选中")
        btn_remove.setObjectName("danger")
        btn_remove.clicked.connect(self._remove_selected)
        btn_bar.addWidget(btn_remove)

        layout.addLayout(btn_bar)

        self.table_tracked = QTableWidget()
        self.table_tracked.setColumnCount(5)
        self.table_tracked.setHorizontalHeaderLabels(
            ["会议", "截稿日期", "天数", "备注", "已同步"]
        )
        self.table_tracked.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table_tracked.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table_tracked.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self.table_tracked)

        # 底部统计
        self.lbl_stats = QLabel("")
        layout.addWidget(self.lbl_stats)

        return w

    # ─────────────── Tab 2: 会议库 ───────────────
    def _build_browse_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        # 分类筛选
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("分类:"))
        self.combo_cat = QComboBox()
        self.combo_cat.addItem("全部")
        self.combo_cat.addItems(CATEGORIES)
        self.combo_cat.currentTextChanged.connect(self._filter_browse)
        filter_bar.addWidget(self.combo_cat)

        filter_bar.addWidget(QLabel("搜索:"))
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("输入会议名称...")
        self.edit_search.textChanged.connect(self._filter_browse)
        filter_bar.addWidget(self.edit_search)

        layout.addLayout(filter_bar)

        self.table_browse = QTableWidget()
        self.table_browse.setColumnCount(4)
        self.table_browse.setHorizontalHeaderLabels(
            ["缩写", "全称", "分类", "操作"]
        )
        self.table_browse.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table_browse.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table_browse.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self.table_browse)

        return w

    # ─────────────── Tab 3: 手动添加 ───────────────
    def _build_add_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        group = QGroupBox("添加自定义会议/期刊截稿")
        form = QFormLayout(group)

        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("例: My Conference 2026")
        form.addRow("会议名称:", self.edit_name)

        self.edit_abbr = QLineEdit()
        self.edit_abbr.setPlaceholderText("例: ICRA")
        form.addRow("缩写:", self.edit_abbr)

        self.date_deadline = QDateEdit()
        self.date_deadline.setCalendarPopup(True)
        self.date_deadline.setDate(QDate.currentDate().addMonths(3))
        form.addRow("截稿日期:", self.date_deadline)

        self.edit_note = QTextEdit()
        self.edit_note.setPlaceholderText("备注（可选）：如 OpenReview 链接等")
        self.edit_note.setMaximumHeight(80)
        form.addRow("备注:", self.edit_note)

        layout.addWidget(group)

        btn_add = QPushButton("➕ 添加到追踪列表")
        btn_add.clicked.connect(self._add_custom)
        layout.addWidget(btn_add)

        layout.addStretch()
        return w

    # ─────────────── Tab 4: 设置 ───────────────
    def _build_settings_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        group = QGroupBox("同步设置")
        form = QFormLayout(group)

        self.combo_calendar = QComboBox()
        self.combo_calendar.setEditable(True)
        try:
            self.combo_calendar.addItems(get_calendar_list())
        except Exception:
            self.combo_calendar.addItem("默认")
        form.addRow("日历名称:", self.combo_calendar)

        self.combo_reminders = QComboBox()
        self.combo_reminders.setEditable(True)
        try:
            self.combo_reminders.addItems(get_reminder_lists())
        except Exception:
            self.combo_reminders.addItem("提醒")
        form.addRow("提醒列表:", self.combo_reminders)

        self.spin_alert = QSpinBox()
        self.spin_alert.setRange(1, 180)
        self.spin_alert.setValue(30)
        self.spin_alert.setSuffix(" 天")
        form.addRow("提前提醒:", self.spin_alert)

        self.chk_auto = QCheckBox("添加会议时自动同步到日历")
        form.addRow("", self.chk_auto)

        layout.addWidget(group)

        btn_save = QPushButton("💾 保存设置")
        btn_save.clicked.connect(self._save_settings)
        layout.addWidget(btn_save)

        layout.addStretch()
        return w

    # ─────────────── 数据加载 ───────────────
    def _load_data(self):
        self.config = load_config()
        self._refresh_tracked()
        self._fill_browse()
        self._load_settings()

    def _refresh_tracked(self):
        self.config = load_config()
        tracked = self.config.get("tracked", [])
        self.table_tracked.setRowCount(len(tracked))

        today = date.today()
        for i, item in enumerate(tracked):
            d = datetime.strptime(item["deadline"], "%Y-%m-%d").date()
            days_left = (d - today).days

            self.table_tracked.setItem(i, 0, QTableWidgetItem(item["name"]))
            self.table_tracked.setItem(i, 1, QTableWidgetItem(item["deadline"]))

            days_item = QTableWidgetItem()
            if days_left < 0:
                days_item.setText(f"已过期 ({abs(days_left)}天前)")
                days_item.setForeground(QColor("#f38ba8"))
            elif days_left <= 7:
                days_item.setText(f"⚠️ {days_left} 天")
                days_item.setForeground(QColor("#fab387"))
            elif days_left <= 30:
                days_item.setText(f"📌 {days_left} 天")
                days_item.setForeground(QColor("#f9e2af"))
            else:
                days_item.setText(f"{days_left} 天")
                days_item.setForeground(QColor("#a6e3a1"))
            self.table_tracked.setItem(i, 2, days_item)

            self.table_tracked.setItem(i, 3, QTableWidgetItem(item.get("note", "")))
            self.table_tracked.setItem(
                i, 4, QTableWidgetItem("✅" if item.get("synced") else "❌")
            )

        # 统计
        synced = sum(1 for t in tracked if t.get("synced"))
        self.lbl_stats.setText(
            f"共 {len(tracked)} 个会议 · {synced} 个已同步 · "
            f"{len(tracked) - synced} 个待同步"
        )

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

            btn = QPushButton("➕ 追踪")
            btn.setMaximumWidth(80)
            btn.clicked.connect(lambda _, a=abbr: self._add_from_browse(a))
            self.table_browse.setCellWidget(i, 3, btn)

    def _filter_browse(self):
        cat = self.combo_cat.currentText()
        search = self.edit_search.text().lower()
        filtered = [
            (a, v)
            for a, v in self._browse_data
            if (cat == "全部" or v["category"] == cat)
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
            QMessageBox.information(
                self,
                "滚动投稿",
                f"{abbr} 是滚动投稿期刊，没有固定截稿日期。\n请使用「添加会议」标签手动添加。",
            )
            return

        added = 0
        for r in conf["rounds"]:
            add_tracked(
                f"{abbr} ({r['year']}) — {r['note']}",
                r["deadline"].strftime("%Y-%m-%d"),
                conf["full_name"],
            )
            added += 1

        if self.chk_auto.isChecked():
            self._sync_latest(added)

        self._refresh_tracked()
        QMessageBox.information(
            self, "已添加", f"已添加 {abbr} 的 {added} 个截稿日期 ✅"
        )

    def _add_custom(self):
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "缺少信息", "请输入会议名称")
            return

        abbr = self.edit_abbr.text().strip()
        deadline = self.date_deadline.date().toPyDate().strftime("%Y-%m-%d")
        note = self.edit_note.toPlainText().strip()

        full_name = f"{name}" + (f" ({abbr})" if abbr else "")
        add_tracked(full_name, deadline, note)

        if self.chk_auto.isChecked():
            self._sync_latest(1)

        self.edit_name.clear()
        self.edit_abbr.clear()
        self.edit_note.clear()
        self._refresh_tracked()
        QMessageBox.information(self, "已添加", f"已添加 {full_name} ✅")

    def _remove_selected(self):
        rows = set()
        for idx in self.table_tracked.selectedIndexes():
            rows.add(idx.row())
        if not rows:
            return
        for row in sorted(rows, reverse=True):
            remove_tracked(row)
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
            ok1 = add_calendar_event(
                item["name"],
                d,
                item.get("note", ""),
                calendar_name=cal,
                alert_days_before=alert_days,
            )
            ok2 = add_reminder(
                f"截稿: {item['name']}",
                d - timedelta(days=alert_days),
                f"距离 {item['name']} 截稿还有 {alert_days} 天",
                list_name=rem,
            )
            if ok1 and ok2:
                mark_synced(i)
                success += 1

        self._refresh_tracked()
        QMessageBox.information(
            self,
            "同步完成",
            f"已同步 {success}/{len(to_sync)} 个会议到日历和提醒事项 ✅\n\n"
            f"日历: {cal}\n提醒列表: {rem}\n提前: {alert_days} 天",
        )

    def _sync_latest(self, count: int):
        """自动同步最近添加的 N 条"""
        self.config = load_config()
        tracked = self.config.get("tracked", [])
        cal = self.combo_calendar.currentText()
        rem = self.combo_reminders.currentText()
        alert_days = self.spin_alert.value()

        for item in tracked[-count:]:
            d = datetime.strptime(item["deadline"], "%Y-%m-%d").date()
            add_calendar_event(
                item["name"],
                d,
                item.get("note", ""),
                calendar_name=cal,
                alert_days_before=alert_days,
            )
            add_reminder(
                f"截稿: {item['name']}",
                d - timedelta(days=alert_days),
                f"距离 {item['name']} 截稿还有 {alert_days} 天",
                list_name=rem,
            )
            item["synced"] = True

        save_config(self.config)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DeadlineTracker")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
