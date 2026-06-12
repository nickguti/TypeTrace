import sys

with open("ui.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: _process_queue crash
old_process = "        self.header.update_stats(self.tracker.current_apm, self.tracker.current_wpm, self.tracker.is_tracking)"
new_process = """        apm, wpm = self.tracker.get_apm_wpm()
        is_tracking = not getattr(self.tracker, "incognito_mode", False)
        self.header.update_stats(apm, wpm, is_tracking)"""
if old_process in content:
    content = content.replace(old_process, new_process)
else:
    print("Failed to find process_queue crash line.")

# Fix 2: Drawer overlapping text (remove paintEvent text/line drawing)
old_paint = """    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), hex_to_qcolor(self.tokens.bg_panel))
        
        painter.fillRect(QRect(0, 0, 4, self.height()), hex_to_qcolor(self.tokens.accent))
        
        painter.fillRect(self.title_bar.geometry(), hex_to_qcolor(self.tokens.bg_window))
        
        painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
        painter.drawLine(0, self.title_bar.height() - 1, self.width(), self.title_bar.height() - 1)
        
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), QLabel) and item.widget().property("is_section_header"):
                w = item.widget()
                geo = w.geometry()
                y = geo.bottom() + 4
                painter.setPen(QPen(hex_to_qcolor(self.tokens.border), 1.0))
                painter.drawLine(geo.left(), y, geo.right(), y)
                painter.setPen(hex_to_qcolor(self.tokens.text_secondary))
                painter.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
                painter.drawText(geo, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, w.text())
        
        painter.end()"""

new_paint = """    def _on_kb_layout_change(self, text):
        if self.parent():
            self.parent().settings_mgr.set("keyboard_layout", text)
            if hasattr(self.parent(), "heatmap"):
                self.parent().heatmap.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), hex_to_qcolor(self.tokens.bg_panel))
        
        painter.fillRect(QRect(0, 0, 4, self.height()), hex_to_qcolor(self.tokens.accent))
        
        painter.fillRect(self.title_bar.geometry(), hex_to_qcolor(self.tokens.bg_window))
        
        painter.end()"""
if old_paint in content:
    content = content.replace(old_paint, new_paint)
else:
    print("Failed to find SettingsDrawer paintEvent.")

# Fix 3: set_tokens QSS fix
old_qss = """                    if w.property("is_section_header"):
                        w.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 11px; font-weight: 600; letter-spacing: 1px; background: transparent;")"""
new_qss = """                    if w.property("is_section_header"):
                        w.setStyleSheet(f"color: {self.tokens.text_secondary}; font-size: 11px; font-weight: 600; letter-spacing: 1px; background: transparent; border-bottom: 1px solid {self.tokens.border}; padding-bottom: 4px;")"""
if old_qss in content:
    content = content.replace(old_qss, new_qss)
else:
    print("Failed to find set_tokens qss line.")

# Fix 4: Add keyboard layout setting
old_drawer_init = """        kb_theme_row = QHBoxLayout()
        kb_theme_row.addWidget(QLabel("Heatmap Theme:"))
        self.kb_theme_combo = QComboBox()
        self.kb_theme_combo.addItems(list(KEYBOARD_THEMES.keys()))
        self.kb_theme_combo.currentTextChanged.connect(self._on_kb_theme_change)
        kb_theme_row.addWidget(self.kb_theme_combo)
        self.content_layout.addLayout(kb_theme_row)
        
        print("Drawer section Interface")"""
new_drawer_init = """        kb_theme_row = QHBoxLayout()
        kb_theme_row.addWidget(QLabel("Heatmap Theme:"))
        self.kb_theme_combo = QComboBox()
        self.kb_theme_combo.addItems(list(KEYBOARD_THEMES.keys()))
        self.kb_theme_combo.currentTextChanged.connect(self._on_kb_theme_change)
        kb_theme_row.addWidget(self.kb_theme_combo)
        self.content_layout.addLayout(kb_theme_row)
        
        kb_layout_row = QHBoxLayout()
        kb_layout_row.addWidget(QLabel("Keyboard Layout:"))
        self.kb_layout_combo = QComboBox()
        self.kb_layout_combo.addItems(["100%", "TKL"])
        self.kb_layout_combo.currentTextChanged.connect(self._on_kb_layout_change)
        kb_layout_row.addWidget(self.kb_layout_combo)
        self.content_layout.addLayout(kb_layout_row)
        
        print("Drawer section Interface")"""
if old_drawer_init in content:
    content = content.replace(old_drawer_init, new_drawer_init)
else:
    print("Failed to find drawer init kb layout section.")

old_sync = """        kb = settings_mgr.get("heatmap_theme")
        self.kb_theme_combo.setCurrentText(kb if kb in KEYBOARD_THEMES else "Classic Heatmap")
        self.kb_theme_combo.blockSignals(False)
        
        self.lang_combo.blockSignals(True)"""
new_sync = """        kb = settings_mgr.get("heatmap_theme")
        self.kb_theme_combo.setCurrentText(kb if kb in KEYBOARD_THEMES else "Classic Heatmap")
        self.kb_theme_combo.blockSignals(False)
        
        self.kb_layout_combo.blockSignals(True)
        self.kb_layout_combo.setCurrentText(settings_mgr.get("keyboard_layout", "100%"))
        self.kb_layout_combo.blockSignals(False)
        
        self.lang_combo.blockSignals(True)"""
if old_sync in content:
    content = content.replace(old_sync, new_sync)
else:
    print("Failed to find sync settings section.")

# Fix 5: KeyboardHeatmapWidget scaling & aspect ratio
old_rect = """    def _compute_draw_rect(self):
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
        return QRectF(offset_x, offset_y, draw_w, draw_h)"""
new_rect = """    def _compute_draw_rect(self):
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return QRectF(0, 0, 0, 0), 1.10, "100%"
            
        fmt = self.parent_ui.settings_mgr.get("keyboard_layout", "100%") if self.parent_ui else "100%"
        ar = 4.4 if fmt == "100%" else 3.6
        max_rx = 1.10 if fmt == "100%" else 0.88
        
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
        return QRectF(offset_x, offset_y, draw_w, draw_h), max_rx, fmt"""
if old_rect in content:
    content = content.replace(old_rect, new_rect)
else:
    print("Failed to find _compute_draw_rect")

old_p_rect = """        draw_rect = self._compute_draw_rect()
        if draw_rect.width() < 50 or draw_rect.height() < 20:"""
new_p_rect = """        draw_rect, max_rx, fmt = self._compute_draw_rect()
        if draw_rect.width() < 50 or draw_rect.height() < 20:"""
content = content.replace(old_p_rect, new_p_rect)

old_p_loop = """        for key in KEYBOARD_LAYOUT:
            key_id = key["id"]
            px = draw_rect.x() + key["rx"] * draw_rect.width()
            py = draw_rect.y() + key["ry"] * draw_rect.height()
            pw = key["rw"] * draw_rect.width()
            ph = key["rh"] * draw_rect.height()"""
new_p_loop = """        for key in KEYBOARD_LAYOUT:
            if fmt == "TKL" and key["rx"] > 0.86:
                continue
            key_id = key["id"]
            px = draw_rect.x() + (key["rx"] / max_rx) * draw_rect.width()
            py = draw_rect.y() + key["ry"] * draw_rect.height()
            pw = (key["rw"] / max_rx) * draw_rect.width()
            ph = key["rh"] * draw_rect.height()"""
content = content.replace(old_p_loop, new_p_loop)

old_hit_loop = """        draw_rect = self._compute_draw_rect()
        for key in KEYBOARD_LAYOUT:
            key_id = key["id"]
            px = draw_rect.x() + key["rx"] * draw_rect.width()
            py = draw_rect.y() + key["ry"] * draw_rect.height()
            pw = key["rw"] * draw_rect.width()
            ph = key["rh"] * draw_rect.height()"""
new_hit_loop = """        draw_rect, max_rx, fmt = self._compute_draw_rect()
        for key in KEYBOARD_LAYOUT:
            if fmt == "TKL" and key["rx"] > 0.86:
                continue
            key_id = key["id"]
            px = draw_rect.x() + (key["rx"] / max_rx) * draw_rect.width()
            py = draw_rect.y() + key["ry"] * draw_rect.height()
            pw = (key["rw"] / max_rx) * draw_rect.width()
            ph = key["rh"] * draw_rect.height()"""
content = content.replace(old_hit_loop, new_hit_loop)


# Fix 6: Add theme transition animation
old_theme = """    def change_theme_mode(self, mode_str: str):
        is_dark = (mode_str.lower() == "dark")
        if is_dark == self.is_dark_mode:
            return
        self.is_dark_mode = is_dark
        self.settings_mgr.set("theme", mode_str.lower())
        base = DARK_TOKENS if is_dark else LIGHT_TOKENS
        new_tokens = replace(base, accent=self.settings_mgr.get("accent_color"))
        self._apply_theme(new_tokens)"""

new_theme = """    def change_theme_mode(self, mode_str: str):
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
        self.transition_anim.start()"""
if old_theme in content:
    content = content.replace(old_theme, new_theme)
else:
    print("Failed to find change_theme_mode")

with open("ui.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixes applied successfully via python script.")
