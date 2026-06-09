#!/usr/bin/env python3
"""Build script that writes the complete ui.py with all 15 features."""
import os

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.py")

# ─── PART 1: IMPORTS, CONSTANTS, THEMES, KEYBOARD LAYOUT ───
PART1 = r'''import os
import sys
import json
import math
import logging
import queue
import webbrowser
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QCheckBox,
    QTabBar, QFrame, QScrollArea, QLineEdit, QDialog, QGraphicsOpacityEffect,
    QMessageBox, QFileDialog, QSizePolicy, QStackedWidget, QButtonGroup
)
from PyQt6.QtCore import (
    Qt, QTimer, QRectF, QPointF, pyqtSignal, QObject, QSize,
    QTime, QPropertyAnimation, QAbstractAnimation, pyqtSlot, QMetaObject, Q_ARG
)
from PyQt6.QtGui import (
    QColor, QPainter, QFont, QFontDatabase, QPen, QBrush,
    QLinearGradient, QIcon, QPixmap, QPainterPath, QFontMetrics,
    QMouseEvent
)

import utils

APP_VERSION = "2.0.0"
APP_GITHUB = "https://github.com/nickguti/TypeTrace"

BG_MAIN = "#0B0C10"
BG_CARD = "#171A23"
BG_CARD_INNER = "#111318"
BORDER_COLOR = "#2F313D"
BORDER_INNER = "#1D1F2A"
ACCENT = "#00F5D4"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#8E9297"

KEYCAP_BASE = "#20222B"
KEYCAP_HOVER = "#2F313D"
DANGER = "#A63A50"
DANGER_HOVER = "#C93B55"

FONT_FAMILY = "Inter"

GLOBAL_QSS = """
QMainWindow, QWidget { background-color: #0B0C10; color: #FFFFFF; font-family: "Inter", "Segoe UI", "SF Pro Display", sans-serif; font-size: 13px; }
QTabBar::tab { background: #0B0C10; color: #8E9297; padding: 8px 18px; border: none; font-size: 13px; font-weight: 400; }
QTabBar::tab:selected { color: #FFFFFF; border-bottom: 2px solid #00F5D4; background: #171A23; }
QTabBar::tab:hover:!selected { color: #FFFFFF; background: #13151C; }
QTabWidget::pane { border: 1px solid #2F313D; background: #171A23; }
QPushButton { background: transparent; border: 1px solid #2F313D; color: #8E9297; padding: 6px 14px; border-radius: 4px; font-size: 13px; font-weight: 500; }
QPushButton:hover { border-color: #00F5D4; color: #FFFFFF; }
QPushButton:pressed { background: rgba(0,245,212,0.1); }
QLabel { color: #FFFFFF; font-size: 13px; }
QComboBox { background: #171A23; border: 1px solid #2F313D; color: #FFFFFF; padding: 4px 8px; border-radius: 4px; font-size: 13px; }
QComboBox:hover { border-color: #00F5D4; }
QScrollBar:vertical { background: #0B0C10; width: 6px; }
QScrollBar::handle:vertical { background: #2F313D; border-radius: 3px; }
QScrollBar::handle:vertical:hover { background: #00F5D4; }
QCheckBox { color: #8E9297; font-size: 13px; spacing: 8px; min-height: 32px; }
QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #2F313D; border-radius: 4px; background: #171A23; }
QCheckBox::indicator:checked { background: #00F5D4; border-color: #00F5D4; image: none; }
QLineEdit { background: #171A23; border: 1px solid #2F313D; color: #FFFFFF; padding: 4px 8px; border-radius: 4px; font-size: 13px; }
"""

def hex_to_qcolor(hex_str):
    hex_str = hex_str.lstrip('#')
    return QColor(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

KEYBOARD_THEMES = {
    "Classic Heatmap": [
        (0.00, QColor("#171A23")),
        (0.25, QColor("#0F4C75")),
        (0.50, QColor("#1B7F4F")),
        (0.75, QColor("#D4A017")),
        (1.00, QColor("#C0392B")),
    ],
    "Neon": [
        (0.00, QColor("#0D0D0D")),
        (0.30, QColor("#7B2FBE")),
        (0.65, QColor("#00F5D4")),
        (1.00, QColor("#FFFFFF")),
    ],
    "Monochrome": [
        (0.00, QColor("#171A23")),
        (1.00, QColor("#FFFFFF")),
    ],
    "Ice Blue": [
        (0.00, QColor("#0B0C10")),
        (0.30, QColor("#0A2A4A")),
        (0.65, QColor("#0077B6")),
        (1.00, QColor("#90E0EF")),
    ],
    "Sunset": [
        (0.00, QColor("#1A0A00")),
        (0.30, QColor("#7B2D00")),
        (0.60, QColor("#E05C00")),
        (0.85, QColor("#FFB347")),
        (1.00, QColor("#FFF0A0")),
    ],
}

def interpolate_color_ramp(val, ramp):
    val = max(0.0, min(1.0, val))
    if val <= ramp[0][0]:
        return QColor(ramp[0][1])
    if val >= ramp[-1][0]:
        return QColor(ramp[-1][1])
    for i in range(len(ramp) - 1):
        t1, c1 = ramp[i]
        t2, c2 = ramp[i + 1]
        if t1 <= val <= t2:
            span = t2 - t1
            if span == 0:
                return QColor(c1)
            ratio = (val - t1) / span
            r = int(c1.red() + (c2.red() - c1.red()) * ratio)
            g = int(c1.green() + (c2.green() - c1.green()) * ratio)
            b = int(c1.blue() + (c2.blue() - c1.blue()) * ratio)
            return QColor(r, g, b)
    return QColor(ramp[-1][1])

'''

