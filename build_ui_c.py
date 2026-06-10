#!/usr/bin/env python3
"""Build script part C for ui.py: HourlyChartWidget, MiniCard, IncognitoOverlay, WelcomeDialog, ExportDialog, ProcessMappingDialog, AboutDialog."""
import os

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.py")

PART_C = r'''
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
'''

with open(TARGET, "a", encoding="utf-8") as f:
    f.write(PART_C)
print(f"Part C written. Lines: {sum(1 for _ in open(TARGET, encoding='utf-8'))}")
