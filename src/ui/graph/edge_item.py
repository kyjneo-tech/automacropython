from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QBrush, QPen, QColor, QPainterPath

class EdgeItem(QGraphicsPathItem):
    """
    Draws a Bezier curve between two nodes (Source Output -> Target Input).
    Tracks nodes to update automatically on move.
    """
    def __init__(self, source_item, target_item):
        super().__init__()
        self.setZValue(-1) # Behind nodes
        self.setFlag(QGraphicsPathItem.ItemIsSelectable)
        
        self.source_item = source_item
        self.target_item = target_item
        self.source_node_id = source_item.node_id
        
        # Style
        self._pen = QPen(QColor("#AAAAAA"))
        self._pen.setWidth(2)
        
        self._selected_pen = QPen(QColor("#00FFcc"))
        self._selected_pen.setWidth(4)
        
        self.setPen(self._pen)
        
        self.adjust()
        
    def adjust(self):
        """Update path based on current node positions."""
        if not self.source_item or not self.target_item:
            return
            
        # Source Output: Bottom Center
        start = self.source_item.scenePos() + QPointF(self.source_item.width/2, self.source_item.height)
        # Target Input: Top Center
        end = self.target_item.scenePos() + QPointF(self.target_item.width/2, 0)
        
        path = QPainterPath()
        path.moveTo(start)
        
        # Control Points for Vertical Cubic Bezier
        dy = end.y() - start.y()
        
        curvature = max(abs(dy) * 0.5, 50) 
        
        ctrl1 = QPointF(start.x(), start.y() + curvature)
        ctrl2 = QPointF(end.x(), end.y() - curvature)
            
        path.cubicTo(ctrl1, ctrl2, end)
        self.setPath(path)
        
    def paint(self, painter, option, widget):
        if self.isSelected():
            painter.setPen(self._selected_pen)
        else:
            painter.setPen(self._pen)
        
        painter.drawPath(self.path())
