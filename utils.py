import os
import sys
import csv
import shutil
import subprocess
import ctypes

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

