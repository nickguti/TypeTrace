import sys

with open("ui.py", "r", encoding="utf-8") as f:
    content = f.read()

old_sync = """        if hasattr(self, "kb_layout_combo"):
            self.kb_layout_combo.blockSignals(True)
            self.kb_layout_combo.setCurrentText(settings_mgr.get("keyboard_layout", "100%"))
            self.kb_layout_combo.blockSignals(False)"""

new_sync = """        if hasattr(self, "kb_layout_combo"):
            self.kb_layout_combo.blockSignals(True)
            val = settings_mgr.get("keyboard_layout")
            self.kb_layout_combo.setCurrentText(val if val is not None else "100%")
            self.kb_layout_combo.blockSignals(False)"""

content = content.replace(old_sync, new_sync)

old_rect = """        fmt = self.parent_ui.settings_mgr.get("keyboard_layout", "100%") if self.parent_ui else "100%"
"""
new_rect = """        fmt = "100%"
        if self.parent_ui:
            f_val = self.parent_ui.settings_mgr.get("keyboard_layout")
            if f_val:
                fmt = f_val
"""
content = content.replace(old_rect, new_rect)

with open("ui.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed get() parameter bug")
