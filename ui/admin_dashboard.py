from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
import sys
import os
from theme_manager import apply_shadow


def create_initials_avatar(name, size=40, bg_color="#38BDF8", text_color="#FFFFFF"):
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
    lbl.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border-radius: {radius}px; font-weight: 800; font-size: 12pt; ")
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
            
            # Occupancy Ring
            occupancy_data = db_dal.get_route_occupancy()
            total_students = sum(d[1] for d in occupancy_data)
            total_capacity = sum(d[2] for d in occupancy_data)
            if total_capacity > 0:
                self.progress_occupancy.set_value((total_students / total_capacity) * 100, max_val=100)
                
            # Fee Ring
            fee_data = db_dal.get_fee_status_distribution()
            total_paid = fee_data['fully_paid']
            total_pending = fee_data['pending']
            total_fees = total_paid + total_pending
            if total_fees > 0:
                self.progress_fee.set_value((total_paid / total_fees) * 100, max_val=100)
            
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
        self.title_label
        title_box.addWidget(self.title_label)
        
        sub_label = QLabel("Live transport metrics, student enrollment summary, and fleet operations.")
        sub_label
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        
        main_layout.addLayout(header_layout)

        # Summary Grid
        self.summary_frame = QFrame()
        grid = QGridLayout(self.summary_frame)
        grid.setContentsMargins(0, 5, 0, 10)
        grid.setSpacing(16)

        def create_kpi_card(title, subtext, val_color="#38BDF8"):
            card = QFrame()
            card.setObjectName("statCard")
            apply_shadow(card)
            card.setStyleSheet("QFrame#cardFrame {   border-radius: 10px; }")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(18, 18, 18, 18)
            
            lbl_title = QLabel(title)
            lbl_title
            lbl_val = QLabel("0")
            lbl_val.setStyleSheet(f"font-size: 26pt; font-weight: 800; color: {val_color}; border: none; margin-top: 4px;")
            lbl_sub = QLabel(subtext)
            lbl_sub
            
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

        # Circular Progress Section
        progress_layout = QHBoxLayout()
        progress_layout.setContentsMargins(10, 10, 10, 20)
        progress_layout.setSpacing(40)
        
        from ui.components.circular_progress import CircularProgress
        self.progress_occupancy = CircularProgress(self, color="#38BDF8", title="Avg Occupancy")
        self.progress_fee = CircularProgress(self, color="#10B981", title="Fee Paid %")
        
        progress_layout.addWidget(self.progress_occupancy)
        progress_layout.addWidget(self.progress_fee)
        progress_layout.addStretch()
        
        main_layout.addLayout(progress_layout)

        # Quick Actions Section
        qa_label = QLabel("Quick Actions & Management")
        qa_label
        main_layout.addWidget(qa_label)

        qa_frame = QFrame()
        qa_layout = QGridLayout(qa_frame)
        qa_layout.setContentsMargins(0, 5, 0, 0)
        qa_layout.setSpacing(14)

        def create_action_btn(text, callback, col, row=0):
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(46)
            btn.setObjectName("actionButton")
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
        self.setWindowTitle("NeoYatra — Admin Portal")
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
                "BusRecords": "Admin Portal  /  Bus Fleet Records",
                "AttendanceRecordsView": "Admin Portal  /  Student Attendance Records",
                "ProfileView": "Admin Portal  /  Personal Profile & Security",
                "SettingsView": "Admin Portal  /  System Settings & Preferences"
            }
            name = frame_class.__name__ if hasattr(frame_class, '__name__') else str(frame_class)
            self.header_breadcrumb.setText(title_map.get(frame_class, title_map.get(name, f"Admin Portal  /  {name}")))

        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if frame_class == DashboardHome:
            frame = DashboardHome(self)
        elif hasattr(frame_class, '__name__') and frame_class.__name__ == "ProfileView":
            frame = frame_class('admin', user_id=1, dashboard_ref=self)
        elif hasattr(frame_class, '__name__') and frame_class.__name__ == "SettingsView":
            frame = frame_class('admin', dashboard_ref=self)
        else:
            frame = frame_class(self)
        
        self.content_layout.addWidget(frame)

    def create_widgets(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        content_widget = QWidget()
        self.main_layout = QHBoxLayout(content_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        root_layout.addWidget(content_widget)

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
        
        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        lbl_brand1 = QLabel("NeoYatra")
        lbl_brand1.setObjectName("pageTitle")
        lbl_brand2 = QLabel("Transport Portal")
        lbl_brand2.setObjectName("statDesc")
        brand_text.addWidget(lbl_brand1)
        brand_text.addWidget(lbl_brand2)
        
        sidebar_top_layout.addWidget(self.sidebar_toggle_btn)
        sidebar_top_layout.addSpacing(10)
        sidebar_top_layout.addLayout(brand_text)
        sidebar_top_layout.addStretch()
        self.sidebar_layout.addLayout(sidebar_top_layout)
        
        self.sidebar_layout.addSpacing(10)

        # User Profile Card in Sidebar (exactly like screenshot!)
        user_card = QFrame()
        user_card.setStyleSheet("QFrame {  border-radius: 8px;  }")
        user_card_layout = QHBoxLayout(user_card)
        user_card_layout.setContentsMargins(12, 10, 12, 10)
        user_card_layout.setSpacing(10)
        
        self.user_avatar = create_initials_avatar("SuperAdmin", size=38, bg_color="#2563EB", text_color="#FFFFFF")
        user_card_layout.addWidget(self.user_avatar)
        
        user_text = QVBoxLayout()
        user_text.setSpacing(2)
        self.lbl_uname = QLabel("Administrator")
        self.lbl_uname.setObjectName("statTitle")
        lbl_urole = QLabel("Admin")
        lbl_urole.setObjectName("statDesc")
        user_text.addWidget(self.lbl_uname)
        user_text.addWidget(lbl_urole)
        user_card_layout.addLayout(user_text)
        user_card_layout.addStretch()
        
        self.sidebar_layout.addWidget(user_card)
        self.sidebar_layout.addSpacing(12)

        self.btn_home = self.add_sidebar_button("Dashboard", lambda: self.show_frame(DashboardHome, self.btn_home))
        self.btn_stu_mgmt = self.add_sidebar_button("Student Management", self.open_student_management)
        self.btn_stu_rec = self.add_sidebar_button("Student Records", self.open_student_records)
        self.btn_par_mgmt = self.add_sidebar_button("Parent Management", self.open_parent_management)
        self.btn_par_rec = self.add_sidebar_button("Parent Records", self.open_parent_records)
        self.btn_bus_mgmt = self.add_sidebar_button("Bus Management", self.open_bus_management)
        self.btn_bus_rec = self.add_sidebar_button("Bus Fleet Records", self.open_bus_records)
        self.btn_attendance = self.add_sidebar_button("Attendance Records", self.open_attendance_records)
        
        self.sidebar_layout.addSpacing(15)

        

        self.btn_profile = self.add_sidebar_button("Profile & Security", self.open_profile_view)
        self.btn_settings = self.add_sidebar_button("System Settings", self.open_settings_view)
        self.btn_logout = self.add_sidebar_button("Logout", self.logout)
        
        self.sidebar_layout.addStretch()

        # Footer (Copyright & Version exactly like screenshot)
        footer_line = QFrame()
        footer_line.setFixedHeight(1)
        footer_line
        self.sidebar_layout.addWidget(footer_line)
        
        footer_layout = QHBoxLayout()
        lbl_copy = QLabel("@2026 Copyright")
        lbl_copy
        lbl_ver = QLabel("version 1.4.0")
        lbl_ver
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
        top_bar.setObjectName("topBar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(15, 6, 20, 6)
        
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setFixedSize(38, 38)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.toggle_btn.hide()
        top_bar_layout.addWidget(self.toggle_btn)
        
        self.header_breadcrumb = QLabel("Admin Portal  /  Dashboard Overview")
        self.header_breadcrumb
        top_bar_layout.addWidget(self.header_breadcrumb)
        
        top_bar_layout.addStretch()

        # Right-side action badge icons
        # System Online and Alerts have been removed

        # Theme Toggle
        self.theme_btn = QPushButton("Night Mode")
        self.theme_btn.setObjectName("secondaryButton")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setStyleSheet("QPushButton { font-size: 11pt; border: none; background: transparent; font-weight: bold; color: #64748B; padding: 4px 10px; } QPushButton:hover { color: #38BDF8; }")
        self.theme_btn.clicked.connect(self.toggle_theme)
        from theme_manager import ThemeManager
        if ThemeManager.get_instance().get_current_theme() == "dark":
            self.theme_btn.setText("Day Mode")
        top_bar_layout.addWidget(self.theme_btn)
        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFixedHeight(34)
        logout_btn.setObjectName("dangerButton")
        logout_btn.clicked.connect(self.logout)
        top_bar_layout.addWidget(logout_btn)

        right_layout.addWidget(top_bar)

        # Content Frame
        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.content_frame, 1)

        self.main_layout.addWidget(right_container, 1)
        
        # Register buttons
        self.sidebar_buttons = [self.btn_home, self.btn_stu_mgmt, self.btn_stu_rec, self.btn_par_mgmt, self.btn_par_rec, self.btn_bus_mgmt, self.btn_bus_rec, self.btn_attendance, self.btn_profile, self.btn_settings, self.btn_logout]

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
                btn.setStyleSheet("QPushButton#sidebarBtn {  color: #38BDF8; border-left: 4px solid #38BDF8; font-weight: 800; text-align: left; padding-left: 12px; }")
            else:
                btn.setStyleSheet("QPushButton#sidebarBtn { background-color: transparent;  border: none; font-weight: 600; text-align: left; padding-left: 14px; } QPushButton#sidebarBtn:hover {   }")

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
        
    def open_attendance_records(self):
        from ui.attendance_records import AttendanceRecordsView
        self.show_frame(AttendanceRecordsView, self.btn_attendance)
        
    def open_profile_view(self):
        from ui.profile_view import ProfileView
        self.show_frame(ProfileView, self.btn_profile)
        
    def open_settings_view(self):
        from ui.settings_view import SettingsView
        self.show_frame(SettingsView, self.btn_settings)

    def update_user_display(self):
        from dal import db_dal
        admin_data = db_dal.get_admin_by_id(1)
        if admin_data:
            fname = admin_data[3]
            self.lbl_uname.setText(fname)
            new_avatar = create_initials_avatar(fname, size=38, bg_color="#2563EB", text_color="#FFFFFF")
            self.user_avatar.deleteLater()
            self.user_avatar = new_avatar
            self.user_avatar.setParent(self.lbl_uname.parentWidget())
            self.lbl_uname.parentWidget().layout().insertWidget(0, self.user_avatar)
        
    def toggle_theme(self):
        from theme_manager import ThemeManager
        tm = ThemeManager.get_instance()
        mode = tm.toggle_theme()
        if mode == "dark":
            self.theme_btn.setText("Day Mode")
        else:
            self.theme_btn.setText("Night Mode")

    def logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
