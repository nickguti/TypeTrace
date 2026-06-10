#!/usr/bin/env python3
"""Build script that assembles the complete ui.py with all features A-I + original 1-15."""
import os, sys

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.py")

# ══════════════════════════════════════════════════════════════════════
# PART 1: Imports, constants, themes, helpers, keyboard layout
# ══════════════════════════════════════════════════════════════════════
P1 = '''import os
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
    QMessageBox, QFileDialog, QSizePolicy, QStackedWidget, QButtonGroup,
    QRadioButton, QMenu, QColorDialog
)
from PyQt6.QtCore import (
    Qt, QTimer, QRectF, QPointF, pyqtSignal, QObject, QSize,
    QTime, QPropertyAnimation, QAbstractAnimation, pyqtSlot, QMetaObject, Q_ARG
)
from PyQt6.QtGui import (
    QColor, QPainter, QFont, QFontDatabase, QPen, QBrush,
    QLinearGradient, QIcon, QPixmap, QPainterPath, QFontMetrics,
    QMouseEvent, QCursor
)

import utils

APP_VERSION = "2.0.0"
APP_GITHUB = "https://github.com/nickguti/TypeTrace"

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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

LIGHT_BG_MAIN = "#F0F2F5"
LIGHT_BG_CARD = "#FFFFFF"
LIGHT_BG_CARD_INNER = "#F7F8FA"
LIGHT_BORDER = "#D0D3DB"
LIGHT_BORDER_INNER = "#E2E4E9"
LIGHT_TEXT_PRIMARY = "#1A1C23"
LIGHT_TEXT_SECONDARY = "#6B7280"
LIGHT_KEYCAP_BASE = "#E8EAF0"
LIGHT_KEYCAP_HOVER = "#D5D8E0"

BASE_QSS = """
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
QComboBox QAbstractItemView { background: #171A23; color: #FFFFFF; selection-background-color: #00F5D4; selection-color: #0B0C10; border: 1px solid #2F313D; }
QScrollBar:vertical { background: #0B0C10; width: 6px; }
QScrollBar::handle:vertical { background: #2F313D; border-radius: 3px; }
QScrollBar::handle:vertical:hover { background: #00F5D4; }
QCheckBox { color: #8E9297; font-size: 13px; spacing: 8px; min-height: 32px; }
QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #2F313D; border-radius: 4px; background: #171A23; }
QCheckBox::indicator:checked { background: #00F5D4; border-color: #00F5D4; image: none; }
QLineEdit { background: #171A23; border: 1px solid #2F313D; color: #FFFFFF; padding: 4px 8px; border-radius: 4px; font-size: 13px; }
QRadioButton { color: #8E9297; font-size: 13px; spacing: 8px; }
QRadioButton::indicator { width: 16px; height: 16px; border: 1px solid #2F313D; border-radius: 8px; background: #171A23; }
QRadioButton::indicator:checked { background: #00F5D4; border-color: #00F5D4; }
QMenu { background: #171A23; color: #FFFFFF; border: 1px solid #2F313D; }
QMenu::item:selected { background: #00F5D4; color: #0B0C10; }
"""

LIGHT_BASE_QSS = """
QMainWindow, QWidget { background-color: #F0F2F5; color: #1A1C23; font-family: "Inter", "Segoe UI", "SF Pro Display", sans-serif; font-size: 13px; }
QTabBar::tab { background: #F0F2F5; color: #6B7280; padding: 8px 18px; border: none; font-size: 13px; font-weight: 400; }
QTabBar::tab:selected { color: #1A1C23; border-bottom: 2px solid #00F5D4; background: #FFFFFF; }
QTabBar::tab:hover:!selected { color: #1A1C23; background: #E8EAF0; }
QTabWidget::pane { border: 1px solid #D0D3DB; background: #FFFFFF; }
QPushButton { background: transparent; border: 1px solid #D0D3DB; color: #6B7280; padding: 6px 14px; border-radius: 4px; font-size: 13px; font-weight: 500; }
QPushButton:hover { border-color: #00F5D4; color: #1A1C23; }
QPushButton:pressed { background: rgba(0,245,212,0.1); }
QLabel { color: #1A1C23; font-size: 13px; }
QComboBox { background: #FFFFFF; border: 1px solid #D0D3DB; color: #1A1C23; padding: 4px 8px; border-radius: 4px; font-size: 13px; }
QComboBox:hover { border-color: #00F5D4; }
QComboBox QAbstractItemView { background: #FFFFFF; color: #1A1C23; selection-background-color: #00F5D4; selection-color: #0B0C10; border: 1px solid #D0D3DB; }
QScrollBar:vertical { background: #F0F2F5; width: 6px; }
QScrollBar::handle:vertical { background: #D0D3DB; border-radius: 3px; }
QScrollBar::handle:vertical:hover { background: #00F5D4; }
QCheckBox { color: #6B7280; font-size: 13px; spacing: 8px; min-height: 32px; }
QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #D0D3DB; border-radius: 4px; background: #FFFFFF; }
QCheckBox::indicator:checked { background: #00F5D4; border-color: #00F5D4; image: none; }
QLineEdit { background: #FFFFFF; border: 1px solid #D0D3DB; color: #1A1C23; padding: 4px 8px; border-radius: 4px; font-size: 13px; }
QRadioButton { color: #6B7280; font-size: 13px; spacing: 8px; }
QRadioButton::indicator { width: 16px; height: 16px; border: 1px solid #D0D3DB; border-radius: 8px; background: #FFFFFF; }
QRadioButton::indicator:checked { background: #00F5D4; border-color: #00F5D4; }
QMenu { background: #FFFFFF; color: #1A1C23; border: 1px solid #D0D3DB; }
QMenu::item:selected { background: #00F5D4; color: #0B0C10; }
"""


def hex_to_qcolor(hex_str):
    hex_str = hex_str.lstrip('#')
    return QColor(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))


def qcolor_to_hex(c):
    return f"#{c.red():02x}{c.green():02x}{c.blue():02x}"

'''

