import collections
import time
import logging
import threading
import ctypes
from pynput import keyboard

import keymap
import utils

# Nomi dei tasti che sono essi stessi un modificatore: premendoli da soli non
# si sta componendo nessuna scorciatoia.
MODIFIER_KEY_NAMES = {
    "Ctrl_L", "Ctrl_R", "Shift_L", "Shift_R",
    "Alt_L", "Alt_R", "Win_L", "Win_R",
}

# Virtual-key code dei modificatori, per risincronizzare lo stato con Windows
_VK_MODIFIERS = {
    "ctrl": (0x11,),          # VK_CONTROL
    "shift": (0x10,),         # VK_SHIFT
    "alt": (0x12,),           # VK_MENU
    "win": (0x5B, 0x5C),      # VK_LWIN, VK_RWIN
}

BUILTIN_GAMING_PROCESSES = {
    "steam.exe", "epicgameslauncher.exe", "leagueoflegends.exe", "valorant.exe",
    "csgo.exe", "cs2.exe", "minecraft.exe", "fortnite.exe", "robloxplayerbeta.exe",
    "r5apex.exe", "overwatch.exe", "destiny2.exe", "eldenring.exe", "cyberpunk2077.exe",
    "witcher3.exe", "gta5.exe", "rockstargameslauncher.exe", "battlenet.exe",
    "pathofexile.exe", "dota2.exe", "among_us.exe", "terraria.exe",
    "stardewvalley.exe", "re2.exe", "re3.exe", "re4.exe", "sekiro.exe",
    "fallout4.exe", "skyrim.exe", "skyrimse.exe", "newvegasLauncher.exe"
}

BUILTIN_DESKTOP_PROCESSES = {
    "chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "brave.exe",
    "code.exe", "cursor.exe", "pycharm64.exe", "idea64.exe", "webstorm64.exe",
    "sublime_text.exe", "notepad.exe", "notepad++.exe", "wordpad.exe",
    "winword.exe", "excel.exe", "powerpnt.exe", "onenote.exe",
    "outlook.exe", "thunderbird.exe", "slack.exe", "discord.exe", "teams.exe",
    "zoom.exe", "telegram.exe", "whatsapp.exe", "signal.exe",
    "explorer.exe", "cmd.exe", "powershell.exe", "windowsterminal.exe",
    "wt.exe", "obsidian.exe", "notion.exe", "figma.exe", "xd.exe",
    "photoshop.exe", "illustrator.exe", "premiere.exe", "afterfx.exe",
    "spotify.exe", "vlc.exe"
}

def get_active_window_title():
    """Fetches the window title of the foreground active window using ctypes."""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return ""
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ""
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""

def is_gaming_by_heuristic(process_name, title):
    """Secondary heuristic to identify gaming process based on non-productivity window title keywords."""
    if not title:
        return False
    title_lower = title.lower()
    productivity_keywords = [
        "code", "visual studio", "pycharm", "eclipse", "editor", "document", "spreadsheet", 
        "workbook", "presentation", "onenote", "outlook", "mail", "browser", "slack", 
        "discord", "teams", "zoom", "meet", "workspace", "folder", "explorer", "github", 
        "notion", "obsidian", "photoshop", "illustrator", "premiere", "figma", "pdf",
        "chrome", "firefox", "edge", "opera", "brave", "safari"
    ]
    return not any(kw in title_lower for kw in productivity_keywords)

