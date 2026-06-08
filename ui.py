import os
import json
import math
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter
from datetime import datetime
import logging
import queue
import webbrowser

import utils
from overlay import FloatingOverlay
from tracker import BUILTIN_GAMING_PROCESSES, BUILTIN_DESKTOP_PROCESSES
# App Constants
APP_VERSION = "1.1.0"
APP_GITHUB = "https://github.com/nickguti/TypeTrace"
# Set appearance mode and theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# =====================================================================
# Design Tokens
# =====================================================================
BG_MAIN = "#0B0C10"
BG_CARD = "#171A23"
BG_CARD_INNER = "#111318"
BORDER_COLOR = "#232733"
BORDER_INNER = "#1D1F2A"
ACCENT = "#00F5D4"
ACCENT_HOVER = "#00D4B4"
DANGER = "#A63A50"
DANGER_HOVER = "#C93B55"
KEYCAP_BASE = "#20222B"
KEYCAP_HOVER = "#2F313D"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#8E9297"
GRID_LINE = "#1F2330"

FONT_FAMILY = "Inter"

# Helper to resolve profile emoji based on type
def get_profile_emoji(profile_name):
    name_lower = profile_name.lower()
    if name_lower == "gaming":
        return "🎮"
    elif name_lower == "desktop":
        return "🖥️"
    elif name_lower == "total":
        return "🌐"
    else:
        return "👤"

# =====================================================================
# Rounded Rectangle Canvas Helper (High Performance Polygon)
# =====================================================================
def draw_rounded_rect(canvas, x0, y0, x1, y1, r=6, **kwargs):
    if r <= 0:
        return canvas.create_rectangle(x0, y0, x1, y1, **kwargs)
        
    points = []
    # Top-right corner
    cx, cy = x1 - r, y0 + r
    for i in range(10):
        angle = math.radians(270 + i * 10)
        points.append(cx + r * math.cos(angle))
        points.append(cy + r * math.sin(angle))
        
    # Bottom-right corner
    cx, cy = x1 - r, y1 - r
    for i in range(10):
        angle = math.radians(0 + i * 10)
        points.append(cx + r * math.cos(angle))
        points.append(cy + r * math.sin(angle))
        
    # Bottom-left corner
    cx, cy = x0 + r, y1 - r
    for i in range(10):
        angle = math.radians(90 + i * 10)
        points.append(cx + r * math.cos(angle))
        points.append(cy + r * math.sin(angle))
        
    # Top-left corner
    cx, cy = x0 + r, y0 + r
    for i in range(10):
        angle = math.radians(180 + i * 10)
        points.append(cx + r * math.cos(angle))
        points.append(cy + r * math.sin(angle))
        
    return canvas.create_polygon(points, **kwargs)

# =====================================================================
# 100% ANSI Keyboard Layout Definition
# =====================================================================
LEFT_KEYBOARD_LAYOUT = [
    # Row 0 (Function keys)
    [
        ("Esc", 4, "Esc"), ("spacer", 4, "spacer"), ("F1", 4, "F1"), ("F2", 4, "F2"), 
        ("F3", 4, "F3"), ("F4", 4, "F4"), ("spacer", 2, "spacer"), ("F5", 4, "F5"), 
        ("F6", 4, "F6"), ("F7", 4, "F7"), ("F8", 4, "F8"), ("spacer", 2, "spacer"), 
        ("F9", 4, "F9"), ("F10", 4, "F10"), ("F11", 4, "F11"), ("F12", 4, "F12")
    ],
    # Row 1 (Numbers Row)
    [
        ("`", 4, "`"), ("1", 4, "1"), ("2", 4, "2"), ("3", 4, "3"), ("4", 4, "4"),
        ("5", 4, "5"), ("6", 4, "6"), ("7", 4, "7"), ("8", 4, "8"), ("9", 4, "9"),
        ("0", 4, "0"), ("-", 4, "-"), ("=", 4, "="), ("Backspace", 8, "Backspace")
    ],
    # Row 2 (QWERTY Row)
    [
        ("Tab", 6, "Tab"), ("Q", 4, "Q"), ("W", 4, "W"), ("E", 4, "E"), ("R", 4, "R"),
        ("T", 4, "T"), ("Y", 4, "Y"), ("U", 4, "U"), ("I", 4, "I"), ("O", 4, "O"),
        ("P", 4, "P"), ("[", 4, "["), ("]", 4, "]"), ("\\", 6, "\\")
    ],
    # Row 3 (ASDF Row)
    [
        ("Caps", 7, "Caps"), ("A", 4, "A"), ("S", 4, "S"), ("D", 4, "D"), ("F", 4, "F"),
        ("G", 4, "G"), ("H", 4, "H"), ("J", 4, "J"), ("K", 4, "K"), ("L", 4, "L"),
        (";", 4, ";"), ("'", 4, "'"), ("Enter", 9, "Enter")
    ],
    # Row 4 (Shift Row)
    [
        ("Shift", 9, "Shift_L"), ("Z", 4, "Z"), ("X", 4, "X"), ("C", 4, "C"), ("V", 4, "V"),
        ("B", 4, "B"), ("N", 4, "N"), ("M", 4, "M"), (",", 4, ","), (".", 4, "."),
        ("/", 4, "/"), ("Shift ", 11, "Shift_R")
    ],
    # Row 5 (Modifiers Row)
    [
        ("Ctrl", 5, "Ctrl_L"), ("Win", 5, "Win_L"), ("Alt", 5, "Alt_L"), ("Space", 25, "Space"),
        ("Alt ", 5, "Alt_R"), ("Win ", 5, "Win_R"), ("Menu", 5, "Menu"), ("Ctrl ", 5, "Ctrl_R")
    ]
]

NAV_KEYBOARD_LAYOUT = [
    # Row 0
    [("PrtSc", 1, "Print_screen"), ("ScrLk", 1, "Scroll_lock"), ("Pause", 1, "Pause")],
    # Row 1
    [("Ins", 1, "Insert"), ("Home", 1, "Home"), ("PgUp", 1, "Page_up")],
    # Row 2
    [("Del", 1, "Delete"), ("End", 1, "End"), ("PgDn", 1, "Page_down")],
    # Row 3 (Empty Spacer Row)
    [("empty", 1, "spacer"), ("empty", 1, "spacer"), ("empty", 1, "spacer")],
    # Row 4
    [("spacer", 1, "spacer"), ("↑", 1, "Up"), ("spacer", 1, "spacer")],
    # Row 5
    [("←", 1, "Left"), ("↓", 1, "Down"), ("→", 1, "Right")]
]

# Numpad coordinates format: (Label, Row, Col, RowSpan, ColSpan, Database_Key_ID)
NUMPAD_KEYBOARD_LAYOUT = [
    ("spacer", 0, 0, 1, 4, "spacer"),
    ("Num", 1, 0, 1, 1, "Num_lock"), ("/", 1, 1, 1, 1, "Kp_/"), ("*", 1, 2, 1, 1, "Kp_*"), ("-", 1, 3, 1, 1, "Kp_-"),
    ("7", 2, 0, 1, 1, "Kp_7"), ("8", 2, 1, 1, 1, "Kp_8"), ("9", 2, 2, 1, 1, "Kp_9"), ("+", 2, 3, 2, 1, "Kp_+"),
    ("4", 3, 0, 1, 1, "Kp_4"), ("5", 3, 1, 1, 1, "Kp_5"), ("6", 3, 2, 1, 1, "Kp_6"),
    ("1", 4, 0, 1, 1, "Kp_1"), ("2", 4, 1, 1, 1, "Kp_2"), ("3", 4, 2, 1, 1, "Kp_3"), ("Ent", 4, 3, 2, 1, "Kp_enter"),
    ("0", 5, 0, 1, 2, "Kp_0"), (".", 5, 2, 1, 1, "Kp_.")
]

# =====================================================================
# Toast Notification System
# =====================================================================
class ToastNotification:
    """Temporary overlay notification that appears at the bottom-right of the window."""
    def __init__(self, parent, message, toast_type="success", duration=3000):
        self.parent = parent
        self.duration = duration
        
        if toast_type == "success":
            bg_color = "#111318"
            border_color = ACCENT
            text_color = ACCENT
            icon = "✓"
        elif toast_type == "error":
            bg_color = "#111318"
            border_color = DANGER
            text_color = DANGER
            icon = "✗"
        else:
            bg_color = "#111318"
            border_color = BORDER_COLOR
            text_color = TEXT_SECONDARY
            icon = "ℹ"
        
        self.frame = customtkinter.CTkFrame(
            parent,
            fg_color=bg_color,
            border_color=border_color,
            border_width=1,
            corner_radius=10
        )
        
        self.label = customtkinter.CTkLabel(
            self.frame,
            text=f" {icon}  {message}",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=text_color,
            anchor="w"
        )
        self.label.pack(padx=16, pady=10)
        
        self.frame.place(relx=1.0, rely=1.0, anchor="se", x=-30, y=-70)
        self.frame.lift()
        
        self._fade_step = 0
        parent.after(self.duration, self._start_fade)
    
    def _start_fade(self):
        self._fade_step += 1
        if self._fade_step >= 5:
            try:
                self.frame.destroy()
            except Exception:
                pass
            return
        try:
            self.frame.place(relx=1.0, rely=1.0, anchor="se", x=-30, y=-70 + (self._fade_step * 15))
            self.parent.after(50, self._start_fade)
        except Exception:
            pass

# =====================================================================
# Canvas-Based Tooltip INSIDE root window (BUG 1 FIXED)
# =====================================================================
class Tooltip:
    def __init__(self, widget, get_text_func, root_canvas_parent):
        self.widget = widget
        self.get_text_func = get_text_func
        self.root = root_canvas_parent  # the TypeTraceUI root window
        self._tip_frame = None
        self._schedule_id = None
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        widget.bind("<Motion>", self._on_motion)

    def _on_enter(self, event):
        self._schedule_id = self.widget.after(300, self._show)

    def _on_leave(self, event):
        if self._schedule_id:
            self.widget.after_cancel(self._schedule_id)
            self._schedule_id = None
        self._hide()

    def _on_motion(self, event):
        # Reposition tooltip if already visible
        if self._tip_frame and self._tip_frame.winfo_exists():
            self._reposition()

    def _show(self):
        self._hide()  # destroy any previous instance
        text = self.get_text_func()
        if not text:
            return

        # Place tooltip as a CTkFrame INSIDE the root window using place()
        self._tip_frame = customtkinter.CTkFrame(
            self.root,
            fg_color="#111318",
            border_color="#00F5D4",
            border_width=1,
            corner_radius=8
        )
        lbl = customtkinter.CTkLabel(
            self._tip_frame,
            text=text,
            justify="left",
            font=("Inter", 10),
            text_color="#FFFFFF",
            padx=12,
            pady=10
        )
        lbl.pack()

        # Calculate position relative to root window
        self._reposition()
        self._tip_frame.lift()  # bring above other widgets

    def _reposition(self):
        if not self._tip_frame:
            return
        # Get pointer position relative to root window
        rx = self.root.winfo_pointerx() - self.root.winfo_rootx() + 15
        ry = self.root.winfo_pointery() - self.root.winfo_rooty() + 15
        # Clamp so it doesn't go off-screen within the window
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        self._tip_frame.update_idletasks()
        tw = self._tip_frame.winfo_reqwidth()
        th = self._tip_frame.winfo_reqheight()
        if rx + tw > win_w - 10:
            rx = rx - tw - 30
        if ry + th > win_h - 10:
            ry = ry - th - 30
        self._tip_frame.place(x=rx, y=ry)

    def _hide(self):
        if self._tip_frame:
            try:
                self._tip_frame.destroy()
            except Exception:
                pass
            self._tip_frame = None

