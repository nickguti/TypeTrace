# === overlay.py ===
import os
import json
import math
from PyQt6.QtWidgets import (
    QWidget, QMenu, QDialog, QVBoxLayout, QHBoxLayout,
    QCheckBox, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QPoint, QRectF, QPointF, QTime
from PyQt6.QtGui import (
    QMouseEvent, QPainter, QColor, QFont, QPen, QBrush,
    QPainterPath, QCursor, QFontMetrics
)


class OverlayFieldConfigDialog(QDialog):
    def __init__(self, parent_overlay):
        super().__init__(parent_overlay)
        self.parent_overlay = parent_overlay
        self.setWindowTitle("Configure Overlay Fields")
        self.setFixedSize(300, 320)
        bg = parent_overlay._bg_color
        text_c = parent_overlay._text_primary
        accent_c = parent_overlay._accent_hex
        self.setStyleSheet(f"background-color: {bg}; color: {text_c};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        title = QLabel("Select and reorder overlay fields:")
        title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {text_c};")
        layout.addWidget(title)
        self.field_checks = {}
        all_fields = ["apm", "wpm", "session", "profile", "top_key"]
        labels = {"apm": "APM", "wpm": "WPM", "session": "Session Timer", "profile": "Active Profile", "top_key": "Top Key"}
        current = parent_overlay._visible_fields[:]
        for fid in current:
            if fid in all_fields:
                cb = QCheckBox(labels.get(fid, fid))
                cb.setChecked(True)
                layout.addWidget(cb)
                self.field_checks[fid] = cb
        for fid in all_fields:
            if fid not in current:
                cb = QCheckBox(labels.get(fid, fid))
                cb.setChecked(False)
                layout.addWidget(cb)
                self.field_checks[fid] = cb
        btn_row = QHBoxLayout()
        up_btn = QPushButton("\u2191 Up")
        up_btn.setFixedHeight(28)
        up_btn.setStyleSheet(f"border: 1px solid #2F313D; color: {text_c}; background: transparent;")
        btn_row.addWidget(up_btn)
        down_btn = QPushButton("\u2193 Down")
        down_btn.setFixedHeight(28)
        down_btn.setStyleSheet(f"border: 1px solid #2F313D; color: {text_c}; background: transparent;")
        btn_row.addWidget(down_btn)
        layout.addLayout(btn_row)
        apply_btn = QPushButton("Apply")
        apply_btn.setFixedHeight(36)
        apply_btn.setStyleSheet(f"border: 1px solid {accent_c}; color: {accent_c}; background: transparent; font-weight: bold;")
        apply_btn.clicked.connect(self._apply)
        layout.addWidget(apply_btn)
        layout.addStretch()

    def _apply(self):
        selected = []
        for fid, cb in self.field_checks.items():
            if cb.isChecked():
                selected.append(fid)
        if not selected:
            selected = ["apm"]
        self.parent_overlay._visible_fields = selected
        if self.parent_overlay._settings:
            self.parent_overlay._settings.set("overlay_fields", selected)
        self.parent_overlay._recalc_size()
        self.parent_overlay.update()
        self.accept()


class FloatingOverlay(QWidget):
    def __init__(self, parent_ui=None, settings=None):
        super().__init__(None)
        self._parent_ui = parent_ui
        self._settings = settings
        self._accent_hex = "#00F5D4"
        self._bg_color = "#171A23"
        self._border_color = "#2F313D"
        self._text_primary = "#FFFFFF"
        self._text_secondary = "#8E9297"
        self._is_light = False
        if settings:
            self._accent_hex = settings.get("accent_color")
            theme = settings.get("theme")
            if theme == "light":
                self._is_light = True
                self._bg_color = "#FFFFFF"
                self._border_color = "#D0D3DB"
                self._text_primary = "#1A1C23"
                self._text_secondary = "#6B7280"
        self.setWindowTitle("TypeTrace Overlay")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._visible_fields = ["apm", "wpm"]
        if settings:
            stored = settings.get("overlay_fields")
            if isinstance(stored, list) and len(stored) > 0:
                self._visible_fields = stored
        self._data = {"apm": 0, "wpm": 0, "session": "00:00:00", "profile": "Default", "top_key": "Space (0%)"}
        self._drag_pos = QPoint()
        self._dragging = False
        self._resizing = False
        self._resize_start_pos = QPoint()
        self._resize_start_size = None
        self._grip_size = 14
        self._recalc_size()
        self._restore_position()

    def _recalc_size(self):
        row_h = 24
        h = 16 + len(self._visible_fields) * row_h + 8
        w = 200
        if self._settings:
            w = self._settings.get("overlay_width") or 200
            stored_h = self._settings.get("overlay_height")
            if stored_h and stored_h > h:
                h = stored_h
        self.resize(max(w, 140), max(h, 50))

    def _restore_position(self):
        ox = None
        oy = None
        if self._settings:
            ox = self._settings.get("overlay_x")
            oy = self._settings.get("overlay_y")
        if ox is not None and oy is not None:
            self.move(int(ox), int(oy))
        else:
            screen = self.screen()
            if screen:
                geo = screen.availableGeometry()
                self.move(geo.right() - self.width() - 20, geo.bottom() - self.height() - 20)

    def update_theme(self, accent_hex, is_light):
        self._accent_hex = accent_hex
        self._is_light = is_light
        if is_light:
            self._bg_color = "#FFFFFF"
            self._border_color = "#D0D3DB"
            self._text_primary = "#1A1C23"
            self._text_secondary = "#6B7280"
        else:
            self._bg_color = "#171A23"
            self._border_color = "#2F313D"
            self._text_primary = "#FFFFFF"
            self._text_secondary = "#8E9297"
        self.update()

    def update_data(self, apm=0, wpm=0, session="00:00:00", profile="Default", top_key="Space (0%)"):
        self._data["apm"] = apm
        self._data["wpm"] = wpm
        self._data["session"] = session
        self._data["profile"] = profile
        self._data["top_key"] = top_key
        self.update()

    def update_stats(self, apm, wpm):
        self._data["apm"] = apm
        self._data["wpm"] = wpm
        self.update()

    def _hex_to_qc(self, h):
        h = h.lstrip('#')
        return QColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = self._hex_to_qc(self._bg_color)
        bg.setAlpha(230)
        border_c = self._hex_to_qc(self._border_color)
        accent_c = self._hex_to_qc(self._accent_hex)
        text_c = self._hex_to_qc(self._text_primary)
        sec_c = self._hex_to_qc(self._text_secondary)
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)
        painter.fillPath(path, bg)
        painter.setPen(QPen(border_c, 1.0))
        painter.drawPath(path)
        field_labels = {"apm": "APM", "wpm": "WPM", "session": "SESSION", "profile": "PROFILE", "top_key": "TOP KEY"}
        y = 10
        row_h = 24
        for fid in self._visible_fields:
            label_text = field_labels.get(fid, fid.upper())
            value_text = str(self._data.get(fid, ""))
            painter.setPen(sec_c)
            font_label = QFont("Inter", 10)
            painter.setFont(font_label)
            painter.drawText(QRectF(12, y, 70, row_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label_text)
            painter.setPen(accent_c)
            font_val = QFont("Inter", 13, QFont.Weight.Bold)
            painter.setFont(font_val)
            painter.drawText(QRectF(82, y, self.width() - 94, row_h), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, value_text)
            y += row_h
        grip_x = self.width() - self._grip_size
        grip_y = self.height() - self._grip_size
        painter.setPen(QPen(border_c, 1.5))
        for i in range(3):
            offset = 4 + i * 4
            painter.drawLine(int(grip_x + offset), int(self.height() - 4), int(self.width() - 4), int(grip_y + offset))
        painter.end()

    def _in_grip(self, pos):
        return (pos.x() >= self.width() - self._grip_size and pos.y() >= self.height() - self._grip_size)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            local_pos = event.position().toPoint()
            if self._in_grip(local_pos):
                self._resizing = True
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_size = self.size()
            else:
                self._dragging = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        local_pos = event.position().toPoint()
        if self._resizing:
            delta = event.globalPosition().toPoint() - self._resize_start_pos
            new_w = max(140, self._resize_start_size.width() + delta.x())
            new_h = max(50, self._resize_start_size.height() + delta.y())
            self.resize(int(new_w), int(new_h))
            event.accept()
        elif self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        else:
            if self._in_grip(local_pos):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._resizing:
                self._resizing = False
                if self._settings:
                    self._settings.set("overlay_width", self.width())
                    self._settings.set("overlay_height", self.height())
            elif self._dragging:
                self._dragging = False
                if self._settings:
                    self._settings.set("overlay_x", self.x())
                    self._settings.set("overlay_y", self.y())
            event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        configure_action = menu.addAction("Configure Fields\u2026")
        close_action = menu.addAction("Close Overlay")
        action = menu.exec(event.globalPos())
        if action == configure_action:
            dlg = OverlayFieldConfigDialog(self)
            dlg.exec()
        elif action == close_action:
            self.hide()
            if self._parent_ui and hasattr(self._parent_ui, 'overlay_check'):
                self._parent_ui.overlay_check.setChecked(False)
