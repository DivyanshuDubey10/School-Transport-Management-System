import sys
from PyQt6.QtWidgets import QApplication
from ui.login import LoginWindow

def main():
    app = QApplication(sys.argv)
    
    # Load stylesheet
    try:
        with open("style.qss", "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Could not load stylesheet: {e}")

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()