# =====================================================================
# Productivity Chart (24h bar chart)
# =====================================================================
class ProductivityChart(customtkinter.CTkCanvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_CARD, highlightthickness=0, **kwargs)
        self.last_hourly_data = {}
        self.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event):
        self.draw_chart(self.last_hourly_data)
        
    def draw_chart(self, hourly_data):
        self.last_hourly_data = hourly_data
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1: width = 500
        if height <= 1: height = 150
        
        hours_values = [0] * 24
        for hour_str, hour_stats in hourly_data.items():
            try:
                hour_part = int(hour_str.split("T")[1].split(":")[0])
                hours_values[hour_part] += sum(hour_stats.get("keys", {}).values())
            except Exception:
                pass
                
        max_val = max(hours_values)
        if max_val == 0:
            self.create_text(width // 2, height // 2, text="No productivity logs recorded yet.", fill=TEXT_SECONDARY, font=(FONT_FAMILY, 11))
            return
            
        padding_x = 25
        padding_y = 20
        chart_w = width - padding_x * 2
        chart_h = height - padding_y * 2
        
        total_chart_w = 24 * 18 - 12
        start_x = padding_x + (chart_w - total_chart_w) / 2
        if start_x < padding_x:
            start_x = padding_x
            
        grid_lines_count = 3
        for i in range(1, grid_lines_count + 1):
            y = height - padding_y - (chart_h * i / (grid_lines_count + 1))
            self.create_line(padding_x, y, width - padding_x, y, fill=GRID_LINE, width=1)
            
        self.create_line(padding_x, height - padding_y, width - padding_x, height - padding_y, fill=GRID_LINE, width=1)
        
        for hour in range(24):
            val = hours_values[hour]
            if val == 0:
                continue
            bar_h = (val / max_val) * chart_h
            
            x0 = start_x + hour * 18
            x1 = x0 + 6
            y1 = height - padding_y
            y0 = y1 - bar_h
            
            num_slices = int(max(4, bar_h // 2))
            for s in range(num_slices):
                sy0 = y0 + s * (bar_h / num_slices)
                sy1 = y0 + (s + 1) * (bar_h / num_slices)
                t = s / (num_slices - 1) if num_slices > 1 else 0.0
                r = int(0 + (23 - 0) * t)
                g = int(245 + (26 - 245) * t)
                b = int(212 + (35 - 212) * t)
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.create_rectangle(x0, sy0, x1, sy1, fill=color, outline="")
                
            self.create_oval(x0, y0 - 3, x1, y0 + 3, fill=ACCENT, outline="")
            
        for h in [0, 6, 12, 18, 23]:
            x = start_x + h * 18 + 3
            self.create_text(x, height - padding_y + 12, text=f"{h}h", fill=TEXT_SECONDARY, font=(FONT_FAMILY, 9))

# =====================================================================
# Heatmap Legend (Gradient bar)
# =====================================================================
class HeatmapLegend(customtkinter.CTkCanvas):
    """Thin horizontal gradient bar showing heatmap color scale."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_CARD, highlightthickness=0, height=24, **kwargs)
        self.current_theme = "Classic"
        self.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event=None):
        self.draw_legend(self.current_theme)
        
    def draw_legend(self, theme):
        self.current_theme = theme
        self.delete("all")
        width = self.winfo_width()
        if width <= 1:
            width = 400
        height = self.winfo_height()
        
        bar_y0 = 4
        bar_y1 = height - 4
        bar_x0 = 50
        bar_x1 = width - 50
        bar_w = bar_x1 - bar_x0
        
        if bar_w <= 0:
            return
            
        num_slices = min(bar_w, 100)
        for i in range(num_slices):
            t = i / max(1, num_slices - 1)
            color = utils.interpolate_color(t, theme=theme)
            x0 = bar_x0 + (bar_w * i / num_slices)
            x1 = bar_x0 + (bar_w * (i + 1) / num_slices)
            self.create_rectangle(x0, bar_y0, x1, bar_y1, fill=color, outline="")
        
        self.create_text(bar_x0 - 5, (bar_y0 + bar_y1) // 2, text="0%", fill=TEXT_SECONDARY, font=(FONT_FAMILY, 8), anchor="e")
        self.create_text(bar_x1 + 5, (bar_y0 + bar_y1) // 2, text="100%", fill=TEXT_SECONDARY, font=(FONT_FAMILY, 8), anchor="w")

# =====================================================================
# Process Mapping Dialog
# =====================================================================
class ProcessMappingDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        
        self.title("Configure Process Mappings")
        self.geometry("450x600")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.transient(parent)
        self.configure(fg_color=BG_MAIN)
        self.grab_set()
        
        frame = customtkinter.CTkFrame(self, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        title_lbl = customtkinter.CTkLabel(frame, text="Smart Process Auto-switching", font=(FONT_FAMILY, 15, "bold"), text_color=ACCENT)
        title_lbl.pack(pady=10)
        
        desc_lbl = customtkinter.CTkLabel(
            frame, 
            text="Map background process names (.exe) to specific profiles. TypeTrace switches profiles automatically when the process goes in the foreground.", 
            font=(FONT_FAMILY, 10), 
            text_color=TEXT_SECONDARY, 
            wraplength=380
        )
        desc_lbl.pack(pady=(0, 15))
        
        add_frame = customtkinter.CTkFrame(frame, fg_color=KEYCAP_BASE, border_color=BORDER_COLOR, border_width=1, corner_radius=12)
        add_frame.pack(fill="x", padx=15, pady=5)
        
        process_lbl = customtkinter.CTkLabel(add_frame, text="Process (.exe):", font=(FONT_FAMILY, 10), text_color=TEXT_SECONDARY)
        process_lbl.grid(row=0, column=0, padx=8, pady=10, sticky="w")
        
        self.process_entry = customtkinter.CTkEntry(
            add_frame, placeholder_text="code.exe", width=110, 
            fg_color=BG_CARD, border_color=BORDER_COLOR, text_color=TEXT_PRIMARY, font=(FONT_FAMILY, 10)
        )
        self.process_entry.grid(row=0, column=1, padx=4, pady=10)
        
        profile_lbl = customtkinter.CTkLabel(add_frame, text="Profile:", font=(FONT_FAMILY, 10), text_color=TEXT_SECONDARY)
        profile_lbl.grid(row=0, column=2, padx=8, pady=10, sticky="w")
        
        # Filter profiles to exclude "Total" since Total never receives direct keystrokes!
        profile_choices = [p for p in self.db.get_profiles() if p != "Total"]
        self.profile_combo = customtkinter.CTkComboBox(
            add_frame, values=profile_choices, width=100,
            fg_color=BG_CARD, border_color=BORDER_COLOR, button_color=KEYCAP_BASE, button_hover_color=KEYCAP_HOVER, text_color=TEXT_PRIMARY,
            dropdown_fg_color=KEYCAP_BASE, dropdown_hover_color=KEYCAP_HOVER, dropdown_text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, 10)
        )
        self.profile_combo.grid(row=0, column=3, padx=4, pady=10)
        
        add_btn = customtkinter.CTkButton(
            add_frame, text="Add", width=45, fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color=BG_MAIN, font=(FONT_FAMILY, 11, "bold"), command=self.add_mapping
        )
        add_btn.grid(row=0, column=4, padx=8, pady=10)
        
        # Mappings list scrollable frame
        list_title = customtkinter.CTkLabel(frame, text="Custom Mappings", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY)
        list_title.pack(pady=(10, 2))
        
        self.list_frame = customtkinter.CTkScrollableFrame(
            frame, height=180, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=12
        )
        self.list_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Recent processes scrollable frame (Requirement 13a)
        recent_lbl = customtkinter.CTkLabel(frame, text="Recent Processes", font=(FONT_FAMILY, 12, "bold"), text_color=ACCENT)
        recent_lbl.pack(pady=(10, 2))
        
        self.recent_frame = customtkinter.CTkScrollableFrame(
            frame, height=150, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=12
        )
        self.recent_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        self.load_mappings()
        self.load_recent()
        
    def load_mappings(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        mappings = self.db.get_profile_mappings()
        for idx, (proc, prof) in enumerate(mappings.items()):
            row_frame = customtkinter.CTkFrame(self.list_frame, fg_color=KEYCAP_BASE, border_color=BORDER_COLOR, border_width=1, corner_radius=8)
            row_frame.pack(fill="x", pady=2, padx=2)
            
            # Check if this custom mapping is for a built-in process (auto-detected)
            is_builtin_gaming = proc.lower() in BUILTIN_GAMING_PROCESSES
            is_builtin_desktop = proc.lower() in BUILTIN_DESKTOP_PROCESSES
            
            lbl_type = "auto-detected" if (is_builtin_gaming or is_builtin_desktop) else "custom"
            lbl_text = f"{proc}  ➜  {prof} ({lbl_type})"
            lbl_font = (FONT_FAMILY, 10, "italic") if (is_builtin_gaming or is_builtin_desktop) else ("Consolas", 10, "bold")
            
            lbl = customtkinter.CTkLabel(row_frame, text=lbl_text, font=lbl_font, text_color=TEXT_PRIMARY, anchor="w")
            lbl.pack(side="left", padx=10, pady=5)
            
            del_btn = customtkinter.CTkButton(
                row_frame, text="Remove", width=60, fg_color=DANGER, hover_color=DANGER_HOVER, text_color=TEXT_PRIMARY, font=(FONT_FAMILY, 10, "bold"),
                command=lambda p=proc: self.delete_mapping(p)
            )
            del_btn.pack(side="right", padx=10, pady=5)

    def load_recent(self):
        for widget in self.recent_frame.winfo_children():
            widget.destroy()
            
        recent = self.db.get_recent_processes(limit=5)
        
        for entry in recent:
            if not isinstance(entry, dict):
                continue
            proc = entry.get("process_name", "")
            category = entry.get("category", "Unknown")
            
            row_frame = customtkinter.CTkFrame(self.recent_frame, fg_color=KEYCAP_BASE, border_color=BORDER_COLOR, border_width=1, corner_radius=8)
            row_frame.pack(fill="x", pady=2, padx=2)
            
            # Label: Process name + auto-detected category in gray
            lbl_text = f"{proc}  ({category})"
            lbl = customtkinter.CTkLabel(row_frame, text=lbl_text, font=(FONT_FAMILY, 10, "italic"), text_color=TEXT_SECONDARY, anchor="w")
            lbl.pack(side="left", padx=10, pady=5)
            
            btn_frame = customtkinter.CTkFrame(row_frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=5)
            
            # "→ Gaming" button
            g_btn = customtkinter.CTkButton(
                btn_frame, text="→ Gaming", width=70, height=22, fg_color=KEYCAP_BASE, hover_color=ACCENT, 
                text_color=TEXT_PRIMARY, font=(FONT_FAMILY, 9, "bold"),
                command=lambda p=proc: self.quick_map(p, "Gaming")
            )
            g_btn.pack(side="left", padx=2, pady=2)
            
            # "→ Desktop" button
            d_btn = customtkinter.CTkButton(
                btn_frame, text="→ Desktop", width=70, height=22, fg_color=KEYCAP_BASE, hover_color=ACCENT, 
                text_color=TEXT_PRIMARY, font=(FONT_FAMILY, 9, "bold"),
                command=lambda p=proc: self.quick_map(p, "Desktop")
            )
            d_btn.pack(side="left", padx=2, pady=2)
            
    def add_mapping(self):
        proc = self.process_entry.get().strip().lower()
        prof = self.profile_combo.get()
        
        if not proc:
            return
            
        if not proc.endswith(".exe"):
            proc += ".exe"
            
        if proc == ".exe" or not prof:
            messagebox.showerror("Error", "Please fill in a valid process name.")
            return
            
        mappings = self.db.get_profile_mappings()
        mappings[proc] = prof
        self.db.set_profile_mappings(mappings)
        self.process_entry.delete(0, tk.END)
        self.load_mappings()
        self.load_recent()
        
    def quick_map(self, process_name, profile_name):
        self.process_entry.delete(0, tk.END)
        self.process_entry.insert(0, process_name)
        self.profile_combo.set(profile_name)
        self.add_mapping()

    def delete_mapping(self, proc):
        mappings = self.db.get_profile_mappings()
        if proc in mappings:
            del mappings[proc]
            self.db.set_profile_mappings(mappings)
            self.load_mappings()
            self.load_recent()

# =====================================================================
# About Dialog
# =====================================================================
class AboutDialog(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About TypeTrace")
        self.geometry("380x280")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.transient(parent)
        self.configure(fg_color=BG_MAIN)
        self.grab_set()
        
        frame = customtkinter.CTkFrame(self, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        logo = customtkinter.CTkLabel(frame, text="TYPETRACE", font=(FONT_FAMILY, 28, "bold"), text_color=ACCENT)
        logo.pack(pady=(25, 2))
        
        version_lbl = customtkinter.CTkLabel(frame, text=f"v{APP_VERSION}", font=(FONT_FAMILY, 12), text_color=TEXT_SECONDARY)
        version_lbl.pack(pady=(0, 12))
        
        desc = customtkinter.CTkLabel(
            frame, 
            text="Privacy-focused keystroke analytics.\nAll data stored locally on your machine.",
            font=(FONT_FAMILY, 11), text_color=TEXT_SECONDARY, justify="center"
        )
        desc.pack(pady=(0, 16))
        
        sep = customtkinter.CTkFrame(frame, fg_color=BORDER_COLOR, height=1)
        sep.pack(fill="x", padx=30, pady=(0, 16))
        
        github_lbl = customtkinter.CTkLabel(
            frame,
            text=f"★ GitHub Repository",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=ACCENT,
            cursor="hand2"
        )
        github_lbl.pack(pady=(0, 5))
        github_lbl.bind("<Button-1>", lambda e: webbrowser.open(APP_GITHUB))
        
        footer = customtkinter.CTkLabel(frame, text="Made with ⌨️ by TypeTrace", font=(FONT_FAMILY, 9), text_color="#555555")
        footer.pack(pady=(5, 10))

# =====================================================================
# Main Application UI
# =====================================================================
class TypeTraceUI(customtkinter.CTk):
    def __init__(self, db, tracker, shutdown_callback=None):
        super().__init__()
        self.db = db
        self.tracker = tracker
        self.shutdown_callback = shutdown_callback
        
        # Configure Main Window
        self.title("TypeTrace — Keystroke Analytics")
        self.geometry("1500x820")
        self.resizable(True, True)
        self.minsize(1200, 700)
        self.configure(fg_color=BG_MAIN)
        
        self._set_window_icon()
        
        self.protocol('WM_DELETE_WINDOW', self.withdraw_to_tray)
        
        self.overlay = None
        self.current_layout = "ANSI 100%"
        self._status_pulse_step = 0
        self._resize_job = None
        self._is_updating = False
        self._key_color_cache = {}  # Color cache to stop bulk redraws (STEP 2)
        self._heatmap_loop_started = False
        self.viewing_profile = self.tracker.active_profile
        
        self.incognito_var = tk.BooleanVar(value=self.tracker.incognito_mode)
        self.heatmap_var = tk.BooleanVar(value=False)
        self.startup_var = tk.BooleanVar(value=utils.is_startup_enabled())
        self.overlay_var = tk.BooleanVar(value=self.db.get_overlay_enabled())
        
        self.key_buttons = {}
        self.tooltips = {}
        
        self.setup_layout()
        self.update_ui_stats()
        
        if self.overlay_var.get():
            self.after(500, self.toggle_overlay)
            
        self.run_background_updates()
        
        # Set up UI states for profile view buttons (Requirement 10)
        self.update_profile_selector_ui()
        
        self._pulse_status_dot()
        
        self.bind("<Configure>", self.on_resize)

    def _set_window_icon(self):
        try:
            from PIL import Image, ImageDraw, ImageTk
            size = 64
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([2, 2, size-2, size-2], fill=(0, 245, 212, 255))
            draw.rounded_rectangle([14, 22, 50, 42], fill=(11, 12, 16, 255), outline=(255, 255, 255, 200), width=2, radius=3)
            draw.line([23, 22, 23, 42], fill=(255, 255, 255, 180), width=1)
            draw.line([32, 22, 32, 42], fill=(255, 255, 255, 180), width=1)
            draw.line([41, 22, 41, 42], fill=(255, 255, 255, 180), width=1)
            draw.line([14, 32, 50, 32], fill=(255, 255, 255, 180), width=1)
            photo = ImageTk.PhotoImage(img)
            self.iconphoto(True, photo)
            self._icon_ref = photo
        except Exception:
            pass

    def setup_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.master_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.master_frame.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)
        self.master_frame.grid_columnconfigure(0, weight=1)
        self.master_frame.grid_rowconfigure(1, weight=1)
        
        # 1. TOP HEADER BAR
        self.header_frame = customtkinter.CTkFrame(self.master_frame, fg_color="transparent", height=55)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.header_frame.pack_propagate(False)

        self.logo_container = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        self.logo_container.pack(side="left")

        self.logo_label = customtkinter.CTkLabel(
            self.logo_container, 
            text="TYPETRACE", 
            font=(FONT_FAMILY, 24, "bold"),
            text_color=ACCENT
        )
        self.logo_label.pack(anchor="w")

        self.sub_logo_label = customtkinter.CTkLabel(
            self.logo_container, 
            text="PRIVACY-FOCUSED KEYSTROKE ANALYZER", 
            font=(FONT_FAMILY, 9, "bold"),
            text_color=TEXT_SECONDARY
        )
        self.sub_logo_label.pack(anchor="w")

        self.header_metrics = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_metrics.pack(side="left", expand=True)

        self.header_apm_label = customtkinter.CTkLabel(
            self.header_metrics, text="APM: 0", font=(FONT_FAMILY, 20, "bold"), text_color=ACCENT
        )
        self.header_apm_label.pack(side="left", padx=(0, 20))

        self.header_wpm_label = customtkinter.CTkLabel(
            self.header_metrics, text="WPM: 0", font=(FONT_FAMILY, 20, "bold"), text_color=TEXT_PRIMARY
        )
        self.header_wpm_label.pack(side="left")

        self.header_right = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_right.pack(side="right")

        self.status_indicator_frame = customtkinter.CTkFrame(self.header_right, fg_color="transparent")
        self.status_indicator_frame.pack(side="left", padx=(0, 12))
        
        self.status_dot_canvas = tk.Canvas(self.status_indicator_frame, width=12, height=12, bg=BG_MAIN, highlightthickness=0)
        self.status_dot_canvas.pack(side="left", padx=(0, 6))
        self.status_dot = self.status_dot_canvas.create_oval(1, 1, 11, 11, fill=ACCENT, outline="")
        
        # Active Process Indicator (Requirement 20)
        self.proc_label = customtkinter.CTkLabel(
            self.status_indicator_frame, text="● Tracking", font=(FONT_FAMILY, 9), text_color=TEXT_SECONDARY
        )
        self.proc_label.pack(side="left", padx=(4, 0))

        self.about_btn = customtkinter.CTkButton(
            self.header_right, text="?", width=32, height=32,
            fg_color=KEYCAP_BASE, hover_color=KEYCAP_HOVER, text_color=TEXT_SECONDARY,
            font=(FONT_FAMILY, 14, "bold"), corner_radius=16,
            command=self.open_about_dialog
        )
        self.about_btn.pack(side="left", padx=(8, 0))

        # 2. KEYBOARD SECTION (Top Card)
        self.top_card = customtkinter.CTkFrame(self.master_frame, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        self.top_card.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        self.top_card.grid_columnconfigure(0, weight=1)
        self.top_card.grid_rowconfigure(2, weight=1)
        self.top_card.grid_rowconfigure(3, minsize=34, weight=0)

        self.kb_header = customtkinter.CTkFrame(self.top_card, fg_color="transparent")
        self.kb_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(12, 3))
        
        self.main_title = customtkinter.CTkLabel(
            self.kb_header, text="Virtual Keyboard Analytics", font=(FONT_FAMILY, 14, "bold"), text_color=TEXT_PRIMARY
        )
        self.main_title.pack(side="left")
        
        self.layout_combo = customtkinter.CTkComboBox(
            self.kb_header, values=["ANSI 100%", "TKL", "75%", "65%", "60%"],
            command=self.switch_keyboard_layout, width=120, height=26,
            font=(FONT_FAMILY, 10), fg_color=KEYCAP_BASE, border_color=BORDER_COLOR,
            button_color=KEYCAP_BASE, button_hover_color=KEYCAP_HOVER, text_color=TEXT_PRIMARY,
            dropdown_fg_color=KEYCAP_BASE, dropdown_hover_color=KEYCAP_HOVER, dropdown_text_color=TEXT_PRIMARY
        )
        self.layout_combo.set("ANSI 100%")
        self.layout_combo.pack(side="right")
        
        layout_lbl = customtkinter.CTkLabel(
            self.kb_header, text="Layout:", font=(FONT_FAMILY, 10), text_color=TEXT_SECONDARY
        )
        layout_lbl.pack(side="right", padx=(0, 6))

        self.main_subtitle = customtkinter.CTkLabel(
            self.top_card, 
            text="Hover over any key to view exact statistics. Toggle Heatmap to color keys dynamically.",
            font=(FONT_FAMILY, 10), text_color=TEXT_SECONDARY
        )
        self.main_subtitle.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 8))
        
        # Single Keyboard Container for native Grid Scaling
        self.keyboard_container = customtkinter.CTkFrame(self.top_card, fg_color="transparent")
        self.keyboard_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 8))
        
        self.generate_keyboard()
        
        self.legend_frame = customtkinter.CTkFrame(self.top_card, height=34, fg_color="transparent")
        self.legend_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.legend_frame.pack_propagate(False)
        self.heatmap_legend = HeatmapLegend(self.legend_frame)

        # 3. BOTTOM SECTION: Three-Column Grid
        self.bottom_grid = customtkinter.CTkFrame(self.master_frame, fg_color="transparent")
        self.bottom_grid.grid(row=2, column=0, sticky="ew", pady=(0, 12))

        self.bottom_grid.grid_columnconfigure(0, weight=1, uniform="bottom_cols")
        self.bottom_grid.grid_columnconfigure(1, weight=1, uniform="bottom_cols")
        self.bottom_grid.grid_columnconfigure(2, weight=1, uniform="bottom_cols")

        # CARD 0: CONFIGURATION & THEMES
        self.config_card = customtkinter.CTkFrame(self.bottom_grid, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        self.config_card.grid(row=0, column=0, padx=(0, 12), sticky="nsew")

        self.config_title = customtkinter.CTkLabel(self.config_card, text="⚙️ CONFIGURATION", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY)
        self.config_title.pack(anchor="w", padx=15, pady=(12, 8))

        # Profile selection redesign occupying full width of card (Requirement 10)
        self.profile_lbl = customtkinter.CTkLabel(self.config_card, text="Select Profile (Stats View):", font=(FONT_FAMILY, 10), text_color=TEXT_SECONDARY)
        self.profile_lbl.pack(anchor="w", padx=15, pady=(0, 2))

        self.profile_row = customtkinter.CTkFrame(self.config_card, fg_color="transparent")
        self.profile_row.pack(fill="x", padx=15, pady=(0, 6))

        # Icon buttons for built-in profiles (Total, Desktop, Gaming)
        self.btn_total = customtkinter.CTkButton(
            self.profile_row, text="🌐 Total", width=75, height=26, corner_radius=8, font=(FONT_FAMILY, 10),
            command=lambda: self._set_viewing_profile("Total")
        )
        self.btn_total.pack(side="left", padx=2)

        self.btn_desktop = customtkinter.CTkButton(
            self.profile_row, text="🖥️ Desktop", width=75, height=26, corner_radius=8, font=(FONT_FAMILY, 10),
            command=lambda: self._set_viewing_profile("Desktop")
        )
        self.btn_desktop.pack(side="left", padx=2)

        self.btn_gaming = customtkinter.CTkButton(
            self.profile_row, text="🎮 Gaming", width=75, height=26, corner_radius=8, font=(FONT_FAMILY, 10),
            command=lambda: self._set_viewing_profile("Gaming")
        )
        self.btn_gaming.pack(side="left", padx=2)

        # Combobox for custom profiles
        self.profile_combobox = customtkinter.CTkComboBox(
            self.profile_row, values=self.get_custom_profiles(), command=self.on_custom_profile_selected, width=100, height=28,
            font=(FONT_FAMILY, 10), fg_color=KEYCAP_BASE, border_color=BORDER_COLOR, button_color=KEYCAP_BASE, button_hover_color=KEYCAP_HOVER,
            text_color=TEXT_PRIMARY, dropdown_fg_color=KEYCAP_BASE, dropdown_hover_color=KEYCAP_HOVER, dropdown_text_color=TEXT_PRIMARY
        )
        self.profile_combobox.set("custom ▾")
        self.profile_combobox.pack(side="left", padx=(6, 2))

        self.add_profile_btn = customtkinter.CTkButton(
            self.profile_row, text="+", width=26, height=28, fg_color=KEYCAP_BASE, hover_color=ACCENT, text_color=TEXT_PRIMARY, font=(FONT_FAMILY, 12, "bold"), command=self.create_profile_dialog
        )
        self.add_profile_btn.pack(side="left", padx=2)

        self.del_profile_btn = customtkinter.CTkButton(
            self.profile_row, text="🗑", width=26, height=28, fg_color=KEYCAP_BASE, hover_color=DANGER, text_color=TEXT_PRIMARY, font=(FONT_FAMILY, 11, "bold"), command=self.delete_active_profile
        )
        # Delete button visibility managed in update_profile_selector_ui

        self.config_inner = customtkinter.CTkFrame(self.config_card, fg_color="transparent")
        self.config_inner.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        self.config_inner.columnconfigure(0, weight=1, uniform="config_cols")
        self.config_inner.columnconfigure(1, weight=1, uniform="config_cols")

        # Left Column - Theme only
        self.config_left = customtkinter.CTkFrame(self.config_inner, fg_color="transparent")
        self.config_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.theme_lbl = customtkinter.CTkLabel(self.config_left, text="Heatmap Theme:", font=(FONT_FAMILY, 10), text_color=TEXT_SECONDARY)
        self.theme_lbl.pack(anchor="w", pady=(0, 2))

        self.theme_combo = customtkinter.CTkComboBox(
            self.config_left, values=["Classic", "Cyberpunk", "Matrix", "Stealth"],
            command=self.change_heatmap_theme, font=(FONT_FAMILY, 10), height=26,
            fg_color=KEYCAP_BASE, border_color=BORDER_COLOR, button_color=KEYCAP_BASE, button_hover_color=KEYCAP_HOVER, text_color=TEXT_PRIMARY,
            dropdown_fg_color=KEYCAP_BASE, dropdown_hover_color=KEYCAP_HOVER, dropdown_text_color=TEXT_PRIMARY
        )
        self.theme_combo.set(self.db.get_heatmap_theme())
        self.theme_combo.pack(fill="x", pady=(0, 6))

        # Right Column - Switches
        self.config_right = customtkinter.CTkFrame(self.config_inner, fg_color="transparent")
        self.config_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.heatmap_switch = customtkinter.CTkSwitch(
            self.config_right, text="🔥 Heatmap View", variable=self.heatmap_var, onvalue=True, offvalue=False,
            command=self.toggle_heatmap, font=(FONT_FAMILY, 10), progress_color=ACCENT, text_color=TEXT_SECONDARY, height=20
        )
        self.heatmap_switch.pack(anchor="w", pady=2)

        self.incognito_switch = customtkinter.CTkSwitch(
            self.config_right, text="🕵️ Incognito Mode", variable=self.incognito_var, onvalue=True, offvalue=False,
            command=self.toggle_incognito, font=(FONT_FAMILY, 10), progress_color=DANGER, text_color=TEXT_SECONDARY, height=20
        )
        self.incognito_switch.pack(anchor="w", pady=2)

        self.overlay_switch = customtkinter.CTkSwitch(
            self.config_right, text="📺 Floating Widget", variable=self.overlay_var, onvalue=True, offvalue=False,
            command=self.toggle_overlay, font=(FONT_FAMILY, 10), progress_color=ACCENT, text_color=TEXT_SECONDARY, height=20
        )
        self.overlay_switch.pack(anchor="w", pady=2)

        self.startup_checkbox = customtkinter.CTkSwitch(
            self.config_right, text="💻 Boot Startup", variable=self.startup_var, onvalue=True, offvalue=False,
            command=self.toggle_startup, font=(FONT_FAMILY, 10), progress_color=ACCENT, text_color=TEXT_SECONDARY, height=20
        )
        self.startup_checkbox.pack(anchor="w", pady=2)

        # Action Buttons
        self.action_buttons_frame = customtkinter.CTkFrame(self.config_card, fg_color="transparent")
        self.action_buttons_frame.pack(fill="x", padx=15, pady=(0, 12))

        self.action_buttons_frame.columnconfigure(0, weight=1, uniform="act_btns")
        self.action_buttons_frame.columnconfigure(1, weight=1, uniform="act_btns")
        self.action_buttons_frame.columnconfigure(2, weight=1, uniform="act_btns")
        self.action_buttons_frame.columnconfigure(3, weight=1, uniform="act_btns")

        self.smart_switch_btn = customtkinter.CTkButton(
            self.action_buttons_frame, text="🔄 Auto-Switch", fg_color="transparent", hover_color=KEYCAP_HOVER,
            border_color=BORDER_COLOR, border_width=1, text_color=TEXT_SECONDARY, font=(FONT_FAMILY, 10), command=self.open_mappings_dialog
        )
        self.smart_switch_btn.grid(row=0, column=0, padx=2, sticky="ew")

        self.export_csv_btn = customtkinter.CTkButton(
            self.action_buttons_frame, text="📥 CSV", fg_color="transparent", hover_color=KEYCAP_HOVER,
            border_color=BORDER_COLOR, border_width=1, text_color=TEXT_SECONDARY, font=(FONT_FAMILY, 10), command=self.export_csv
        )
        self.export_csv_btn.grid(row=0, column=1, padx=2, sticky="ew")

        self.export_json_btn = customtkinter.CTkButton(
            self.action_buttons_frame, text="📥 JSON", fg_color="transparent", hover_color=KEYCAP_HOVER,
            border_color=BORDER_COLOR, border_width=1, text_color=TEXT_SECONDARY, font=(FONT_FAMILY, 10), command=self.export_json
        )
        self.export_json_btn.grid(row=0, column=2, padx=2, sticky="ew")

        self.reset_btn = customtkinter.CTkButton(
            self.action_buttons_frame, text="⚠️ Reset", fg_color=DANGER, hover_color=DANGER_HOVER,
            text_color=TEXT_PRIMARY, font=(FONT_FAMILY, 10, "bold"), command=self.reset_statistics_dialog
        )
        self.reset_btn.grid(row=0, column=3, padx=2, sticky="ew")

        # CARD 1: TELEMETRY — 3 Mini-Cards
        self.telemetry_card = customtkinter.CTkFrame(self.bottom_grid, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        self.telemetry_card.grid(row=0, column=1, padx=(0, 12), sticky="nsew")

        self.telemetry_title = customtkinter.CTkLabel(self.telemetry_card, text="📊 TELEMETRY & METRICS", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY)
        self.telemetry_title.pack(anchor="w", padx=15, pady=(12, 8))

        self.mini_cards = customtkinter.CTkFrame(self.telemetry_card, fg_color="transparent")
        self.mini_cards.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        
        self.mini_cards.columnconfigure(0, weight=1, uniform="mini")
        self.mini_cards.columnconfigure(1, weight=1, uniform="mini")
        self.mini_cards.columnconfigure(2, weight=1, uniform="mini")
        self.mini_cards.rowconfigure(0, weight=1)

        # Mini-Card A: Session Stats
        self.mc_session = customtkinter.CTkFrame(self.mini_cards, fg_color=BG_CARD_INNER, border_color=BORDER_INNER, border_width=1, corner_radius=12)
        self.mc_session.grid(row=0, column=0, padx=4, sticky="nsew")
        
        mc_a_title = customtkinter.CTkLabel(self.mc_session, text="SESSION", font=(FONT_FAMILY, 8, "bold"), text_color=TEXT_SECONDARY)
        mc_a_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        self.session_time_lbl = customtkinter.CTkLabel(self.mc_session, text="00:00:00", font=(FONT_FAMILY, 16, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.session_time_lbl.pack(anchor="w", padx=10, pady=(0, 2))
        
        self.session_keys_lbl = customtkinter.CTkLabel(self.mc_session, text="Keys: 0", font=(FONT_FAMILY, 10), text_color=TEXT_SECONDARY, anchor="w")
        self.session_keys_lbl.pack(anchor="w", padx=10, pady=0)
        
        self.error_ratio_lbl = customtkinter.CTkLabel(self.mc_session, text="⌫ Ratio: 0.0%", font=(FONT_FAMILY, 10), text_color=TEXT_SECONDARY, anchor="w")
        self.error_ratio_lbl.pack(anchor="w", padx=10, pady=(0, 8))

        # Mini-Card B: Leaderboard
        self.mc_leaderboard = customtkinter.CTkFrame(self.mini_cards, fg_color=BG_CARD_INNER, border_color=BORDER_INNER, border_width=1, corner_radius=12)
        self.mc_leaderboard.grid(row=0, column=1, padx=4, sticky="nsew")
        
        mc_b_title = customtkinter.CTkLabel(self.mc_leaderboard, text="TOP KEYS", font=(FONT_FAMILY, 8, "bold"), text_color=TEXT_SECONDARY)
        mc_b_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        self.top_keys_labels = []
        for i in range(3):
            lbl = customtkinter.CTkLabel(self.mc_leaderboard, text=f"{i+1}. —", font=("Consolas", 9, "bold"), text_color=TEXT_SECONDARY, anchor="w")
            lbl.pack(anchor="w", padx=10, pady=0)
            self.top_keys_labels.append(lbl)
        
        mc_b_combo_title = customtkinter.CTkLabel(self.mc_leaderboard, text="TOP COMBOS", font=(FONT_FAMILY, 8, "bold"), text_color=TEXT_SECONDARY)
        mc_b_combo_title.pack(anchor="w", padx=10, pady=(4, 2))
        
        self.top_combos_labels = []
        for i in range(2):
            lbl = customtkinter.CTkLabel(self.mc_leaderboard, text=f"{i+1}. —", font=("Consolas", 9, "bold"), text_color=TEXT_SECONDARY, anchor="w")
            lbl.pack(anchor="w", padx=10, pady=0)
            self.top_combos_labels.append(lbl)

        # Mini-Card C: Bursts
        self.mc_bursts = customtkinter.CTkFrame(self.mini_cards, fg_color=BG_CARD_INNER, border_color=BORDER_INNER, border_width=1, corner_radius=12)
        self.mc_bursts.grid(row=0, column=2, padx=4, sticky="nsew")
        
        mc_c_title = customtkinter.CTkLabel(self.mc_bursts, text="BURSTS", font=(FONT_FAMILY, 8, "bold"), text_color=TEXT_SECONDARY)
        mc_c_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        self.total_bursts_lbl = customtkinter.CTkLabel(self.mc_bursts, text="0 recorded", font=(FONT_FAMILY, 14, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.total_bursts_lbl.pack(anchor="w", padx=10, pady=(0, 4))
        
        records_title = customtkinter.CTkLabel(self.mc_bursts, text="RECORDS", font=(FONT_FAMILY, 8, "bold"), text_color=TEXT_SECONDARY)
        records_title.pack(anchor="w", padx=10, pady=(0, 2))
        
        self.burst_labels = []
        for i in range(3):
            lbl = customtkinter.CTkLabel(self.mc_bursts, text=f"{i+1}. —", font=("Consolas", 9, "bold"), text_color=TEXT_SECONDARY, anchor="w")
            lbl.pack(anchor="w", padx=10, pady=0)
            self.burst_labels.append(lbl)

        # CARD 2: PRODUCTIVITY PROFILE
        self.chart_card = customtkinter.CTkFrame(self.bottom_grid, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        self.chart_card.grid(row=0, column=2, sticky="nsew")

        self.chart_title = customtkinter.CTkLabel(self.chart_card, text="📈 HOURLY PRODUCTIVITY", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY)
        self.chart_title.pack(anchor="w", padx=15, pady=(12, 8))

        self.chart_canvas = ProductivityChart(self.chart_card)
        self.chart_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # STATUS BAR (Bottom)
        self.status_bar = customtkinter.CTkFrame(self.master_frame, height=30, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=12)
        self.status_bar.grid(row=3, column=0, sticky="ew", pady=(0, 0))

        self.status_left_lbl = customtkinter.CTkLabel(
            self.status_bar, text="System Status: Tracking Active", font=(FONT_FAMILY, 10), text_color=ACCENT
        )
        self.status_left_lbl.pack(side="left", padx=15, pady=4)

        self.led_frame = customtkinter.CTkFrame(self.status_bar, fg_color="transparent")
        self.led_frame.pack(side="right", padx=15, pady=4)

        self.led_lbl = customtkinter.CTkLabel(
            self.led_frame, text="Burst Mode", font=(FONT_FAMILY, 10), text_color=TEXT_SECONDARY
        )
        self.led_lbl.pack(side="left", padx=5)

        self.led_canvas = tk.Canvas(self.led_frame, width=10, height=10, bg=BG_CARD, highlightthickness=0)
        self.led_canvas.pack(side="left", padx=2, pady=5)
        self.led_circle = self.led_canvas.create_oval(1, 1, 9, 9, fill="#333333", outline="")

    # =====================================================================
    # Status Dot Pulse Animation
    # =====================================================================
    def _pulse_status_dot(self):
        try:
            if self.incognito_var.get():
                colors = ["#A63A50", "#D44D63", "#A63A50", "#8A3040"]
            else:
                colors = [ACCENT, "#00C4A8", "#009E89", "#00C4A8"]
            
            idx = self._status_pulse_step % len(colors)
            self.status_dot_canvas.itemconfig(self.status_dot, fill=colors[idx])
            self._status_pulse_step += 1
        except Exception:
            pass
        finally:
            try:
                self.after(800, self._pulse_status_dot)
            except Exception:
                pass

    # =====================================================================
    # Native Grid Keyboard Generation & Layout
    # =====================================================================
    def generate_keyboard(self):
        # Destroy previous key buttons
        if hasattr(self, 'key_buttons') and isinstance(self.key_buttons, dict):
            for btn in self.key_buttons.values():
                if hasattr(btn, 'destroy'):
                    btn.destroy()

        # Destroy previous sub-frames
        for attr in ('left_keyboard_frame', 'nav_keyboard_frame', 'numpad_keyboard_frame'):
            if hasattr(self, attr):
                frame = getattr(self, attr)
                if frame and hasattr(frame, 'destroy'):
                    frame.destroy()
        # Clear any leftover children in keyboard_container
        for child in self.keyboard_container.winfo_children():
            child.destroy()

        self.keys_data = []
        self.key_buttons = {}
        self.tooltips = {}

        # Centralized Tooltip State
        self.active_tooltip_key = None
        self.tooltip_window = None
        self.tooltip_after_id = None

        # Determine which blocks are visible
        show_nav = self.current_layout in ["ANSI 100%", "TKL", "75%", "65%"]
        show_numpad = self.current_layout == "ANSI 100%"
        row_start = 1 if self.current_layout in ["65%", "60%"] else 0

        # --- Configure keyboard_container columns with proportional weights ---
        self.keyboard_container.grid_rowconfigure(0, weight=1)
        
        # Reset all 3 columns first
        for ci in range(3):
            self.keyboard_container.grid_columnconfigure(ci, weight=0, minsize=0)
        
        self.keyboard_container.grid_columnconfigure(0, weight=10, minsize=550)
        if show_nav:
            self.keyboard_container.grid_columnconfigure(1, weight=2, minsize=110)
        if show_numpad:
            self.keyboard_container.grid_columnconfigure(2, weight=3, minsize=130)

        # --- LEFT BLOCK (Alphanumeric) ---
        self.left_keyboard_frame = customtkinter.CTkFrame(self.keyboard_container, fg_color="transparent")
        self.left_keyboard_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        for row_idx, row_keys in enumerate(LEFT_KEYBOARD_LAYOUT):
            if row_idx < row_start:
                continue
            display_row = row_idx - row_start
            
            row_frame = customtkinter.CTkFrame(self.left_keyboard_frame, fg_color="transparent")
            row_frame.pack(fill="x", expand=True, pady=2, padx=5)
            
            key_height = 24 if row_idx == 0 else 28
            
            col = 0
            for label, span, db_key in row_keys:
                row_frame.columnconfigure(col, weight=span)
                
                if db_key == "spacer":
                    spacer = customtkinter.CTkFrame(row_frame, fg_color="transparent", height=key_height)
                    spacer.grid(row=0, column=col, sticky="ew", padx=2, pady=2)
                    col += 1
                    continue

                self.keys_data.append({
                    "db_key": db_key,
                    "label": label,
                    "block": "left",
                    "row": row_idx,
                    "col": col,
                    "colspan": 1,
                    "rowspan": 1
                })
                
                btn = customtkinter.CTkButton(
                    row_frame,
                    text=label,
                    height=key_height,
                    font=(FONT_FAMILY, 11, "bold"),
                    fg_color=self.get_key_target_color(db_key),
                    text_color=TEXT_PRIMARY if self.heatmap_var.get() else TEXT_SECONDARY,
                    hover_color=KEYCAP_HOVER,
                    corner_radius=6,
                    border_width=1,
                    border_color="#2F313D"
                )
                btn.bind("<Enter>", lambda e, k=db_key: self.on_key_enter_btn(k))
                btn.bind("<Leave>", lambda e, k=db_key: self.on_key_leave_btn(k))
                btn.bind("<Button-1>", lambda e, k=db_key: self.on_key_click_btn(k))
                btn.grid(row=0, column=col, sticky="ew", padx=2, pady=2)
                self.key_buttons[db_key] = btn
                col += 1

        # --- NAV BLOCK ---
        if show_nav:
            self.nav_keyboard_frame = customtkinter.CTkFrame(self.keyboard_container, fg_color="transparent")
            self.nav_keyboard_frame.grid(row=0, column=1, sticky="nsew", padx=4)
            
            for row_idx, row_keys in enumerate(NAV_KEYBOARD_LAYOUT):
                if row_idx < row_start:
                    continue
                display_row = row_idx - row_start
                
                row_frame = customtkinter.CTkFrame(self.nav_keyboard_frame, fg_color="transparent")
                row_frame.pack(fill="x", expand=True, pady=2, padx=2)
                
                key_height = 24 if row_idx == 0 else 28
                
                col = 0
                for label, span, db_key in row_keys:
                    row_frame.columnconfigure(col, weight=1)
                    
                    if db_key == "spacer" or label == "empty":
                        spacer = customtkinter.CTkFrame(row_frame, fg_color="transparent", height=key_height)
                        spacer.grid(row=0, column=col, sticky="ew", padx=2, pady=2)
                        col += 1
                        continue
                    
                    # 65% layout only shows arrow keys from nav
                    if self.current_layout == "65%" and db_key not in ["Up", "Down", "Left", "Right"]:
                        spacer = customtkinter.CTkFrame(row_frame, fg_color="transparent", height=key_height)
                        spacer.grid(row=0, column=col, sticky="ew", padx=2, pady=2)
                        col += 1
                        continue
                    
                    self.keys_data.append({
                        "db_key": db_key,
                        "label": label,
                        "block": "nav",
                        "row": row_idx,
                        "col": col,
                        "colspan": 1,
                        "rowspan": 1
                    })
                    
                    btn = customtkinter.CTkButton(
                        row_frame,
                        text=label,
                        height=key_height,
                        font=(FONT_FAMILY, 11, "bold"),
                        fg_color=self.get_key_target_color(db_key),
                        text_color=TEXT_PRIMARY if self.heatmap_var.get() else TEXT_SECONDARY,
                        hover_color=KEYCAP_HOVER,
                        corner_radius=6,
                        border_width=1,
                        border_color="#2F313D"
                    )
                    btn.bind("<Enter>", lambda e, k=db_key: self.on_key_enter_btn(k))
                    btn.bind("<Leave>", lambda e, k=db_key: self.on_key_leave_btn(k))
                    btn.bind("<Button-1>", lambda e, k=db_key: self.on_key_click_btn(k))
                    btn.grid(row=0, column=col, sticky="ew", padx=2, pady=2)
                    self.key_buttons[db_key] = btn
                    col += 1
        else:
            self.nav_keyboard_frame = None

        # --- NUMPAD BLOCK ---
        if show_numpad:
            self.numpad_keyboard_frame = customtkinter.CTkFrame(self.keyboard_container, fg_color="transparent")
            self.numpad_keyboard_frame.grid(row=0, column=2, sticky="nsew", padx=(4, 0))
            
            # Numpad uses a true grid because of rowspan keys (+ and Enter)
            num_rows = 6 - row_start
            num_cols = 4
            for ri in range(num_rows):
                self.numpad_keyboard_frame.grid_rowconfigure(ri, weight=1)
            for ci in range(num_cols):
                self.numpad_keyboard_frame.grid_columnconfigure(ci, weight=1)
            
            for label, row, col, rowspan, colspan, db_key in NUMPAD_KEYBOARD_LAYOUT:
                if row < row_start:
                    continue
                display_row = row - row_start
                
                if db_key == "spacer":
                    spacer = customtkinter.CTkFrame(self.numpad_keyboard_frame, fg_color="transparent")
                    spacer.grid(row=display_row, column=col, columnspan=colspan, rowspan=rowspan, sticky="nsew", padx=2, pady=2)
                    continue
                
                key_height = 24 if row == 0 else 28
                
                self.keys_data.append({
                    "db_key": db_key,
                    "label": label,
                    "block": "numpad",
                    "row": row,
                    "col": col,
                    "colspan": colspan,
                    "rowspan": rowspan
                })
                
                btn = customtkinter.CTkButton(
                    self.numpad_keyboard_frame,
                    text=label,
                    height=key_height,
                    font=(FONT_FAMILY, 11, "bold"),
                    fg_color=self.get_key_target_color(db_key),
                    text_color=TEXT_PRIMARY if self.heatmap_var.get() else TEXT_SECONDARY,
                    hover_color=KEYCAP_HOVER,
                    corner_radius=6,
                    border_width=1,
                    border_color="#2F313D"
                )
                btn.bind("<Enter>", lambda e, k=db_key: self.on_key_enter_btn(k))
                btn.bind("<Leave>", lambda e, k=db_key: self.on_key_leave_btn(k))
                btn.bind("<Button-1>", lambda e, k=db_key: self.on_key_click_btn(k))
                btn.grid(row=display_row, column=col, rowspan=rowspan, columnspan=colspan, sticky="nsew", padx=2, pady=2)
                self.key_buttons[db_key] = btn
        else:
            self.numpad_keyboard_frame = None

    def is_key_visible(self, key_data, layout_name):
        block = key_data["block"]
        row = key_data["row"]
        db_key = key_data["db_key"]
        
        if layout_name == "ANSI 100%":
            return True
            
        elif layout_name == "TKL" or layout_name == "75%":
            return block != "numpad"
            
        elif layout_name == "65%":
            if block == "numpad":
                return False
            if block == "left" and row == 0:
                return False
            if block == "nav":
                return db_key in ["Up", "Down", "Left", "Right"]
            return True
            
        elif layout_name == "60%":
            if block != "left":
                return False
            return row > 0
            
        return True

    # =====================================================================
    # Layout Switcher (Flickerless Redraw)
    # =====================================================================
    def switch_keyboard_layout(self, layout_name):
        self._is_updating = True
        self.current_layout = layout_name
        self.generate_keyboard()
        self.update_heatmap_colors()
        self.update_idletasks()
        self._is_updating = False

    # =====================================================================
    # Hover, Tooltip and Click Manager
    # =====================================================================
    def on_key_enter_btn(self, db_key):
        btn = self.key_buttons.get(db_key)
        if btn and hasattr(btn, 'configure'):
            btn.configure(border_color=ACCENT, border_width=2)
            if not self.heatmap_var.get():
                btn.configure(fg_color=KEYCAP_HOVER)
                
        self.active_tooltip_key = db_key
        if self.tooltip_after_id:
            self.after_cancel(self.tooltip_after_id)
        self.tooltip_after_id = self.after(250, lambda: self.show_key_tooltip(db_key))

    def on_key_leave_btn(self, db_key):
        btn = self.key_buttons.get(db_key)
        if btn and hasattr(btn, 'configure'):
            btn.configure(border_color="#2F313D", border_width=1)
            if not self.heatmap_var.get():
                btn.configure(fg_color=self.get_key_target_color(db_key))
                
        if self.tooltip_after_id:
            self.after_cancel(self.tooltip_after_id)
            self.tooltip_after_id = None
        self.hide_key_tooltip()
        self.active_tooltip_key = None

    def on_key_click_btn(self, db_key):
        self.flash_key(db_key)

    # Canvas key hover tooltip without CTkToplevel (BUG 1 FIXED)
    def show_key_tooltip(self, db_key):
        if not db_key or db_key != self.active_tooltip_key:
            return
        self.hide_key_tooltip()
        
        text = self.get_key_tooltip_text(db_key)
        if not text:
            return
            
        self.tooltip_window = frame = customtkinter.CTkFrame(
            self,
            fg_color="#111318",
            border_color="#00F5D4",
            border_width=1,
            corner_radius=8
        )
        lbl = customtkinter.CTkLabel(
            frame, text=text, justify="left", font=(FONT_FAMILY, 10),
            text_color=TEXT_PRIMARY, padx=12, pady=10
        )
        lbl.pack()
        
        rx = self.winfo_pointerx() - self.winfo_rootx() + 15
        ry = self.winfo_pointery() - self.winfo_rooty() + 15
        
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        frame.update_idletasks()
        tw = frame.winfo_reqwidth()
        th = frame.winfo_reqheight()
        if rx + tw > win_w - 10:
            rx = rx - tw - 30
        if ry + th > win_h - 10:
            ry = ry - th - 30
            
        frame.place(x=rx, y=ry)
        frame.lift()

    def hide_key_tooltip(self):
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except Exception:
                pass
            self.tooltip_window = None

    def get_key_tooltip_text(self, db_key):
        stats = self.db.get_key_stats(self.viewing_profile, db_key)
        
        key_label = db_key
        if db_key == "Space": key_label = "Spacebar"
        elif db_key == "Ctrl_L": key_label = "Left Ctrl"
        elif db_key == "Ctrl_R": key_label = "Right Ctrl"
        elif db_key == "Shift_L": key_label = "Left Shift"
        elif db_key == "Shift_R": key_label = "Right Shift"
        elif db_key == "Alt_L": key_label = "Left Alt"
        elif db_key == "Alt_R": key_label = "Right Alt"
        elif db_key == "Win_L": key_label = "Left Win"
        elif db_key == "Win_R": key_label = "Right Win"
        elif db_key == "Print_screen": key_label = "Print Screen"
        elif db_key == "Scroll_lock": key_label = "Scroll Lock"
        elif db_key == "Num_lock": key_label = "Num Lock"
        elif db_key == "Page_up": key_label = "Page Up"
        elif db_key == "Page_down": key_label = "Page Down"
        elif db_key.startswith("Kp_"):
            n_val = db_key.replace("Kp_", "")
            if n_val == "enter": n_val = "Enter"
            elif n_val == "add": n_val = "+"
            elif n_val == "subtract": n_val = "-"
            elif n_val == "multiply": n_val = "*"
            elif n_val == "divide": n_val = "/"
            key_label = f"Numpad {n_val}"
            
        consumed_pct = (stats['total'] / 50000000.0) * 100
            
        return (
            f"=== KEY: {key_label} ===\n\n"
            f"• Total Presses:  {stats['total']}\n"
            f"• Usage Share:    {stats['percentage']}\n"
            f"• Peak Frequency: {stats['peak_ppm']}\n"
            f"• Heat Trend:     {stats['trend']}\n"
            f"• Switch Life Used: {consumed_pct:.5f}%\n"
            f"• Next key (Bigram): {stats['bigram']}"
        )

# =====================================================================
# Heatmap Theming & Color Calculation
# =====================================================================
    def toggle_heatmap(self):
        self._is_updating = True
        
        if self.heatmap_var.get():
            self.heatmap_legend.pack(fill="both", expand=True)
            self.heatmap_legend.draw_legend(self.db.get_heatmap_theme())
            self.update_heatmap_colors()
        else:
            self.heatmap_legend.pack_forget()
            color_map = {k: (KEYCAP_BASE, TEXT_SECONDARY) for k in self.key_buttons.keys()}
            self._apply_key_colors(color_map)
            
        self.update_idletasks()
        self._is_updating = False

    # Single batch key color configuration method with cache (BUG 2 FIXED & STEP 2)
    def _apply_key_colors(self, color_map):
        for key_id, (bg, fg) in color_map.items():
            cache_key = (key_id, bg, fg)
            if self._key_color_cache.get(key_id) == cache_key:
                continue  # skip redraw entirely if color hasn't changed (STEP 2)
            self._key_color_cache[key_id] = cache_key
            
            btn = self.key_buttons.get(key_id)
            if btn and hasattr(btn, 'configure'):
                btn.configure(fg_color=bg, text_color=fg)
                
        # Flush pending geometry/draw in one batch on keyboard_container (STEP 4)
        self.keyboard_container.update_idletasks()
    def update_heatmap_colors(self):
        """Recalculates colors for all buttons in the virtual keyboard layout (BUG 2 & 3 FIXED)."""
        if not self.heatmap_var.get():
            return  # don't refresh if heatmap is off
            
        aggregated = self.db.get_aggregated_stats(self.viewing_profile)
        keys_counts = aggregated.get("keys", {})
        
        visible_counts = []
        for k in self.key_buttons.keys():
            count = keys_counts.get(k, 0)
            if k == "Kp_enter" and count == 0:
                count = keys_counts.get("Enter", 0)
            elif k == "Shift_R" and count == 0:
                count = keys_counts.get("Shift_L", 0)
            elif k == "Ctrl_R" and count == 0:
                count = keys_counts.get("Ctrl_L", 0)
            elif k == "Alt_R" and count == 0:
                count = keys_counts.get("Alt_L", 0)
            elif k == "Win_R" and count == 0:
                count = keys_counts.get("Win_L", 0)
            visible_counts.append(count)
            
        max_count = max(visible_counts) if visible_counts else 0
        theme = self.db.get_heatmap_theme()
        
        color_map = {}
        for db_key in self.key_buttons.keys():
            count = keys_counts.get(db_key, 0)
            if db_key == "Kp_enter" and count == 0:
                count = keys_counts.get("Enter", 0)
            elif db_key == "Shift_R" and count == 0:
                count = keys_counts.get("Shift_L", 0)
            elif db_key == "Ctrl_R" and count == 0:
                count = keys_counts.get("Ctrl_L", 0)
            elif db_key == "Alt_R" and count == 0:
                count = keys_counts.get("Alt_L", 0)
            elif db_key == "Win_R" and count == 0:
                count = keys_counts.get("Win_L", 0)
                
            factor = count / max_count if max_count > 0 else 0.0
            heatmap_color = utils.interpolate_color(factor, theme=theme)
            
            # Determine contrasting foreground color
            new_fg = TEXT_PRIMARY if factor < 0.5 else BG_MAIN
            color_map[db_key] = (heatmap_color, new_fg)
            
        self._apply_key_colors(color_map)

    def get_key_target_color(self, key_name):
        if self.heatmap_var.get():
            aggregated = self.db.get_aggregated_stats(self.viewing_profile)
            keys_counts = aggregated.get("keys", {})
            
            visible_counts = []
            for k in self.key_buttons.keys():
                count = keys_counts.get(k, 0)
                if k == "Kp_enter" and count == 0:
                    count = keys_counts.get("Enter", 0)
                elif k == "Shift_R" and count == 0:
                    count = keys_counts.get("Shift_L", 0)
                elif k == "Ctrl_R" and count == 0:
                    count = keys_counts.get("Ctrl_L", 0)
                elif k == "Alt_R" and count == 0:
                    count = keys_counts.get("Alt_L", 0)
                elif k == "Win_R" and count == 0:
                    count = keys_counts.get("Win_L", 0)
                visible_counts.append(count)
                
            max_count = max(visible_counts) if visible_counts else 0
            
            count = keys_counts.get(key_name, 0)
            if key_name == "Kp_enter" and count == 0:
                count = keys_counts.get("Enter", 0)
            elif key_name == "Shift_R" and count == 0:
                count = keys_counts.get("Shift_L", 0)
            elif key_name == "Ctrl_R" and count == 0:
                count = keys_counts.get("Ctrl_L", 0)
            elif key_name == "Alt_R" and count == 0:
                count = keys_counts.get("Alt_L", 0)
            elif key_name == "Win_R" and count == 0:
                count = keys_counts.get("Win_L", 0)
                
            factor = count / max_count if max_count > 0 else 0.0
            theme = self.db.get_heatmap_theme()
            return utils.interpolate_color(factor, theme=theme)
        else:
            return KEYCAP_BASE

    def change_heatmap_theme(self, theme):
        self._key_color_cache = {}  # Clear cache on theme change to force redraw (STEP 2)
        self._is_updating = True
        
        self.db.set_heatmap_theme(theme)
        if self.heatmap_var.get():
            self.heatmap_legend.draw_legend(theme)
            self.update_heatmap_colors()
            
        self.update_idletasks()
        self._is_updating = False

    # =====================================================================
    # Key Glow Flash Animation
    # =====================================================================
    def flash_key(self, key_name):
        try:
            btn = self.key_buttons.get(key_name)
            if not btn or not hasattr(btn, 'configure'):
                return
                
            btn.configure(fg_color=ACCENT, text_color=TEXT_PRIMARY)
            self.keyboard_container.update_idletasks()
            
            self.after(50, lambda: self.fade_key_step(key_name, 0.25))
        except Exception as e:
            logging.exception(f"Error flashing key '{key_name}': {e}")

    def fade_key_step(self, key_name, ratio):
        try:
            btn = self.key_buttons.get(key_name)
            if not btn or not hasattr(btn, 'configure'):
                return
                
            target_color = self.get_key_target_color(key_name)
            resting_text_color = TEXT_PRIMARY if self.heatmap_var.get() else TEXT_SECONDARY
            
            if ratio >= 1.0:
                btn.configure(fg_color=target_color, text_color=resting_text_color)
                self.keyboard_container.update_idletasks()
                return
                
            glow_color = ACCENT
            glow_text_color = TEXT_PRIMARY
            
            def hex_to_rgb(h):
                h = h.lstrip('#')
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                
            c_glow_bg = hex_to_rgb(glow_color)
            c_target_bg = hex_to_rgb(target_color)
            
            c_glow_txt = hex_to_rgb(glow_text_color)
            c_target_txt = hex_to_rgb(resting_text_color)
            
            bg_r = int(c_glow_bg[0] + (c_target_bg[0] - c_glow_bg[0]) * ratio)
            bg_g = int(c_glow_bg[1] + (c_target_bg[1] - c_glow_bg[1]) * ratio)
            bg_b = int(c_glow_bg[2] + (c_target_bg[2] - c_glow_bg[2]) * ratio)
            fade_bg = f"#{bg_r:02x}{bg_g:02x}{bg_b:02x}"
            
            txt_r = int(c_glow_txt[0] + (c_target_txt[0] - c_glow_txt[0]) * ratio)
            txt_g = int(c_glow_txt[1] + (c_target_txt[1] - c_glow_txt[1]) * ratio)
            txt_b = int(c_glow_txt[2] + (c_target_txt[2] - c_glow_txt[2]) * ratio)
            fade_txt = f"#{txt_r:02x}{txt_g:02x}{txt_b:02x}"
            
            btn.configure(fg_color=fade_bg, text_color=fade_txt)
            self.keyboard_container.update_idletasks()
            
            self.after(35, lambda: self.fade_key_step(key_name, ratio + 0.25))
        except Exception:
            pass

    # =====================================================================
    # Window Resize Debouncing (FIX 3)
    # =====================================================================
    def on_resize(self, event):
        if event.widget != self:
            return
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(120, self._execute_delayed_resize)

    def _execute_delayed_resize(self):
        self._resize_job = None
        self._is_updating = True
        self.update_idletasks()
        self._is_updating = False

    # =====================================================================
    # Statistics Updates
    # =====================================================================
    def update_ui_stats(self):
        try:
            apm, wpm = self.tracker.get_apm_wpm()
            self.header_apm_label.configure(text=f"APM: {apm}")
            self.header_wpm_label.configure(text=f"WPM: {wpm}")
            
            session_dur = self.tracker.get_session_duration()
            self.session_time_lbl.configure(text=session_dur)
            
            # Leaderboard & stats calculations read from viewing_profile (Requirement 12)
            aggregated = self.db.get_aggregated_stats(self.viewing_profile)
            
            total_keys = sum(aggregated.get("keys", {}).values())
            self.session_keys_lbl.configure(text=f"Keys: {total_keys}")
            
            keys_data = aggregated.get("keys", {})
            total_clicks = sum(keys_data.values())
            backspace_clicks = keys_data.get("Backspace", 0) + keys_data.get("Delete", 0)
            ratio = (backspace_clicks / total_clicks) * 100 if total_clicks > 0 else 0.0
            self.error_ratio_lbl.configure(text=f"⌫ Ratio: {ratio:.1f}%")
            
            # Leaderboard
            sorted_keys = sorted(keys_data.items(), key=lambda x: x[1], reverse=True)[:len(self.top_keys_labels)]
            for idx in range(len(self.top_keys_labels)):
                lbl = self.top_keys_labels[idx]
                if idx < len(sorted_keys):
                    k, count = sorted_keys[idx]
                    k_lbl = k
                    if k == "Space": k_lbl = "Space"
                    elif k.startswith("Kp_"): k_lbl = "Num" + k.replace("Kp_", "")
                    lbl.configure(text=f"{idx+1}. {k_lbl} : {count}")
                else:
                    lbl.configure(text=f"{idx+1}. —")
                    
            sorted_combos = sorted(aggregated.get("combinations", {}).items(), key=lambda x: x[1], reverse=True)[:len(self.top_combos_labels)]
            for idx in range(len(self.top_combos_labels)):
                lbl = self.top_combos_labels[idx]
                if idx < len(sorted_combos):
                    combo, count = sorted_combos[idx]
                    lbl.configure(text=f"{idx+1}. {combo} : {count}")
                else:
                    lbl.configure(text=f"{idx+1}. —")
                    
            # Bursts
            bursts = self.db.get_burst_records(self.viewing_profile)
            self.total_bursts_lbl.configure(text=f"{len(bursts)} recorded")
            for idx in range(len(self.burst_labels)):
                lbl = self.burst_labels[idx]
                if idx < len(bursts):
                    record = bursts[idx]
                    lbl.configure(text=f"{idx+1}. {record['peak_apm']}APM {record['duration']}s")
                else:
                    lbl.configure(text=f"{idx+1}. —")
                    
            # Chart (read from get_stats_for_profile)
            profile_data = self.db.get_stats_for_profile(self.viewing_profile)
            hourly_data = profile_data.get("hourly", {})
            self.chart_canvas.draw_chart(hourly_data)
            
            if self.overlay:
                self.overlay.update_stats(apm, wpm)
                
            if apm >= 250:
                self.led_canvas.itemconfig(self.led_circle, fill=ACCENT)
                self.led_lbl.configure(text_color=ACCENT)
            else:
                self.led_canvas.itemconfig(self.led_circle, fill="#333333")
                self.led_lbl.configure(text_color=TEXT_SECONDARY)
                
            if self.incognito_var.get():
                self.status_left_lbl.configure(text="System Status: Incognito Active", text_color=DANGER)
            else:
                self.status_left_lbl.configure(text="System Status: Tracking Active", text_color=ACCENT)
                
            # Process Indicator (Requirement 20)
            proc = self.tracker.last_detected_process
            active = self.tracker.active_profile
            icon = "🎮" if active == "Gaming" else "🖥️" if active == "Desktop" else "●"
            text_val = f"{icon} {proc} → {active}" if proc else "● Tracking"
            self.proc_label.configure(text=text_val)
                
        except Exception as e:
            logging.exception(f"Error updating UI stats: {e}")

    def run_background_updates(self):
        """Periodically runs background updates, rate-limiting UI updates (FIX 5)."""
        if not self._heatmap_loop_started:
            self._heatmap_loop_started = True
            self.after(2000, self._refresh_heatmap_colors)
            
        try:
            self.db.save_data()
            
            # Skip UI updates if window is minimized or hidden in system tray
            if self.state() in ["iconic", "withdrawn"]:
                return
                
            # Skip if a resize or theme change operation is already active
            if self._is_updating:
                return
                
            self.update_ui_stats()
        except Exception as e:
            logging.exception(f"Error in background update loop: {e}")
        finally:
            try:
                self.after(1000, self.run_background_updates)
            except Exception:
                pass

    # Independent heatmap refresh loop scheduled at 2000ms (STEP 3)
    def _refresh_heatmap_colors(self):
        if not self.heatmap_var.get():
            self.after(2000, self._refresh_heatmap_colors)
            return
        if getattr(self, '_heatmap_busy', False):
            self.after(2000, self._refresh_heatmap_colors)
            return
        self._heatmap_busy = True
        try:
            self.update_heatmap_colors()
        finally:
            self._heatmap_busy = False
            self.after(2000, self._refresh_heatmap_colors)

    # =====================================================================
    # Profile Selector Utilities (Requirement 10 & 12)
    # =====================================================================
    def get_custom_profiles(self):
        """Returns the list of custom profiles (excluding built-in profiles)."""
        return [p for p in self.db.get_profiles() if p not in ("Total", "Desktop", "Gaming")]

    def update_profile_selector_ui(self):
        """Updates the styling and configuration of the profile buttons and combobox."""
        profile = self.viewing_profile
        
        # Total button
        if profile == "Total":
            self.btn_total.configure(fg_color=ACCENT, text_color=BG_MAIN, font=(FONT_FAMILY, 10, "bold"))
        else:
            self.btn_total.configure(fg_color=KEYCAP_BASE, text_color=TEXT_SECONDARY, font=(FONT_FAMILY, 10))
            
        # Desktop button
        if profile == "Desktop":
            self.btn_desktop.configure(fg_color=ACCENT, text_color=BG_MAIN, font=(FONT_FAMILY, 10, "bold"))
        else:
            self.btn_desktop.configure(fg_color=KEYCAP_BASE, text_color=TEXT_SECONDARY, font=(FONT_FAMILY, 10))
            
        # Gaming button
        if profile == "Gaming":
            self.btn_gaming.configure(fg_color=ACCENT, text_color=BG_MAIN, font=(FONT_FAMILY, 10, "bold"))
        else:
            self.btn_gaming.configure(fg_color=KEYCAP_BASE, text_color=TEXT_SECONDARY, font=(FONT_FAMILY, 10))
            
        # Update combobox options and value
        custom_profiles = self.get_custom_profiles()
        self.profile_combobox.configure(values=custom_profiles)
        
        if profile in ("Total", "Desktop", "Gaming"):
            self.profile_combobox.set("custom ▾")
            self.del_profile_btn.pack_forget()
        else:
            self.profile_combobox.set(profile)
            # Re-pack trash delete button next to custom combobox
            self.del_profile_btn.pack(side="left", padx=2)

    def _set_viewing_profile(self, name):
        """Sets the viewing profile, updates active states, and updates UI stats."""
        self.viewing_profile = name
        self.update_profile_selector_ui()
        self.update_heatmap_colors()
        self.update_ui_stats()

    def switch_viewing_profile(self, profile_name):
        """Switches only the display stats VIEW to the selected profile."""
        self._set_viewing_profile(profile_name)

    def on_custom_profile_selected(self, profile_name):
        """Triggered when a custom profile is picked in the combobox."""
        if profile_name == "custom ▾":
            return
        self._set_viewing_profile(profile_name)

    # =====================================================================
    # Profile Management
    # =====================================================================
    def change_profile(self, profile_name):
        # Triggered by tracker background thread auto-switching event
        # Do NOT override self.viewing_profile automatically — the user may be
        # viewing a different profile intentionally. Only update indicators.
        self.update_ui_stats()

    def create_profile_dialog(self):
        dialog = customtkinter.CTkInputDialog(text="Enter new profile name:", title="Add Profile")
        name = dialog.get_input()
        if name:
            name = name.strip()
            if self.db.create_profile(name):
                self.viewing_profile = name
                self.tracker.set_profile(name)
                self.db.set_last_profile(name)
                self.update_profile_selector_ui()
                self.update_heatmap_colors()
                self.update_ui_stats()
                ToastNotification(self, f"Profile '{name}' created.", "success")
            else:
                ToastNotification(self, "Profile name empty or already exists.", "error")

    def delete_active_profile(self):
        profile = self.viewing_profile
        if profile in ("Default", "Total", "Desktop", "Gaming"):
            ToastNotification(self, "Cannot delete protected profiles.", "error")
            return
            
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete profile '{profile}'? All statistics will be permanently lost."
        )
        if confirm:
            self.db.delete_profile(profile)
            self.viewing_profile = "Default"
            self.tracker.set_profile("Default")
            self.db.set_last_profile("Default")
            self.update_profile_selector_ui()
            self.update_heatmap_colors()
            self.update_ui_stats()
            ToastNotification(self, f"Profile '{profile}' deleted.", "success")

    # =====================================================================
    # Toggles & Settings
    # =====================================================================
    def toggle_incognito(self):
        self.tracker.incognito_mode = self.incognito_var.get()
        if self.tracker.incognito_mode:
            self.logo_label.configure(text_color=DANGER)
        else:
            self.logo_label.configure(text_color=ACCENT)

    def toggle_overlay(self):
        enabled = self.overlay_var.get()
        self.db.set_overlay_enabled(enabled)
        if enabled:
            if not self.overlay:
                self.overlay = FloatingOverlay(self)
        else:
            if self.overlay:
                try:
                    self.overlay.destroy()
                except Exception:
                    pass
                self.overlay = None

    def update_incognito_ui_state(self, value):
        self.incognito_var.set(value)
        self.toggle_incognito()

    def toggle_startup(self):
        utils.set_startup(self.startup_var.get())

    # =====================================================================
    # Dialogs & Exports
    # =====================================================================
    def open_mappings_dialog(self):
        ProcessMappingDialog(self, self.db)

    def open_about_dialog(self):
        AboutDialog(self)

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Export Profile Statistics to CSV",
            initialfile=f"typetrace_{self.viewing_profile.lower()}_stats.csv"
        )
        if filepath:
            aggregated = self.db.get_aggregated_stats(self.viewing_profile)
            if utils.export_stats_to_csv(filepath, aggregated):
                ToastNotification(self, f"CSV exported successfully!", "success")
            else:
                ToastNotification(self, "Export failed. Check permissions.", "error")

    def export_json(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Export Profile Statistics to JSON",
            initialfile=f"typetrace_{self.viewing_profile.lower()}_stats.json"
        )
        if filepath:
            try:
                aggregated = self.db.get_aggregated_stats(self.viewing_profile)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(aggregated, f, indent=4)
                ToastNotification(self, f"JSON exported successfully!", "success")
            except Exception as e:
                ToastNotification(self, f"Export failed: {e}", "error")

    def reset_statistics_dialog(self):
        confirm = messagebox.askyesno(
            "Reset Statistics", 
            f"Are you sure you want to clear statistics for profile '{self.viewing_profile}'?\n"
            "This action cannot be undone."
        )
        if confirm:
            self._key_color_cache = {}  # Clear cache on reset (STEP 2)
            self.db.reset_profile_statistics(self.viewing_profile)
            self.update_heatmap_colors()
            self.update_ui_stats()
            ToastNotification(self, f"Statistics for '{self.viewing_profile}' reset.", "success")

    # =====================================================================
    # Window Management
    # =====================================================================
    def withdraw_to_tray(self):
        self.withdraw()

    def restore_from_tray(self):
        self.after(0, self.mostra_finestra)

    def mostra_finestra(self):
        self.deiconify()
        self.focus_force()
        self.lift()

    # =====================================================================
    # Thread-Safe Event Queue Processing
    # =====================================================================
    def process_event_queue(self, event_queue):
        for _ in range(50):
            try:
                event_type, val = event_queue.get_nowait()
                self.handle_thread_event(event_type, val)
                event_queue.task_done()
            except queue.Empty:
                break
                
        try:
            self.after(30, lambda: self.process_event_queue(event_queue))
        except Exception:
            pass

    def handle_thread_event(self, event_type, val):
        try:
            if event_type == "keystroke":
                self.flash_key(val)
                self.update_ui_stats()
            elif event_type == "incognito":
                self.update_incognito_ui_state(val)
            elif event_type == "restore":
                self.restore_from_tray()
            elif event_type == "toggle_incognito":
                self.tracker.toggle_incognito()
            elif event_type == "toggle_overlay":
                current = self.overlay_var.get()
                self.overlay_var.set(not current)
                self.toggle_overlay()
            elif event_type == "burst_detected":
                self.update_ui_stats()
            elif event_type == "profile_changed":
                self.change_profile(val)
            elif event_type == "exit":
                if self.shutdown_callback:
                    self.shutdown_callback(val)
        except Exception as e:
            logging.exception(f"Error handling thread event '{event_type}': {e}")
