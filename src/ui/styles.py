DARK_STYLESHEET = """
QMainWindow {
    background-color: #1E1E1E;
}

QWidget {
    color: #CCCCCC;
    font-family: 'Segoe UI', 'San Francisco', 'Helvetica', 'Arial', sans-serif;
    font-size: 13px;
}

/* Splitter Handle */
QSplitter::handle {
    background-color: #2D2D2D;
    width: 2px;
}

/* List/Tree Views (Toolbox) */
QListWidget, QTreeWidget {
    background-color: #252526;
    border: none;
    color: #CCCCCC;
}

QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #37373D;
    color: white;
}

QListWidget::item:hover {
    background-color: #2A2D2E;
}

/* Graphics View (Canvas) */
QGraphicsView {
    background-color: #1E1E1E; /* Infinite canvas grid will be drawn over this */
    border: none;
}

/* Labels */
QLabel {
    color: #CCCCCC;
}

/* Header Labels */
QLabel#Header {
    font-weight: bold;
    color: #BBBBBB;
    padding: 5px;
    background-color: #252526;
}

/* Buttons */
QPushButton {
    background-color: #0E639C;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 2px;
}

QPushButton:hover {
    background-color: #1177BB;
}

QPushButton:pressed {
    background-color: #094771;
}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
    background-color: #3C3C3C;
    border: 1px solid #3C3C3C;
    color: #CCCCCC;
    padding: 4px;
    border-radius: 2px;
}

QLineEdit:focus {
    border: 1px solid #007ACC;
}
"""