# ─── KEYBOARD LAYOUT ───
KEYBOARD_LAYOUT_STR = '''KEYBOARD_LAYOUT = [
    {"id": "Esc", "label": "Esc", "rx": 0.0, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F1", "label": "F1", "rx": 0.0833, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F2", "label": "F2", "rx": 0.125, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F3", "label": "F3", "rx": 0.1667, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F4", "label": "F4", "rx": 0.2083, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F5", "label": "F5", "rx": 0.2708, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F6", "label": "F6", "rx": 0.3125, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F7", "label": "F7", "rx": 0.3542, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F8", "label": "F8", "rx": 0.3958, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F9", "label": "F9", "rx": 0.4583, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F10", "label": "F10", "rx": 0.5, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F11", "label": "F11", "rx": 0.5417, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "F12", "label": "F12", "rx": 0.5833, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "Print_screen", "label": "PrtSc", "rx": 0.6458, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "Scroll_lock", "label": "ScrLk", "rx": 0.6875, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "Pause", "label": "Pause", "rx": 0.7292, "ry": 0.0, "rw": 0.0417, "rh": 0.155},
    {"id": "`", "label": "`", "rx": 0.0, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "1", "label": "1", "rx": 0.0417, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "2", "label": "2", "rx": 0.0833, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "3", "label": "3", "rx": 0.125, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "4", "label": "4", "rx": 0.1667, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "5", "label": "5", "rx": 0.2083, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "6", "label": "6", "rx": 0.25, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "7", "label": "7", "rx": 0.2917, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "8", "label": "8", "rx": 0.3333, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "9", "label": "9", "rx": 0.375, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "0", "label": "0", "rx": 0.4167, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "-", "label": "-", "rx": 0.4583, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "=", "label": "=", "rx": 0.5, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "Backspace", "label": "Bksp", "rx": 0.5417, "ry": 0.17, "rw": 0.0833, "rh": 0.155},
    {"id": "Insert", "label": "Ins", "rx": 0.6458, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "Home", "label": "Home", "rx": 0.6875, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "Page_up", "label": "PgUp", "rx": 0.7292, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "Num_lock", "label": "Num", "rx": 0.7917, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_/", "label": "/", "rx": 0.8333, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_*", "label": "*", "rx": 0.875, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_-", "label": "-", "rx": 0.9167, "ry": 0.17, "rw": 0.0417, "rh": 0.155},
    {"id": "Tab", "label": "Tab", "rx": 0.0, "ry": 0.34, "rw": 0.0625, "rh": 0.155},
    {"id": "Q", "label": "Q", "rx": 0.0625, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "W", "label": "W", "rx": 0.1042, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "E", "label": "E", "rx": 0.1458, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "R", "label": "R", "rx": 0.1875, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "T", "label": "T", "rx": 0.2292, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "Y", "label": "Y", "rx": 0.2708, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "U", "label": "U", "rx": 0.3125, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "I", "label": "I", "rx": 0.3542, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "O", "label": "O", "rx": 0.3958, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "P", "label": "P", "rx": 0.4375, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "[", "label": "[", "rx": 0.4792, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "]", "label": "]", "rx": 0.5208, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "\\\\", "label": "\\\\", "rx": 0.5625, "ry": 0.34, "rw": 0.0625, "rh": 0.155},
    {"id": "Delete", "label": "Del", "rx": 0.6458, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "End", "label": "End", "rx": 0.6875, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "Page_down", "label": "PgDn", "rx": 0.7292, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_7", "label": "7", "rx": 0.7917, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_8", "label": "8", "rx": 0.8333, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_9", "label": "9", "rx": 0.875, "ry": 0.34, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_+", "label": "+", "rx": 0.9167, "ry": 0.34, "rw": 0.0417, "rh": 0.325},
    {"id": "Caps", "label": "Caps", "rx": 0.0, "ry": 0.51, "rw": 0.0729, "rh": 0.155},
    {"id": "A", "label": "A", "rx": 0.0729, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "S", "label": "S", "rx": 0.1146, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "D", "label": "D", "rx": 0.1563, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "F", "label": "F", "rx": 0.1979, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "G", "label": "G", "rx": 0.2396, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "H", "label": "H", "rx": 0.2813, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "J", "label": "J", "rx": 0.3229, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "K", "label": "K", "rx": 0.3646, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "L", "label": "L", "rx": 0.4063, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": ";", "label": ";", "rx": 0.4479, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "'", "label": "'", "rx": 0.4896, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "Enter", "label": "Enter", "rx": 0.5313, "ry": 0.51, "rw": 0.0938, "rh": 0.155},
    {"id": "Kp_4", "label": "4", "rx": 0.7917, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_5", "label": "5", "rx": 0.8333, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_6", "label": "6", "rx": 0.875, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
    {"id": "Shift_L", "label": "Shift", "rx": 0.0, "ry": 0.68, "rw": 0.0938, "rh": 0.155},
    {"id": "Z", "label": "Z", "rx": 0.0938, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "X", "label": "X", "rx": 0.1354, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "C", "label": "C", "rx": 0.1771, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "V", "label": "V", "rx": 0.2188, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "B", "label": "B", "rx": 0.2604, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "N", "label": "N", "rx": 0.3021, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "M", "label": "M", "rx": 0.3438, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": ",", "label": ",", "rx": 0.3854, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": ".", "label": ".", "rx": 0.4271, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "/", "label": "/", "rx": 0.4688, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "Shift_R", "label": "Shift", "rx": 0.5104, "ry": 0.68, "rw": 0.1146, "rh": 0.155},
    {"id": "Up", "label": "\u2191", "rx": 0.6875, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_1", "label": "1", "rx": 0.7917, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_2", "label": "2", "rx": 0.8333, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_3", "label": "3", "rx": 0.875, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_enter", "label": "Ent", "rx": 0.9167, "ry": 0.68, "rw": 0.0417, "rh": 0.325},
    {"id": "Ctrl_L", "label": "Ctrl", "rx": 0.0, "ry": 0.85, "rw": 0.0521, "rh": 0.155},
    {"id": "Win_L", "label": "Win", "rx": 0.0521, "ry": 0.85, "rw": 0.0521, "rh": 0.155},
    {"id": "Alt_L", "label": "Alt", "rx": 0.1042, "ry": 0.85, "rw": 0.0521, "rh": 0.155},
    {"id": "Space", "label": "Space", "rx": 0.1563, "ry": 0.85, "rw": 0.2604, "rh": 0.155},
    {"id": "Alt_R", "label": "Alt", "rx": 0.4167, "ry": 0.85, "rw": 0.0521, "rh": 0.155},
    {"id": "Win_R", "label": "Win", "rx": 0.4688, "ry": 0.85, "rw": 0.0521, "rh": 0.155},
    {"id": "Menu", "label": "Fn", "rx": 0.5208, "ry": 0.85, "rw": 0.0521, "rh": 0.155},
    {"id": "Ctrl_R", "label": "Ctrl", "rx": 0.5729, "ry": 0.85, "rw": 0.0521, "rh": 0.155},
    {"id": "Left", "label": "\u2190", "rx": 0.6458, "ry": 0.85, "rw": 0.0417, "rh": 0.155},
    {"id": "Down", "label": "\u2193", "rx": 0.6875, "ry": 0.85, "rw": 0.0417, "rh": 0.155},
    {"id": "Right", "label": "\u2192", "rx": 0.7292, "ry": 0.85, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_0", "label": "0", "rx": 0.7917, "ry": 0.85, "rw": 0.0833, "rh": 0.155},
    {"id": "Kp_.", "label": ".", "rx": 0.875, "ry": 0.85, "rw": 0.0417, "rh": 0.155},
]

'''

