from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox, QFrame, QApplication
from PyQt6.QtCore import Qt
from ui.admin_dashboard import AdminDashboard
from ui.parent_dashboard import ParentDashboard

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("School Transport Management System")
        self.setFixedSize(900, 600)
        self.create_widgets()

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login Frame
        self.login_frame = QFrame()
        self.login_frame.setFixedSize(500, 450)
        self.login_frame.setObjectName("loginFrame")
        self.login_frame.setStyleSheet("QFrame#loginFrame { background-color: #333333; border-radius: 10px; border: 1px solid #444444; }")
        
        frame_layout = QVBoxLayout(self.login_frame)
        frame_layout.setContentsMargins(40, 40, 40, 40)
        frame_layout.setSpacing(20)

        # Title
        self.title_label = QLabel("School Transport System")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.title_label)

        # Username
        self.username_label = QLabel("Username")
        frame_layout.addWidget(self.username_label)
        
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Enter username")
        frame_layout.addWidget(self.username_entry)

        # Password
        self.password_label = QLabel("Password")
        frame_layout.addWidget(self.password_label)

        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Enter password")
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        frame_layout.addWidget(self.password_entry)

        # Show Password
        self.show_password_cb = QCheckBox("Show Password")
        self.show_password_cb.stateChanged.connect(self.toggle_password_visibility)
        frame_layout.addWidget(self.show_password_cb)

        # Spacer
        frame_layout.addStretch()

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.login)
        self.login_button.setMinimumHeight(40)
        frame_layout.addWidget(self.login_button)

        main_layout.addWidget(self.login_frame)

    def toggle_password_visibility(self, state):
        if self.show_password_cb.isChecked():
            self.password_entry.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)

    def login(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()

        from dal import db_dal
        import security

        # Check Admin first
        admin = db_dal.get_admin_by_username(username)
        if admin and security.verify_password(password, admin[2]):
            QMessageBox.information(self, "Success", "Login Successful as Admin!")
            self.dashboard = AdminDashboard()
            self.dashboard.show()
            self.close()
            return

        # Check Parent
        parent = db_dal.get_parent_by_username(username)
        if parent and security.verify_password(password, parent[6]):
            QMessageBox.information(self, "Success", f"Welcome back, {parent[1]}!")
            parent_id = parent[0]
            self.dashboard = ParentDashboard(parent_id)
            self.dashboard.show()
            self.close()
            return

        QMessageBox.critical(self, "Error", "Invalid username or password.")
