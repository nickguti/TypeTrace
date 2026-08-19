# Changelog

Notable changes to TypeTrace. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions use
[semantic versioning](https://semver.org/).

## [3.2.0] - 2026-08-19

A full pass over the codebase: 31 defects fixed, four advertised features that
had never actually run, and the first test coverage of the interface.

### Fixed

- **Process auto-switch had never fired.** The process was opened with
  `PROCESS_QUERY_LIMITED_INFORMATION` and then queried with
  `GetModuleBaseNameW`, which requires more than that, so the call always
  failed silently. Profile mappings, the recent-app list and the gaming banner
  all depended on it and were dead with it.
- **Telemetry tab** read the literal `Total` profile instead of the internal
  aggregate, leaving the chart, the burst record and the counter permanently
  empty; and it stopped halfway through drawing when sorting nested bigrams.
- **Incognito mode was unreachable.** The tray menu item sent an event nothing
  handled, and the `Ctrl+Shift+I` hotkey never fired.
- **Key names:** 28 of 104 keys could never light up, because the tracker and
  the drawn keyboard used two different naming conventions.
- **Keys pressed with Ctrl** were stored as control characters (`\x13`
  instead of `S`).
- **Modifiers stayed latched** after `Alt+Tab`, so every later keystroke was
  recorded as an `Alt+…` shortcut.
- **AltGr** produced `Ctrl+Alt` combinations that were never pressed.
- **A lone modifier** logged `Ctrl+Ctrl_L` as if it were a shortcut.
- **Resetting statistics, creating a profile and switching profile** all
  raised exceptions from method names that do not exist.
- **Data in the packaged executable** was written to PyInstaller's temporary
  folder and disappeared on every close. It now lives in `%APPDATA%\TypeTrace`.
- **Missing translations in the binary:** the build did not bundle
  `lang.json`, so the interface showed raw keys instead of text.
- **Non-atomic saves:** an interruption mid-write truncated the database. Now
  written to a temporary file and swapped in, keeping a `.bak`.
- **Export** reported success even when the write failed, and ignored two of
  its own checkboxes.
- **The floating overlay** could open empty and off-screen with no way back.
- **Start with Windows** registered a command Windows could not run.
- Memory growth in the key animations while minimised, a frozen theme snapshot
  left over the interface, compact mode not restored, an unrotated log, no
  single-instance guard, and a shutdown path that re-entered itself.

### Added

- **Typing accuracy:** corrections against total keystrokes.
- **Daily activity:** a chart of the last 30 days.
- **Current and best streak**, and the **best-day record**.
- **Profile management** in the interface: create and delete.
- **A switch to turn automatic profile switching off.**
- `CHANGELOG.md`, `LICENSE` (MIT, which the README claimed without shipping
  it) and 38 tests — 23 of them on the interface — run in CI before the build.

### Changed

- **Incremental aggregation:** totals are no longer recomputed on every
  keystroke. The cost is constant instead of growing with the archive.
- **Repaints:** the keyboard is no longer redrawn 33 times a second while
  nothing moves, and the timers stop when the window is in the tray.
- **History compaction:** hourly data older than 180 days becomes daily, with
  identical totals.
- `requirements.txt` reduced to the five real dependencies. It had been a full
  development-machine freeze containing a reference to a local path, which
  stopped the build from installing anything at all.

### Migration

On first launch existing data is copied to `%APPDATA%\TypeTrace`, key names are
repaired and history beyond 180 days is compacted. The original files are left
untouched and a `.bak` copy is kept. `TYPETRACE_DATA_DIR` overrides the
location.
