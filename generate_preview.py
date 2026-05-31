"""生成 UI 预览图"""
import sys
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPainterPath, QLinearGradient, QPen, QBrush, QImage
from PyQt6.QtWidgets import QApplication

def generate_preview():
    app = QApplication(sys.argv)
    
    # 创建图片
    w, h = 960, 640
    img = QImage(w, h, QImage.Format.Format_ARGB32)
    img.fill(QColor("#f5f5f7"))
    
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # ─── 侧边栏 ───
    sidebar_rect = QRectF(0, 0, 200, h)
    painter.setBrush(QColor(255, 255, 255, 184))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(sidebar_rect, 0, 0)
    
    # 侧边栏分割线
    painter.setPen(QPen(QColor(0, 0, 0, 15), 1))
    painter.drawLine(200, 0, 200, h)
    
    # App 标题
    title_font = QFont("SF Pro Display", 18)
    title_font.setBold(True)
    painter.setFont(title_font)
    painter.setPen(QColor("#1d1d1f"))
    painter.drawText(QRectF(16, 20, 180, 30), Qt.AlignmentFlag.AlignLeft, "📅 Deadline")
    
    # 侧边栏按钮
    sidebar_items = [
        ("📋  已追踪", True),
        ("🔍  会议库", False),
        ("➕  添加会议", False),
        ("⚙️  设置", False),
    ]
    
    btn_font = QFont("SF Pro Text", 13)
    painter.setFont(btn_font)
    
    for i, (text, selected) in enumerate(sidebar_items):
        y = 68 + i * 40
        if selected:
            # 选中状态背景
            painter.setBrush(QColor(0, 122, 255, 31))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(12, y, 176, 36), 8, 8)
            painter.setPen(QColor("#007aff"))
            font = QFont("SF Pro Text", 13)
            font.setBold(True)
            painter.setFont(font)
        else:
            painter.setPen(QColor("#1d1d1f"))
            painter.setFont(QFont("SF Pro Text", 13))
        
        painter.drawText(QRectF(24, y, 160, 36), Qt.AlignmentFlag.AlignVCenter, text)
    
    # 版本号
    painter.setPen(QColor("#86868b"))
    painter.setFont(QFont("SF Pro Text", 11))
    painter.drawText(QRectF(16, h - 40, 180, 20), Qt.AlignmentFlag.AlignLeft, "v1.1")
    
    # ─── 内容区 ───
    content_x = 224
    
    # 页面标题
    title_font = QFont("SF Pro Display", 22)
    title_font.setBold(True)
    painter.setFont(title_font)
    painter.setPen(QColor("#1d1d1f"))
    painter.drawText(QRectF(content_x, 20, 300, 30), Qt.AlignmentFlag.AlignLeft, "已追踪的会议")
    
    # ─── 统计卡片 ───
    cards = [
        ("追踪中", "3", "#007aff"),
        ("紧急", "1", "#ff3b30"),
        ("已同步", "0", "#34c759"),
    ]
    
    for i, (label, value, color) in enumerate(cards):
        x = content_x + i * 152
        y = 68
        card_rect = QRectF(x, y, 140, 80)
        
        # 卡片背景
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor(0, 0, 0, 15), 1))
        painter.drawRoundedRect(card_rect, 12, 12)
        
        # 数值
        val_font = QFont("SF Pro Display", 28)
        val_font.setBold(True)
        painter.setFont(val_font)
        painter.setPen(QColor(color))
        painter.drawText(QRectF(x + 16, y + 12, 110, 35), Qt.AlignmentFlag.AlignLeft, value)
        
        # 标签
        painter.setFont(QFont("SF Pro Text", 11))
        painter.setPen(QColor("#86868b"))
        painter.drawText(QRectF(x + 16, y + 50, 110, 20), Qt.AlignmentFlag.AlignLeft, label)
    
    # ─── 按钮栏 ───
    btn_y = 168
    
    # 同步按钮
    sync_rect = QRectF(content_x, btn_y, 140, 36)
    painter.setBrush(QColor("#007aff"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(sync_rect, 8, 8)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("SF Pro Text", 13))
    painter.drawText(sync_rect, Qt.AlignmentFlag.AlignCenter, "☁️  同步到日历")
    
    # 移除按钮
    remove_rect = QRectF(content_x + 152, btn_y, 100, 36)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(QColor("#ff3b30"), 1))
    painter.drawRoundedRect(remove_rect, 8, 8)
    painter.setPen(QColor("#ff3b30"))
    painter.drawText(remove_rect, Qt.AlignmentFlag.AlignCenter, "移除选中")
    
    # ─── 截稿日期列表 ───
    items = [
        ("NeurIPS 2026 — Abstract", "2026-05-22", 21, "red"),
        ("NeurIPS 2026 — Full paper", "2026-05-29", 28, "orange"),
        ("ICML 2026 — Main conference", "2026-01-31", -121, "red"),
    ]
    
    list_y = 224
    
    for i, (name, deadline, days, urgency) in enumerate(items):
        y = list_y + i * 64
        item_rect = QRectF(content_x, y, 520, 56)
        
        # 卡片背景
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor(0, 0, 0, 15), 1))
        painter.drawRoundedRect(item_rect, 10, 10)
        
        # 状态点
        if days <= 7:
            dot_color = QColor("#ff3b30")
            urgency_text = "紧急"
        elif days <= 14:
            dot_color = QColor("#ff9500")
            urgency_text = f"{days}天"
        elif days <= 30:
            dot_color = QColor("#ffcc00")
            urgency_text = f"{days}天"
        else:
            dot_color = QColor("#34c759")
            urgency_text = f"{days}天"
        
        if days < 0:
            dot_color = QColor("#ff3b30")
            urgency_text = f"已过期"
        
        painter.setBrush(dot_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(content_x + 22, y + 28), 4, 4)
        
        # 会议名
        painter.setPen(QColor("#1d1d1f"))
        painter.setFont(QFont("SF Pro Text", 13))
        painter.drawText(QRectF(content_x + 36, y + 8, 280, 20), Qt.AlignmentFlag.AlignLeft, name)
        
        # 倒计时
        painter.setPen(dot_color)
        font = QFont("SF Pro Text", 13)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(content_x + 36, y + 30, 60, 16), Qt.AlignmentFlag.AlignLeft, urgency_text)
        
        # 截稿日期
        painter.setPen(QColor("#86868b"))
        painter.setFont(QFont("SF Pro Text", 12))
        painter.drawText(QRectF(content_x + 340, y + 8, 100, 20), Qt.AlignmentFlag.AlignLeft, deadline)
        
        # 同步状态
        painter.setPen(QColor("#86868b"))
        painter.setFont(QFont("SF Pro Text", 14))
        painter.drawText(QRectF(content_x + 460, y + 8, 40, 20), Qt.AlignmentFlag.AlignCenter, "○")
    
    painter.end()
    
    # 保存
    img.save("/tmp/deadline_tracker_preview.png", "PNG")
    print("预览图已保存到 /tmp/deadline_tracker_preview.png")

if __name__ == "__main__":
    generate_preview()
