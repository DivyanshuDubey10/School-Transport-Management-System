from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_avatar_cell(name, subtext, bg_color="#38BDF8", text_color="#FFFFFF"):
    """Creates a circular initials avatar cell matching modern SaaS dashboards."""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(10, 6, 10, 6)
    layout.setSpacing(12)
    
    avatar = QLabel()
    avatar.setFixedSize(38, 38)
    avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
    parts = name.strip().split()
    if len(parts) >= 2:
        init = (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1 and len(parts[0]) > 0:
        init = parts[0][:2].upper()
    else:
        init = "FL"
    avatar.setText(init)
    avatar.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border-radius: 19px; font-weight: 800; font-size: 11pt; border: 1px solid #9CA3AF;")
    layout.addWidget(avatar)
    
    text_box = QVBoxLayout()
    text_box.setSpacing(2)
    text_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)
    
    lbl_main = QLabel(name)
    lbl_main.setObjectName("statTitle")
    text_box.addWidget(lbl_main)
    
    lbl_sub = QLabel(subtext)
    lbl_sub.setObjectName("statDesc")
    text_box.addWidget(lbl_sub)
    
    layout.addLayout(text_box)
    layout.addStretch()
    return widget

def create_twoline_cell(main_text, sub_text, main_color="#111827", sub_color="#1F2937"):
    """Creates a 2-line cell with primary text and muted subtext."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(12, 6, 12, 6)
    layout.setSpacing(2)
    layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
    
    lbl_main = QLabel(main_text)
    lbl_main.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {main_color}; border: none;")
    layout.addWidget(lbl_main)
    
    lbl_sub = QLabel(sub_text)
    lbl_sub.setStyleSheet(f"font-size: 8.5pt; color: {sub_color}; border: none;")
    layout.addWidget(lbl_sub)
    return widget

class BusRecords(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.bus_data_map = {}
        self.create_widgets()
        self.load_buses()
        
    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(18)

        # 1. Page Header with Title and REFRESH button (matching screenshot)
        header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_label = QLabel("Drivers & Bus Fleet Directory")
        title_label.setObjectName("pageTitle")
        title_box.addWidget(title_label)
        
        sub_label = QLabel("Manage school transport fleet, assigned drivers, capacity limits, and route alignments.")
        sub_label.setObjectName("statDesc")
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        
        main_layout.addLayout(header_layout)

        # 2. Search Bar & Actions Box
        search_layout = QHBoxLayout()
        
        self.update_button = QPushButton("Update Selected")
        self.update_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_button.setFixedHeight(38)
        self.update_button.setObjectName("actionButton")
        self.update_button.clicked.connect(self.open_update_window)
        search_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Selected Bus")
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setFixedHeight(38)
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self.delete_bus)
        search_layout.addWidget(self.delete_button)
        
        search_layout.addStretch()
        
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Bus Number, Driver, or Route...")
        self.search_entry.setFixedWidth(320)
        self.search_entry.textChanged.connect(self.load_buses)
        search_layout.addWidget(self.search_entry)
        
        main_layout.addLayout(search_layout)

        # 3. Modern SaaS Table
        self.buses_table = QTableWidget()
        self.buses_table.setColumnCount(6)
        self.buses_table.setHorizontalHeaderLabels(["ID", "Bus & Capacity", "Driver Profile", "Contact Phone", "Status & Tenant", "Assigned Travel Route"])
        
        header = self.buses_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.buses_table.setColumnWidth(0, 50)   # ID
        self.buses_table.setColumnWidth(1, 160)  # Bus & Capacity
        self.buses_table.setColumnWidth(2, 240)  # Driver Profile (with Avatar)
        self.buses_table.setColumnWidth(3, 150)  # Phone
        self.buses_table.setColumnWidth(4, 150)  # Status & Tenant
        header.setStretchLastSection(True)
        
        self.buses_table.verticalHeader().setDefaultSectionSize(58)
        self.buses_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.buses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.buses_table.setAlternatingRowColors(True)
        self.buses_table.setObjectName("dataTable")
        self.buses_table.itemSelectionChanged.connect(self.select_bus)
        self.buses_table.verticalScrollBar().setSingleStep(15)
        
        main_layout.addWidget(self.buses_table)

        # 4. Pagination & Footer Bar (exactly like screenshot)
        footer_bar = QHBoxLayout()
        
        self.lbl_total_rows = QLabel("Rows per page:  15    •    1-0 of 0 items")
        self.lbl_total_rows
        footer_bar.addWidget(self.lbl_total_rows)
        
        footer_bar.addStretch()
        
        pagination_controls = QLabel("|<     <     1     >     >|")
        pagination_controls
        footer_bar.addWidget(pagination_controls)
        
        main_layout.addLayout(footer_bar)

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
        self.bus_data_map.clear()
        for row_idx, row_data in enumerate(buses):
            self.buses_table.insertRow(row_idx)
            # row_data: (bus_id, bus_number, driver_name, driver_phone, capacity, route_id, route_name, username)
            bus_id_val = int(row_data[0])
            self.bus_data_map[bus_id_val] = row_data
            
            bus_id = str(row_data[0])
            bus_no = str(row_data[1])
            drv_name = str(row_data[2]) if row_data[2] else "Unassigned Driver"
            drv_phone = str(row_data[3]) if row_data[3] else "N/A"
            capacity = str(row_data[4])
            route_name = str(row_data[6]) if row_data[6] else "No Route Assigned"

            # Set background text items for reliable selection
            self.buses_table.setItem(row_idx, 0, QTableWidgetItem(bus_id))
            self.buses_table.setItem(row_idx, 1, QTableWidgetItem(bus_no))
            self.buses_table.setItem(row_idx, 2, QTableWidgetItem(drv_name))
            self.buses_table.setItem(row_idx, 3, QTableWidgetItem(drv_phone))
            self.buses_table.setItem(row_idx, 4, QTableWidgetItem(f"Capacity: {capacity}"))
            self.buses_table.setItem(row_idx, 5, QTableWidgetItem(route_name))

        total = len(buses)
        self.lbl_total_rows.setText(f"Rows per page:  15    •    1-{total} of {total} items")

    def delete_bus(self):
        if not hasattr(self, "selected_bus_id"):
            QMessageBox.critical(self, "Error", "Please select a bus from the table first.")
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

    def open_update_window(self):
        if not hasattr(self, "selected_bus_id"):
            QMessageBox.critical(self, "Error", "Please select a bus first.")
            return

        from PyQt6.QtWidgets import QDialog, QFormLayout
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Bus Details")
        dialog.setFixedSize(420, 360)
        dialog
        
        layout = QFormLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        bus_data = self.bus_data_map.get(self.selected_bus_id)
        if not bus_data:
            return

        bus_no_entry = QLineEdit(str(bus_data[1]))
        driver_name_entry = QLineEdit(str(bus_data[2]) if bus_data[2] else "")
        driver_phone_entry = QLineEdit(str(bus_data[3]) if bus_data[3] else "")
        capacity_entry = QLineEdit(str(bus_data[4]))
        username_entry = QLineEdit(str(bus_data[7]) if bus_data[7] else "")
        password_entry = QLineEdit()
        password_entry.setPlaceholderText("Leave blank to keep current password")
        password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addRow("Bus Number:", bus_no_entry)
        layout.addRow("Driver Name:", driver_name_entry)
        layout.addRow("Driver Phone:", driver_phone_entry)
        layout.addRow("Capacity:", capacity_entry)
        layout.addRow("Driver Username:", username_entry)
        layout.addRow("New Password:", password_entry)

        save_btn = QPushButton("Save Bus Changes")
        save_btn.setFixedHeight(40)
        save_btn.setObjectName("primaryButton")
        
        def save_changes():
            from dal import db_dal
            try:
                capacity_val = int(capacity_entry.text().strip())
            except ValueError:
                QMessageBox.critical(dialog, "Error", "Capacity must be a valid number.")
                return

            try:
                success = db_dal.update_bus(
                    self.selected_bus_id,
                    bus_no_entry.text().strip(),
                    driver_name_entry.text().strip(),
                    driver_phone_entry.text().strip(),
                    capacity_val,
                    username_entry.text().strip(),
                    password_entry.text().strip()
                )
                if success:
                    QMessageBox.information(dialog, "Success", "Bus updated successfully!")
                    dialog.accept()
                    self.load_buses()
                else:
                    QMessageBox.critical(dialog, "Error", "Could not update bus.")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to update bus: {e}")
                
        save_btn.clicked.connect(save_changes)
        layout.addWidget(save_btn)
        
        dialog.exec()
