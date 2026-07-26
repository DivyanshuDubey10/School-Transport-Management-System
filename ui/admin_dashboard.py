from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
import sys
import os

def create_initials_avatar(name, size=40, bg_color="#38BDF8", text_color="#0F172A"):
    """Helper to create a circular initials avatar badge."""
    lbl = QLabel()
    lbl.setFixedSize(size, size)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    parts = name.strip().split()
    if len(parts) >= 2:
        initials = (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1 and len(parts[0]) > 0:
        initials = parts[0][:2].upper()
    else:
        initials = "AD"
    lbl.setText(initials)
    radius = size // 2
    lbl.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border-radius: {radius}px; font-weight: 800; font-size: 12pt; border: 1px solid #475569;")
    return lbl

class DashboardHome(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.create_widgets()
        self.load_dashboard_stats()

    def load_dashboard_stats(self):
        try:
            from dal import db_dal
            stats = db_dal.get_dashboard_stats()
            
            self.card1_value.setText(str(stats["total_students"]))
            self.card2_value.setText(str(stats["total_buses"]))
            self.card3_value.setText(str(stats["total_routes"]))
            
        except Exception as e:
            print(f"Error loading stats: {e}")
            self.card1_value.setText("0")
            self.card2_value.setText("0")
            self.card3_value.setText("0")

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)
        
        # 1. Page Header with Title and REFRESH button (matching screenshot)
        header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        self.title_label = QLabel("Admin Dashboard Overview")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: 800; color: #F8FAFC; letter-spacing: -0.5px;")
        title_box.addWidget(self.title_label)
        
        sub_label = QLabel("Live transport metrics, student enrollment summary, and fleet operations.")
        sub_label.setStyleSheet("font-size: 10pt; color: #94A3B8;")
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setFixedSize(130, 38)
        refresh_btn.setStyleSheet("QPushButton { background-color: #1E293B; color: #38BDF8; border: 1.5px solid #38BDF8; border-radius: 6px; font-weight: bold; font-size: 10pt; } QPushButton:hover { background-color: #38BDF8; color: #0F172A; }")
        refresh_btn.clicked.connect(self.load_dashboard_stats)
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        main_layout.addLayout(header_layout)

        # Summary Grid
        self.summary_frame = QFrame()
        grid = QGridLayout(self.summary_frame)
        grid.setContentsMargins(0, 5, 0, 10)
        grid.setSpacing(16)

        def create_kpi_card(title, subtext, val_color="#38BDF8"):
            card = QFrame()
            card.setObjectName("cardFrame")
            card.setStyleSheet("QFrame#cardFrame { background-color: #131C31; border: 1px solid #334155; border-radius: 10px; }")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(18, 18, 18, 18)
            
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #94A3B8; border: none;")
            lbl_val = QLabel("0")
            lbl_val.setStyleSheet(f"font-size: 26pt; font-weight: 800; color: {val_color}; border: none; margin-top: 4px;")
            lbl_sub = QLabel(subtext)
            lbl_sub.setStyleSheet("font-size: 9pt; color: #64748B; border: none;")
            
            layout.addWidget(lbl_title)
            layout.addWidget(lbl_val)
            layout.addWidget(lbl_sub)
            return card, lbl_val

        card1, self.card1_value = create_kpi_card("TOTAL ENROLLED STUDENTS", "Active in School Database", "#38BDF8")
        card2, self.card2_value = create_kpi_card("ACTIVE BUS FLEET", "Operational Transport Vehicles", "#10B981")
        card3, self.card3_value = create_kpi_card("DESIGNATED ROUTES", "City & Suburban Pickup Paths", "#F59E0B")

        grid.addWidget(card1, 0, 0)
        grid.addWidget(card2, 0, 1)
        grid.addWidget(card3, 0, 2)

        main_layout.addWidget(self.summary_frame)

        # Quick Actions Section
        qa_label = QLabel("Quick Actions & Management")
        qa_label.setStyleSheet("font-size: 13pt; font-weight: bold; color: #F8FAFC; margin-top: 10px;")
        main_layout.addWidget(qa_label)

        qa_frame = QFrame()
        qa_layout = QGridLayout(qa_frame)
        qa_layout.setContentsMargins(0, 5, 0, 0)
        qa_layout.setSpacing(14)

        def create_action_btn(text, callback, col, row=0):
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(46)
            btn.setStyleSheet("QPushButton { background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; border-radius: 8px; font-weight: bold; font-size: 10.5pt; padding: 0 16px; text-align: left; } QPushButton:hover { background-color: #2563EB; border-color: #38BDF8; color: #FFFFFF; }")
            btn.clicked.connect(callback)
            qa_layout.addWidget(btn, row, col)
            return btn

        create_action_btn("Enroll New Student", self.app_controller.open_student_management, 0, 0)
        create_action_btn("View Student Directory", self.app_controller.open_student_records, 1, 0)
        create_action_btn("Register New Bus & Route", self.app_controller.open_bus_management, 0, 1)
        create_action_btn("Inspect Fleet Records", self.app_controller.open_bus_records, 1, 1)
        create_action_btn("Register Parent Account", self.app_controller.open_parent_management, 0, 2)
        create_action_btn("View Parent Accounts", self.app_controller.open_parent_records, 1, 2)

        main_layout.addWidget(qa_frame)
        main_layout.addStretch()


class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("School Bus Management System — Admin Portal")
        self.setMinimumSize(1100, 680)
        self.resize(1200, 750)
        self.create_widgets()
        self.show_frame(DashboardHome, self.btn_home)
        
    def show_frame(self, frame_class, active_btn=None):
        if active_btn:
            self.set_active_sidebar_btn(active_btn)
            title_map = {
                DashboardHome: "Admin Portal  /  Dashboard Overview",
                "StudentManagement": "Admin Portal  /  Student Management",
                "StudentRecords": "Admin Portal  /  Student Records Directory",
                "ParentManagement": "Admin Portal  /  Parent Account Registration",
                "ParentRecords": "Admin Portal  /  Parent Accounts Directory",
                "BusManagement": "Admin Portal  /  Bus Fleet & Route Assignment",
                "BusRecords": "Admin Portal  /  Bus Fleet Records"
            }
            name = frame_class.__name__ if hasattr(frame_class, '__name__') else str(frame_class)
            self.header_breadcrumb.setText(title_map.get(frame_class, f"Admin Portal  /  {name}"))

        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if frame_class == DashboardHome:
            frame = DashboardHome(self)
        else:
            frame = frame_class(self)
        
        self.content_layout.addWidget(frame)

    def create_widgets(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Professional Executive Sidebar (Matching Screenshot Structure)
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(240)
        self.sidebar_frame.setObjectName("sidebarFrame")
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(14, 20, 14, 15)
        self.sidebar_layout.setSpacing(8)
        
        # Sidebar Top Layout (Hamburger + Brand Logo)
        sidebar_top_layout = QHBoxLayout()
        self.sidebar_toggle_btn = QPushButton("☰")
        self.sidebar_toggle_btn.setObjectName("toggleBtn")
        self.sidebar_toggle_btn.setFixedSize(38, 38)
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar)
        
        logo_icon = QLabel("M")
        logo_icon.setFixedSize(32, 32)
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setStyleSheet("background-color: #2563EB; color: #FFFFFF; font-weight: 900; font-size: 14pt; border-radius: 16px;")
        
        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        lbl_brand1 = QLabel("School Bus")
        lbl_brand1.setStyleSheet("font-size: 11pt; font-weight: 800; color: #F8FAFC; border: none;")
        lbl_brand2 = QLabel("Management System")
        lbl_brand2.setStyleSheet("font-size: 8.5pt; font-weight: 600; color: #38BDF8; border: none;")
        brand_text.addWidget(lbl_brand1)
        brand_text.addWidget(lbl_brand2)
        
        sidebar_top_layout.addWidget(self.sidebar_toggle_btn)
        sidebar_top_layout.addWidget(logo_icon)
        sidebar_top_layout.addLayout(brand_text)
        sidebar_top_layout.addStretch()
        self.sidebar_layout.addLayout(sidebar_top_layout)
        
        self.sidebar_layout.addSpacing(10)

        # User Profile Card in Sidebar (exactly like screenshot!)
        user_card = QFrame()
        user_card.setStyleSheet("QFrame { background-color: #1E293B; border-radius: 8px; border: 1px solid #334155; }")
        user_card_layout = QHBoxLayout(user_card)
        user_card_layout.setContentsMargins(12, 10, 12, 10)
        user_card_layout.setSpacing(10)
        
        user_avatar = create_initials_avatar("SuperAdmin", size=38, bg_color="#2563EB", text_color="#FFFFFF")
        user_card_layout.addWidget(user_avatar)
        
        user_text = QVBoxLayout()
        user_text.setSpacing(2)
        lbl_uname = QLabel("Administrator")
        lbl_uname.setStyleSheet("font-size: 10pt; font-weight: bold; color: #F8FAFC; border: none;")
        lbl_urole = QLabel("SuperAdmin Portal")
        lbl_urole.setStyleSheet("font-size: 8.5pt; color: #38BDF8; border: none;")
        user_text.addWidget(lbl_uname)
        user_text.addWidget(lbl_urole)
        user_card_layout.addLayout(user_text)
        user_card_layout.addStretch()
        
        self.sidebar_layout.addWidget(user_card)
        self.sidebar_layout.addSpacing(12)

        # Section Header 1: APPLICATION
        cat_app = QLabel("APPLICATION")
        cat_app.setStyleSheet("font-size: 8pt; font-weight: 800; color: #64748B; letter-spacing: 1px; margin-left: 4px; border: none;")
        self.sidebar_layout.addWidget(cat_app)

        self.btn_home = self.add_sidebar_button("Dashboard", lambda: self.show_frame(DashboardHome, self.btn_home))
        self.btn_stu_mgmt = self.add_sidebar_button("Student Management", self.open_student_management)
        self.btn_stu_rec = self.add_sidebar_button("Student Records", self.open_student_records)
        self.btn_par_mgmt = self.add_sidebar_button("Parent Management", self.open_parent_management)
        self.btn_par_rec = self.add_sidebar_button("Parent Records", self.open_parent_records)
        self.btn_bus_mgmt = self.add_sidebar_button("Bus Management", self.open_bus_management)
        self.btn_bus_rec = self.add_sidebar_button("Bus Fleet Records", self.open_bus_records)
        
        self.sidebar_layout.addSpacing(15)

        # Section Header 2: MANAGEMENT
        cat_mgmt = QLabel("MANAGEMENT")
        cat_mgmt.setStyleSheet("font-size: 8pt; font-weight: 800; color: #64748B; letter-spacing: 1px; margin-left: 4px; border: none;")
        self.sidebar_layout.addWidget(cat_mgmt)

        self.btn_logout = self.add_sidebar_button("Logout", self.logout)
        
        self.sidebar_layout.addStretch()

        # Footer (Copyright & Version exactly like screenshot)
        footer_line = QFrame()
        footer_line.setFixedHeight(1)
        footer_line.setStyleSheet("background-color: #1E293B; border: none;")
        self.sidebar_layout.addWidget(footer_line)
        
        footer_layout = QHBoxLayout()
        lbl_copy = QLabel("@2026 Copyright")
        lbl_copy.setStyleSheet("font-size: 8pt; color: #64748B; border: none;")
        lbl_ver = QLabel("version 1.4.0")
        lbl_ver.setStyleSheet("font-size: 8pt; color: #64748B; border: none;")
        footer_layout.addWidget(lbl_copy)
        footer_layout.addStretch()
        footer_layout.addWidget(lbl_ver)
        self.sidebar_layout.addLayout(footer_layout)

        self.main_layout.addWidget(self.sidebar_frame)

        # 2. Main Content Area & Sleek Top Bar
        right_container = QFrame()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top Bar (with toggle button and right-side action icons like screenshot)
        top_bar = QFrame()
        top_bar.setFixedHeight(54)
        top_bar.setStyleSheet("background-color: #0F172A; border-bottom: 1px solid #1E293B;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(15, 6, 20, 6)
        
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setFixedSize(38, 38)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.toggle_btn.hide()
        top_bar_layout.addWidget(self.toggle_btn)
        
        self.header_breadcrumb = QLabel("Admin Portal  /  Dashboard Overview")
        self.header_breadcrumb.setStyleSheet("font-size: 11pt; font-weight: bold; color: #94A3B8; border: none; margin-left: 10px;")
        top_bar_layout.addWidget(self.header_breadcrumb)
        
        top_bar_layout.addStretch()

        # Right-side action badge icons
        status_online = QLabel("System Online")
        status_online.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #10B981; background-color: #064E3B; padding: 4px 10px; border-radius: 12px; border: none;")
        top_bar_layout.addWidget(status_online)
        
        notif_btn = QPushButton("Alerts")
        notif_btn.setFixedSize(54, 34)
        notif_btn.setToolTip("System Notifications")
        notif_btn.setStyleSheet("QPushButton { background-color: #1E293B; border-radius: 6px; font-size: 9.5pt; font-weight: bold; border: 1px solid #334155; color: #94A3B8; } QPushButton:hover { background-color: #334155; color: #F8FAFC; }")
        top_bar_layout.addWidget(notif_btn)

        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFixedHeight(34)
        logout_btn.setStyleSheet("QPushButton { background-color: #EF4444; color: #FFFFFF; border: none; border-radius: 6px; padding: 0px 14px; font-weight: bold; font-size: 9.5pt; } QPushButton:hover { background-color: #DC2626; }")
        logout_btn.clicked.connect(self.logout)
        top_bar_layout.addWidget(logout_btn)

        right_layout.addWidget(top_bar)

        # Content Frame
        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.content_frame, 1)

        self.main_layout.addWidget(right_container, 1)
        self.sidebar_buttons = []
        
        # Register buttons
        self.sidebar_buttons = [self.btn_home, self.btn_stu_mgmt, self.btn_stu_rec, self.btn_par_mgmt, self.btn_par_rec, self.btn_bus_mgmt, self.btn_bus_rec, self.btn_logout]

    def add_sidebar_button(self, text, command):
        btn = QPushButton(text)
        btn.setObjectName("sidebarBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(command)
        btn.setMinimumHeight(38)
        self.sidebar_layout.addWidget(btn)
        return btn

    def set_active_sidebar_btn(self, active_btn):
        for btn in self.sidebar_buttons:
            if btn == active_btn:
                btn.setStyleSheet("QPushButton#sidebarBtn { background-color: #1E293B; color: #38BDF8; border-left: 4px solid #38BDF8; font-weight: 800; text-align: left; padding-left: 12px; }")
            else:
                btn.setStyleSheet("QPushButton#sidebarBtn { background-color: transparent; color: #94A3B8; border: none; font-weight: 600; text-align: left; padding-left: 14px; } QPushButton#sidebarBtn:hover { background-color: #1E293B; color: #F8FAFC; }")

    def toggle_sidebar(self):
        if self.sidebar_frame.isVisible():
            self.sidebar_frame.hide()
            self.toggle_btn.show()
        else:
            self.sidebar_frame.show()
            self.toggle_btn.hide()

    def open_student_management(self):
        from ui.student_management import StudentManagement
        self.show_frame(StudentManagement, self.btn_stu_mgmt)
        
    def open_student_records(self):
        from ui.student_records import StudentRecords
        self.show_frame(StudentRecords, self.btn_stu_rec)
        
    def open_parent_management(self):
        from ui.parent_management import ParentManagement
        self.show_frame(ParentManagement, self.btn_par_mgmt)
        
    def open_parent_records(self):
        from ui.parent_records import ParentRecords
        self.show_frame(ParentRecords, self.btn_par_rec)
        
    def open_bus_management(self):
        from ui.bus_management import BusManagement
        self.show_frame(BusManagement, self.btn_bus_mgmt)
        
    def open_bus_records(self):
        from ui.bus_records import BusRecords
        self.show_frame(BusRecords, self.btn_bus_rec)
        
    def logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()