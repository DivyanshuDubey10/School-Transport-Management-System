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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Add New Bus")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Bus Number
        self.bus_number_entry = QLineEdit()
        self.bus_number_entry.setPlaceholderText("Enter Bus Number")
        self.bus_number_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Bus Number"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.bus_number_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Driver Name
        self.driver_name_entry = QLineEdit()
        self.driver_name_entry.setPlaceholderText("Enter Driver Name")
        self.driver_name_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Driver Name"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.driver_name_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Driver Phone
        self.driver_phone_entry = QLineEdit()
        self.driver_phone_entry.setPlaceholderText("Enter Driver Phone")
        self.driver_phone_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Driver Phone"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.driver_phone_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Capacity
        self.capacity_entry = QLineEdit()
        self.capacity_entry.setPlaceholderText("Enter Bus Capacity")
        self.capacity_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Capacity"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.capacity_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        # Route Assignment
        self.route_dropdown = QComboBox()
        self.route_dropdown.addItems(self.route_options)
        self.route_dropdown.setFixedWidth(300)
        form_layout.addWidget(QLabel("Assign Route"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.route_dropdown, alignment=Qt.AlignmentFlag.AlignCenter)

        # Save Button
        save_button = QPushButton("Save Bus")
        save_button.setFixedWidth(150)
        save_button.clicked.connect(self.save_bus)
        form_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(form_layout)
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
