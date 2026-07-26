from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_avatar_cell(name, subtext, bg_color="#38BDF8", text_color="#0F172A"):
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
    avatar.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border-radius: 19px; font-weight: 800; font-size: 11pt; border: 1px solid #475569;")
    layout.addWidget(avatar)
    
    text_box = QVBoxLayout()
    text_box.setSpacing(2)
    text_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)
    
    lbl_main = QLabel(name)
    lbl_main.setStyleSheet("font-size: 11pt; font-weight: bold; color: #F8FAFC; border: none;")
    text_box.addWidget(lbl_main)
    
    lbl_sub = QLabel(subtext)
    lbl_sub.setStyleSheet("font-size: 8.5pt; color: #94A3B8; border: none;")
    text_box.addWidget(lbl_sub)
    
    layout.addLayout(text_box)
    layout.addStretch()
    return widget

def create_twoline_cell(main_text, sub_text, main_color="#F8FAFC", sub_color="#94A3B8"):
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
        title_label.setStyleSheet("font-size: 18pt; font-weight: 800; color: #F8FAFC; letter-spacing: -0.5px;")
        title_box.addWidget(title_label)
        
        sub_label = QLabel("Manage school transport fleet, assigned drivers, capacity limits, and route alignments.")
        sub_label.setStyleSheet("font-size: 10pt; color: #94A3B8;")
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setFixedSize(130, 38)
        refresh_btn.setStyleSheet("QPushButton { background-color: #1E293B; color: #38BDF8; border: 1.5px solid #38BDF8; border-radius: 6px; font-weight: bold; font-size: 10pt; } QPushButton:hover { background-color: #38BDF8; color: #0F172A; }")
        refresh_btn.clicked.connect(self.load_buses)
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        main_layout.addLayout(header_layout)

        # 2. Search Bar & Actions Box
        search_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("Delete Selected Bus")
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setFixedHeight(38)
        self.delete_button.setStyleSheet("QPushButton { background-color: #7F1D1D; color: #F8FAFC; border: 1px solid #991B1B; border-radius: 6px; font-weight: bold; padding: 0 16px; font-size: 10pt; } QPushButton:hover { background-color: #991B1B; }")
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
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
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
        self.buses_table.setStyleSheet("QTableWidget { background-color: #0F172A; alternate-background-color: #131C31; border: 1px solid #334155; border-radius: 8px; } QHeaderView::section { background-color: #1E293B; color: #38BDF8; font-weight: bold; font-size: 10pt; padding: 12px; border-bottom: 2px solid #334155; } QTableWidget::item { padding: 8px; font-size: 10.5pt; }")
        self.buses_table.itemSelectionChanged.connect(self.select_bus)
        
        main_layout.addWidget(self.buses_table)

        # 4. Pagination & Footer Bar (exactly like screenshot)
        footer_bar = QHBoxLayout()
        
        self.lbl_total_rows = QLabel("Rows per page:  15    •    1-0 of 0 items")
        self.lbl_total_rows.setStyleSheet("font-size: 9.5pt; color: #94A3B8; font-weight: 600;")
        footer_bar.addWidget(self.lbl_total_rows)
        
        footer_bar.addStretch()
        
        pagination_controls = QLabel("|<     <     1     >     >|")
        pagination_controls.setStyleSheet("font-size: 11pt; font-weight: bold; color: #38BDF8; letter-spacing: 4px;")
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
        for row_idx, row_data in enumerate(buses):
            self.buses_table.insertRow(row_idx)
            # row_data: (bus_id, bus_number, driver_name, driver_phone, capacity, route_id, route_name)
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

            # Set custom visual SaaS widgets
            self.buses_table.setCellWidget(row_idx, 1, create_twoline_cell(f"Bus #{bus_no}", f"Max Seats: {capacity}", "#F8FAFC", "#38BDF8"))
            
            # Avatar cell for Driver Name
            avatar_colors = ["#38BDF8", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#3B82F6"]
            color_choice = avatar_colors[row_idx % len(avatar_colors)]
            self.buses_table.setCellWidget(row_idx, 2, create_avatar_cell(drv_name, f"Driver ID: DRV-{100+row_idx}", color_choice, "#0F172A"))
            
            self.buses_table.setCellWidget(row_idx, 3, create_twoline_cell(drv_phone, "Active Mobile", "#E2E8F0", "#64748B"))
            self.buses_table.setCellWidget(row_idx, 4, create_twoline_cell("Active", "Tenant: ORG-STMS", "#10B981", "#64748B"))
            self.buses_table.setCellWidget(row_idx, 5, create_twoline_cell(route_name, "Daily School Pickup", "#F8FAFC", "#94A3B8"))

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
