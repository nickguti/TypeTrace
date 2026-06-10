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
    QTabBar, QButtonGroup, QRadioButton, QDialog, QLineEdit,
    QColorDialog, QGraphicsOpacityEffect, QMessageBox, QFileDialog, QScrollArea, QFrame, QGridLayout, QSizePolicy, QScrollBar
)
from PyQt6.QtCore import (
    Qt, QTimer, QTime, QRectF, QPointF, pyqtSignal, pyqtSlot, QAbstractAnimation,
    QPropertyAnimation, QMetaObject, Q_ARG, QEasingCurve, QRect
)
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QPainterPath,
    QLinearGradient, QRadialGradient, QCursor, QFontDatabase
)
import utils

APP_VERSION = "2.1.0"
APP_GITHUB = "https://github.com/nicolas/typetrace"

FONT_FAMILY = "Segoe UI Variable"

@dataclass
class ThemeTokens:
    bg_window: str
    bg_panel: str
    bg_input: str
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
    bg_window="#0B0C10", bg_panel="#171A23", bg_input="#171A23",
    border="#2F313D", accent="#00F5D4",
    text_primary="#FFFFFF", text_secondary="#8E9297",
    key_cold="#1E2130", key_shadow="#000000",
    key_highlight="rgba(255,255,255,0.08)",
    tab_pane_bg="#171A23", status_bar_bg="#0B0C10"
)

