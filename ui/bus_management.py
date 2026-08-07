from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BusManagement(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.fetch_points()
        self.create_widgets()
        
    def fetch_points(self):
        from dal import db_dal
        self.point_options = db_dal.get_all_pickup_points()
        if not self.point_options: self.point_options = ["Main Campus", "North Station", "South Station", "East Gate", "West End"]
    
    def create_widgets(self):
        from PyQt6.QtWidgets import QGridLayout, QFrame
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title
        title_label = QLabel("Bus Management")
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

        form_title = QLabel("Add New Bus")
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

        # Row 1: Bus Number & Capacity
        self.bus_number_entry = QLineEdit()
        self.bus_number_entry.setPlaceholderText("Enter Bus Number")
        form_layout.addLayout(create_field("Bus Number", self.bus_number_entry), 1, 0)

        self.capacity_entry = QLineEdit()
        self.capacity_entry.setPlaceholderText("Enter Bus Capacity")
        form_layout.addLayout(create_field("Capacity", self.capacity_entry), 1, 1)

        # Row 2: Driver Name & Phone
        self.driver_name_entry = QLineEdit()
        self.driver_name_entry.setPlaceholderText("Enter Driver Name")
        form_layout.addLayout(create_field("Driver Name", self.driver_name_entry), 2, 0)

        self.driver_phone_entry = QLineEdit()
        self.driver_phone_entry.setPlaceholderText("Enter Driver Phone")
        form_layout.addLayout(create_field("Driver Phone", self.driver_phone_entry), 2, 1)

        # Row 3: Driver Login Credentials
        self.driver_username_entry = QLineEdit()
        self.driver_username_entry.setPlaceholderText("Driver Login Username")
        form_layout.addLayout(create_field("Driver Username", self.driver_username_entry), 3, 0)

        self.driver_password_entry = QLineEdit()
        self.driver_password_entry.setPlaceholderText("Driver Login Password")
        self.driver_password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addLayout(create_field("Driver Password", self.driver_password_entry), 3, 1)

        # Row 4: Route Starting and Ending Points (Editable Dropdowns)
        self.start_point_dropdown = QComboBox()
        self.start_point_dropdown.setEditable(True)
        self.start_point_dropdown.addItems(self.point_options)
        self.start_point_dropdown.setPlaceholderText("Select or type starting point")
        form_layout.addLayout(create_field("Route Starting Point", self.start_point_dropdown), 4, 0)

        self.end_point_dropdown = QComboBox()
        self.end_point_dropdown.setEditable(True)
        self.end_point_dropdown.addItems(self.point_options)
        self.end_point_dropdown.setPlaceholderText("Select or type ending point")
        form_layout.addLayout(create_field("Route Ending Point", self.end_point_dropdown), 4, 1)

        # Save Button
        self.save_button = QPushButton("Save Bus")
        self.save_button.setFixedWidth(200)
        self.save_button.clicked.connect(self.save_bus)
        form_layout.addWidget(self.save_button, 5, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
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

    def save_bus(self):
        bus_number = self.bus_number_entry.text().strip()
        driver_name = self.driver_name_entry.text().strip()
        driver_phone = self.driver_phone_entry.text().strip()
        capacity_str = self.capacity_entry.text().strip()
        username = self.driver_username_entry.text().strip()
        password = self.driver_password_entry.text().strip()
        start_point = self.start_point_dropdown.currentText().strip()
        end_point = self.end_point_dropdown.currentText().strip()
        
        if not bus_number or not driver_name or not driver_phone or not capacity_str or not start_point or not end_point:
            QMessageBox.critical(self, "Error", "All fields except credentials are required.")
            return

        if start_point.lower() == end_point.lower():
            QMessageBox.critical(self, "Error", "Starting Point and Ending Point cannot be the same.")
            return

        try:
            capacity = int(capacity_str)
        except ValueError:
            QMessageBox.critical(self, "Error", "Capacity must be a valid number.")
            return

        route_name = f"{start_point} to {end_point}"

        from dal import db_dal
        
        try:
            route_id = db_dal.get_or_create_route(route_name)
            success = db_dal.add_bus(bus_number, driver_name, driver_phone, capacity, route_id, username, password)
            if success:
                QMessageBox.information(self, "Success", "Bus and route assigned successfully.")
                
                self.bus_number_entry.clear()
                self.driver_name_entry.clear()
                self.driver_phone_entry.clear()
                self.capacity_entry.clear()
                self.driver_username_entry.clear()
                self.driver_password_entry.clear()
                self.start_point_dropdown.setCurrentIndex(0)
                self.end_point_dropdown.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