# ─── PART 2: WIDGET CLASSES ───
PART2 = '''class KeyTooltip(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.key_name = ""
        self.press_count = 0
        self.percentage = 0.0
        self.rank_text = ""
        self.resize(160, 95)

    def update_info(self, key_name, count, total, rank_idx):
        self.key_name = key_name
        self.press_count = count
        self.percentage = (count / total * 100) if total > 0 else 0.0
        if count > 0:
            self.rank_text = f"#{rank_idx} most used"
        else:
            self.rank_text = "Not used"
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, 6, 6)
        painter.fillPath(path, hex_to_qcolor(BG_CARD))
        painter.setPen(QPen(hex_to_qcolor(ACCENT), 1.0))
        painter.drawPath(path)
        painter.setPen(hex_to_qcolor(TEXT_PRIMARY))
        font = QFont(FONT_FAMILY, 13, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(12, 12, self.width() - 24, 20), Qt.AlignmentFlag.AlignLeft, self.key_name)
        painter.setPen(hex_to_qcolor(TEXT_SECONDARY))
        font = QFont(FONT_FAMILY, 12)
        painter.setFont(font)
        painter.drawText(QRectF(12, 36, self.width() - 24, 16), Qt.AlignmentFlag.AlignLeft, f"{self.press_count:,} presses")
        painter.drawText(QRectF(12, 52, self.width() - 24, 16), Qt.AlignmentFlag.AlignLeft, f"{self.percentage:.1f}% of total")
        painter.setPen(hex_to_qcolor(ACCENT))
        painter.drawText(QRectF(12, 68, self.width() - 24, 16), Qt.AlignmentFlag.AlignLeft, self.rank_text)


class HeaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.displayed_apm = 0.0
        self.target_apm = 0
        self.displayed_wpm = 0.0
        self.target_wpm = 0
        self.is_tracking = True
        self.is_incognito = False
        self.help_btn = QPushButton("?", self)
        self.help_btn.setFixedSize(20, 20)
        self.help_btn.setStyleSheet(f"QPushButton {{ background: {BG_CARD}; border: 1px solid {BORDER_COLOR}; color: {TEXT_SECONDARY}; border-radius: 10px; padding: 0px; font-size: 11px; font-weight: bold; }} QPushButton:hover {{ background: {BORDER_COLOR}; color: {TEXT_PRIMARY}; border-color: {ACCENT}; }}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.help_btn.move(self.width() - 30, 14)

    def update_stats(self, apm, wpm, is_tracking):
        self.target_apm = apm
        self.target_wpm = wpm
        self.is_tracking = is_tracking

    def on_anim_tick(self):
        if abs(self.displayed_apm - self.target_apm) < 0.5:
            self.displayed_apm = float(self.target_apm)
        else:
            self.displayed_apm += (self.target_apm - self.displayed_apm) * 0.18
        if abs(self.displayed_wpm - self.target_wpm) < 0.5:
            self.displayed_wpm = float(self.target_wpm)
        else:
            self.displayed_wpm += (self.target_wpm - self.displayed_wpm) * 0.18

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), hex_to_qcolor(BG_MAIN))
        painter.setPen(QPen(hex_to_qcolor(BORDER_COLOR), 1.0))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(hex_to_qcolor(ACCENT)))
        painter.drawRoundedRect(QRectF(15, 10, 28, 28), 6, 6)
        painter.setPen(hex_to_qcolor(BG_MAIN))
        font = QFont(FONT_FAMILY, 13, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(15, 10, 28, 28), Qt.AlignmentFlag.AlignCenter, "TT")
        painter.setPen(hex_to_qcolor(TEXT_PRIMARY))
        font = QFont(FONT_FAMILY, 14, QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(QRectF(55, 8, 200, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "TYPETRACE")
        painter.setPen(hex_to_qcolor(TEXT_SECONDARY))
        font = QFont(FONT_FAMILY, 10)
        painter.setFont(font)
        painter.drawText(QRectF(55, 26, 300, 14), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "PRIVACY-FOCUSED KEYSTROKE ANALYZER")
        cx = self.width() / 2
        painter.setPen(hex_to_qcolor(ACCENT))
        font = QFont(FONT_FAMILY, 22, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(cx - 110, 0, 70, 48), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(round(self.displayed_apm)))
        painter.setPen(hex_to_qcolor(TEXT_SECONDARY))
        font = QFont(FONT_FAMILY, 11)
        painter.setFont(font)
        painter.drawText(QRectF(cx - 35, 0, 30, 48), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "APM")
        painter.setPen(QPen(hex_to_qcolor(BORDER_COLOR), 1.0))
        painter.drawLine(int(cx), 10, int(cx), 38)
        painter.setPen(hex_to_qcolor(ACCENT))
        font = QFont(FONT_FAMILY, 22, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(cx + 10, 0, 70, 48), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(round(self.displayed_wpm)))
        painter.setPen(hex_to_qcolor(TEXT_SECONDARY))
        font = QFont(FONT_FAMILY, 11)
        painter.setFont(font)
        painter.drawText(QRectF(cx + 85, 0, 30, 48), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "WPM")
        if self.is_incognito:
            c = hex_to_qcolor("#FF3B3B")
            painter.setBrush(QBrush(c))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(self.width() - 110, 24), 4, 4)
            painter.setPen(c)
            font = QFont(FONT_FAMILY, 11)
            painter.setFont(font)
            painter.drawText(QRectF(self.width() - 100, 0, 80, 48), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "INCOGNITO")
        else:
            if self.is_tracking:
                elapsed_ms = QTime.currentTime().msecsSinceStartOfDay()
                opacity = 0.7 + 0.3 * math.sin(2 * math.pi * elapsed_ms / 1200)
                c = hex_to_qcolor(ACCENT)
                c.setAlphaF(opacity)
                painter.setBrush(QBrush(c))
            else:
                painter.setBrush(QBrush(hex_to_qcolor(TEXT_SECONDARY)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(self.width() - 110, 24), 4, 4)
            painter.setPen(hex_to_qcolor(TEXT_SECONDARY))
            font = QFont(FONT_FAMILY, 11)
            painter.setFont(font)
            painter.drawText(QRectF(self.width() - 100, 0, 60, 48), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Tracking" if self.is_tracking else "Paused")


class LegendBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.theme = "Classic Heatmap"

    def set_theme(self, name):
        self.theme = name
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        panel_rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(panel_rect, 6, 6)
        painter.fillPath(path, hex_to_qcolor(BG_CARD))
        painter.setPen(QPen(hex_to_qcolor(BORDER_COLOR), 1.0))
        painter.drawPath(path)
        painter.setPen(hex_to_qcolor(TEXT_SECONDARY))
        font = QFont(FONT_FAMILY, 10)
        font.setItalic(True)
        painter.setFont(font)
        painter.drawText(QRectF(8, 4, 40, 16), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Cold")
        painter.drawText(QRectF(self.width() - 48, 4, 40, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "Hot")
        bar_x = 55
        bar_w = self.width() - 110
        bar_y = 8
        bar_h = 10
        ramp = KEYBOARD_THEMES.get(self.theme, KEYBOARD_THEMES["Classic Heatmap"])
        if bar_w > 0:
            grad = QLinearGradient(bar_x, bar_y, bar_x + bar_w, bar_y)
            for t_stop, c_stop in ramp:
                grad.setColorAt(t_stop, c_stop)
            painter.fillRect(QRectF(bar_x, bar_y, bar_w, bar_h), grad)
            painter.setPen(QPen(hex_to_qcolor(BORDER_COLOR), 1.0))
            font.setItalic(False)
            painter.setFont(font)
            for i, val in enumerate([0, 25, 50, 75, 100]):
                tx = bar_x + (bar_w * i / 4)
                painter.drawLine(int(tx), bar_y + bar_h, int(tx), bar_y + bar_h + 4)
                align = Qt.AlignmentFlag.AlignCenter
                w_t = 30
                ox = -15
                if val == 0:
                    align = Qt.AlignmentFlag.AlignLeft
                    ox = 0
                elif val == 100:
                    align = Qt.AlignmentFlag.AlignRight
                    ox = -30
                painter.setPen(hex_to_qcolor(TEXT_SECONDARY))
                painter.drawText(QRectF(tx + ox, bar_y + bar_h + 6, w_t, 14), align | Qt.AlignmentFlag.AlignVCenter, f"{val}%")

'''