# ══════════════════════════════════════════════════════════════════════
# PART 2: SettingsManager + Translator + Keyboard themes
# ══════════════════════════════════════════════════════════════════════
P2 = '''
class SettingsManager:
    DEFAULTS = {
        "accent_color": "#00F5D4",
        "theme": "dark",
        "compact_mode": False,
        "language": "en",
        "overlay_x": None,
        "overlay_y": None,
        "overlay_width": 200,
        "overlay_height": 80,
        "overlay_fields": ["apm", "wpm"],
        "welcome_shown": False,
    }

    def __init__(self):
        self._path = os.path.join(_SCRIPT_DIR, "settings.json")
        self._data = {}
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}
        for k, v in self.DEFAULTS.items():
            if k not in self._data:
                self._data[k] = v

    def get(self, key):
        return self._data.get(key, self.DEFAULTS.get(key))

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def save(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass


class Translator:
    def __init__(self, lang_code="en"):
        self._lang = lang_code
        self._strings = {}
        self._load()

    def _load(self):
        lang_path = os.path.join(_SCRIPT_DIR, "lang.json")
        try:
            with open(lang_path, "r", encoding="utf-8") as f:
                all_langs = json.load(f)
            self._strings = all_langs.get(self._lang, all_langs.get("en", {}))
        except Exception:
            self._strings = {}

    def t(self, key):
        return self._strings.get(key, key)


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

# ══════════════════════════════════════════════════════════════════════
# PART 3: Keyboard layout data
# ══════════════════════════════════════════════════════════════════════
P3 = '''KEYBOARD_LAYOUT = [
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
    {"id": "\\\\\\\\", "label": "\\\\\\\\", "rx": 0.5625, "ry": 0.34, "rw": 0.0625, "rh": 0.155},
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
    {"id": "\\'", "label": "\\'", "rx": 0.4896, "ry": 0.51, "rw": 0.0417, "rh": 0.155},
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
    {"id": "Up", "label": "\\u2191", "rx": 0.6875, "ry": 0.68, "rw": 0.0417, "rh": 0.155},
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
    {"id": "Left", "label": "\\u2190", "rx": 0.6458, "ry": 0.85, "rw": 0.0417, "rh": 0.155},
    {"id": "Down", "label": "\\u2193", "rx": 0.6875, "ry": 0.85, "rw": 0.0417, "rh": 0.155},
    {"id": "Right", "label": "\\u2192", "rx": 0.7292, "ry": 0.85, "rw": 0.0417, "rh": 0.155},
    {"id": "Kp_0", "label": "0", "rx": 0.7917, "ry": 0.85, "rw": 0.0833, "rh": 0.155},
    {"id": "Kp_.", "label": ".", "rx": 0.875, "ry": 0.85, "rw": 0.0417, "rh": 0.155},
]

