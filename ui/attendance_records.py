from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dal import db_dal

class AttendanceRecordsView(QWidget):
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.load_attendance()

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_label = QLabel("Student Attendance Records")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #38BDF8;")
        title_box.addWidget(title_label)
        
        sub_label = QLabel("View daily attendance marked by bus drivers.")
        sub_label.setStyleSheet("font-size: 10pt; color: #94A3B8;")
        title_box.addWidget(sub_label)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedSize(100, 38)
        refresh_btn.setStyleSheet("QPushButton { background-color: #1E293B; color: #38BDF8; border: 1.5px solid #38BDF8; border-radius: 6px; font-weight: bold; font-size: 10pt; }")
        refresh_btn.clicked.connect(self.load_attendance)
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignBottom)
        
        main_layout.addLayout(header_layout)

        # Search Bar
        search_layout = QHBoxLayout()
        search_layout.addStretch()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Student Name or Bus Number...")
        self.search_entry.setFixedWidth(300)
        self.search_entry.textChanged.connect(self.load_attendance)
        search_layout.addWidget(self.search_entry)
        main_layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Student Name", "Class", "Bus Number", "Status"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("QTableWidget { background-color: #0F172A; alternate-background-color: #131C31; border: 1px solid #334155; border-radius: 8px; } QHeaderView::section { background-color: #1E293B; color: #94A3B8; font-weight: bold; font-size: 10pt; padding: 10px; border-bottom: 2px solid #334155; } QTableWidget::item { padding: 8px 12px; font-size: 10.5pt; color: #F8FAFC; }")
        
        main_layout.addWidget(self.table)

    def load_attendance(self):
        query = self.search_entry.text().strip()
        records = db_dal.get_attendance_history_for_admin(query)
        
        self.table.setRowCount(0)
        for row_idx, record in enumerate(records):
            # date, student_name, student_class, bus_number, status
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(record[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(record[1]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(record[2]))
            self.table.setItem(row_idx, 3, QTableWidgetItem(record[3]))
            
            status = record[4]
            status_item = QTableWidgetItem(status)
            if status == "Present":
                status_item.setForeground(Qt.GlobalColor.green)
            elif status == "Absent":
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row_idx, 4, status_item)
