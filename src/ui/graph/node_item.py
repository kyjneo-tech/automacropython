from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QBrush, QPen, QColor, QFont, QPainterPath, QLinearGradient, QPolygonF

class NodeItem(QGraphicsItem):
    def __init__(self, node_data, on_select_callback=None, on_move_callback=None):
        super().__init__()
        self.node_id = node_data.id
        self.label_text = node_data.label
        self.type = node_data.type
        self.on_select_callback = on_select_callback
        self.on_move_callback = on_move_callback
        
        # Vertical Layout Dimensions
        self.width = 180
        self.height = 80
        self.setPos(node_data.x, node_data.y)
        
        # Flags
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # UI Properties (Tech Style)
        # Darker, higher contrast
        self._brush = QBrush(QColor("#1E1E1E"))
        self._pen = QPen(QColor("#333333"))
        self._pen.setWidth(1)
        self._selected_pen = QPen(QColor("#00FFcc")) # Cyan Neon for selection
        self._selected_pen.setWidth(3)
        
        self._font = QFont("Consolas", 10) # Monospace for tech feel
        self._font.setBold(True)
        
        # Ports (Interactive) - VERTICAL
        from PySide6.QtWidgets import QGraphicsRectItem
        
        # Ports (Interactive) - VERTICAL (Larger for easier connection)
        from PySide6.QtWidgets import QGraphicsRectItem
        
        # Input Port (Top Center)
        self.input_port = QGraphicsRectItem(self.width/2 - 10, -10, 20, 10, self) # 20x10
        self.input_port.setBrush(QBrush(QColor("#666666")))
        self.input_port.setPen(QPen(Qt.NoPen))
        self.input_port.setData(0, "port_in")
        self.input_port.setData(1, self.node_id)
        self.input_port.setZValue(1.0)
        
        # Output Port (Bottom Center)
        self.output_port = QGraphicsRectItem(self.width/2 - 10, self.height, 20, 10, self) # 20x10
        self.output_port.setBrush(QBrush(QColor("#AAAAAA")))
        self.output_port.setPen(QPen(Qt.NoPen))
        self.output_port.setData(0, "port_out")
        self.output_port.setData(1, self.node_id)
        self.output_port.setZValue(1.0)

        self.edges = []
        
    def add_edge(self, edge):
        self.edges.append(edge)

    def boundingRect(self):
        return QRectF(0, -10, self.width, self.height + 20)
        
    def paint(self, painter, option, widget):
        # 1. Main Body (Chamfered Rect)
        # Tech styling: Cut corners
        path = QPainterPath()
        w, h = self.width, self.height
        cut = 10
        
        # Polygon for chamfered edges
        from PySide6.QtCore import QPointF
        poly = [
            QPointF(0, cut), QPointF(cut, 0), # Top Left Cut
            QPointF(w - cut, 0), QPointF(w, cut), # Top Right Cut
            QPointF(w, h - cut), QPointF(w - cut, h), # Bottom Right Cut
            QPointF(cut, h), QPointF(0, h - cut), # Bottom Left Cut
            QPointF(0, cut)
        ]
        path.addPolygon(QPolygonF(poly))
        
        # Glow/Stroke
        if self.isSelected():
            painter.setPen(self._selected_pen)
            # Add simple glow effect by drawing twice? Or just thick pen.
        else:
            painter.setPen(self._pen)
            
        # Background
        gradient = QLinearGradient(0, 0, 0, self.height)
        gradient.setColorAt(0, QColor("#2D2D30"))
        gradient.setColorAt(1, QColor("#1E1E1E"))
        painter.setBrush(gradient)
        painter.drawPath(path)
        
        # 2. Tech Decor (Header Line)
        # Cyan strip at top instead of left
        painter.setPen(Qt.NoPen)
        from src.domain.actions import ActionType
        
        # Color code by type
        if self.type == ActionType.CLICK:
            painter.setBrush(QColor("#FF4081")) # Pink
        elif self.type == ActionType.KEYBOARD_INPUT:
            painter.setBrush(QColor("#00E676")) # Green
        elif self.type == ActionType.WAIT:
            painter.setBrush(QColor("#FFEA00")) # Yellow
        elif self.type == ActionType.IMAGE_MATCH:
            painter.setBrush(QColor("#2979FF")) # Blue
        else:
            painter.setBrush(QColor("#9E9E9E")) # Grey
            
        painter.drawRect(cut, 0, w - 2*cut, 4)
        
        # 3. Label
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(self._font)
        painter.drawText(QRectF(0, 0, self.width, self.height), Qt.AlignCenter, self.label_text)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            if self.on_select_callback:
                if value: # Selected
                    self.on_select_callback(self.node_id)
                else: # Deselected
                    pass
        
        if change == QGraphicsItem.ItemPositionHasChanged:
            if self.on_move_callback:
                self.on_move_callback(self.node_id, self.x(), self.y())
            # Update connected edges
            for edge in self.edges:
                edge.adjust()
                
        return super().itemChange(change, value)
