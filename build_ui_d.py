#!/usr/bin/env python3
"""Build script part D for ui.py: SettingsDrawer and TypeTraceUI."""
import os

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.py")

PART_D = r'''
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
'''

with open(TARGET, "a", encoding="utf-8") as f:
    f.write(PART_D)
print(f"Part D written. Lines: {sum(1 for _ in open(TARGET, encoding='utf-8'))}")
