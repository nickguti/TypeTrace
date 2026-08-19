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

def _csv_safe(value):
    """Neutralizza le celle che un foglio di calcolo interpreterebbe come formule.

    Fra i nomi dei tasti ci sono "=", "-" e "+": aperti in Excel diventerebbero
    formule (ed e' una via nota per l'esecuzione di comandi).
    """
    text = str(value)
    if text[:1] in ("=", "+", "-", "@"):
        return "'" + text
    return text


def export_stats_to_csv(filepath, aggregated_data):
    """
    Exports keystrokes, combinations, bigrams, hourly history and burst records.
    aggregated_data format:
    {
        "keys": {"A": 50, "Space": 120, ...},
        "combinations": {"Ctrl+C": 5, ...},
        "bigrams": {"T": {"H": 12, ...}},
        "hourly": {"2026-08-17T09:00:00": {"keys": {...}}},   # facoltativo
        "burst_records": [{"timestamp": ..., "peak_apm": ...}] # facoltativo
    }
    """
    try:
        with open(filepath, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # --- Key Counts Section ---
            writer.writerow(["=== KEYSTROKE COUNTS ==="])
            writer.writerow(["Key", "Press Count"])
            # Sort by count descending
            sorted_keys = sorted(aggregated_data.get("keys", {}).items(), key=lambda x: x[1], reverse=True)
            for key, count in sorted_keys:
                writer.writerow([_csv_safe(key), count])
                
            writer.writerow([]) # Empty spacer line
            
            # --- Combinations Section ---
            writer.writerow(["=== KEYBOARD COMBINATIONS ==="])
            writer.writerow(["Combination", "Press Count"])
            sorted_combos = sorted(aggregated_data.get("combinations", {}).items(), key=lambda x: x[1], reverse=True)
            for combo, count in sorted_combos:
                writer.writerow([_csv_safe(combo), count])
                
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
                writer.writerow([_csv_safe(k1), _csv_safe(k2), count])

            # --- Cronologia oraria ---
            # Le caselle "includi cronologia" e "includi burst" del dialogo di
            # esportazione non avevano alcun effetto sul CSV: i dati arrivavano
            # fin qui e venivano scartati.
            hourly = aggregated_data.get("hourly")
            if hourly:
                writer.writerow([])
                writer.writerow(["=== HOURLY HISTORY ==="])
                writer.writerow(["Hour", "Key", "Press Count"])
                for hour_key in sorted(hourly.keys()):
                    keys = hourly[hour_key].get("keys", {}) if isinstance(hourly[hour_key], dict) else {}
                    for key, count in sorted(keys.items(), key=lambda x: x[1], reverse=True):
                        writer.writerow([hour_key, _csv_safe(key), count])

            # --- Record di velocita' ---
            bursts = aggregated_data.get("burst_records")
            if bursts:
                writer.writerow([])
                writer.writerow(["=== BURST RECORDS ==="])
                writer.writerow(["Timestamp", "Peak APM", "Duration (s)"])
                for record in bursts:
                    if isinstance(record, dict):
                        writer.writerow([record.get("timestamp", ""),
                                         record.get("peak_apm", 0),
                                         record.get("duration", 0)])

        return True
    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return False

def setup_first_run():
    """Preparazione al primo avvio.

    Crea soltanto il file di lancio accanto al codice, e solo quando si gira da
    sorgente. La creazione del collegamento sul Desktop non avviene piu' in
    automatico: scrivere sul Desktop dell'utente senza chiederglielo e' un
    effetto collaterale inatteso, e nell'eseguibile congelato il collegamento
    puntava comunque a un main.py inesistente. Ora e' create_desktop_shortcut(),
    che va invocata su richiesta esplicita.
    """
    if getattr(sys, "frozen", False):
        return True

    project_dir = os.path.dirname(os.path.abspath(__file__))
    bat_path = os.path.join(project_dir, "run_typetrace.bat")

    if os.path.exists(bat_path):
        return True

    # Si usa l'interprete corrente, non "pythonw" dal PATH: altrimenti in un
    # ambiente virtuale si finisce per lanciare l'interprete di sistema.
    pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw_exe):
        pythonw_exe = sys.executable

    bat_content = (
        "@echo off\n"
        'cd /d "%~dp0"\n'
        f'start "" "{pythonw_exe}" main.py\n'
        "exit\n"
    )
    try:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
        return True
    except Exception as e:
        print(f"Error creating batch script: {e}")
        return False


