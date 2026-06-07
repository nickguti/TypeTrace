import os
import sys
import csv
import shutil
import subprocess
import ctypes
import time
import concurrent.futures

def interpolate_color(val, theme="Classic"):
    """
    Interpolates a color based on the selected Heatmap Theme:
    - Classic: Grey -> Blue -> Orange -> Red
    - Cyberpunk: Black -> Dark Purple -> Fuchsia -> Neon Cyan
    - Matrix: Black -> Dark Green -> Bright Green -> White/Green
    - Stealth: Dark Grey -> Anthracite -> White -> Silver
    """
    # Clamp val between 0.0 and 1.0
    val = max(0.0, min(1.0, float(val)))
    
    if theme == "Cyberpunk":
        points = [
            (0.0, (18, 18, 18)),
            (0.3, (80, 0, 100)),
            (0.7, (255, 0, 127)),
            (1.0, (0, 240, 255))
        ]
    elif theme == "Matrix":
        points = [
            (0.0, (18, 18, 18)),
            (0.3, (0, 70, 0)),
            (0.7, (0, 220, 0)),
            (1.0, (200, 255, 200))
        ]
    elif theme == "Stealth":
        points = [
            (0.0, (43, 43, 43)),
            (0.4, (70, 70, 70)),
            (0.8, (200, 200, 200)),
            (1.0, (230, 230, 230))
        ]
    else: # "Classic" or default
        points = [
            (0.0, (43, 43, 43)),
            (0.2, (0, 95, 115)),
            (0.5, (10, 147, 150)),
            (0.75, (202, 103, 2)),
            (1.0, (174, 32, 18))
        ]
    
    # Edge cases
    if val <= 0.0:
        return f"#{points[0][1][0]:02x}{points[0][1][1]:02x}{points[0][1][2]:02x}"
    if val >= 1.0:
        return f"#{points[-1][1][0]:02x}{points[-1][1][1]:02x}{points[-1][1][2]:02x}"
        
    for i in range(len(points) - 1):
        p1, c1 = points[i]
        p2, c2 = points[i+1]
        if p1 <= val <= p2:
            t = (val - p1) / (p2 - p1)
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            return f"#{r:02x}{g:02x}{b:02x}"
            
    return "#2b2b2b"

def get_startup_folder():
    """
    Returns the path to the Windows Startup folder.
    """
    appdata = os.environ.get("APPDATA")
    if appdata:
        return os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup")
    return None

def set_startup(enabled: bool):
    """
    Enables or disables launching the app on Windows boot by writing/removing
    a .bat shortcut to the Windows Startup directory.
    """
    startup_dir = get_startup_folder()
    if not startup_dir:
        return False
        
    bat_path = os.path.join(startup_dir, "typetrace_startup.bat")
    
    if enabled:
        # Get path of pythonw.exe (which runs python without a console window)
        python_exe = sys.executable
        pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
        if not os.path.exists(pythonw_exe):
            # Fallback if replace doesn't find it
            pythonw_exe = "pythonw.exe"
            
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
        
        # Batch script that executes main.py using pythonw
        content = f'@echo off\nstart "" "{pythonw_exe}" "{script_path}"\n'
        try:
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error enabling startup: {e}")
            return False
    else:
        if os.path.exists(bat_path):
            try:
                os.remove(bat_path)
                return True
            except Exception as e:
                print(f"Error disabling startup: {e}")
                return False
        return True

def is_startup_enabled():
    """
    Checks if the startup batch file exists in the Windows Startup directory.
    """
    startup_dir = get_startup_folder()
    if not startup_dir:
        return False
    bat_path = os.path.join(startup_dir, "typetrace_startup.bat")
    return os.path.exists(bat_path)

def export_stats_to_csv(filepath, aggregated_data):
    """
    Exports keystrokes, combinations, and bigrams statistics to a single CSV file with clean headers.
    aggregated_data format:
    {
        "keys": {"A": 50, "Space": 120, ...},
        "combinations": {"Ctrl+C": 5, ...},
        "bigrams": {"T": {"H": 12, ...}}
    }
    """
    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # --- Key Counts Section ---
            writer.writerow(["=== KEYSTROKE COUNTS ==="])
            writer.writerow(["Key", "Press Count"])
            # Sort by count descending
            sorted_keys = sorted(aggregated_data.get("keys", {}).items(), key=lambda x: x[1], reverse=True)
            for key, count in sorted_keys:
                writer.writerow([key, count])
                
            writer.writerow([]) # Empty spacer line
            
            # --- Combinations Section ---
            writer.writerow(["=== KEYBOARD COMBINATIONS ==="])
            writer.writerow(["Combination", "Press Count"])
            sorted_combos = sorted(aggregated_data.get("combinations", {}).items(), key=lambda x: x[1], reverse=True)
            for combo, count in sorted_combos:
                writer.writerow([combo, count])
                
            writer.writerow([]) # Empty spacer line
            
            # --- Bigrams Section ---
            writer.writerow(["=== MOST FREQUENT BIGRAMS (KEY TRANSITIONS) ==="])
            writer.writerow(["First Key", "Second Key", "Transition Count"])
            bigrams_list = []
            for k1, next_keys in aggregated_data.get("bigrams", {}).items():
                for k2, count in next_keys.items():
                    bigrams_list.append((k1, k2, count))
            # Sort by transitions count descending
            sorted_bigrams = sorted(bigrams_list, key=lambda x: x[2], reverse=True)
            for k1, k2, count in sorted_bigrams[:100]: # Limit to top 100 bigrams to keep it readable
                writer.writerow([k1, k2, count])
                
        return True
    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return False

