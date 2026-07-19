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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Add New Route")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.route_name_entry = QLineEdit()
        self.route_name_entry.setPlaceholderText("Enter Route Name")
        self.route_name_entry.setFixedWidth(300)
        form_layout.addWidget(QLabel("Route Name"), alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.route_name_entry, alignment=Qt.AlignmentFlag.AlignCenter)

        save_button = QPushButton("Save Route")
        save_button.setFixedWidth(150)
        save_button.clicked.connect(self.save_route)
        form_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(form_layout)
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