def create_desktop_shortcut():
    """Crea un collegamento a TypeTrace sul Desktop dell'utente.

    I percorsi vengono passati come argomenti separati e non interpolati nello
    script PowerShell: un apostrofo nel nome utente rompeva la sintassi (e in
    generale permetteva di iniettare comandi).
    """
    target = sys.executable if getattr(sys, "frozen", False) else \
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_typetrace.bat")
    working_dir = os.path.dirname(target)

    ps_script = (
        "param([string]$Target, [string]$WorkDir)\n"
        "$desktop = [Environment]::GetFolderPath('Desktop')\n"
        "$WshShell = New-Object -ComObject WScript.Shell\n"
        "$Shortcut = $WshShell.CreateShortcut((Join-Path $desktop 'TypeTrace.lnk'))\n"
        "$Shortcut.TargetPath = $Target\n"
        "$Shortcut.WorkingDirectory = $WorkDir\n"
        "$Shortcut.Save()\n"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script,
             "-Target", target, "-WorkDir", working_dir],
            capture_output=True, check=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return True
    except Exception as e:
        print(f"Error creating desktop shortcut: {e}")
        return False

def get_active_window_process_name(hwnd=None):
    """Nome dell'eseguibile della finestra in primo piano.

    Si usa QueryFullProcessImageNameW invece di GetModuleBaseNameW: la prima
    funziona con i diritti ridotti PROCESS_QUERY_LIMITED_INFORMATION, la
    seconda ne richiede di piu' (PROCESS_QUERY_INFORMATION | PROCESS_VM_READ)
    e falliva sempre in silenzio, restituendo None. Con essa non ha mai
    funzionato niente di quanto ci sta sopra: cambio automatico di profilo,
    mappature dei processi, elenco delle app recenti, banner "gaming mode".
    """
    try:
        if hwnd is None:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return None

        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return None

        # 0x1000 = PROCESS_QUERY_LIMITED_INFORMATION
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid.value)
        if not handle:
            return None

        try:
            size = ctypes.c_ulong(260)
            buf = ctypes.create_unicode_buffer(size.value)
            if ctypes.windll.kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
                name = os.path.basename(buf.value)
                if name:
                    return name

            # Ripiego per i sistemi piu' vecchi: richiede diritti maggiori
            handle2 = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, pid.value)
            if handle2:
                try:
                    buf2 = ctypes.create_unicode_buffer(260)
                    if ctypes.windll.psapi.GetModuleBaseNameW(handle2, 0, buf2, 260):
                        return buf2.value or None
                finally:
                    ctypes.windll.kernel32.CloseHandle(handle2)
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)

        return None
    except Exception:
        return None

# Applicazioni note. Vivono qui perche' li usano sia classify_process sia
# tracker.py: prima esistevano due copie divergenti e quella del tracker non
# veniva letta da nessuno.
KNOWN_GAMING_PROCESSES = {
    "steam.exe", "epicgameslauncher.exe", "leagueoflegends.exe", "valorant.exe",
    "csgo.exe", "cs2.exe", "minecraft.exe", "fortnite.exe", "robloxplayerbeta.exe",
    "r5apex.exe", "overwatch.exe", "destiny2.exe", "eldenring.exe", "cyberpunk2077.exe",
    "witcher3.exe", "gta5.exe", "rockstargameslauncher.exe", "battlenet.exe",
    "pathofexile.exe", "dota2.exe", "among_us.exe", "terraria.exe",
    "stardewvalley.exe", "re2.exe", "re3.exe", "re4.exe", "sekiro.exe",
    "fallout4.exe", "skyrim.exe", "skyrimse.exe", "newvegaslauncher.exe",
}

