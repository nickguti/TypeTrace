#!/usr/bin/env python3
"""Build script part A for ui.py: Imports, ThemeTokens, QSS Template, SettingsManager."""
import os

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.py")

PART_A = r'''import sys
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
    QColorDialog, QGraphicsOpacityEffect, QMessageBox, QFileDialog, QScrollArea, QFrame, QGridLayout
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
'''

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(PART_A)
print(f"Part A written. Lines: {sum(1 for _ in open(TARGET, encoding='utf-8'))}")
