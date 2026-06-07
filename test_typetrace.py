import os
import unittest
import json
from datetime import datetime, timedelta

from database import Database

class TestTypeTraceDatabase(unittest.TestCase):
    def setUp(self):
        # Create a database with a separate test filename
        self.test_filename = "test_typetrace_data.json"
        self.db = Database(filepath=self.test_filename)
        
    def tearDown(self):
        # Clean up database file
        if os.path.exists(self.db.filepath):
            try:
                os.remove(self.db.filepath)
            except Exception:
                pass
                
    def test_default_profile_initialization(self):
        """Verify that default profile is set up on init."""
        self.assertIn("Default", self.db.get_profiles())
        self.assertEqual(self.db.get_last_profile(), "Default")
        
    def test_create_and_delete_profile(self):
        """Verify profile creation and deletion logic."""
        # Create
        self.assertTrue(self.db.create_profile("CustomProfile"))
        self.assertIn("CustomProfile", self.db.get_profiles())
        
        # Prevent duplicates
        self.assertFalse(self.db.create_profile("CustomProfile"))
        
        # Delete
        self.assertTrue(self.db.delete_profile("CustomProfile"))
        self.assertNotIn("CustomProfile", self.db.get_profiles())
        
        # Prevent deleting "Default" or built-in profiles
        self.assertFalse(self.db.delete_profile("Default"))
        self.assertFalse(self.db.delete_profile("Total"))
        self.assertFalse(self.db.delete_profile("Desktop"))
        self.assertFalse(self.db.delete_profile("Gaming"))

    def test_builtin_profiles_initialization(self):
        """Verify that Total, Desktop, and Gaming are initialized and marked as built-in."""
        profiles = self.db.get_profiles()
        self.assertIn("Total", profiles)
        self.assertIn("Desktop", profiles)
        self.assertIn("Gaming", profiles)
        self.assertNotIn("__all__", profiles) # Hidden internal profile
        # Check that they are marked as built-in in settings
        self.assertIn("Total", self.db.data["settings"]["builtin_profiles"])
        self.assertIn("Desktop", self.db.data["settings"]["builtin_profiles"])
        self.assertIn("Gaming", self.db.data["settings"]["builtin_profiles"])

    def test_total_profile_aggregation(self):
        """Verify that the Total profile aggregates data from all non-Total profiles."""
        # Log keys to Desktop and Gaming
        self.db.log_key("Desktop", "A")
        self.db.log_key("Gaming", "B")
        self.db.log_key("Gaming", "B")
        
        # Get stats for Total
        total_stats = self.db.get_aggregated_stats("Total")
        
        # Total should contain the sum of Desktop and Gaming
        self.assertEqual(total_stats["keys"].get("A"), 1)
        self.assertEqual(total_stats["keys"].get("B"), 2)

    def test_keystroke_logging_and_aggregation(self):
        """Verify that logged keys accumulate correctly in hourly buckets."""
        profile = "Default"
        
        # Log key A three times, key Space twice
        self.db.log_key(profile, "A")
        self.db.log_key(profile, "A")
        self.db.log_key(profile, "A")
        self.db.log_key(profile, "Space")
        self.db.log_key(profile, "Space")
        
        # Verify aggregated stats
        stats = self.db.get_aggregated_stats(profile)
        self.assertEqual(stats["keys"]["A"], 3)
        self.assertEqual(stats["keys"]["Space"], 2)
        
    def test_bigram_transitions(self):
        """Verify transition bigrams are counted correctly."""
        profile = "Default"
        
        # Log transition T -> H
        self.db.log_key(profile, "T", bigram_next="H")
        self.db.log_key(profile, "T", bigram_next="H")
        self.db.log_key(profile, "T", bigram_next="E")
        
        stats = self.db.get_aggregated_stats(profile)
        self.assertEqual(stats["bigrams"]["T"]["H"], 2)
        self.assertEqual(stats["bigrams"]["T"]["E"], 1)
        
    def test_detailed_key_statistics(self):
        """Verify hover stats calculations (percentages, peak PPM, trends)."""
        profile = "Default"
        
        # Log keys
        self.db.log_key(profile, "A", bigram_next="N")
        self.db.log_key(profile, "A", bigram_next="N")
        self.db.log_key(profile, "B")
        
        # Compute stats for 'A'
        stats_a = self.db.get_key_stats(profile, "A")
        
        # 2 A's out of 3 total presses = 66.67%
        self.assertEqual(stats_a["total"], 2)
        self.assertEqual(stats_a["percentage"], "66.67%")
        
        # Bigram next: N (2 times)
        self.assertEqual(stats_a["bigram"], "'N' (2 times)")
        
        # Peak PPM (2 presses in current hour bucket / 60)
        self.assertEqual(stats_a["peak_ppm"], "0.03 presses/min")
        
    def test_trend_calculation_empty(self):
        """Verify trends when no usage is logged yet."""
        stats = self.db.get_key_stats("Default", "Z")
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["trend"], "Stable (No usage yet)")

    def test_corrupted_json_load_recovery(self):
        """Verify that loading corrupted JSON renames it to database_corrupted.json and heals the file."""
        filepath = self.db.filepath
        # Write corrupted JSON content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("{ invalid json structure: [ ] ")
            
        # Re-initialize the database to trigger recovery logic
        healed_db = Database(filepath=self.test_filename)
        
        # Verify database is recovered
        self.assertIn("Default", healed_db.get_profiles())
        
        # Verify that the corrupted file was renamed
        corrupted_path = filepath.replace("test_typetrace_data.json", "database_corrupted.json")
        self.assertTrue(os.path.exists(corrupted_path))
        
        # Clean up corrupted file
        if os.path.exists(corrupted_path):
            os.remove(corrupted_path)

    def test_backspace_ratio_tracking(self):
        """Verify that backspace ratio is tracked and calculated correctly."""
        from tracker import KeystrokeTracker
        from pynput.keyboard import Key, KeyCode
        
        tracker = KeystrokeTracker(self.db)
        
        # Initially 0
        self.assertEqual(tracker.session_total_clicks, 0)
        self.assertEqual(tracker.session_backspace_clicks, 0)
        
        # Click normal keys and backspaces
        tracker.on_press(KeyCode.from_char('a'))
        tracker.on_press(KeyCode.from_char('b'))
        tracker.on_press(Key.backspace)
        tracker.on_press(Key.delete)
        
        self.assertEqual(tracker.session_total_clicks, 4)
        self.assertEqual(tracker.session_backspace_clicks, 2)
        
        # Calculate ratio
        ratio = (tracker.session_backspace_clicks / tracker.session_total_clicks) * 100
        self.assertEqual(ratio, 50.0)

    def test_burst_mode_record_logging(self):
        """Verify that burst records can be added and are correctly sorted/retrieved."""
        profile = "Default"
        
        # Log a few bursts
        self.db.add_burst_record(profile, peak_apm=260, duration=6.5)
        self.db.add_burst_record(profile, peak_apm=300, duration=10.2)
        self.db.add_burst_record(profile, peak_apm=280, duration=5.1)
        
        records = self.db.get_burst_records(profile)
        self.assertEqual(len(records), 3)
        
        # Records should be sorted by peak_apm descending
        self.assertEqual(records[0]["peak_apm"], 300)
        self.assertEqual(records[1]["peak_apm"], 280)
        self.assertEqual(records[2]["peak_apm"], 260)

    def test_switch_wear_calculation_tooltip(self):
        """Verify that switch wear percentage math is correct based on total presses."""
        # Log a key 5000 times (should be 0.01000% of 50M)
        profile = "Default"
        for _ in range(5000):
            self.db.log_key(profile, "Space")
            
        stats = self.db.get_key_stats(profile, "Space")
        self.assertEqual(stats["total"], 5000)
        
        consumed_pct = (stats['total'] / 50000000.0) * 100
        self.assertAlmostEqual(consumed_pct, 0.01)

    def test_settings_and_mappings_persistence(self):
        """Verify settings such as heatmap theme, overlay enable, and process mapping persistence."""
        # Heatmap theme
        self.db.set_heatmap_theme("Cyberpunk")
        self.assertEqual(self.db.get_heatmap_theme(), "Cyberpunk")
        
        # Overlay enabled
        self.db.set_overlay_enabled(True)
        self.assertTrue(self.db.get_overlay_enabled())
        
        # Profile mappings
        mappings = {"code.exe": "Coding", "notepad.exe": "Notes"}
        self.db.set_profile_mappings(mappings)
        self.assertEqual(self.db.get_profile_mappings(), mappings)

    def test_process_classification(self):
        """Verify process automatic classification heuristics."""
        import utils
        
        # 1. Definite desktop process (should return "desktop")
        res_desktop = utils.classify_process("explorer.exe")
        self.assertEqual(res_desktop, "desktop")
        
        res_chrome = utils.classify_process("chrome.exe")
        self.assertEqual(res_chrome, "desktop")
        
        # 2. Test cache functionality
        utils._classify_cache["test_dummy_game.exe"] = ("gaming", utils.time.time())
        res_cached = utils.classify_process("test_dummy_game.exe")
        self.assertEqual(res_cached, "gaming")

    def test_recent_processes_list(self):
        """Verify settings['recent_processes'] upsert and trim functionality."""
        self.db.log_process_seen("chrome.exe", "Desktop")
        self.db.log_process_seen("game.exe", "Gaming")
        
        # Manually set timestamps to guarantee deterministic sort order
        for entry in self.db.data["settings"]["recent_processes"]:
            if entry["process_name"] == "game.exe":
                entry["last_seen"] = "2026-06-07 18:00:00"
            elif entry["process_name"] == "chrome.exe":
                entry["last_seen"] = "2026-06-07 17:00:00"
        self.db.save_data()
        
        recent = self.db.get_recent_processes(limit=5)
        self.assertEqual(len(recent), 2)
        
        # Latest first
        self.assertEqual(recent[0]["process_name"], "game.exe")
        self.assertEqual(recent[0]["category"], "Gaming")
        self.assertEqual(recent[1]["process_name"], "chrome.exe")
        self.assertEqual(recent[1]["category"], "Desktop")
        
        # Upsert
        self.db.log_process_seen("chrome.exe", "Coding")
        for entry in self.db.data["settings"]["recent_processes"]:
            if entry["process_name"] == "chrome.exe":
                entry["last_seen"] = "2026-06-07 19:00:00"
        self.db.save_data()
        
        recent_updated = self.db.get_recent_processes(limit=5)
        self.assertEqual(len(recent_updated), 2)
        self.assertEqual(recent_updated[0]["process_name"], "chrome.exe")
        self.assertEqual(recent_updated[0]["category"], "Coding")

if __name__ == "__main__":
    unittest.main()
