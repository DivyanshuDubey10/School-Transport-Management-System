from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLineEdit, QMessageBox, QSpacerItem, QSizePolicy, QDialog, QComboBox)
from PyQt6.QtCore import Qt, QDate
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dal import db_dal

class RouteMapView(QWidget):
    def __init__(self, driver_dashboard):
        super().__init__()
        self.driver_dashboard = driver_dashboard
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        
        title = QLabel("My Route Map")
        title.setStyleSheet("font-size: 18pt; font-weight: 800; color: #F8FAFC;")
        layout.addWidget(title)
        
        sub = QLabel("Stops and student counts for your route.")
        sub.setStyleSheet("font-size: 10pt; color: #94A3B8;")
        layout.addWidget(sub)
        
        layout.addSpacing(15)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.setSpacing(15)
        
        # Group students by pickup point
        bus_id = self.driver_dashboard.bus_id
        students = db_dal.get_students_by_bus(bus_id)
        
        stops = {}
        for s in students:
            # s: s_id, s_name, s_class, p_pickup, p_phone, p_name
            pickup = s[3]
            if pickup not in stops:
                stops[pickup] = []
            stops[pickup].append(s[1])
            
        if not stops:
            lbl = QLabel("No students assigned to this route.")
            lbl.setStyleSheet("color: #94A3B8;")
            content_layout.addWidget(lbl)
        else:
            for idx, (stop, st_list) in enumerate(stops.items()):
                card = QFrame()
                card.setStyleSheet("background-color: #1E293B; border-radius: 8px; border: 1px solid #334155; padding: 10px;")
                cl = QVBoxLayout(card)
                
                header = QLabel(f"Stop {idx+1}: {stop}")
                header.setStyleSheet("font-size: 12pt; font-weight: bold; color: #38BDF8; border: none;")
                cl.addWidget(header)
                
                desc = QLabel(f"{len(st_list)} Students: {', '.join(st_list)}")
                desc.setStyleSheet("font-size: 10pt; color: #F8FAFC; border: none;")
                desc.setWordWrap(True)
                cl.addWidget(desc)
                
                content_layout.addWidget(card)
                
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

