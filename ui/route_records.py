from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class RouteRecords(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.create_widgets()
        self.load_routes()
        
    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Route Records")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Search Frame
        search_layout = QHBoxLayout()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Route Name...")
        self.search_entry.setFixedWidth(300)
        search_layout.addWidget(self.search_entry, alignment=Qt.AlignmentFlag.AlignRight)

        search_button = QPushButton("Search")
        search_button.setFixedWidth(100)
        search_button.clicked.connect(self.load_routes)
        search_layout.addWidget(search_button, alignment=Qt.AlignmentFlag.AlignLeft)

        main_layout.addLayout(search_layout)

        # Table
        self.routes_table = QTableWidget()
        self.routes_table.setColumnCount(2)
        self.routes_table.setHorizontalHeaderLabels(["ID", "Route Name"])
        self.routes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.routes_table.horizontalHeader().setStretchLastSection(True)
        self.routes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.routes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.routes_table.itemSelectionChanged.connect(self.select_route)
        main_layout.addWidget(self.routes_table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.update_button = QPushButton("Update Route")
        self.update_button.clicked.connect(self.open_update_window)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Route")
        self.delete_button.clicked.connect(self.delete_route)
        button_layout.addWidget(self.delete_button)

        main_layout.addLayout(button_layout)

    def select_route(self):
        selected_items = self.routes_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        self.selected_route = [self.routes_table.item(row, col).text() for col in range(2)]
        self.selected_route_id = self.selected_route[0]

    def load_routes(self):
        search_query = self.search_entry.text().strip()
        
        from dal import db_dal
        routes = db_dal.get_all_routes(search_query=search_query)

        self.routes_table.setRowCount(0)
        for row_idx, row_data in enumerate(routes):
            self.routes_table.insertRow(row_idx)
            for col_idx, item in enumerate(row_data):
                self.routes_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

    def delete_route(self):
        if not hasattr(self, "selected_route_id"):
            QMessageBox.critical(self, "Error", "Please select a route first.")
            return

        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     'Are you sure you want to delete this route?\n(Ensure no buses or students are assigned to this route first!)', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            from dal import db_dal
            try:
                success = db_dal.delete_route(self.selected_route_id)
                if success:
                    QMessageBox.information(self, "Success", "Route deleted successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Could not delete route.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete route: {e}")

            self.load_routes()

    def open_update_window(self):
        if not hasattr(self, "selected_route_id"):
            QMessageBox.critical(self, "Error", "Please select a route first.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Update Route")
        dialog.setFixedSize(400, 150)
        
        layout = QFormLayout(dialog)
        
        name_entry = QLineEdit(self.selected_route[1])
        layout.addRow("Route Name:", name_entry)

        save_btn = QPushButton("Save Changes")
        def save_changes():
            route_name = name_entry.text().strip()
            if not route_name:
                QMessageBox.critical(dialog, "Error", "All fields are required.")
                return

            from dal import db_dal
            try:
                success = db_dal.update_route(self.selected_route_id, route_name)
                if success:
                    QMessageBox.information(dialog, "Success", "Route updated successfully!")
                    dialog.accept()
                    self.load_routes()
                else:
                    QMessageBox.critical(dialog, "Error", "Failed to update route.")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to update route: {e}")
                
        save_btn.clicked.connect(save_changes)
        layout.addWidget(save_btn)
        
        dialog.exec()
