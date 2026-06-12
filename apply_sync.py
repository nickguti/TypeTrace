import sys

with open("ui.py", "r", encoding="utf-8") as f:
    content = f.read()

old_sync = """        self.theme_combo.setCurrentText(settings_mgr.get("theme").capitalize())
        self.lang_combo.setCurrentText(settings_mgr.get("language"))
        self.compact_cb.setChecked(settings_mgr.get("compact_mode"))
        self.kb_theme_combo.setCurrentText(settings_mgr.get("keyboard_theme"))"""

new_sync = """        self.theme_combo.setCurrentText(settings_mgr.get("theme").capitalize())
        self.lang_combo.setCurrentText(settings_mgr.get("language"))
        self.compact_cb.setChecked(settings_mgr.get("compact_mode"))
        self.kb_theme_combo.setCurrentText(settings_mgr.get("keyboard_theme"))
        if hasattr(self, "kb_layout_combo"):
            self.kb_layout_combo.blockSignals(True)
            self.kb_layout_combo.setCurrentText(settings_mgr.get("keyboard_layout", "100%"))
            self.kb_layout_combo.blockSignals(False)"""

if old_sync in content:
    content = content.replace(old_sync, new_sync)
else:
    print("Failed to find sync")

with open("ui.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Sync patch applied.")
