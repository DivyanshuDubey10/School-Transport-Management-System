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
        title_label = QLabel("Student Management")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #38BDF8;")
        main_layout.addWidget(title_label)

        # Form Container (Card)
        form_frame = QFrame()
        form_frame.setObjectName("cardFrame")
        form_frame.setFixedWidth(660)
        
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(32, 32, 32, 32)
        form_layout.setHorizontalSpacing(24)
        form_layout.setVerticalSpacing(20)
        form_layout.setColumnStretch(0, 1)
        form_layout.setColumnStretch(1, 1)

        form_title = QLabel("Add New Student")
        form_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC; margin-bottom: 10px;")
        form_layout.addWidget(form_title, 0, 0, 1, 2)

        def create_field(label_text, widget):
            field_layout = QVBoxLayout()
            field_layout.setSpacing(6)
            field_layout.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #94A3B8;")
            field_layout.addWidget(lbl)
            field_layout.addWidget(widget)
            return field_layout

        # Row 1: Name and Class
        self.student_name_entry = QLineEdit()
        self.student_name_entry.setPlaceholderText("Enter Student Name")
        form_layout.addLayout(create_field("Student Name", self.student_name_entry), 1, 0)

        self.student_class_entry = QLineEdit()
        self.student_class_entry.setPlaceholderText("Enter Student Class")
        form_layout.addLayout(create_field("Student Class", self.student_class_entry), 1, 1)

        # Row 2: Parent and Route Dropdowns
        self.parent_id_entry = QComboBox()
        self.parent_id_entry.addItems(self.parent_options)
        form_layout.addLayout(create_field("Parent", self.parent_id_entry), 2, 0)

        self.route_id_entry = QComboBox()
        self.route_id_entry.addItems(self.route_options)
        form_layout.addLayout(create_field("Route", self.route_id_entry), 2, 1)

        # Row 3: Fees
        self.fee_paid_entry = QLineEdit()
        self.fee_paid_entry.setPlaceholderText("0.00")
        form_layout.addLayout(create_field("Fee Paid (₹)", self.fee_paid_entry), 3, 0)

        self.fee_balance_entry = QLineEdit()
        self.fee_balance_entry.setPlaceholderText("0.00")
        form_layout.addLayout(create_field("Fee Balance (₹)", self.fee_balance_entry), 3, 1)

        # Action Buttons Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(0, 15, 0, 0)
        
        self.save_button = QPushButton("Save Student")
        self.save_button.setFixedWidth(180)
        self.save_button.clicked.connect(self.save_student)
        buttons_layout.addWidget(self.save_button)
        
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.setFixedWidth(160)
        self.clear_button.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.clear_button)
        
        form_layout.addLayout(buttons_layout, 4, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        # Center Layout for Form (Horizontal and Vertical)
        h_center_layout = QHBoxLayout()
        h_center_layout.addStretch()
        h_center_layout.addWidget(form_frame)
        h_center_layout.addStretch()

        v_center_layout = QVBoxLayout()
        v_center_layout.addStretch()
        v_center_layout.addLayout(h_center_layout)
        v_center_layout.addStretch()
        
        main_layout.addLayout(v_center_layout)
        main_layout.addStretch()

    def clear_form(self):
        self.student_name_entry.clear()
        self.student_class_entry.clear()
        self.fee_paid_entry.clear()
        self.fee_balance_entry.clear()
        if self.parent_id_entry.count() > 0:
            self.parent_id_entry.setCurrentIndex(0)
        if self.route_id_entry.count() > 0:
            self.route_id_entry.setCurrentIndex(0)
        self.student_name_entry.setFocus()




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
            QMessageBox.information(self, "Success", "Student added successfully!")

        self.clear_form()
