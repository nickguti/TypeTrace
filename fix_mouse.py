import sys

with open("ui.py", "r", encoding="utf-8") as f:
    content = f.read()

old_mouse_move = """        pos = event.position()
        draw_rect = self._compute_draw_rect()
        found_key = None
        for key in KEYBOARD_LAYOUT:
            px = draw_rect.x() + key["rx"] * draw_rect.width()
            py = draw_rect.y() + key["ry"] * draw_rect.height()
            pw = key["rw"] * draw_rect.width()
            ph = key["rh"] * draw_rect.height()"""

new_mouse_move = """        pos = event.position()
        draw_rect, max_rx, fmt = self._compute_draw_rect()
        found_key = None
        for key in KEYBOARD_LAYOUT:
            if fmt == "TKL" and key["rx"] > 0.86:
                continue
            px = draw_rect.x() + (key["rx"] / max_rx) * draw_rect.width()
            py = draw_rect.y() + key["ry"] * draw_rect.height()
            pw = (key["rw"] / max_rx) * draw_rect.width()
            ph = key["rh"] * draw_rect.height()"""

if old_mouse_move in content:
    content = content.replace(old_mouse_move, new_mouse_move)
else:
    print("Failed to find mouseMoveEvent lines!")

with open("ui.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Mouse move fix applied.")
