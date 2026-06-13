# TypeTrace — Cross-file Notes

> RULE FOR ALL CHATS: Never overwrite this file. Always APPEND new entries
> at the BOTTOM. Never delete or modify existing entries from other chats.
> Read the full file before every response.

---

## Framework
- PyQt6 (migrated from CustomTkinter)
- Styling via setStyleSheet() with CSS-like syntax
- Layouts: QVBoxLayout, QHBoxLayout, QGridLayout
- Threading: QThread or threading.Thread with signal/slot

## Project structure
- main.py      — entry point, tray icon, logging
- ui.py        — main PyQt6 window, all UI panels
- overlay.py   — borderless floating HUD widget
- tracker.py   — pynput keyboard listener, APM/WPM, process monitoring
- database.py  — JSON storage, profile management, stats aggregation
- utils.py     — process classification, color interpolation, win32 helpers

## Design system
- BG_MAIN        = "#0B0C10"
- BG_CARD        = "#111318"
- BG_CARD_INNER  = "#171A23"
- BORDER         = "#232733"
- ACCENT         = "#00F5D4"
- KEYCAP_BASE    = "#20222B"
- KEYCAP_HOVER   = "#2F313D"
- TEXT_PRIMARY   = "#FFFFFF"
- TEXT_SECONDARY = "#8E9297"
- FONT_FAMILY    = "Inter"

## Key interfaces between files
- tracker.active_profile → read by ui.py (header indicator) and overlay.py
- tracker.last_detected_process → read by ui.py (header label)
- tracker.apm, tracker.wpm → read by ui.py and overlay.py
- tracker.ui_update_callback → called with ("profile_changed", name) and ("key_pressed", key)
- db.get_aggregated_stats("Total") → reads from "__all__" internal profile
- db.get_profiles() → never returns "__all__"
- overlay toggled by "Floating Widget" switch in ui.py

## Built-in profiles
- Total, Desktop, Gaming, Default → protected, cannot be deleted
- "__all__" → internal aggregate profile, never shown in UI

## Known issues
- Keyboard resize still causes layout issues at non-default window sizes

## Changelog
(chats append here after each modification)

## 2026-06-10 DATABASE
- Initialized database agent.
- Updated `get_builtin_profiles()`, `_ensure_builtin_profiles()`, and `get_profiles()` to explicitly include "Default" as a built-in protected profile according to project context.

## 2026-06-10 OVERLAY
- Added `activate()` and `deactivate()` methods to `FloatingOverlay` so `ui.py` can toggle its visibility successfully.
- Added color fallback for `accent_color` to prevent rendering crashes in `paintEvent` if missing from settings.
- Updated positioning logic in `_restore_position` to use `QApplication.primaryScreen()` preventing issues before the top-level widget is shown.
- Fixed a bug in `contextMenuEvent` targeting the incorrect UI checkbox variable name (`overlay_cb`).

## 2026-06-10 OVERLAY (UI Exceptions)
- With user permission, broke the `overlay.py`-only rule to fix a critical UI connection in `ui.py`.
- Modified `_on_overlay_toggle` in `ui.py` to instantiate `FloatingOverlay` on first use and hook `activate()`/`deactivate()`.
- Added live APM/WPM updates to `floating_overlay` directly within `_process_queue` in `ui.py`.

## 2026-06-10 UI
- Implemented `mouseMoveEvent` and `leaveEvent` in `KeyboardHeatmapWidget` to show `KeyTooltip` on hover.
- Positioned the tooltip at the global cursor position `+ QPoint(15, 15)` and clamped it to the screen edges via `QApplication.primaryScreen().availableGeometry()`.
- To avoid performance spam, it fetches exact hits/totals/rank from the database ONLY when the hovered `key_id` actually changes.
- Gracefully handles empty hits/DB by passing `-1` for the rank to hide the ranking label natively.

