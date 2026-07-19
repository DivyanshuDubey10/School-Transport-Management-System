from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class StudentRecords(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.create_widgets()
        self.load_students()
        
    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Student Records")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Search Frame
        search_layout = QHBoxLayout()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Name or Class...")
        self.search_entry.setFixedWidth(300)
        search_layout.addWidget(self.search_entry, alignment=Qt.AlignmentFlag.AlignRight)

        search_button = QPushButton("Search")
        search_button.setFixedWidth(100)
        search_button.clicked.connect(self.load_students)
        search_layout.addWidget(search_button, alignment=Qt.AlignmentFlag.AlignLeft)

        main_layout.addLayout(search_layout)

        # Table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(10)
        self.students_table.setHorizontalHeaderLabels(["ID", "Name", "Class", "Parent", "Phone", "Address", "Bus", "Route", "Fee Paid", "Fee Balance"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.students_table.horizontalHeader().setStretchLastSection(True)
        self.students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.students_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.students_table.itemSelectionChanged.connect(self.select_student)
        main_layout.addWidget(self.students_table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.update_button = QPushButton("Update Student")
        self.update_button.clicked.connect(self.open_update_window)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Student")
        self.delete_button.clicked.connect(self.delete_student)
        button_layout.addWidget(self.delete_button)

        main_layout.addLayout(button_layout)

    def select_student(self):
        selected_items = self.students_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        self.selected_student = [self.students_table.item(row, col).text() for col in range(10)]
        self.selected_student_id = self.selected_student[0]

    def load_students(self):
        search_query = self.search_entry.text().strip()
        
        from dal import db_dal
        students = db_dal.get_all_students(search_query=search_query)

        self.students_table.setRowCount(0)
        for row_idx, row_data in enumerate(students):
            self.students_table.insertRow(row_idx)
            for col_idx, item in enumerate(row_data):
                self.students_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

    def delete_student(self):
        if not hasattr(self, "selected_student_id"):
            QMessageBox.critical(self, "Error", "Please select a student first.")
            return

        reply = QMessageBox.question(self, 'Confirm Delete', 'Are you sure you want to delete this student?', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            from dal import db_dal
            try:
                success = db_dal.delete_student(self.selected_student_id)
                if success:
                    QMessageBox.information(self, "Success", "Student deleted successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Could not delete student.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete student: {e}")

            self.load_students()

    def open_update_window(self):
        if not hasattr(self, "selected_student_id"):
            QMessageBox.critical(self, "Error", "Please select a student first.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Update Student")
        dialog.setFixedSize(400, 300)
        
        layout = QFormLayout(dialog)
        
        name_entry = QLineEdit(self.selected_student[1])
        class_entry = QLineEdit(self.selected_student[2])
        parent_entry = QLineEdit(self.selected_student[3])
        route_entry = QLineEdit(self.selected_student[7])
        fee_paid_entry = QLineEdit(self.selected_student[8])
        fee_balance_entry = QLineEdit(self.selected_student[9])
        
        layout.addRow("Student Name:", name_entry)
        layout.addRow("Student Class:", class_entry)
        layout.addRow("Parent ID:", parent_entry)
        layout.addRow("Route ID:", route_entry)
        layout.addRow("Fee Paid:", fee_paid_entry)
        layout.addRow("Fee Balance:", fee_balance_entry)

        save_btn = QPushButton("Save Changes")
        def save_changes():
            from dal import db_dal
            try:
                fee_paid = float(fee_paid_entry.text().strip()) if fee_paid_entry.text().strip() else 0.0
                fee_balance = float(fee_balance_entry.text().strip()) if fee_balance_entry.text().strip() else 0.0
            except ValueError:
                QMessageBox.critical(dialog, "Error", "Fee Paid and Fee Balance must be valid numbers.")
                return

            try:
                success = db_dal.update_student(
                    self.selected_student_id,
                    name_entry.text().strip(),
                    class_entry.text().strip(),
                    parent_entry.text().strip(),
                    route_entry.text().strip(),
                    fee_paid,
                    fee_balance
                )
                if success:
                    QMessageBox.information(dialog, "Success", "Student updated successfully!")
                    dialog.accept()
                    self.load_students()
                else:
                    QMessageBox.critical(dialog, "Error", "Could not update student.")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to update student: {e}")
                
        save_btn.clicked.connect(save_changes)
        layout.addWidget(save_btn)
        
        dialog.exec()