# ─── PART 3: KeyboardHeatmapWidget ───
PART3 = '''class KeyboardHeatmapWidget(QWidget):
    ASPECT_RATIO = 3.6

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_colors = {}
        self.target_colors = {}
        self.transition_start = None
        self.ripples = []
        self.key_stats = {}
        self.heatmap_enabled = False
        self.current_theme_name = "Classic Heatmap"
        self._hovered_key_id = None
        self.setMouseTracking(True)
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.flash_overlay_alpha = 0.0
        self.banner_state = None
        self.parent_ui = None
        self.tooltip = KeyTooltip()

    def set_theme(self, name):
        self.current_theme_name = name
        if self.parent_ui and self.heatmap_enabled:
            self.parent_ui._update_heatmap_colors()
        self.update()

    def _resolve_color(self, normalized_value):
        ramp = KEYBOARD_THEMES.get(self.current_theme_name, KEYBOARD_THEMES["Classic Heatmap"])
        return interpolate_color_ramp(normalized_value, ramp)

    def start_gaming_banner(self, from_profile):
        self.flash_overlay_alpha = 255.0
        self.banner_state = {"start_time": QTime.currentTime(), "from": from_profile}
        self.update()

    def _compute_draw_rect(self):
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return QRectF(0, 0, 0, 0)
        current_ratio = w / h
        if current_ratio > self.ASPECT_RATIO:
            draw_h = h
            draw_w = draw_h * self.ASPECT_RATIO
            offset_x = (w - draw_w) / 2.0
            offset_y = 0.0
        else:
            draw_w = w
            draw_h = draw_w / self.ASPECT_RATIO
            offset_x = 0.0
            offset_y = (h - draw_h) / 2.0
        return QRectF(offset_x, offset_y, draw_w, draw_h)

    def update_colors(self, color_map):
        self.target_colors = color_map
        self.transition_start = QTime.currentTime()

    def add_ripple(self, key_id):
        self.ripples.append({"key_id": key_id, "start_time": QTime.currentTime(), "duration_ms": 300})

    def get_current_key_color(self, key_id):
        base_c = self.current_colors.get(key_id, hex_to_qcolor(KEYCAP_BASE))
        if self.transition_start and key_id in self.target_colors:
            elapsed = self.transition_start.msecsTo(QTime.currentTime())
            if elapsed >= 400:
                return self.target_colors[key_id]
            else:
                t = elapsed / 400.0
                target_c = self.target_colors[key_id]
                r = int(base_c.red() + (target_c.red() - base_c.red()) * t)
                g = int(base_c.green() + (target_c.green() - base_c.green()) * t)
                b = int(base_c.blue() + (target_c.blue() - base_c.blue()) * t)
                return QColor(r, g, b)
        return base_c

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), hex_to_qcolor(BG_CARD_INNER))
        draw_rect = self._compute_draw_rect()
        if draw_rect.width() < 50 or draw_rect.height() < 20:
            painter.end()
            return
        font_size = max(7, int(draw_rect.height() / 25))
        font = QFont(FONT_FAMILY, font_size)
        font.setBold(True)
        painter.setFont(font)
        border_pen = QPen(hex_to_qcolor(BORDER_COLOR), 1.0)
        hover_pen = QPen(hex_to_qcolor(ACCENT), 2.0)
        now = QTime.currentTime()
        active_ripples = {}
        kept_ripples = []
        for r in self.ripples:
            elapsed = r["start_time"].msecsTo(now)
            if elapsed < r["duration_ms"]:
                t = elapsed / r["duration_ms"]
                alpha = 1.0 - t
                kid = r["key_id"]
                if kid not in active_ripples or alpha > active_ripples[kid]:
                    active_ripples[kid] = alpha
                kept_ripples.append(r)
        self.ripples = kept_ripples
        if self.transition_start and self.transition_start.msecsTo(now) >= 400:
            self.current_colors = self.target_colors.copy()
            self.transition_start = None
        for key in KEYBOARD_LAYOUT:
            key_id = key["id"]
            px = draw_rect.x() + key["rx"] * draw_rect.width()
            py = draw_rect.y() + key["ry"] * draw_rect.height()
            pw = key["rw"] * draw_rect.width()
            ph = key["rh"] * draw_rect.height()
            key_rect = QRectF(px + 1.5, py + 1.5, pw - 3, ph - 3)
            radius = ph * 0.15
            base_color = self.get_current_key_color(key_id)
            if key_id in active_ripples:
                alpha = active_ripples[key_id]
                accent = hex_to_qcolor(ACCENT)
                r_c = int(base_color.red() * (1 - alpha) + accent.red() * alpha)
                g_c = int(base_color.green() * (1 - alpha) + accent.green() * alpha)
                b_c = int(base_color.blue() * (1 - alpha) + accent.blue() * alpha)
                fill_color = QColor(r_c, g_c, b_c)
            else:
                fill_color = base_color
                if key_id == self._hovered_key_id and not self.heatmap_enabled:
                    fill_color = hex_to_qcolor(KEYCAP_HOVER)
            shadow_rect = QRectF(key_rect.x(), key_rect.y() + ph * 0.08, key_rect.width(), key_rect.height())
            painter.setBrush(QBrush(QColor(0, 0, 0, 153)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(shadow_rect, radius, radius)
            painter.setBrush(QBrush(fill_color))
            if key_id == self._hovered_key_id:
                painter.setPen(hover_pen)
            else:
                painter.setPen(border_pen)
            painter.drawRoundedRect(key_rect, radius, radius)
            hl_rect = QRectF(key_rect.x() + 1, key_rect.y() + 1, key_rect.width() - 2, ph * 0.25)
            painter.setBrush(QBrush(QColor(255, 255, 255, 20)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(hl_rect, radius - 1, radius - 1)
            if self.heatmap_enabled and key_id in self.current_colors:
                c = self.current_colors[key_id]
                lum = 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()
                text_color = hex_to_qcolor(BG_MAIN) if lum > 128 else hex_to_qcolor(TEXT_PRIMARY)
            else:
                text_color = hex_to_qcolor(TEXT_SECONDARY)
            if key_id in active_ripples:
                text_color = hex_to_qcolor(TEXT_PRIMARY)
            painter.setPen(text_color)
            painter.drawText(key_rect, Qt.AlignmentFlag.AlignCenter, key["label"])
        if self.flash_overlay_alpha > 0:
            painter.fillRect(self.rect(), QColor(0, 245, 212, int(self.flash_overlay_alpha)))
            self.flash_overlay_alpha -= 255.0 * (16.0 / 200.0)
            if self.flash_overlay_alpha < 0:
                self.flash_overlay_alpha = 0
        if self.banner_state:
            elapsed = self.banner_state["start_time"].msecsTo(now)
            if elapsed < 1200:
                if elapsed < 150:
                    alpha_factor = elapsed / 150.0
                elif elapsed > 1050:
                    alpha_factor = (1200 - elapsed) / 150.0
                else:
                    alpha_factor = 1.0
                banner_w = 300
                banner_h = 70
                bx = (self.width() - banner_w) / 2
                by = (self.height() - banner_h) / 2
                bg_c = hex_to_qcolor("#171A23")
                bg_c.setAlphaF(0.92 * alpha_factor)
                brd_c = hex_to_qcolor(ACCENT)
                brd_c.setAlphaF(alpha_factor)
                path = QPainterPath()
                path.addRoundedRect(QRectF(bx, by, banner_w, banner_h), banner_h / 2, banner_h / 2)
                painter.fillPath(path, bg_c)
                painter.setPen(QPen(brd_c, 1.0))
                painter.drawPath(path)
                painter.setBrush(QBrush(brd_c))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRectF(bx + 25, by + 25, 12, 20), 6, 6)
                painter.drawRoundedRect(QRectF(bx + 45, by + 25, 12, 20), 6, 6)
                painter.drawRoundedRect(QRectF(bx + 30, by + 30, 22, 10), 2, 2)
                painter.setPen(brd_c)
                font = QFont(FONT_FAMILY, 22, QFont.Weight.Bold)
                painter.setFont(font)
                painter.drawText(QRectF(bx + 70, by + 10, 200, 30), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "GAMING MODE")
                t2c = hex_to_qcolor(TEXT_SECONDARY)
                t2c.setAlphaF(alpha_factor)
                painter.setPen(t2c)
                font = QFont(FONT_FAMILY, 13)
                painter.setFont(font)
                from_name = self.banner_state["from"]
                painter.drawText(QRectF(bx + 70, by + 40, 200, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"Auto-switched from {from_name}")
            else:
                self.banner_state = None
        painter.end()

    def mouseMoveEvent(self, event):
        pos = event.position()
        draw_rect = self._compute_draw_rect()
        found_key = None
        for key in KEYBOARD_LAYOUT:
            px = draw_rect.x() + key["rx"] * draw_rect.width()
            py = draw_rect.y() + key["ry"] * draw_rect.height()
            pw = key["rw"] * draw_rect.width()
            ph = key["rh"] * draw_rect.height()
            key_rect = QRectF(px, py, pw, ph)
            if key_rect.contains(pos):
                found_key = key
                break
        if found_key:
            key_id = found_key["id"]
            if self._hovered_key_id != key_id:
                self._hovered_key_id = key_id
            count = self.key_stats.get(key_id, 0)
            total = sum(self.key_stats.values())
            sorted_keys = sorted(self.key_stats.items(), key=lambda x: x[1], reverse=True)
            rank_idx = -1
            for i, (k, c) in enumerate(sorted_keys):
                if k == key_id:
                    rank_idx = i + 1
                    break
            self.tooltip.update_info(found_key["label"], count, total, rank_idx)
            cursor_pos = event.globalPosition().toPoint()
            tt_x = cursor_pos.x() + 12
            tt_y = cursor_pos.y() + 12
            screen_geo = QApplication.primaryScreen().geometry()
            if tt_x + self.tooltip.width() > screen_geo.right():
                tt_x = cursor_pos.x() - self.tooltip.width() - 12
            if tt_y + self.tooltip.height() > screen_geo.bottom():
                tt_y = cursor_pos.y() - self.tooltip.height() - 12
            self.tooltip.move(tt_x, tt_y)
            self.tooltip.show()
        else:
            if self._hovered_key_id is not None:
                self._hovered_key_id = None
            self.tooltip.hide()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        if self._hovered_key_id is not None:
            self._hovered_key_id = None
        self.tooltip.hide()
        super().leaveEvent(event)

'''

# ─── PART 4: HourlyChart, MiniCard, IncognitoOverlay ───
PART4 = '''class HourlyChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hourly_data = {}
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, hourly_data):
        self.hourly_data = hourly_data

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), hex_to_qcolor(BG_CARD))
        w = self.width()
        h = self.height()
        if w < 50 or h < 30:
            painter.end()
            return
        hours_values = [0] * 24
        for hour_str, hour_stats in self.hourly_data.items():
            try:
                hour_part = int(hour_str.split("T")[1].split(":")[0])
                hours_values[hour_part] += sum(hour_stats.get("keys", {}).values())
            except Exception:
                pass
        max_val = max(hours_values) if hours_values else 0
        if max_val == 0:
            font = QFont(FONT_FAMILY, 13)
            painter.setFont(font)
            painter.setPen(hex_to_qcolor(TEXT_SECONDARY))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No productivity logs recorded yet.")
            painter.end()
            return
        padding_x = 35
        padding_y = 25
        chart_w = w - padding_x * 2
        chart_h = h - padding_y * 2
        grid_pen = QPen(hex_to_qcolor(BORDER_COLOR), 1.0)
        painter.setPen(grid_pen)
        for i in range(1, 4):
            y = h - padding_y - (chart_h * i / 4)
            painter.drawLine(int(padding_x), int(y), int(w - padding_x), int(y))
        painter.drawLine(int(padding_x), int(h - padding_y), int(w - padding_x), int(h - padding_y))
        bar_total_w = chart_w / 24.0
        bar_w = max(3, bar_total_w * 0.4)
        accent_c = hex_to_qcolor(ACCENT)
        dark_c = QColor(23, 26, 35)
        for hour in range(24):
            val = hours_values[hour]
            if val == 0:
                continue
            bar_h = (val / max_val) * chart_h
            x0 = padding_x + hour * bar_total_w + (bar_total_w - bar_w) / 2.0
            y_bottom = h - padding_y
            y_top = y_bottom - bar_h
            grad = QLinearGradient(x0, y_top, x0, y_bottom)
            grad.setColorAt(0.0, accent_c)
            grad.setColorAt(1.0, dark_c)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(QRectF(x0, y_top, bar_w, bar_h), 2, 2)
            painter.setBrush(QBrush(accent_c))
            painter.drawEllipse(QPointF(x0 + bar_w / 2, y_top), 3, 3)
        font = QFont(FONT_FAMILY, 12)
        painter.setFont(font)
        painter.setPen(hex_to_qcolor(TEXT_SECONDARY))
        for h_val in [0, 6, 12, 18, 23]:
            x = padding_x + h_val * bar_total_w + bar_total_w / 2
            painter.drawText(QRectF(x - 15, h - padding_y + 4, 30, 16), Qt.AlignmentFlag.AlignCenter, f"{h_val}h")
        painter.end()


class MiniCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 12, 12)
        painter.fillPath(path, hex_to_qcolor(BG_CARD_INNER))
        painter.setPen(QPen(hex_to_qcolor(BORDER_INNER), 1.0))
        painter.drawPath(path)
        painter.end()


class IncognitoOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.alpha_factor = 0.0
        self.pulse_timer = QTimer(self)
        self.pulse_timer.setInterval(16)
        self.pulse_timer.timeout.connect(self._on_pulse)
        self.is_active = False

    def activate(self):
        self.is_active = True
        self.alpha_factor = 1.0
        self.pulse_timer.start()
        self.show()
        self.raise_()

    def deactivate(self):
        self.is_active = False

    def _on_pulse(self):
        if not self.is_active and self.alpha_factor > 0:
            self.alpha_factor -= 16.0 / 300.0
            if self.alpha_factor <= 0:
                self.alpha_factor = 0.0
                self.pulse_timer.stop()
                self.hide()
        self.update()

    def paintEvent(self, event):
        if self.alpha_factor <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        elapsed_ms = QTime.currentTime().msecsSinceStartOfDay()
        pulse = 120 + 80 * math.sin(2 * math.pi * elapsed_ms / 1800)
        c = hex_to_qcolor("#FF3B3B")
        c.setAlpha(int(pulse * self.alpha_factor))
        painter.setPen(QPen(c, 3.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(1.5, 1.5, self.width() - 3, self.height() - 3), 8, 8)

'''

