#!/usr/bin/env python3
"""Build script part B for ui.py: HeaderWidget, KeyTooltip, LegendBarWidget, KeyboardHeatmapWidget."""
import os

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.py")

PART_B = r'''
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
'''

with open(TARGET, "a", encoding="utf-8") as f:
    f.write(PART_B)
print(f"Part B written. Lines: {sum(1 for _ in open(TARGET, encoding='utf-8'))}")