## 2026-06-11 UI (Bugfix)
- Fixed data-fetching bug in `_update_heatmap_colors` and `_update_telemetry`.
- Swapped `get_stats_for_profile` to `get_aggregated_stats` to correctly retrieve the aggregated "keys" top-level dictionary.
- Retained the call to `get_stats_for_profile` solely to fetch "hourly" data for the chart widget to avoid breaking the telemetry graphs.

## 2026-06-11 UI (Feature)
- Introduced the "Keyboard Style" setting in `SettingsDrawer` (Mechanical, Flat, Outlined).
- Updated `SettingsManager.DEFAULTS` to include `"keyboard_style": "Mechanical"` as fallback.
- Hooked combobox events to `settings_mgr` and refreshed `KeyboardHeatmapWidget.paintEvent`.
- Modified drawing logic in `paintEvent` to dynamically handle shadows, highlights, transparent backgrounds (NoBrush), colored outlines, and readable text colors depending on the active style.

## 2026-06-11 UI (Bugfix)
- Fixed `TypeError` crash on startup inside `SettingsDrawer.sync_settings`. Removed the unsupported second fallback argument from `settings_mgr.get("keyboard_theme")` and `settings_mgr.get("keyboard_style")` as `SettingsManager` automatically relies on its internal `DEFAULTS`.

## 2026-06-11 UI (Bugfix)
- Fixed `TypeError` crash in `KeyboardHeatmapWidget.paintEvent` caused by passing a default fallback argument to `settings_mgr.get("keyboard_style")`.

## 2026-06-11 UI (Feature)
- Replaced the basic "Flat" and "Outlined" keyboard styles with rich "Neon Cyberpunk" and "Pudding Keycaps" variants.
- Introduced a new "60%" keyboard layout sizing option. Added specific calculation logic (`ar=3.0`, `max_rx=0.72`) in `_compute_draw_rect` to prevent UI warping and filtering logic in `paintEvent` to correctly drop F-row, NumPad, and navigation clusters.

## 2026-06-11 UI (Tweak)
- Swapped the instantiation blocks in `HeaderWidget.__init__` so `compact_btn` is added to the layout before `gear_btn`, changing their visual order on the right side of the header.

## 2026-06-11 UI (Feature)
- Implemented "minimize to system tray" logic. Cliccare sulla 'X' nasconde la finestra (`event.ignore()`, `self.hide()`) preservando il logger in esecuzione.
- Il programma intercetta gli eventi "restore" (dal system tray) per riattivare la finestra (`self.show()`, `self.activateWindow()`).
- Il programma intercetta gli eventi "exit" che forzano la chiusura abilitando un flag `self._force_quit`.
- Rimosso `self.tracker.stop()` da `closeEvent` (delega al main.py che già lo gestisce).

## 2026-06-11 UI (Bugfix)
- Fixed `process_event_queue` in `ui.py` which was completely ignoring the shared queue generated by the system tray menu in `main.py`. The method now correctly assigns `self.event_queue = q`.

## 2026-06-11 UI (Feature)
- Completato il restyling totale del pannello Telemetry in `ui.py`.
- Introdotte le `MiniCard` "Total Keystrokes", "Peak Hourly APM" (calcolato dai dati "hourly") e "Most Used Key".
- Aggiunto un nuovo widget `TelemetryProgressListWidget` che renderizza progress bar orizzontali per "Top Combinations" e "Top Bigrams".
- Integrato l'esistente `HourlyChartWidget` come "Activity Timeline".
- Avvolto l'intero layout del tab in una `QScrollArea` stilizzata e aggiornato il metodo `_update_telemetry` per popolare i nuovi widget. Aggiornata anche `_apply_theme` per colorare i nuovi widget in tempo reale.