# ─── PART 5: TypeTraceUI class ───
PART5 = '''class TypeTraceUI(QMainWindow):
    _trigger_profile_switch = pyqtSignal(str, str)
    _trigger_incognito = pyqtSignal(bool)

    def __init__(self, db, tracker, shutdown_callback=None):
        self._qt_app = QApplication.instance()
        if self._qt_app is None:
            self._qt_app = QApplication(sys.argv)
        self._qt_app.setStyleSheet(GLOBAL_QSS)
        super().__init__()
        self.db = db
        self.tracker = tracker
        self.shutdown_callback = shutdown_callback
        self.overlay = None
        self.heatmap_enabled = False
        self.viewing_profile = self.tracker.active_profile
        self.incognito_active = False
        self.setWindowTitle("TypeTrace \\u2014 Keystroke Analytics")
        self.resize(1500, 820)
        self.setMinimumSize(1000, 600)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.header = HeaderWidget()
        self.header.help_btn.clicked.connect(self._open_about_dialog)
        main_layout.addWidget(self.header)
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(20, 10, 20, 10)
        body_layout.setSpacing(10)
        self.keyboard_widget = KeyboardHeatmapWidget()
        self.keyboard_widget.parent_ui = self
        self.heatmap_legend = LegendBarWidget()
        self.heatmap_legend.setVisible(False)
        kbd_container = QVBoxLayout()
        kbd_container.setSpacing(10)
        kbd_container.addWidget(self.keyboard_widget)
        kbd_container.addWidget(self.heatmap_legend)
        body_layout.addLayout(kbd_container, 3)
        self.tab_bar = QTabBar()
        self.tab_bar.addTab("\\u2699\\ufe0f Configuration")
        self.tab_bar.addTab("\\U0001f4ca Telemetry")
        self.tab_bar.addTab("\\U0001f4c8 Hourly Chart")
        self.tab_bar.currentChanged.connect(self._on_tab_changed)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self._build_config_tab())
        self.stacked_widget.addWidget(self._build_telemetry_tab())
        self.stacked_widget.addWidget(self._build_chart_tab())
        tab_layout = QVBoxLayout()
        tab_layout.setSpacing(0)
        tab_layout.addWidget(self.tab_bar)
        tab_layout.addWidget(self.stacked_widget)
        body_layout.addLayout(tab_layout, 1)
        main_layout.addLayout(body_layout)
        self.incognito_overlay = IncognitoOverlay(central)
        self.incognito_overlay.hide()
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(16)
        self.anim_timer.timeout.connect(self._on_anim_tick)
        self.anim_timer.start()
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._on_background_tick)
        self._update_timer.start(1000)
        self._event_queue = None
        self._queue_timer = QTimer(self)
        self._queue_timer.timeout.connect(self._poll_event_queue)
        self._queue_timer.start(30)
        self._save_timer = QTimer(self)
        self._save_timer.timeout.connect(self._save_data)
        self._save_timer.start(5000)
        self._trigger_profile_switch.connect(self._do_profile_switch_animation)
        self._trigger_incognito.connect(self._do_set_incognito)
        self.update_ui_stats()
        self._update_chip_styles()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'incognito_overlay'):
            self.incognito_overlay.setGeometry(self.centralWidget().rect())

    def _on_anim_tick(self):
        self.header.on_anim_tick()
        self.header.update()
        self.keyboard_widget.update()
        if self.heatmap_enabled:
            self.heatmap_legend.update()
        if self.incognito_active:
            self.incognito_overlay.update()

    def _on_tab_changed(self, index):
        self.stacked_widget.setCurrentIndex(index)
        widget = self.stacked_widget.currentWidget()
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        self.tab_anim = QPropertyAnimation(effect, b"opacity")
        self.tab_anim.setDuration(150)
        self.tab_anim.setStartValue(0.0)
        self.tab_anim.setEndValue(1.0)
        self.tab_anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def _make_section_label(self, text):
        spaced = "  ".join(text.upper())
        lbl = QLabel(spaced)
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent; margin-bottom: 4px;")
        return lbl

    def _build_config_tab(self):
        tab = QWidget()
        tab.setStyleSheet(f"background-color: {BG_CARD};")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        layout.addWidget(self._make_section_label("Select Profile"))
        profile_row = QHBoxLayout()
        profile_row.setSpacing(6)
        profile_row.setContentsMargins(0, 0, 0, 0)
        self.profile_btn_group = QButtonGroup(self)
        self.profile_btn_group.setExclusive(True)
        self.chips = {}
        for name, icon in [("Total", "\\U0001f310"), ("Desktop", "\\U0001f5a5\\ufe0f"), ("Gaming", "\\U0001f3ae")]:
            btn = QPushButton(f"{icon} {name}")
            btn.setFixedHeight(28)
            btn.setMinimumWidth(max(60, len(name) * 9 + 20))
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name: self._on_profile_chip_clicked(n))
            self.profile_btn_group.addButton(btn)
            profile_row.addWidget(btn)
            self.chips[name] = btn
        self.profile_combobox = QComboBox()
        self.profile_combobox.addItems(self._get_custom_profiles())
        self.profile_combobox.setPlaceholderText("custom \\u25be")
        self.profile_combobox.setCurrentIndex(-1)
        self.profile_combobox.currentTextChanged.connect(self._on_custom_profile_selected)
        profile_row.addWidget(self.profile_combobox)
        add_btn = QPushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.clicked.connect(self._create_profile_dialog)
        profile_row.addWidget(add_btn)
        self.del_profile_btn = QPushButton("\\U0001f5d1")
        self.del_profile_btn.setFixedSize(28, 28)
        self.del_profile_btn.setStyleSheet("background: #A63A50; color: #FFFFFF; border: none;")
        self.del_profile_btn.clicked.connect(self._delete_active_profile)
        self.del_profile_btn.setVisible(False)
        profile_row.addWidget(self.del_profile_btn)
        profile_row.addStretch()
        layout.addLayout(profile_row)
        grid = QGridLayout()
        grid.setSpacing(8)
        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        left_col.addWidget(self._make_section_label("Keyboard Theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(KEYBOARD_THEMES.keys()))
        self.theme_combo.setCurrentText("Classic Heatmap")
        self.theme_combo.currentTextChanged.connect(self._change_keyboard_theme)
        left_col.addWidget(self.theme_combo)
        left_col.addStretch()
        grid.addLayout(left_col, 0, 0)
        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        self.heatmap_check = QCheckBox("\\U0001f525 Heatmap View")
        self.heatmap_check.stateChanged.connect(self._toggle_heatmap)
        right_col.addWidget(self.heatmap_check)
        self.incognito_check = QCheckBox("\\U0001f575\\ufe0f Incognito Mode")
        self.incognito_check.setChecked(self.tracker.incognito_mode)
        self.incognito_check.stateChanged.connect(self._toggle_incognito)
        right_col.addWidget(self.incognito_check)
        self.overlay_check = QCheckBox("\\U0001f4fa Floating Widget")
        self.overlay_check.setChecked(self.db.get_overlay_enabled())
        self.overlay_check.stateChanged.connect(self._toggle_overlay)
        right_col.addWidget(self.overlay_check)
        self.startup_check = QCheckBox("\\U0001f4bb Boot Startup")
        self.startup_check.setChecked(utils.is_startup_enabled())
        self.startup_check.stateChanged.connect(self._toggle_startup)
        right_col.addWidget(self.startup_check)
        right_col.addStretch()
        grid.addLayout(right_col, 0, 1)
        layout.addLayout(grid)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        auto_btn = QPushButton("\\U0001f504 Auto-Switch")
        auto_btn.setFixedHeight(40)
        auto_btn.setMinimumWidth(120)
        auto_btn.clicked.connect(self._open_mappings_dialog)
        btn_row.addWidget(auto_btn)
        csv_btn = QPushButton("\\U0001f4c4 CSV Export")
        csv_btn.setFixedHeight(40)
        csv_btn.setMinimumWidth(120)
        csv_btn.clicked.connect(self._export_csv)
        btn_row.addWidget(csv_btn)
        json_btn = QPushButton("{ } JSON Export")
        json_btn.setFixedHeight(40)
        json_btn.setMinimumWidth(120)
        json_btn.clicked.connect(self._export_json)
        btn_row.addWidget(json_btn)
        reset_btn = QPushButton("\\u26a0 Reset")
        reset_btn.setFixedHeight(40)
        reset_btn.setMinimumWidth(120)
        reset_btn.setStyleSheet("background: transparent; color: #A63A50; border: 1px solid #A63A50; font-size: 14px; font-weight: 500;")
        reset_btn.clicked.connect(self._reset_statistics_dialog)
        btn_row.addWidget(reset_btn)
        layout.addLayout(btn_row)
        layout.addStretch()
        return tab

    def _build_telemetry_tab(self):
        tab = QWidget()
        tab.setStyleSheet(f"background-color: {BG_CARD};")
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)
        session_card = MiniCard()
        sc_layout = QVBoxLayout(session_card)
        sc_layout.setContentsMargins(12, 10, 12, 10)
        sc_layout.setSpacing(2)
        sc_title = QLabel("SESSION")
        sc_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: bold; background: transparent;")
        sc_layout.addWidget(sc_title)
        self.session_time_lbl = QLabel("00:00:00")
        self.session_time_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold; background: transparent;")
        sc_layout.addWidget(self.session_time_lbl)
        self.session_keys_lbl = QLabel("Keys: 0")
        self.session_keys_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        sc_layout.addWidget(self.session_keys_lbl)
        self.error_ratio_lbl = QLabel("\\u232b Ratio: 0.0%")
        self.error_ratio_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        sc_layout.addWidget(self.error_ratio_lbl)
        sc_layout.addStretch()
        layout.addWidget(session_card)
        leader_card = MiniCard()
        lc_layout = QVBoxLayout(leader_card)
        lc_layout.setContentsMargins(12, 10, 12, 10)
        lc_layout.setSpacing(2)
        lc_title = QLabel("TOP KEYS")
        lc_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: bold; background: transparent;")
        lc_layout.addWidget(lc_title)
        self.top_keys_labels = []
        for i in range(3):
            lbl = QLabel(f"{i+1}. \\u2014")
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-family: Consolas; font-weight: bold; background: transparent;")
            lc_layout.addWidget(lbl)
            self.top_keys_labels.append(lbl)
        combo_title = QLabel("TOP COMBOS")
        combo_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: bold; background: transparent;")
        lc_layout.addWidget(combo_title)
        self.top_combos_labels = []
        for i in range(2):
            lbl = QLabel(f"{i+1}. \\u2014")
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-family: Consolas; font-weight: bold; background: transparent;")
            lc_layout.addWidget(lbl)
            self.top_combos_labels.append(lbl)
        lc_layout.addStretch()
        layout.addWidget(leader_card)
        burst_card = MiniCard()
        bc_layout = QVBoxLayout(burst_card)
        bc_layout.setContentsMargins(12, 10, 12, 10)
        bc_layout.setSpacing(2)
        bc_title = QLabel("BURSTS")
        bc_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: bold; background: transparent;")
        bc_layout.addWidget(bc_title)
        self.total_bursts_lbl = QLabel("0 recorded")
        self.total_bursts_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold; background: transparent;")
        bc_layout.addWidget(self.total_bursts_lbl)
        records_title = QLabel("RECORDS")
        records_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: bold; background: transparent;")
        bc_layout.addWidget(records_title)
        self.burst_labels = []
        for i in range(3):
            lbl = QLabel(f"{i+1}. \\u2014")
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-family: Consolas; font-weight: bold; background: transparent;")
            bc_layout.addWidget(lbl)
            self.burst_labels.append(lbl)
        bc_layout.addStretch()
        layout.addWidget(burst_card)
        return tab

    def _build_chart_tab(self):
        tab = QWidget()
        tab.setStyleSheet(f"background-color: {BG_CARD};")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 12, 15, 12)
        self.hourly_chart = HourlyChartWidget()
        layout.addWidget(self.hourly_chart)
        return tab

    def _on_background_tick(self):
        try:
            if not self.isVisible():
                return
            self.update_ui_stats()
        except Exception as e:
            logging.exception(f"Error in background update: {e}")

    def _poll_event_queue(self):
        if self._event_queue is None:
            return
        for _ in range(50):
            try:
                event_type, val = self._event_queue.get_nowait()
                self.handle_thread_event(event_type, val)
                self._event_queue.task_done()
            except queue.Empty:
                break

    def _save_data(self):
        try:
            self.db.save_data()
        except Exception:
            pass

    def update_ui_stats(self):
        try:
            apm, wpm = self.tracker.get_apm_wpm()
            is_tracking = not self.incognito_check.isChecked()
            self.header.update_stats(apm, wpm, is_tracking)
            if self.overlay:
                self.overlay.update_stats(apm, wpm)
            session_dur = self.tracker.get_session_duration()
            self.session_time_lbl.setText(session_dur)
            aggregated = self.db.get_aggregated_stats(self.viewing_profile)
            total_keys = sum(aggregated.get("keys", {}).values())
            self.session_keys_lbl.setText(f"Keys: {total_keys}")
            keys_data = aggregated.get("keys", {})
            total_clicks = sum(keys_data.values())
            backspace_clicks = keys_data.get("Backspace", 0) + keys_data.get("Delete", 0)
            ratio = (backspace_clicks / total_clicks) * 100 if total_clicks > 0 else 0.0
            self.error_ratio_lbl.setText(f"\\u232b Ratio: {ratio:.1f}%")
            sorted_keys = sorted(keys_data.items(), key=lambda x: x[1], reverse=True)[:len(self.top_keys_labels)]
            for idx in range(len(self.top_keys_labels)):
                lbl = self.top_keys_labels[idx]
                if idx < len(sorted_keys):
                    k, count = sorted_keys[idx]
                    k_lbl = k
                    if k == "Space":
                        k_lbl = "Space"
                    elif k.startswith("Kp_"):
                        k_lbl = "Num" + k.replace("Kp_", "")
                    lbl.setText(f"{idx+1}. {k_lbl} : {count}")
                else:
                    lbl.setText(f"{idx+1}. \\u2014")
            sorted_combos = sorted(aggregated.get("combinations", {}).items(), key=lambda x: x[1], reverse=True)[:len(self.top_combos_labels)]
            for idx in range(len(self.top_combos_labels)):
                lbl = self.top_combos_labels[idx]
                if idx < len(sorted_combos):
                    combo, count = sorted_combos[idx]
                    lbl.setText(f"{idx+1}. {combo} : {count}")
                else:
                    lbl.setText(f"{idx+1}. \\u2014")
            bursts = self.db.get_burst_records(self.viewing_profile)
            self.total_bursts_lbl.setText(f"{len(bursts)} recorded")
            for idx in range(len(self.burst_labels)):
                lbl = self.burst_labels[idx]
                if idx < len(bursts):
                    record = bursts[idx]
                    lbl.setText(f"{idx+1}. {record['peak_apm']}APM {record['duration']}s")
                else:
                    lbl.setText(f"{idx+1}. \\u2014")
            profile_data = self.db.get_stats_for_profile(self.viewing_profile)
            hourly_data = profile_data.get("hourly", {})
            self.hourly_chart.set_data(hourly_data)
            self.keyboard_widget.key_stats = keys_data
        except Exception as e:
            logging.exception(f"Error updating UI stats: {e}")

    def _update_heatmap_colors(self):
        if not self.heatmap_enabled:
            return
        aggregated = self.db.get_aggregated_stats(self.viewing_profile)
        keys_counts = aggregated.get("keys", {})
        all_ids = [k["id"] for k in KEYBOARD_LAYOUT]
        visible_counts = []
        for key_id in all_ids:
            count = keys_counts.get(key_id, 0)
            if key_id == "Kp_enter" and count == 0:
                count = keys_counts.get("Enter", 0)
            elif key_id == "Shift_R" and count == 0:
                count = keys_counts.get("Shift_L", 0)
            elif key_id == "Ctrl_R" and count == 0:
                count = keys_counts.get("Ctrl_L", 0)
            elif key_id == "Alt_R" and count == 0:
                count = keys_counts.get("Alt_L", 0)
            elif key_id == "Win_R" and count == 0:
                count = keys_counts.get("Win_L", 0)
            visible_counts.append(count)
        max_count = max(visible_counts) if visible_counts else 0
        color_map = {}
        for i, key_id in enumerate(all_ids):
            count = visible_counts[i]
            factor = count / max_count if max_count > 0 else 0.0
            color_map[key_id] = self.keyboard_widget._resolve_color(factor)
        self.keyboard_widget.update_colors(color_map)

    def _toggle_heatmap(self, state):
        self.heatmap_enabled = bool(state)
        self.keyboard_widget.heatmap_enabled = self.heatmap_enabled
        if self.heatmap_enabled:
            self.heatmap_legend.set_theme(self.keyboard_widget.current_theme_name)
            self.heatmap_legend.setVisible(True)
            self._update_heatmap_colors()
        else:
            self.heatmap_legend.setVisible(False)
            self.keyboard_widget.update_colors({})

    def _change_keyboard_theme(self, name):
        self.keyboard_widget.set_theme(name)
        self.heatmap_legend.set_theme(name)

    def _toggle_incognito(self, state):
        active = bool(state)
        self.tracker.incognito_mode = active
        self.set_incognito(active)
        self.update_ui_stats()

    def set_incognito(self, active):
        self.incognito_active = active
        self.header.is_incognito = active
        if active:
            self.incognito_overlay.setGeometry(self.centralWidget().rect())
            self.incognito_overlay.activate()
            self.incognito_check.setStyleSheet(f"QCheckBox {{ color: #FF3B3B; }} QCheckBox::indicator:checked {{ background: #FF3B3B; border-color: #FF3B3B; }}")
        else:
            self.incognito_overlay.deactivate()
            self.incognito_check.setStyleSheet("")

    @pyqtSlot(bool)
    def _do_set_incognito(self, active):
        self.set_incognito(active)

    def _toggle_overlay(self, state):
        enabled = bool(state)
        self.db.set_overlay_enabled(enabled)
        if enabled:
            if not self.overlay:
                from overlay import FloatingOverlay
                self.overlay = FloatingOverlay(self)
                self.overlay.show()
        else:
            if self.overlay:
                self.overlay.close()
                self.overlay = None

    def _toggle_startup(self, state):
        utils.set_startup(bool(state))

    def _get_custom_profiles(self):
        return [p for p in self.db.get_profiles() if p not in ("Total", "Desktop", "Gaming")]

    def _update_chip_styles(self):
        selected_style = f"background-color: rgba(0,245,212,0.15); border: 1px solid {ACCENT}; color: {ACCENT}; border-radius: 14px; padding: 0 14px; font-size: 13px;"
        unselected_style = f"background-color: transparent; border: 1px solid {BORDER_COLOR}; color: {TEXT_SECONDARY}; border-radius: 14px; padding: 0 14px; font-size: 13px;"
        for name, btn in self.chips.items():
            if name == self.viewing_profile:
                btn.setStyleSheet(selected_style)
                btn.setChecked(True)
            else:
                btn.setStyleSheet(unselected_style)
                btn.setChecked(False)

    def update_profile_selector_ui(self):
        profile = self.viewing_profile
        self._update_chip_styles()
        custom_profiles = self._get_custom_profiles()
        self.profile_combobox.blockSignals(True)
        self.profile_combobox.clear()
        self.profile_combobox.addItems(custom_profiles)
        if profile in ("Total", "Desktop", "Gaming"):
            self.profile_combobox.setCurrentIndex(-1)
            self.del_profile_btn.setVisible(False)
        else:
            idx = self.profile_combobox.findText(profile)
            if idx >= 0:
                self.profile_combobox.setCurrentIndex(idx)
            self.del_profile_btn.setVisible(True)
            if self.profile_btn_group.checkedButton():
                self.profile_btn_group.setExclusive(False)
                self.profile_btn_group.checkedButton().setChecked(False)
                self.profile_btn_group.setExclusive(True)
        self.profile_combobox.blockSignals(False)

    def _on_profile_chip_clicked(self, name):
        self._set_viewing_profile(name)

    def _set_viewing_profile(self, name):
        self.viewing_profile = name
        self.update_profile_selector_ui()
        self._update_heatmap_colors()
        self.update_ui_stats()

    def _on_custom_profile_selected(self, profile_name):
        if not profile_name:
            return
        self._set_viewing_profile(profile_name)

    def _create_profile_dialog(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Add Profile", "Enter new profile name:")
        if ok and name:
            name = name.strip()
            if self.db.create_profile(name):
                self.viewing_profile = name
                self.tracker.set_profile(name)
                self.db.set_last_profile(name)
                self.update_profile_selector_ui()
                self._update_heatmap_colors()
                self.update_ui_stats()
            else:
                QMessageBox.warning(self, "Error", "Profile name empty or already exists.")

    def _delete_active_profile(self):
        profile = self.viewing_profile
        if profile in ("Default", "Total", "Desktop", "Gaming"):
            QMessageBox.warning(self, "Error", "Cannot delete protected profiles.")
            return
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete profile '{profile}'?\\nAll statistics will be permanently lost.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_profile(profile)
            self.viewing_profile = "Default"
            self.tracker.set_profile("Default")
            self.db.set_last_profile("Default")
            self.update_profile_selector_ui()
            self._update_heatmap_colors()
            self.update_ui_stats()

    def trigger_profile_switch_animation(self, from_profile, to_profile):
        self._trigger_profile_switch.emit(from_profile, to_profile)

    @pyqtSlot(str, str)
    def _do_profile_switch_animation(self, from_profile, to_profile):
        if to_profile == "Gaming":
            self.keyboard_widget.start_gaming_banner(from_profile)

    def change_profile(self, profile_name):
        self.update_ui_stats()

    def update_incognito_ui_state(self, value):
        self.incognito_check.setChecked(value)
        self._toggle_incognito(value)

    def _open_mappings_dialog(self):
        dialog = ProcessMappingDialog(self, self.db)
        dialog.exec()

    def _open_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def _export_csv(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Profile Statistics to CSV", f"typetrace_{self.viewing_profile.lower()}_stats.csv", "CSV Files (*.csv)")
        if filepath:
            aggregated = self.db.get_aggregated_stats(self.viewing_profile)
            if utils.export_stats_to_csv(filepath, aggregated):
                QMessageBox.information(self, "Export", "CSV exported successfully!")
            else:
                QMessageBox.warning(self, "Export", "Export failed. Check permissions.")

    def _export_json(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Profile Statistics to JSON", f"typetrace_{self.viewing_profile.lower()}_stats.json", "JSON Files (*.json)")
        if filepath:
            try:
                aggregated = self.db.get_aggregated_stats(self.viewing_profile)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(aggregated, f, indent=4)
                QMessageBox.information(self, "Export", "JSON exported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Export", f"Export failed: {e}")

    def _reset_statistics_dialog(self):
        reply = QMessageBox.question(self, "Reset Statistics", f"Are you sure you want to clear statistics for profile '{self.viewing_profile}'?\\nThis action cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.reset_profile_statistics(self.viewing_profile)
            self._update_heatmap_colors()
            self.update_ui_stats()

    def toggle_heatmap(self):
        self.heatmap_check.setChecked(not self.heatmap_check.isChecked())

    def toggle_incognito(self):
        self.incognito_check.setChecked(not self.incognito_check.isChecked())

    def toggle_overlay(self):
        self.overlay_check.setChecked(not self.overlay_check.isChecked())

    def withdraw_to_tray(self):
        self.hide()

    def restore_from_tray(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def mostra_finestra(self):
        self.restore_from_tray()

    def process_event_queue(self, event_queue):
        self._event_queue = event_queue

    def handle_thread_event(self, event_type, val):
        try:
            if event_type == "keystroke":
                self.keyboard_widget.add_ripple(val)
                self.update_ui_stats()
            elif event_type == "incognito":
                self.update_incognito_ui_state(val)
            elif event_type == "restore":
                self.restore_from_tray()
            elif event_type == "toggle_incognito":
                self.tracker.toggle_incognito()
            elif event_type == "toggle_overlay":
                self.toggle_overlay()
            elif event_type == "burst_detected":
                self.update_ui_stats()
            elif event_type == "profile_changed":
                self.change_profile(val)
            elif event_type == "exit":
                if self.shutdown_callback:
                    self.shutdown_callback(val)
        except Exception as e:
            logging.exception(f"Error handling thread event '{event_type}': {e}")

    def mainloop(self):
        self.show()
        self._qt_app.exec()

    def destroy(self):
        self._qt_app.quit()

    def closeEvent(self, event):
        event.ignore()
        self.withdraw_to_tray()

    def run_background_updates(self):
        return

    def after(self, ms, callback):
        QTimer.singleShot(ms, callback)

    def state(self):
        if self.isMinimized():
            return "iconic"
        if not self.isVisible():
            return "withdrawn"
        return "normal"

    def withdraw(self):
        self.hide()

    def deiconify(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def focus_force(self):
        self.activateWindow()

    def lift(self):
        self.raise_()

    def configure(self, **kwargs):
        return

    def winfo_pointerx(self):
        from PyQt6.QtGui import QCursor
        return QCursor.pos().x()

    def winfo_pointery(self):
        from PyQt6.QtGui import QCursor
        return QCursor.pos().y()

    def winfo_rootx(self):
        return self.mapToGlobal(self.rect().topLeft()).x()

    def winfo_rooty(self):
        return self.mapToGlobal(self.rect().topLeft()).y()

    def winfo_width(self):
        return self.width()

    def winfo_height(self):
        return self.height()

'''

