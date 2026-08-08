from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout, QFrame)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_avatar_cell(name, subtext, bg_color="#38BDF8", text_color="#FFFFFF"):
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
        init = "PR"
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

class ParentRecords(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.create_widgets()
        self.load_parents()
        
    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(18)

        # 1. Page Header with Title and REFRESH button
        header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_label = QLabel("Parent Accounts Directory")
        title_label.setObjectName("pageTitle")
        title_box.addWidget(title_label)
        
        sub_label = QLabel("Registered guardian profiles, portal login credentials, contact phones, and pickup locations.")
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
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setFixedHeight(38)
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self.delete_parent)
        search_layout.addWidget(self.delete_button)

        search_layout.addStretch()
        
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search parent name, username, or phone...")
        self.search_entry.setFixedWidth(320)
        self.search_entry.textChanged.connect(self.load_parents)
        search_layout.addWidget(self.search_entry)
        
        main_layout.addLayout(search_layout)

        # 3. Table
        self.parents_table = QTableWidget()
        self.parents_table.setColumnCount(6)
        self.parents_table.setHorizontalHeaderLabels(["ID", "Parent Profile", "Contact Phone", "Home Address", "Designated Stop", "Portal Account"])
        header = self.parents_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.parents_table.setColumnWidth(0, 50)
        self.parents_table.setColumnWidth(1, 240)
        self.parents_table.setColumnWidth(2, 150)
        self.parents_table.setColumnWidth(3, 220)
        self.parents_table.setColumnWidth(4, 180)
        self.parents_table.setColumnWidth(5, 160)
        header.setStretchLastSection(True)
        
        self.parents_table.verticalHeader().setDefaultSectionSize(58)
        self.parents_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.parents_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.parents_table.setAlternatingRowColors(True)
        self.parents_table.setObjectName("dataTable")
        self.parents_table.itemSelectionChanged.connect(self.select_parent)
        self.parents_table.verticalScrollBar().setSingleStep(15)
        main_layout.addWidget(self.parents_table)

        # 4. Footer Bar
        footer_bar = QHBoxLayout()
        self.lbl_total_rows = QLabel("Rows per page:  15    •    1-0 of 0 items")
        self.lbl_total_rows
        footer_bar.addWidget(self.lbl_total_rows)
        footer_bar.addStretch()
        pagination_controls = QLabel("|<     <     1     >     >|")
        pagination_controls
        footer_bar.addWidget(pagination_controls)
        main_layout.addLayout(footer_bar)

    def select_parent(self):
        selected_items = self.parents_table.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        self.selected_parent = [self.parents_table.item(row, col).text() if self.parents_table.item(row, col) else "" for col in range(6)]
        self.selected_parent_id = self.selected_parent[0]

    def load_parents(self):
        search_query = self.search_entry.text().strip()
        from dal import db_dal
        parents = db_dal.get_all_parents(search_query=search_query)

        self.parents_table.setRowCount(0)
        for row_idx, row_data in enumerate(parents):
            self.parents_table.insertRow(row_idx)
            # row_data: (parent_id, parent_name, phone, address, pickup_point, username, password)
            p_id = str(row_data[0])
            p_name = str(row_data[1])
            phone = str(row_data[2]) if row_data[2] else "N/A"
            addr = str(row_data[3]) if row_data[3] else "N/A"
            stop = str(row_data[4]) if row_data[4] else "N/A"
            uname = str(row_data[5])

            self.parents_table.setItem(row_idx, 0, QTableWidgetItem(p_id))
            self.parents_table.setItem(row_idx, 1, QTableWidgetItem(p_name))
            self.parents_table.setItem(row_idx, 2, QTableWidgetItem(phone))
            self.parents_table.setItem(row_idx, 3, QTableWidgetItem(addr))
            self.parents_table.setItem(row_idx, 4, QTableWidgetItem(stop))
            self.parents_table.setItem(row_idx, 5, QTableWidgetItem(uname))

        total = len(parents)
        self.lbl_total_rows.setText(f"Rows per page:  15    •    1-{total} of {total} items")

    def delete_parent(self):
        if not hasattr(self, "selected_parent_id"):
            QMessageBox.critical(self, "Error", "Please select a parent from the table first.")
            return

        reply = QMessageBox.question(self, 'Confirm Delete', 'Are you sure you want to delete this parent account?', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            from dal import db_dal
            try:
                success = db_dal.delete_parent(int(self.selected_parent_id))
                if success:
                    QMessageBox.information(self, "Success", "Parent deleted successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Could not delete parent.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete parent: {e}")
            self.load_parents()

    def open_update_window(self):
        if not hasattr(self, "selected_parent_id"):
            QMessageBox.critical(self, "Error", "Please select a parent first.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Update Parent Account")
        dialog.setFixedSize(420, 320)
        dialog
        
        layout = QFormLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        name_entry = QLineEdit(self.selected_parent[1])
        phone_entry = QLineEdit(self.selected_parent[2])
        address_entry = QLineEdit(self.selected_parent[3])
        pickup_entry = QLineEdit(self.selected_parent[4])
        username_entry = QLineEdit(self.selected_parent[5])
        
        layout.addRow("Parent Name:", name_entry)
        layout.addRow("Phone Number:", phone_entry)
        layout.addRow("Home Address:", address_entry)
        layout.addRow("Pickup Point:", pickup_entry)
        layout.addRow("Username:", username_entry)

        save_btn = QPushButton("Save Account Changes")
        save_btn.setFixedHeight(40)
        save_btn.setObjectName("primaryButton")
        def save_changes():
            from dal import db_dal
            try:
                success = db_dal.update_parent(
                    int(self.selected_parent_id),
                    name_entry.text().strip(),
                    phone_entry.text().strip(),
                    address_entry.text().strip(),
                    pickup_entry.text().strip(),
                    username_entry.text().strip()
                )
                if success:
                    QMessageBox.information(dialog, "Success", "Parent updated successfully!")
                    dialog.accept()
                    self.load_parents()
                else:
                    QMessageBox.critical(dialog, "Error", "Could not update parent.")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to update parent: {e}")
                
        save_btn.clicked.connect(save_changes)
        layout.addWidget(save_btn)
        
        dialog.exec()