def setup_first_run():
    """
    Automates configuration on the first launch:
    1. Creates 'run_typetrace.bat' in the project directory.
    2. Dynamically queries the Windows Desktop path and generates a 'TypeTrace.lnk' shortcut
       pointing to the .bat script, avoiding overwrites if either exists.
    """
    project_dir = os.path.dirname(os.path.abspath(__file__))
    bat_path = os.path.join(project_dir, "run_typetrace.bat")
    
    # 1. Create run_typetrace.bat if it doesn't exist
    if not os.path.exists(bat_path):
        bat_content = (
            "@echo off\n"
            'cd /d "%~dp0"\n'
            'start "" pythonw main.py\n'
            "exit\n"
        )
        try:
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat_content)
            print(f"Created script: {bat_path}")
        except Exception as e:
            print(f"Error creating batch script: {e}")
            return False

    # 2. Find Desktop and create TypeTrace.lnk if it doesn't exist
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "[Environment]::GetFolderPath('Desktop')"],
            capture_output=True, text=True, check=True
        )
        desktop_path = res.stdout.strip()
    except Exception:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
    shortcut_path = os.path.join(desktop_path, "TypeTrace.lnk")
    
    if not os.path.exists(shortcut_path):
        # We invoke PowerShell ComObject WScript.Shell to create the shortcut file (.lnk)
        # This resolves the exact Windows Desktop path dynamically even on OneDrive folders
        ps_script = f"""
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
        $Shortcut.TargetPath = '{bat_path}'
        $Shortcut.WorkingDirectory = '{project_dir}'
        $Shortcut.Save()
        """
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, check=True)
            print(f"Created desktop shortcut pointing to: {bat_path}")
        except Exception as e:
            print(f"Error creating desktop shortcut: {e}")
            return False
            
    return True

