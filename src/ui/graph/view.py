from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QBrush, QPen, QColor, QWheelEvent, QMouseEvent, QPainterPath

class GraphView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None, on_drop_callback=None, on_connect_callback=None):
        super().__init__(scene, parent)
        self.on_drop_callback = on_drop_callback
        self.on_connect_callback = on_connect_callback
        
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True) # Enable Drop
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Pan/Zoom State
        self._is_panning = False
        self._pan_start = QPointF(0, 0)
        
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        # Draw Dark Background
        painter.fillRect(rect, QColor("#1E1E1E"))
        
        # Draw Grid (100px major, 20px minor)
        left = int(rect.left()) - (int(rect.left()) % 20)
        top = int(rect.top()) - (int(rect.top()) % 20)
        
        # Draw Minor Grid
        grid_pen = QPen(QColor("#2D2D2D"))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        
        # Draw huge grid covering viewport
        # Simplified: Draw lines
        # (For production, optimize loops)
        
        # A simpler way is to use a texture pattern, but drawing lines is fine for now
        # Actually, let's just make a simple dot grid or line grid
        
        # Grid Size = 40
        grid_size = 40
        
        lines = []
        # Vertical lines
        x = left
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += grid_size
            
        # Horizontal lines
        y = top
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += grid_size

    def wheelEvent(self, event: QWheelEvent):
        # Zoom Logic
        zoom_in = event.angleDelta().y() > 0
        factor = 1.1 if zoom_in else 0.9
        self.scale(factor, factor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self._is_panning = True
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().keyPressEvent(event)
        
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self._is_panning = False
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super().keyReleaseEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasText() and self.on_drop_callback:
            # Get Drop Position in Scene Coordinates
            drop_pos = self.mapToScene(event.position().toPoint())
            action_type_str = event.mimeData().text()
            self.on_drop_callback(action_type_str, drop_pos.x(), drop_pos.y())
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
            
    # Linking Interaction
    
    def mousePressEvent(self, event: QMouseEvent):
        # Middle Button Panning
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._pan_start = event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return

        # Check if clicking on port
        item = self.itemAt(event.position().toPoint())
        if item and item.data(0) == "port_out":
            self._is_linking = True
            self._link_start_node = item.data(1)
            self._link_start_pos = self.mapToScene(event.position().toPoint())
            
            # Create temp edge
            self._temp_edge = TempEdgeItem(self._link_start_pos, self._link_start_pos)
            self.scene().addItem(self._temp_edge)
            return
            
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            # Panning Logic
            delta = event.position().toPoint() - self._pan_start
            self._pan_start = event.position().toPoint()
            
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        if getattr(self, '_is_linking', False):
            # Update temp edge
            mouse_pos = self.mapToScene(event.position().toPoint())
            
            # --- SNAPPING LOGIC ---
            target_port = self._find_nearby_port(mouse_pos)
            if target_port:
                # Calculate center of port in scene coords
                port_center_local = target_port.rect().center()
                port_center_scene = target_port.mapToScene(port_center_local)
                mouse_pos = port_center_scene
            # ----------------------

            self._temp_edge.update_path(self._link_start_pos, mouse_pos)
            return
            
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton and self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return

        if getattr(self, '_is_linking', False):
            self._is_linking = False
            
            # Check drop target using Snapping Logic
            mouse_pos = self.mapToScene(event.position().toPoint())
            target_port = self._find_nearby_port(mouse_pos)
            
            target_node_id = None
            if target_port:
                target_node_id = target_port.data(1)
            
            print(f"DEBUG: Connection Drop Target: {target_node_id}")
            
            if target_node_id:
                print(f"DEBUG: Connecting to {target_node_id}")
                if hasattr(self, 'on_connect_callback') and self.on_connect_callback:
                    self.on_connect_callback(self._link_start_node, target_node_id)
            else:
                 print("DEBUG: No valid input port found nearby.")
            
            # Cleanup temp edge
            if self._temp_edge:
                try:
                    if self._temp_edge.scene() == self.scene():
                        self.scene().removeItem(self._temp_edge)
                except RuntimeError:
                    pass 
            self._temp_edge = None
            return
            
        super().mouseReleaseEvent(event)

    def _find_nearby_port(self, scene_pos: QPointF):
        """Find a valid input port near the given scene position."""
        snap_range = 40 # px radius
        search_rect = QRectF(scene_pos.x() - snap_range/2, scene_pos.y() - snap_range/2, snap_range, snap_range)
        nearby_items = self.scene().items(search_rect)
        
        for item in nearby_items:
            if item.data(0) == "port_in":
                # Prevent connecting to the source node itself (Loopback within same node usually not useful)
                if getattr(self, '_link_start_node', None) == item.data(1):
                    continue
                return item
        return None

# Helper Class for Dragging Visualization
class TempEdgeItem(QGraphicsPathItem):
    def __init__(self, start, end):
        super().__init__()
        self.setZValue(100) # Top
        self._pen = QPen(QColor("#00FFcc"))
        self._pen.setWidth(2)
        self._pen.setStyle(Qt.DashLine)
        self.setPen(self._pen)
        self.update_path(start, end)
        
    def update_path(self, start, end):
        path = QPainterPath()
        path.moveTo(start)
        
        # Simple curve
        dy = end.y() - start.y()
        curvature = max(abs(dy) * 0.5, 50) 
        
        ctrl1 = QPointF(start.x(), start.y() + curvature)
        ctrl2 = QPointF(end.x(), end.y() - curvature)
            
        path.cubicTo(ctrl1, ctrl2, end)
        self.setPath(path)
