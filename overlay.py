from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent

class FloatingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(None) # Independent top-level window
        
        self.setWindowTitle("TypeTrace Overlay")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setWindowOpacity(0.85)
        self.resize(160, 65)
        
        # Default positioning at top-middle of the screen
        if self.screen():
            screen = self.screen().availableGeometry()
            x = int(screen.width() / 2) - 80
            y = 50
            self.move(x, y)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = QFrame(self)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #121212;
                border: 1.5px solid #58a6ff;
                border-radius: 10px;
            }
        """)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(2)
        
        self.apm_lbl = QLabel("APM: 0")
        self.apm_lbl.setStyleSheet("color: #58a6ff; font-family: Consolas; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        self.apm_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.apm_lbl)
        
        self.wpm_lbl = QLabel("WPM: 0")
        self.wpm_lbl.setStyleSheet("color: #ffffff; font-family: Consolas; font-size: 11px; border: none; background: transparent;")
        self.wpm_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.wpm_lbl)
        
        layout.addWidget(self.frame)
        
        self.drag_position = QPoint()
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def update_stats(self, apm, wpm):
        try:
            self.apm_lbl.setText(f"APM: {apm}")
            self.wpm_lbl.setText(f"WPM: {wpm}")
        except Exception:
            pass
