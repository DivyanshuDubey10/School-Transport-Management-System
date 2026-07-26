from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLineEdit)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class ChildrenView(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.parent_dashboard = parent_dashboard
        self.create_widgets()

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Top Header
        header_layout = QHBoxLayout()
        title_label = QLabel(f"Welcome, {self.parent_dashboard.parent_name}")
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet("font-size: 20pt; font-weight: 800; color: #38BDF8; letter-spacing: -0.5px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        subtitle_label = QLabel("Your Children's Transport Details")
        subtitle_label.setStyleSheet("font-size: 15pt; font-weight: bold; color: #F8FAFC;")
        subtitle_label.setContentsMargins(0, 5, 0, 10)
        main_layout.addWidget(subtitle_label)

        # Scroll Area for Cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        self.populate_cards()

    def populate_cards(self):
        children = self.parent_dashboard.children_records
        if not children:
            no_record_label = QLabel("No transport records found for your children.")
            no_record_label.setStyleSheet("font-size: 12pt; color: #94A3B8;")
            no_record_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            empty_frame = QFrame()
            empty_frame.setObjectName("cardFrame")
            empty_layout = QVBoxLayout(empty_frame)
            empty_layout.setContentsMargins(30, 30, 30, 30)
            empty_layout.addWidget(no_record_label)
            self.scroll_layout.addWidget(empty_frame)
        else:
            for child in children:
                self.create_child_card(child)

    def create_child_card(self, child):
        # child format: s.student_name, s.student_class, s.fee_paid, s.fee_balance, b.bus_number, b.driver_name, b.driver_phone, r.route_name, p.pickup_point
        s_name, s_class, fee_paid, fee_balance, bus_no, drv_name, drv_phone, r_name, p_pickup = child
        
        card = QFrame()
        card.setObjectName("cardFrame")
        
        card_layout = QGridLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # Child Header
        header_label = QLabel(f"{s_name} (Class {s_class})")
        header_label.setStyleSheet("font-size: 15pt; font-weight: bold; color: #38BDF8; border: none;")
        card_layout.addWidget(header_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Fee Details
        fee_frame = QFrame()
        fee_frame.setStyleSheet("border: none;")
        fee_layout = QVBoxLayout(fee_frame)
        fee_layout.setContentsMargins(0, 0, 0, 0)
        fee_layout.setSpacing(5)
        
        fee_paid_label = QLabel(f"Fee Paid: ₹{fee_paid}")
        fee_paid_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: #10B981;")
        fee_layout.addWidget(fee_paid_label, alignment=Qt.AlignmentFlag.AlignRight)

        fee_balance_val = float(fee_balance)
        fee_balance_color = "#EF4444" if fee_balance_val > 0 else "#10B981"
        fee_balance_text = f"Balance Due: ₹{fee_balance}" if fee_balance_val > 0 else "Fully Paid"
        fee_balance_label = QLabel(f"{fee_balance_text}")
        fee_balance_label.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {fee_balance_color};")
        fee_layout.addWidget(fee_balance_label, alignment=Qt.AlignmentFlag.AlignRight)

        card_layout.addWidget(fee_frame, 0, 1, Qt.AlignmentFlag.AlignRight)

        # Bus Details
        bus_frame = QFrame()
        bus_frame.setStyleSheet("border: none;")
        bus_layout = QVBoxLayout(bus_frame)
        bus_layout.setContentsMargins(0, 0, 0, 0)
        bus_layout.setSpacing(5)
        
        bus_title = QLabel("Bus Details")
        bus_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #38BDF8;")
        bus_layout.addWidget(bus_title)
        
        bus_layout.addWidget(QLabel(f"Number: {bus_no if bus_no else 'N/A'}"))
        bus_layout.addWidget(QLabel(f"Driver: {drv_name if drv_name else 'N/A'}"))
        bus_layout.addWidget(QLabel(f"Contact: {drv_phone if drv_phone else 'N/A'}"))
        card_layout.addWidget(bus_frame, 1, 0)

        # Route Details
        route_frame = QFrame()
        route_frame.setStyleSheet("border: none;")
        route_layout = QVBoxLayout(route_frame)
        route_layout.setContentsMargins(0, 0, 0, 0)
        route_layout.setSpacing(5)

        route_title = QLabel("Route Details")
        route_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #38BDF8;")
        route_layout.addWidget(route_title)
        
        route_layout.addWidget(QLabel(f"Route: {r_name if r_name else 'N/A'}"))
        route_layout.addWidget(QLabel(f"Pickup/Drop: {p_pickup if p_pickup else 'N/A'}"))
        card_layout.addWidget(route_frame, 1, 1)

        self.scroll_layout.addWidget(card)


class ParentBusSchedule(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.parent_dashboard = parent_dashboard
        self.create_widgets()
        self.load_buses()

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("School Bus Routes & Schedule")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #38BDF8;")
        main_layout.addWidget(title_label)

        # Search Frame
        search_layout = QHBoxLayout()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Bus Number or Route...")
        self.search_entry.setFixedWidth(300)
        search_layout.addWidget(self.search_entry, alignment=Qt.AlignmentFlag.AlignRight)

        search_button = QPushButton("Search")
        search_button.setFixedWidth(100)
        search_button.clicked.connect(self.load_buses)
        search_layout.addWidget(search_button, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(search_layout)

        # Table
        self.buses_table = QTableWidget()
        self.buses_table.setColumnCount(4)
        self.buses_table.setHorizontalHeaderLabels(["Bus Number", "Driver Name", "Driver Phone", "Assigned Route / Path"])
        header = self.buses_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.buses_table.setColumnWidth(0, 140)
        self.buses_table.setColumnWidth(1, 200)
        self.buses_table.setColumnWidth(2, 160)
        header.setStretchLastSection(True)
        self.buses_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.buses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.buses_table)

    def load_buses(self):
        search_query = self.search_entry.text().strip()
        from dal import db_dal
        buses = db_dal.get_all_buses(search_query=search_query)

        self.buses_table.setRowCount(0)
        for row_idx, row_data in enumerate(buses):
            self.buses_table.insertRow(row_idx)
            # row_data: (bus_id, bus_number, driver_name, driver_phone, capacity, route_id, route_name)
            display_data = [
                str(row_data[1]),
                str(row_data[2]),
                str(row_data[3]),
                str(row_data[6]) if row_data[6] else "Unassigned"
            ]
            for col_idx, item in enumerate(display_data):
                self.buses_table.setItem(row_idx, col_idx, QTableWidgetItem(item))


class ParentDashboard(QWidget):
    def __init__(self, parent_id):
        super().__init__()
        self.parent_id = parent_id
        
        self.setWindowTitle("Parent Dashboard - School Transport System")
        self.setMinimumSize(950, 600)
        self.resize(1050, 650)
        
        self.fetch_data()
        self.create_widgets()
        self.show_frame(ChildrenView)

    def fetch_data(self):
        from dal import db_dal
        
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute("SELECT parent_name FROM parent WHERE parent_id = ?", (self.parent_id,))
        result = cursor.fetchone()
        self.parent_name = result[0] if result else "Parent"
        connection.close()

        # Fetch children info via DAL
        self.children_records = db_dal.get_parent_dashboard_students(self.parent_id)

    def create_widgets(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar Frame
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(220)
        self.sidebar_frame.setObjectName("sidebarFrame")
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(12, 20, 12, 20)
        self.sidebar_layout.setSpacing(6)

        # Sidebar Top Layout (Hamburger + Title)
        sidebar_top_layout = QHBoxLayout()
        self.sidebar_toggle_btn = QPushButton("☰")
        self.sidebar_toggle_btn.setObjectName("toggleBtn")
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar)
        self.sidebar_toggle_btn.setFixedSize(40, 40)
        
        self.sidebar_title = QLabel("STMS")
        self.sidebar_title.setStyleSheet("font-size: 18pt; font-weight: 800; color: #38BDF8; letter-spacing: -1px; border: none;")
        
        sidebar_top_layout.addWidget(self.sidebar_toggle_btn)
        sidebar_top_layout.addWidget(self.sidebar_title)
        sidebar_top_layout.addStretch()
        self.sidebar_layout.addLayout(sidebar_top_layout)

        # Sidebar Buttons
        self.add_sidebar_button("My Children", lambda: self.show_frame(ChildrenView))
        self.add_sidebar_button("Bus Routes", lambda: self.show_frame(ParentBusSchedule))
        self.add_sidebar_button("Refresh Data", self.refresh_dashboard)
        
        self.sidebar_layout.addStretch()
        self.add_sidebar_button("Logout", self.logout)

        self.main_layout.addWidget(self.sidebar_frame)

        # Right Content Area
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top bar with hamburger toggle button when sidebar is hidden
        top_bar = QFrame()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet("background-color: #0F172A; border-bottom: 1px solid #1E293B;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(15, 5, 15, 5)
        
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.toggle_btn.hide() # Hidden by default since sidebar is visible
        top_bar_layout.addWidget(self.toggle_btn)
        
        header_title = QLabel(f"Parent Portal — {self.parent_name}")
        header_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #94A3B8; border: none;")
        top_bar_layout.addWidget(header_title)
        top_bar_layout.addStretch()

        right_layout.addWidget(top_bar)

        # Content Frame
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

    def toggle_sidebar(self):
        if self.sidebar_frame.isVisible():
            self.sidebar_frame.hide()
            self.toggle_btn.show()
        else:
            self.sidebar_frame.show()
            self.toggle_btn.hide()

    def show_frame(self, frame_class):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        frame = frame_class(self)
        self.content_layout.addWidget(frame)

    def refresh_dashboard(self):
        self.fetch_data()
        # Reload current view
        self.show_frame(ChildrenView)

    def logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