# ─── PART 6: ProcessMappingDialog and AboutDialog ───
PART6 = '''class ProcessMappingDialog(QDialog):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Configure Process Mappings")
        self.setFixedSize(500, 550)
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        title = QLabel("Smart Process Auto-switching")
        title.setStyleSheet(f"color: {ACCENT}; font-size: 15px; font-weight: bold; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        desc = QLabel("Map background process names (.exe) to specific profiles. TypeTrace switches profiles automatically when the process goes in the foreground.")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        add_row = QHBoxLayout()
        add_row.setSpacing(4)
        add_row.addWidget(QLabel("Process:"))
        self.process_entry = QLineEdit()
        self.process_entry.setPlaceholderText("code.exe")
        self.process_entry.setFixedWidth(120)
        add_row.addWidget(self.process_entry)
        add_row.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        profile_choices = [p for p in self.db.get_profiles() if p != "Total"]
        self.profile_combo.addItems(profile_choices)
        self.profile_combo.setFixedWidth(110)
        add_row.addWidget(self.profile_combo)
        add_btn = QPushButton("Add")
        add_btn.setStyleSheet(f"background: {ACCENT}; color: {BG_MAIN}; border: none;")
        add_btn.setFixedWidth(50)
        add_btn.clicked.connect(self._add_mapping)
        add_row.addWidget(add_btn)
        layout.addLayout(add_row)
        mapping_title = QLabel("Custom Mappings")
        mapping_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold; background: transparent;")
        layout.addWidget(mapping_title)
        self.mapping_scroll = QScrollArea()
        self.mapping_scroll.setWidgetResizable(True)
        self.mapping_scroll.setStyleSheet(f"background: {BG_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 8px;")
        self.mapping_container = QWidget()
        self.mapping_layout = QVBoxLayout(self.mapping_container)
        self.mapping_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mapping_layout.setSpacing(4)
        self.mapping_layout.setContentsMargins(4, 4, 4, 4)
        self.mapping_scroll.setWidget(self.mapping_container)
        layout.addWidget(self.mapping_scroll)
        recent_title = QLabel("Recent Processes")
        recent_title.setStyleSheet(f"color: {ACCENT}; font-size: 13px; font-weight: bold; background: transparent;")
        layout.addWidget(recent_title)
        self.recent_scroll = QScrollArea()
        self.recent_scroll.setWidgetResizable(True)
        self.recent_scroll.setStyleSheet(f"background: {BG_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 8px;")
        self.recent_container = QWidget()
        self.recent_layout = QVBoxLayout(self.recent_container)
        self.recent_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.recent_layout.setSpacing(4)
        self.recent_layout.setContentsMargins(4, 4, 4, 4)
        self.recent_scroll.setWidget(self.recent_container)
        layout.addWidget(self.recent_scroll)
        self._load_mappings()
        self._load_recent()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _load_mappings(self):
        self._clear_layout(self.mapping_layout)
        mappings = self.db.get_profile_mappings()
        for proc, prof in mappings.items():
            row = QHBoxLayout()
            lbl = QLabel(f"{proc}  \\u27a1  {prof}")
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-family: Consolas; font-weight: bold; background: transparent;")
            row.addWidget(lbl)
            row.addStretch()
            del_btn = QPushButton("Remove")
            del_btn.setStyleSheet("background: #A63A50; color: #FFFFFF; border: none;")
            del_btn.setFixedWidth(70)
            del_btn.clicked.connect(lambda checked, p=proc: self._delete_mapping(p))
            row.addWidget(del_btn)
            container = QWidget()
            container.setLayout(row)
            container.setStyleSheet(f"background-color: {KEYCAP_BASE}; border: 1px solid {BORDER_COLOR}; border-radius: 6px;")
            self.mapping_layout.addWidget(container)

    def _load_recent(self):
        self._clear_layout(self.recent_layout)
        recent = self.db.get_recent_processes(limit=5)
        for entry in recent:
            if not isinstance(entry, dict):
                continue
            proc = entry.get("process_name", "")
            category = entry.get("category", "Unknown")
            row = QHBoxLayout()
            lbl = QLabel(f"{proc}  ({category})")
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-style: italic; background: transparent;")
            row.addWidget(lbl)
            row.addStretch()
            g_btn = QPushButton("\\u2192 Gaming")
            g_btn.setFixedWidth(75)
            g_btn.clicked.connect(lambda checked, p=proc: self._quick_map(p, "Gaming"))
            row.addWidget(g_btn)
            d_btn = QPushButton("\\u2192 Desktop")
            d_btn.setFixedWidth(75)
            d_btn.clicked.connect(lambda checked, p=proc: self._quick_map(p, "Desktop"))
            row.addWidget(d_btn)
            container = QWidget()
            container.setLayout(row)
            container.setStyleSheet(f"background-color: {KEYCAP_BASE}; border: 1px solid {BORDER_COLOR}; border-radius: 6px;")
            self.recent_layout.addWidget(container)

    def _add_mapping(self):
        proc = self.process_entry.text().strip().lower()
        prof = self.profile_combo.currentText()
        if not proc:
            return
        if not proc.endswith(".exe"):
            proc += ".exe"
        if proc == ".exe" or not prof:
            QMessageBox.warning(self, "Error", "Please fill in a valid process name.")
            return
        mappings = self.db.get_profile_mappings()
        mappings[proc] = prof
        self.db.set_profile_mappings(mappings)
        self.process_entry.clear()
        self._load_mappings()
        self._load_recent()

    def _quick_map(self, process_name, profile_name):
        mappings = self.db.get_profile_mappings()
        proc = process_name.lower()
        if not proc.endswith(".exe"):
            proc += ".exe"
        mappings[proc] = profile_name
        self.db.set_profile_mappings(mappings)
        self._load_mappings()
        self._load_recent()

    def _delete_mapping(self, proc):
        mappings = self.db.get_profile_mappings()
        if proc in mappings:
            del mappings[proc]
            self.db.set_profile_mappings(mappings)
            self._load_mappings()
            self._load_recent()


class AboutDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("About TypeTrace")
        self.setFixedSize(380, 280)
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)
        logo = QLabel("TYPETRACE")
        logo.setStyleSheet(f"color: {ACCENT}; font-size: 28px; font-weight: bold; background: transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        version = QLabel(f"v{APP_VERSION}")
        version.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        desc = QLabel("Privacy-focused keystroke analytics.\\nAll data stored locally on your machine.")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {BORDER_COLOR}; max-height: 1px;")
        layout.addWidget(sep)
        github_btn = QPushButton("\\u2605 GitHub Repository")
        github_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {ACCENT}; border: none; font-size: 13px; font-weight: bold; padding: 8px; }} QPushButton:hover {{ text-decoration: underline; color: {TEXT_PRIMARY}; }}")
        github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        github_btn.clicked.connect(lambda: webbrowser.open(APP_GITHUB))
        layout.addWidget(github_btn)
        footer = QLabel("Made with \\u2328\\ufe0f by TypeTrace")
        footer.setStyleSheet("color: #555555; font-size: 9px; background: transparent;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
'''

# ─── ASSEMBLE AND WRITE ───
with open(TARGET, "w", encoding="utf-8") as f:
    f.write(PART1)
    f.write(KEYBOARD_LAYOUT_STR)
    f.write(PART2)
    f.write(PART3)
    f.write(PART4)
    f.write(PART5)
    f.write(PART6)

print(f"Successfully wrote {TARGET}")

# Count lines
with open(TARGET, "r", encoding="utf-8") as f:
    lines = f.readlines()
print(f"Total lines: {len(lines)}")