class MyStudentsView(QWidget):
    def __init__(self, driver_dashboard):
        super().__init__()
        self.driver_dashboard = driver_dashboard
        self.create_widgets()

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(18)

        # Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_label = QLabel("My Bus Route Students")
        title_label.setStyleSheet("font-size: 18pt; font-weight: 800; color: #F8FAFC; letter-spacing: -0.5px;")
        title_box.addWidget(title_label)
        
        sub_label = QLabel("View students assigned to your bus and mark daily attendance.")
        sub_label.setStyleSheet("font-size: 10pt; color: #94A3B8;")
        title_box.addWidget(sub_label)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # Date Picker for Attendance
        self.date_label = QLabel(f"Attendance Date: {QDate.currentDate().toString('yyyy-MM-dd')}")
        self.date_label.setStyleSheet("font-size: 11pt; color: #38BDF8; font-weight: bold;")
        header_layout.addWidget(self.date_label, alignment=Qt.AlignmentFlag.AlignBottom)

        mark_all_btn = QPushButton("Mark All Present")
        mark_all_btn.setFixedSize(140, 38)
        mark_all_btn.setStyleSheet("QPushButton { background-color: #10B981; color: white; border-radius: 6px; font-weight: bold; font-size: 10pt; } QPushButton:hover { background-color: #059669; }")
        mark_all_btn.clicked.connect(self.mark_all_present)
        header_layout.addWidget(mark_all_btn, alignment=Qt.AlignmentFlag.AlignBottom)

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setFixedSize(100, 38)
        refresh_btn.setStyleSheet("QPushButton { background-color: #1E293B; color: #38BDF8; border: 1.5px solid #38BDF8; border-radius: 6px; font-weight: bold; font-size: 10pt; }")
        refresh_btn.clicked.connect(self.load_students)
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignBottom)
        
        main_layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Student Name", "Class", "Pickup Point", "Parent Phone", "Status (Today)", "Action"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("QTableWidget { background-color: #0F172A; alternate-background-color: #131C31; border: 1px solid #334155; border-radius: 8px; } QHeaderView::section { background-color: #1E293B; color: #94A3B8; font-weight: bold; font-size: 10pt; padding: 10px; border-bottom: 2px solid #334155; } QTableWidget::item { padding: 8px 12px; font-size: 10.5pt; color: #F8FAFC; }")
        
        main_layout.addWidget(self.table)
        
        self.load_students()

    def load_students(self):
        bus_id = self.driver_dashboard.bus_id
        students = db_dal.get_students_by_bus(bus_id)
        today = QDate.currentDate().toString("yyyy-MM-dd")
        
        attendance_records = db_dal.get_attendance_by_bus_and_date(bus_id, today)
        attendance_map = {record[0]: record[1] for record in attendance_records}

        self.table.setRowCount(0)
        for row_idx, student in enumerate(students):
            s_id, s_name, s_class, p_pickup, p_phone, p_name = student
            self.table.insertRow(row_idx)
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(s_name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(s_class))
            self.table.setItem(row_idx, 2, QTableWidgetItem(p_pickup))
            self.table.setItem(row_idx, 3, QTableWidgetItem(p_phone))
            
            current_status = attendance_map.get(s_id, "Not Marked")
            status_item = QTableWidgetItem(current_status)
            if current_status == "Present":
                status_item.setForeground(Qt.GlobalColor.green)
            elif current_status == "Absent":
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row_idx, 4, status_item)

            # Actions
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(5, 5, 5, 5)
            
            present_btn = QPushButton("Present")
            present_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            present_btn.setStyleSheet("QPushButton { background-color: #059669; color: white; border-radius: 4px; padding: 6px; font-weight: bold; } QPushButton:hover { background-color: #10B981; }")
            present_btn.clicked.connect(lambda checked, sid=s_id: self.mark_attendance(sid, "Present"))
            
            absent_btn = QPushButton("Absent")
            absent_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            absent_btn.setStyleSheet("QPushButton { background-color: #B91C1C; color: white; border-radius: 4px; padding: 6px; font-weight: bold; } QPushButton:hover { background-color: #EF4444; }")
            absent_btn.clicked.connect(lambda checked, sid=s_id: self.mark_attendance(sid, "Absent"))
            
            action_layout.addWidget(present_btn)
            action_layout.addWidget(absent_btn)
            
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 5, action_widget)

    def mark_attendance(self, student_id, status):
        bus_id = self.driver_dashboard.bus_id
        today = QDate.currentDate().toString("yyyy-MM-dd")
        if db_dal.mark_attendance(student_id, bus_id, today, status):
            self.load_students()
        else:
            QMessageBox.critical(self, "Error", "Failed to mark attendance.")

    def mark_all_present(self):
        bus_id = self.driver_dashboard.bus_id
        today = QDate.currentDate().toString("yyyy-MM-dd")
        students = db_dal.get_students_by_bus(bus_id)
        for s in students:
            db_dal.mark_attendance(s[0], bus_id, today, "Present")
        self.load_students()
