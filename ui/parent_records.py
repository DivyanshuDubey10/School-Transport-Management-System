from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout, QFrame)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_avatar_cell(name, subtext, bg_color="#38BDF8", text_color="#0F172A"):
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
        title_label.setStyleSheet("font-size: 18pt; font-weight: 800; color: #F8FAFC; letter-spacing: -0.5px;")
        title_box.addWidget(title_label)
        
        sub_label = QLabel("Registered guardian profiles, portal login credentials, contact phones, and pickup locations.")
        sub_label.setStyleSheet("font-size: 10pt; color: #94A3B8;")
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setFixedSize(130, 38)
        refresh_btn.setStyleSheet("QPushButton { background-color: #1E293B; color: #38BDF8; border: 1.5px solid #38BDF8; border-radius: 6px; font-weight: bold; font-size: 10pt; } QPushButton:hover { background-color: #38BDF8; color: #0F172A; }")
        refresh_btn.clicked.connect(self.load_parents)
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        main_layout.addLayout(header_layout)

        # 2. Search Bar & Actions Box
        search_layout = QHBoxLayout()
        
        self.update_button = QPushButton("Update Selected")
        self.update_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_button.setFixedHeight(38)
        self.update_button.setStyleSheet("QPushButton { background-color: #1E293B; color: #38BDF8; border: 1px solid #38BDF8; border-radius: 6px; font-weight: bold; padding: 0 16px; font-size: 10pt; } QPushButton:hover { background-color: #2563EB; color: #FFFFFF; }")
        self.update_button.clicked.connect(self.open_update_window)
        search_layout.addWidget(self.update_button)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setFixedHeight(38)
        self.delete_button.setStyleSheet("QPushButton { background-color: #7F1D1D; color: #F8FAFC; border: 1px solid #991B1B; border-radius: 6px; font-weight: bold; padding: 0 16px; font-size: 10pt; } QPushButton:hover { background-color: #991B1B; }")
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
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
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
        self.parents_table.setStyleSheet("QTableWidget { background-color: #0F172A; alternate-background-color: #131C31; border: 1px solid #334155; border-radius: 8px; } QHeaderView::section { background-color: #1E293B; color: #38BDF8; font-weight: bold; font-size: 10pt; padding: 12px; border-bottom: 2px solid #334155; } QTableWidget::item { padding: 8px; font-size: 10.5pt; }")
        self.parents_table.itemSelectionChanged.connect(self.select_parent)
        main_layout.addWidget(self.parents_table)

        # 4. Footer Bar
        footer_bar = QHBoxLayout()
        self.lbl_total_rows = QLabel("Rows per page:  15    •    1-0 of 0 items")
        self.lbl_total_rows.setStyleSheet("font-size: 9.5pt; color: #94A3B8; font-weight: 600;")
        footer_bar.addWidget(self.lbl_total_rows)
        footer_bar.addStretch()
        pagination_controls = QLabel("|<     <     1     >     >|")
        pagination_controls.setStyleSheet("font-size: 11pt; font-weight: bold; color: #38BDF8; letter-spacing: 4px;")
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

            avatar_colors = ["#10B981", "#38BDF8", "#8B5CF6", "#F59E0B", "#EC4899", "#3B82F6"]
            col_choice = avatar_colors[row_idx % len(avatar_colors)]
            self.parents_table.setCellWidget(row_idx, 1, create_avatar_cell(p_name, f"Parent ID: PAR-{1000+row_idx}", col_choice, "#0F172A"))
            self.parents_table.setCellWidget(row_idx, 2, create_twoline_cell(phone, "Verified Mobile", "#F8FAFC", "#64748B"))
            self.parents_table.setCellWidget(row_idx, 3, create_twoline_cell(addr[:22]+("..." if len(addr)>22 else ""), "Home Residence", "#E2E8F0", "#64748B"))
            self.parents_table.setCellWidget(row_idx, 4, create_twoline_cell(stop, "Morning Pickup Point", "#38BDF8", "#64748B"))
            self.parents_table.setCellWidget(row_idx, 5, create_twoline_cell(f"@{uname}", "Active Web Portal", "#10B981", "#64748B"))

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
                success = db_dal.delete_parent(self.selected_parent_id)
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
        dialog.setStyleSheet("QDialog { background-color: #1E293B; color: #F8FAFC; } QLabel { color: #F8FAFC; font-weight: bold; font-size: 10pt; } QLineEdit { background-color: #0F172A; border: 1px solid #334155; border-radius: 6px; padding: 6px; color: #F8FAFC; font-size: 10pt; }")
        
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
        save_btn.setStyleSheet("QPushButton { background-color: #10B981; color: #FFFFFF; border: none; border-radius: 6px; font-weight: bold; font-size: 10.5pt; margin-top: 10px; } QPushButton:hover { background-color: #059669; }")
        def save_changes():
            from dal import db_dal
            try:
                success = db_dal.update_parent(
                    self.selected_parent_id,
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