class KeystrokeTracker:
    def __init__(self, db, ui_update_callback=None):
        self.db = db
        self.ui_update_callback = ui_update_callback
        
        # State variables
        self.active_profile = self.db.get_last_profile()
        self.incognito_mode = False
        self.last_detected_process = ""
        self.last_detected_category = "Unknown"
        
        # Modifier tracking
        self.pressed_modifiers = {
            "ctrl": False,
            "shift": False,
            "alt": False,
            "win": False
        }
        # AltGr su Windows equivale a Ctrl_L + Alt_R: va riconosciuto a parte,
        # altrimenti ogni carattere che lo richiede (@ # [ ] { }) verrebbe
        # archiviato come una scorciatoia Ctrl+Alt mai premuta.
        self.altgr_active = False
        self.pressed_keys = set()

        # L'utente puo' disattivare il cambio automatico di profilo
        self.auto_switch_enabled = True
        
        # Bigram tracking (last key pressed)
        self.last_key = None
        
        # APM/WPM tracking.
        # Una deque perche' viene riempita dal thread dell'hook e svuotata da
        # quello della UI: append e popleft sono atomici, mentre riassegnare
        # una lista faceva perdere le battute arrivate nel frattempo.
        self.keystroke_times = collections.deque()
        
        # pynput listener
        self.listener = None
        
        # Advanced statistics (Backspace Ratio tracking)
        self.session_total_clicks = 0
        self.session_backspace_clicks = 0
        
        # Session timer
        self.session_start_time = time.time()
        
        # Burst Mode Detection
        self.burst_active = False
        self.burst_start_time = None
        self.burst_peak_apm = 0
        
        # Smart Automation Thread
        self.automation_thread = None
        self.stop_automation = False

    def set_profile(self, profile_name):
        """Changes the active log profile."""
        self.active_profile = profile_name
        self.last_key = None

    def toggle_incognito(self):
        """Toggles the incognito status."""
        self.incognito_mode = not self.incognito_mode
        self.last_key = None
        if self.ui_update_callback:
            self.ui_update_callback("incognito", self.incognito_mode)
        return self.incognito_mode

    def map_key_to_name(self, key):
        """Translates pynput key events to standardized keyboard strings (Full 100% Keyboard)."""
        # 1. Check for Virtual Key Codes (VK) on Windows for Numpad keys
        if hasattr(key, 'vk') and key.vk is not None:
            vk = key.vk
            if 96 <= vk <= 105:
                return f"Kp_{vk - 96}"
            elif vk == 110:
                return "Kp_."
            elif vk == 111:
                return "Kp_/"
            elif vk == 106:
                return "Kp_*"
            elif vk == 109:
                return "Kp_-"
            elif vk == 107:
                return "Kp_+"
                
        # 2. Character keys
        if hasattr(key, 'char') and key.char is not None:
            c = key.char
            # Con Ctrl premuto il sistema produce un carattere di controllo
            # (Ctrl+S -> "\x13") e il tasto reale andrebbe perso: si risale dal
            # virtual-key code, che resta valido.
            if len(c) == 1 and ord(c) < 32:
                by_vk = keymap.key_for_vk(getattr(key, 'vk', None))
                if by_vk:
                    return by_vk
                return keymap.CTRL_CHAR_TO_KEY.get(c, c)
            if c == ' ':
                return 'Space'
            if c.isalpha():
                return c.upper()
            symbol_map = {
                ';': ';', '\'': '\'', ',': ',', '.': '.', '/': '/',
                '[': '[', ']': ']', '\\': '\\', '-': '-', '=': '=',
                '`': '`'
            }
            return symbol_map.get(c, c)
            
        # 3. Special keys mapping
        from pynput.keyboard import Key
        special_map = {
            Key.space: 'Space',
            Key.enter: 'Enter',
            Key.tab: 'Tab',
            Key.backspace: 'Backspace',
            Key.caps_lock: 'Caps',
            Key.shift: 'Shift_L',
            Key.shift_l: 'Shift_L',
            Key.shift_r: 'Shift_R',
            Key.ctrl: 'Ctrl_L',
            Key.ctrl_l: 'Ctrl_L',
            Key.ctrl_r: 'Ctrl_R',
            Key.alt: 'Alt_L',
            Key.alt_l: 'Alt_L',
            Key.alt_gr: 'Alt_R',
            Key.alt_r: 'Alt_R',
            Key.cmd: 'Win_L',
            Key.cmd_l: 'Win_L',
            Key.cmd_r: 'Win_R',
            Key.esc: 'Esc',
            Key.up: 'Up',
            Key.down: 'Down',
            Key.left: 'Left',
            Key.right: 'Right',
            Key.insert: 'Insert',
            Key.delete: 'Delete',
            Key.home: 'Home',
            Key.end: 'End',
            Key.page_up: 'Page_up',
            Key.page_down: 'Page_down',
            Key.print_screen: 'Print_screen',
            Key.scroll_lock: 'Scroll_lock',
            Key.pause: 'Pause',
            Key.num_lock: 'Num_lock',
            Key.f1: 'F1', Key.f2: 'F2', Key.f3: 'F3', Key.f4: 'F4',
            Key.f5: 'F5', Key.f6: 'F6', Key.f7: 'F7', Key.f8: 'F8',
            Key.f9: 'F9', Key.f10: 'F10', Key.f11: 'F11', Key.f12: 'F12'
        }
        
        if key in special_map:
            return special_map[key]

        # Ultima risorsa: pynput rappresenta i tasti che non sa nominare come
        # "<49>". Prima di archiviare quella stringa si prova con il vk.
        by_vk = keymap.key_for_vk(getattr(key, 'vk', None))
        if by_vk:
            return by_vk

        name = str(key).replace('Key.', '')
        return name.capitalize()

    def _sync_modifiers(self):
        """Riallinea lo stato dei modificatori a quello reale del sistema.

        Durante un Alt+Tab il focus passa a un'altra finestra mentre Alt e'
        ancora premuto e l'evento di rilascio puo' non arrivare mai all'hook:
        senza questo controllo il modificatore resta agganciato per sempre e
        ogni tasto successivo viene archiviato come combinazione "Alt+X".
        """
        try:
            get_state = ctypes.windll.user32.GetAsyncKeyState
        except Exception:
            return
        for name, vks in _VK_MODIFIERS.items():
            try:
                down = any(get_state(vk) & 0x8000 for vk in vks)
            except Exception:
                return
            if not down and self.pressed_modifiers.get(name):
                self.pressed_modifiers[name] = False
                if name == "alt":
                    self.altgr_active = False

    def reset_key_state(self):
        """Azzera i tasti considerati premuti (usato al cambio di finestra)."""
        self.pressed_keys.clear()
        for name in self.pressed_modifiers:
            self.pressed_modifiers[name] = False
        self.altgr_active = False
        self.last_key = None

    def on_press(self, key):
        """Callback invoked when a key is pressed."""
        try:
            # Prima di tutto si verifica che i modificatori ancora segnati come
            # premuti lo siano davvero: gli eventi di rilascio possono essersi
            # persi mentre il focus era su un'altra finestra.
            self._sync_modifiers()

            key_name = self.map_key_to_name(key)
            if key_name in self.pressed_keys:
                return
            self.pressed_keys.add(key_name)

            # 1. Update modifier states
            is_modifier = False
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self.pressed_modifiers["ctrl"] = True
                is_modifier = True
            elif key == keyboard.Key.alt_gr:
                # Windows sintetizza Ctrl_L subito prima di AltGr: quel Ctrl non
                # e' stato premuto dall'utente e va ritirato.
                self.altgr_active = True
                self.pressed_modifiers["ctrl"] = False
                self.pressed_modifiers["alt"] = False
                is_modifier = True
            elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                self.pressed_modifiers["shift"] = True
                is_modifier = True
            elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                self.pressed_modifiers["alt"] = True
                is_modifier = True
            elif key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
                self.pressed_modifiers["win"] = True
                is_modifier = True

            # 2. Check for Global Hotkeys
            # Ctrl + Shift + I to toggle Incognito Mode
            if self.pressed_modifiers["ctrl"] and self.pressed_modifiers["shift"] and key_name == 'I':
                self.toggle_incognito()
                return
                
            # Ctrl + Shift + O to toggle Floating Overlay
            if self.pressed_modifiers["ctrl"] and self.pressed_modifiers["shift"] and key_name == 'O':
                if self.ui_update_callback:
                    self.ui_update_callback("toggle_overlay", None)
                return
                
            # If in incognito, suppress tracking entirely
            if self.incognito_mode:
                return
                
            # 3. Add to APM calculation window
            self.keystroke_times.append(time.time())
            
            # Track session clicks and backspaces for ratio
            self.session_total_clicks += 1
            if key_name in ("Backspace", "Delete"):
                self.session_backspace_clicks += 1
            
            # 4. Check for active keyboard combinations
            combination = None
            active_mods = []
            if self.pressed_modifiers["ctrl"]: active_mods.append("Ctrl")
            if self.pressed_modifiers["alt"]: active_mods.append("Alt")
            if self.pressed_modifiers["win"]: active_mods.append("Win")
            if self.pressed_modifiers["shift"]: active_mods.append("Shift")

            # Only log combination if it includes modifiers (and not just shift by itself for typing capitals)
            non_shift_mods = any(self.pressed_modifiers[m] for m in ["ctrl", "alt", "win"])
            # Un modificatore premuto da solo non e' una scorciatoia: senza
            # questa guardia si archiviavano voci come "Ctrl+Ctrl_L".
            if non_shift_mods and active_mods and key_name not in MODIFIER_KEY_NAMES:
                combination = "+".join(active_mods) + "+" + key_name

            # 5. Log the keystroke
            # Ignore modifier keys and other special utility keys for bigram transitions
            ignore_bigrams = [
                'Shift_L', 'Shift_R', 'Ctrl_L', 'Ctrl_R', 'Alt_L', 'Alt_R', 'Win_L', 'Win_R', 'Esc', 'Caps'
            ]
            
            bigram_next = None
            current_last_key = self.last_key # Store the actual previous key before updating
            if key_name not in ignore_bigrams:
                if self.last_key and self.last_key not in ignore_bigrams:
                    bigram_next = key_name
                self.last_key = key_name
            else:
                self.last_key = None
                
            # Commit to database in-memory
            self.db.log_key(
                self.active_profile,
                key_name,
                combination=combination,
                bigram_next=bigram_next,
                last_key=current_last_key
            )
            
            # Trigger UI update if callback registered
            if self.ui_update_callback:
                self.ui_update_callback("keystroke", key_name)
        except Exception as e:
            logging.exception(f"Unhandled exception in on_press for key '{key}': {e}")

    def on_release(self, key):
        """Callback invoked when a key is released."""
        try:
            key_name = self.map_key_to_name(key)
            if key_name in self.pressed_keys:
                self.pressed_keys.remove(key_name)
                
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self.pressed_modifiers["ctrl"] = False
            elif key == keyboard.Key.alt_gr:
                self.altgr_active = False
                self.pressed_modifiers["alt"] = False
                self.pressed_modifiers["ctrl"] = False
            elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                self.pressed_modifiers["shift"] = False
            elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                self.pressed_modifiers["alt"] = False
            elif key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
                self.pressed_modifiers["win"] = False
        except Exception as e:
            logging.exception(f"Unhandled exception in on_release for key '{key}': {e}")

    def get_apm_wpm(self):
        """Calculates and returns the rolling APM and WPM (last 60 seconds)."""
        now = time.time()
        # Clean up events older than 60 seconds
        cutoff = now - 60
        try:
            while self.keystroke_times and self.keystroke_times[0] < cutoff:
                self.keystroke_times.popleft()
        except IndexError:
            pass

        apm = len(self.keystroke_times)
        wpm = int(apm / 5) # 5 strokes standard = 1 word
        return apm, wpm

    def get_session_duration(self):
        """Returns the current session duration as a formatted string (HH:MM:SS)."""
        elapsed = int(time.time() - self.session_start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def start(self):
        """Starts the global keyboard hook listener thread and the active window monitor thread."""
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.daemon = True
        self.listener.start()
        
        # Start background automation thread
        self.stop_automation = False
        self.automation_thread = threading.Thread(target=self.run_window_monitoring)
        self.automation_thread.daemon = True
        self.automation_thread.start()

    def stop(self):
        """Stops the global keyboard hook listener and window monitor thread."""
        if self.listener:
            self.listener.stop()
        self.stop_automation = True

        # Un burst ancora in corso alla chiusura andrebbe perso: se ha gia'
        # superato la soglia di durata lo si archivia adesso.
        if self.burst_active and self.burst_start_time:
            duration = time.time() - self.burst_start_time
            if duration >= 5.0:
                try:
                    self.db.add_burst_record(self.active_profile, self.burst_peak_apm, duration)
                except Exception as e:
                    logging.exception(f"Error saving in-progress burst on shutdown: {e}")
            self.burst_active = False

    def run_window_monitoring(self):
        """Background thread executing every 1s for Burst APM logging and Profile Auto-switching."""
        iteration = 0
        while not self.stop_automation:
            time.sleep(1)
            iteration += 1
            
            # 1. Burst Mode Check (every 1 second)
            try:
                apm, _ = self.get_apm_wpm()
                if apm >= 250:
                    if not self.burst_active:
                        self.burst_active = True
                        self.burst_start_time = time.time()
                        self.burst_peak_apm = apm
                    else:
                        self.burst_peak_apm = max(self.burst_peak_apm, apm)
                else:
                    if self.burst_active:
                        duration = time.time() - self.burst_start_time
                        if duration >= 5.0:
                            # Log record in database under the active profile
                            self.db.add_burst_record(self.active_profile, self.burst_peak_apm, duration)
                            if self.ui_update_callback:
                                self.ui_update_callback("burst_detected", (self.burst_peak_apm, duration))
                        self.burst_active = False
                        self.burst_start_time = None
                        self.burst_peak_apm = 0
            except Exception as e:
                logging.exception(f"Error in burst detection loop: {e}")
                
            # 2. Active Window Monitor Check (every 2 seconds)
            if iteration % 2 == 0:
                try:
                    proc_name = utils.get_active_window_process_name()
                    if proc_name and proc_name.lower() != self.last_detected_process.lower():
                        self.last_detected_process = proc_name
                        proc_lower = proc_name.lower()

                        # La finestra in primo piano e' cambiata: i tasti che
                        # risultavano premuti appartengono all'applicazione
                        # precedente e i loro rilasci potrebbero non arrivare.
                        self.reset_key_state()

                        # In incognito non si registra nemmeno quali applicazioni
                        # sono state usate.
                        if self.incognito_mode:
                            continue

                        # Priority 1: user's custom mappings
                        mappings = self.db.get_profile_mappings()
                        if proc_lower in mappings:
                            target_profile = mappings[proc_lower]
                        # Priority 2: auto-classify
                        else:
                            category = utils.classify_process(proc_name)
                            target_profile = "Gaming" if category == "gaming" else "Desktop"

                        # Log to recent processes
                        self.db.log_process_seen(proc_name, target_profile)

                        # Switch profile if changed
                        if (self.auto_switch_enabled
                                and target_profile in self.db.get_profiles()
                                and target_profile != self.active_profile):
                            self.set_profile(target_profile)
                            self.db.set_last_profile(target_profile)
                            if self.ui_update_callback:
                                self.ui_update_callback("profile_changed", target_profile)
                except Exception as e:
                    logging.exception(f"Error in active window monitoring loop: {e}")

