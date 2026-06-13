import sys
import os
import json
import logging
import math
import queue
import webbrowser
from dataclasses import dataclass, replace
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QCheckBox, QStackedWidget,
    QTabWidget, QTabBar, QButtonGroup, QRadioButton, QDialog, QLineEdit,
    QColorDialog, QGraphicsOpacityEffect, QMessageBox, QFileDialog, QScrollArea, QFrame, QGridLayout, QSizePolicy, QScrollBar
)
from PyQt6.QtCore import (
    Qt, QTimer, QTime, QRectF, QPointF, pyqtSignal, pyqtSlot, QAbstractAnimation,
    QPropertyAnimation, QMetaObject, Q_ARG, QEasingCurve, QRect, QSize, pyqtProperty,
    QSequentialAnimationGroup
)
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QPainterPath,
    QLinearGradient, QRadialGradient, QCursor, QFontDatabase
)
import utils

class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()

APP_VERSION = "2.1.0"
APP_GITHUB = "https://github.com/nicolas/typetrace"

FONT_FAMILY = "Segoe UI Variable"

@dataclass
class ThemeTokens:
    bg_window: str
    bg_panel: str
    bg_input: str
    bg_hover: str
    border: str
    accent: str
    text_primary: str
    text_secondary: str
    key_cold: str
    key_shadow: str
    key_highlight: str
    tab_pane_bg: str
    status_bar_bg: str

DARK_TOKENS = ThemeTokens(
    bg_window="#0B0C10", bg_panel="#171A23", bg_input="#171A23", bg_hover="#13151C",
    border="#2F313D", accent="#00F5D4",
    text_primary="#FFFFFF", text_secondary="#8E9297",
    key_cold="#1E2130", key_shadow="#000000",
    key_highlight="rgba(255,255,255,0.08)",
    tab_pane_bg="#171A23", status_bar_bg="#0B0C10"
)

LIGHT_TOKENS = ThemeTokens(
    bg_window="#F0F2F7", bg_panel="#FFFFFF", bg_input="#F7F8FC", bg_hover="#E8EBF4",
    border="#D1D5E0", accent="#00C4AA",
    text_primary="#1C1E26", text_secondary="#6B7280",
    key_cold="#E2E5EF", key_shadow="#C5C9D6",
    key_highlight="rgba(255,255,255,0.9)",
    tab_pane_bg="#FFFFFF", status_bar_bg="#E8EBF4"
)

def build_qss(tokens: ThemeTokens) -> str:
    return f"""
QMainWindow {{
    background-color: {tokens.bg_window};
}}
QWidget {{
    color: {tokens.text_primary};
    font-family: "{FONT_FAMILY}";
}}
QPushButton {{
    background-color: {tokens.bg_input};
    color: {tokens.text_primary};
    border: 1px solid {tokens.border};
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {tokens.border};
}}
QPushButton:pressed {{
    background-color: {tokens.bg_window};
}}
QPushButton:disabled {{
    background-color: {tokens.bg_window};
    color: {tokens.text_secondary};
    border: 1px solid {tokens.border};
}}
QLabel {{
    background: transparent;
}}
QCheckBox {{
    color: {tokens.text_primary};
    font-size: 13px;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    background: {tokens.bg_input};
    border: 1px solid {tokens.border};
}}
QCheckBox::indicator:hover {{
    border: 1px solid {tokens.accent};
}}
QCheckBox::indicator:checked {{
    background: {tokens.accent};
    border-color: {tokens.accent};
    image: url(); /* Placeholder for custom check icon if needed */
}}
QComboBox {{
    background-color: {tokens.bg_input};
    color: {tokens.text_primary};
    border: 1px solid {tokens.border};
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 13px;
}}
QComboBox:hover {{
    border: 1px solid {tokens.accent};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {tokens.text_secondary};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {tokens.bg_input};
    color: {tokens.text_primary};
    selection-background-color: rgba({int(tokens.accent[1:3], 16)}, {int(tokens.accent[3:5], 16)}, {int(tokens.accent[5:7], 16)}, 0.3);
    border: 1px solid {tokens.border};
    border-radius: 4px;
    outline: none;
}}
QLineEdit {{
    background-color: {tokens.bg_input};
    color: {tokens.text_primary};
    border: 1px solid {tokens.border};
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1px solid {tokens.accent};
}}
QScrollBar:vertical {{
    background: {tokens.bg_window};
    width: 10px;
    margin: 0px 0px 0px 0px;
}}
QScrollBar:horizontal {{
    background: {tokens.bg_window};
    height: 10px;
    margin: 0px 0px 0px 0px;
}}
QScrollBar::handle:vertical {{
    background: {tokens.border};
    min-height: 20px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal {{
    background: {tokens.border};
    min-width: 20px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: {tokens.text_secondary};
}}
QScrollBar::handle:horizontal:hover {{
    background: {tokens.text_secondary};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    background: none;
    height: 0px;
    width: 0px;
}}
QMenu {{
    background-color: {tokens.bg_panel};
    border: 1px solid {tokens.border};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item {{
    color: {tokens.text_primary};
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: rgba({int(tokens.accent[1:3], 16)}, {int(tokens.accent[3:5], 16)}, {int(tokens.accent[5:7], 16)}, 0.15);
    color: {tokens.accent};
}}
QMenu::separator {{
    height: 1px;
    background: {tokens.border};
    margin: 4px 0;
}}
QDialog {{
    background-color: {tokens.bg_window};
}}
QToolTip {{
    background-color: {tokens.bg_panel};
    color: {tokens.text_primary};
    border: 1px solid {tokens.border};
    border-radius: 4px;
    padding: 4px 8px;
}}
"""

def hex_to_qcolor(h):
    if not h: return QColor(0,0,0)
    h = str(h).strip('#')
    if len(h) != 6: return QColor(0,0,0)
    return QColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def qcolor_to_hex(c):
    return f"#{c.red():02X}{c.green():02X}{c.blue():02X}"

def interpolate_color(c1: QColor, c2: QColor, factor: float) -> QColor:
    r = int(c1.red() + (c2.red() - c1.red()) * factor)
    g = int(c1.green() + (c2.green() - c1.green()) * factor)
    b = int(c1.blue() + (c2.blue() - c1.blue()) * factor)
    return QColor(r, g, b)

def interpolate_color_ramp(val, ramp):
    if val <= ramp[0][0]: return ramp[0][1]
    if val >= ramp[-1][0]: return ramp[-1][1]
    for i in range(len(ramp) - 1):
        t1, c1 = ramp[i]
        t2, c2 = ramp[i + 1]
        if t1 <= val <= t2:
            span = t2 - t1
            if span == 0: return c1
            f = (val - t1) / span
            return interpolate_color(c1, c2, f)
    return ramp[-1][1]

KEYBOARD_THEMES = {
    "Classic Heatmap": [
        (0.0, QColor(30, 33, 48)),
        (0.1, QColor(40, 100, 150)),
        (0.3, QColor(0, 245, 212)),
        (0.6, QColor(255, 215, 0)),
        (1.0, QColor(255, 59, 59))
    ],
    "Neon": [
        (0.0, QColor(20, 20, 30)),
        (0.2, QColor(138, 43, 226)),
        (0.5, QColor(255, 20, 147)),
        (0.8, QColor(0, 255, 255)),
        (1.0, QColor(255, 255, 255))
    ],
    "Monochrome": [
        (0.0, QColor(40, 40, 40)),
        (0.3, QColor(100, 100, 100)),
        (0.6, QColor(180, 180, 180)),
        (1.0, QColor(255, 255, 255))
    ],
    "Ice Blue": [
        (0.0, QColor(10, 25, 50)),
        (0.2, QColor(30, 80, 140)),
        (0.5, QColor(70, 150, 220)),
        (0.8, QColor(150, 200, 255)),
        (1.0, QColor(220, 240, 255))
    ],
    "Sunset": [
        (0.0, QColor(40, 10, 30)),
        (0.2, QColor(120, 30, 50)),
        (0.5, QColor(220, 80, 40)),
        (0.8, QColor(250, 160, 50)),
        (1.0, QColor(255, 230, 100))
    ]
}

