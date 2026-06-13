<div align="center">
  <img src="assets/screenshot.png" alt="TypeTrace Logo/Screenshot" width="100%">

  # 📊 TypeTrace

  **Premium Keyboard Analytics & Heatmap Dashboard**

  [![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
  [![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
  [![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
  [![Downloads](https://img.shields.io/github/downloads/nickguti/TypeTrace/total?color=brightgreen)](https://github.com/nickguti/TypeTrace/releases/latest)
  [![Latest Release](https://img.shields.io/github/v/release/nickguti/TypeTrace)](https://github.com/nickguti/TypeTrace/releases/latest)
  
  [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/nickguti)

  <p align="center">
    TypeTrace is a modern, thread-safe, and dark-themed desktop application written in Python and PyQt6 to track, analyze, and visualize your typing habits and gaming performance globally in real-time.
  </p>
</div>

---

<div align="center">
  <img src="assets/demo.gif" alt="TypeTrace Demo" width="800">
</div>

## ⌨️ Key Features

- **⌨️ 100% Full-Size ANSI Virtual Keyboard:** Real-time keypress tracking with a smooth "Glow Effect" animation. Supports multiple layouts (100% Full-Size, TKL, 75%, 65%, and 60%).
- **🔥 Dynamic Heatmap Visualization:** Multi-theme support (Neon Cyberpunk, Pudding Keycaps, Mechanical) using advanced color interpolation based on global key frequency.
- **🧠 Advanced Analytics:** Error-rate analysis, live and peak APM/WPM monitoring, bigram transition tracking, and "Burst Mode" detection.
- **🔧 Smart Automation (Process Auto-Switch):** Context-aware profiles (e.g., automatically switches between "Gaming" and "Desktop" based on the active Windows process).
- **🛡️ Local Privacy & Incognito Mode:** 100% local JSON storage (zero data telemetries) and a global hotkey (`Ctrl+Shift+I`) to instantly pause tracking.
- **🎛️ Floating In-Game Overlay:** A compact, borderless, always-on-top draggable widget showing live APM counter.

---

## 🚀 Quick Start (For General Users)

👉 [**Download TypeTrace.exe**](https://github.com/nickguti/TypeTrace/releases/latest)

Getting started with TypeTrace is simple and requires no setup:

1. Go to the **Releases** section on the right side of this repository.
2. Download the pre-compiled executable `TypeTrace.exe`.
3. Double-click `TypeTrace.exe` to run. **No Python installation required!**

---

## 🛠️ Installation & Setup (For Developers)

If you prefer to run the application from source or customize it, follow these steps:

### Prerequisites
- Python 3.9 or higher installed on your system.
- Windows Operating System (for process auto-switch API support).

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nickguti/typetrace.git
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
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

---

## ☕ Support the Project

If you find TypeTrace useful for your daily work or gaming sessions, consider supporting the development!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/nickguti)

---

## 🗺️ Roadmap

- [ ] Linux & macOS support
- [ ] Weekly PDF report export
- [ ] Multi-language UI (EN / IT / ES)
- [ ] More heatmap themes
- [ ] Web dashboard (optional companion)
- [ ] Plugin system for custom analytics

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