'''

# ══════════════════════════════════════════════════════════════════════
# PART 4: Widget classes (KeyTooltip, HeaderWidget, LegendBarWidget)
# ══════════════════════════════════════════════════════════════════════
P4 = r'''class KeyTooltip(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.key_name = ""
        self.press_count = 0
        self.percentage = 0.0
        self.rank_text = ""
        self.resize(160, 95)
        self._is_light = False

    def update_info(self, key_name, count, total, rank_idx):
        self.key_name = key_name
        self.press_count = count
        self.percentage = (count / total * 100) if total > 0 else 0.0
        self.rank_text = f"#{rank_idx} most used" if count > 0 else "Not used"
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, 6, 6)
        bg = hex_to_qcolor(LIGHT_BG_CARD if self._is_light else BG_CARD)
        accent = hex_to_qcolor(ACCENT)
        tp = hex_to_qcolor(LIGHT_TEXT_PRIMARY if self._is_light else TEXT_PRIMARY)
        ts = hex_to_qcolor(LIGHT_TEXT_SECONDARY if self._is_light else TEXT_SECONDARY)
        painter.fillPath(path, bg)
        painter.setPen(QPen(accent, 1.0))
        painter.drawPath(path)
        painter.setPen(tp)
        painter.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        painter.drawText(QRectF(12, 12, self.width() - 24, 20), Qt.AlignmentFlag.AlignLeft, self.key_name)
        painter.setPen(ts)
        painter.setFont(QFont(FONT_FAMILY, 12))
        painter.drawText(QRectF(12, 36, self.width() - 24, 16), Qt.AlignmentFlag.AlignLeft, f"{self.press_count:,} presses")
        painter.drawText(QRectF(12, 52, self.width() - 24, 16), Qt.AlignmentFlag.AlignLeft, f"{self.percentage:.1f}% of total")
        painter.setPen(accent)
        painter.drawText(QRectF(12, 68, self.width() - 24, 16), Qt.AlignmentFlag.AlignLeft, self.rank_text)


class HeaderWidget(QWidget):
    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.displayed_apm = 0.0
        self.target_apm = 0
        self.displayed_wpm = 0.0
        self.target_wpm = 0
        self.is_tracking = True
        self.is_incognito = False
        self._is_light = False
        self._accent_hex = ACCENT
        self._tr = tr
        self.help_btn = QPushButton("?", self)
        self.help_btn.setFixedSize(20, 20)
        self.help_btn.setStyleSheet(f"QPushButton {{ background: {BG_CARD}; border: 1px solid {BORDER_COLOR}; color: {TEXT_SECONDARY}; border-radius: 10px; padding: 0px; font-size: 11px; font-weight: bold; }} QPushButton:hover {{ background: {BORDER_COLOR}; color: {TEXT_PRIMARY}; border-color: {ACCENT}; }}")
        self.compact_btn = QPushButton("\u229f", self)
        self.compact_btn.setFixedSize(24, 24)
        self.compact_btn.setToolTip("Compact Mode")
        self.compact_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid {BORDER_COLOR}; color: {TEXT_SECONDARY}; border-radius: 4px; padding: 0px; font-size: 14px; }} QPushButton:hover {{ border-color: {ACCENT}; color: {TEXT_PRIMARY}; }}")
        self.theme_btn = QPushButton("\u263e", self)
        self.theme_btn.setFixedSize(24, 24)
        self.theme_btn.setToolTip("Toggle Light/Dark")
        self.theme_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid {BORDER_COLOR}; color: {TEXT_SECONDARY}; border-radius: 4px; padding: 0px; font-size: 14px; }} QPushButton:hover {{ border-color: {ACCENT}; color: {TEXT_PRIMARY}; }}")
        self.color_btn = QPushButton("", self)
        self.color_btn.setFixedSize(90, 20)
        self.color_btn.setToolTip("Choose Accent Color")
        self._update_color_btn_style()

    def _update_color_btn_style(self):
        self.color_btn.setText(f"\u25cf {self._accent_hex.upper()}")
        self.color_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid {BORDER_COLOR}; color: {self._accent_hex}; border-radius: 4px; padding: 0px; font-size: 12px; font-weight: bold; }} QPushButton:hover {{ border-color: {self._accent_hex}; }}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        right = self.width() - 30
        self.help_btn.move(right, 14)
        self.compact_btn.move(right - 30, 12)
        self.theme_btn.move(right - 60, 12)
        self.color_btn.move(right - 160, 14)

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
        bg = hex_to_qcolor(LIGHT_BG_MAIN if self._is_light else BG_MAIN)
        brd = hex_to_qcolor(LIGHT_BORDER if self._is_light else BORDER_COLOR)
        tp = hex_to_qcolor(LIGHT_TEXT_PRIMARY if self._is_light else TEXT_PRIMARY)
        ts = hex_to_qcolor(LIGHT_TEXT_SECONDARY if self._is_light else TEXT_SECONDARY)
        accent = hex_to_qcolor(self._accent_hex)
        painter.fillRect(self.rect(), bg)
        painter.setPen(QPen(brd, 1.0))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(accent))
        painter.drawRoundedRect(QRectF(15, 10, 28, 28), 6, 6)
        painter.setPen(hex_to_qcolor(BG_MAIN))
        painter.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        painter.drawText(QRectF(15, 10, 28, 28), Qt.AlignmentFlag.AlignCenter, "TT")
        painter.setPen(tp)
        painter.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.DemiBold))
        title = self._tr.t("app_title") if self._tr else "TYPETRACE"
        painter.drawText(QRectF(55, 8, 200, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, title)
        painter.setPen(ts)
        painter.setFont(QFont(FONT_FAMILY, 10))
        subtitle = self._tr.t("app_subtitle") if self._tr else "PRIVACY-FOCUSED KEYSTROKE ANALYZER"
        painter.drawText(QRectF(55, 26, 300, 14), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, subtitle)
        cx = self.width() / 2 - 40
        painter.setPen(accent)
        painter.setFont(QFont(FONT_FAMILY, 22, QFont.Weight.Bold))
        painter.drawText(QRectF(cx - 110, 0, 70, 48), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(round(self.displayed_apm)))
        painter.setPen(ts)
        painter.setFont(QFont(FONT_FAMILY, 11))
        painter.drawText(QRectF(cx - 35, 0, 30, 48), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "APM")
        painter.setPen(QPen(brd, 1.0))
        painter.drawLine(int(cx), 10, int(cx), 38)
        painter.setPen(accent)
        painter.setFont(QFont(FONT_FAMILY, 22, QFont.Weight.Bold))
        painter.drawText(QRectF(cx + 10, 0, 70, 48), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(round(self.displayed_wpm)))
        painter.setPen(ts)
        painter.setFont(QFont(FONT_FAMILY, 11))
        painter.drawText(QRectF(cx + 85, 0, 30, 48), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "WPM")
        if self.is_incognito:
            c = hex_to_qcolor("#FF3B3B")
            painter.setBrush(QBrush(c))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx + 140, 24), 4, 4)
            painter.setPen(c)
            painter.setFont(QFont(FONT_FAMILY, 11))
            inc_text = self._tr.t("tracking_incognito") if self._tr else "INCOGNITO"
            painter.drawText(QRectF(cx + 150, 0, 80, 48), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, inc_text)
        else:
            if self.is_tracking:
                elapsed_ms = QTime.currentTime().msecsSinceStartOfDay()
                opacity = 0.7 + 0.3 * math.sin(2 * math.pi * elapsed_ms / 1200)
                c = accent
                c2 = QColor(c)
                c2.setAlphaF(opacity)
                painter.setBrush(QBrush(c2))
            else:
                painter.setBrush(QBrush(ts))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx + 140, 24), 4, 4)
            painter.setPen(ts)
            painter.setFont(QFont(FONT_FAMILY, 11))
            trk_text = self._tr.t("tracking_active") if self._tr else "Tracking"
            if not self.is_tracking:
                trk_text = self._tr.t("tracking_paused") if self._tr else "Paused"
            painter.drawText(QRectF(cx + 150, 0, 60, 48), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, trk_text)


