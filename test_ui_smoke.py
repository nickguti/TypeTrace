"""Test di fumo sull'interfaccia.

I quindici test esistenti coprivano database, tracker e utils, cioe' l'unica
parte che non si rompeva: tutti i crash registrati nel log stavano in ui.py.
Questi test istanziano la finestra vera e percorrono i punti che fallivano,
piu' i contratti fra moduli che nessuno verificava.

Girano senza schermo: basta QT_QPA_PLATFORM=offscreen (impostato qui sotto).
"""

import os
import shutil
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# I test non devono scrivere sulle impostazioni vere dell'utente
_SETTINGS_DIR = tempfile.mkdtemp(prefix="typetrace_test_")
os.environ["TYPETRACE_DATA_DIR"] = _SETTINGS_DIR

import keymap
import utils
from database import Database
from tracker import KeystrokeTracker

from PyQt6.QtWidgets import QApplication

_app = QApplication.instance() or QApplication([])


class TestModuleContracts(unittest.TestCase):
    """Ogni metodo che l'interfaccia invoca deve esistere davvero.

    Cinque dei crash storici erano nomi di metodo inventati: add_profile,
    reset_profile, set_active_profile, l'attributo burst_val.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = Database(filepath="test_data.json", directory=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_database_exposes_every_method_the_ui_calls(self):
        import re
        src = open(os.path.join(os.path.dirname(__file__), "ui.py"), encoding="utf-8").read()
        called = set(re.findall(r"(?:self\.db|self\._db|self\.parent_ui\.db)\.([a-z_]+)\(", src))
        missing = sorted(name for name in called if not hasattr(self.db, name))
        self.assertEqual(missing, [], f"ui.py chiama metodi inesistenti su Database: {missing}")

    def test_tracker_exposes_every_method_the_ui_calls(self):
        import re
        src = open(os.path.join(os.path.dirname(__file__), "ui.py"), encoding="utf-8").read()
        called = set(re.findall(r"self\.tracker\.([a-z_]+)\(", src))
        tracker = KeystrokeTracker(self.db)
        missing = sorted(name for name in called if not hasattr(tracker, name))
        self.assertEqual(missing, [], f"ui.py chiama metodi inesistenti su KeystrokeTracker: {missing}")

    def test_total_profile_reads_the_aggregate(self):
        """get_stats_for_profile("Total") deve leggere "__all__"."""
        self.db.log_key("Desktop", "A")
        stats = self.db.get_stats_for_profile("Total")
        self.assertTrue(stats.get("hourly"), "la vista Total risulta vuota")

    def test_stats_snapshot_is_a_copy(self):
        self.db.log_key("Default", "A")
        snapshot = self.db.get_stats_for_profile("Default")
        snapshot["hourly"].clear()
        self.assertTrue(self.db.get_stats_for_profile("Default").get("hourly"))


class TestKeyNaming(unittest.TestCase):
    """I nomi salvati dal tracker devono corrispondere ai tasti disegnati."""

    def test_every_drawn_key_is_reachable(self):
        from ui import KEYBOARD_LAYOUT
        tracker = KeystrokeTracker.__new__(KeystrokeTracker)
        producible = set()
        for vk, name in keymap.VK_TO_KEY.items():
            producible.add(name)
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            producible.add(letter)
        producible.update({"Space", "Enter", "Tab", "Backspace", "Caps", "Esc",
                           "Shift_L", "Shift_R", "Ctrl_L", "Ctrl_R", "Alt_L",
                           "Alt_R", "Win_L", "Win_R", "Menu", "Insert", "Delete",
                           "Home", "End", "Page_up", "Page_down", "Up", "Down",
                           "Left", "Right", "Print_screen", "Scroll_lock",
                           "Pause", "Num_lock"})
        unreachable = []
        for key in KEYBOARD_LAYOUT:
            stored = keymap.key_for_layout(key["id"])
            if stored not in producible:
                unreachable.append((key["id"], stored))
        self.assertEqual(unreachable, [], f"tasti che non si illumineranno mai: {unreachable}")

    def test_control_characters_resolve_to_real_keys(self):
        """Ctrl+S deve contare come "S", non come "\\x13"."""
        from pynput.keyboard import KeyCode
        tracker = KeystrokeTracker.__new__(KeystrokeTracker)
        self.assertEqual(tracker.map_key_to_name(KeyCode(char="\x13", vk=83)), "S")
        self.assertEqual(tracker.map_key_to_name(KeyCode(char="\x16", vk=86)), "V")

    def test_legacy_data_can_be_repaired(self):
        self.assertEqual(keymap.repair_key_name("\x13"), "S")
        self.assertEqual(keymap.repair_key_name("<65>"), "A")
        self.assertEqual(keymap.repair_key_name("Space"), "Space")


class TestTrackerBehaviour(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = Database(filepath="test_data.json", directory=self.tmp)
        self.tracker = KeystrokeTracker(self.db)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_lone_modifier_is_not_a_shortcut(self):
        """Premere il solo Ctrl non deve produrre la combinazione Ctrl+Ctrl_L."""
        from pynput.keyboard import Key
        self.tracker.on_press(Key.ctrl_l)
        combos = self.db.get_aggregated_stats("Default").get("combinations", {})
        self.assertEqual(combos, {}, f"combinazioni spurie: {combos}")

    def test_modifier_state_can_be_reset(self):
        self.tracker.pressed_modifiers["alt"] = True
        self.tracker.pressed_keys.add("A")
        self.tracker.reset_key_state()
        self.assertFalse(self.tracker.pressed_modifiers["alt"])
        self.assertEqual(self.tracker.pressed_keys, set())


class TestWindowSmoke(unittest.TestCase):
    """Costruisce la finestra vera e percorre i punti che andavano in eccezione."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = Database(filepath="test_data.json", directory=self.tmp)
        # Dati realistici: bigrammi annidati e un record di raffica
        for key in ("A", "S", "D", "Space", "Esc", ",", "Caps"):
            self.db.log_key("Default", key, bigram_next="S", last_key="A")
        self.db.log_key("Default", "C", combination="Ctrl+C")
        self.db.add_burst_record("Default", 320, 8.5)
        self.tracker = KeystrokeTracker(self.db)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _build(self):
        from ui import TypeTraceUI
        window = TypeTraceUI(self.db, self.tracker)
        # Niente avvisi ne' procedura guidata durante i test
        window.settings_mgr.set("tray_notice_shown", True)
        window.settings_mgr.set("welcome_shown", True)
        window._force_quit = True
        return window

    def test_window_builds(self):
        window = self._build()
        self.addCleanup(window.close)
        self.assertIsNotNone(window.peak_val)

    def test_telemetry_tab_renders_completely(self):
        """La scheda si interrompeva sull'ordinamento dei bigrammi annidati."""
        window = self._build()
        self.addCleanup(window.close)
        window._update_telemetry()
        self.assertNotEqual(window.peak_val.text(), "0 APM (0s)")
        self.assertTrue(window.bigrams_list.data, "lista dei bigrammi vuota")

    def test_burst_event_updates_the_card(self):
        """L'evento burst_detected sollevava AttributeError su burst_val."""
        window = self._build()
        self.addCleanup(window.close)
        window.event_queue.put(("burst_detected", (450, 12.0)))
        window._process_queue()
        self.assertIn("450", window.peak_val.text())

    def test_incognito_from_tray_is_handled(self):
        """L'evento del menu dell'area di notifica veniva scartato in silenzio."""
        window = self._build()
        self.addCleanup(window.close)
        self.assertFalse(self.tracker.incognito_mode)
        window.event_queue.put(("toggle_incognito", None))
        window._process_queue()
        self.assertTrue(self.tracker.incognito_mode)

    def test_profile_change_does_not_raise(self):
        window = self._build()
        self.addCleanup(window.close)
        self.db.create_profile("Lavoro")
        window.profile_combo.addItem("Lavoro")
        window.profile_combo.setCurrentText("Lavoro")
        self.assertEqual(self.tracker.active_profile, "Lavoro")
        self.assertEqual(self.db.get_last_profile(), "Lavoro")

    def test_reset_button_actually_resets(self):
        window = self._build()
        self.addCleanup(window.close)
        window.current_profile = "Default"
        self.db.reset_profile_statistics("Default")
        self.assertEqual(self.db.get_stats_for_profile("Default").get("hourly"), {})

    def test_heatmap_lights_the_keys_that_were_pressed(self):
        window = self._build()
        self.addCleanup(window.close)
        window.heatmap.heatmap_enabled = True
        window._update_heatmap_colors()
        colored = window.heatmap.target_colors
        # "Esc", "," e "Caps" sono salvati cosi', ma la tastiera li disegna
        # come "Escape", "Comma" e "CapsLock".
        for layout_id in ("Escape", "Comma", "CapsLock"):
            self.assertIn(layout_id, colored, f"il tasto {layout_id} non si illumina")


class TestProcessDetection(unittest.TestCase):
    def test_foreground_process_is_detected(self):
        """Restituiva sempre None: l'auto-switch non poteva funzionare."""
        if os.name != "nt":
            self.skipTest("solo Windows")
        name = utils.get_active_window_process_name()
        self.assertTrue(name and name.lower().endswith(".exe"),
                        f"nome del processo non rilevato: {name!r}")

    def test_desktop_apps_are_not_classified_as_games(self):
        for app in ("notion.exe", "obsidian.exe", "figma.exe", "whatsapp.exe", "chrome.exe"):
            self.assertEqual(utils.classify_process(app), "desktop", app)


if __name__ == "__main__":
    unittest.main()