## 2026-06-11 UI (Feature)
- Completata la Fase 2: Configurazione e Overlay.
- Rimosso definitivamente il `SettingsDrawer` e il pulsante con l'ingranaggio nell'header.
- Tutte le impostazioni sono state migrate nel main flow:
  - `tab_config` ricostruita da zero usando `QScrollArea` e `MiniCard` tematiche (Appearance, Behavior, Data & Profiles).
  - Creata una nuova `tab_overlay` per la gestione indipendente di metriche (APM, WPM, Peak APM, Profilo) e aspetto (Opacità e Scala) dell'overlay flottante tramite `QSlider` e `SettingsManager`.
- Implementato un custom widget `ModernSwitch` che rimpiazza tutte le `QCheckBox` per le impostazioni booleane, offrendo un feeling in stile iOS/Material completamente integrato col sistema di token dell'interfaccia.

## 2026-06-11 FEATURE: Connect Overlay Settings
- Modified `ui.py` to include a 'Toggle Floating Overlay' `QPushButton` at the top of `tab_overlay` with styling connected to `_apply_theme`.
- Updated boolean setting toggles (APM, WPM, Peak, Profile) and sliders (Opacity, Scale) in `ui.py` to immediately call `self.floating_overlay.apply_settings()`.
- Added `apply_settings()` to `FloatingOverlay` in `overlay.py` which dynamically reads settings, updates `_visible_fields`, `_scale`, opacity, and triggers a UI update.
- Updated `FloatingOverlay.paintEvent` and geometry functions to leverage `painter.scale()` ensuring the HUD scales seamlessly.
- Deleted `OverlayFieldConfigDialog` and removed its context menu action since all settings are now managed securely via `ui.py` and `SettingsManager`.

## 2026-06-11 FEATURE: Fix Overlay State Synchronization
- Validated `_on_overlay_toggle` inside `ui.py` explicitly calls `self.floating_overlay.apply_settings()` upon lazy instantiation.
- Confirmed `self.btn_toggle_overlay.setText()` updates accurately reflecting the floating widget state (Mostra/Nascondi).
- Verified `_on_overlay_setting_change` effectively pushes live updates to the overlay via `apply_settings()` if it has been instantiated.
- Checked `apply_settings` inside `overlay.py` correctly triggers `_recalc_size()` and explicitly calls `self.update()` to guarantee instantaneous, flicker-free repaint of the UI when settings are hot-swapped.

## 2026-06-11 UI (Feature)
- Re-architected `tab_home` inside `ui.py` to embed a top "Dashboard" layout, moving the Keyboard Heatmap rendering inside a dedicated container.
- Dashboard includes real-time `APM` and `Parole` metrics, alongside a `ModernSwitch` to dynamically toggle the Heatmap visibility.
- Finalized Telemetry subtitles (`QLabel`) dynamically styled with `TEXT_SECONDARY` across `chart_card`, `combos_card`, and `bigrams_card`.
- Implemented a smooth Transparency Cross-Fade effect during `_on_kb_theme_change` and `_on_kb_style_change`. Utilizes `QGraphicsOpacityEffect` and `QPropertyAnimation` on a grabbed screenshot to seamlessly transition from the Settings tab back to the Keyboard Heatmap over 1.5 seconds.

## 2026-06-11 BUGFIX: Overlay Initialization Crash
- Fixed a fatal `TypeError` in `overlay.py`'s `apply_settings` method which occurred when calling `self._settings.get()` with a default argument on the custom `SettingsManager`.
- Replaced all 6 settings retrieval calls (`overlay_show_apm`, `wpm`, `peak`, `profile`, `opacity`, `scale`) with inline Python evaluation fallback `if ... is not None else ...` to gracefully handle undefined settings without crashing the UI thread.

