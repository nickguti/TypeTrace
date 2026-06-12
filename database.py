import os
import json
import threading
from datetime import datetime, timedelta

DEFAULT_DATA = {
    "settings": {
        "startup": False,
        "last_profile": "Default",
        "builtin_profiles": ["Total", "Desktop", "Gaming", "Default"],
        "recent_processes": []
    },
    "profiles": {
        "Default": {
            "hourly": {},
            "combinations": {},
            "bigrams": {},
            "burst_records": []
        },
        "Total": {
            "hourly": {},
            "combinations": {},
            "bigrams": {},
            "burst_records": []
        },
        "Desktop": {
            "hourly": {},
            "combinations": {},
            "bigrams": {},
            "burst_records": []
        },
        "Gaming": {
            "hourly": {},
            "combinations": {},
            "bigrams": {},
            "burst_records": []
        }
    }
}

class Database:
    def __init__(self, filepath="typetrace_data.json"):
        # Put the database file in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.filepath = os.path.join(script_dir, filepath)
        
        # Thread synchronization primitives (Reentrant Lock to prevent self-deadlocks on nested saves)
        self.lock = threading.RLock()
        
        self.data = {}
        self.load_data()
        
    def load_data(self):
        """Loads data from the JSON file or initializes default structure if file doesn't exist."""
        with self.lock:
            if not os.path.exists(self.filepath):
                self.data = json.loads(json.dumps(DEFAULT_DATA)) # Deep copy
                # Ensure built-in and hidden aggregate profiles exist
                self._ensure_builtin_profiles()
                self.save_data()
                return
                
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                    
                # Perform strict validation of structure types to prevent software crashes on load
                if not isinstance(self.data, dict):
                    raise ValueError("Database root is not a dictionary")
                    
                if "profiles" not in self.data or not isinstance(self.data["profiles"], dict):
                    self.data["profiles"] = {}
                    
                if "settings" not in self.data or not isinstance(self.data["settings"], dict):
                    self.data["settings"] = {}
                settings = self.data["settings"]
                settings.setdefault("startup", False)
                settings.setdefault("last_profile", "Default")
                settings.setdefault("heatmap_theme", "Classic")
                settings.setdefault("overlay_enabled", False)
                if "profile_mappings" not in settings or not isinstance(settings["profile_mappings"], dict):
                    settings["profile_mappings"] = {
                        "code.exe": "Coding",
                        "eclipse.exe": "Coding",
                        "cs2.exe": "Gaming",
                        "overwatch.exe": "Gaming"
                    }
                    
                if "Default" not in self.data["profiles"]:
                    self.data["profiles"]["Default"] = {"hourly": {}, "combinations": {}, "bigrams": {}, "burst_records": []}
                    
                self._ensure_builtin_profiles()
                
                if "recent_processes" not in self.data.get("settings", {}) or not isinstance(self.data["settings"]["recent_processes"], list):
                    self.data.setdefault("settings", {})["recent_processes"] = []
                    
                # Deep validate each profile to make sure sub-keys exist and are dictionaries/lists
                for p_name, p_data in list(self.data["profiles"].items()):
                    if not isinstance(p_data, dict):
                        self.data["profiles"][p_name] = {"hourly": {}, "combinations": {}, "bigrams": {}, "burst_records": []}
                        continue
                    if "hourly" not in p_data or not isinstance(p_data["hourly"], dict):
                        p_data["hourly"] = {}
                    if "combinations" not in p_data or not isinstance(p_data["combinations"], dict):
                        p_data["combinations"] = {}
                    if "bigrams" not in p_data or not isinstance(p_data["bigrams"], dict):
                        p_data["bigrams"] = {}
                    if "burst_records" not in p_data or not isinstance(p_data["burst_records"], list):
                        p_data["burst_records"] = []
                        
            except Exception as e:
                import logging
                logging.error(f"Database corruption or load error: {e}. Re-initializing database.")
                
                # Rename corrupted database to database_corrupted.json
                corrupted_filename = "database_corrupted.json"
                script_dir = os.path.dirname(os.path.abspath(__file__))
                corrupted_path = os.path.join(script_dir, corrupted_filename)
                
                if os.path.exists(self.filepath):
                    try:
                        if os.path.exists(corrupted_path):
                            os.remove(corrupted_path) # Remove old backup
                        os.rename(self.filepath, corrupted_path)
                        logging.info(f"Renamed corrupted database file to: {corrupted_path}")
                    except Exception as rename_err:
                        logging.error(f"Failed to rename corrupted file: {rename_err}")
                
                # Reset to default structure
                self.data = json.loads(json.dumps(DEFAULT_DATA))
                self._ensure_builtin_profiles()
                self.save_data()

    def _ensure_builtin_profiles(self):
        """Helper to ensure all built-in profiles exist and are correctly marked."""
        if "settings" not in self.data:
            self.data["settings"] = {}
        if "builtin_profiles" not in self.data["settings"] or not isinstance(self.data["settings"]["builtin_profiles"], list):
            self.data["settings"]["builtin_profiles"] = ["Total", "Desktop", "Gaming", "Default"]
            
        for p in ["Total", "Desktop", "Gaming", "Default"]:
            if p not in self.data["profiles"]:
                self.data["profiles"][p] = {"hourly": {}, "combinations": {}, "bigrams": {}, "burst_records": []}
            elif not isinstance(self.data["profiles"][p], dict):
                self.data["profiles"][p] = {"hourly": {}, "combinations": {}, "bigrams": {}, "burst_records": []}
        
        if "__all__" not in self.data["profiles"]:
            self.data["profiles"]["__all__"] = {"hourly": {}, "combinations": {}, "bigrams": {}, "burst_records": []}
        elif not isinstance(self.data["profiles"]["__all__"], dict):
            self.data["profiles"]["__all__"] = {"hourly": {}, "combinations": {}, "bigrams": {}, "burst_records": []}

    def save_data(self):
        """Saves current memory state to the local JSON database file."""
        with self.lock:
            try:
                with open(self.filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=4)
            except Exception as e:
                import logging
                logging.error(f"Error saving database: {e}")

    def get_profiles(self):
        """Returns list of profile names, with built-ins first and excluding the hidden internal __all__ profile."""
        with self.lock:
            builtins = ["Total", "Desktop", "Gaming", "Default"]
            all_keys = list(self.data.get("profiles", {}).keys())
            customs = [p for p in all_keys if p not in builtins and p != "__all__"]
            existing_builtins = [p for p in builtins if p in all_keys]
            return existing_builtins + customs

    def get_last_profile(self):
        """Returns the last active profile name."""
        with self.lock:
            return self.data.get("settings", {}).get("last_profile", "Default")

    def set_last_profile(self, name):
        """Sets the last active profile name."""
        with self.lock:
            if name in self.get_profiles():
                self.data.setdefault("settings", {})["last_profile"] = name
                self.save_data()

    def create_profile(self, name):
        """Creates a new profile if it doesn't exist."""
        with self.lock:
            if not name or name.strip() == "":
                return False
            name = name.strip()
            if name in self.data["profiles"]:
                return False
            
            self.data["profiles"][name] = {
                "hourly": {},
                "combinations": {},
                "bigrams": {}
            }
            self.save_data()
            return True

    def delete_profile(self, name):
        """Deletes a profile. Resets to Default if the active one is deleted."""
        with self.lock:
            if name in ("Total", "Desktop", "Gaming", "Default", "__all__"):
                return False
            if name not in self.data["profiles"]:
                return False
            
            del self.data["profiles"][name]
            if self.get_last_profile() == name:
                self.set_last_profile("Default")
            self.save_data()
            return True

    def reset_statistics(self):
        """Resets all data to the default empty template."""
        with self.lock:
            self.data = json.loads(json.dumps(DEFAULT_DATA))
            self._ensure_builtin_profiles()
            self.save_data()

    def reset_profile_statistics(self, profile_name):
        """Resets statistics only for the specified profile."""
        with self.lock:
            target = "__all__" if profile_name == "Total" else profile_name
            if target in self.data["profiles"]:
                self.data["profiles"][target] = {
                    "hourly": {},
                    "combinations": {},
                    "bigrams": {},
                    "burst_records": []
                }
                if profile_name in ("Total", "Desktop", "Gaming", "Default"):
                    self.data["profiles"][target]["is_builtin"] = True
                self.save_data()

    def get_stats_for_profile(self, profile_name):
        """Returns the stats profile dict."""
        with self.lock:
            return self.data["profiles"].get(profile_name, {"hourly": {}, "combinations": {}, "bigrams": {}, "burst_records": []})


    def get_profile_type(self, profile_name):
        """Returns the profile type: gaming, desktop, or custom."""
        with self.lock:
            name_lower = profile_name.lower()
            if name_lower == "gaming":
                return "gaming"
            elif name_lower == "desktop":
                return "desktop"
            else:
                profile = self.data["profiles"].get(profile_name, {})
                return profile.get("profile_type", "custom")

    def log_key(self, profile_name, key_name, combination=None, bigram_next=None, last_key=None):
        """Logs in memory the key press, combinations, and bigram transitions to the active profile and __all__."""
        with self.lock:
            self._log_key_to_profile(profile_name, key_name, combination, bigram_next, last_key)
            if profile_name != "__all__":
                self._log_key_to_profile("__all__", key_name, combination, bigram_next, last_key)

    def _log_key_to_profile(self, profile_name, key_name, combination=None, bigram_next=None, last_key=None):
        try:
            if profile_name not in self.data["profiles"]:
                self.create_profile(profile_name)
                
            profile = self.data["profiles"][profile_name]
            
            # Get hourly bucket key: YYYY-MM-DDTHH:00:00
            now = datetime.now()
            hour_key = now.strftime("%Y-%m-%dT%H:00:00")
            
            # Initialize hourly stats structures
            hourly = profile.setdefault("hourly", {})
            hour_data = hourly.setdefault(hour_key, {"keys": {}, "combinations": {}})
            if "keys" not in hour_data:
                hour_data["keys"] = {}
            if "combinations" not in hour_data:
                hour_data["combinations"] = {}
                
            # 1. Log the key press
            hour_data["keys"][key_name] = hour_data["keys"].get(key_name, 0) + 1
            
            # 2. Log combinations if present (e.g. Ctrl+C)
            if combination:
                hour_data["combinations"][combination] = hour_data["combinations"].get(combination, 0) + 1
                # Also log in the aggregated combinations structure for performance
                profile.setdefault("combinations", {})
                profile["combinations"][combination] = profile["combinations"].get(combination, 0) + 1
                
            # 3. Log bigram transitions
            if bigram_next:
                first_key = last_key if last_key else key_name
                bigrams = profile.setdefault("bigrams", {})
                k1_dict = bigrams.setdefault(first_key, {})
                k1_dict[bigram_next] = k1_dict.get(bigram_next, 0) + 1
        except Exception as e:
            import logging
            logging.exception(f"Error logging key '{key_name}' to profile '{profile_name}': {e}")

    def get_aggregated_stats(self, profile_name):
        """
        Returns fully aggregated key usage counts, combination counts, and bigram transition counts
        across all hour buckets for the specified profile.
        """
        with self.lock:
            read_from = "__all__" if profile_name == "Total" else profile_name
            profile = self.get_stats_for_profile(read_from)
            
            aggregated_keys = {}
            # Aggregate hourly key counts
            for hour_key, hour_data in profile.get("hourly", {}).items():
                for key, count in hour_data.get("keys", {}).items():
                    aggregated_keys[key] = aggregated_keys.get(key, 0) + count
                    
            # Combinations are already aggregated on the profile level
            aggregated_combos = profile.get("combinations", {})
            
            # Bigrams are already aggregated on the profile level
            aggregated_bigrams = profile.get("bigrams", {})
            
            return {
                "keys": aggregated_keys,
                "combinations": aggregated_combos,
                "bigrams": aggregated_bigrams
            }

    def get_key_stats(self, profile_name, key_name):
        """
        Calculates specific hover statistics for a key under the given profile:
        - Total count
        - Percentage of total typing
        - Average peak-hour frequency (presses/min)
        - Heat trend (last 24 hours vs overall average)
        - Most common next key (bigram)
        """
        with self.lock:
            read_from = "__all__" if profile_name == "Total" else profile_name
            profile = self.get_stats_for_profile(read_from)
            hourly = profile.get("hourly", {})
            
            # 1. Total count of this key and total keys overall
            total_key_presses = 0
            total_all_presses = 0
            
            # Track hourly data for this key
            hourly_counts = []
            
            for hour_key, hour_data in hourly.items():
                k_counts = hour_data.get("keys", {})
                total_all_presses += sum(k_counts.values())
                
                val = k_counts.get(key_name, 0)
                total_key_presses += val
                hourly_counts.append((hour_key, val))
                
            if total_key_presses == 0:
                return self._empty_stats()
                
            # 2. Percentage
            percentage = (total_key_presses / total_all_presses) * 100 if total_all_presses > 0 else 0.0
            
            # 3. Peak Hour Frequency (presses per minute in peak hour)
            max_hour_count = max([val for _, val in hourly_counts]) if hourly_counts else 0
            peak_ppm = max_hour_count / 60.0
            
            # 4. Heat Trend: Last 24 Hours vs Historical Average
            # Sum last 24 hours
            now = datetime.now()
            twenty_four_hours_ago = now - timedelta(hours=24)
            
            key_count_24h = 0
            active_hours_24h = 0
            
            # Calculate historical active hours (excluding or including, let's check all hours)
            total_recorded_hours = len(hourly)
            
            for hour_str, val in hourly_counts:
                try:
                    hour_dt = datetime.strptime(hour_str, "%Y-%m-%dT%H:00:00")
                    if hour_dt >= twenty_four_hours_ago:
                        key_count_24h += val
                        active_hours_24h += 1
                except ValueError:
                    pass
                    
            # Hourly averages
            avg_24h = key_count_24h / 24.0 # Average per hour in last 24h
            avg_hist = total_key_presses / max(1, total_recorded_hours) # Historical hourly average
            
            if total_recorded_hours < 2:
                heat_trend = "Stable (Insufficient data)"
            else:
                if avg_hist == 0:
                    heat_trend = "Stable"
                else:
                    pct_change = ((avg_24h - avg_hist) / avg_hist) * 100
                    if abs(pct_change) < 5:
                        heat_trend = "Stable"
                    elif pct_change > 0:
                        heat_trend = f"+{pct_change:.1f}% (Higher)"
                    else:
                        heat_trend = f"{pct_change:.1f}% (Lower)"
                        
            # 5. Bigram (Next key pressed most frequently after this one)
            bigrams_for_key = profile.get("bigrams", {}).get(key_name, {})
            next_key = "None"
            max_bigram_count = 0
            
            for n_key, count in bigrams_for_key.items():
                if count > max_bigram_count:
                    max_bigram_count = count
                    next_key = n_key
                    
            bigram_str = f"'{next_key}' ({max_bigram_count} times)" if max_bigram_count > 0 else "None"
            
            return {
                "total": total_key_presses,
                "percentage": f"{percentage:.2f}%",
                "peak_ppm": f"{peak_ppm:.2f} presses/min",
                "trend": heat_trend,
                "bigram": bigram_str
            }
            
    def _empty_stats(self):
        return {
            "total": 0,
            "percentage": "0.00%",
            "peak_ppm": "0.00 presses/min",
            "trend": "Stable (No usage yet)",
            "bigram": "None"
        }

    def get_heatmap_theme(self):
        with self.lock:
            return self.data.get("settings", {}).get("heatmap_theme", "Classic")

    def set_heatmap_theme(self, theme):
        with self.lock:
            self.data.setdefault("settings", {})["heatmap_theme"] = theme
            self.save_data()

    def get_profile_mappings(self):
        with self.lock:
            return self.data.get("settings", {}).get("profile_mappings", {})

    def set_profile_mappings(self, mappings):
        with self.lock:
            self.data.setdefault("settings", {})["profile_mappings"] = mappings
            self.save_data()

    def add_burst_record(self, profile_name, peak_apm, duration, is_internal=False):
        with self.lock:
            if not is_internal and profile_name != "__all__":
                self.add_burst_record("__all__", peak_apm, duration, is_internal=True)

            if profile_name in self.data["profiles"]:
                profile = self.data["profiles"][profile_name]
                bursts = profile.setdefault("burst_records", [])
                bursts.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "peak_apm": peak_apm,
                    "duration": round(duration, 2)
                })
                # Keep top 10 best records
                profile["burst_records"] = sorted(bursts, key=lambda x: x["peak_apm"], reverse=True)[:10]
                self.save_data()

    def get_burst_records(self, profile_name):
        with self.lock:
            read_from = "__all__" if profile_name == "Total" else profile_name
            profile = self.get_stats_for_profile(read_from)
            return profile.get("burst_records", [])

    def get_overlay_enabled(self):
        with self.lock:
            return self.data.get("settings", {}).get("overlay_enabled", False)

    def set_overlay_enabled(self, enabled):
        with self.lock:
            self.data.setdefault("settings", {})["overlay_enabled"] = enabled
            self.save_data()

    def get_builtin_profiles(self):
        """Returns the list of built-in profiles."""
        return ["Total", "Desktop", "Gaming", "Default"]

    def get_recent_processes(self, limit=10):
        """Reads from settings['recent_processes'] list of dicts. Returns sorted by last_seen descending."""
        with self.lock:
            recent_list = self.data.get("settings", {}).get("recent_processes", [])
            if not isinstance(recent_list, list):
                recent_list = []
            
            # Sort by last_seen descending
            sorted_list = sorted(
                recent_list,
                key=lambda x: x.get("last_seen", ""),
                reverse=True
            )
            return sorted_list[:limit]

    def log_process_seen(self, process_name, category):
        """Upserts process_name into settings['recent_processes']. Keep list max 50 and save."""
        with self.lock:
            settings = self.data.setdefault("settings", {})
            recent_list = settings.setdefault("recent_processes", [])
            if not isinstance(recent_list, list):
                recent_list = []
                settings["recent_processes"] = recent_list
                
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Look for existing entry
            found = False
            for entry in recent_list:
                if isinstance(entry, dict) and entry.get("process_name", "").lower() == process_name.lower():
                    entry["last_seen"] = now_str
                    entry["category"] = category
                    found = True
                    break
                    
            if not found:
                recent_list.append({
                    "process_name": process_name,
                    "category": category,
                    "last_seen": now_str
                })
                
            # Sort by last_seen descending
            recent_list.sort(key=lambda x: x.get("last_seen", ""), reverse=True)
            
            # Trim to max 50
            if len(recent_list) > 50:
                recent_list = recent_list[:50]
                settings["recent_processes"] = recent_list
                
            self.save_data()

