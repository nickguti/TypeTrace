import customtkinter
import tkinter as tk

class FloatingOverlay(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Configure Window
        self.title("TypeTrace Overlay")
        self.overrideredirect(True)      # Remove window decorations (borderless)
        self.attributes("-topmost", True)  # Always on top
        self.attributes("-alpha", 0.85)    # Slight transparency
        
        # Make #121212 transparent on Windows for custom-shaped HUD feel
        self.wm_attributes("-transparentcolor", "#121212")
        
        # Default positioning at top-middle of the screen
        screen_width = self.winfo_screenwidth()
        x = int(screen_width / 2) - 80
        y = 50
        self.geometry(f"160x65+{x}+{y}")
        
        # Frame container
        self.frame = customtkinter.CTkFrame(
            self, 
            fg_color="#121212", 
            border_color="#58a6ff", 
            border_width=1.5, 
            corner_radius=10
        )
        self.frame.pack(fill="both", expand=True)
        
        # Live Stats Labels
        self.apm_lbl = customtkinter.CTkLabel(
            self.frame, 
            text="APM: 0", 
            font=("Consolas", 14, "bold"), 
            text_color="#58a6ff"
        )
        self.apm_lbl.pack(pady=(10, 2))
        
        self.wpm_lbl = customtkinter.CTkLabel(
            self.frame, 
            text="WPM: 0", 
            font=("Consolas", 11), 
            text_color="#ffffff"
        )
        self.wpm_lbl.pack(pady=(0, 10))
        
        # Bind Drag events to all widgets for seamless positioning
        self.frame.bind("<Button-1>", self.start_drag)
        self.frame.bind("<B1-Motion>", self.drag)
        self.apm_lbl.bind("<Button-1>", self.start_drag)
        self.apm_lbl.bind("<B1-Motion>", self.drag)
        self.wpm_lbl.bind("<Button-1>", self.start_drag)
        self.wpm_lbl.bind("<B1-Motion>", self.drag)
        
        self.drag_x = 0
        self.drag_y = 0
        
    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
        
    def drag(self, event):
        x = self.winfo_pointerx() - self.drag_x
        y = self.winfo_pointery() - self.drag_y
        self.geometry(f"+{x}+{y}")
        
    def update_stats(self, apm, wpm):
        """Update displayed APM and WPM statistics."""
        try:
            self.apm_lbl.configure(text=f"APM: {apm}")
            self.wpm_lbl.configure(text=f"WPM: {wpm}")
        except Exception:
            pass # Handle window destruction during update
