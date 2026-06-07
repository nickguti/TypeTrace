import time
import logging
import threading
from pynput import keyboard

import utils

class KeystrokeTracker:
    def __init__(self, db, ui_update_callback=None):
        self.db = db
        self.ui_update_callback = ui_update_callback
        
        # State variables
        self.active_profile = self.db.get_last_profile()
        self.incognito_mode = False
        
        # Modifier tracking
        self.pressed_modifiers = {
            "ctrl": False,
            "shift": False,
            "alt": False,
            "win": False
        }
        
        # Bigram tracking (last key pressed)
        self.last_key = None
        
        # APM/WPM tracking
        self.keystroke_times = []
        
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
            
        # Fallback
        name = str(key).replace('Key.', '')
        return name.capitalize()

    def on_press(self, key):
        """Callback invoked when a key is pressed."""
        try:
            # 1. Update modifier states
            is_modifier = False
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self.pressed_modifiers["ctrl"] = True
                is_modifier = True
            elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                self.pressed_modifiers["shift"] = True
                is_modifier = True
            elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
                self.pressed_modifiers["alt"] = True
                is_modifier = True
            elif key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
                self.pressed_modifiers["win"] = True
                is_modifier = True
                
            key_name = self.map_key_to_name(key)
            
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
            if non_shift_mods and active_mods:
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
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self.pressed_modifiers["ctrl"] = False
            elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                self.pressed_modifiers["shift"] = False
            elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
                self.pressed_modifiers["alt"] = False
            elif key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
                self.pressed_modifiers["win"] = False
        except Exception as e:
            logging.exception(f"Unhandled exception in on_release for key '{key}': {e}")

    def get_apm_wpm(self):
        """Calculates and returns the rolling APM and WPM (last 60 seconds)."""
        now = time.time()
        # Clean up events older than 60 seconds
        self.keystroke_times = [t for t in self.keystroke_times if t >= now - 60]
        
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
                    if proc_name:
                        proc_name_lower = proc_name.lower()
                        mappings = self.db.get_profile_mappings()
                        if proc_name_lower in mappings:
                            target_profile = mappings[proc_name_lower]
                            # Make sure target profile exists and is different
                            if target_profile in self.db.get_profiles() and target_profile != self.active_profile:
                                self.set_profile(target_profile)
                                self.db.set_last_profile(target_profile)
                                if self.ui_update_callback:
                                    self.ui_update_callback("profile_changed", target_profile)
                except Exception as e:
                    logging.exception(f"Error in active window monitoring loop: {e}")
