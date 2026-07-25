from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BusManagement(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.fetch_routes()
        self.create_widgets()
        
    def fetch_routes(self):
        from dal import db_dal
        routes = db_dal.get_all_routes()
        self.route_options = [f"{row[0]} - {row[1]}" for row in routes]
        if not self.route_options: self.route_options = [""]
    
    def create_widgets(self):
        from PyQt6.QtWidgets import QGridLayout, QFrame
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title
        title_label = QLabel("Bus Management")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #38BDF8;")
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
        form_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC; margin-bottom: 10px;")
        form_layout.addWidget(form_title, 0, 0, 1, 2)

        def create_field(label_text, widget):
            field_layout = QVBoxLayout()
            field_layout.setSpacing(6)
            field_layout.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #94A3B8;")
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

        # Row 3: Route Assignment (spanning both columns for a full-width clean look)
        self.route_dropdown = QComboBox()
        self.route_dropdown.addItems(self.route_options)
        form_layout.addLayout(create_field("Assign Route", self.route_dropdown), 3, 0, 1, 2)

        # Save Button
        self.save_button = QPushButton("Save Bus")
        self.save_button.setFixedWidth(200)
        self.save_button.clicked.connect(self.save_bus)
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

    def save_bus(self):
        bus_number = self.bus_number_entry.text().strip()
        driver_name = self.driver_name_entry.text().strip()
        driver_phone = self.driver_phone_entry.text().strip()
        capacity_str = self.capacity_entry.text().strip()
        route_selection = self.route_dropdown.currentText()
        route_id = route_selection.split(" - ")[0] if " - " in route_selection else ""
        
        if not bus_number:
            QMessageBox.critical(self, "Error", "Bus Number is required.")
            return
            
        if not driver_name:
            QMessageBox.critical(self, "Error", "Driver Name is required.")
            return
            
        if not driver_phone:
            QMessageBox.critical(self, "Error", "Driver Phone is required.")
            return
            
        if not capacity_str:
            QMessageBox.critical(self, "Error", "Capacity is required.")
            return
            
        try:
            capacity = int(capacity_str)
        except ValueError:
            QMessageBox.critical(self, "Error", "Capacity must be a valid number.")
            return

        from dal import db_dal
        
        try:
            success = db_dal.add_bus(bus_number, driver_name, driver_phone, capacity, route_id if route_id else None)
            if success:
                QMessageBox.information(self, "Success", "Bus saved successfully.")
                
                self.bus_number_entry.clear()
                self.driver_name_entry.clear()
                self.driver_phone_entry.clear()
                self.capacity_entry.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
