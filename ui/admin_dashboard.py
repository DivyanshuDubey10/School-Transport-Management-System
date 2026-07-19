from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QScrollArea
from PyQt6.QtCore import Qt

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
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        self.title_label = QLabel("School Transport Management System")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        # Welcome
        self.welcome_label = QLabel("Welcome, Admin! Here's your system overview:")
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.welcome_label)

        # Summary Grid
        self.summary_frame = QFrame()
        grid = QGridLayout(self.summary_frame)

        # Card 1
        card1 = QFrame()
        card1.setStyleSheet("background-color: #333333; border-radius: 10px; padding: 20px;")
        card1_layout = QVBoxLayout(card1)
        card1_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card1_title = QLabel("Total Students")
        self.card1_value = QLabel("0")
        self.card1_value.setStyleSheet("font-size: 36px; font-weight: bold; color: #1f538d;")
        card1_layout.addWidget(card1_title)
        card1_layout.addWidget(self.card1_value)
        grid.addWidget(card1, 0, 0)

        # Card 2
        card2 = QFrame()
        card2.setStyleSheet("background-color: #333333; border-radius: 10px; padding: 20px;")
        card2_layout = QVBoxLayout(card2)
        card2_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card2_title = QLabel("Active Buses")
        self.card2_value = QLabel("0")
        self.card2_value.setStyleSheet("font-size: 36px; font-weight: bold; color: #1f538d;")
        card2_layout.addWidget(card2_title)
        card2_layout.addWidget(self.card2_value)
        grid.addWidget(card2, 0, 1)

        # Card 3
        card3 = QFrame()
        card3.setStyleSheet("background-color: #333333; border-radius: 10px; padding: 20px;")
        card3_layout = QVBoxLayout(card3)
        card3_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card3_title = QLabel("Total Routes")
        self.card3_value = QLabel("0")
        self.card3_value.setStyleSheet("font-size: 36px; font-weight: bold; color: #1f538d;")
        card3_layout.addWidget(card3_title)
        card3_layout.addWidget(self.card3_value)
        grid.addWidget(card3, 0, 2)

        main_layout.addWidget(self.summary_frame)

        # Quick Actions
        qa_label = QLabel("Quick Actions")
        qa_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        qa_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(qa_label)

        qa_frame = QFrame()
        qa_layout = QHBoxLayout(qa_frame)
        qa_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_add_student = QPushButton("Add New Student")
        btn_add_student.clicked.connect(self.app_controller.open_student_management)
        qa_layout.addWidget(btn_add_student)

        btn_view_students = QPushButton("View Students")
        btn_view_students.clicked.connect(self.app_controller.open_student_records)
        qa_layout.addWidget(btn_view_students)

        btn_manage_buses = QPushButton("Manage Buses")
        btn_manage_buses.clicked.connect(self.app_controller.open_bus_management)
        qa_layout.addWidget(btn_manage_buses)

        btn_view_routes = QPushButton("View Routes")
        btn_view_routes.clicked.connect(self.app_controller.open_route_records)
        qa_layout.addWidget(btn_view_routes)

        main_layout.addWidget(qa_frame)
        main_layout.addStretch()


class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        self.setFixedSize(900, 600)
        self.create_widgets()
        self.show_frame(DashboardHome)
        
    def show_frame(self, frame_class):
        # Remove existing widgets in content layout
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

        # Sidebar
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(200)
        self.sidebar_frame.setStyleSheet("background-color: #222222;")
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        
        # Sidebar Close Button
        self.close_sidebar_btn = QPushButton("×")
        self.close_sidebar_btn.setStyleSheet("font-size: 20px; font-weight: bold; background: transparent; color: white;")
        self.close_sidebar_btn.clicked.connect(self.toggle_sidebar)
        self.sidebar_layout.addWidget(self.close_sidebar_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Title
        self.sidebar_title = QLabel("STMS")
        self.sidebar_title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        self.sidebar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(self.sidebar_title)
        
        # Sidebar Buttons
        self.add_sidebar_button("Dashboard", lambda: self.show_frame(DashboardHome))
        self.add_sidebar_button("Student Management", self.open_student_management)
        self.add_sidebar_button("Student Records", self.open_student_records)
        self.add_sidebar_button("Parent Management", self.open_parent_management)
        self.add_sidebar_button("Parent Records", self.open_parent_records)
        self.add_sidebar_button("Bus Management", self.open_bus_management)
        self.add_sidebar_button("Route Management", self.open_route_management)
        self.add_sidebar_button("Route Records", self.open_route_records)
        
        self.sidebar_layout.addStretch()

        self.add_sidebar_button("Logout", self.logout)

        self.main_layout.addWidget(self.sidebar_frame)

        # Main Content Area
        self.right_container = QFrame()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        # Top bar
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(50)
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(10, 0, 0, 0)

        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setStyleSheet("font-size: 20px; font-weight: bold; background: transparent; color: white;")
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.top_bar_layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.right_layout.addWidget(self.top_bar)

        # Content Frame
        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.right_layout.addWidget(self.content_frame)

        self.main_layout.addWidget(self.right_container)

    def add_sidebar_button(self, text, command):
        btn = QPushButton(text)
        btn.clicked.connect(command)
        btn.setMinimumHeight(40)
        btn.setStyleSheet("text-align: left; padding-left: 15px; border-radius: 0px;")
        self.sidebar_layout.addWidget(btn)

    def toggle_sidebar(self):
        if self.sidebar_frame.isVisible():
            self.sidebar_frame.hide()
        else:
            self.sidebar_frame.show()

    def open_student_management(self):
        from ui.student_management import StudentManagement
        self.show_frame(StudentManagement)
        
    def open_student_records(self):
        from ui.student_records import StudentRecords
        self.show_frame(StudentRecords)
        
    def open_parent_management(self):
        from ui.parent_management import ParentManagement
        self.show_frame(ParentManagement)
        
    def open_parent_records(self):
        from ui.parent_records import ParentRecords
        self.show_frame(ParentRecords)
        
    def open_bus_management(self):
        from ui.bus_management import BusManagement
        self.show_frame(BusManagement)
        
    def open_route_management(self):
        from ui.route_management import RouteManagement
        self.show_frame(RouteManagement)
        
    def open_route_records(self):
        from ui.route_records import RouteRecords
        self.show_frame(RouteRecords)

    def logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()