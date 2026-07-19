from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ParentManagement(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.create_widgets()
    
    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Parent Management")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Name
        self.parent_name_entry = QLineEdit()
        self.parent_name_entry.setPlaceholderText("Enter Parent Name")
        self.parent_name_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Parent Name"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.parent_name_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Username
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Enter Username")
        self.username_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Username"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.username_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Password
        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Enter Password")
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Password"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.password_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Phone
        self.phone_entry = QLineEdit()
        self.phone_entry.setPlaceholderText("Enter Phone Number")
        self.phone_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Phone Number"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.phone_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Address
        self.address_entry = QLineEdit()
        self.address_entry.setPlaceholderText("Enter Address")
        self.address_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Address"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.address_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Pickup
        self.pickup_entry = QLineEdit()
        self.pickup_entry.setPlaceholderText("Enter Pickup Point")
        self.pickup_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Pickup Point"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.pickup_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Save Button
        save_button = QPushButton("Save Parent")
        save_button.setFixedWidth(150)
        save_button.clicked.connect(self.save_parent)
        form_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()

    def save_parent(self):
        parent_name = self.parent_name_entry.text().strip()
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()
        phone = self.phone_entry.text().strip()
        address = self.address_entry.text().strip()
        pickup_point = self.pickup_entry.text().strip()

        if not all([parent_name, username, password, phone, address, pickup_point]):
            QMessageBox.critical(self, "Error", "All fields are required.")
            return
            
        import security
        hashed_pw = security.hash_password(password)
        
        from dal import db_dal
        
        try:
            success = db_dal.add_parent(parent_name, phone, address, pickup_point, username, hashed_pw)
            if success:
                QMessageBox.information(self, "Success", "Parent information saved successfully.")
                self.parent_name_entry.clear()
                self.username_entry.clear()
                self.password_entry.clear()
                self.phone_entry.clear()
                self.address_entry.clear()
                self.pickup_entry.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")