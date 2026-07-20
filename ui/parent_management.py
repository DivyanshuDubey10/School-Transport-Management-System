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
        from PyQt6.QtWidgets import QGridLayout, QFrame
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title
        title_label = QLabel("👨‍👩‍👧‍👦 Parent Management")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #89B4FA;")
        main_layout.addWidget(title_label)

        # Main Container to center the form
        center_layout = QHBoxLayout()
        
        # Form Container (Card)
        form_frame = QFrame()
        form_frame.setObjectName("cardFrame")
        form_frame.setMinimumWidth(650)
        
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        form_title = QLabel("Add New Parent")
        form_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        form_layout.addWidget(form_title, 0, 0, 1, 4)

        # Row 1: Name and Phone
        self.parent_name_entry = QLineEdit()
        self.parent_name_entry.setPlaceholderText("Enter Parent Name")
        form_layout.addWidget(QLabel("Parent Name:"), 1, 0)
        form_layout.addWidget(self.parent_name_entry, 1, 1)

        self.phone_entry = QLineEdit()
        self.phone_entry.setPlaceholderText("Enter Phone Number")
        form_layout.addWidget(QLabel("Phone Number:"), 1, 2)
        form_layout.addWidget(self.phone_entry, 1, 3)

        # Row 2: Username and Password
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Enter Username")
        form_layout.addWidget(QLabel("Username:"), 2, 0)
        form_layout.addWidget(self.username_entry, 2, 1)

        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Enter Password")
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(QLabel("Password:"), 2, 2)
        form_layout.addWidget(self.password_entry, 2, 3)

        # Row 3: Address and Pickup Point
        self.address_entry = QLineEdit()
        self.address_entry.setPlaceholderText("Enter Address")
        form_layout.addWidget(QLabel("Address:"), 3, 0)
        form_layout.addWidget(self.address_entry, 3, 1)

        self.pickup_entry = QLineEdit()
        self.pickup_entry.setPlaceholderText("Enter Pickup Point")
        form_layout.addWidget(QLabel("Pickup Point:"), 3, 2)
        form_layout.addWidget(self.pickup_entry, 3, 3)

        # Save Button
        self.save_button = QPushButton("💾 Save Parent")
        self.save_button.setFixedWidth(200)
        self.save_button.clicked.connect(self.save_parent)
        form_layout.addWidget(self.save_button, 4, 0, 1, 4, Qt.AlignmentFlag.AlignCenter)
        
        center_layout.addStretch()
        center_layout.addWidget(form_frame)
        center_layout.addStretch()
        
        main_layout.addLayout(center_layout)
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