import sys
import os
# Ensure project root is in sys.path so 'src' module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtWidgets import QApplication
from src.state.store import Store
from src.ui.main_window import MainWindow
from src.ui.styles import DARK_STYLESHEET

def main():
    app = QApplication(sys.argv)
    
    # Apply Theme
    app.setStyleSheet(DARK_STYLESHEET)
    
    # Initialize Store
    store = Store()
    
    # Create Window
    window = MainWindow(store)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
