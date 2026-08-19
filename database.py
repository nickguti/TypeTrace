import copy
import logging
import os
import json
import threading
from datetime import datetime, timedelta

import paths

# Intervallo minimo fra due scritture su disco. Il file viene riscritto per
# intero (circa 100 ms su un database di un anno) e la scrittura avviene
# tenendo il lock che serve anche all'hook della tastiera: salvare a ogni
# evento rischiava di superare il LowLevelHooksTimeout di Windows, che rimuove
# silenziosamente gli hook troppo lenti.
AUTOSAVE_INTERVAL_SECONDS = 20

# Per quanti giorni si conserva il dettaglio ora per ora. Oltre questa soglia i
# bucket vengono fusi in uno per giorno: l'ora esatta non serve piu' a nessuna
# schermata, mentre i totali per tasto restano identici.
HOURLY_RETENTION_DAYS = 180

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
    def __init__(self, filepath="typetrace_data.json", directory=None):
        if directory is not None:
            # Usato dai test, che lavorano su una cartella temporanea
            self.filepath = os.path.join(directory, filepath)
        elif os.path.isabs(filepath):
            self.filepath = filepath
        else:
            # I dati vanno in %APPDATA%: sotto PyInstaller la cartella del
            # modulo e' temporanea e verrebbe cancellata all'uscita.
            self.filepath = paths.migrate_legacy_file(filepath)

        # Thread synchronization primitives (Reentrant Lock to prevent self-deadlocks on nested saves)
        self.lock = threading.RLock()

        # Salvataggio differito: le modifiche segnano il database come "sporco"
        # e un thread dedicato le scrive al massimo ogni AUTOSAVE_INTERVAL_SECONDS.
        self._dirty = False
        self._stop_autosave = threading.Event()
        self._autosave_thread = None

        # Conteggi aggregati tenuti in memoria e aggiornati a ogni battuta.
        # Prima ogni richiesta ripercorreva tutti i bucket orari: con 205 bucket
        # erano 1,1 ms, ma la scansione cresce in modo lineare con lo storico e
        # l'interfaccia la invocava a ogni tasto premuto.
        self._agg_cache = {}

        self.data = {}
        self.load_data()

    # ------------------------------------------------------------------
    # Salvataggio differito
    # ------------------------------------------------------------------

    def mark_dirty(self):
        """Segnala che ci sono modifiche da scrivere, senza toccare il disco."""
        self._dirty = True

    def start_autosave(self):
        """Avvia il thread che scrive periodicamente le modifiche in sospeso."""
        if self._autosave_thread is not None:
            return
        self._stop_autosave.clear()
        self._autosave_thread = threading.Thread(target=self._autosave_loop, daemon=True)
        self._autosave_thread.start()

    def stop_autosave(self):
        """Ferma il thread di salvataggio e scrive un'ultima volta."""
        self._stop_autosave.set()
        if self._autosave_thread is not None:
            self._autosave_thread.join(timeout=2.0)
            self._autosave_thread = None
        if self._dirty:
            self.save_data()

    def _autosave_loop(self):
        while not self._stop_autosave.wait(AUTOSAVE_INTERVAL_SECONDS):
            if self._dirty:
                try:
                    self.save_data()
                except Exception as e:
                    logging.error(f"Autosave failed: {e}")

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
                    # I profili indicati devono esistere: il tracker ignora in
                    # silenzio le mappature verso profili inesistenti.
                    settings["profile_mappings"] = {
                        "code.exe": "Desktop",
                        "eclipse.exe": "Desktop",
                        "cs2.exe": "Gaming",
                        "overwatch.exe": "Gaming"
                    }
                    
                if "Default" not in self.data["profiles"]:
                    self.data["profiles"]["Default"] = {"hourly": {}, "combinations": {}, "bigrams": {}, "burst_records": []}
                    
                self._ensure_builtin_profiles()

                # Recupero dello storico raccolto dalle versioni precedenti
                if self._migrate_key_names():
                    self.mark_dirty()

                # Storico vecchio: si tiene il totale, si perde solo l'ora esatta
                self.compact_history()

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
                corrupted_path = os.path.join(os.path.dirname(self.filepath), corrupted_filename)
                
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

    SCHEMA_VERSION = 2

    def _migrate_key_names(self):
        """Ripara una volta sola i nomi dei tasti raccolti dalle versioni precedenti.

        Fino alla 3.1.5 un tasto premuto insieme a Ctrl veniva archiviato come
        il carattere di controllo prodotto dal sistema ("\\x13" invece di "S"),
        e i tasti che pynput non sapeva nominare come "<65>". La corrispondenza
        e' deterministica, quindi lo storico si recupera. Nella stessa passata
        si eliminano le combinazioni composte dal solo modificatore
        ("Ctrl+Ctrl_L"), che non corrispondono a nessuna scorciatoia reale.
        """
        settings = self.data.setdefault("settings", {})
        if settings.get("schema_version", 1) >= self.SCHEMA_VERSION:
            return 0

        import keymap

        repaired = 0

        def fix(name):
            nonlocal repaired
            new_name = keymap.repair_key_name(name)
            if new_name != name:
                repaired += 1
            return new_name

        def merge(target, key, value):
            target[key] = target.get(key, 0) + value

        for profile in self.data.get("profiles", {}).values():
            if not isinstance(profile, dict):
                continue

            for hour_data in profile.get("hourly", {}).values():
                keys = hour_data.get("keys")
                if isinstance(keys, dict):
                    rebuilt = {}
                    for name, count in keys.items():
                        merge(rebuilt, fix(name), count)
                    hour_data["keys"] = rebuilt

            combos = profile.get("combinations")
            if isinstance(combos, dict):
                rebuilt = {}
                for combo, count in combos.items():
                    parts = combo.split("+")
                    if len(parts) < 2:
                        continue
                    last = fix(parts[-1])
                    mods = parts[:-1]
                    # "Ctrl+Ctrl_L" e simili: il tasto e' il modificatore stesso
                    if last.rstrip("_LR") in ("Ctrl", "Alt", "Shift", "Win"):
                        repaired += 1
                        continue
                    merge(rebuilt, "+".join(mods + [last]), count)
                profile["combinations"] = rebuilt

            bigrams = profile.get("bigrams")
            if isinstance(bigrams, dict):
                rebuilt = {}
                for first, nexts in bigrams.items():
                    if not isinstance(nexts, dict):
                        continue
                    target = rebuilt.setdefault(fix(first), {})
                    for second, count in nexts.items():
                        merge(target, fix(second), count)
                profile["bigrams"] = rebuilt

        settings["schema_version"] = self.SCHEMA_VERSION
        self._invalidate_aggregates()
        if repaired:
            logging.info(f"Migrated {repaired} legacy key names")
        return repaired

    def compact_history(self, retention_days=HOURLY_RETENTION_DAYS):
        """Fonde i bucket orari piu' vecchi in un bucket per giorno.

        Ogni ora di attivita' e' un dizionario di conteggi: dopo un anno sono
        migliaia di voci e il file cresce senza limite. Oltre la finestra di
        conservazione l'ora esatta non serve piu' a nessuna schermata, mentre i
        totali per tasto restano intatti. Le chiavi compattate hanno la forma
        "YYYY-MM-DD", senza la "T": chi analizza l'ora del giorno le ignora da
        se', chi somma i totali le include normalmente.

        Restituisce il numero di bucket fusi.
        """
        with self.lock:
            cutoff = (datetime.now() - timedelta(days=retention_days)).strftime("%Y-%m-%dT%H:00:00")
            merged = 0

            for profile in self.data.get("profiles", {}).values():
                if not isinstance(profile, dict):
                    continue
                hourly = profile.get("hourly")
                if not isinstance(hourly, dict):
                    continue

                rebuilt = {}
                for hour_key, hour_data in hourly.items():
                    if "T" in hour_key and hour_key < cutoff:
                        day_key = hour_key.split("T")[0]
                        target = rebuilt.setdefault(day_key, {"keys": {}})
                        for key, count in hour_data.get("keys", {}).items():
                            target["keys"][key] = target["keys"].get(key, 0) + count
                        merged += 1
                    else:
                        rebuilt[hour_key] = hour_data
                profile["hourly"] = rebuilt

            if merged:
                self._invalidate_aggregates()
                self.mark_dirty()
                logging.info(f"Compacted {merged} hourly buckets")
            return merged

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
        """Scrive lo stato in memoria sul file JSON, in modo atomico.

        La serializzazione avviene tenendo il lock, la scrittura no: cosi' il
        thread della tastiera non resta bloccato per tutta la durata dell'I/O.
        Si scrive su un file temporaneo e lo si sposta con os.replace, che e'
        atomico: un'interruzione a meta' non puo' piu' troncare il database.
        """
        with self.lock:
            try:
                payload = json.dumps(self.data, indent=4)
            except Exception as e:
                logging.error(f"Error serializing database: {e}")
                return
            self._dirty = False

        tmp_path = self.filepath + ".tmp"
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())

            # Copia di sicurezza della versione precedente
            if os.path.exists(self.filepath):
                backup = self.filepath + ".bak"
                try:
                    os.replace(self.filepath, backup)
                except Exception:
                    pass

            os.replace(tmp_path, self.filepath)
        except Exception as e:
            logging.error(f"Error saving database: {e}")
            self._dirty = True
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

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
            
            # burst_records incluso: ogni altro punto del codice lo assume
            self.data["profiles"][name] = self._empty_profile()
            self._invalidate_aggregates(name)
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
            self._invalidate_aggregates(name)
            if self.get_last_profile() == name:
                self.set_last_profile("Default")
            self.save_data()
            return True

    def reset_statistics(self):
        """Azzera tutte le statistiche conservando le impostazioni.

        Prima veniva riassegnato DEFAULT_DATA per intero, cancellando anche
        mappature dei processi, tema della heatmap, avvio automatico e stato
        dell'overlay: cose che l'utente non si aspetta di perdere premendo
        "azzera statistiche".
        """
        with self.lock:
            settings = self.data.get("settings", {})
            self.data = json.loads(json.dumps(DEFAULT_DATA))
            if isinstance(settings, dict):
                self.data["settings"] = settings
            self._ensure_builtin_profiles()
            self._invalidate_aggregates()
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
                # L'aggregato "__all__" contiene ancora i dati appena azzerati:
                # senza questo passaggio il reset sembrava non aver fatto nulla
                # perche' la vista predefinita e' proprio quella aggregata.
                self._rebuild_all()
                self._invalidate_aggregates()
                self.save_data()

    def _rebuild_all(self):
        """Ricostruisce il profilo aggregato "__all__" dai profili reali."""
        aggregate = self._empty_profile()
        for name, profile in self.data.get("profiles", {}).items():
            if name in ("__all__", "Total") or not isinstance(profile, dict):
                continue
            for hour_key, hour_data in profile.get("hourly", {}).items():
                bucket = aggregate["hourly"].setdefault(hour_key, {"keys": {}})
                for key, count in hour_data.get("keys", {}).items():
                    bucket["keys"][key] = bucket["keys"].get(key, 0) + count
            for combo, count in profile.get("combinations", {}).items():
                aggregate["combinations"][combo] = aggregate["combinations"].get(combo, 0) + count
            for first, nexts in profile.get("bigrams", {}).items():
                target = aggregate["bigrams"].setdefault(first, {})
                for second, count in nexts.items():
                    target[second] = target.get(second, 0) + count
            aggregate["burst_records"].extend(profile.get("burst_records", []))
        aggregate["burst_records"] = sorted(
            aggregate["burst_records"], key=lambda x: x.get("peak_apm", 0), reverse=True
        )[:10]
        self.data["profiles"]["__all__"] = aggregate

    def _empty_profile(self):
        return {"hourly": {}, "combinations": {}, "bigrams": {}, "burst_records": []}

    def _resolve_profile_name(self, profile_name):
        """"Total" e' una vista sul profilo interno "__all__"."""
        return "__all__" if profile_name == "Total" else profile_name

    def _cached_key_counts(self, profile_name, profile=None):
        """Conteggi per tasto del profilo, calcolati una volta sola.

        La prima richiesta percorre lo storico; da li' in avanti il totale
        viene aggiornato battuta per battuta da _log_key_to_profile.
        """
        resolved = self._resolve_profile_name(profile_name)
        cached = self._agg_cache.get(resolved)
        if cached is not None:
            return cached

        if profile is None:
            profile = self._profile_ref(profile_name)
        counts = {}
        for hour_data in profile.get("hourly", {}).values():
            for key, count in hour_data.get("keys", {}).items():
                counts[key] = counts.get(key, 0) + count
        self._agg_cache[resolved] = counts
        return counts

    def _invalidate_aggregates(self, profile_name=None):
        """Scarta i totali in memoria dopo una modifica non incrementale."""
        if profile_name is None:
            self._agg_cache.clear()
        else:
            self._agg_cache.pop(self._resolve_profile_name(profile_name), None)
            self._agg_cache.pop("__all__", None)

    def _profile_ref(self, profile_name):
        """Riferimento interno al profilo, senza copia. Solo per uso interno.

        "Total" e' una vista: i dati stanno nel profilo interno "__all__".
        """
        read_from = "__all__" if profile_name == "Total" else profile_name
        return self.data["profiles"].get(read_from, self._empty_profile())

    def get_stats_for_profile(self, profile_name):
        """Istantanea dei dati di un profilo.

        Traduce "Total" in "__all__" come gli altri accessori: senza questa
        traduzione i chiamanti ricevevano il profilo "Total" letterale, che non
        scrive nessuno, e vedevano cronologia e record sempre vuoti.

        Restituisce una copia: il chiamante la itera nel thread della UI mentre
        quello della tastiera continua ad aggiungere chiavi.
        """
        with self.lock:
            return copy.deepcopy(self._profile_ref(profile_name))


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
            self.mark_dirty()

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

            # Il totale in memoria si aggiorna qui, cosi' l'interfaccia non
            # deve piu' ripercorrere lo storico a ogni tasto premuto.
            cached = self._agg_cache.get(profile_name)
            if cached is not None:
                cached[key_name] = cached.get(key_name, 0) + 1
            
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
            profile = self._profile_ref(profile_name)

            aggregated_keys = dict(self._cached_key_counts(profile_name, profile))

            # Combinations are already aggregated on the profile level
            aggregated_combos = dict(profile.get("combinations", {}))

            # Bigrams are already aggregated on the profile level
            aggregated_bigrams = {k: dict(v) for k, v in profile.get("bigrams", {}).items()}

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
            profile = self._profile_ref(profile_name)
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
            
    # ------------------------------------------------------------------
    # Statistiche derivate
    # ------------------------------------------------------------------

    def get_daily_totals(self, profile_name, days=None):
        """Battute per giorno, dalla piu' vecchia alla piu' recente.

        I bucket sono orari ("2026-08-17T09:00:00") o giornalieri se compattati
        ("2026-08-17"): in entrambi i casi la data e' il prefisso.
        """
        with self.lock:
            profile = self._profile_ref(profile_name)
            totals = {}
            for bucket_key, bucket in profile.get("hourly", {}).items():
                day = bucket_key.split("T")[0]
                if not isinstance(bucket, dict):
                    continue
                totals[day] = totals.get(day, 0) + sum(bucket.get("keys", {}).values())

        ordered = sorted(totals.items())
        if days is None:
            return ordered

        # Si riempiono anche i giorni senza attivita', altrimenti il grafico
        # mente sulla continuita' dell'uso.
        today = datetime.now().date()
        window = []
        for offset in range(days - 1, -1, -1):
            day = (today - timedelta(days=offset)).strftime("%Y-%m-%d")
            window.append((day, totals.get(day, 0)))
        return window

    def get_accuracy_stats(self, profile_name):
        """Rapporto fra correzioni e battute totali.

        session_total_clicks e session_backspace_clicks erano gia' contati dal
        tracker ma non venivano letti da nessuno, e valevano comunque solo per
        la sessione in corso. Qui il calcolo si basa sui conteggi archiviati,
        quindi vale su tutto lo storico del profilo.
        """
        with self.lock:
            counts = self._cached_key_counts(profile_name)
            total = sum(counts.values())
            corrections = counts.get("Backspace", 0) + counts.get("Delete", 0)

        if total <= 0:
            return {"total": 0, "corrections": 0, "accuracy": 0.0, "correction_rate": 0.0}

        rate = corrections / total
        return {
            "total": total,
            "corrections": corrections,
            "accuracy": (1.0 - rate) * 100.0,
            "correction_rate": rate * 100.0,
        }

    def get_streaks(self, profile_name):
        """Giorni consecutivi di attivita': serie in corso e serie migliore."""
        days = [day for day, count in self.get_daily_totals(profile_name) if count > 0]
        if not days:
            return {"current": 0, "best": 0, "active_days": 0, "best_day": None, "best_day_count": 0}

        dates = sorted(datetime.strptime(day, "%Y-%m-%d").date() for day in days)

        best = run = 1
        for previous, current in zip(dates, dates[1:]):
            run = run + 1 if (current - previous).days == 1 else 1
            best = max(best, run)

        # La serie in corso vale solo se arriva a oggi o a ieri
        today = datetime.now().date()
        current_run = 0
        if (today - dates[-1]).days <= 1:
            current_run = 1
            for previous, following in zip(reversed(dates[:-1]), reversed(dates[1:])):
                if (following - previous).days == 1:
                    current_run += 1
                else:
                    break

        totals = dict(self.get_daily_totals(profile_name))
        best_day = max(totals.items(), key=lambda x: x[1]) if totals else (None, 0)

        return {
            "current": current_run,
            "best": best,
            "active_days": len(dates),
            "best_day": best_day[0],
            "best_day_count": best_day[1],
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
                self.mark_dirty()

    def get_burst_records(self, profile_name):
        with self.lock:
            return list(self._profile_ref(profile_name).get("burst_records", []))

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

            # Cambia a ogni passaggio di finestra: si segna soltanto, ci pensa
            # il thread di salvataggio periodico.
            self.mark_dirty()

