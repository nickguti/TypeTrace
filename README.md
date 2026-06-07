# 📊 TypeTrace — Premium Keyboard Analytics & Heatmap Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

**TypeTrace** is a modern, thread-safe, and dark-themed desktop application written in Python to track, analyze, and visualize your typing habits and gaming performance globally in real-time.

---

## ⌨️ Key Features

- **⌨️ 100% Full-Size ANSI Virtual Keyboard:** Real-time keypress tracking with a smooth "Glow Effect" animation. Supports multiple layouts (100% Full-Size, TKL, 75%, 65%, and 60%).
- **🔥 Dynamic Heatmap Visualization:** Multi-theme support (Classic, Cyberpunk, Matrix, Stealth) using advanced color interpolation based on global key frequency.
- **🧠 Advanced Analytics:** Error-rate analysis (Backspace Ratio), live and peak APM/WPM monitoring, bigram transition tracking, and background "Burst Mode" detection for performance spikes.
- **🔧 Smart Automation (Process Auto-Switch):** Seamlessly context-aware profiles (e.g., automatically switches between "Gaming" and "Coding" based on the active Windows process).
- **🛡️ Local Privacy & Incognito Mode:** 100% local JSON storage (zero data telemetries) and a global hotkey (`Ctrl+Shift+I`) to instantly pause tracking.
- **🎛️ Floating In-Game Overlay:** A compact, borderless, always-on-top draggable widget showing live APM counter.

---

## 🚀 Quick Start (For General Users)

Getting started with TypeTrace is simple and requires no setup:

1. Go to the **Releases** section on the right side of this repository.
2. Download the pre-compiled executable `TypeTrace.exe`.
3. Double-click `TypeTrace.exe` to run. No Python installation required!

---

## 🛠️ Installation & Setup (For Developers)

If you prefer to run the application from source or customize it, follow these steps:

### Prerequisites
- Python 3.9 or higher installed on your system.
- Windows Operating System (for process auto-switch API support).

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/typetrace/typetrace.git
   cd typetrace
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows (Command Prompt):
   venv\Scripts\activate
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install customtkinter pynput pystray Pillow
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

---

## 📐 Architecture

TypeTrace is designed with modularity, performance, and thread-safety in mind. Below is an overview of the core files that make up the project:

| File Name | Description |
| :--- | :--- |
| `[main.py](file:///C:/Users/nicolas/.gemini/antigravity/scratch/typetrace/main.py)` | The main entry point of the application. Manages high-level startup configuration, thread orchestration, tray icon integration, and the shutdown pipeline. |
| `[ui.py](file:///C:/Users/nicolas/.gemini/antigravity/scratch/typetrace/ui.py)` | Contains the CustomTkinter GUI layout. Implements the keyboard builder, layouts, statistics display, settings tabs, and the customizable dashboard. |
| `[tracker.py](file:///C:/Users/nicolas/.gemini/antigravity/scratch/typetrace/tracker.py)` | Handles keyboard hooks globally via `pynput`. Tracks keystrokes, monitors modifier keys, measures APM/WPM, and runs background burst-detection logic. |
| `[database.py](file:///C:/Users/nicolas/.gemini/antigravity/scratch/typetrace/database.py)` | Manages local storage persistence using thread-safe JSON. Encapsulates all profiling data and keystroke metrics under a strict `RLock` synchronization barrier. |
| `[utils.py](file:///C:/Users/nicolas/.gemini/antigravity/scratch/typetrace/utils.py)` | Houses helper utilities, such as color interpolation models, automated shortcut generators, telemetry exports, and Windows API wrappers. |
| `[overlay.py](file:///C:/Users/nicolas/.gemini/antigravity/scratch/typetrace/overlay.py)` | Manages the floating, transparent, always-on-top APM widget that overlays in-game screens. |

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
