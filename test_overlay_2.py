import sys
from PyQt6.QtWidgets import QApplication
from overlay import FloatingOverlay

app = QApplication(sys.argv)
overlay = FloatingOverlay()
print("Screen before show:", overlay.screen())
overlay.show()
print("Screen after show:", overlay.screen())
print("Position:", overlay.pos())
sys.exit(0)