KEYBOARD_LAYOUT = [
    {"id": "Escape", "label": "Esc", "rx": 0.0, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F1", "label": "F1", "rx": 0.07, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F2", "label": "F2", "rx": 0.12, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F3", "label": "F3", "rx": 0.17, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F4", "label": "F4", "rx": 0.22, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F5", "label": "F5", "rx": 0.29, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F6", "label": "F6", "rx": 0.34, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F7", "label": "F7", "rx": 0.39, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F8", "label": "F8", "rx": 0.44, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F9", "label": "F9", "rx": 0.51, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F10", "label": "F10", "rx": 0.56, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F11", "label": "F11", "rx": 0.61, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "F12", "label": "F12", "rx": 0.66, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "PrintScreen", "label": "PrtSc", "rx": 0.73, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "ScrollLock", "label": "ScrLk", "rx": 0.78, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "Pause", "label": "Pause", "rx": 0.83, "ry": 0.0, "rw": 0.05, "rh": 0.16},
    {"id": "Backquote", "label": "`", "rx": 0.0, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "1", "label": "1", "rx": 0.05, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "2", "label": "2", "rx": 0.10, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "3", "label": "3", "rx": 0.15, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "4", "label": "4", "rx": 0.20, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "5", "label": "5", "rx": 0.25, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "6", "label": "6", "rx": 0.30, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "7", "label": "7", "rx": 0.35, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "8", "label": "8", "rx": 0.40, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "9", "label": "9", "rx": 0.45, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "0", "label": "0", "rx": 0.50, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "Minus", "label": "-", "rx": 0.55, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "Equal", "label": "=", "rx": 0.60, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "Backspace", "label": "\u2190", "rx": 0.65, "ry": 0.18, "rw": 0.06, "rh": 0.16},
    {"id": "Insert", "label": "Ins", "rx": 0.73, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "Home", "label": "Home", "rx": 0.78, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "PageUp", "label": "PgUp", "rx": 0.83, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "NumLock", "label": "Num", "rx": 0.90, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_Divide", "label": "/", "rx": 0.95, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_Multiply", "label": "*", "rx": 1.00, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_Subtract", "label": "-", "rx": 1.05, "ry": 0.18, "rw": 0.05, "rh": 0.16},
    {"id": "Tab", "label": "Tab", "rx": 0.0, "ry": 0.36, "rw": 0.075, "rh": 0.16},
    {"id": "Q", "label": "Q", "rx": 0.075, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "W", "label": "W", "rx": 0.125, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "E", "label": "E", "rx": 0.175, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "R", "label": "R", "rx": 0.225, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "T", "label": "T", "rx": 0.275, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "Y", "label": "Y", "rx": 0.325, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "U", "label": "U", "rx": 0.375, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "I", "label": "I", "rx": 0.425, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "O", "label": "O", "rx": 0.475, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "P", "label": "P", "rx": 0.525, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "BracketLeft", "label": "[", "rx": 0.575, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "BracketRight", "label": "]", "rx": 0.625, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "Backslash", "label": "\\", "rx": 0.675, "ry": 0.36, "rw": 0.035, "rh": 0.16},
    {"id": "Delete", "label": "Del", "rx": 0.73, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "End", "label": "End", "rx": 0.78, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "PageDown", "label": "PgDn", "rx": 0.83, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_7", "label": "7", "rx": 0.90, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_8", "label": "8", "rx": 0.95, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_9", "label": "9", "rx": 1.00, "ry": 0.36, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_Add", "label": "+", "rx": 1.05, "ry": 0.36, "rw": 0.05, "rh": 0.34},
    {"id": "CapsLock", "label": "Caps", "rx": 0.0, "ry": 0.54, "rw": 0.09, "rh": 0.16},
    {"id": "A", "label": "A", "rx": 0.09, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "S", "label": "S", "rx": 0.14, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "D", "label": "D", "rx": 0.19, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "F", "label": "F", "rx": 0.24, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "G", "label": "G", "rx": 0.29, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "H", "label": "H", "rx": 0.34, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "J", "label": "J", "rx": 0.39, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "K", "label": "K", "rx": 0.44, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "L", "label": "L", "rx": 0.49, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "Semicolon", "label": ";", "rx": 0.54, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "Quote", "label": "'", "rx": 0.59, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "Enter", "label": "Enter", "rx": 0.64, "ry": 0.54, "rw": 0.07, "rh": 0.16},
    {"id": "Kp_4", "label": "4", "rx": 0.90, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_5", "label": "5", "rx": 0.95, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_6", "label": "6", "rx": 1.00, "ry": 0.54, "rw": 0.05, "rh": 0.16},
    {"id": "Shift_L", "label": "Shift", "rx": 0.0, "ry": 0.72, "rw": 0.11, "rh": 0.16},
    {"id": "Z", "label": "Z", "rx": 0.11, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "X", "label": "X", "rx": 0.16, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "C", "label": "C", "rx": 0.21, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "V", "label": "V", "rx": 0.26, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "B", "label": "B", "rx": 0.31, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "N", "label": "N", "rx": 0.36, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "M", "label": "M", "rx": 0.41, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "Comma", "label": ",", "rx": 0.46, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "Period", "label": ".", "rx": 0.51, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "Slash", "label": "/", "rx": 0.56, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "Shift_R", "label": "Shift", "rx": 0.61, "ry": 0.72, "rw": 0.10, "rh": 0.16},
    {"id": "Up", "label": "\u2191", "rx": 0.78, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_1", "label": "1", "rx": 0.90, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_2", "label": "2", "rx": 0.95, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_3", "label": "3", "rx": 1.00, "ry": 0.72, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_Enter", "label": "Ent", "rx": 1.05, "ry": 0.72, "rw": 0.05, "rh": 0.34},
    {"id": "Ctrl_L", "label": "Ctrl", "rx": 0.0, "ry": 0.90, "rw": 0.06, "rh": 0.16},
    {"id": "Win_L", "label": "Win", "rx": 0.06, "ry": 0.90, "rw": 0.06, "rh": 0.16},
    {"id": "Alt_L", "label": "Alt", "rx": 0.12, "ry": 0.90, "rw": 0.06, "rh": 0.16},
    {"id": "Space", "label": "", "rx": 0.18, "ry": 0.90, "rw": 0.30, "rh": 0.16},
    {"id": "Alt_R", "label": "Alt", "rx": 0.48, "ry": 0.90, "rw": 0.06, "rh": 0.16},
    {"id": "Win_R", "label": "Win", "rx": 0.54, "ry": 0.90, "rw": 0.06, "rh": 0.16},
    {"id": "Menu", "label": "\u2630", "rx": 0.60, "ry": 0.90, "rw": 0.05, "rh": 0.16},
    {"id": "Ctrl_R", "label": "Ctrl", "rx": 0.65, "ry": 0.90, "rw": 0.06, "rh": 0.16},
    {"id": "Left", "label": "\u2190", "rx": 0.73, "ry": 0.90, "rw": 0.05, "rh": 0.16},
    {"id": "Down", "label": "\u2193", "rx": 0.78, "ry": 0.90, "rw": 0.05, "rh": 0.16},
    {"id": "Right", "label": "\u2192", "rx": 0.83, "ry": 0.90, "rw": 0.05, "rh": 0.16},
    {"id": "Kp_0", "label": "0", "rx": 0.90, "ry": 0.90, "rw": 0.10, "rh": 0.16},
    {"id": "Kp_Decimal", "label": ".", "rx": 1.00, "ry": 0.90, "rw": 0.05, "rh": 0.16},
]

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
        "keyboard_theme": "Classic Heatmap",
        "keyboard_style": "Mechanical",
        "overlay_opacity": 1.0,
        "overlay_scale": 1.0,
        "overlay_show_apm": True,
        "overlay_show_wpm": True,
        "overlay_show_peak": False,
        "overlay_show_profile": True
    }

    def __init__(self):
        self._path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        self._data = self.DEFAULTS.copy()
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self._data.update(loaded)
            except Exception as e:
                logging.error(f"Error loading settings.json: {e}")
        else:
            self.save()

    def get(self, key):
        return self._data.get(key, self.DEFAULTS.get(key))

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def save(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
        except Exception as e:
            logging.error(f"Error writing settings.json: {e}")

class Translator:
    def __init__(self, lang_code: str):
        self._lang_code = lang_code
        self._dict = {}
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lang.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    all_langs = json.load(f)
                    self._dict = all_langs.get(lang_code, all_langs.get("en", {}))
            except Exception as e:
                logging.error(f"Error loading lang.json: {e}")

    def t(self, key: str) -> str:
        return self._dict.get(key, key)

class HeaderWidget(QWidget):
    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.tr = tr
        self.tokens = DARK_TOKENS
        self.setFixedHeight(80)
        self.apm = 0
        self.wpm = 0
        self.is_tracking = True
        self.is_incognito = False
        self.bg_pulse_alpha = 0
        layout = QHBoxLayout(self)
        layout.setContentsMargins(80, 0, 20, 0)
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.title_lbl = QLabel(self.tr.t("app_title") if self.tr else "TYPETRACE")
        self.title_lbl.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        title_layout.addWidget(self.title_lbl)
        self.subtitle_lbl = QLabel(self.tr.t("app_subtitle") if self.tr else "PRIVACY-FOCUSED KEYSTROKE ANALYZER")
        self.subtitle_lbl.setFont(QFont(FONT_FAMILY, 10))
        title_layout.addWidget(self.subtitle_lbl)
        layout.addLayout(title_layout)
        layout.addStretch()
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        self.status_dot = QLabel("●")
        self.status_dot.setFont(QFont(FONT_FAMILY, 14))
        stats_layout.addWidget(self.status_dot)
        self.status_lbl = QLabel()
        self.status_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        stats_layout.addWidget(self.status_lbl)
        self.apm_lbl = QLabel("0 APM")
        self.apm_lbl.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        self.apm_lbl.setMinimumWidth(80)
        self.apm_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        stats_layout.addWidget(self.apm_lbl)
        self.wpm_lbl = QLabel("0 WPM")
        self.wpm_lbl.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        self.wpm_lbl.setMinimumWidth(80)
        self.wpm_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        stats_layout.addWidget(self.wpm_lbl)
        layout.addLayout(stats_layout)
        layout.addSpacing(20)
        
        self.compact_btn = QPushButton("\u229f")
        self.compact_btn.setFixedSize(32, 32)
        self.compact_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.compact_btn.setToolTip(self.tr.t("compact_mode") if self.tr else "Compact Mode")
        layout.addWidget(self.compact_btn)
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setToolTip("Impostazioni")
        layout.addWidget(self.settings_btn)

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.title_lbl.setStyleSheet(f"color: {self.tokens.text_primary}; background: transparent;")
        self.subtitle_lbl.setStyleSheet(f"color: {self.tokens.text_secondary}; background: transparent;")
        self.apm_lbl.setStyleSheet(f"color: {self.tokens.accent}; background: transparent;")
        self.wpm_lbl.setStyleSheet(f"color: {self.tokens.accent}; background: transparent;")
        
        btn_qss = f"""
            QPushButton {{
                background-color: transparent;
                color: {self.tokens.text_secondary};
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {self.tokens.bg_panel};
                color: {self.tokens.text_primary};
            }}
        """
        self.compact_btn.setStyleSheet(btn_qss)
        self.settings_btn.setStyleSheet(btn_qss)
        self._update_status_labels()
        self.update()

    def update_stats(self, apm, wpm, is_tracking):
        self.apm = apm
        self.wpm = wpm
        self.is_tracking = is_tracking
        self.apm_lbl.setText(f"{self.apm} APM")
        self.wpm_lbl.setText(f"{self.wpm} WPM")
        self._update_status_labels()

    def _update_status_labels(self):
        if self.is_incognito:
            c = "#FF3B3B"
            self.status_lbl.setText(self.tr.t("tracking_incognito") if self.tr else "INCOGNITO")
        else:
            c = self.tokens.accent
            self.status_lbl.setText(self.tr.t("tracking_active") if self.tr else "Tracking")
        self.status_dot.setStyleSheet(f"color: {c}; background: transparent;")
        
        if self.is_incognito:
            self.status_lbl.setStyleSheet(f"color: {c}; background: transparent;")
        else:
            self.status_lbl.setStyleSheet(f"color: {self.tokens.text_secondary}; background: transparent;")

    def on_anim_tick(self):
        self.bg_pulse_alpha += 0.05
        if self.bg_pulse_alpha > 2 * math.pi:
            self.bg_pulse_alpha -= 2 * math.pi

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), hex_to_qcolor(self.tokens.bg_window))
        if not self.is_incognito and self.is_tracking:
            pulse = (math.sin(self.bg_pulse_alpha) + 1) / 2
            alpha = int(10 + 15 * pulse)
            c = hex_to_qcolor(self.tokens.accent)
            c.setAlpha(alpha)
            painter.fillRect(self.rect(), c)
            
        painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        
        # Draw "TT" monogram
        m_size = 40
        mx = 20
        my = (self.height() - m_size) // 2
        path = QPainterPath()
        path.addRoundedRect(QRectF(mx, my, m_size, m_size), 8, 8)
        painter.fillPath(path, hex_to_qcolor(self.tokens.accent))
        painter.setPen(QPen(hex_to_qcolor("#0B0C10"), 1.0))
        painter.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        painter.drawText(QRectF(mx, my, m_size, m_size), Qt.AlignmentFlag.AlignCenter, "TT")
        
        # Vertical Separator before stats
        painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
        sep_x = self.width() - 320
        painter.drawLine(sep_x, 20, sep_x, self.height() - 20)
        
        painter.end()


class KeyTooltip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tokens = DARK_TOKENS
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.key_label = ""
        self.count = 0
        self.total = 0
        self.rank = 0
        self.resize(160, 60)

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.update()

    def update_info(self, key_label, count, total, rank):
        self.key_label = key_label
        self.count = count
        self.total = total
        self.rank = rank
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, 6, 6)
        painter.fillPath(path, hex_to_qcolor(self.tokens.bg_panel))
        painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
        painter.drawPath(path)
        painter.setPen(hex_to_qcolor(self.tokens.text_primary))
        painter.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        painter.drawText(QRectF(10, 8, self.width() - 20, 20), Qt.AlignmentFlag.AlignLeft, self.key_label)
        if self.total > 0:
            pct = (self.count / self.total) * 100
        else:
            pct = 0.0
        stats = f"{self.count} hits ({pct:.1f}%)"
        painter.setPen(hex_to_qcolor(self.tokens.text_secondary))
        painter.setFont(QFont(FONT_FAMILY, 11))
        painter.drawText(QRectF(10, 30, self.width() - 20, 20), Qt.AlignmentFlag.AlignLeft, stats)
        if self.rank > 0:
            painter.setPen(hex_to_qcolor(self.tokens.accent))
            painter.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            painter.drawText(QRectF(10, 8, self.width() - 20, 20), Qt.AlignmentFlag.AlignRight, f"#{self.rank}")
        painter.end()