LIGHT_TOKENS = ThemeTokens(
    bg_window="#EEF0F5", bg_panel="#F7F8FC", bg_input="#FFFFFF",
    border="#C8CDD8", accent="#00F5D4",
    text_primary="#1A1C23", text_secondary="#5A6278",
    key_cold="#DDE0EA", key_shadow="#B0B5C3",
    key_highlight="rgba(255,255,255,0.6)",
    tab_pane_bg="#F0F2F8", status_bar_bg="#E4E7F0"
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
QTabWidget::pane {{
    border: 1px solid {tokens.border};
    border-radius: 8px;
    background: {tokens.tab_pane_bg};
    margin-top: -1px;
}}
QTabWidget::tab-bar {{
    alignment: left;
}}
QTabBar::tab {{
    background: transparent;
    color: {tokens.text_secondary};
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:selected {{
    color: {tokens.text_primary};
    border-bottom: 2px solid {tokens.accent};
}}
QTabBar::tab:hover:!selected {{
    color: {tokens.text_primary};
}}
QTabBar::tab:!selected {{
    color: {tokens.text_secondary};
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
        "keyboard_theme": "Classic Heatmap"
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
        layout.setContentsMargins(20, 0, 20, 0)
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
        
        self.gear_btn = QPushButton("\u2699")
        self.gear_btn.setFixedSize(32, 32)
        self.gear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.gear_btn.setToolTip("Settings")
        layout.addWidget(self.gear_btn)
        
        self.compact_btn = QPushButton("\u229f")
        self.compact_btn.setFixedSize(32, 32)
        self.compact_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.compact_btn.setToolTip(self.tr.t("compact_mode") if self.tr else "Compact Mode")
        layout.addWidget(self.compact_btn)

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.title_lbl.setStyleSheet(f"color: {self.tokens.accent}; background: transparent;")
        self.subtitle_lbl.setStyleSheet(f"color: {self.tokens.text_secondary}; background: transparent;")
        self.apm_lbl.setStyleSheet(f"color: {self.tokens.text_primary}; background: transparent;")
        self.wpm_lbl.setStyleSheet(f"color: {self.tokens.text_primary}; background: transparent;")
        
        btn_qss = f"""
            QPushButton {{
                background-color: transparent;
                color: {self.tokens.text_secondary};
                border: 1px solid {self.tokens.border};
                border-radius: 4px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                color: {self.tokens.text_primary};
                border: 1px solid {self.tokens.accent};
            }}
        """
        self.gear_btn.setStyleSheet(btn_qss)
        self.compact_btn.setStyleSheet(btn_qss)
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
        self.status_lbl.setStyleSheet(f"color: {c}; background: transparent;")

    def on_anim_tick(self):
        self.bg_pulse_alpha += 0.05
        if self.bg_pulse_alpha > 2 * math.pi:
            self.bg_pulse_alpha -= 2 * math.pi

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), hex_to_qcolor(self.tokens.bg_panel))
        if not self.is_incognito and self.is_tracking:
            pulse = (math.sin(self.bg_pulse_alpha) + 1) / 2
            alpha = int(10 + 15 * pulse)
            c = hex_to_qcolor(self.tokens.accent)
            c.setAlpha(alpha)
            painter.fillRect(self.rect(), c)
        painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
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
        painter.fillRect(self.rect(), hex_to_qcolor(self.tokens.bg_panel))
        draw_rect = self._compute_draw_rect()
        if draw_rect.width() < 50 or draw_rect.height() < 20:
            painter.end()
            return
        font_size = max(7, int(draw_rect.height() / 25))
        font = QFont(FONT_FAMILY, font_size)
        font.setBold(True)
        painter.setFont(font)
        border_pen = QPen(hex_to_qcolor(self.tokens.border), 1.0)
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
        shadow_c.setAlpha(80 if self.tokens.key_shadow == "#B0B5C3" else 153)
        hl_parts = self.tokens.key_highlight.strip("rgba()").split(",")
        hl_c = QColor(int(hl_parts[0]), int(hl_parts[1]), int(hl_parts[2]), int(float(hl_parts[3]) * 255))
        
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
                r_c = int(base_color.red() * (1 - alpha) + accent_c.red() * alpha)
                g_c = int(base_color.green() * (1 - alpha) + accent_c.green() * alpha)
                b_c = int(base_color.blue() * (1 - alpha) + accent_c.blue() * alpha)
                fill_color = QColor(r_c, g_c, b_c)
            else:
                fill_color = base_color
                if key_id == self._hovered_key_id and not self.heatmap_enabled:
                    hc = hex_to_qcolor(self.tokens.border)
                    fill_color = interpolate_color(base_color, hc, 0.3)
                    
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
            
            if self.heatmap_enabled and key_id in self.current_colors:
                c = self.current_colors[key_id]
                lum = 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()
                text_color = QColor("#171A23" if lum > 128 else "#E8EAF0")
            else:
                text_color = hex_to_qcolor(self.tokens.text_secondary)
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
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 12, 12)
        painter.fillPath(path, hex_to_qcolor(self.tokens.bg_input))
        painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
        painter.drawPath(path)
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

class SettingsDrawer(QWidget):
    def __init__(self, parent, tr=None, ui_parent=None):
        super().__init__(parent)
        self.tr = tr
        self.ui_parent = ui_parent
        self.tokens = DARK_TOKENS
        self.setFixedWidth(320)
        self.hide()
        
        self.is_open = False
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.finished.connect(self._on_anim_finished)
        
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(48)
        self.content_layout.addWidget(self.header_widget)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(16)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll.setWidget(self.scroll_content)
        
        self.content_layout.addWidget(self.scroll)
        
        self.close_rect = QRect(280, 14, 20, 20)
        
        self._build_sections()

    def set_tokens(self, tokens: ThemeTokens):
        self.tokens = tokens
        self.update()

    def _build_sections(self):
        def _section_header(text):
            lbl = QLabel("  ".join(text.upper()))
            lbl.setFixedHeight(24)
            lbl.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 11px; border-bottom: 1px solid {self.tokens.border}; margin-bottom: 8px;")
            return lbl

        def _row(label_text, control):
            row = QWidget()
            row.setMinimumHeight(36)
            lo = QHBoxLayout(row)
            lo.setContentsMargins(0, 0, 0, 0)
            lo.setSpacing(10)
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {self.tokens.text_primary}; font-size: 13px;")
            lo.addWidget(lbl)
            lo.addStretch()
            lo.addWidget(control)
            return row

        self.scroll_layout.addWidget(_section_header(self.tr.t("appearance") if self.tr else "Appearance"))
        
        theme_row = QWidget()
        theme_lo = QHBoxLayout(theme_row)
        theme_lo.setContentsMargins(0,0,0,0)
        self.dark_chip = QPushButton("\u263e Dark")
        self.dark_chip.setCheckable(True)
        self.dark_chip.clicked.connect(lambda: self.ui_parent._set_theme_mode("dark"))
        self.light_chip = QPushButton("\u2600 Light")
        self.light_chip.setCheckable(True)
        self.light_chip.clicked.connect(lambda: self.ui_parent._set_theme_mode("light"))
        theme_lo.addWidget(self.dark_chip)
        theme_lo.addWidget(self.light_chip)
        self.scroll_layout.addWidget(_row(self.tr.t("theme") if self.tr else "Theme", theme_row))
        
        self.accent_btn = QPushButton()
        self.accent_btn.setFixedSize(100, 28)
        self.accent_btn.clicked.connect(self.ui_parent._pick_accent_color)
        self.scroll_layout.addWidget(_row(self.tr.t("accent_color") if self.tr else "Accent Color", self.accent_btn))
        
        self.kbd_theme_combo = QComboBox()
        self.kbd_theme_combo.addItems(list(KEYBOARD_THEMES.keys()))
        self.kbd_theme_combo.currentTextChanged.connect(self.ui_parent._change_keyboard_theme)
        self.scroll_layout.addWidget(_row(self.tr.t("keyboard_theme") if self.tr else "Keyboard Theme", self.kbd_theme_combo))
        
        self.scroll_layout.addWidget(_section_header(self.tr.t("interface") if self.tr else "Interface"))
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Italiano"])
        self.lang_combo.currentIndexChanged.connect(self.ui_parent._change_language)
        self.scroll_layout.addWidget(_row(self.tr.t("language") if self.tr else "Language", self.lang_combo))
        
        self.lang_notice = QLabel("")
        self.lang_notice.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 11px;")
        self.lang_notice.setVisible(False)
        self.scroll_layout.addWidget(self.lang_notice)
        
        self.compact_check = QCheckBox()
        self.compact_check.stateChanged.connect(self.ui_parent._toggle_compact_check)
        self.scroll_layout.addWidget(_row(self.tr.t("compact_mode") if self.tr else "Compact Mode", self.compact_check))
        
        self.startup_check = QCheckBox()
        self.startup_check.setChecked(utils.is_startup_enabled())
        self.startup_check.stateChanged.connect(self.ui_parent._toggle_startup)
        self.scroll_layout.addWidget(_row(self.tr.t("boot_startup") if self.tr else "Boot Startup", self.startup_check))
        
        self.scroll_layout.addWidget(_section_header(self.tr.t("tracking") if self.tr else "Tracking"))
        
        self.auto_btn = QPushButton(self.tr.t("auto_switch") if self.tr else "Auto-Switch")
        self.auto_btn.clicked.connect(self.ui_parent._open_mappings_dialog)
        self.scroll_layout.addWidget(_row("Smart Mapping", self.auto_btn))
        
        self.heatmap_check = QCheckBox()
        self.heatmap_check.stateChanged.connect(self.ui_parent._toggle_heatmap)
        self.scroll_layout.addWidget(_row(self.tr.t("heatmap_view") if self.tr else "Heatmap View", self.heatmap_check))
        
        self.overlay_check = QCheckBox()
        self.overlay_check.stateChanged.connect(self.ui_parent._toggle_overlay_check)
        self.scroll_layout.addWidget(_row(self.tr.t("floating_widget") if self.tr else "Floating Widget", self.overlay_check))
        
        self.scroll_layout.addWidget(_section_header(self.tr.t("data") if self.tr else "Data"))
        
        self.export_btn = QPushButton("\u21e7 " + (self.tr.t("export") if self.tr else "Export"))
        self.export_btn.setFixedHeight(36)
        self.export_btn.clicked.connect(self.ui_parent._open_export_dialog)
        self.scroll_layout.addWidget(self.export_btn)
        
        self.reset_btn = QPushButton("\u26a0 " + (self.tr.t("reset") if self.tr else "Reset"))
        self.reset_btn.setFixedHeight(36)
        self.reset_btn.setStyleSheet("background: transparent; color: #E05C5C; border: 1px solid #E05C5C;")
        self.reset_btn.clicked.connect(self.ui_parent._reset_statistics_dialog)
        self.scroll_layout.addWidget(self.reset_btn)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), hex_to_qcolor(self.tokens.bg_panel))
        
        painter.setPen(QPen(hex_to_qcolor(self.tokens.accent), 2.0))
        painter.drawLine(0, 0, 0, self.height())
        
        painter.fillRect(0, 0, self.width(), 48, hex_to_qcolor(self.tokens.bg_window))
        
        painter.setPen(hex_to_qcolor(self.tokens.text_primary))
        painter.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        painter.drawText(QRectF(20, 0, self.width()-40, 48), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Settings")
        
        painter.setPen(QPen(hex_to_qcolor(self.tokens.text_secondary), 2.0))
        painter.drawLine(285, 19, 295, 29)
        painter.drawLine(295, 19, 285, 29)
        
        painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
        painter.drawLine(0, 48, self.width(), 48)
        
        painter.end()

    def mousePressEvent(self, event):
        if self.close_rect.contains(event.pos()):
            self.toggle()
        else:
            super().mousePressEvent(event)

    def toggle(self):
        parent_w = self.parentWidget().width()
        parent_h = self.parentWidget().height()
        self.anim.stop()
        if self.is_open:
            self.anim.setDuration(180)
            self.anim.setStartValue(QRect(parent_w - 320, 0, 320, parent_h))
            self.anim.setEndValue(QRect(parent_w, 0, 320, parent_h))
            self.anim.setEasingCurve(QEasingCurve.Type.InCubic)
            self.is_open = False
        else:
            self.setGeometry(parent_w, 0, 320, parent_h)
            self.show()
            self.raise_()
            self.anim.setDuration(220)
            self.anim.setStartValue(QRect(parent_w, 0, 320, parent_h))
            self.anim.setEndValue(QRect(parent_w - 320, 0, 320, parent_h))
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.is_open = True
        self.anim.start()

    def _on_anim_finished(self):
        if not self.is_open:
            self.hide()


class TypeTraceUI(QMainWindow):
    _trigger_profile_switch = pyqtSignal(str, str)
    _trigger_incognito = pyqtSignal(bool)

    def __init__(self, db, tracker, shutdown_callback=None):
        self._qt_app = QApplication.instance()
        if self._qt_app is None:
            self._qt_app = QApplication(sys.argv)
        super().__init__()
        self.db = db
        self.tracker = tracker
        self.shutdown_callback = shutdown_callback
        self.overlay = None
        self.heatmap_enabled = False
        self.viewing_profile = self.tracker.active_profile
        self.incognito_active = False
        self.settings = SettingsManager()
        
        self.current_tokens = DARK_TOKENS if self.settings.get("theme") == "dark" else LIGHT_TOKENS
        self.current_tokens = replace(self.current_tokens, accent=self.settings.get("accent_color"))
        
        self.tr = Translator(self.settings.get("language"))
        
        self.setWindowTitle("TypeTrace \u2014 Keystroke Analytics")
        self.resize(1500, 820)
        self.setMinimumSize(900, 500)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.header = HeaderWidget(tr=self.tr)
        self.header.gear_btn.clicked.connect(self._toggle_drawer)
        self.header.compact_btn.clicked.connect(self._toggle_compact)
        main_layout.addWidget(self.header)
        
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(20, 10, 20, 10)
        body_layout.setSpacing(10)
        
        self.keyboard_widget = KeyboardHeatmapWidget()
        self.keyboard_widget.parent_ui = self
        self.heatmap_legend = LegendBarWidget(tr=self.tr)
        self.heatmap_legend.setVisible(False)
        
        kbd_container = QVBoxLayout()
        kbd_container.setSpacing(10)
        kbd_container.addWidget(self.keyboard_widget)
        kbd_container.addWidget(self.heatmap_legend)
        body_layout.addLayout(kbd_container, 3)
        
        self.tab_bar = QTabBar()
        self.tab_bar.addTab(self.tr.t("tab_config") if self.tr else "Configuration")
        self.tab_bar.addTab(self.tr.t("tab_telemetry") if self.tr else "Telemetry")
        self.tab_bar.addTab(self.tr.t("tab_chart") if self.tr else "Chart")
        self.tab_bar.currentChanged.connect(self._on_tab_changed)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self._build_config_tab())
        self.stacked_widget.addWidget(self._build_telemetry_tab())
        self.stacked_widget.addWidget(self._build_chart_tab())
        
        self.tab_container = QWidget()
        tab_layout = QVBoxLayout(self.tab_container)
        tab_layout.setSpacing(0)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(self.tab_bar)
        tab_layout.addWidget(self.stacked_widget)
        body_layout.addWidget(self.tab_container, 1)
        
        main_layout.addLayout(body_layout)
        
        self.incognito_overlay = IncognitoOverlay(central)
        self.incognito_overlay.hide()
        
        self.settings_drawer = SettingsDrawer(central, tr=self.tr, ui_parent=self)
        
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
        self._queue_timer.start(50)
        
        self._save_timer = QTimer(self)
        self._save_timer.timeout.connect(self._save_data)
        self._save_timer.start(5000)
        
        self._trigger_profile_switch.connect(self._do_profile_switch_animation)
        self._trigger_incognito.connect(self._do_set_incognito)
        
        self._apply_theme(self.current_tokens)
        self._update_drawer_state()
        self._update_chip_styles()
        self.update_ui_stats()
        
        if self.settings.get("compact_mode"):
            self._apply_compact(True)
            
        self.setWindowOpacity(0.0)
        self._fade_opacity = 0.0
        self._fade_timer = QTimer(self)
        self._fade_timer.setInterval(16)
        self._fade_timer.timeout.connect(self._on_fade_tick)
        if not self.settings.get("welcome_shown"):
            QTimer.singleShot(50, self._show_welcome)
        else:
            QTimer.singleShot(50, self._start_fade_in)

    def _apply_theme(self, tokens: ThemeTokens):
        qss = build_qss(tokens)
        self._qt_app.setStyleSheet(qss)
        
        self.keyboard_widget.set_tokens(tokens)
        self.header.set_tokens(tokens)
        self.heatmap_legend.set_tokens(tokens)
        self.incognito_overlay.set_tokens(tokens)
        self.settings_drawer.set_tokens(tokens)
        self.hourly_chart.set_tokens(tokens)
        for card in [self.session_card, self.leader_card, self.burst_card]:
            card.set_tokens(tokens)
            
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QPushButton, QLabel, QCheckBox, QComboBox, QLineEdit, QScrollBar)):
                widget.setStyleSheet("")
                
        self.current_tokens = tokens
        self._update_chip_styles()
        self._update_drawer_state()
        
        QApplication.instance().processEvents()

    def _update_drawer_state(self):
        accent_hex = self.current_tokens.accent
        self.settings_drawer.accent_btn.setText(f"\u25cf {accent_hex}")
        self.settings_drawer.accent_btn.setStyleSheet(f"color: {accent_hex}; font-weight: bold;")
        
        is_dark = self.settings.get("theme") == "dark"
        d_chip = self.settings_drawer.dark_chip
        l_chip = self.settings_drawer.light_chip
        selected_qss = f"background: rgba({int(accent_hex[1:3],16)},{int(accent_hex[3:5],16)},{int(accent_hex[5:7],16)},0.15); border: 1px solid {accent_hex}; color: {accent_hex}; border-radius: 14px;"
        unselected_qss = f"background: transparent; border: 1px solid {self.current_tokens.border}; color: {self.current_tokens.text_secondary}; border-radius: 14px;"
        d_chip.setStyleSheet(selected_qss if is_dark else unselected_qss)
        l_chip.setStyleSheet(selected_qss if not is_dark else unselected_qss)
        
        lang_idx = 1 if self.settings.get("language") == "it" else 0
        self.settings_drawer.lang_combo.setCurrentIndex(lang_idx)
        self.settings_drawer.compact_check.setChecked(self.settings.get("compact_mode"))
        self.settings_drawer.kbd_theme_combo.setCurrentText(self.settings.get("keyboard_theme"))
        self.settings_drawer.overlay_check.setChecked(self.db.get_overlay_enabled())

    def _set_theme_mode(self, mode):
        if self.settings.get("theme") == mode:
            return
        self.settings.set("theme", mode)
        self._theme_target_tokens = DARK_TOKENS if mode == "dark" else LIGHT_TOKENS
        self._theme_target_tokens = replace(self._theme_target_tokens, accent=self.settings.get("accent_color"))
        
        self._theme_fade_phase = "out"
        self._theme_fade_val = 1.0
        self._theme_fade_timer = QTimer(self)
        self._theme_fade_timer.setInterval(16)
        self._theme_fade_timer.timeout.connect(self._on_theme_fade)
        self._theme_fade_timer.start()

    def _on_theme_fade(self):
        if self._theme_fade_phase == "out":
            self._theme_fade_val -= 1.0 / (150.0 / 16.0)
            if self._theme_fade_val <= 0.3:
                self._theme_fade_val = 0.3
                self._theme_fade_phase = "swap"
            self.setWindowOpacity(self._theme_fade_val)
        elif self._theme_fade_phase == "swap":
            self._apply_theme(self._theme_target_tokens)
            if self.overlay:
                self.overlay.update_theme(self.current_tokens.accent, self.settings.get("theme") == "light")
            self._theme_fade_phase = "in"
        elif self._theme_fade_phase == "in":
            self._theme_fade_val += 1.0 / (150.0 / 16.0)
            if self._theme_fade_val >= 1.0:
                self._theme_fade_val = 1.0
                self._theme_fade_timer.stop()
            self.setWindowOpacity(self._theme_fade_val)

    def _pick_accent_color(self):
        initial = hex_to_qcolor(self.current_tokens.accent)
        color = QColorDialog.getColor(initial, self, "Choose Accent Color")
        if color.isValid():
            new_hex = qcolor_to_hex(color)
            self.settings.set("accent_color", new_hex)
            new_tokens = replace(self.current_tokens, accent=new_hex)
            self._apply_theme(new_tokens)
            if self.overlay:
                self.overlay.update_theme(new_hex, self.settings.get("theme") == "light")

    def _toggle_drawer(self):
        self.settings_drawer.toggle()

    def _show_welcome(self):
        dlg = WelcomeDialog(self, tr=self.tr, tokens=self.current_tokens)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            pname = dlg.get_profile_name()
            if pname and pname != "Default":
                self.db.create_profile(pname)
                self.tracker.set_profile(pname)
                self.db.set_last_profile(pname)
                self.viewing_profile = pname
        self.settings.set("welcome_shown", True)
        self._start_fade_in()

    def _start_fade_in(self):
        self._fade_opacity = 0.0
        self.setWindowOpacity(0.0)
        self._fade_timer.start()

    def _on_fade_tick(self):
        self._fade_opacity += 1.0 / (600.0 / 16.0)
        if self._fade_opacity >= 1.0:
            self._fade_opacity = 1.0
            self._fade_timer.stop()
        self.setWindowOpacity(self._fade_opacity)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'incognito_overlay'):
            self.incognito_overlay.setGeometry(self.centralWidget().rect())
        if hasattr(self, 'settings_drawer'):
            w = self.width()
            if self.settings_drawer.is_open:
                self.settings_drawer.setGeometry(w - 320, 0, 320, self.height())
            else:
                self.settings_drawer.setGeometry(w, 0, 320, self.height())

    def _toggle_compact(self):
        compact = not self.settings.get("compact_mode")
        self.settings.set("compact_mode", compact)
        self.settings_drawer.compact_check.setChecked(compact)
        self._apply_compact(compact)

    def _toggle_compact_check(self, state):
        compact = bool(state)
        self.settings.set("compact_mode", compact)
        self._apply_compact(compact)

    def _apply_compact(self, compact):
        if compact:
            self.tab_container.hide()
            self.setFixedSize(900, 280)
            self.header.compact_btn.setText("\u229e")
            self.header.compact_btn.setToolTip(self.tr.t("expand") if self.tr else "Expand")
        else:
            self.tab_container.show()
            self.setMinimumSize(900, 500)
            self.setMaximumSize(16777215, 16777215)
            self.header.compact_btn.setText("\u229f")
            self.header.compact_btn.setToolTip(self.tr.t("compact_mode") if self.tr else "Compact Mode")

    def _on_anim_tick(self):
        self.header.on_anim_tick()
        self.header.update()
        self.keyboard_widget.update()
        if self.heatmap_enabled:
            self.heatmap_legend.update()
        if self.incognito_active:
            self.incognito_overlay.update()
        if self.overlay and self.overlay.isVisible():
            session_dur = self.tracker.get_session_duration()
            aggregated = self.db.get_aggregated_stats(self.viewing_profile)
            keys_data = aggregated.get("keys", {})
            total = sum(keys_data.values())
            top_key_str = "None (0%)"
            if keys_data:
                top_k = max(keys_data, key=keys_data.get)
                pct = (keys_data[top_k] / total * 100) if total > 0 else 0
                top_key_str = f"{top_k} ({pct:.1f}%)"
            apm, wpm = self.tracker.get_apm_wpm()
            self.overlay.update_data(apm=apm, wpm=wpm, session=session_dur, profile=self.viewing_profile, top_key=top_key_str)

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

    def _build_config_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        lbl_sel = QLabel(self.tr.t("select_profile") if self.tr else "SELECT PROFILE")
        layout.addWidget(lbl_sel)
        
        profile_row = QHBoxLayout()
        profile_row.setSpacing(6)
        profile_row.setContentsMargins(0, 0, 0, 0)
        self.profile_btn_group = QButtonGroup(self)
        self.profile_btn_group.setExclusive(True)
        self.chips = {}
        for name, icon in [("Total", "\U0001f310"), ("Desktop", "\U0001f5a5\ufe0f"), ("Gaming", "\U0001f3ae")]:
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
        self.profile_combobox.setPlaceholderText("custom \u25be")
        self.profile_combobox.setCurrentIndex(-1)
        self.profile_combobox.currentTextChanged.connect(self._on_custom_profile_selected)
        profile_row.addWidget(self.profile_combobox)
        
        add_btn = QPushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.clicked.connect(self._create_profile_dialog)
        profile_row.addWidget(add_btn)
        
        self.del_profile_btn = QPushButton("\U0001f5d1")
        self.del_profile_btn.setFixedSize(28, 28)
        self.del_profile_btn.clicked.connect(self._delete_active_profile)
        self.del_profile_btn.setVisible(False)
        profile_row.addWidget(self.del_profile_btn)
        
        profile_row.addStretch()
        layout.addLayout(profile_row)
        
        layout.addStretch()
        
        hint = QLabel("Open \u2699 Settings for more options")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)
        
        layout.addStretch()
        return tab

    def _build_telemetry_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)
        
        self.session_card = MiniCard()
        sc_layout = QVBoxLayout(self.session_card)
        sc_layout.setContentsMargins(12, 10, 12, 10)
        self.sc_title = QLabel(self.tr.t("session") if self.tr else "Session")
        sc_layout.addWidget(self.sc_title)
        self.session_time_lbl = QLabel("00:00:00")
        self.session_time_lbl.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        sc_layout.addWidget(self.session_time_lbl)
        self.session_keys_lbl = QLabel("Keys: 0")
        sc_layout.addWidget(self.session_keys_lbl)
        self.error_ratio_lbl = QLabel("\u232b Ratio: 0.0%")
        sc_layout.addWidget(self.error_ratio_lbl)
        sc_layout.addStretch()
        layout.addWidget(self.session_card)
        
        self.leader_card = MiniCard()
        lc_layout = QVBoxLayout(self.leader_card)
        lc_layout.setContentsMargins(12, 10, 12, 10)
        self.lc_title = QLabel(self.tr.t("top_keys") if self.tr else "Top Keys")
        lc_layout.addWidget(self.lc_title)
        self.top_keys_labels = []
        for i in range(3):
            lbl = QLabel(f"{i+1}. \u2014")
            lbl.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
            lc_layout.addWidget(lbl)
            self.top_keys_labels.append(lbl)
        self.combo_title = QLabel(self.tr.t("top_combos") if self.tr else "Top Combos")
        lc_layout.addWidget(self.combo_title)
        self.top_combos_labels = []
        for i in range(2):
            lbl = QLabel(f"{i+1}. \u2014")
            lbl.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
            lc_layout.addWidget(lbl)
            self.top_combos_labels.append(lbl)
        lc_layout.addStretch()
        layout.addWidget(self.leader_card)
        
        self.burst_card = MiniCard()
        bc_layout = QVBoxLayout(self.burst_card)
        bc_layout.setContentsMargins(12, 10, 12, 10)
        self.bc_title = QLabel(self.tr.t("bursts") if self.tr else "Bursts")
        bc_layout.addWidget(self.bc_title)
        self.total_bursts_lbl = QLabel("0 recorded")
        self.total_bursts_lbl.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        bc_layout.addWidget(self.total_bursts_lbl)
        self.records_title = QLabel(self.tr.t("records") if self.tr else "Records")
        bc_layout.addWidget(self.records_title)
        self.burst_labels = []
        for i in range(3):
            lbl = QLabel(f"{i+1}. \u2014")
            lbl.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
            bc_layout.addWidget(lbl)
            self.burst_labels.append(lbl)
        bc_layout.addStretch()
        layout.addWidget(self.burst_card)
        return tab

    def _build_chart_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 12, 15, 12)
        self.hourly_chart = HourlyChartWidget(tr=self.tr)
        layout.addWidget(self.hourly_chart)
        return tab

    def _change_language(self, index):
        codes = ["en", "it"]
        code = codes[index] if index < len(codes) else "en"
        self.settings.set("language", code)
        self.settings_drawer.lang_notice.setText(self.tr.t("restart_notice") if self.tr else "Restart to apply")
        self.settings_drawer.lang_notice.setVisible(True)
        QTimer.singleShot(3000, lambda: self.settings_drawer.lang_notice.setVisible(False))

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
            is_tracking = not self.tracker.incognito_mode
            self.header.update_stats(apm, wpm, is_tracking)
            session_dur = self.tracker.get_session_duration()
            self.session_time_lbl.setText(session_dur)
            aggregated = self.db.get_aggregated_stats(self.viewing_profile)
            total_keys = sum(aggregated.get("keys", {}).values())
            self.session_keys_lbl.setText(f"Keys: {total_keys}")
            keys_data = aggregated.get("keys", {})
            total_clicks = sum(keys_data.values())
            backspace_clicks = keys_data.get("Backspace", 0) + keys_data.get("Delete", 0)
            ratio = (backspace_clicks / total_clicks) * 100 if total_clicks > 0 else 0.0
            self.error_ratio_lbl.setText(f"\u232b Ratio: {ratio:.1f}%")
            sorted_keys = sorted(keys_data.items(), key=lambda x: x[1], reverse=True)[:len(self.top_keys_labels)]
            for idx in range(len(self.top_keys_labels)):
                lbl = self.top_keys_labels[idx]
                if idx < len(sorted_keys):
                    k, count = sorted_keys[idx]
                    k_lbl = "Space" if k == "Space" else ("Num" + k.replace("Kp_", "") if k.startswith("Kp_") else k)
                    lbl.setText(f"{idx+1}. {k_lbl} : {count}")
                else:
                    lbl.setText(f"{idx+1}. \u2014")
            sorted_combos = sorted(aggregated.get("combinations", {}).items(), key=lambda x: x[1], reverse=True)[:len(self.top_combos_labels)]
            for idx in range(len(self.top_combos_labels)):
                lbl = self.top_combos_labels[idx]
                if idx < len(sorted_combos):
                    combo, count = sorted_combos[idx]
                    lbl.setText(f"{idx+1}. {combo} : {count}")
                else:
                    lbl.setText(f"{idx+1}. \u2014")
            bursts = self.db.get_burst_records(self.viewing_profile)
            self.total_bursts_lbl.setText(f"{len(bursts)} recorded")
            for idx in range(len(self.burst_labels)):
                lbl = self.burst_labels[idx]
                if idx < len(bursts):
                    record = bursts[idx]
                    lbl.setText(f"{idx+1}. {record['peak_apm']}APM {record['duration']}s")
                else:
                    lbl.setText(f"{idx+1}. \u2014")
            profile_data = self.db.get_stats_for_profile(self.viewing_profile)
            hourly_data = profile_data.get("hourly", {})
            self.hourly_chart.set_data(hourly_data)
            self.keyboard_widget.key_stats = keys_data
            
            ts = self.current_tokens.text_secondary
            for lbl in [self.sc_title, self.lc_title, self.combo_title, self.bc_title, self.records_title]:
                lbl.setStyleSheet(f"color: {ts}; font-size: 11px; font-weight: bold; background: transparent;")
            for lbl in [self.session_keys_lbl, self.error_ratio_lbl]:
                lbl.setStyleSheet(f"color: {ts}; font-size: 12px; background: transparent;")
            for lbls in [self.top_keys_labels, self.top_combos_labels, self.burst_labels]:
                for lbl in lbls:
                    lbl.setStyleSheet(f"color: {ts}; font-size: 12px; font-family: Consolas; font-weight: bold; background: transparent;")

            if getattr(self, "del_profile_btn", None):
                self.del_profile_btn.setStyleSheet("background: #A63A50; color: #FFFFFF; border: none;")
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
            mirror_map = {"Kp_enter": "Enter", "Shift_R": "Shift_L", "Ctrl_R": "Ctrl_L", "Alt_R": "Alt_L", "Win_R": "Win_L"}
            if count == 0 and key_id in mirror_map:
                count = keys_counts.get(mirror_map[key_id], 0)
            visible_counts.append(count)
        max_count = max(visible_counts) if visible_counts else 0
        color_map = {}
        for i, key_id in enumerate(all_ids):
            factor = visible_counts[i] / max_count if max_count > 0 else 0.0
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
        self.settings.set("keyboard_theme", name)
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
        else:
            self.incognito_overlay.deactivate()

    @pyqtSlot(bool)
    def _do_set_incognito(self, active):
        self.set_incognito(active)

    def _toggle_overlay_check(self, state):
        enabled = bool(state)
        self.db.set_overlay_enabled(enabled)
        if enabled:
            if not self.overlay:
                from overlay import FloatingOverlay
                self.overlay = FloatingOverlay(parent_ui=self, settings=self.settings)
                self.overlay.update_theme(self.current_tokens.accent, self.settings.get("theme") == "light")
                self.overlay.show()
        else:
            if self.overlay:
                self.overlay.close()
                self.overlay = None

    def toggle_overlay(self):
        ch = self.settings_drawer.overlay_check
        ch.setChecked(not ch.isChecked())

    def _toggle_startup(self, state):
        utils.set_startup(bool(state))

    def _get_custom_profiles(self):
        return [p for p in self.db.get_profiles() if p not in ("Total", "Desktop", "Gaming")]

    def _update_chip_styles(self):
        accent = self.current_tokens.accent
        brd = self.current_tokens.border
        ts = self.current_tokens.text_secondary
        selected_style = f"background-color: rgba({int(accent[1:3],16)},{int(accent[3:5],16)},{int(accent[5:7],16)},0.15); border: 1px solid {accent}; color: {accent}; border-radius: 14px; padding: 0 14px; font-size: 13px;"
        unselected_style = f"background-color: transparent; border: 1px solid {brd}; color: {ts}; border-radius: 14px; padding: 0 14px; font-size: 13px;"
        for name, btn in self.chips.items():
            if name == self.viewing_profile:
                btn.setStyleSheet(selected_style)
                btn.setChecked(True)
            else:
                btn.setStyleSheet(unselected_style)
                btn.setChecked(False)

    def update_profile_selector_ui(self):
        self._update_chip_styles()
        custom_profiles = self._get_custom_profiles()
        self.profile_combobox.blockSignals(True)
        self.profile_combobox.clear()
        self.profile_combobox.addItems(custom_profiles)
        if self.viewing_profile in ("Total", "Desktop", "Gaming"):
            self.profile_combobox.setCurrentIndex(-1)
            self.del_profile_btn.setVisible(False)
        else:
            idx = self.profile_combobox.findText(self.viewing_profile)
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
        title = self.tr.t("add_profile") if self.tr else "Add Profile"
        prompt = self.tr.t("add_profile_prompt") if self.tr else "Enter new profile name:"
        name, ok = QInputDialog.getText(self, title, prompt)
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
                QMessageBox.warning(self, "Error", "Profile already exists.")

    def _delete_active_profile(self):
        profile = self.viewing_profile
        if profile in ("Default", "Total", "Desktop", "Gaming"):
            QMessageBox.warning(self, "Error", "Cannot delete default profiles.")
            return
        reply = QMessageBox.question(self, "Delete Profile", f"Delete '{profile}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
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
        self.settings_drawer.incognito_check.setChecked(value)
        self._toggle_incognito(value)

    def _open_mappings_dialog(self):
        dialog = ProcessMappingDialog(self, self.db, tr=self.tr, tokens=self.current_tokens)
        dialog.exec()

    def _open_about_dialog(self):
        dialog = AboutDialog(self, tr=self.tr, tokens=self.current_tokens)
        dialog.exec()

    def _open_export_dialog(self):
        dialog = ExportDialog(self, db=self.db, viewing_profile=self.viewing_profile, tr=self.tr, tokens=self.current_tokens)
        dialog.exec()

    def _reset_statistics_dialog(self):
        reply = QMessageBox.question(self, "Reset Profile", f"Reset statistics for '{self.viewing_profile}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.reset_profile_statistics(self.viewing_profile)
            self._update_heatmap_colors()
            self.update_ui_stats()

    def withdraw_to_tray(self):
        self.hide()

    def restore_from_tray(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def process_event_queue(self, event_queue):
        self._event_queue = event_queue

    def handle_thread_event(self, event_type, val):
        try:
            if event_type == "keystroke":
                self.keyboard_widget.add_ripple(val)
                self.update_ui_stats()
            elif event_type == "incognito":
                self.set_incognito(val)
            elif event_type == "restore":
                self.restore_from_tray()
            elif event_type == "toggle_incognito":
                self.tracker.toggle_incognito()
            elif event_type == "toggle_overlay":
                self.toggle_overlay()
            elif event_type == "burst_detected":
                self.update_ui_stats()
            elif event_type == "profile_changed":
                old_profile = self.viewing_profile
                self.viewing_profile = val
                self.update_profile_selector_ui()
                self.trigger_profile_switch_animation(old_profile, val)
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

    def winfo_pointerx(self):
        return QCursor.pos().x()

    def winfo_pointery(self):
        return QCursor.pos().y()

    def winfo_rootx(self):
        return self.mapToGlobal(self.rect().topLeft()).x()

    def winfo_rooty(self):
        return self.mapToGlobal(self.rect().topLeft()).y()

    def winfo_width(self):
        return self.width()

    def winfo_height(self):
        return self.height()
