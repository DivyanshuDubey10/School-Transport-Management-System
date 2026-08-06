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
        init = "ST"
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

class StudentRecords(QWidget):
    def __init__(self, master=None):
        super().__init__()
        self.create_widgets()
        self.load_students()
        
    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(18)

        # 1. Page Header with Title and REFRESH button
        header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_label = QLabel("Student Records Directory")
        title_label.setStyleSheet("font-size: 18pt; font-weight: 800; color: #F8FAFC; letter-spacing: -0.5px;")
        title_box.addWidget(title_label)
        
        sub_label = QLabel("Enrolled student directory, class assignments, parent contacts, and fee balance tracking.")
        sub_label.setStyleSheet("font-size: 10pt; color: #94A3B8;")
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setFixedSize(130, 38)
        refresh_btn.setStyleSheet("QPushButton { background-color: #1E293B; color: #38BDF8; border: 1.5px solid #38BDF8; border-radius: 6px; font-weight: bold; font-size: 10pt; } QPushButton:hover { background-color: #38BDF8; color: #0F172A; }")
        refresh_btn.clicked.connect(self.load_students)
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        main_layout.addLayout(header_layout)

        # 2. Search Bar & Action Buttons
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
        self.delete_button.clicked.connect(self.delete_student)
        search_layout.addWidget(self.delete_button)

        search_layout.addStretch()
        
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search student name, class, or phone...")
        self.search_entry.setFixedWidth(320)
        self.search_entry.textChanged.connect(self.load_students)
        search_layout.addWidget(self.search_entry)
        
        main_layout.addLayout(search_layout)

        # 3. Table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(8)
        self.students_table.setHorizontalHeaderLabels(["ID", "Student Profile", "Class & Route", "Parent Contact", "Address", "Bus", "Fee Paid", "Balance Due"])
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.students_table.setColumnWidth(0, 50)
        self.students_table.setColumnWidth(1, 230)
        self.students_table.setColumnWidth(2, 140)
        self.students_table.setColumnWidth(3, 170)
        self.students_table.setColumnWidth(4, 160)
        self.students_table.setColumnWidth(5, 80)
        self.students_table.setColumnWidth(6, 110)
        self.students_table.setColumnWidth(7, 120)
        header.setStretchLastSection(True)
        
        self.students_table.verticalHeader().setDefaultSectionSize(58)
        self.students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.students_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.students_table.setAlternatingRowColors(True)
        self.students_table.setStyleSheet("QTableWidget { background-color: #0F172A; alternate-background-color: #131C31; border: 1px solid #334155; border-radius: 8px; } QHeaderView::section { background-color: #1E293B; color: #94A3B8; font-weight: bold; font-size: 10pt; padding: 12px; border-bottom: 2px solid #334155; } QTableWidget::item { padding: 8px; font-size: 10.5pt; color: #F8FAFC; }")
        self.students_table.itemSelectionChanged.connect(self.select_student)
        self.students_table.verticalScrollBar().setSingleStep(15)
        main_layout.addWidget(self.students_table)

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

    def select_student(self):
        selected_items = self.students_table.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        self.selected_student = [self.students_table.item(row, col).text() if self.students_table.item(row, col) else "" for col in range(8)]
        self.selected_student_id = self.selected_student[0]

    def load_students(self):
        search_query = self.search_entry.text().strip()
        from dal import db_dal
        students = db_dal.get_all_students(search_query=search_query)

        self.students_table.setRowCount(0)
        for row_idx, row_data in enumerate(students):
            self.students_table.insertRow(row_idx)
            # row_data: (student_id, student_name, student_class, parent_id, parent_phone, address, bus_id, route_id, fee_paid, fee_balance)
            s_id = str(row_data[0])
            s_name = str(row_data[1])
            s_class = str(row_data[2])
            p_phone = str(row_data[4]) if row_data[4] else "N/A"
            addr = str(row_data[5]) if row_data[5] else "N/A"
            bus_id = str(row_data[6]) if row_data[6] else "N/A"
            route_id = str(row_data[7]) if row_data[7] else "N/A"
            f_paid = str(row_data[8])
            f_bal = str(row_data[9])

            self.students_table.setItem(row_idx, 0, QTableWidgetItem(s_id))
            self.students_table.setItem(row_idx, 1, QTableWidgetItem(s_name))
            self.students_table.setItem(row_idx, 2, QTableWidgetItem(s_class))
            self.students_table.setItem(row_idx, 3, QTableWidgetItem(p_phone))
            self.students_table.setItem(row_idx, 4, QTableWidgetItem(addr))
            self.students_table.setItem(row_idx, 5, QTableWidgetItem(bus_id))
            self.students_table.setItem(row_idx, 6, QTableWidgetItem(f_paid))
            self.students_table.setItem(row_idx, 7, QTableWidgetItem(f_bal))

        total = len(students)
        self.lbl_total_rows.setText(f"Rows per page:  15    •    1-{total} of {total} items")

    def delete_student(self):
        if not hasattr(self, "selected_student_id"):
            QMessageBox.critical(self, "Error", "Please select a student from the table first.")
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
        dialog.setWindowTitle("Update Student Profile")
        dialog.setFixedSize(420, 340)
        dialog.setStyleSheet("QDialog { background-color: #1E293B; color: #F8FAFC; } QLabel { color: #F8FAFC; font-weight: bold; font-size: 10pt; } QLineEdit { background-color: #0F172A; border: 1px solid #334155; border-radius: 6px; padding: 6px; color: #F8FAFC; font-size: 10pt; }")
        
        layout = QFormLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        name_entry = QLineEdit(self.selected_student[1])
        class_entry = QLineEdit(self.selected_student[2])
        parent_entry = QLineEdit(self.selected_student[3])
        route_entry = QLineEdit(self.selected_student[7])
        fee_paid_entry = QLineEdit(self.selected_student[6])
        fee_balance_entry = QLineEdit(self.selected_student[7])
        
        layout.addRow("Student Name:", name_entry)
        layout.addRow("Student Class:", class_entry)
        layout.addRow("Parent ID:", parent_entry)
        layout.addRow("Route ID:", route_entry)
        layout.addRow("Fee Paid (₹):", fee_paid_entry)
        layout.addRow("Fee Balance (₹):", fee_balance_entry)

        save_btn = QPushButton("Save Profile Changes")
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet("QPushButton { background-color: #10B981; color: #FFFFFF; border: none; border-radius: 6px; font-weight: bold; font-size: 10.5pt; margin-top: 10px; } QPushButton:hover { background-color: #059669; }")
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