class DriverDashboard(QWidget):
    def __init__(self, bus_id):
        super().__init__()
        self.bus_id = bus_id
        self.setWindowTitle("NeoYatra — Driver Portal")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 750)
        
        self.fetch_data()
        self.create_widgets()
        self.show_frame(MyStudentsView, self.btn_students)

    def fetch_data(self):
        pass

    def create_widgets(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        content_widget = QWidget()
        self.main_layout = QHBoxLayout(content_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        root_layout.addWidget(content_widget)

        self.sidebar_buttons = []
        
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(240)
        self.sidebar_frame.setObjectName("sidebarFrame")
        self.sidebar_frame.setStyleSheet("QFrame#sidebarFrame { background-color: #1E293B; }")
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(14, 20, 14, 15)
        self.sidebar_layout.setSpacing(8)

        sidebar_top_layout = QHBoxLayout()
        logo_icon = QLabel("D")
        logo_icon.setFixedSize(32, 32)
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setStyleSheet("background-color: #10B981; color: #FFFFFF; font-weight: 900; font-size: 14pt; border-radius: 16px;")
        
        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        lbl_brand1 = QLabel("NeoYatra")
        lbl_brand1.setStyleSheet("font-size: 11pt; font-weight: 800; color: #F8FAFC; border: none;")
        lbl_brand2 = QLabel("Driver Portal")
        lbl_brand2.setStyleSheet("font-size: 8.5pt; font-weight: 600; color: #10B981; border: none;")
        brand_text.addWidget(lbl_brand1)
        brand_text.addWidget(lbl_brand2)
        
        sidebar_top_layout.addWidget(logo_icon)
        sidebar_top_layout.addLayout(brand_text)
        sidebar_top_layout.addStretch()
        self.sidebar_layout.addLayout(sidebar_top_layout)
        
        self.sidebar_layout.addSpacing(25)

        cat_app = QLabel("APPLICATION")
        cat_app.setStyleSheet("font-size: 8pt; font-weight: 800; color: #64748B; letter-spacing: 1px; margin-left: 4px; border: none;")
        self.sidebar_layout.addWidget(cat_app)

        self.btn_students = self.add_sidebar_button("My Route Students", lambda: self.show_frame(MyStudentsView, self.btn_students))
        self.btn_route_map = self.add_sidebar_button("My Route Map", lambda: self.show_frame(RouteMapView, self.btn_route_map))
        
        self.sidebar_layout.addStretch()
        
        self.btn_sos = QPushButton("EMERGENCY SOS")
        self.btn_sos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sos.setFixedHeight(40)
        self.btn_sos.setStyleSheet("QPushButton { background-color: #7F1D1D; color: #FFFFFF; font-weight: bold; border-radius: 6px; border: 1px solid #DC2626; } QPushButton:hover { background-color: #991B1B; }")
        self.btn_sos.clicked.connect(self.trigger_sos)
        self.sidebar_layout.addWidget(self.btn_sos)
        self.sidebar_layout.addSpacing(10)

        self.btn_logout = self.add_sidebar_button("Logout", self.logout)
        self.main_layout.addWidget(self.sidebar_frame)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        top_bar = QFrame()
        top_bar.setFixedHeight(54)
        top_bar.setStyleSheet("background-color: #0F172A; border-bottom: 1px solid #1E293B;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(15, 6, 20, 6)
        
        self.header_breadcrumb = QLabel(f"Driver Portal")
        self.header_breadcrumb.setStyleSheet("font-size: 11pt; font-weight: bold; color: #94A3B8; border: none; margin-left: 10px;")
        top_bar_layout.addWidget(self.header_breadcrumb)
        top_bar_layout.addStretch()
        
        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFixedHeight(34)
        logout_btn.setStyleSheet("QPushButton { background-color: #EF4444; color: #FFFFFF; border: none; border-radius: 6px; padding: 0px 14px; font-weight: bold; font-size: 9.5pt; }")
        logout_btn.clicked.connect(self.logout)
        top_bar_layout.addWidget(logout_btn)
        
        right_layout.addWidget(top_bar)

        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        right_layout.addWidget(self.content_frame, 1)
        self.main_layout.addLayout(right_layout, 1)

    def add_sidebar_button(self, text, command):
        btn = QPushButton(text)
        btn.setObjectName("sidebarBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(command)
        self.sidebar_layout.addWidget(btn)
        self.sidebar_buttons.append(btn)
        return btn

    def set_active_sidebar_btn(self, active_btn):
        for btn in self.sidebar_buttons:
            if btn == active_btn:
                btn.setStyleSheet("QPushButton#sidebarBtn { background-color: #0F172A; color: #10B981; border-left: 4px solid #10B981; font-weight: 800; }")
            else:
                btn.setStyleSheet("QPushButton#sidebarBtn { background-color: transparent; color: #94A3B8; border: none; font-weight: 600; }")

    def show_frame(self, frame_class, active_btn=None):
        if active_btn:
            self.set_active_sidebar_btn(active_btn)

        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        frame = frame_class(self)
        self.content_layout.addWidget(frame)

    def logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def trigger_sos(self):
        QMessageBox.warning(self, "Emergency SOS", "SOS Alert Sent to Administration!\n\nPlease stay calm and await instructions.")
