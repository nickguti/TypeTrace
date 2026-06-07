import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter
from datetime import datetime
import logging
import queue
import webbrowser

import utils
from overlay import FloatingOverlay

# App Constants
APP_VERSION = "1.0.0"
APP_GITHUB = "https://github.com/typetrace/typetrace"

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
    ("spacer", 0, 0, 1, 4, "spacer"), # Align top row spacer (where F-keys align)
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
        
        # Color based on type
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
        
        # Create toast frame
        self.frame = customtkinter.CTkFrame(
            parent,
            fg_color=bg_color,
            border_color=border_color,
            border_width=1,
            corner_radius=10
        )
        
        # Toast content
        self.label = customtkinter.CTkLabel(
            self.frame,
            text=f" {icon}  {message}",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=text_color,
            anchor="w"
        )
        self.label.pack(padx=16, pady=10)
        
        # Position at bottom-right
        self.frame.place(relx=1.0, rely=1.0, anchor="se", x=-30, y=-70)
        self.frame.lift()
        
        # Auto-dismiss
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
        # Progressively reduce visibility by moving down
        try:
            self.frame.place(relx=1.0, rely=1.0, anchor="se", x=-30, y=-70 + (self._fade_step * 15))
            self.parent.after(50, self._start_fade)
        except Exception:
            pass


# =====================================================================
# Tooltip
# =====================================================================

