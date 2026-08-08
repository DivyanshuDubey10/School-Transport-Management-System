import sys
from PyQt6.QtWidgets import QApplication
from ui.login import LoginWindow
from theme_manager import ThemeManager

def main():
    app = QApplication(sys.argv)
    
    # Initialize and apply default theme
    theme_manager = ThemeManager.get_instance()
    theme_manager.apply_theme()

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()