class LegendBarWidget(QWidget):
    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.tr = tr
        self.tokens = DARK_TOKENS
        self.setFixedHeight(30)
        self.current_theme_name = "Classic Heatmap"
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.update()

    def set_theme(self, name):
        self.current_theme_name = name
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), hex_to_qcolor(self.tokens.bg_panel))
        ramp = KEYBOARD_THEMES.get(self.current_theme_name, KEYBOARD_THEMES["Classic Heatmap"])
        bar_w = 300
        bar_h = 10
        x = (self.width() - bar_w) / 2
        y = (self.height() - bar_h) / 2
        grad = QLinearGradient(x, y, x + bar_w, y)
        for t, c in ramp:
            grad.setColorAt(t, c)
        path = QPainterPath()
        path.addRoundedRect(QRectF(x, y, bar_w, bar_h), 4, 4)
        painter.fillPath(path, QBrush(grad))
        painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
        painter.drawPath(path)
        painter.setPen(hex_to_qcolor(self.tokens.text_secondary))
        painter.setFont(QFont(FONT_FAMILY, 10))
        lbl_low = self.tr.t("Less") if self.tr else "Less"
        lbl_high = self.tr.t("More") if self.tr else "More"
        painter.drawText(QRectF(x - 50, y - 5, 40, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, lbl_low)
        painter.drawText(QRectF(x + bar_w + 10, y - 5, 40, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, lbl_high)
        painter.end()


class KeyboardHeatmapWidget(QWidget):
    ASPECT_RATIO = 3.6

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tokens = DARK_TOKENS
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

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.tooltip.set_tokens(tokens)
        self.update()

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
            return QRectF(0, 0, 0, 0), 1.10, "100%"
            
        fmt = "100%"
        if self.parent_ui:
            f_val = self.parent_ui.settings_mgr.get("keyboard_layout")
            if f_val:
                fmt = f_val
        if fmt == "100%":
            ar = 4.4
            max_rx = 1.10
        elif fmt == "60%":
            ar = 3.0
            max_rx = 0.72
        else:
            ar = 3.6
            max_rx = 0.88
        
        current_ratio = w / h
        if current_ratio > ar:
            draw_h = h
            draw_w = draw_h * ar
            offset_x = (w - draw_w) / 2.0
            offset_y = 0.0
        else:
            draw_w = w
            draw_h = draw_w / ar
            offset_x = 0.0
            offset_y = (h - draw_h) / 2.0
        return QRectF(offset_x, offset_y, draw_w, draw_h), max_rx, fmt

    def update_colors(self, color_map):
        self.target_colors = color_map
        if not color_map:
            self.current_colors = {}
            self.transition_start = None
        else:
            if not self.transition_start:
                self.transition_start = QTime.currentTime()

    def add_ripple(self, key_id):
        self.ripples.append({"key_id": key_id, "start_time": QTime.currentTime(), "duration_ms": 300})

    def get_current_key_color(self, key_id):
        base_c = self.current_colors.get(key_id, hex_to_qcolor(self.tokens.key_cold))
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
        
        bg_color = hex_to_qcolor(self.tokens.bg_window)
        painter.fillRect(self.rect(), bg_color)
        
        draw_rect, max_rx, fmt = self._compute_draw_rect()
        if draw_rect.width() < 50 or draw_rect.height() < 20:
            painter.end()
            return
            
        font_size = max(7, int(draw_rect.height() / 25))
        font = QFont(FONT_FAMILY, font_size)
        font.setBold(True)
        painter.setFont(font)
        
        draw_border = bg_color.lightness() > 128
        border_pen = QPen(hex_to_qcolor(self.tokens.border), 0.5) if draw_border else Qt.PenStyle.NoPen
        
        accent_c = hex_to_qcolor(self.tokens.accent)
        hover_pen = QPen(accent_c, 2.0)
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
            
        shadow_c = hex_to_qcolor(self.tokens.key_shadow)
        shadow_c.setAlpha(80 if draw_border else 153)
        hl_parts = self.tokens.key_highlight.strip("rgba()").split(",")
        hl_c = QColor(int(hl_parts[0]), int(hl_parts[1]), int(hl_parts[2]), int(float(hl_parts[3]) * 255))
        
        kb_style = "Mechanical"
        if self.parent_ui and hasattr(self.parent_ui, "settings_mgr"):
            kb_style = self.parent_ui.settings_mgr.get("keyboard_style")
            
        for key in KEYBOARD_LAYOUT:
            if fmt == "TKL" and key["rx"] > 0.86:
                continue
            if fmt == "60%" and (key["ry"] < 0.1 or key["rx"] > 0.71):
                continue
            key_id = key["id"]
            px = draw_rect.x() + (key["rx"] / max_rx) * draw_rect.width()
            py = draw_rect.y() + key["ry"] * draw_rect.height()
            pw = (key["rw"] / max_rx) * draw_rect.width()
            ph = key["rh"] * draw_rect.height()
            key_rect = QRectF(px + 1.5, py + 1.5, pw - 3, ph - 3)
            radius = ph * 0.15
            base_color = self.get_current_key_color(key_id)
            if key_id in active_ripples:
                alpha = active_ripples[key_id]
                r_c = int(base_color.red() * (1 - alpha) + accent_c.red() * alpha)
                g_c = int(base_color.green() * (1 - alpha) + accent_c.green() * alpha)
                b_c = int(base_color.blue() * (1 - alpha) + accent_c.blue() * alpha)
                fill_color = QColor(r_c, g_c, b_c)
            else:
                fill_color = base_color
                if key_id == self._hovered_key_id and not self.heatmap_enabled:
                    hc = hex_to_qcolor(self.tokens.border)
                    fill_color = interpolate_color(base_color, hc, 0.3)
                    
            if kb_style == "Neon Cyberpunk":
                glow_rect = key_rect.adjusted(-2, -2, 2, 2)
                glow_color = QColor(fill_color)
                glow_color.setAlpha(25)
                painter.setBrush(QBrush(glow_color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(glow_rect, radius, radius)
                
                base_c = QColor(fill_color)
                base_c.setAlpha(38)
                painter.setBrush(QBrush(base_c))
                border_color = hover_pen if key_id == self._hovered_key_id else QPen(fill_color, 1.5)
                painter.setPen(border_color)
                painter.drawRoundedRect(key_rect, radius, radius)
            elif kb_style == "Pudding Keycaps":
                shadow_rect = QRectF(key_rect.x(), key_rect.y() + ph * 0.08, key_rect.width(), key_rect.height())
                pudding_base = QColor(fill_color)
                pudding_base.setAlpha(int(255 * 0.90))
                painter.setBrush(QBrush(pudding_base))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(shadow_rect, radius, radius)
                
                top_color = QColor("#1E2130")
                painter.setBrush(QBrush(top_color))
                if key_id == self._hovered_key_id:
                    painter.setPen(hover_pen)
                else:
                    painter.setPen(border_pen)
                painter.drawRoundedRect(key_rect, radius, radius)
            else:
                shadow_rect = QRectF(key_rect.x(), key_rect.y() + ph * 0.08, key_rect.width(), key_rect.height())
                painter.setBrush(QBrush(shadow_c))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(shadow_rect, radius, radius)
                
                painter.setBrush(QBrush(fill_color))
                if key_id == self._hovered_key_id:
                    painter.setPen(hover_pen)
                else:
                    painter.setPen(border_pen)
                painter.drawRoundedRect(key_rect, radius, radius)
                
                hl_rect = QRectF(key_rect.x() + 1, key_rect.y() + 1, key_rect.width() - 2, ph * 0.25)
                painter.setBrush(QBrush(hl_c))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(hl_rect, radius - 1, radius - 1)
            
            if kb_style == "Neon Cyberpunk":
                if self.heatmap_enabled and key_id in self.current_colors:
                    text_color = QColor(fill_color)
                    text_color.setAlpha(255)
                else:
                    text_color = hex_to_qcolor(self.tokens.text_primary)
            else:
                if self.heatmap_enabled and key_id in self.current_colors:
                    c = self.current_colors[key_id]
                    lum = 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()
                    text_color = QColor("#171A23" if lum > 128 else "#E8EAF0")
                else:
                    text_color = hex_to_qcolor(self.tokens.text_primary)
                    
            if key_id in active_ripples:
                text_color = hex_to_qcolor(self.tokens.text_primary)
            painter.setPen(text_color)
            painter.drawText(key_rect, Qt.AlignmentFlag.AlignCenter, key["label"])
            
        if self.flash_overlay_alpha > 0:
            ac = hex_to_qcolor(self.tokens.accent)
            ac.setAlpha(int(self.flash_overlay_alpha))
            painter.fillRect(self.rect(), ac)
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
                bg_c = hex_to_qcolor(self.tokens.bg_window)
                bg_c.setAlphaF(0.92 * alpha_factor)
                brd_c2 = hex_to_qcolor(self.tokens.accent)
                brd_c2.setAlphaF(alpha_factor)
                path = QPainterPath()
                path.addRoundedRect(QRectF(bx, by, banner_w, banner_h), banner_h / 2, banner_h / 2)
                painter.fillPath(path, bg_c)
                painter.setPen(QPen(brd_c2, 1.0))
                painter.drawPath(path)
                painter.setBrush(QBrush(brd_c2))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRectF(bx + 25, by + 25, 12, 20), 6, 6)
                painter.drawRoundedRect(QRectF(bx + 45, by + 25, 12, 20), 6, 6)
                painter.drawRoundedRect(QRectF(bx + 30, by + 30, 22, 10), 2, 2)
                painter.setPen(brd_c2)
                painter.setFont(QFont(FONT_FAMILY, 22, QFont.Weight.Bold))
                painter.drawText(QRectF(bx + 70, by + 10, 200, 30), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "GAMING MODE")
                t2c = hex_to_qcolor(self.tokens.text_secondary)
                t2c.setAlphaF(alpha_factor)
                painter.setPen(t2c)
                painter.setFont(QFont(FONT_FAMILY, 13))
                from_name = self.banner_state["from"]
                painter.drawText(QRectF(bx + 70, by + 40, 200, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"Auto-switched from {from_name}")
            else:
                self.banner_state = None
        painter.end()

    def mouseMoveEvent(self, event):
        if not self.parent_ui or not getattr(self.parent_ui, "db", None):
            super().mouseMoveEvent(event)
            return

        pos = event.position()
        draw_rect, max_rx, fmt = self._compute_draw_rect()
        found_key = None
        
        for key in KEYBOARD_LAYOUT:
            if fmt == "TKL" and key["rx"] > 0.86:
                continue
            px = draw_rect.x() + (key["rx"] / max_rx) * draw_rect.width()
            py = draw_rect.y() + key["ry"] * draw_rect.height()
            pw = (key["rw"] / max_rx) * draw_rect.width()
            ph = key["rh"] * draw_rect.height()
            key_rect = QRectF(px, py, pw, ph)
            if key_rect.contains(pos):
                found_key = key
                break
                
        if found_key:
            key_id = found_key["id"]
            if self._hovered_key_id != key_id:
                self._hovered_key_id = key_id
                
                profile = getattr(self.parent_ui, "current_profile", "Default")
                if not profile:
                    profile = "Default"
                
                key_data = self.parent_ui.db.get_key_stats(profile, key_id)
                count = key_data.get("total", 0)
                
                agg_stats = self.parent_ui.db.get_aggregated_stats(profile)
                all_keys = agg_stats.get("keys", {})
                
                total_all_presses = sum(all_keys.values())
                
                if count <= 0:
                    rank_idx = -1
                else:
                    sorted_keys = sorted(all_keys.items(), key=lambda x: x[1], reverse=True)
                    rank_idx = -1
                    for i, (k, c) in enumerate(sorted_keys):
                        if k == key_id:
                            rank_idx = i + 1
                            break
                            
                self.tooltip.update_info(found_key["label"], count, total_all_presses, rank_idx)
                
            cursor_pos = event.globalPosition().toPoint()
            tt_x = cursor_pos.x() + 15
            tt_y = cursor_pos.y() + 15
            
            screen_geo = QApplication.primaryScreen().availableGeometry()
            if tt_x + self.tooltip.width() > screen_geo.right():
                tt_x = cursor_pos.x() - self.tooltip.width() - 15
            if tt_y + self.tooltip.height() > screen_geo.bottom():
                tt_y = cursor_pos.y() - self.tooltip.height() - 15
                
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

class HourlyChartWidget(QWidget):
    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.hourly_data = {}
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tokens = DARK_TOKENS
        self._tr = tr

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.update()

    def set_data(self, hourly_data):
        self.hourly_data = hourly_data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), hex_to_qcolor(self.tokens.bg_panel))
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
            painter.setFont(QFont(FONT_FAMILY, 13))
            painter.setPen(hex_to_qcolor(self.tokens.text_secondary))
            no_data = self._tr.t("no_data") if self._tr else "No productivity logs recorded yet."
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, no_data)
            painter.end()
            return
        padding_x = 35
        padding_y = 25
        chart_w = w - padding_x * 2
        chart_h = h - padding_y * 2
        painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
        for i in range(1, 4):
            y = h - padding_y - (chart_h * i / 4)
            painter.drawLine(int(padding_x), int(y), int(w - padding_x), int(y))
        painter.drawLine(int(padding_x), int(h - padding_y), int(w - padding_x), int(h - padding_y))
        bar_total_w = chart_w / 24.0
        bar_w = max(3, bar_total_w * 0.4)
        dark_c = hex_to_qcolor(self.tokens.bg_window)
        accent_c = hex_to_qcolor(self.tokens.accent)
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
        painter.setFont(QFont(FONT_FAMILY, 12))
        painter.setPen(hex_to_qcolor(self.tokens.text_secondary))
        for h_val in [0, 6, 12, 18, 23]:
            x = padding_x + h_val * bar_total_w + bar_total_w / 2
            painter.drawText(QRectF(x - 15, h - padding_y + 4, 30, 16), Qt.AlignmentFlag.AlignCenter, f"{h_val}h")
        painter.end()


class MiniCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tokens = DARK_TOKENS

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.setStyleSheet(f"""
            MiniCard {{
                background-color: {tokens.bg_panel};
                border: 1px solid {tokens.border};
                border-radius: 10px;
            }}
        """)
        self.update()


class ModernSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tokens = DARK_TOKENS
        self._thumb_pos = 0.0
        self._anim = QPropertyAnimation(self, b"thumb_pos")
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.stateChanged.connect(self._on_state_change)

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.update()

    @pyqtProperty(float)
    def thumb_pos(self):
        return self._thumb_pos

    def hitButton(self, pos):
        return self.rect().contains(pos)

    @thumb_pos.setter
    def thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()

    def _on_state_change(self, state):
        self._anim.stop()
        self._anim.setEndValue(1.0 if self.isChecked() else 0.0)
        self._anim.start()

    def sizeHint(self):
        return QSize(44, 24)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = 40
        h = 22
        y = (self.height() - h) // 2
        
        bg_color = hex_to_qcolor(self.tokens.accent) if self.isChecked() else hex_to_qcolor(self.tokens.border)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(QRectF(0, y, w, h), h/2, h/2)
        
        thumb_r = h - 4
        thumb_x = 2 + self._thumb_pos * (w - thumb_r - 4)
        thumb_y = y + 2
        
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.drawEllipse(QRectF(thumb_x, thumb_y, thumb_r, thumb_r))
        painter.end()


class TelemetryProgressListWidget(QWidget):
    def __init__(self, parent=None, tr=None):
        super().__init__(parent)
        self.data = []
        self.tokens = DARK_TOKENS
        self._tr = tr
        self.setMinimumHeight(150)
        
    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.update()
        
    def set_data(self, data):
        self.data = data
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        
        if not self.data:
            painter.setFont(QFont(FONT_FAMILY, 12))
            painter.setPen(hex_to_qcolor(self.tokens.text_secondary))
            no_data = self._tr.t("no_data") if self._tr else "No data available."
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, no_data)
            painter.end()
            return
            
        w = self.width()
        h = self.height()
        padding_x = 10
        padding_y = 10
        item_h = (h - 2 * padding_y) / max(5, len(self.data))
        
        max_val = max([count for label, count in self.data]) if self.data else 1
        
        bg_bar_c = hex_to_qcolor(self.tokens.border)
        accent_c = hex_to_qcolor(self.tokens.accent)
        text_primary = hex_to_qcolor(self.tokens.text_primary)
        text_sec = hex_to_qcolor(self.tokens.text_secondary)
        
        font_label = QFont(FONT_FAMILY, 11, QFont.Weight.Medium)
        font_count = QFont(FONT_FAMILY, 10)
        
        for i, (label, count) in enumerate(self.data):
            y = padding_y + i * item_h
            painter.setFont(font_label)
            painter.setPen(text_primary)
            painter.drawText(QRectF(padding_x, y, w * 0.3, item_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(label))
            
            painter.setFont(font_count)
            painter.setPen(text_sec)
            painter.drawText(QRectF(w - padding_x - 50, y, 50, item_h), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(count))
            
            bar_x = padding_x + w * 0.35
            bar_w = w - bar_x - padding_x - 60
            bar_y = y + item_h / 2 - 4
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bg_bar_c))
            painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, 8), 4, 4)
            
            fill_w = (count / max_val) * bar_w if max_val > 0 else 0
            if fill_w > 0:
                painter.setBrush(QBrush(accent_c))
                painter.drawRoundedRect(QRectF(bar_x, bar_y, fill_w, 8), 4, 4)
                
        painter.end()


class IncognitoOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.tokens = DARK_TOKENS
        self.alpha_factor = 0.0
        self.pulse_timer = QTimer(self)
        self.pulse_timer.setInterval(16)
        self.pulse_timer.timeout.connect(self._on_pulse)
        self.is_active = False

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.update()

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


class WelcomeDialog(QDialog):
    def __init__(self, parent=None, tr=None, tokens=None):
        super().__init__(parent)
        self._tr = tr
        self.tokens = tokens or DARK_TOKENS
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(640, 420)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.stacked = QStackedWidget(self)
        self.stacked.setGeometry(30, 30, 580, 310)
        self.stacked.setStyleSheet(f"background: transparent;")
        
        self._build_page1()
        self._build_page2()
        self._build_page3()
        self._build_page4()
        
        self.back_btn = QPushButton(tr.t("back") if tr else "\u2190 Back", self)
        self.back_btn.setGeometry(30, 370, 90, 32)
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.setVisible(False)
        
        self.next_btn = QPushButton(tr.t("next") if tr else "Next \u2192", self)
        self.next_btn.setGeometry(520, 370, 90, 32)
        self.next_btn.clicked.connect(self._go_next)
        
        self._current_page = 0
        self.profile_name_entry = None
        self.set_tokens(self.tokens)
        
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.move((geo.width() - 640) // 2, (geo.height() - 420) // 2)

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.back_btn.setStyleSheet(f"border: 1px solid {self.tokens.border}; color: {self.tokens.text_secondary}; background: transparent; border-radius: 4px;")
        self.next_btn.setStyleSheet(f"border: 1px solid {self.tokens.accent}; color: {self.tokens.accent}; background: transparent; border-radius: 4px; font-weight: bold;")
        self.update()

    def _make_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        return page

    def _build_page1(self):
        page = self._make_page()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo = QLabel("TYPETRACE")
        self.logo.setStyleSheet(f"color: {self.tokens.accent}; font-size: 36px; font-weight: bold; background: transparent;")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo)
        self.sub = QLabel(self._tr.t("app_subtitle") if self._tr else "PRIVACY-FOCUSED KEYSTROKE ANALYZER")
        self.sub.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 13px; background: transparent;")
        self.sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub)
        layout.addSpacing(30)
        self.body1 = QLabel(self._tr.t("welcome_page1_body") if self._tr else "Welcome, let\u2019s take a quick tour \u2192")
        self.body1.setStyleSheet(f"color: {self.tokens.text_primary}; font-size: 16px; background: transparent;")
        self.body1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.body1)
        self.stacked.addWidget(page)

    def _build_page2(self):
        page = self._make_page()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title2 = QLabel(self._tr.t("welcome_page2_title") if self._tr else "Keyboard Heatmap")
        self.title2.setStyleSheet(f"color: {self.tokens.accent}; font-size: 22px; font-weight: bold; background: transparent;")
        self.title2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title2)
        layout.addSpacing(15)
        self.body2 = QLabel(self._tr.t("welcome_page2_body") if self._tr else "See which keys you press the most with a color-coded heatmap.")
        self.body2.setStyleSheet(f"color: {self.tokens.text_primary}; font-size: 14px; background: transparent;")
        self.body2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body2.setWordWrap(True)
        layout.addWidget(self.body2)
        self.stacked.addWidget(page)

    def _build_page3(self):
        page = self._make_page()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title3 = QLabel(self._tr.t("welcome_page3_title") if self._tr else "Three Powerful Tabs")
        self.title3.setStyleSheet(f"color: {self.tokens.accent}; font-size: 22px; font-weight: bold; background: transparent;")
        self.title3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title3)
        layout.addSpacing(15)
        self.lbls3 = []
        for key in ["welcome_page3_body_config", "welcome_page3_body_telemetry", "welcome_page3_body_chart"]:
            lbl = QLabel("\u2022 " + (self._tr.t(key) if self._tr else key))
            lbl.setStyleSheet(f"color: {self.tokens.text_primary}; font-size: 14px; background: transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)
            self.lbls3.append(lbl)
        self.stacked.addWidget(page)

    def _build_page4(self):
        page = self._make_page()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title4 = QLabel(self._tr.t("welcome_page4_title") if self._tr else "You\u2019re all set!")
        self.title4.setStyleSheet(f"color: {self.tokens.accent}; font-size: 22px; font-weight: bold; background: transparent;")
        self.title4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title4)
        layout.addSpacing(15)
        self.body4 = QLabel(self._tr.t("welcome_page4_body") if self._tr else "Enter a default profile name:")
        self.body4.setStyleSheet(f"color: {self.tokens.text_primary}; font-size: 14px; background: transparent;")
        self.body4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.body4)
        self.profile_name_entry = QLineEdit("Default")
        self.profile_name_entry.setFixedWidth(200)
        self.profile_name_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.profile_name_entry, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        self.start_btn = QPushButton(self._tr.t("welcome_start") if self._tr else "Start TypeTrace \u2192")
        self.start_btn.setFixedSize(200, 40)
        self.start_btn.setStyleSheet(f"border: 2px solid {self.tokens.accent}; color: {self.tokens.accent}; background: transparent; font-size: 15px; font-weight: bold; border-radius: 6px;")
        self.start_btn.clicked.connect(self.accept)
        layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.stacked.addWidget(page)

    def get_profile_name(self):
        if self.profile_name_entry:
            return self.profile_name_entry.text().strip() or "Default"
        return "Default"

    def _go_next(self):
        if self._current_page < 3:
            self._current_page += 1
            self.stacked.setCurrentIndex(self._current_page)
            self.back_btn.setVisible(self._current_page > 0)
            if self._current_page == 3:
                self.next_btn.setVisible(False)

    def _go_back(self):
        if self._current_page > 0:
            self._current_page -= 1
            self.stacked.setCurrentIndex(self._current_page)
            self.back_btn.setVisible(self._current_page > 0)
            self.next_btn.setVisible(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        painter.fillPath(path, hex_to_qcolor(self.tokens.bg_window))
        painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
        painter.drawPath(path)
        dot_y = self.height() - 20
        dot_cx = self.width() / 2
        for i in range(4):
            x = dot_cx - 24 + i * 16
            if i == self._current_page:
                painter.setBrush(QBrush(hex_to_qcolor(self.tokens.accent)))
            else:
                painter.setBrush(QBrush(hex_to_qcolor(self.tokens.border)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, dot_y), 4, 4)
        painter.end()


class ExportDialog(QDialog):
    def __init__(self, parent=None, db=None, viewing_profile="Default", tr=None, tokens=None):
        super().__init__(parent)
        self._db = db
        self._profile = viewing_profile
        self._tr = tr
        self.tokens = tokens or DARK_TOKENS
        self.setWindowTitle(tr.t("export_title") if tr else "Export Data")
        self.setFixedSize(480, 380)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        self.fmt_lbl = QLabel(tr.t("export_format") if tr else "Format")
        self.fmt_lbl.setStyleSheet("font-size: 11px; font-weight: bold;")
        layout.addWidget(self.fmt_lbl)
        
        self.fmt_group = QButtonGroup(self)
        self.rb_csv = QRadioButton(tr.t("export_csv_desc") if tr else "CSV")
        self.rb_json = QRadioButton(tr.t("export_json_desc") if tr else "JSON")
        self.rb_both = QRadioButton(tr.t("export_both_desc") if tr else "Both")
        self.rb_csv.setChecked(True)
        self.fmt_group.addButton(self.rb_csv, 0)
        self.fmt_group.addButton(self.rb_json, 1)
        self.fmt_group.addButton(self.rb_both, 2)
        layout.addWidget(self.rb_csv)
        layout.addWidget(self.rb_json)
        layout.addWidget(self.rb_both)
        
        self.scope_lbl = QLabel(tr.t("export_scope") if tr else "Scope")
        self.scope_lbl.setStyleSheet("font-size: 11px; font-weight: bold;")
        layout.addWidget(self.scope_lbl)
        
        self.scope_all = QRadioButton(tr.t("export_all_profiles") if tr else "All profiles")
        self.scope_current = QRadioButton(tr.t("export_current_profile") if tr else "Current profile only")
        self.scope_current.setChecked(True)
        self.scope_group = QButtonGroup(self)
        self.scope_group.addButton(self.scope_all, 0)
        self.scope_group.addButton(self.scope_current, 1)
        layout.addWidget(self.scope_all)
        layout.addWidget(self.scope_current)
        
        self.inc_history = QCheckBox(tr.t("export_include_history") if tr else "Include session history")
        self.inc_history.setChecked(True)
        layout.addWidget(self.inc_history)
        self.inc_bigrams = QCheckBox(tr.t("export_include_bigrams") if tr else "Include bigram data")
        self.inc_bigrams.setChecked(True)
        layout.addWidget(self.inc_bigrams)
        self.inc_bursts = QCheckBox(tr.t("export_include_bursts") if tr else "Include burst records")
        self.inc_bursts.setChecked(True)
        layout.addWidget(self.inc_bursts)
        
        dest_row = QHBoxLayout()
        self.dest_lbl = QLabel(tr.t("export_destination") if tr else "Destination")
        self.dest_lbl.setStyleSheet("font-size: 11px; font-weight: bold;")
        dest_row.addWidget(self.dest_lbl)
        self.dest_entry = QLineEdit(os.path.expanduser("~/TypeTrace_export"))
        dest_row.addWidget(self.dest_entry)
        self.browse_btn = QPushButton(tr.t("export_browse") if tr else "Browse\u2026")
        self.browse_btn.setFixedWidth(70)
        self.browse_btn.clicked.connect(self._browse)
        dest_row.addWidget(self.browse_btn)
        layout.addLayout(dest_row)
        
        self.export_btn = QPushButton(tr.t("export_now") if tr else "Export Now")
        self.export_btn.setFixedHeight(40)
        self.export_btn.clicked.connect(self._do_export)
        layout.addWidget(self.export_btn)
        
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("font-size: 12px;")
        self.status_lbl.setWordWrap(True)
        layout.addWidget(self.status_lbl)
        
        self.open_btn = QPushButton(tr.t("open_folder") if tr else "Open Folder")
        self.open_btn.setFixedHeight(32)
        self.open_btn.setVisible(False)
        self.open_btn.clicked.connect(self._open_folder)
        layout.addWidget(self.open_btn)
        self._exported_path = ""
        self.set_tokens(self.tokens)

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.setStyleSheet(f"background-color: {self.tokens.bg_window};")
        self.fmt_lbl.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 11px; font-weight: bold;")
        self.scope_lbl.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 11px; font-weight: bold;")
        self.dest_lbl.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 11px; font-weight: bold;")
        self.export_btn.setStyleSheet(f"border: 2px solid {self.tokens.accent}; color: {self.tokens.accent}; font-size: 14px; font-weight: bold;")
        self.update()

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select Export Folder", self.dest_entry.text())
        if path:
            self.dest_entry.setText(path)

    def _do_export(self):
        dest = self.dest_entry.text().strip()
        if not dest:
            return
        os.makedirs(dest, exist_ok=True)
        fmt_id = self.fmt_group.checkedId()
        profiles_to_export = []
        if self.scope_all.isChecked():
            profiles_to_export = self._db.get_profiles()
        else:
            profiles_to_export = [self._profile]
        try:
            for pname in profiles_to_export:
                aggregated = self._db.get_aggregated_stats(pname)
                export_data = {"keys": aggregated.get("keys", {}), "combinations": aggregated.get("combinations", {})}
                if self.inc_bigrams.isChecked():
                    export_data["bigrams"] = aggregated.get("bigrams", {})
                if self.inc_bursts.isChecked():
                    export_data["burst_records"] = self._db.get_burst_records(pname)
                if self.inc_history.isChecked():
                    profile_data = self._db.get_stats_for_profile(pname)
                    export_data["hourly"] = profile_data.get("hourly", {})
                safe_name = pname.replace(" ", "_").lower()
                if fmt_id == 0 or fmt_id == 2:
                    csv_path = os.path.join(dest, f"typetrace_{safe_name}.csv")
                    utils.export_stats_to_csv(csv_path, export_data)
                if fmt_id == 1 or fmt_id == 2:
                    json_path = os.path.join(dest, f"typetrace_{safe_name}.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(export_data, f, indent=4)
            success_text = self._tr.t("export_success") if self._tr else "\u2713 Exported to"
            self.status_lbl.setText(f"{success_text} {dest}")
            self.status_lbl.setStyleSheet(f"color: {self.tokens.accent}; font-size: 12px;")
            self._exported_path = dest
            self.open_btn.setVisible(True)
        except Exception as e:
            err_text = self._tr.t("export_error") if self._tr else "\u2717 Error:"
            self.status_lbl.setText(f"{err_text} {e}")
            self.status_lbl.setStyleSheet("color: #FF3B3B; font-size: 12px;")

    def _open_folder(self):
        if self._exported_path and os.path.isdir(self._exported_path):
            os.startfile(self._exported_path)


class ProcessMappingDialog(QDialog):
    def __init__(self, parent, db, tr=None, tokens=None):
        super().__init__(parent)
        self.db = db
        self._tr = tr
        self.tokens = tokens or DARK_TOKENS
        self.setWindowTitle("Configure Process Mappings")
        self.setFixedSize(500, 550)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.title_lbl = QLabel("Smart Process Auto-switching")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_lbl)
        
        self.desc_lbl = QLabel("Map background process names (.exe) to specific profiles.")
        self.desc_lbl.setWordWrap(True)
        layout.addWidget(self.desc_lbl)
        
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
        self.add_btn = QPushButton("Add")
        self.add_btn.setFixedWidth(50)
        self.add_btn.clicked.connect(self._add_mapping)
        add_row.addWidget(self.add_btn)
        layout.addLayout(add_row)
        
        self.mapping_title = QLabel("Custom Mappings")
        layout.addWidget(self.mapping_title)
        
        self.mapping_scroll = QScrollArea()
        self.mapping_scroll.setWidgetResizable(True)
        self.mapping_container = QWidget()
        self.mapping_layout = QVBoxLayout(self.mapping_container)
        self.mapping_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mapping_layout.setSpacing(4)
        self.mapping_layout.setContentsMargins(4, 4, 4, 4)
        self.mapping_scroll.setWidget(self.mapping_container)
        layout.addWidget(self.mapping_scroll)
        
        self.recent_title = QLabel("Recent Processes")
        layout.addWidget(self.recent_title)
        
        self.recent_scroll = QScrollArea()
        self.recent_scroll.setWidgetResizable(True)
        self.recent_container = QWidget()
        self.recent_layout = QVBoxLayout(self.recent_container)
        self.recent_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.recent_layout.setSpacing(4)
        self.recent_layout.setContentsMargins(4, 4, 4, 4)
        self.recent_scroll.setWidget(self.recent_container)
        layout.addWidget(self.recent_scroll)
        
        self._load_mappings()
        self._load_recent()
        self.set_tokens(self.tokens)

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.setStyleSheet(f"background-color: {self.tokens.bg_window};")
        self.title_lbl.setStyleSheet(f"color: {self.tokens.accent}; font-size: 15px; font-weight: bold; background: transparent;")
        self.desc_lbl.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 12px; background: transparent;")
        self.mapping_title.setStyleSheet(f"color: {self.tokens.text_primary}; font-size: 13px; font-weight: bold; background: transparent;")
        self.recent_title.setStyleSheet(f"color: {self.tokens.accent}; font-size: 13px; font-weight: bold; background: transparent;")
        self.add_btn.setStyleSheet(f"background: {self.tokens.accent}; color: {self.tokens.bg_window}; border: none;")
        self.mapping_scroll.setStyleSheet(f"background: {self.tokens.bg_panel}; border: 1px solid {self.tokens.border}; border-radius: 8px;")
        self.recent_scroll.setStyleSheet(f"background: {self.tokens.bg_panel}; border: 1px solid {self.tokens.border}; border-radius: 8px;")
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
            lbl = QLabel(f"{proc}  \u27a1  {prof}")
            lbl.setStyleSheet(f"color: {self.tokens.text_primary}; font-size: 12px; font-family: Consolas; font-weight: bold; background: transparent;")
            row.addWidget(lbl)
            row.addStretch()
            del_btn = QPushButton("Remove")
            del_btn.setStyleSheet("background: #A63A50; color: #FFFFFF; border: none;")
            del_btn.setFixedWidth(70)
            del_btn.clicked.connect(lambda checked, p=proc: self._delete_mapping(p))
            row.addWidget(del_btn)
            container = QWidget()
            container.setLayout(row)
            container.setStyleSheet(f"background-color: {self.tokens.bg_input}; border: 1px solid {self.tokens.border}; border-radius: 6px;")
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
            lbl.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 12px; font-style: italic; background: transparent;")
            row.addWidget(lbl)
            row.addStretch()
            g_btn = QPushButton("\u2192 Gaming")
            g_btn.setFixedWidth(75)
            g_btn.clicked.connect(lambda checked, p=proc: self._quick_map(p, "Gaming"))
            row.addWidget(g_btn)
            d_btn = QPushButton("\u2192 Desktop")
            d_btn.setFixedWidth(75)
            d_btn.clicked.connect(lambda checked, p=proc: self._quick_map(p, "Desktop"))
            row.addWidget(d_btn)
            container = QWidget()
            container.setLayout(row)
            container.setStyleSheet(f"background-color: {self.tokens.bg_input}; border: 1px solid {self.tokens.border}; border-radius: 6px;")
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
    def __init__(self, parent, tr=None, tokens=None):
        super().__init__(parent)
        self._tr = tr
        self.tokens = tokens or DARK_TOKENS
        title = tr.t("about_title") if tr else "About TypeTrace"
        self.setWindowTitle(title)
        self.setFixedSize(380, 280)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.logo = QLabel("TYPETRACE")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo)
        
        self.version = QLabel(f"v{APP_VERSION}")
        self.version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.version)
        
        desc_text = tr.t("about_desc") if tr else "Privacy-focused keystroke analytics.\nAll data stored locally on your machine."
        self.desc = QLabel(desc_text)
        self.desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.desc)
        
        self.sep = QFrame()
        self.sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(self.sep)
        
        self.github_btn = QPushButton("\u2605 GitHub Repository")
        self.github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.github_btn.clicked.connect(lambda: webbrowser.open(APP_GITHUB))
        layout.addWidget(self.github_btn)
        
        footer_text = tr.t("about_footer") if tr else "Made with \u2328\ufe0f by TypeTrace"
        self.footer = QLabel(footer_text)
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.footer)
        
        self.set_tokens(self.tokens)

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.setStyleSheet(f"background-color: {self.tokens.bg_window};")
        self.logo.setStyleSheet(f"color: {self.tokens.accent}; font-size: 28px; font-weight: bold; background: transparent;")
        self.version.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 12px; background: transparent;")
        self.desc.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 13px; background: transparent;")
        self.sep.setStyleSheet(f"background-color: {self.tokens.border}; max-height: 1px;")
        self.github_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {self.tokens.accent}; border: none; font-size: 13px; font-weight: bold; padding: 8px; }} QPushButton:hover {{ color: {self.tokens.text_primary}; }}")
        self.footer.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 9px; background: transparent;")




