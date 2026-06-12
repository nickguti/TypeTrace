import sys
from PyQt6.QtWidgets import QApplication
from overlay import FloatingOverlay

app = QApplication(sys.argv)
overlay = FloatingOverlay()
overlay.show()
sys.exit(app.exec())
