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



# Stessa famiglia usata dalla finestra principale: "Inter" non fa parte di
# Windows e il testo ricadeva su un ripiego diverso da quello del resto della UI.
FONT_FAMILY = "Segoe UI Variable"


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
            self._accent_hex = settings.get("accent_color") or "#00F5D4"
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
        # "peak" era elencato fra i campi mostrabili ma non esisteva qui: la
        # riga "PEAK APM" restava percio' sempre vuota.
        self._data = {"apm": 0, "wpm": 0, "peak": 0, "session": "00:00:00",
                      "profile": "Default", "top_key": "Space (0%)"}
        self._drag_pos = QPoint()
        self._dragging = False
        self._resizing = False
        self._resize_start_pos = QPoint()
        self._resize_start_size = None
        self._grip_size = 14
        self._scale = 1.0
        if self._settings and self._settings.get("overlay_scale"):
            self._scale = self._settings.get("overlay_scale")
        self._recalc_size()
        self._restore_position()

    def _recalc_size(self):
        scale = getattr(self, '_scale', 1.0)
        row_h = 24
        logical_h = 16 + len(self._visible_fields) * row_h + 8
        logical_w = 200
        if self._settings:
            stored_w = self._settings.get("overlay_width")
            # Si rispetta la larghezza scelta dall'utente: prima un max() la
            # riportava sempre ad almeno 200 px, annullando i ridimensionamenti
            # piu' stretti appena salvati.
            if stored_w:
                logical_w = max(140, stored_w / scale)
            stored_h = self._settings.get("overlay_height")
            if stored_h and stored_h > (logical_h * scale):
                logical_h = stored_h / scale
        self.resize(max(int(logical_w * scale), int(140 * scale)), max(int(logical_h * scale), int(50 * scale)))

    def _restore_position(self):
        """Rimette l'overlay dove l'utente lo aveva lasciato, se e' ancora visibile.

        La posizione salvata veniva applicata senza controlli: bastava scollegare
        un monitor per ritrovarsi le coordinate di uno schermo che non c'e' piu'
        (per esempio x=-291) e un widget irraggiungibile, che non si puo'
        nemmeno trascinare indietro.
        """
        from PyQt6.QtWidgets import QApplication

        ox = None
        oy = None
        if self._settings:
            ox = self._settings.get("overlay_x")
            oy = self._settings.get("overlay_y")

        if ox is not None and oy is not None and self._is_on_a_screen(int(ox), int(oy)):
            self.move(int(ox), int(oy))
            return

        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.right() - self.width() - 20, geo.bottom() - self.height() - 20)

    def _is_on_a_screen(self, x, y):
        """True se il rettangolo dell'overlay ricade in un'area visibile."""
        from PyQt6.QtCore import QRect
        from PyQt6.QtWidgets import QApplication

        rect = QRect(x, y, max(self.width(), 40), max(self.height(), 30))
        for screen in QApplication.screens():
            if screen.availableGeometry().intersects(rect):
                # Serve una porzione visibile sufficiente ad afferrarlo col mouse
                visible = screen.availableGeometry().intersected(rect)
                if visible.width() >= 40 and visible.height() >= 20:
                    return True
        return False

    def reset_position(self):
        """Riporta l'overlay in basso a destra sullo schermo principale."""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.right() - self.width() - 20, geo.bottom() - self.height() - 20)
            if self._settings:
                self._settings.set("overlay_x", self.x())
                self._settings.set("overlay_y", self.y())

    def activate(self):
        self.show()
        self.raise_()

    def deactivate(self):
        self.hide()

    def apply_settings(self):
        if not self._settings:
            return
        show_apm = self._settings.get("overlay_show_apm") if self._settings.get("overlay_show_apm") is not None else True
        show_wpm = self._settings.get("overlay_show_wpm") if self._settings.get("overlay_show_wpm") is not None else True
        show_peak = self._settings.get("overlay_show_peak") if self._settings.get("overlay_show_peak") is not None else False
        show_profile = self._settings.get("overlay_show_profile") if self._settings.get("overlay_show_profile") is not None else True
        opacity = self._settings.get("overlay_opacity") if self._settings.get("overlay_opacity") is not None else 1.0
        scale = self._settings.get("overlay_scale") if self._settings.get("overlay_scale") is not None else 1.0
        
        fields = []
        if show_apm: fields.append("apm")
        if show_wpm: fields.append("wpm")
        if show_peak: fields.append("peak")
        if show_profile: fields.append("profile")

        # Spegnendo tutte e quattro le voci restava un rettangolo vuoto senza
        # alcun modo di capire cosa fosse: si tiene sempre almeno l'APM.
        if not fields:
            fields = ["apm"]

        self._visible_fields = fields
        self.setWindowOpacity(opacity)
        self._scale = scale
        
        self._recalc_size()
        self.update()

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

    def update_data(self, apm=0, wpm=0, session="00:00:00", profile="Default",
                    top_key="Space (0%)", peak=None):
        self._data["apm"] = apm
        self._data["wpm"] = wpm
        self._data["session"] = session
        self._data["profile"] = profile
        self._data["top_key"] = top_key
        if peak is not None:
            self._data["peak"] = peak
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
        
        scale = getattr(self, '_scale', 1.0)
        painter.scale(scale, scale)
        logical_w = self.width() / scale
        logical_h = self.height() / scale

        bg = self._hex_to_qc(self._bg_color)
        bg.setAlpha(230)
        border_c = self._hex_to_qc(self._border_color)
        accent_c = self._hex_to_qc(self._accent_hex)
        text_c = self._hex_to_qc(self._text_primary)
        sec_c = self._hex_to_qc(self._text_secondary)
        
        rect = QRectF(0, 0, logical_w, logical_h)
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)
        painter.fillPath(path, bg)
        painter.setPen(QPen(border_c, 1.0))
        painter.drawPath(path)
        
        field_labels = {"apm": "APM", "wpm": "WPM", "session": "SESSION", "profile": "PROFILE", "top_key": "TOP KEY", "peak": "PEAK APM"}
        y = 10
        row_h = 24
        for fid in self._visible_fields:
            label_text = field_labels.get(fid, fid.upper())
            value_text = str(self._data.get(fid, ""))
            painter.setPen(sec_c)
            font_label = QFont(FONT_FAMILY, 10)
            painter.setFont(font_label)
            painter.drawText(QRectF(12, y, 80, row_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label_text)
            painter.setPen(accent_c)
            font_val = QFont(FONT_FAMILY, 13, QFont.Weight.Bold)
            painter.setFont(font_val)
            painter.drawText(QRectF(92, y, logical_w - 104, row_h), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, value_text)
            y += row_h
            
        grip_x = logical_w - self._grip_size
        grip_y = logical_h - self._grip_size
        painter.setPen(QPen(border_c, 1.5))
        for i in range(3):
            offset = 4 + i * 4
            painter.drawLine(int(grip_x + offset), int(logical_h - 4), int(logical_w - 4), int(grip_y + offset))
        painter.end()

    def _in_grip(self, pos):
        scale = getattr(self, '_scale', 1.0)
        grip_phys = self._grip_size * scale
        return (pos.x() >= self.width() - grip_phys and pos.y() >= self.height() - grip_phys)

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
            scale = getattr(self, '_scale', 1.0)
            new_w = max(140 * scale, self._resize_start_size.width() + delta.x())
            new_h = max(50 * scale, self._resize_start_size.height() + delta.y())
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
        close_action = menu.addAction("Close Overlay")
        action = menu.exec(event.globalPos())
        if action == close_action:
            self.deactivate()
