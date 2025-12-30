from PySide6.QtWidgets import QWidget, QApplication, QRubberBand
from PySide6.QtCore import Qt, QRect, Signal, QPoint
from PySide6.QtGui import QPainter, QColor, QScreen, QPixmap
import uuid
import os

class SnippingToolOverlay(QWidget):
    capture_done = Signal(str) # Path

    def __init__(self, screen: QScreen, on_capture_callback):
        super().__init__()
        self.screen = screen
        self.on_capture_callback = on_capture_callback
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # Geometry
        geo = screen.geometry()
        self.setGeometry(geo)
        
        self.rubberband = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.is_selecting = False
        
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100)) # Dim background

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberband.setGeometry(QRect(self.origin, self.origin).normalized()) # Fixed: Pass Rect directly
            self.rubberband.show()
            self.is_selecting = True

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.rubberband.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = False
            rect = self.rubberband.geometry()
            
            if rect.width() > 10 and rect.height() > 10:
                self.hide() 
                global_top_left = self.mapToGlobal(rect.topLeft())
                # Pass self.screen explicitly
                self.on_capture_callback(self.screen, global_top_left.x(), global_top_left.y(), rect.width(), rect.height())
                self.close()
            else:
                self.rubberband.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

class SnippingTool(QWidget):
    image_captured = Signal(str)

    def __init__(self):
        super().__init__()
        self.overlays = []
        self._setup_overlays()
        
    def _setup_overlays(self):
        for screen in QApplication.screens():
            overlay = SnippingToolOverlay(screen, self._on_capture)
            self.overlays.append(overlay)
            
    def _on_capture(self, target_screen, x, y, w, h):
        # Close all overlays
        for ov in self.overlays:
            div = ov 
            ov.close()
        self.overlays.clear()
        
        # Local coords in screen (Logical)
        screen_geo = target_screen.geometry()
        local_x = x - screen_geo.x()
        local_y = y - screen_geo.y()
        
        # Device Pixel Ratio (e.g. 2.0 for Retina)
        dpr = target_screen.devicePixelRatio()
        
        # Grab FULL screen (Physical Pixels)
        # grabWindow(0) is the most reliable way to get the screen content
        full_pixmap = target_screen.grabWindow(0)
        
        # Scale Coordinates to Physical
        phy_x = int(local_x * dpr)
        phy_y = int(local_y * dpr)
        phy_w = int(w * dpr)
        phy_h = int(h * dpr)
        
        # Crop
        pixmap = full_pixmap.copy(phy_x, phy_y, phy_w, phy_h)
        
        # Save
        if not os.path.exists("assets"):
             os.makedirs("assets")
             
        filename = f"assets/capture_{uuid.uuid4().hex[:8]}.png"
        pixmap.save(filename)
        
        self.image_captured.emit(os.path.abspath(filename))