class TypeTraceUI(QMainWindow):
    def __init__(self, db, tracker, shutdown_callback=None):
        if not QApplication.instance():
            import sys
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()
            
        super().__init__()
        self.db = db
        self.tracker = tracker
        self.shutdown_callback = shutdown_callback
        self._force_quit = False
        self.settings_mgr = SettingsManager()
        self.tr = Translator(self.settings_mgr.get("language"))
        
        theme_str = self.settings_mgr.get("theme")
        self.is_dark_mode = (theme_str == "dark")
        self.current_tokens = replace(DARK_TOKENS if self.is_dark_mode else LIGHT_TOKENS)
        self.current_tokens.accent = self.settings_mgr.get("accent_color")
        
        self.is_compact = self.settings_mgr.get("compact_mode")
        self.current_profile = "Total"
        
        self.event_queue = queue.Queue()
        self.tracker.ui_update_callback = self._on_tracker_event
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_queue)
        self.timer.start(16)
        
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._on_anim_tick)
        self.anim_timer.start(30)
        
        self.telemetry_cards = []
        
        self._init_ui()
        self._apply_theme(self.current_tokens)
        
        if not self.settings_mgr.get("welcome_shown"):
            QTimer.singleShot(500, self._show_welcome)

    def _show_welcome(self):
        dlg = WelcomeDialog(self, self.tr, self.current_tokens)
        dlg.exec()
        pname = dlg.get_profile_name()
        if pname not in self.db.get_profiles() and pname != "Total":
            self.db.add_profile(pname)
            self.profile_combo.addItem(pname)
            self.profile_combo.setCurrentText(pname)
        self.settings_mgr.set("welcome_shown", True)

    def _init_ui(self):
        self.setWindowTitle("TypeTrace")
        self.resize(900, 600)
        self.setMinimumSize(800, 500)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.header = HeaderWidget(self, self.tr)
        self.header.compact_btn.clicked.connect(self.toggle_compact_mode)
        main_layout.addWidget(self.header)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        self.tab_home = QWidget()
        home_layout = QVBoxLayout(self.tab_home)
        home_layout.setContentsMargins(20, 20, 20, 20)
        home_layout.setSpacing(15)
        
        self.dash_widget = QWidget()
        dash_layout = QHBoxLayout(self.dash_widget)
        dash_layout.setContentsMargins(0, 0, 0, 0)
        self.main_stats_lbl = QLabel("APM: 0 | Parole: 0")
        self.main_stats_lbl.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        dash_layout.addWidget(self.main_stats_lbl)
        dash_layout.addStretch()
        dash_layout.addWidget(QLabel("Mostra Heatmap"))
        self.heatmap_toggle = ModernSwitch()
        self.heatmap_toggle.toggled.connect(self._on_heatmap_toggle)
        dash_layout.addWidget(self.heatmap_toggle)
        
        home_layout.addWidget(self.dash_widget)
        self.header.settings_btn.clicked.connect(self._toggle_settings_drawer)
        
        self.heatmap_container = QWidget()
        hc_layout = QVBoxLayout(self.heatmap_container)
        hc_layout.setContentsMargins(0, 0, 0, 0)
        hc_layout.setSpacing(15)
        
        self.heatmap = KeyboardHeatmapWidget(self)
        self.heatmap.parent_ui = self
        self.heatmap.set_theme(self.settings_mgr.get("keyboard_theme"))
        hc_layout.addWidget(self.heatmap, stretch=1)
        self.legend = LegendBarWidget(self, self.tr)
        self.legend.set_theme(self.settings_mgr.get("keyboard_theme"))
        hc_layout.addWidget(self.legend)
        self.heatmap_toggle.setChecked(True)
        
        home_layout.addWidget(self.heatmap_container, stretch=1)
        
        self.tab_widget.addTab(self.tab_home, self.tr.t("tab_keyboard"))
        
        self.tab_telemetry = QScrollArea()
        self.tab_telemetry.setWidgetResizable(True)
        self.tab_telemetry.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        tel_container = QWidget()
        tel_layout = QVBoxLayout(tel_container)
        tel_layout.setContentsMargins(20, 20, 20, 20)
        tel_layout.setSpacing(20)
        
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        self.telemetry_labels = []
        self.telemetry_sub_labels = []
        
        self.session_card = MiniCard()
        sc_layout = QVBoxLayout(self.session_card)
        sc_lbl = QLabel(self.tr.t("telemetry_session") if self.tr else "Estimated Words")
        sc_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        sc_sub = QLabel("Totale parole stimate (tasti / 5)")
        sc_sub.setFont(QFont(FONT_FAMILY, 10))
        sc_sub.setStyleSheet(f"color: {self.current_tokens.text_secondary};")
        self.telemetry_sub_labels.append(sc_sub)
        self.session_val = QLabel("0")
        self.session_val.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        sc_layout.addWidget(sc_lbl)
        sc_layout.addWidget(sc_sub)
        sc_layout.addSpacing(10)
        sc_layout.addWidget(self.session_val)
        sc_layout.addStretch()
        cards_layout.addWidget(self.session_card)
        
        self.peak_card = MiniCard()
        pc_layout = QVBoxLayout(self.peak_card)
        pc_lbl = QLabel("Fastest Burst")
        pc_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        pc_sub = QLabel("Record APM (tracciato nel database)")
        pc_sub.setFont(QFont(FONT_FAMILY, 10))
        pc_sub.setStyleSheet(f"color: {self.current_tokens.text_secondary};")
        self.telemetry_sub_labels.append(pc_sub)
        self.peak_val = QLabel("0 APM (0s)")
        self.peak_val.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        pc_layout.addWidget(pc_lbl)
        pc_layout.addWidget(pc_sub)
        pc_layout.addSpacing(10)
        pc_layout.addWidget(self.peak_val)
        pc_layout.addStretch()
        cards_layout.addWidget(self.peak_card)
        
        self.top_key_card = MiniCard()
        tkc_layout = QVBoxLayout(self.top_key_card)
        tkc_lbl = QLabel("Most Used Key")
        tkc_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        tkc_sub = QLabel("Tasto più premuto in assoluto")
        tkc_sub.setFont(QFont(FONT_FAMILY, 10))
        tkc_sub.setStyleSheet(f"color: {self.current_tokens.text_secondary};")
        self.telemetry_sub_labels.append(tkc_sub)
        self.top_key_val = QLabel("-")
        self.top_key_val.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        tkc_layout.addWidget(tkc_lbl)
        tkc_layout.addWidget(tkc_sub)
        tkc_layout.addSpacing(10)
        tkc_layout.addWidget(self.top_key_val)
        tkc_layout.addStretch()
        cards_layout.addWidget(self.top_key_card)
        
        self.telemetry_cards = [self.session_card, self.peak_card, self.top_key_card]
        tel_layout.addLayout(cards_layout)
        
        self.chart_card = MiniCard()
        cc_layout = QVBoxLayout(self.chart_card)
        cc_lbl = QLabel("Activity Timeline")
        cc_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        cc_sub = QLabel("Eventi orari")
        cc_sub.setFont(QFont(FONT_FAMILY, 10))
        cc_sub.setStyleSheet(f"color: {self.current_tokens.text_secondary};")
        self.telemetry_sub_labels.append(cc_sub)
        self.chart_widget = HourlyChartWidget(self, self.tr)
        cc_layout.addWidget(cc_lbl)
        cc_layout.addWidget(cc_sub)
        cc_layout.addSpacing(10)
        cc_layout.addWidget(self.chart_widget, stretch=1)
        tel_layout.addWidget(self.chart_card, stretch=1)
        self.telemetry_cards.append(self.chart_card)
        
        lists_layout = QHBoxLayout()
        lists_layout.setSpacing(20)
        
        self.combos_card = MiniCard()
        cb_layout = QVBoxLayout(self.combos_card)
        cb_lbl = QLabel("Top Combinations")
        cb_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        cb_sub = QLabel("Scorciatoie più usate")
        cb_sub.setFont(QFont(FONT_FAMILY, 10))
        cb_sub.setStyleSheet(f"color: {self.current_tokens.text_secondary};")
        self.telemetry_sub_labels.append(cb_sub)
        self.combos_list = TelemetryProgressListWidget(self, self.tr)
        cb_layout.addWidget(cb_lbl)
        cb_layout.addWidget(cb_sub)
        cb_layout.addSpacing(10)
        cb_layout.addWidget(self.combos_list, stretch=1)
        lists_layout.addWidget(self.combos_card, stretch=1)
        
        self.bigrams_card = MiniCard()
        bg_layout = QVBoxLayout(self.bigrams_card)
        bg_lbl = QLabel("Top Bigrams")
        bg_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        bg_sub = QLabel("Coppie di tasti")
        bg_sub.setFont(QFont(FONT_FAMILY, 10))
        bg_sub.setStyleSheet(f"color: {self.current_tokens.text_secondary};")
        self.telemetry_sub_labels.append(bg_sub)
        self.bigrams_list = TelemetryProgressListWidget(self, self.tr)
        bg_layout.addWidget(bg_lbl)
        bg_layout.addWidget(bg_sub)
        bg_layout.addSpacing(10)
        bg_layout.addWidget(self.bigrams_list, stretch=1)
        lists_layout.addWidget(self.bigrams_card, stretch=1)
        
        self.telemetry_cards.extend([self.combos_card, self.bigrams_card])
        
        self.telemetry_labels.extend([sc_lbl, pc_lbl, tkc_lbl, cc_lbl, cb_lbl, bg_lbl])
        tel_layout.addLayout(lists_layout)
        
        self.tab_telemetry.setWidget(tel_container)
        self.tab_widget.addTab(self.tab_telemetry, self.tr.t("tab_telemetry"))
        
        self._create_config_tab()
        self._create_overlay_tab()
        
        self.overlay = IncognitoOverlay(self)
        self.overlay.resize(self.size())
        
        self.sync_settings()
        
        self.compact_restore_btn = QPushButton("✖", self)
        self.compact_restore_btn.setFixedSize(30, 30)
        self.compact_restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.compact_restore_btn.clicked.connect(self.toggle_compact_mode)
        self.compact_restore_btn.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.resize(self.size())
        if hasattr(self, "compact_restore_btn"):
            self.compact_restore_btn.move(self.width() - 40, 10)
        if hasattr(self, "settings_drawer") and self.settings_drawer.isVisible():
            target_width = 380
            self.settings_drawer.setGeometry(self.width() - target_width, 0, target_width, self.height())

    def _create_config_tab(self):
        self.settings_drawer = QScrollArea(self)
        self.settings_drawer.setWidgetResizable(True)
        self.settings_drawer.setFrameShape(QFrame.Shape.NoFrame)
        self.settings_drawer.setStyleSheet("background: transparent;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        drawer_top_bar = QHBoxLayout()
        drawer_top_bar.addStretch()
        btn_close_drawer = QPushButton("❌ Chiudi")
        btn_close_drawer.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        btn_close_drawer.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close_drawer.clicked.connect(self._toggle_settings_drawer)
        btn_close_drawer.setStyleSheet(f"background-color: transparent; color: {self.current_tokens.text_secondary}; border: none;")
        drawer_top_bar.addWidget(btn_close_drawer)
        layout.addLayout(drawer_top_bar)
        
        app_card = MiniCard()
        app_layout = QVBoxLayout(app_card)
        app_layout.setSpacing(15)
        app_lbl = QLabel("Appearance")
        app_lbl.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        app_layout.addWidget(app_lbl)
        
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Language:"))
        self.lang_combo = NoScrollComboBox()
        self.lang_combo.addItems(["en", "it"])
        self.lang_combo.currentTextChanged.connect(self._on_lang_change)
        lang_row.addWidget(self.lang_combo)
        app_layout.addLayout(lang_row)
        
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("UI Theme:"))
        self.theme_combo = NoScrollComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_change)
        theme_row.addWidget(self.theme_combo)
        app_layout.addLayout(theme_row)
        
        kb_theme_row = QHBoxLayout()
        kb_theme_row.addWidget(QLabel("Heatmap Theme:"))
        self.kb_theme_combo = NoScrollComboBox()
        self.kb_theme_combo.addItems(list(KEYBOARD_THEMES.keys()))
        self.kb_theme_combo.currentTextChanged.connect(self._on_kb_theme_change)
        kb_theme_row.addWidget(self.kb_theme_combo)
        app_layout.addLayout(kb_theme_row)
        
        kb_style_row = QHBoxLayout()
        kb_style_row.addWidget(QLabel("Keyboard Style:"))
        self.kb_style_combo = NoScrollComboBox()
        self.kb_style_combo.addItems(["Mechanical", "Neon Cyberpunk", "Pudding Keycaps"])
        self.kb_style_combo.currentTextChanged.connect(self._on_kb_style_change)
        kb_style_row.addWidget(self.kb_style_combo)
        app_layout.addLayout(kb_style_row)
        
        kb_layout_row = QHBoxLayout()
        kb_layout_row.addWidget(QLabel("Keyboard Layout:"))
        self.kb_layout_combo = NoScrollComboBox()
        self.kb_layout_combo.addItems(["100%", "TKL", "60%"])
        self.kb_layout_combo.currentTextChanged.connect(self._on_kb_layout_change)
        kb_layout_row.addWidget(self.kb_layout_combo)
        app_layout.addLayout(kb_layout_row)
        
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Accent Color:"))
        self.color_btn = QPushButton("")
        self.color_btn.setFixedSize(24, 24)
        self.color_btn.clicked.connect(self._pick_color)
        color_row.addWidget(self.color_btn)
        color_row.addStretch()
        app_layout.addLayout(color_row)
        
        layout.addWidget(app_card)
        
        beh_card = MiniCard()
        beh_layout = QVBoxLayout(beh_card)
        beh_layout.setSpacing(15)
        beh_lbl = QLabel("Behavior")
        beh_lbl.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        beh_layout.addWidget(beh_lbl)
        
        cmp_row = QHBoxLayout()
        cmp_row.addWidget(QLabel("Enable Compact Mode"))
        cmp_row.addStretch()
        self.compact_cb = ModernSwitch()
        self.compact_cb.toggled.connect(self._on_compact_change)
        cmp_row.addWidget(self.compact_cb)
        beh_layout.addLayout(cmp_row)
        
        startup_row = QHBoxLayout()
        startup_row.addWidget(QLabel("Start with Windows"))
        startup_row.addStretch()
        self.startup_cb = ModernSwitch()
        self.startup_cb.toggled.connect(self._on_startup_change)
        startup_row.addWidget(self.startup_cb)
        beh_layout.addLayout(startup_row)
        
        layout.addWidget(beh_card)
        
        data_card = MiniCard()
        data_layout = QVBoxLayout(data_card)
        data_layout.setSpacing(15)
        data_lbl = QLabel("Data & Profiles")
        data_lbl.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        data_layout.addWidget(data_lbl)
        
        prof_row = QHBoxLayout()
        prof_row.addWidget(QLabel("Active Profile:"))
        self.profile_combo = NoScrollComboBox()
        self.profile_combo.setMinimumWidth(200)
        self.profile_combo.addItems(self.db.get_profiles())
        self.profile_combo.setCurrentText(self.current_profile)
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed_ui)
        prof_row.addWidget(self.profile_combo)
        prof_row.addStretch()
        data_layout.addLayout(prof_row)
        
        self.smart_map_btn = QPushButton("Configure Auto-Switch")
        self.smart_map_btn.clicked.connect(self._open_smart_map)
        data_layout.addWidget(self.smart_map_btn)
        
        self.export_btn = QPushButton("Export Data...")
        self.export_btn.clicked.connect(self._open_export)
        data_layout.addWidget(self.export_btn)
        
        self.reset_btn = QPushButton("Reset Profile Stats")
        self.reset_btn.setStyleSheet("color: #FF3B3B; font-weight: bold;")
        self.reset_btn.clicked.connect(self._reset_stats)
        data_layout.addWidget(self.reset_btn)
        
        layout.addWidget(data_card)
        
        self.settings_drawer.setWidget(container)
        self.config_cards = [app_card, beh_card, data_card]
        
        self.settings_drawer.setStyleSheet(f"QScrollArea {{ background-color: {self.current_tokens.bg_panel}; border-left: 2px solid {self.current_tokens.border}; }}")
        self.settings_drawer.hide()
        self.settings_drawer.raise_()
        
    def _create_overlay_tab(self):
        self.tab_overlay = QScrollArea()
        self.tab_overlay.setWidgetResizable(True)
        self.tab_overlay.setFrameShape(QFrame.Shape.NoFrame)
        self.tab_overlay.setStyleSheet("background: transparent;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.btn_toggle_overlay = QPushButton("Mostra Widget Fluttuante")
        self.btn_toggle_overlay.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        self.btn_toggle_overlay.clicked.connect(self._on_overlay_toggle)
        layout.addWidget(self.btn_toggle_overlay)
        
        metrics_card = MiniCard()
        metrics_layout = QVBoxLayout(metrics_card)
        metrics_layout.setSpacing(15)
        metrics_lbl = QLabel("Overlay Metrics")
        metrics_lbl.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        metrics_layout.addWidget(metrics_lbl)
        
        self.overlay_show_apm = ModernSwitch()
        self.overlay_show_wpm = ModernSwitch()
        self.overlay_show_peak = ModernSwitch()
        self.overlay_show_profile = ModernSwitch()
        
        toggles = [
            ("Show APM", self.overlay_show_apm, "overlay_show_apm"),
            ("Show WPM", self.overlay_show_wpm, "overlay_show_wpm"),
            ("Show Peak APM", self.overlay_show_peak, "overlay_show_peak"),
            ("Show Profile", self.overlay_show_profile, "overlay_show_profile")
        ]
        
        for text, cb, key in toggles:
            row = QHBoxLayout()
            lbl = QLabel(text)
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            lbl.mousePressEvent = lambda e, c=cb: c.toggle()
            row.addWidget(lbl)
            row.addStretch()
            cb.toggled.connect(lambda checked, k=key: self._on_overlay_setting_change(k, checked))
            row.addWidget(cb)
            metrics_layout.addLayout(row)
            
        layout.addWidget(metrics_card)
        
        app_card = MiniCard()
        app_layout = QVBoxLayout(app_card)
        app_layout.setSpacing(15)
        app_lbl = QLabel("Overlay Appearance")
        app_lbl.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        app_layout.addWidget(app_lbl)
        
        from PyQt6.QtWidgets import QSlider
        
        op_row = QHBoxLayout()
        op_row.addWidget(QLabel("Opacity:"))
        self.overlay_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.overlay_opacity_slider.setRange(20, 100)
        self.overlay_opacity_slider.valueChanged.connect(self._on_overlay_opacity_change)
        op_row.addWidget(self.overlay_opacity_slider)
        app_layout.addLayout(op_row)
        
        sc_row = QHBoxLayout()
        sc_row.addWidget(QLabel("Scale:"))
        self.overlay_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.overlay_scale_slider.setRange(50, 200)
        self.overlay_scale_slider.valueChanged.connect(self._on_overlay_scale_change)
        sc_row.addWidget(self.overlay_scale_slider)
        app_layout.addLayout(sc_row)
        
        layout.addWidget(app_card)
        
        self.tab_overlay.setWidget(container)
        self.tab_widget.addTab(self.tab_overlay, "Overlay")
        self.overlay_cards = [metrics_card, app_card]
        
    def _on_overlay_opacity_change(self, val):
        self.settings_mgr.set("overlay_opacity", val / 100.0)
        if hasattr(self, "floating_overlay"):
            self.floating_overlay.apply_settings()
            
    def _on_overlay_scale_change(self, val):
        self.settings_mgr.set("overlay_scale", val / 100.0)
        if hasattr(self, "floating_overlay"):
            self.floating_overlay.apply_settings()

    def _on_overlay_setting_change(self, key, value):
        self.settings_mgr.set(key, value)
        if hasattr(self, "floating_overlay"):
            self.floating_overlay.apply_settings()

    def _on_overlay_toggle(self):
        if not hasattr(self, "floating_overlay"):
            from overlay import FloatingOverlay
            self.floating_overlay = FloatingOverlay(self, self.settings_mgr)
            self.floating_overlay.apply_settings()
        if self.floating_overlay.isVisible():
            self.floating_overlay.deactivate()
            self.btn_toggle_overlay.setText("Mostra Widget Fluttuante")
        else:
            self.floating_overlay.activate()
            self.btn_toggle_overlay.setText("Nascondi Widget Fluttuante")

    def sync_settings(self):
        mgr = self.settings_mgr
        
        self.theme_combo.blockSignals(True)
        self.lang_combo.blockSignals(True)
        self.compact_cb.blockSignals(True)
        self.kb_theme_combo.blockSignals(True)
        self.kb_style_combo.blockSignals(True)
        self.kb_layout_combo.blockSignals(True)
        self.startup_cb.blockSignals(True)
        
        self.overlay_show_apm.blockSignals(True)
        self.overlay_show_wpm.blockSignals(True)
        self.overlay_show_peak.blockSignals(True)
        self.overlay_show_profile.blockSignals(True)
        self.overlay_opacity_slider.blockSignals(True)
        self.overlay_scale_slider.blockSignals(True)
        
        self.theme_combo.setCurrentText(mgr.get("theme").capitalize())
        self.lang_combo.setCurrentText(mgr.get("language"))
        self.compact_cb.setChecked(mgr.get("compact_mode"))
        self.kb_theme_combo.setCurrentText(mgr.get("keyboard_theme"))
        self.kb_style_combo.setCurrentText(mgr.get("keyboard_style"))
        self.kb_layout_combo.setCurrentText(mgr.get("keyboard_layout") or "100%")
        
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, "TypeTrace")
            self.startup_cb.setChecked(True)
            winreg.CloseKey(key)
        except Exception:
            self.startup_cb.setChecked(False)
            
        self.overlay_show_apm.setChecked(mgr.get("overlay_show_apm"))
        self.overlay_show_wpm.setChecked(mgr.get("overlay_show_wpm"))
        self.overlay_show_peak.setChecked(mgr.get("overlay_show_peak"))
        self.overlay_show_profile.setChecked(mgr.get("overlay_show_profile"))
        self.overlay_opacity_slider.setValue(int(mgr.get("overlay_opacity") * 100))
        self.overlay_scale_slider.setValue(int(mgr.get("overlay_scale") * 100))
        
        self.theme_combo.blockSignals(False)
        self.lang_combo.blockSignals(False)
        self.compact_cb.blockSignals(False)
        self.kb_theme_combo.blockSignals(False)
        self.kb_style_combo.blockSignals(False)
        self.kb_layout_combo.blockSignals(False)
        self.startup_cb.blockSignals(False)
        
        self.overlay_show_apm.blockSignals(False)
        self.overlay_show_wpm.blockSignals(False)
        self.overlay_show_peak.blockSignals(False)
        self.overlay_show_profile.blockSignals(False)
        self.overlay_opacity_slider.blockSignals(False)
        self.overlay_scale_slider.blockSignals(False)

    def _on_kb_layout_change(self, text):
        self.settings_mgr.set("keyboard_layout", text)
        if hasattr(self, "heatmap"):
            self.heatmap.update()

    def _on_theme_change(self, text):
        if hasattr(self, "change_theme_mode"):
            self.change_theme_mode(text.lower())

    def _on_lang_change(self, text):
        self.settings_mgr.set("language", text)
        QMessageBox.information(self, "Restart Required", "Language changed. Please restart TypeTrace for the changes to take effect.")

    def _on_compact_change(self, checked):
        if self.is_compact != checked:
            self.toggle_compact_mode()

    def _on_heatmap_toggle(self, checked):
        if hasattr(self, "heatmap"):
            self.heatmap.heatmap_enabled = checked
            self._update_heatmap_colors()
            self.heatmap.update()

    def _toggle_settings_drawer(self):
        if not hasattr(self, "settings_drawer"): return
        target_width = 380
        is_open = self.settings_drawer.isVisible()
        
        if not is_open:
            self.settings_drawer.setGeometry(self.width(), 0, target_width, self.height())
            self.settings_drawer.show()
            self.settings_drawer.raise_()
            end_x = self.width() - target_width
        else:
            end_x = self.width()
            
        self.drawer_anim = QPropertyAnimation(self.settings_drawer, b"geometry")
        self.drawer_anim.setDuration(250)
        self.drawer_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.drawer_anim.setStartValue(self.settings_drawer.geometry())
        self.drawer_anim.setEndValue(QRect(end_x, 0, target_width, self.height()))
        
        if is_open:
            self.drawer_anim.finished.connect(self.settings_drawer.hide)
        self.drawer_anim.start()

    def _on_kb_theme_change(self, text):
        if hasattr(self, "heatmap"):
            self.heatmap.set_theme(text)
            self.legend.set_theme(text)
            self.settings_mgr.set("keyboard_theme", text)

    def _on_kb_style_change(self, text):
        if hasattr(self, "heatmap"):
            self.settings_mgr.set("keyboard_style", text)
            self.heatmap.update()

    def _on_startup_change(self, checked):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            if checked:
                exe_path = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, "TypeTrace", 0, winreg.REG_SZ, f'"{exe_path}"')
            else:
                try:
                    winreg.DeleteValue(key, "TypeTrace")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            logging.error(f"Failed to set startup registry key: {e}")

    def _pick_color(self):
        c = QColorDialog.getColor(hex_to_qcolor(self.current_tokens.accent), self, "Select Accent Color")
        if c.isValid():
            hex_c = qcolor_to_hex(c)
            if hasattr(self, "change_accent_color"):
                self.change_accent_color(hex_c)

    def _open_smart_map(self):
        d = ProcessMappingDialog(self, self.db, self.tr, self.current_tokens)
        d.exec()

    def _open_export(self):
        d = ExportDialog(self, self.db, self.current_profile, self.tr, self.current_tokens)
        d.exec()

    def _reset_stats(self):
        prof = self.current_profile
        reply = QMessageBox.question(self, "Reset Stats", f"Are you sure you want to reset all stats for profile '{prof}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.reset_profile(prof)
            self._request_full_update()

    def _apply_theme(self, tokens: ThemeTokens):
        self.current_tokens = tokens
        qss = build_qss(tokens)
        QApplication.instance().setStyleSheet(qss)
        
        self.tab_widget.tabBar().setStyleSheet(f"""
            QTabBar {{
                background-color: {tokens.bg_window};
                border-bottom: 1px solid {tokens.border};
            }}
            QTabBar::tab {{
                background: {tokens.bg_window};
                color: {tokens.text_secondary};
                padding: 10px 24px;
                border: none;
                font-size: 13px;
                min-width: 120px;
            }}
            QTabBar::tab:selected {{
                color: {tokens.text_primary};
                border-bottom: 2px solid {tokens.accent};
                background: {tokens.bg_panel};
            }}
            QTabBar::tab:hover:!selected {{
                color: {tokens.text_primary};
                background: {tokens.bg_hover};
            }}
        """)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                background: {tokens.tab_pane_bg};
                border: 1px solid {tokens.border};
                border-top: none;
            }}
            QTabWidget > QTabBar {{
                background-color: {tokens.bg_window};
            }}
        """)
        
        for cards_list in [self.telemetry_cards, getattr(self, 'config_cards', []), getattr(self, 'overlay_cards', [])]:
            for card in cards_list:
                if hasattr(card, "set_tokens"):
                    card.set_tokens(tokens)
                else:
                    card.setStyleSheet(f"background-color: {tokens.bg_panel}; border: 1px solid {tokens.border}; border-radius: 10px;")
        
        self.header.set_tokens(tokens)
        self.heatmap.set_tokens(tokens)
        self.legend.set_tokens(tokens)
        self.chart_widget.set_tokens(tokens)
        self.combos_list.set_tokens(tokens)
        self.bigrams_list.set_tokens(tokens)
        self.overlay.set_tokens(tokens)
        
        if hasattr(self, "compact_cb"):
            self.compact_cb.set_tokens(tokens)
            self.startup_cb.set_tokens(tokens)
            self.overlay_show_apm.set_tokens(tokens)
            self.overlay_show_wpm.set_tokens(tokens)
            self.overlay_show_peak.set_tokens(tokens)
            self.overlay_show_profile.set_tokens(tokens)
            
        if hasattr(self, "btn_toggle_overlay"):
            self.btn_toggle_overlay.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {tokens.accent};
                    border: 2px solid {tokens.accent};
                    border-radius: 8px;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: rgba({int(tokens.accent[1:3], 16)}, {int(tokens.accent[3:5], 16)}, {int(tokens.accent[5:7], 16)}, 0.15);
                }}
            """)
            
        if hasattr(self, "heatmap_toggle"):
            self.heatmap_toggle.set_tokens(tokens)
        if hasattr(self, "main_stats_lbl"):
            self.main_stats_lbl.setStyleSheet(f"color: {tokens.text_primary};")
        if hasattr(self, "settings_drawer"):
            self.settings_drawer.setStyleSheet(f"QScrollArea {{ background-color: {tokens.bg_panel}; border-left: 2px solid {tokens.border}; }}")
        if hasattr(self, "btn_close_drawer"):
            self.btn_close_drawer.setStyleSheet(f"background-color: transparent; color: {tokens.text_secondary}; border: none;")
        if hasattr(self, "compact_restore_btn"):
            self.compact_restore_btn.setStyleSheet(f"background-color: transparent; color: {tokens.text_secondary}; border: none; font-size: 16px; font-weight: bold;")
            
        self.setStyleSheet(f"TypeTraceUI {{ background-color: {tokens.bg_window}; }}")
        
        for lbl in self.telemetry_labels + getattr(self, "telemetry_sub_labels", []):
            lbl.setStyleSheet("color: " + tokens.text_secondary)
        
        self._update_heatmap_colors()
        self.update()
        self.tab_widget.tabBar().update()
        self.tab_widget.update()
        self.tab_widget.tabBar().repaint()

    def change_theme_mode(self, mode_str: str):
        is_dark = (mode_str.lower() == "dark")
        if is_dark == self.is_dark_mode:
            return
            
        self.transition_pixmap = self.grab()
        self.transition_label = QLabel(self)
        self.transition_label.setPixmap(self.transition_pixmap)
        self.transition_label.setGeometry(self.rect())
        self.transition_label.show()
        
        self.is_dark_mode = is_dark
        self.settings_mgr.set("theme", mode_str.lower())
        base = DARK_TOKENS if is_dark else LIGHT_TOKENS
        new_tokens = replace(base, accent=self.settings_mgr.get("accent_color"))
        self._apply_theme(new_tokens)
        
        effect = QGraphicsOpacityEffect(self.transition_label)
        self.transition_label.setGraphicsEffect(effect)
        self.transition_anim = QPropertyAnimation(effect, b"opacity")
        self.transition_anim.setDuration(300)
        self.transition_anim.setStartValue(1.0)
        self.transition_anim.setEndValue(0.0)
        self.transition_anim.finished.connect(self.transition_label.deleteLater)
        self.transition_anim.start()

    def change_accent_color(self, hex_color: str):
        self.settings_mgr.set("accent_color", hex_color)
        new_tokens = replace(self.current_tokens)
        new_tokens.accent = hex_color
        self._apply_theme(new_tokens)

    def toggle_compact_mode(self):
        self.is_compact = not self.is_compact
        self.settings_mgr.set("compact_mode", self.is_compact)
        
        if self.is_compact:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.header.hide()
            self.tab_widget.tabBar().hide()
            if hasattr(self, "dash_widget"):
                self.dash_widget.hide()
            self.legend.hide()
            if hasattr(self, "compact_restore_btn"):
                self.compact_restore_btn.show()
                self.compact_restore_btn.raise_()
            self.setMinimumSize(400, 200)
            self.resize(600, 250)
            self.show()
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.FramelessWindowHint & ~Qt.WindowType.WindowStaysOnTopHint)
            self.setMinimumSize(800, 500)
            self.resize(900, 600)
            self.header.show()
            self.tab_widget.tabBar().show()
            if hasattr(self, "dash_widget"):
                self.dash_widget.show()
            if self.heatmap.heatmap_enabled:
                self.legend.show()
            if hasattr(self, "compact_restore_btn"):
                self.compact_restore_btn.hide()
            self.show()

    def mousePressEvent(self, event):
        if self.is_compact and event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_compact and event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def _on_tracker_event(self, event_type, value):
        self.event_queue.put((event_type, value))

    def _process_queue(self):
        needs_heatmap_update = False
        while not self.event_queue.empty():
            try:
                ev_type, val = self.event_queue.get_nowait()
                if ev_type == "keystroke":
                    self.heatmap.add_ripple(val)
                    needs_heatmap_update = True
                elif ev_type == "incognito":
                    self.header.is_incognito = val
                    if val:
                        self.overlay.activate()
                    else:
                        self.overlay.deactivate()
                    self.header.update_stats(self.header.apm, self.header.wpm, self.header.is_tracking)
                elif ev_type == "toggle_overlay":
                    pass 
                elif ev_type == "restore":
                    self.show()
                    self.activateWindow()
                elif ev_type == "exit":
                    self._force_quit = True
                    self.close()
                elif ev_type == "profile_changed":
                    if self.profile_combo.currentText() != val:
                        self.profile_combo.setCurrentText(val)
                    if val != self.current_profile:
                        self.heatmap.start_gaming_banner(self.current_profile)
                    self.current_profile = val
                    self._request_full_update()
                elif ev_type == "burst_detected":
                    peak, dur = val
                    txt = f"{peak} APM ({dur:.1f}s)"
                    self.burst_val.setText(txt)
            except queue.Empty:
                break
        
        apm, wpm = self.tracker.get_apm_wpm()
        is_tracking = not getattr(self.tracker, "incognito_mode", False)
        self.header.update_stats(apm, wpm, is_tracking)
        
        if hasattr(self, "floating_overlay") and self.floating_overlay.isVisible():
            self.floating_overlay.update_data(apm, wpm, "00:00:00", self.current_profile, "Space (0%)")
        
        if needs_heatmap_update and self.heatmap.heatmap_enabled:
            self._update_heatmap_colors()

    def _on_anim_tick(self):
        self.header.on_anim_tick()
        self.header.update()
        self.heatmap.update()

    def _on_tab_changed(self, index):
        if index == 1:
            self._update_telemetry()
        elif index == 0:
            self._update_heatmap_colors()

    def _on_profile_changed_ui(self, profile_name):
        if profile_name != self.current_profile:
            self.current_profile = profile_name
            self.tracker.set_active_profile(profile_name)
            self._request_full_update()

    def _request_full_update(self):
        if self.tab_widget.currentIndex() == 0:
            self._update_heatmap_colors()
        elif self.tab_widget.currentIndex() == 1:
            self._update_telemetry()

    def _update_heatmap_colors(self):
        agg_stats = self.db.get_aggregated_stats(self.current_profile)
        keys_data = agg_stats.get("keys", {})
        self.heatmap.key_stats = keys_data
        
        if not self.heatmap.heatmap_enabled:
            self.heatmap.update_colors({})
            self.heatmap.update()
            return
            
        if not keys_data:
            self.heatmap.update_colors({})
            self.heatmap.update()
            return
            
        counts = sorted(keys_data.values())
        idx = int(len(counts) * 0.95)
        if idx >= len(counts): idx = len(counts) - 1
        max_val = counts[idx] if counts and counts[idx] > 0 else 1
        
        target_colors = {}
        for k, count in keys_data.items():
            if count > 0:
                norm = min(1.0, math.pow(count / max_val, 0.6))
                target_colors[k] = self.heatmap._resolve_color(norm)
        
        self.heatmap.update_colors(target_colors)
        self.heatmap.update()

    def _update_telemetry(self):
        agg_stats = self.db.get_aggregated_stats(self.current_profile)
        keys_data = agg_stats.get("keys", {})
        total_keys = sum(keys_data.values())
        estimated_words = total_keys // 5
        self.session_val.setText(f"{estimated_words:,}")
        
        raw_stats = self.db.get_stats_for_profile(self.current_profile)
        hourly_data = raw_stats.get("hourly", {})
        
        peak_apm = 0
        burst_records = raw_stats.get("burst_records", [])
        if burst_records:
            best_burst = max(burst_records, key=lambda x: x.get("peak_apm", 0))
            peak_apm = best_burst.get("peak_apm", 0)
            
        if hasattr(self, "main_stats_lbl"):
            self.main_stats_lbl.setText(f"APM: {peak_apm} | Parole: {estimated_words}")
            
        if keys_data:
            top_key = max(keys_data.items(), key=lambda x: x[1])[0]
            self.top_key_val.setText(str(top_key))
        else:
            self.top_key_val.setText("-")
            
        combos_data = agg_stats.get("combinations", {})
        sorted_combos = sorted(combos_data.items(), key=lambda x: x[1], reverse=True)[:5]
        self.combos_list.set_data(sorted_combos)
        
        bigrams_data = agg_stats.get("bigrams", {})
        sorted_bigrams = sorted(bigrams_data.items(), key=lambda x: x[1], reverse=True)[:5]
        self.bigrams_list.set_data(sorted_bigrams)
            
        raw_stats = self.db.get_stats_for_profile(self.current_profile)
        hourly_data = raw_stats.get("hourly", {})
        self.chart_widget.set_data(hourly_data)
        
        burst_records = raw_stats.get("burst_records", [])
        if burst_records:
            best_burst = max(burst_records, key=lambda x: x.get("peak_apm", 0))
            p_apm = best_burst.get("peak_apm", 0)
            p_dur = best_burst.get("duration", 0)
            self.peak_val.setText(f"{p_apm} APM ({p_dur}s)")
        else:
            self.peak_val.setText("0 APM (0s)")

    def closeEvent(self, event):
        if getattr(self, "_force_quit", False):
            if self.shutdown_callback:
                self.shutdown_callback()
            event.accept()
        else:
            self.hide()
            event.ignore()

    def process_event_queue(self, q=None):
        if q is not None:
            self.event_queue = q

    def mainloop(self):
        self.show()
        import sys
        sys.exit(self._app.exec())

    def destroy(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    from database import Database
    from tracker import KeystrokeTracker
    db = Database()
    tracker = KeystrokeTracker(db)
    tracker.start()
    ui = TypeTraceUI(db, tracker)
    ui.show()
    sys.exit(app.exec())