class Tooltip:
    def __init__(self, widget, get_text_func):
        self.widget = widget
        self.get_text_func = get_text_func
        self.tip_window = None
        self.id = None
        
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        
    def enter(self, event=None):
        self.schedule()
        
    def leave(self, event=None):
        self.unschedule()
        self.hide_tip()
        
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(250, self.show_tip)
        
    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
            
    def show_tip(self, event=None):
        x = self.widget.winfo_pointerx() + 15
        y = self.widget.winfo_pointery() + 15
        
        self.tip_window = tw = customtkinter.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-alpha", 0.95)
        tw.attributes("-topmost", True)
        tw.transient(self.widget.winfo_toplevel())
        
        frame = customtkinter.CTkFrame(
            tw,
            fg_color=BG_CARD_INNER,
            border_color=ACCENT,
            border_width=1.5,
            corner_radius=8
        )
        frame.pack(padx=1, pady=1, fill="both", expand=True)
        
        text = self.get_text_func()
        label = customtkinter.CTkLabel(
            frame,
            text=text,
            justify="left",
            font=(FONT_FAMILY, 10),
            text_color=TEXT_PRIMARY,
            padx=12,
            pady=10
        )
        label.pack()
        
    def hide_tip(self):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None

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
        
        # 24 hours distribution bucket
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
            
        # Draw background grid lines
        grid_lines_count = 3
        for i in range(1, grid_lines_count + 1):
            y = height - padding_y - (chart_h * i / (grid_lines_count + 1))
            self.create_line(padding_x, y, width - padding_x, y, fill=GRID_LINE, width=1)
            
        # Draw X Axis line
        self.create_line(padding_x, height - padding_y, width - padding_x, height - padding_y, fill=GRID_LINE, width=1)
        
        # Draw bars with gradient
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
                
            # Rounded top cap
            self.create_oval(x0, y0 - 3, x1, y0 + 3, fill=ACCENT, outline="")
            
        # Draw labels
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
            
        # Draw gradient slices
        num_slices = min(bar_w, 100)
        for i in range(num_slices):
            t = i / max(1, num_slices - 1)
            color = utils.interpolate_color(t, theme=theme)
            x0 = bar_x0 + (bar_w * i / num_slices)
            x1 = bar_x0 + (bar_w * (i + 1) / num_slices)
            self.create_rectangle(x0, bar_y0, x1, bar_y1, fill=color, outline="")
        
        # Labels
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
        self.geometry("450x450")
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
        
        # Configuration entry row
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
        
        self.profile_combo = customtkinter.CTkComboBox(
            add_frame, values=self.db.get_profiles(), width=100,
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
        
        # Scrollable mapping list
        self.list_frame = customtkinter.CTkScrollableFrame(
            frame, height=200, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=12
        )
        self.list_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.load_mappings()
        
    def load_mappings(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        mappings = self.db.get_profile_mappings()
        for idx, (proc, prof) in enumerate(mappings.items()):
            row_frame = customtkinter.CTkFrame(self.list_frame, fg_color=KEYCAP_BASE, border_color=BORDER_COLOR, border_width=1, corner_radius=8)
            row_frame.pack(fill="x", pady=2, padx=2)
            
            lbl = customtkinter.CTkLabel(row_frame, text=f"{proc}  ➜  {prof}", font=("Consolas", 10, "bold"), text_color=TEXT_PRIMARY, anchor="w")
            lbl.pack(side="left", padx=10, pady=5)
            
            del_btn = customtkinter.CTkButton(
                row_frame, text="Remove", width=60, fg_color=DANGER, hover_color=DANGER_HOVER, text_color=TEXT_PRIMARY, font=(FONT_FAMILY, 10, "bold"),
                command=lambda p=proc: self.delete_mapping(p)
            )
            del_btn.pack(side="right", padx=10, pady=5)
            
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

    def delete_mapping(self, proc):
        mappings = self.db.get_profile_mappings()
        if proc in mappings:
            del mappings[proc]
            self.db.set_profile_mappings(mappings)
            self.load_mappings()


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
        
        # Logo
        logo = customtkinter.CTkLabel(frame, text="TYPETRACE", font=(FONT_FAMILY, 28, "bold"), text_color=ACCENT)
        logo.pack(pady=(25, 2))
        
        # Version
        version_lbl = customtkinter.CTkLabel(frame, text=f"v{APP_VERSION}", font=(FONT_FAMILY, 12), text_color=TEXT_SECONDARY)
        version_lbl.pack(pady=(0, 12))
        
        # Description
        desc = customtkinter.CTkLabel(
            frame, 
            text="Privacy-focused keystroke analytics.\nAll data stored locally on your machine.",
            font=(FONT_FAMILY, 11), text_color=TEXT_SECONDARY, justify="center"
        )
        desc.pack(pady=(0, 16))
        
        # Separator
        sep = customtkinter.CTkFrame(frame, fg_color=BORDER_COLOR, height=1)
        sep.pack(fill="x", padx=30, pady=(0, 16))
        
        # GitHub link
        github_lbl = customtkinter.CTkLabel(
            frame,
            text=f"★ GitHub Repository",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=ACCENT,
            cursor="hand2"
        )
        github_lbl.pack(pady=(0, 5))
        github_lbl.bind("<Button-1>", lambda e: webbrowser.open(APP_GITHUB))
        
        # Made with love
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
        self.minsize(1100, 680)
        self.configure(fg_color=BG_MAIN)
        
        # Set programmatic icon
        self._set_window_icon()
        
        # Window setup & close interception
        self.protocol('WM_DELETE_WINDOW', self.withdraw_to_tray)
        
        # State references
        self.overlay = None
        self.current_layout = "ANSI 100%"
        self._status_pulse_step = 0
        
        # Tkinter state variables
        self.incognito_var = tk.BooleanVar(value=self.tracker.incognito_mode)
        self.heatmap_var = tk.BooleanVar(value=False)
        self.startup_var = tk.BooleanVar(value=utils.is_startup_enabled())
        self.overlay_var = tk.BooleanVar(value=self.db.get_overlay_enabled())
        
        # Visual assets map
        self.key_buttons = {}
        self.tooltips = {}
        
        # Build UI layout
        self.setup_layout()
        
        # Initial statistics update
        self.update_ui_stats()
        
        # Load floating overlay on launch if enabled in config
        if self.overlay_var.get():
            self.after(500, self.toggle_overlay)
            
        # Run background loop to update APM/WPM/Stats periodically
        self.run_background_updates()
        
        # Start status dot pulse animation
        self._pulse_status_dot()

    def _set_window_icon(self):
        """Set window icon programmatically using Pillow."""
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
            self._icon_ref = photo  # Keep reference to prevent GC
        except Exception:
            pass

    def setup_layout(self):
        # Master frame for all content (allows padding)
        self.master_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.master_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # =====================================================================
        # 1. TOP HEADER BAR
        # =====================================================================
        self.header_frame = customtkinter.CTkFrame(self.master_frame, fg_color="transparent", height=55)
        self.header_frame.pack(fill="x", pady=(0, 12))
        self.header_frame.pack_propagate(False)

        # Left Side: Logo & Sub-logo
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

        # Center: Live APM / WPM
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

        # Right Side: Status dot + About button
        self.header_right = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_right.pack(side="right")

        # Status indicator
        self.status_indicator_frame = customtkinter.CTkFrame(self.header_right, fg_color="transparent")
        self.status_indicator_frame.pack(side="left", padx=(0, 12))
        
        self.status_dot_canvas = tk.Canvas(self.status_indicator_frame, width=12, height=12, bg=BG_MAIN, highlightthickness=0)
        self.status_dot_canvas.pack(side="left", padx=(0, 6))
        self.status_dot = self.status_dot_canvas.create_oval(1, 1, 11, 11, fill=ACCENT, outline="")
        
        self.status_text = customtkinter.CTkLabel(
            self.status_indicator_frame, text="Tracking", font=(FONT_FAMILY, 10, "bold"), text_color=ACCENT
        )
        self.status_text.pack(side="left")

        # About button
        self.about_btn = customtkinter.CTkButton(
            self.header_right, text="?", width=32, height=32,
            fg_color=KEYCAP_BASE, hover_color=KEYCAP_HOVER, text_color=TEXT_SECONDARY,
            font=(FONT_FAMILY, 14, "bold"), corner_radius=16,
            command=self.open_about_dialog
        )
        self.about_btn.pack(side="left", padx=(8, 0))

        # =====================================================================
        # 2. KEYBOARD SECTION (Top Card)
        # =====================================================================
        self.top_card = customtkinter.CTkFrame(self.master_frame, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        self.top_card.pack(fill="both", expand=True, pady=(0, 12))

        # Keyboard header row
        self.kb_header = customtkinter.CTkFrame(self.top_card, fg_color="transparent")
        self.kb_header.pack(fill="x", padx=20, pady=(12, 3))
        
        self.main_title = customtkinter.CTkLabel(
            self.kb_header, text="Virtual Keyboard Analytics", font=(FONT_FAMILY, 14, "bold"), text_color=TEXT_PRIMARY
        )
        self.main_title.pack(side="left")
        
        # Layout switcher dropdown
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
        self.main_subtitle.pack(anchor="w", padx=20, pady=(0, 8))
        
        # Keyboard container
        self.keyboard_container = customtkinter.CTkFrame(self.top_card, fg_color="transparent")
        self.keyboard_container.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        
        self.keyboard_container.grid_columnconfigure(0, weight=15, uniform="block_cols")
        self.keyboard_container.grid_columnconfigure(1, weight=3, uniform="block_cols")
        self.keyboard_container.grid_columnconfigure(2, weight=4, uniform="block_cols")
        self.keyboard_container.grid_rowconfigure(0, weight=1)
        
        self.left_keyboard_frame = customtkinter.CTkFrame(
            self.keyboard_container, fg_color=BG_MAIN, border_color=BORDER_COLOR, border_width=1, corner_radius=12
        )
        self.left_keyboard_frame.grid(row=0, column=0, padx=(0, 25), pady=0, sticky="nsew")
        
        self.nav_keyboard_frame = customtkinter.CTkFrame(
            self.keyboard_container, fg_color=BG_MAIN, border_color=BORDER_COLOR, border_width=1, corner_radius=12
        )
        self.nav_keyboard_frame.grid(row=0, column=1, padx=(0, 25), pady=0, sticky="nsew")
        
        self.numpad_keyboard_frame = customtkinter.CTkFrame(
            self.keyboard_container, fg_color=BG_MAIN, border_color=BORDER_COLOR, border_width=1, corner_radius=12
        )
        self.numpad_keyboard_frame.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")
        
        self.generate_keyboard()
        
        # Heatmap Legend (hidden by default, shown when heatmap is active)
        self.heatmap_legend = HeatmapLegend(self.top_card)
        # Not packed yet — will show/hide via toggle_heatmap

        # =====================================================================
        # 3. BOTTOM SECTION: Three-Column Grid
        # =====================================================================
        self.bottom_grid = customtkinter.CTkFrame(self.master_frame, fg_color="transparent")
        self.bottom_grid.pack(fill="x", pady=(0, 12))

        self.bottom_grid.grid_columnconfigure(0, weight=1, uniform="bottom_cols")
        self.bottom_grid.grid_columnconfigure(1, weight=1, uniform="bottom_cols")
        self.bottom_grid.grid_columnconfigure(2, weight=1, uniform="bottom_cols")

        # =====================================================================
        # CARD 0: CONFIGURATION & THEMES
        # =====================================================================
        self.config_card = customtkinter.CTkFrame(self.bottom_grid, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        self.config_card.grid(row=0, column=0, padx=(0, 12), sticky="nsew")

        self.config_title = customtkinter.CTkLabel(self.config_card, text="⚙️ CONFIGURATION", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY)
        self.config_title.pack(anchor="w", padx=15, pady=(12, 8))

        self.config_inner = customtkinter.CTkFrame(self.config_card, fg_color="transparent")
        self.config_inner.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        self.config_inner.columnconfigure(0, weight=1, uniform="config_cols")
        self.config_inner.columnconfigure(1, weight=1, uniform="config_cols")

        # Left Column - Profiles & Theme
        self.config_left = customtkinter.CTkFrame(self.config_inner, fg_color="transparent")
        self.config_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.profile_lbl = customtkinter.CTkLabel(self.config_left, text="Active Profile:", font=(FONT_FAMILY, 10), text_color=TEXT_SECONDARY)
        self.profile_lbl.pack(anchor="w", pady=(0, 2))

        self.profile_row = customtkinter.CTkFrame(self.config_left, fg_color="transparent")
        self.profile_row.pack(fill="x", pady=(0, 6))

        self.profile_combobox = customtkinter.CTkComboBox(
            self.profile_row, values=self.db.get_profiles(), command=self.change_profile, width=110, height=26,
            font=(FONT_FAMILY, 10), fg_color=KEYCAP_BASE, border_color=BORDER_COLOR, button_color=KEYCAP_BASE, button_hover_color=KEYCAP_HOVER,
            text_color=TEXT_PRIMARY, dropdown_fg_color=KEYCAP_BASE, dropdown_hover_color=KEYCAP_HOVER, dropdown_text_color=TEXT_PRIMARY
        )
        self.profile_combobox.set(self.tracker.active_profile)
        self.profile_combobox.pack(side="left", padx=(0, 4))

        self.add_profile_btn = customtkinter.CTkButton(
            self.profile_row, text="+", width=24, height=26, fg_color=KEYCAP_BASE, hover_color=ACCENT, text_color=TEXT_PRIMARY, font=(FONT_FAMILY, 12, "bold"), command=self.create_profile_dialog
        )
        self.add_profile_btn.pack(side="left", padx=2)

        self.del_profile_btn = customtkinter.CTkButton(
            self.profile_row, text="🗑", width=24, height=26, fg_color=KEYCAP_BASE, hover_color=DANGER, text_color=TEXT_PRIMARY, font=(FONT_FAMILY, 11, "bold"), command=self.delete_active_profile
        )
        self.del_profile_btn.pack(side="left", padx=2)

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

        # =====================================================================
        # CARD 1: TELEMETRY — 3 Mini-Cards
        # =====================================================================
        self.telemetry_card = customtkinter.CTkFrame(self.bottom_grid, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        self.telemetry_card.grid(row=0, column=1, padx=(0, 12), sticky="nsew")

        self.telemetry_title = customtkinter.CTkLabel(self.telemetry_card, text="📊 TELEMETRY & METRICS", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY)
        self.telemetry_title.pack(anchor="w", padx=15, pady=(12, 8))

        # Mini-cards container
        self.mini_cards = customtkinter.CTkFrame(self.telemetry_card, fg_color="transparent")
        self.mini_cards.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        
        self.mini_cards.columnconfigure(0, weight=1, uniform="mini")
        self.mini_cards.columnconfigure(1, weight=1, uniform="mini")
        self.mini_cards.columnconfigure(2, weight=1, uniform="mini")
        self.mini_cards.rowconfigure(0, weight=1)

        # --- Mini-Card A: Session Stats ---
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

        # --- Mini-Card B: Leaderboard ---
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

        # --- Mini-Card C: Bursts ---
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

        # =====================================================================
        # CARD 2: PRODUCTIVITY PROFILE
        # =====================================================================
        self.chart_card = customtkinter.CTkFrame(self.bottom_grid, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=16)
        self.chart_card.grid(row=0, column=2, sticky="nsew")

        self.chart_title = customtkinter.CTkLabel(self.chart_card, text="📈 HOURLY PRODUCTIVITY", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY)
        self.chart_title.pack(anchor="w", padx=15, pady=(12, 8))

        self.chart_canvas = ProductivityChart(self.chart_card)
        self.chart_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # =====================================================================
        # STATUS BAR (Bottom)
        # =====================================================================
        self.status_bar = customtkinter.CTkFrame(self.master_frame, height=30, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=12)
        self.status_bar.pack(fill="x", pady=(0, 0))

        self.status_left_lbl = customtkinter.CTkLabel(
            self.status_bar, text="System Status: Tracking Active", font=(FONT_FAMILY, 10), text_color=ACCENT
        )
        self.status_left_lbl.pack(side="left", padx=15, pady=4)

        # LED Frame
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
        """Pulses the header status dot between bright and dim to indicate active tracking."""
        try:
            if self.incognito_var.get():
                # Red pulsing in incognito
                colors = ["#A63A50", "#D44D63", "#A63A50", "#8A3040"]
            else:
                # Green pulsing in normal mode
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
    # Keyboard Generation
    # =====================================================================
    def generate_keyboard(self):
        # 1. LEFT BLOCK
        for col in range(60):
            self.left_keyboard_frame.grid_columnconfigure(col, weight=1, uniform="left_col")
        for row in range(6):
            self.left_keyboard_frame.grid_rowconfigure(row, weight=1, uniform="left_row")
            
        for row_idx, row_keys in enumerate(LEFT_KEYBOARD_LAYOUT):
            current_col = 0
            for label, span, db_key in row_keys:
                if db_key == "spacer":
                    current_col += span
                    continue
                    
                btn = customtkinter.CTkButton(
                    self.left_keyboard_frame,
                    text=label,
                    fg_color=KEYCAP_BASE,
                    text_color=TEXT_SECONDARY,
                    hover_color=KEYCAP_HOVER,
                    font=(FONT_FAMILY, 10),
                    corner_radius=6,
                    border_width=0,
                    cursor="hand2"
                )
                btn.grid(row=row_idx, column=current_col, columnspan=span, padx=2, pady=2, sticky="nsew")
                
                self.key_buttons[db_key] = btn
                self.tooltips[db_key] = Tooltip(btn, lambda k=db_key: self.get_key_tooltip_text(k))
                current_col += span

        # 2. NAV BLOCK
        for col in range(3):
            self.nav_keyboard_frame.grid_columnconfigure(col, weight=1, uniform="nav_col")
        for row in range(6):
            self.nav_keyboard_frame.grid_rowconfigure(row, weight=1, uniform="nav_row")
            
        for row_idx, row_keys in enumerate(NAV_KEYBOARD_LAYOUT):
            for col_idx, (label, span, db_key) in enumerate(row_keys):
                if db_key == "spacer" or label == "empty":
                    continue
                    
                btn = customtkinter.CTkButton(
                    self.nav_keyboard_frame,
                    text=label,
                    fg_color=KEYCAP_BASE,
                    text_color=TEXT_SECONDARY,
                    hover_color=KEYCAP_HOVER,
                    font=(FONT_FAMILY, 10),
                    corner_radius=6,
                    border_width=0,
                    cursor="hand2"
                )
                btn.grid(row=row_idx, column=col_idx, columnspan=span, padx=2, pady=2, sticky="nsew")
                
                self.key_buttons[db_key] = btn
                self.tooltips[db_key] = Tooltip(btn, lambda k=db_key: self.get_key_tooltip_text(k))

        # 3. NUMPAD BLOCK
        for col in range(4):
            self.numpad_keyboard_frame.grid_columnconfigure(col, weight=1, uniform="num_col")
        for row in range(6):
            self.numpad_keyboard_frame.grid_rowconfigure(row, weight=1, uniform="num_row")
            
        for label, row, col, rowspan, colspan, db_key in NUMPAD_KEYBOARD_LAYOUT:
            if db_key == "spacer":
                continue
                
            btn = customtkinter.CTkButton(
                self.numpad_keyboard_frame,
                text=label,
                fg_color=KEYCAP_BASE,
                text_color=TEXT_SECONDARY,
                hover_color=KEYCAP_HOVER,
                font=(FONT_FAMILY, 10),
                corner_radius=6,
                border_width=0,
                cursor="hand2"
            )
            btn.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, padx=2, pady=2, sticky="nsew")
            
            self.key_buttons[db_key] = btn
            self.tooltips[db_key] = Tooltip(btn, lambda k=db_key: self.get_key_tooltip_text(k))

    # =====================================================================
    # Keyboard Layout Switcher
    # =====================================================================
    def switch_keyboard_layout(self, layout_name):
        """Show/hide keyboard blocks based on selected layout."""
        self.current_layout = layout_name
        
        # Function row is row 0 of left keyboard
        func_row_keys = [k for _, _, k in LEFT_KEYBOARD_LAYOUT[0] if k != "spacer"]
        
        if layout_name == "ANSI 100%":
            # Show everything
            self.nav_keyboard_frame.grid()
            self.numpad_keyboard_frame.grid()
            for k in func_row_keys:
                if k in self.key_buttons:
                    self.key_buttons[k].grid()
            # Show arrow keys
            for k in ["Up", "Down", "Left", "Right"]:
                if k in self.key_buttons:
                    self.key_buttons[k].grid()
                    
        elif layout_name == "TKL":
            # Hide numpad, show nav
            self.nav_keyboard_frame.grid()
            self.numpad_keyboard_frame.grid_remove()
            for k in func_row_keys:
                if k in self.key_buttons:
                    self.key_buttons[k].grid()
            for k in ["Up", "Down", "Left", "Right"]:
                if k in self.key_buttons:
                    self.key_buttons[k].grid()
                    
        elif layout_name == "75%":
            # Hide numpad, show nav compact
            self.numpad_keyboard_frame.grid_remove()
            self.nav_keyboard_frame.grid()
            for k in func_row_keys:
                if k in self.key_buttons:
                    self.key_buttons[k].grid()
            for k in ["Up", "Down", "Left", "Right"]:
                if k in self.key_buttons:
                    self.key_buttons[k].grid()
                    
        elif layout_name == "65%":
            # Hide numpad + nav + function row
            self.numpad_keyboard_frame.grid_remove()
            self.nav_keyboard_frame.grid_remove()
            for k in func_row_keys:
                if k in self.key_buttons:
                    self.key_buttons[k].grid_remove()
            # Keep arrows
            for k in ["Up", "Down", "Left", "Right"]:
                if k in self.key_buttons:
                    self.key_buttons[k].grid()
                    
        elif layout_name == "60%":
            # Hide numpad + nav + function row + arrows
            self.numpad_keyboard_frame.grid_remove()
            self.nav_keyboard_frame.grid_remove()
            for k in func_row_keys:
                if k in self.key_buttons:
                    self.key_buttons[k].grid_remove()
            for k in ["Up", "Down", "Left", "Right"]:
                if k in self.key_buttons:
                    self.key_buttons[k].grid_remove()

    # =====================================================================
    # Tooltip Generation
    # =====================================================================
    def get_key_tooltip_text(self, db_key):
        """Generates dynamic hover tooltip text for a key."""
        stats = self.db.get_key_stats(self.tracker.active_profile, db_key)
        
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
    # Heatmap
    # =====================================================================
    def toggle_heatmap(self):
        if self.heatmap_var.get():
            self.heatmap_legend.pack(fill="x", padx=20, pady=(0, 10))
            self.heatmap_legend.draw_legend(self.db.get_heatmap_theme())
        else:
            self.heatmap_legend.pack_forget()
        self.update_heatmap_colors()

    def update_heatmap_colors(self):
        """Recalculates colors for all buttons in the virtual keyboard layout."""
        if not self.heatmap_var.get():
            for db_key, btn in self.key_buttons.items():
                btn.configure(fg_color=KEYCAP_BASE, text_color=TEXT_SECONDARY, hover_color=KEYCAP_HOVER)
            return
            
        aggregated = self.db.get_aggregated_stats(self.tracker.active_profile)
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
        
        for db_key, btn in self.key_buttons.items():
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
            btn.configure(fg_color=heatmap_color, text_color=TEXT_PRIMARY, hover_color=heatmap_color)

    def get_key_target_color(self, key_name):
        """Calculates the resting color for a key cap based on current settings."""
        if self.heatmap_var.get():
            aggregated = self.db.get_aggregated_stats(self.tracker.active_profile)
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

    # =====================================================================
    # Key Flash Animation
    # =====================================================================
    def flash_key(self, key_name):
        """Briefly highlights a virtual key using a fade/glow effect transition."""
        try:
            if key_name not in self.key_buttons:
                return
                
            btn = self.key_buttons[key_name]
            btn.configure(fg_color=ACCENT, text_color=TEXT_PRIMARY)
            
            self.after(50, lambda: self.fade_key_step(btn, key_name, 0.25))
        except Exception as e:
            logging.exception(f"Error flashing key '{key_name}': {e}")

    def fade_key_step(self, btn, key_name, ratio):
        """Interpolates between the flash glow color and target color."""
        try:
            target_color = self.get_key_target_color(key_name)
            resting_text_color = TEXT_PRIMARY if self.heatmap_var.get() else TEXT_SECONDARY
            
            if ratio >= 1.0:
                btn.configure(fg_color=target_color, text_color=resting_text_color)
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
            
            self.after(35, lambda: self.fade_key_step(btn, key_name, ratio + 0.25))
        except Exception:
            pass

    # =====================================================================
    # Statistics Updates
    # =====================================================================
    def update_ui_stats(self):
        """Updates all metric displays, leaderboards, and charts."""
        try:
            # 1. Update APM / WPM (header)
            apm, wpm = self.tracker.get_apm_wpm()
            self.header_apm_label.configure(text=f"APM: {apm}")
            self.header_wpm_label.configure(text=f"WPM: {wpm}")
            
            # 2. Session stats mini-card
            session_dur = self.tracker.get_session_duration()
            self.session_time_lbl.configure(text=session_dur)
            self.session_keys_lbl.configure(text=f"Keys: {self.tracker.session_total_clicks}")
            
            total_clicks = self.tracker.session_total_clicks
            backspace_clicks = self.tracker.session_backspace_clicks
            ratio = (backspace_clicks / total_clicks) * 100 if total_clicks > 0 else 0.0
            self.error_ratio_lbl.configure(text=f"⌫ Ratio: {ratio:.1f}%")
            
            # 3. Leaderboard mini-card
            aggregated = self.db.get_aggregated_stats(self.tracker.active_profile)
            
            sorted_keys = sorted(aggregated.get("keys", {}).items(), key=lambda x: x[1], reverse=True)[:len(self.top_keys_labels)]
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
                    
            # 4. Burst records mini-card
            bursts = self.db.get_burst_records(self.tracker.active_profile)
            self.total_bursts_lbl.configure(text=f"{len(bursts)} recorded")
            for idx in range(len(self.burst_labels)):
                lbl = self.burst_labels[idx]
                if idx < len(bursts):
                    record = bursts[idx]
                    lbl.configure(text=f"{idx+1}. {record['peak_apm']}APM {record['duration']}s")
                else:
                    lbl.configure(text=f"{idx+1}. —")
                    
            # 5. Hourly Productivity Chart
            profile = self.tracker.active_profile
            hourly_data = self.db.data.get("profiles", {}).get(profile, {}).get("hourly", {})
            self.chart_canvas.draw_chart(hourly_data)
            
            # 6. Floating Overlay stats
            if self.overlay:
                self.overlay.update_stats(apm, wpm)
                
            # 7. LED indicator based on APM
            if apm >= 250:
                self.led_canvas.itemconfig(self.led_circle, fill=ACCENT)
                self.led_lbl.configure(text_color=ACCENT)
            else:
                self.led_canvas.itemconfig(self.led_circle, fill="#333333")
                self.led_lbl.configure(text_color=TEXT_SECONDARY)
                
            # 8. Update status bar and header dot based on incognito state
            if self.incognito_var.get():
                self.status_left_lbl.configure(text="System Status: Incognito Active", text_color=DANGER)
                self.status_text.configure(text="Incognito", text_color=DANGER)
            else:
                self.status_left_lbl.configure(text="System Status: Tracking Active", text_color=ACCENT)
                self.status_text.configure(text="Tracking", text_color=ACCENT)
                
        except Exception as e:
            logging.exception(f"Error updating UI stats: {e}")

    def run_background_updates(self):
        """Periodically runs background statistics updates and saves data to disk."""
        try:
            self.update_ui_stats()
            self.db.save_data()
            if self.heatmap_var.get():
                self.update_heatmap_colors()
        except Exception as e:
            logging.exception(f"Error in background update loop: {e}")
        finally:
            try:
                self.after(1500, self.run_background_updates)
            except Exception:
                pass

    # =====================================================================
    # Profile Management
    # =====================================================================
    def change_profile(self, profile_name):
        self.tracker.set_profile(profile_name)
        self.db.set_last_profile(profile_name)
        self.update_heatmap_colors()
        self.update_ui_stats()

    def create_profile_dialog(self):
        dialog = customtkinter.CTkInputDialog(text="Enter new profile name:", title="Add Profile")
        name = dialog.get_input()
        if name:
            name = name.strip()
            if self.db.create_profile(name):
                self.profile_combobox.configure(values=self.db.get_profiles())
                self.profile_combobox.set(name)
                self.change_profile(name)
            else:
                ToastNotification(self, "Profile name empty or already exists.", "error")

    def delete_active_profile(self):
        profile = self.tracker.active_profile
        if profile == "Default":
            ToastNotification(self, "Cannot delete the Default profile.", "error")
            return
            
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete profile '{profile}'? All statistics will be permanently lost."
        )
        if confirm:
            self.db.delete_profile(profile)
            profiles = self.db.get_profiles()
            self.profile_combobox.configure(values=profiles)
            self.profile_combobox.set("Default")
            self.change_profile("Default")
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
        """Callback to sync external hotkey triggers with UI controls."""
        self.incognito_var.set(value)
        self.toggle_incognito()

    def toggle_startup(self):
        utils.set_startup(self.startup_var.get())

    def change_heatmap_theme(self, theme):
        self.db.set_heatmap_theme(theme)
        if self.heatmap_var.get():
            self.heatmap_legend.draw_legend(theme)
            self.update_heatmap_colors()

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
            initialfile=f"typetrace_{self.tracker.active_profile.lower()}_stats.csv"
        )
        if filepath:
            aggregated = self.db.get_aggregated_stats(self.tracker.active_profile)
            if utils.export_stats_to_csv(filepath, aggregated):
                ToastNotification(self, f"CSV exported successfully!", "success")
            else:
                ToastNotification(self, "Export failed. Check permissions.", "error")

    def export_json(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Export Profile Statistics to JSON",
            initialfile=f"typetrace_{self.tracker.active_profile.lower()}_stats.json"
        )
        if filepath:
            try:
                aggregated = self.db.get_aggregated_stats(self.tracker.active_profile)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(aggregated, f, indent=4)
                ToastNotification(self, f"JSON exported successfully!", "success")
            except Exception as e:
                ToastNotification(self, f"Export failed: {e}", "error")

    def reset_statistics_dialog(self):
        confirm = messagebox.askyesno(
            "Reset Statistics", 
            f"Are you sure you want to clear statistics for profile '{self.tracker.active_profile}'?\n"
            "This action cannot be undone."
        )
        if confirm:
            self.db.reset_profile_statistics(self.tracker.active_profile)
            self.update_heatmap_colors()
            self.update_ui_stats()
            ToastNotification(self, f"Statistics for '{self.tracker.active_profile}' reset.", "success")

    # =====================================================================
    # Window Management
    # =====================================================================
    def withdraw_to_tray(self):
        """Hides UI main window, putting the application in system background/tray."""
        self.withdraw()

    def restore_from_tray(self):
        """Restores window from system tray thread-safely."""
        self.after(0, self.mostra_finestra)

    def mostra_finestra(self):
        """Brings the window back to the foreground."""
        self.deiconify()
        self.lift()
        self.focus_force()

    # =====================================================================
    # Thread-Safe Event Queue Processing
    # =====================================================================
    def process_event_queue(self, event_queue):
        """
        Periodically pulls events from the thread-safe queue on the main GUI thread.
        This prevents thread violations and segfaults from background threads.
        """
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
        """Processes a dequeued event safely on the main GUI thread."""
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
                self.profile_combobox.set(val)
                self.change_profile(val)
            elif event_type == "exit":
                if self.shutdown_callback:
                    self.shutdown_callback(val)
        except Exception as e:
            logging.exception(f"Error handling thread event '{event_type}': {e}")
