from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BusRecords(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.create_widgets()
        self.load_buses()
        
    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("Bus Records")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #38BDF8;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Search Frame
        search_layout = QHBoxLayout()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Bus Number, Driver, or Route...")
        self.search_entry.setFixedWidth(320)
        search_layout.addWidget(self.search_entry, alignment=Qt.AlignmentFlag.AlignRight)

        search_button = QPushButton("Search")
        search_button.setFixedWidth(100)
        search_button.clicked.connect(self.load_buses)
        search_layout.addWidget(search_button, alignment=Qt.AlignmentFlag.AlignLeft)

        main_layout.addLayout(search_layout)

        # Table
        self.buses_table = QTableWidget()
        self.buses_table.setColumnCount(6)
        self.buses_table.setHorizontalHeaderLabels(["ID", "Bus Number", "Driver Name", "Driver Phone", "Capacity", "Assigned Route / Points"])
        header = self.buses_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.buses_table.setColumnWidth(0, 60)   # ID
        self.buses_table.setColumnWidth(1, 140)  # Bus Number
        self.buses_table.setColumnWidth(2, 180)  # Driver Name
        self.buses_table.setColumnWidth(3, 140)  # Driver Phone
        self.buses_table.setColumnWidth(4, 100)  # Capacity
        header.setStretchLastSection(True)
        self.buses_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.buses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.buses_table.itemSelectionChanged.connect(self.select_bus)
        main_layout.addWidget(self.buses_table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.delete_button = QPushButton("Delete Bus")
        self.delete_button.clicked.connect(self.delete_bus)
        button_layout.addWidget(self.delete_button)

        main_layout.addLayout(button_layout)

    def select_bus(self):
        selected_items = self.buses_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        self.selected_bus = [self.buses_table.item(row, col).text() for col in range(6)]
        self.selected_bus_id = int(self.selected_bus[0])

    def load_buses(self):
        search_query = self.search_entry.text().strip()
        
        from dal import db_dal
        buses = db_dal.get_all_buses(search_query=search_query)

        self.buses_table.setRowCount(0)
        for row_idx, row_data in enumerate(buses):
            self.buses_table.insertRow(row_idx)
            # row_data: (bus_id, bus_number, driver_name, driver_phone, capacity, route_id, route_name)
            display_data = [
                str(row_data[0]),
                str(row_data[1]),
                str(row_data[2]),
                str(row_data[3]),
                str(row_data[4]),
                str(row_data[6]) if row_data[6] else "Unassigned"
            ]
            for col_idx, item in enumerate(display_data):
                self.buses_table.setItem(row_idx, col_idx, QTableWidgetItem(item))

    def delete_bus(self):
        if not hasattr(self, "selected_bus_id"):
            QMessageBox.critical(self, "Error", "Please select a bus first.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete Bus #{self.selected_bus[1]}? This may unassign students on this bus route.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            from dal import db_dal
            success = db_dal.delete_bus(self.selected_bus_id)
            if success:
                QMessageBox.information(self, "Success", "Bus deleted successfully.")
                self.load_buses()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete bus.")
