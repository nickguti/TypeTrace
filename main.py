import os
import sys
import threading
import queue
import ctypes
import pystray
from PIL import Image, ImageDraw
import logging
from logging.handlers import RotatingFileHandler

# Ensure script directory is on the path for clean imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import paths

# Il log va accanto ai dati, non al codice: sotto PyInstaller la cartella del
# modulo e' temporanea. E viene ruotato: il file precedente era arrivato a
# 43 MB, in gran parte con la stessa eccezione ripetuta per mesi.
log_file = paths.data_path("typetrace.log")

_handler = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
))
logging.basicConfig(level=logging.ERROR, handlers=[_handler])

def global_excepthook(exctype, value, traceback):
    logging.critical("Captured unhandled global crash exception:", exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)

sys.excepthook = global_excepthook

from database import Database
from tracker import KeystrokeTracker
from ui import TypeTraceUI
import utils

# Nome del mutex di istanza singola. Due processi TypeTrace installano due hook
# (ogni tasto contato due volte) e scrivono sullo stesso file di dati:
# l'ultimo che salva sovrascrive il lavoro dell'altro.
SINGLE_INSTANCE_MUTEX = "Global\\TypeTrace_SingleInstance_Mutex"

def acquire_single_instance():
    """Restituisce l'handle del mutex, oppure None se l'app e' gia' in esecuzione."""
    try:
        handle = ctypes.windll.kernel32.CreateMutexW(None, False, SINGLE_INSTANCE_MUTEX)
        ERROR_ALREADY_EXISTS = 183
        if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            return None
        return handle
    except Exception:
        # Su piattaforme senza questa API si prosegue senza il controllo
        return -1

def create_tray_icon(tracker, event_queue):
    """
    Generates a system tray icon and menu using Pillow to draw a custom keyboard glyph.
    All tray callbacks are routed thread-safely through the event queue.
    """
    def on_restore(icon, item):
        event_queue.put(("restore", None))

    def on_toggle_incognito(icon, item):
        event_queue.put(("toggle_incognito", None))

    def on_exit(icon, item):
        event_queue.put(("exit", icon))

    def is_incognito_checked(item):
        return tracker.incognito_mode

    # Generate a pixel-perfect 64x64 icon dynamically
    width, height = 64, 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw background circle (GitHub Blue color scheme)
    draw.ellipse([4, 4, 60, 60], fill=(88, 166, 255, 255))

    # Draw a stylized virtual keyboard glyph
    draw.rounded_rectangle([14, 22, 50, 42], fill=(24, 24, 24, 255), outline=(255, 255, 255, 255), width=2, radius=3)
    draw.line([23, 22, 23, 42], fill=(255, 255, 255, 255), width=1)
    draw.line([32, 22, 32, 42], fill=(255, 255, 255, 255), width=1)
    draw.line([41, 22, 41, 42], fill=(255, 255, 255, 255), width=1)
    draw.line([14, 32, 50, 32], fill=(255, 255, 255, 255), width=1)

    # Context menu configuration
    menu = pystray.Menu(
        pystray.MenuItem("Restore TypeTrace", on_restore, default=True),
        pystray.MenuItem("Incognito Mode", on_toggle_incognito, checked=is_incognito_checked),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_exit)
    )

    icon = pystray.Icon("typetrace", image, "TypeTrace", menu)
    return icon

def main():
    # 0. Una sola istanza per volta
    instance_handle = acquire_single_instance()
    if instance_handle is None:
        print("TypeTrace e' gia' in esecuzione (controlla l'area di notifica).")
        return

    # 1. Run auto-configuration on startup
    utils.setup_first_run()

    # 2. Initialize local JSON database
    db = Database()
    db.start_autosave()

    # 3. Thread-safe queue for inter-thread communication
    event_queue = queue.Queue()

    # 4. Thread-safe callback to handle event communication between key hook and Tkinter
    def tracker_callback(event_type, val):
        event_queue.put((event_type, val))

    # 5. Initialize background key logger hook
    tracker = KeystrokeTracker(db, ui_update_callback=tracker_callback)
    tracker.start()

    # Pre-declare variable references for thread safe closures
    app = None
    icon = None
    shutting_down = False

    # 6. Handle shutdown pipeline
    def shutdown(tray_icon=None):
        # destroy() richiama close(), che richiama di nuovo closeEvent e quindi
        # questa stessa funzione: senza guardia la sequenza rientra in se' stessa.
        nonlocal shutting_down
        if shutting_down:
            return
        shutting_down = True

        print("Shutting down TypeTrace...")
        # Stop background key listener
        tracker.stop()
        # Write remaining in-memory statistics to JSON file
        db.stop_autosave()
        db.save_data()
        utils.shutdown_executor()
        # Shutdown system tray loop
        if tray_icon:
            tray_icon.stop()
        elif icon:
            icon.stop()
        # Close the GUI. Si usa quit() dell'applicazione Qt invece di sys.exit:
        # sollevare SystemExit da dentro uno slot lascia il ciclo eventi a meta'.
        try:
            app.close_application()
        except Exception:
            pass

    # 7. Initialize CustomTkinter interface with shutdown callback
    app = TypeTraceUI(db, tracker, shutdown_callback=shutdown)

    # 8. Start checking the event queue on the main thread
    app.process_event_queue(event_queue)

    # 9. Initialize and start pystray icon thread
    icon = create_tray_icon(tracker, event_queue)
    tray_thread = threading.Thread(target=icon.run)
    tray_thread.daemon = True
    tray_thread.start()

    # 10. Start main GUI event loop
    try:
        app.mainloop()
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()