## 2026-06-11 UI (Feature)
- Migrated Settings back to a sliding right-aligned Drawer. Removed `tab_config` from the `QTabWidget` entirely, now spawning `self.settings_drawer` as a direct child `QScrollArea` of the main window.
- Implemented a robust `QPropertyAnimation` targeting the drawer's `geometry` for smooth slide-in/slide-out animations, mapped to a new "⚙️ Impostazioni" button on the Keyboard Dashboard.
- Anchored the drawer seamlessly in `resizeEvent` so it stays glued to the right edge during window resizes.
- Re-wrote the Live Preview UX. Instead of overlaying a screenshot, changing Keyboard Theme or Style now directly triggers a `QSequentialAnimationGroup` applying a fade-down (to 0.15 opacity) and fade-up effect on the drawer itself over 800ms, immediately revealing the real-time background changes on the Keyboard dashboard behind it.

## 2026-06-11 BUGFIX: UI Initialization Crash
- Fixed `AttributeError` in `ui.py` caused by referencing a non-existent `bg_base` token during the setup of `self.settings_drawer.setStyleSheet`. Replaced with `bg_panel` to allow the app to initialize correctly.

## 2026-06-11 BUGFIX: ModernSwitch & Heatmap Toggle
- Fixed `ModernSwitch` failing to trigger reliably. Overrode `hitButton` to correctly validate clicks against the entire custom drawn rectangle instead of the default `QCheckBox` 13x13 bounding box.
- Fixed `_on_heatmap_toggle` which was destructively hiding the entire `heatmap_container`. It now intelligently disables the internal drawing logic of the `KeyboardHeatmapWidget` via an `enabled` flag and visually clears the colors, preserving the layout structure.
- Fixed the initial heatmap synchronization bug in `_init_ui`. Swapped the initialization order so `toggled.connect` is bound *before* `setChecked(True)`, ensuring the starting state is fully loaded into the `KeyboardHeatmapWidget` on app launch.

## 2026-06-12 UI Refinements
- Heatmap startup sync fixed: Relocated `setChecked(True)` to exactly *after* the `heatmap` and `legend` objects are constructed in `_init_ui`.
- Drawer UI polished: Reduced the settings dashboard button into a clean `⚙️` icon with fixed dimensions.
- UX Improvement: Added a dedicated `"❌ Chiudi"` button inside the Settings Drawer's top-right layout, enabling easier dismissal.
- Cleaned up Theme/Style handlers: Removed `QSequentialAnimationGroup` fade logic from `_on_kb_theme_change` and `_on_kb_style_change` in favor of simpler instantaneous visual updates.

## 2026-06-12 BUGFIX: Release Critical UI Adjustments
- Fixed a bug where disabling the heatmap would lock the empty heatmap colors due to an animation transition condition. `update_colors` now correctly instantly empties `self.current_colors` if an empty dictionary is passed.
- Fixed the layout jump that occurred when toggling the heatmap by removing the logic that also toggled visibility of `self.legend`.
- Moved the Settings Drawer gear button completely out of the Dashboard layout and embedded it into `HeaderWidget`, placing it gracefully beside the Compact Mode button at the top right of the application.
- Implemented `NoScrollComboBox` overriding `wheelEvent` to ignore scrolls. Applied this custom class to all Settings Drawer comboboxes so attempting to scroll through the Settings Drawer no longer accidentally changes configuration values.
- Perfected theme synchronization by adding styling cascades for `self.heatmap_toggle`, `self.main_stats_lbl`, `self.settings_drawer`, `self.btn_close_drawer`, and the main `TypeTraceUI` body natively inside `_apply_theme`.

## 2026-06-12 TRACKER
- Added state tracking (`self.pressed_keys`) to ignore OS auto-repeat events when a key is held down.
- Modified `__init__`, `on_press`, and `on_release` to enforce single physical press counts.
- No new public attributes or methods that `ui.py` or `overlay.py` might need were exposed.
## 2026-06-13 BUGFIX: Heatmap Animation and Scale
- Fixed update_colors in KeyboardHeatmapWidget to only reset 	ransition_start if it isn't currently animating, preventing stall on rapid typing.
- Fixed _update_heatmap_colors outlier scaling issue by resolving max count against the 95th percentile, maintaining vibrant coloring.
