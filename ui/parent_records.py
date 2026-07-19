from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ParentRecords(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.create_widgets()
        self.load_parents()
        
    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Parent Records")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Search Frame
        search_layout = QHBoxLayout()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Name, Username or Phone...")
        self.search_entry.setFixedWidth(300)
        search_layout.addWidget(self.search_entry, alignment=Qt.AlignmentFlag.AlignRight)

        search_button = QPushButton("Search")
        search_button.setFixedWidth(100)
        search_button.clicked.connect(self.load_parents)
        search_layout.addWidget(search_button, alignment=Qt.AlignmentFlag.AlignLeft)

        main_layout.addLayout(search_layout)

        # Table
        self.parents_table = QTableWidget()
        self.parents_table.setColumnCount(6)
        self.parents_table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Address", "Pickup Point", "Username"])
        self.parents_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.parents_table.horizontalHeader().setStretchLastSection(True)
        self.parents_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.parents_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.parents_table.itemSelectionChanged.connect(self.select_parent)
        main_layout.addWidget(self.parents_table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.update_button = QPushButton("Update Parent")
        self.update_button.clicked.connect(self.open_update_window)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Parent")
        self.delete_button.clicked.connect(self.delete_parent)
        button_layout.addWidget(self.delete_button)

        main_layout.addLayout(button_layout)

    def select_parent(self):
        selected_items = self.parents_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        self.selected_parent = [self.parents_table.item(row, col).text() for col in range(6)]
        self.selected_parent_id = self.selected_parent[0]

    def load_parents(self):
        search_query = self.search_entry.text().strip()
        
        from dal import db_dal
        parents = db_dal.get_all_parents(search_query=search_query)

        self.parents_table.setRowCount(0)
        for row_idx, row_data in enumerate(parents):
            self.parents_table.insertRow(row_idx)
            # Row data has 7 columns from DB: parent_id, parent_name, phone, address, pickup_point, username, password
            # We only want to display the first 6
            display_data = row_data[:6]
            for col_idx, item in enumerate(display_data):
                self.parents_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

    def delete_parent(self):
        if not hasattr(self, "selected_parent_id"):
            QMessageBox.critical(self, "Error", "Please select a parent first.")
            return

        reply = QMessageBox.question(self, 'Confirm Delete', 'Are you sure you want to delete this parent?', 
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
        dialog.setWindowTitle("Update Parent")
        dialog.setFixedSize(400, 300)
        
        layout = QFormLayout(dialog)
        
        name_entry = QLineEdit(self.selected_parent[1])
        phone_entry = QLineEdit(self.selected_parent[2])
        address_entry = QLineEdit(self.selected_parent[3])
        pickup_entry = QLineEdit(self.selected_parent[4])
        username_entry = QLineEdit(self.selected_parent[5])
        
        layout.addRow("Parent Name:", name_entry)
        layout.addRow("Phone:", phone_entry)
        layout.addRow("Address:", address_entry)
        layout.addRow("Pickup Point:", pickup_entry)
        layout.addRow("Username:", username_entry)

        save_btn = QPushButton("Save Changes")
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