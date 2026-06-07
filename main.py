import os
import sys
import threading
import queue
import pystray
from PIL import Image, ImageDraw
import logging

# Ensure script directory is on the path for clean imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Logging to file "typetrace.log" in the project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(project_dir, "typetrace.log")

logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    level=logging.ERROR
)

def global_excepthook(exctype, value, traceback):
    logging.critical("Captured unhandled global crash exception:", exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)

sys.excepthook = global_excepthook

from database import Database
from tracker import KeystrokeTracker
from ui import TypeTraceUI
import utils

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
    # 0. Run auto-configuration on startup
    utils.setup_first_run()
    
    # 1. Initialize local JSON database
    db = Database()
    
    # 2. Thread-safe queue for inter-thread communication
    event_queue = queue.Queue()
    
    # 3. Thread-safe callback to handle event communication between key hook and Tkinter
    def tracker_callback(event_type, val):
        event_queue.put((event_type, val))

    # 4. Initialize background key logger hook
    tracker = KeystrokeTracker(db, ui_update_callback=tracker_callback)
    tracker.start()
    
    # Pre-declare variable references for thread safe closures
    app = None
    icon = None
    
    # 5. Handle shutdown pipeline
    def shutdown(tray_icon=None):
        print("Shutting down TypeTrace...")
        # Stop background key listener
        tracker.stop()
        # Write remaining in-memory statistics to JSON file
        db.save_data()
        # Shutdown system tray loop
        if tray_icon:
            tray_icon.stop()
        elif icon:
            icon.stop()
        # Destroy GUI loop
        try:
            app.destroy()
        except Exception:
            pass
        sys.exit(0)

    # 6. Initialize CustomTkinter interface with shutdown callback
    app = TypeTraceUI(db, tracker, shutdown_callback=shutdown)
    
    # 7. Start checking the event queue on the main thread
    app.process_event_queue(event_queue)

    # 8. Initialize and start pystray icon thread
    icon = create_tray_icon(tracker, event_queue)
    tray_thread = threading.Thread(target=icon.run)
    tray_thread.daemon = True
    tray_thread.start()
    
    # 9. Start main GUI event loop
    try:
        app.mainloop()
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()
