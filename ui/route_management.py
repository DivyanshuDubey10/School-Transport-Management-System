from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class RouteManagement(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.create_widgets()
    
    def create_widgets(self):
        from PyQt6.QtWidgets import QGridLayout, QFrame, QHBoxLayout
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title
        title_label = QLabel("📍 Route Management")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #89B4FA;")
        main_layout.addWidget(title_label)

        # Main Container to center the form
        center_layout = QHBoxLayout()
        
        # Form Container (Card)
        form_frame = QFrame()
        form_frame.setObjectName("cardFrame")
        form_frame.setMinimumWidth(500)
        
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        form_title = QLabel("Add New Route")
        form_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        form_layout.addWidget(form_title, 0, 0, 1, 2)

        # Row 1: Route Name
        self.route_name_entry = QLineEdit()
        self.route_name_entry.setPlaceholderText("Enter Route Name")
        form_layout.addWidget(QLabel("Route Name:"), 1, 0)
        form_layout.addWidget(self.route_name_entry, 1, 1)

        # Save Button
        self.save_button = QPushButton("💾 Save Route")
        self.save_button.setFixedWidth(200)
        self.save_button.clicked.connect(self.save_route)
        form_layout.addWidget(self.save_button, 2, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        center_layout.addStretch()
        center_layout.addWidget(form_frame)
        center_layout.addStretch()
        
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

    def save_route(self):
        route_name = self.route_name_entry.text().strip()
        
        if not route_name:
            QMessageBox.critical(self, "Error", "Route Name is required.")
            return

        from dal import db_dal
        
        try:
            success = db_dal.add_route(route_name)
            if success:
                QMessageBox.information(self, "Success", "Route saved successfully.")
                self.route_name_entry.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