KNOWN_DESKTOP_PROCESSES = {
    "explorer.exe", "chrome.exe", "firefox.exe", "msedge.exe", "opera.exe",
    "brave.exe", "code.exe", "cursor.exe", "devenv.exe", "pycharm64.exe",
    "idea64.exe", "webstorm64.exe", "sublime_text.exe", "notepad.exe",
    "notepad++.exe", "wordpad.exe", "winword.exe", "excel.exe", "powerpnt.exe",
    "onenote.exe", "outlook.exe", "thunderbird.exe", "slack.exe", "discord.exe",
    "teams.exe", "zoom.exe", "telegram.exe", "whatsapp.exe", "signal.exe",
    "cmd.exe", "powershell.exe", "windowsterminal.exe", "wt.exe",
    "taskmgr.exe", "regedit.exe", "spotify.exe", "vlc.exe", "obs64.exe",
    "obsidian.exe", "notion.exe", "figma.exe", "xd.exe", "photoshop.exe",
    "illustrator.exe", "premiere.exe", "afterfx.exe", "acrobat.exe",
    "thunderbird.exe", "keepass.exe", "keepassxc.exe", "1password.exe",
    "bitwarden.exe", "zotero.exe", "libreoffice.exe", "soffice.exe",
}

# Game detection variables
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
_classify_cache = {}
CACHE_EXPIRY = 30

# Soglia di punteggio oltre la quale un processo e' considerato un gioco.
# Era 15, cioe' meno del solo indizio "usa una libreria grafica": qualunque
# applicazione accelerata via GPU e non presente nell'elenco desktop veniva
# classificata come gioco.
GAMING_SCORE_THRESHOLD = 45

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

def shutdown_executor():
    """Chiude il pool di thread usato per le scansioni dei processi."""
    try:
        _executor.shutdown(wait=False)
    except Exception:
        pass


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

        # Scorciatoie certe: non serve nessuna scansione
        if proc_lower in KNOWN_DESKTOP_PROCESSES:
            _classify_cache[proc_lower] = ("desktop", now)
            return "desktop"
        if proc_lower in KNOWN_GAMING_PROCESSES:
            _classify_cache[proc_lower] = ("gaming", now)
            return "gaming"

        score = 0

        # Submit psutil scan to background thread pool
        scan_timed_out = False
        future = _executor.submit(_scan_psutil_info, process_name)
        try:
            slow_info = future.result(timeout=0.5)
        except Exception:
            scan_timed_out = True
            slow_info = {
                "found": False,
                "exe_path": "",
                "parent_name": "",
                "dlls": []
            }
            
        # --- SEGNALE 1: librerie grafiche ---
        # Da sole non dicono quasi nulla: le carica ogni applicazione
        # accelerata, browser ed Electron compresi. Le API esclusive dei giochi
        # (Vulkan, Direct3D 12) pesano piu' di DXGI, che e' generica.
        strong_dlls = ['vulkan-1.dll', 'd3d12.dll', 'd3d9.dll']
        weak_dlls = ['d3d11.dll', 'opengl32.dll', 'dxgi.dll']
        dll_paths = slow_info.get("dlls", [])
        if any(any(dll in path for path in dll_paths) for dll in strong_dlls):
            score += 35
        elif any(any(dll in path for path in dll_paths) for dll in weak_dlls):
            score += 10
                
        # --- SEGNALE 2: finestra a schermo intero e senza bordi ---
        # Una sola lettura della finestra: prima i segnali 2 e 5 premiavano
        # entrambi l'assenza della barra del titolo, contando due volte la
        # stessa caratteristica fisica.
        try:
            import ctypes.wintypes
            user32 = ctypes.windll.user32
            target_hwnd = hwnd if hwnd is not None else user32.GetForegroundWindow()
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
                has_caption = bool(style & WS_CAPTION)

                if covers_screen and is_borderless:
                    score += 30
                elif covers_screen:
                    score += 15
                elif not has_caption:
                    score += 5
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
                
        # --- SEGNALE 6: applicazioni sicuramente non giochi ---
        if proc_lower in KNOWN_DESKTOP_PROCESSES:
            score -= 50

        # Classification
        result = "gaming" if score >= GAMING_SCORE_THRESHOLD else "desktop"

        # Un verdetto emesso senza i dati della scansione non va messo in cache:
        # altrimenti mezzo secondo di lentezza fissava per trenta secondi una
        # classificazione presa senza indizi.
        if not scan_timed_out:
            _classify_cache[proc_lower] = (result, now)
        return result
    except Exception:
        return "desktop"