class LegendBarWidget(QWidget):
    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.theme = "Classic Heatmap"
        self._is_light = False
        self._tr = tr

    def set_theme(self, name):
        self.theme = name
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = hex_to_qcolor(LIGHT_BG_CARD if self._is_light else BG_CARD)
        brd = hex_to_qcolor(LIGHT_BORDER if self._is_light else BORDER_COLOR)
        ts = hex_to_qcolor(LIGHT_TEXT_SECONDARY if self._is_light else TEXT_SECONDARY)
        panel_rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(panel_rect, 6, 6)
        painter.fillPath(path, bg)
        painter.setPen(QPen(brd, 1.0))
        painter.drawPath(path)
        painter.setPen(ts)
        font = QFont(FONT_FAMILY, 10)
        font.setItalic(True)
        painter.setFont(font)
        cold = self._tr.t("cold") if self._tr else "Cold"
        hot = self._tr.t("hot") if self._tr else "Hot"
        painter.drawText(QRectF(8, 4, 40, 16), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, cold)
        painter.drawText(QRectF(self.width() - 48, 4, 40, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, hot)
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
            painter.setPen(QPen(brd, 1.0))
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
                painter.setPen(ts)
                painter.drawText(QRectF(tx + ox, bar_y + bar_h + 6, w_t, 14), align | Qt.AlignmentFlag.AlignVCenter, f"{val}%")

'''

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(P1)
    f.write(P2)
    f.write(P3)
    f.write(P4)

print(f"Part A written. Lines: {sum(1 for _ in open(TARGET, encoding='utf-8'))}")