def get_active_window_process_name():
    """
    Directly queries Windows APIs using ctypes to find the active foreground process (.exe name).
    Requires no external python packages, ensuring zero overhead.
    """
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return None
            
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        # Open process for name retrieval (0x1000 = PROCESS_QUERY_LIMITED_INFORMATION)
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid.value)
        if not handle:
            return None
            
        # Retrieve base name using PSAPI
        buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.psapi.GetModuleBaseNameW(handle, 0, buf, ctypes.sizeof(buf) // 2)
        ctypes.windll.kernel32.CloseHandle(handle)
        
        name = buf.value
        return name if name else None
    except Exception:
        return None

# Game detection variables
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
_classify_cache = {}
CACHE_EXPIRY = 30

def _scan_psutil_info(process_name):
    """Slow scan using psutil to find target process details and memory mapped DLLs."""
    try:
        import psutil
        proc_lower = process_name.lower()
        
        for proc in psutil.process_iter(['name', 'pid', 'exe', 'ppid']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == proc_lower:
                    pid = proc.info['pid']
                    exe_path = proc.info.get('exe') or ""
                    ppid = proc.info.get('ppid')
                    
                    # Memory map query for loaded DLLs
                    dlls = []
                    try:
                        p = psutil.Process(pid)
                        dlls = [m.path.lower() for m in p.memory_maps()]
                    except Exception:
                        pass
                        
                    # Parent name retrieval
                    parent_name = ""
                    if ppid is not None:
                        try:
                            parent = psutil.Process(ppid)
                            parent_name = parent.name()
                        except Exception:
                            pass
                            
                    return {
                        "found": True,
                        "exe_path": exe_path,
                        "parent_name": parent_name,
                        "dlls": dlls
                    }
            except Exception:
                pass
    except Exception:
        pass
        
    return {
        "found": False,
        "exe_path": "",
        "parent_name": "",
        "dlls": []
    }

def classify_process(process_name, hwnd=None) -> str:
    """
    Returns "gaming" or "desktop".
    Uses multiple heuristics combined into a confidence score.
    """
    try:
        proc_lower = process_name.lower()
        now = time.time()
        
        # 1. Check cache first
        if proc_lower in _classify_cache:
            cached_result, cached_time = _classify_cache[proc_lower]
            if now - cached_time < CACHE_EXPIRY:
                return cached_result
                
        score = 0
        
        # Submit psutil scan to background thread pool
        future = _executor.submit(_scan_psutil_info, process_name)
        try:
            slow_info = future.result(timeout=0.5)
        except Exception:
            slow_info = {
                "found": False,
                "exe_path": "",
                "parent_name": "",
                "dlls": []
            }
            
        # --- SIGNAL 1: Graphics API detection (+40 pts) ---
        game_dlls = ['d3d9.dll', 'd3d11.dll', 'd3d12.dll', 'opengl32.dll', 'vulkan-1.dll', 'dxgi.dll']
        for dll in game_dlls:
            if any(dll in path for path in slow_info.get("dlls", [])):
                score += 40
                break
                
        # --- SIGNAL 2: Fullscreen/Borderless window detection (+25 pts / +10 pts) ---
        try:
            import ctypes
            import ctypes.wintypes
            user32 = ctypes.windll.user32
            target_hwnd = hwnd
            if target_hwnd is None:
                target_hwnd = user32.GetForegroundWindow()
            if target_hwnd:
                rect = ctypes.wintypes.RECT()
                user32.GetWindowRect(target_hwnd, ctypes.byref(rect))
                screen_w = user32.GetSystemMetrics(0)
                screen_h = user32.GetSystemMetrics(1)
                win_w = rect.right - rect.left
                win_h = rect.bottom - rect.top
                covers_screen = (win_w >= screen_w * 0.95 and win_h >= screen_h * 0.95)

                GWL_STYLE = -16
                WS_POPUP = 0x80000000
                WS_CAPTION = 0x00C00000
                style = user32.GetWindowLongW(target_hwnd, GWL_STYLE)
                is_borderless = bool(style & WS_POPUP) and not bool(style & WS_CAPTION)

                if covers_screen and is_borderless:
                    score += 25
                elif covers_screen:
                    score += 10
        except Exception:
            pass
            
        # --- SIGNAL 3: Known game launcher / platform processes (+20 pts) ---
        gaming_platforms = [
            "steam.exe", "epicgameslauncher.exe", "gog.exe", "gogalaxy.exe",
            "battlenet.exe", "riotclientservices.exe", "eadesktop.exe",
            "ubisoftconnect.exe", "xboxapp.exe", "gamingservices.exe"
        ]
        if proc_lower in gaming_platforms:
            score += 20
            
        parent_name = slow_info.get("parent_name", "").lower()
        if parent_name in gaming_platforms:
            score += 20
            
        # --- SIGNAL 4: Process install path heuristics (+15 pts) ---
        exe_path = slow_info.get("exe_path", "").lower()
        if exe_path:
            exe_path_normalized = exe_path.replace('\\', '/')
            gaming_paths = [
                'steamapps', 'epic games', 'gog games', 'ea games', 'riot games',
                'ubisoft game launcher', 'battle.net', 'xbox games', '/games/'
            ]
            if any(p in exe_path_normalized for p in gaming_paths):
                score += 15
                
        # --- SIGNAL 5: No standard window chrome (+10 pts) ---
        try:
            import ctypes
            user32 = ctypes.windll.user32
            target_hwnd = hwnd
            if target_hwnd is None:
                target_hwnd = user32.GetForegroundWindow()
            if target_hwnd:
                GWL_STYLE = -16
                WS_CAPTION = 0x00C00000
                style = user32.GetWindowLongW(target_hwnd, GWL_STYLE)
                has_caption = bool(style & WS_CAPTION)
                if not has_caption:
                    score += 10
        except Exception:
            pass
            
        # --- SIGNAL 6: Known non-game processes (-50 pts) ---
        definite_desktop = [
            "explorer.exe", "chrome.exe", "firefox.exe", "msedge.exe", "opera.exe",
            "brave.exe", "code.exe", "cursor.exe", "devenv.exe", "pycharm64.exe",
            "idea64.exe", "webstorm64.exe", "sublime_text.exe", "notepad.exe",
            "notepad++.exe", "winword.exe", "excel.exe", "powerpnt.exe", "outlook.exe",
            "slack.exe", "discord.exe", "teams.exe", "zoom.exe", "telegram.exe",
            "cmd.exe", "powershell.exe", "windowsterminal.exe", "wt.exe",
            "taskmgr.exe", "regedit.exe", "spotify.exe", "vlc.exe", "obs64.exe"
        ]
        if proc_lower in definite_desktop:
            score -= 50
            
        # Classification
        if score >= 15:
            result = "gaming"
        else:
            result = "desktop"
            
        # Cache results
        _classify_cache[proc_lower] = (result, now)
        return result
    except Exception:
        return "desktop"

