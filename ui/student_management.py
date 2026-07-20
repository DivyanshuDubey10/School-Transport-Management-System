from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class StudentManagement(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.fetch_dropdown_data()
        self.create_widgets()
        
    def fetch_dropdown_data(self):
        from dal import db_dal
        
        parents = db_dal.get_all_parents_dropdown()
        self.parent_options = [f"{row[0]} - {row[1]}" for row in parents]
        if not self.parent_options: self.parent_options = [""]
        
        routes = db_dal.get_all_routes_with_bus_dropdown()
        self.route_options = []
        for row in routes:
            bus_str = f" (Bus: {row[2]})" if row[2] else " (No Bus)"
            self.route_options.append(f"{row[0]} - {row[1]}{bus_str}")
        if not self.route_options: self.route_options = [""]

    def create_widgets(self):
        from PyQt6.QtWidgets import QGridLayout, QFrame
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title
        title_label = QLabel("🎓 Student Management")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #89B4FA;")
        main_layout.addWidget(title_label)

        # Form Container (Card)
        form_frame = QFrame()
        form_frame.setObjectName("cardFrame")
        
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        form_title = QLabel("Add New Student")
        form_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        form_layout.addWidget(form_title, 0, 0, 1, 4)

        # Row 1: Name and Class
        self.student_name_entry = QLineEdit()
        self.student_name_entry.setPlaceholderText("Enter Student Name")
        form_layout.addWidget(QLabel("Student Name:"), 1, 0)
        form_layout.addWidget(self.student_name_entry, 1, 1)

        self.student_class_entry = QLineEdit()
        self.student_class_entry.setPlaceholderText("Enter Student Class")
        form_layout.addWidget(QLabel("Student Class:"), 1, 2)
        form_layout.addWidget(self.student_class_entry, 1, 3)

        # Row 2: Parent and Route Dropdowns
        self.parent_id_entry = QComboBox()
        self.parent_id_entry.addItems(self.parent_options)
        form_layout.addWidget(QLabel("Parent:"), 2, 0)
        form_layout.addWidget(self.parent_id_entry, 2, 1)

        self.route_id_entry = QComboBox()
        self.route_id_entry.addItems(self.route_options)
        form_layout.addWidget(QLabel("Route:"), 2, 2)
        form_layout.addWidget(self.route_id_entry, 2, 3)

        # Row 3: Fees
        self.fee_paid_entry = QLineEdit()
        self.fee_paid_entry.setPlaceholderText("0.00")
        form_layout.addWidget(QLabel("Fee Paid ($):"), 3, 0)
        form_layout.addWidget(self.fee_paid_entry, 3, 1)

        self.fee_balance_entry = QLineEdit()
        self.fee_balance_entry.setPlaceholderText("0.00")
        form_layout.addWidget(QLabel("Fee Balance ($):"), 3, 2)
        form_layout.addWidget(self.fee_balance_entry, 3, 3)

        # Save Button
        self.save_button = QPushButton("💾 Save Student")
        self.save_button.setFixedWidth(200)
        self.save_button.clicked.connect(self.save_student)
        form_layout.addWidget(self.save_button, 4, 0, 1, 4, Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(form_frame)

        # Table Section
        list_label = QLabel("📋 Student Records")
        list_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #89B4FA;")
        main_layout.addWidget(list_label)

        table_frame = QFrame()
        table_frame.setObjectName("cardFrame")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(10, 10, 10, 10)

        self.students_table = QTableWidget()
        self.students_table.setColumnCount(10)
        self.students_table.setHorizontalHeaderLabels(["ID", "Name", "Class", "Parent", "Phone", "Address", "Bus", "Route", "Fee Paid", "Fee Balance"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.students_table.horizontalHeader().setStretchLastSection(True)
        self.students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.students_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.students_table.setStyleSheet("border: none; background-color: transparent;")
        
        table_layout.addWidget(self.students_table)
        main_layout.addWidget(table_frame)
        
        self.load_students()

    def load_students(self):
        from dal import db_dal
        students = db_dal.get_all_students()
        
        self.students_table.setRowCount(0)
        for row_idx, row_data in enumerate(students):
            self.students_table.insertRow(row_idx)
            for col_idx, item in enumerate(row_data):
                self.students_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

    def save_student(self):
        student_name = self.student_name_entry.text().strip()
        student_class = self.student_class_entry.text().strip()
        parent_selection = self.parent_id_entry.currentText()
        route_selection = self.route_id_entry.currentText()
        fee_paid_str = self.fee_paid_entry.text().strip()
        fee_balance_str = self.fee_balance_entry.text().strip()
        
        parent_id = parent_selection.split(" - ")[0] if " - " in parent_selection else ""
        route_id = route_selection.split(" - ")[0] if " - " in route_selection else ""

        if not student_name:
            QMessageBox.critical(self, "Error", "Student Name is required.")
            return
        if not student_class:
            QMessageBox.critical(self, "Error", "Student Class is required.")
            return
        if not parent_id:
            QMessageBox.critical(self, "Error", "Parent ID is required.")
            return
        if not route_id:
            QMessageBox.critical(self, "Error", "Route ID is required.")
            return

        try:
            fee_paid = float(fee_paid_str) if fee_paid_str else 0.0
            fee_balance = float(fee_balance_str) if fee_balance_str else 0.0
        except ValueError:
            QMessageBox.critical(self, "Error", "Fee Paid and Fee Balance must be valid numbers.")
            return

        from dal import db_dal
        
        is_full, current_students, capacity = db_dal.check_bus_capacity(route_id)
        if is_full:
            QMessageBox.critical(self, "Capacity Error", f"The bus for this route is at capacity ({current_students}/{capacity}). Cannot add student.")
            return

        success = db_dal.add_student(student_name, student_class, parent_id, route_id, fee_paid, fee_balance)
        if success:
            self.load_students()
            QMessageBox.information(self, "Success", "Student added successfully!")

        self.student_name_entry.clear()
        self.student_class_entry.clear()
        self.fee_paid_entry.clear()
        self.fee_balance_entry.clear()
        self.parent_id_entry.setCurrentIndex(0)
        self.route_id_entry.setCurrentIndex(0)
