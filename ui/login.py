from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox, QFrame, QApplication
from PyQt6.QtCore import Qt
from ui.admin_dashboard import AdminDashboard
from ui.parent_dashboard import ParentDashboard
from ui.components.custom_title_bar import CustomTitleBar
from ui.components.toast import ToastNotification
from ui.components.toggle_switch import ToggleSwitch

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeoYatra Transport Portal")
        self.setFixedSize(900, 600)
        self.create_widgets()

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login Frame
        self.login_frame = QFrame()
        self.login_frame.setFixedSize(480, 460)
        self.login_frame.setObjectName("loginFrame")
        
        frame_layout = QVBoxLayout(self.login_frame)
        frame_layout.setContentsMargins(40, 40, 40, 40)
        frame_layout.setSpacing(20)

        # Title
        self.title_label = QLabel("NeoYatra")
        self.title_label.setObjectName("pageTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.title_label)

        # Inline Alert Box (Hidden initially)
        self.alert_label = QLabel("")
        self.alert_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alert_label.setVisible(False)
        frame_layout.addWidget(self.alert_label)

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
        show_pwd_layout = QHBoxLayout()
        self.show_password_cb = ToggleSwitch()
        self.show_password_cb.stateChanged.connect(self.toggle_password_visibility)
        lbl_show = QLabel("Show Password")
        lbl_show.setObjectName("userLabel") # maps to secondary text color
        show_pwd_layout.addWidget(self.show_password_cb)
        show_pwd_layout.addWidget(lbl_show)
        show_pwd_layout.addStretch()
        frame_layout.addLayout(show_pwd_layout)

        # Spacer
        frame_layout.addStretch()

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.login)
        self.login_button.setMinimumHeight(40)
        frame_layout.addWidget(self.login_button)

        center_layout.addWidget(self.login_frame)
        main_layout.addLayout(center_layout)

    def toggle_password_visibility(self, state):
        if self.show_password_cb.isChecked():
            self.password_entry.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)

    def show_alert(self, message, type="error"):
        self.alert_label.setText(message)
        if type == "error":
            self.alert_label
        else:
            self.alert_label
        self.alert_label.setVisible(True)

    def login(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()

        from dal import db_dal
        import security

        # Check Admin first
        admin = db_dal.get_admin_by_username(username)
        if admin and security.verify_password(password, admin[2]):
            self.show_alert("Login Successful as Admin!", "success")
            self.dashboard = AdminDashboard()
            self.dashboard.show()
            self.close()
            return

        # Check Parent
        parent = db_dal.get_parent_by_username(username)
        if parent and security.verify_password(password, parent[6]):
            self.show_alert(f"Welcome back, {parent[1]}!", "success")
            parent_id = parent[0]
            self.dashboard = ParentDashboard(parent_id)
            self.dashboard.show()
            self.close()
            return

        # Check Driver
        driver = db_dal.get_driver_by_username(username)
        if driver and driver[7] and security.verify_password(password, driver[7]):
            self.show_alert(f"Welcome Driver {driver[2]}!", "success")
            bus_id = driver[0]
            from ui.driver_dashboard import DriverDashboard
            self.dashboard = DriverDashboard(bus_id)
            self.dashboard.show()
            self.close()
            return

        self.show_alert("⚠ Invalid username or password.", "error")
