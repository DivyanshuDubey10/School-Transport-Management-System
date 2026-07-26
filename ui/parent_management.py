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
        title_label = QLabel("Parent Management")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #38BDF8;")
        main_layout.addWidget(title_label)

        # Form Container (Card)
        form_frame = QFrame()
        form_frame.setObjectName("cardFrame")
        form_frame.setFixedWidth(660)
        
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(32, 32, 32, 32)
        form_layout.setHorizontalSpacing(24)
        form_layout.setVerticalSpacing(20)
        form_layout.setColumnStretch(0, 1)
        form_layout.setColumnStretch(1, 1)

        form_title = QLabel("Add New Parent")
        form_title.setStyleSheet("font-size: 15pt; font-weight: bold; color: #F8FAFC; margin-bottom: 10px;")
        form_layout.addWidget(form_title, 0, 0, 1, 2)

        def create_field(label_text, widget):
            field_layout = QVBoxLayout()
            field_layout.setSpacing(6)
            field_layout.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 10pt; font-weight: 600; color: #94A3B8;")
            field_layout.addWidget(lbl)
            field_layout.addWidget(widget)
            return field_layout

        # Row 1: Name and Phone
        self.parent_name_entry = QLineEdit()
        self.parent_name_entry.setPlaceholderText("Enter Parent Name")
        form_layout.addLayout(create_field("Parent Name", self.parent_name_entry), 1, 0)

        self.phone_entry = QLineEdit()
        self.phone_entry.setPlaceholderText("Enter Phone Number")
        form_layout.addLayout(create_field("Phone Number", self.phone_entry), 1, 1)

        # Row 2: Username and Password
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Enter Username")
        form_layout.addLayout(create_field("Username", self.username_entry), 2, 0)

        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Enter Password")
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addLayout(create_field("Password", self.password_entry), 2, 1)

        # Row 3: Address and Pickup Point
        self.address_entry = QLineEdit()
        self.address_entry.setPlaceholderText("Enter Address")
        form_layout.addLayout(create_field("Address", self.address_entry), 3, 0)

        self.pickup_entry = QLineEdit()
        self.pickup_entry.setPlaceholderText("Enter Pickup Point")
        form_layout.addLayout(create_field("Pickup Point", self.pickup_entry), 3, 1)

        # Save Button
        self.save_button = QPushButton("Save Parent")
        self.save_button.setFixedWidth(200)
        self.save_button.clicked.connect(self.save_parent)
        form_layout.addWidget(self.save_button, 4, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        # Center Layout for Form (Horizontal and Vertical)
        h_center_layout = QHBoxLayout()
        h_center_layout.addStretch()
        h_center_layout.addWidget(form_frame)
        h_center_layout.addStretch()

        v_center_layout = QVBoxLayout()
        v_center_layout.addStretch()
        v_center_layout.addLayout(h_center_layout)
        v_center_layout.addStretch()
        
        main_layout.addLayout(v_center_layout)
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