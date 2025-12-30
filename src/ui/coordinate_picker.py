from PySide6.QtWidgets import QWidget, QLabel, QApplication
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QCursor

class CoordinatePickerOverlay(QWidget):
    """
    transparent overlay for a SINGLE screen.
    """
    def __init__(self, screen, manager):
        super().__init__()
        self.manager = manager
        self.screen_geo = screen.geometry()
        
        # Window setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        
        # Set geometry to cover this specific screen
        self.setGeometry(self.screen_geo)
        
        # Label (will move)
        self.label = QLabel(self)
        self.label.setStyleSheet("""
            background-color: rgba(30, 30, 30, 0.8);
            color: #00FFcc;
            border: 1px solid #00FFcc;
            border-radius: 4px;
            padding: 5px;
            font-weight: bold;
        """)
        self.label.setText(f"Screen: {screen.name()}")
        self.label.adjustSize()
        
    def mouseMoveEvent(self, event):
        # Global position is what we want
        pos = event.globalPosition().toPoint()
        
        # Local pos for label placement relative to this widget
        local_pos = event.pos()
        
        self.label.setText(f"X: {pos.x()}, Y: {pos.y()}")
        self.label.adjustSize()
        
        # Keep label on screen
        lx = local_pos.x() + 20
        ly = local_pos.y() + 20
        
        # Simple boundary check
        if lx + self.label.width() > self.width():
            lx -= (self.label.width() + 40)
        if ly + self.label.height() > self.height():
            ly -= (self.label.height() + 40)
            
        self.label.move(lx, ly)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.globalPosition().toPoint()
            self.manager.notify_picked(pos.x(), pos.y())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.manager.notify_cancelled()

class CoordinatePicker(QObject):
    coords_picked = Signal(int, int)
    
    def __init__(self):
        super().__init__()
        self.overlays = []
        
    def show(self):
        # Create an overlay for every screen
        screens = QApplication.screens()
        for screen in screens:
            overlay = CoordinatePickerOverlay(screen, self)
            overlay.show()
            self.overlays.append(overlay)
            
    def notify_picked(self, x, y):
        self.coords_picked.emit(x, y)
        self.close_all()
        
    def notify_cancelled(self):
        self.close_all()
        
    def close_all(self):
        for overlay in self.overlays:
            overlay.close()
        self.overlays = []
