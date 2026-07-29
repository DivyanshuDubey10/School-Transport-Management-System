from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLineEdit, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

def create_initials_avatar(name, size=44, bg_color="#334155", text_color="#F8FAFC"):
    """Helper to create a circular initials avatar badge like in modern SaaS dashboards."""
    lbl = QLabel()
    lbl.setFixedSize(size, size)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    parts = name.strip().split()
    if len(parts) >= 2:
        initials = (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1 and len(parts[0]) > 0:
        initials = parts[0][:2].upper()
    else:
        initials = "ST"
        
    lbl.setText(initials)
    radius = size // 2
    lbl.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border-radius: {radius}px; font-weight: 800; font-size: 13pt; border: 1px solid #475569;")
    return lbl

class ChildrenView(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.parent_dashboard = parent_dashboard
        self.create_widgets()

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(18)

        # 1. Page Header with Title and REFRESH button (matching screenshot)
        header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_label = QLabel("My Enrolled Children")
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet("font-size: 18pt; font-weight: 800; color: #F8FAFC; letter-spacing: -0.5px;")
        title_box.addWidget(title_label)
        
        sub_label = QLabel("Active student transport profiles, assigned bus routes, and live fee status.")
        sub_label.setStyleSheet("font-size: 10pt; color: #94A3B8;")
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # REFRESH Button exactly like screenshot
        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setFixedSize(130, 38)
        refresh_btn.setStyleSheet("QPushButton { background-color: #1E293B; color: #38BDF8; border: 1.5px solid #38BDF8; border-radius: 6px; font-weight: bold; font-size: 10pt; } QPushButton:hover { background-color: #38BDF8; color: #0F172A; }")
        refresh_btn.clicked.connect(self.parent_dashboard.refresh_dashboard)
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        main_layout.addLayout(header_layout)

        # 2. Search Bar and Filter Section
        search_layout = QHBoxLayout()
        search_layout.addStretch()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search student name, class, or bus number...")
        self.search_entry.setFixedWidth(320)
        self.search_entry.textChanged.connect(self.filter_cards)
        search_layout.addWidget(self.search_entry)
        main_layout.addLayout(search_layout)

        # 3. KPI Summary Banner
        total_children = len(self.parent_dashboard.children_records)
        unique_buses = set()
        total_balance = 0.0
        for child in self.parent_dashboard.children_records:
            if child[4]: unique_buses.add(child[4])
            if child[3]: total_balance += float(child[3])

        summary_frame = QFrame()
        grid = QGridLayout(summary_frame)
        grid.setContentsMargins(0, 5, 0, 10)
        grid.setSpacing(15)

        def create_kpi_card(title, value, subtext, val_color="#38BDF8"):
            card = QFrame()
            card.setObjectName("cardFrame")
            card.setStyleSheet("QFrame#cardFrame { background-color: #131C31; border: 1px solid #334155; border-radius: 10px; }")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(16, 14, 16, 14)
            
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #94A3B8; border: none;")
            lbl_val = QLabel(str(value))
            lbl_val.setStyleSheet(f"font-size: 20pt; font-weight: 800; color: {val_color}; border: none; margin-top: 2px;")
            lbl_sub = QLabel(subtext)
            lbl_sub.setStyleSheet("font-size: 9pt; color: #64748B; border: none;")
            
            layout.addWidget(lbl_title)
            layout.addWidget(lbl_val)
            layout.addWidget(lbl_sub)
            return card

        grid.addWidget(create_kpi_card("TOTAL ENROLLED", f"{total_children} Student{'s' if total_children != 1 else ''}", "Active Transport Profiles"), 0, 0)
        grid.addWidget(create_kpi_card("ASSIGNED BUS FLEET", f"{len(unique_buses)} Active Route{'s' if len(unique_buses) != 1 else ''}", "School Pickup & Drop Service"), 0, 1)
        bal_color = "#EF4444" if total_balance > 0 else "#10B981"
        bal_text = f"₹{total_balance:,.2f}" if total_balance > 0 else "₹0.00 (Clear)"
        bal_sub = "Payment Outstanding" if total_balance > 0 else "All Fee Accounts Paid"
        grid.addWidget(create_kpi_card("TOTAL BALANCE DUE", bal_text, bal_sub, bal_color), 0, 2)
        
        main_layout.addWidget(summary_frame)

        # 4. Scroll Area for Professional Student Cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(16)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        self.all_child_widgets = []
        self.populate_cards()

    def populate_cards(self):
        children = self.parent_dashboard.children_records
        if not children:
            no_record_label = QLabel("No student transport records found.")
            no_record_label.setStyleSheet("font-size: 12pt; color: #94A3B8;")
            no_record_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            empty_frame = QFrame()
            empty_frame.setObjectName("cardFrame")
            empty_layout = QVBoxLayout(empty_frame)
            empty_layout.setContentsMargins(40, 40, 40, 40)
            empty_layout.addWidget(no_record_label)
            self.scroll_layout.addWidget(empty_frame)
        else:
            for child in children:
                card_widget = self.create_child_card(child)
                self.all_child_widgets.append((child, card_widget))
                self.scroll_layout.addWidget(card_widget)

    def filter_cards(self, query):
        query = query.lower().strip()
        for child, widget in self.all_child_widgets:
            s_name, s_class, _, _, bus_no, drv_name, _, r_name, p_pickup = child
            text_pool = f"{s_name} {s_class} {bus_no} {drv_name} {r_name} {p_pickup}".lower()
            widget.setVisible(query in text_pool)

    def create_child_card(self, child):
        s_name, s_class, fee_paid, fee_balance, bus_no, drv_name, drv_phone, r_name, p_pickup = child
        
        card = QFrame()
        card.setObjectName("cardFrame")
        card.setStyleSheet("QFrame#cardFrame { background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; } QFrame#cardFrame:hover { border: 1px solid #475569; background-color: #223046; }")
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 16)
        card_layout.setSpacing(14)

        # Row 1: Student Header (SaaS style with circular avatar + Name + Subtext + Status Pill)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        
        # Circular Initials Avatar
        avatar = create_initials_avatar(s_name, size=46, bg_color="#38BDF8", text_color="#0F172A")
        top_layout.addWidget(avatar)
        
        name_info_box = QVBoxLayout()
        name_info_box.setSpacing(2)
        
        name_lbl = QLabel(s_name)
        name_lbl.setStyleSheet("font-size: 14pt; font-weight: 800; color: #F8FAFC; border: none;")
        name_info_box.addWidget(name_lbl)
        
        sub_info_lbl = QLabel(f"Class {s_class}  •  Tenant: STMS-ORG  •  ID: STU-{hash(s_name)%10000:04d}")
        sub_info_lbl.setStyleSheet("font-size: 9.5pt; color: #94A3B8; border: none;")
        name_info_box.addWidget(sub_info_lbl)
        
        top_layout.addLayout(name_info_box)
        top_layout.addStretch()
        
        status_pill = QLabel("Active Transport")
        status_pill.setStyleSheet("font-size: 9.5pt; font-weight: bold; color: #10B981; background-color: #064E3B; border-radius: 12px; padding: 5px 12px; border: 1px solid #059669;")
        top_layout.addWidget(status_pill)
        
        card_layout.addLayout(top_layout)

        # Divider line
        div1 = QFrame()
        div1.setFixedHeight(1)
        div1.setStyleSheet("background-color: #334155; border: none;")
        card_layout.addWidget(div1)

        # Row 2: Two Column Service & Route Details
        body_layout = QGridLayout()
        body_layout.setHorizontalSpacing(30)
        body_layout.setVerticalSpacing(10)
        body_layout.setColumnStretch(0, 1)
        body_layout.setColumnStretch(1, 1)

        # Left Column: Bus & Driver
        left_layout = QVBoxLayout()
        left_layout.setSpacing(6)
        
        bus_title = QLabel("ASSIGNED BUS SERVICE")
        bus_title.setStyleSheet("font-size: 9.5pt; font-weight: 800; color: #38BDF8; letter-spacing: 0.5px; border: none;")
        left_layout.addWidget(bus_title)
        
        bus_val = QLabel(f"Bus Number:  {bus_no if bus_no else 'Unassigned'}")
        bus_val.setStyleSheet("font-size: 12pt; font-weight: bold; color: #F8FAFC; border: none;")
        left_layout.addWidget(bus_val)
        
        drv_val = QLabel(f"Driver Name:  {drv_name if drv_name else 'N/A'}")
        drv_val.setStyleSheet("font-size: 10.5pt; color: #CBD5E1; border: none;")
        left_layout.addWidget(drv_val)
        
        ph_val = QLabel(f"Contact Phone:  {drv_phone if drv_phone else 'N/A'}")
        ph_val.setStyleSheet("font-size: 10.5pt; color: #CBD5E1; border: none;")
        left_layout.addWidget(ph_val)

        if drv_phone and drv_phone != 'N/A':
            call_btn = QPushButton(f"Call Driver ({drv_phone})")
            call_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            call_btn.setFixedWidth(190)
            call_btn.setStyleSheet("QPushButton { background-color: #0F172A; color: #38BDF8; border: 1px solid #38BDF8; border-radius: 6px; padding: 5px 12px; font-weight: bold; font-size: 9.5pt; } QPushButton:hover { background-color: #38BDF8; color: #0F172A; }")
            call_btn.clicked.connect(lambda checked=False, n=drv_name, p=drv_phone: self.call_driver(n, p))
            left_layout.addWidget(call_btn)

        body_layout.addLayout(left_layout, 0, 0)

        # Right Column: Route & Pickup Point
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        
        rt_title = QLabel("ROUTE & PICKUP STOP")
        rt_title.setStyleSheet("font-size: 9.5pt; font-weight: 800; color: #38BDF8; letter-spacing: 0.5px; border: none;")
        right_layout.addWidget(rt_title)
        
        rt_val = QLabel(f"Route Path:  {r_name if r_name else 'Unassigned'}")
        rt_val.setStyleSheet("font-size: 12pt; font-weight: bold; color: #F8FAFC; border: none;")
        right_layout.addWidget(rt_val)
        
        stop_val = QLabel(f"Designated Stop:  {p_pickup if p_pickup else 'Unassigned'}")
        stop_val.setStyleSheet("font-size: 10.5pt; color: #CBD5E1; border: none;")
        right_layout.addWidget(stop_val)
        
        time_val = QLabel("Standard Morning Pickup & Afternoon Drop Service")
        time_val.setStyleSheet("font-size: 9.5pt; font-style: italic; color: #64748B; border: none; margin-top: 4px;")
        right_layout.addWidget(time_val)
        
        right_layout.addStretch()
        body_layout.addLayout(right_layout, 0, 1)

        card_layout.addLayout(body_layout)

        # Divider line 2
        div2 = QFrame()
        div2.setFixedHeight(1)
        div2.setStyleSheet("background-color: #334155; border: none; margin-top: 4px;")
        card_layout.addWidget(div2)

        # Row 3: Fee Status & Payment Action
        foot_layout = QHBoxLayout()
        foot_layout.setSpacing(10)
        
        paid_lbl = QLabel(f"Total Fee Paid: ₹{fee_paid}")
        paid_lbl.setStyleSheet("font-size: 10.5pt; font-weight: bold; color: #10B981; border: none;")
        foot_layout.addWidget(paid_lbl)

        fee_bal_val = float(fee_balance)
        if fee_bal_val > 0:
            bal_lbl = QLabel(f"  •   Balance Due: ₹{fee_balance}")
            bal_lbl.setStyleSheet("font-size: 10.5pt; font-weight: 800; color: #EF4444; border: none;")
            foot_layout.addWidget(bal_lbl)
            
            foot_layout.addStretch()
            
            pay_btn = QPushButton("Pay Balance Now")
            pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pay_btn.setStyleSheet("QPushButton { background-color: #10B981; color: #FFFFFF; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; font-size: 9.5pt; } QPushButton:hover { background-color: #059669; }")
            pay_btn.clicked.connect(lambda checked=False, student=s_name, bal=fee_balance: self.pay_fee_prompt(student, bal))
            foot_layout.addWidget(pay_btn)
        else:
            bal_lbl = QLabel("  •   Account Fully Paid")
            bal_lbl.setStyleSheet("font-size: 10.5pt; font-weight: bold; color: #10B981; border: none;")
            foot_layout.addWidget(bal_lbl)
            
            foot_layout.addStretch()
            
            clear_pill = QLabel("ALL CLEARED")
            clear_pill.setStyleSheet("font-size: 9pt; font-weight: bold; color: #10B981; background-color: #064E3B; border-radius: 6px; padding: 4px 12px; border: none;")
            foot_layout.addWidget(clear_pill)

        card_layout.addLayout(foot_layout)

        return card

    def call_driver(self, driver_name, phone):
        QMessageBox.information(
            self,
            "Driver Contact",
            f"Calling Driver: {driver_name}\nPhone Number: {phone}\n\n(In a live mobile application, this button initiates a direct phone call or opens WhatsApp!)"
        )

    def pay_fee_prompt(self, student_name, balance):
        QMessageBox.information(
            self,
            "Online Fee Payment",
            f"Fee Payment Portal for {student_name}\nAmount Due: ₹{balance}\n\nTo settle this outstanding balance, please visit the school accounting office or use the online fee payment gateway.\n\nThank you for keeping your account up to date!"
        )


class ParentBusSchedule(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.parent_dashboard = parent_dashboard
        self.create_widgets()
        self.load_buses()

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(18)

        # Title Header with Refresh
        header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_label = QLabel("School Bus Fleet & Routes")
        title_label.setStyleSheet("font-size: 18pt; font-weight: 800; color: #F8FAFC; letter-spacing: -0.5px;")
        title_box.addWidget(title_label)
        
        sub_label = QLabel("Complete schedule of school buses, assigned drivers, contact details, and travel paths.")
        sub_label.setStyleSheet("font-size: 10pt; color: #94A3B8;")
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setFixedSize(130, 38)
        refresh_btn.setStyleSheet("QPushButton { background-color: #1E293B; color: #38BDF8; border: 1.5px solid #38BDF8; border-radius: 6px; font-weight: bold; font-size: 10pt; } QPushButton:hover { background-color: #38BDF8; color: #0F172A; }")
        refresh_btn.clicked.connect(self.load_buses)
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        main_layout.addLayout(header_layout)

        # Search Bar
        search_layout = QHBoxLayout()
        search_layout.addStretch()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Bus Number, Driver Name, or Route...")
        self.search_entry.setFixedWidth(320)
        self.search_entry.textChanged.connect(self.load_buses)
        search_layout.addWidget(self.search_entry)
        main_layout.addLayout(search_layout)

        # Modern SaaS Table
        self.buses_table = QTableWidget()
        self.buses_table.setColumnCount(4)
        self.buses_table.setHorizontalHeaderLabels(["Bus Number", "Driver Profile", "Contact Number", "Assigned Travel Path"])
        
        header = self.buses_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.buses_table.setColumnWidth(0, 150)
        self.buses_table.setColumnWidth(1, 230)
        self.buses_table.setColumnWidth(2, 170)
        header.setStretchLastSection(True)
        
        self.buses_table.verticalHeader().setDefaultSectionSize(48)
        self.buses_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.buses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.buses_table.setAlternatingRowColors(True)
        self.buses_table.setStyleSheet("QTableWidget { background-color: #0F172A; alternate-background-color: #131C31; border: 1px solid #334155; border-radius: 8px; } QHeaderView::section { background-color: #1E293B; color: #38BDF8; font-weight: bold; font-size: 10pt; padding: 10px; border-bottom: 2px solid #334155; } QTableWidget::item { padding: 8px 12px; font-size: 10.5pt; }")
        
        main_layout.addWidget(self.buses_table)

    def load_buses(self):
        search_query = self.search_entry.text().strip()
        from dal import db_dal
        buses = db_dal.get_all_buses(search_query=search_query)

        self.buses_table.setRowCount(0)
        for row_idx, row_data in enumerate(buses):
            self.buses_table.insertRow(row_idx)
            # row_data: (bus_id, bus_number, driver_name, driver_phone, capacity, route_id, route_name)
            bus_no = str(row_data[1])
            drv_name = str(row_data[2]) if row_data[2] else "Unassigned"
            drv_phone = str(row_data[3]) if row_data[3] else "N/A"
            route_name = str(row_data[6]) if row_data[6] else "Unassigned"

            self.buses_table.setItem(row_idx, 0, QTableWidgetItem(f"{bus_no}"))
            self.buses_table.setItem(row_idx, 1, QTableWidgetItem(f"{drv_name}"))
            self.buses_table.setItem(row_idx, 2, QTableWidgetItem(f"{drv_phone}"))
            self.buses_table.setItem(row_idx, 3, QTableWidgetItem(f"{route_name}"))


class ParentDashboard(QWidget):
    def __init__(self, parent_id):
        super().__init__()
        self.parent_id = parent_id
        
        self.setWindowTitle("School Bus Management System — Parent Portal")
        self.setMinimumSize(1100, 680)
        self.resize(1200, 750)
        
        self.fetch_data()
        self.create_widgets()
        self.show_frame(ChildrenView)

    def fetch_data(self):
        from dal import db_dal
        
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute("SELECT parent_name FROM parent WHERE parent_id = ?", (self.parent_id,))
        result = cursor.fetchone()
        self.parent_name = result[0] if result else "Parent Account"
        connection.close()

        self.children_records = db_dal.get_parent_dashboard_students(self.parent_id)

    def create_widgets(self):
        self.sidebar_buttons = []
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
        
        self.user_avatar = create_initials_avatar(self.parent_name, size=38, bg_color="#38BDF8", text_color="#0F172A")
        user_card_layout.addWidget(self.user_avatar)
        
        user_text = QVBoxLayout()
        user_text.setSpacing(2)
        self.lbl_uname = QLabel(self.parent_name[:14] + ("..." if len(self.parent_name) > 14 else ""))
        self.lbl_uname.setStyleSheet("font-size: 10pt; font-weight: bold; color: #F8FAFC; border: none;")
        lbl_urole = QLabel("Parent Account")
        lbl_urole.setStyleSheet("font-size: 8.5pt; color: #94A3B8; border: none;")
        user_text.addWidget(self.lbl_uname)
        user_text.addWidget(lbl_urole)
        user_card_layout.addLayout(user_text)
        user_card_layout.addStretch()
        
        self.sidebar_layout.addWidget(user_card)
        self.sidebar_layout.addSpacing(15)

        # Section Header 1: APPLICATION
        cat_app = QLabel("APPLICATION")
        cat_app.setStyleSheet("font-size: 8pt; font-weight: 800; color: #64748B; letter-spacing: 1px; margin-left: 4px; border: none;")
        self.sidebar_layout.addWidget(cat_app)

        self.btn_children = self.add_sidebar_button("My Children", lambda: self.show_frame(ChildrenView, self.btn_children))
        self.btn_routes = self.add_sidebar_button("Bus Schedules", lambda: self.show_frame(ParentBusSchedule, self.btn_routes))
        
        self.sidebar_layout.addSpacing(15)

        # Section Header 2: MANAGEMENT
        cat_mgmt = QLabel("MANAGEMENT")
        cat_mgmt.setStyleSheet("font-size: 8pt; font-weight: 800; color: #64748B; letter-spacing: 1px; margin-left: 4px; border: none;")
        self.sidebar_layout.addWidget(cat_mgmt)

        self.btn_profile = self.add_sidebar_button("Profile & Security", self.open_profile_view)
        self.btn_settings = self.add_sidebar_button("System Settings", self.open_settings_view)
        self.btn_refresh = self.add_sidebar_button("Refresh Data", self.refresh_dashboard)
        self.btn_logout_sidebar = self.add_sidebar_button("Logout", self.logout)
        
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

        # 2. Right Content Area & Sleek Top Bar
        right_layout = QVBoxLayout()
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
        
        self.header_breadcrumb = QLabel(f"Parent Portal  /  My Children")
        self.header_breadcrumb.setStyleSheet("font-size: 11pt; font-weight: bold; color: #94A3B8; border: none; margin-left: 10px;")
        top_bar_layout.addWidget(self.header_breadcrumb)
        
        top_bar_layout.addStretch()

        # Right-side action badge icons (Company / Logout)
        # System Online and Alerts have been removed


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
                btn.setStyleSheet("QPushButton#sidebarBtn { background-color: #1E293B; color: #38BDF8; border-left: 4px solid #38BDF8; font-weight: 800; }")
            else:
                btn.setStyleSheet("QPushButton#sidebarBtn { background-color: transparent; color: #94A3B8; border: none; font-weight: 600; } QPushButton#sidebarBtn:hover { background-color: #1E293B; color: #F8FAFC; }")

    def toggle_sidebar(self):
        if self.sidebar_frame.isVisible():
            self.sidebar_frame.hide()
            self.toggle_btn.show()
        else:
            self.sidebar_frame.show()
            self.toggle_btn.hide()

    def show_frame(self, frame_class, active_btn=None):
        if active_btn:
            self.set_active_sidebar_btn(active_btn)
            if frame_class == ChildrenView:
                self.header_breadcrumb.setText("Parent Portal  /  My Children")
            elif frame_class == ParentBusSchedule:
                self.header_breadcrumb.setText("Parent Portal  /  Bus Schedules")
            elif hasattr(frame_class, '__name__') and frame_class.__name__ == "ProfileView":
                self.header_breadcrumb.setText("Parent Portal  /  Personal Profile & Security")
            elif hasattr(frame_class, '__name__') and frame_class.__name__ == "SettingsView":
                self.header_breadcrumb.setText("Parent Portal  /  System Settings & Preferences")

        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if hasattr(frame_class, '__name__') and frame_class.__name__ == "ProfileView":
            frame = frame_class('parent', user_id=self.parent_id, dashboard_ref=self)
        elif hasattr(frame_class, '__name__') and frame_class.__name__ == "SettingsView":
            frame = frame_class('parent', dashboard_ref=self)
        else:
            frame = frame_class(self)
        self.content_layout.addWidget(frame)

    def open_profile_view(self):
        from ui.profile_view import ProfileView
        self.show_frame(ProfileView, self.btn_profile)

    def open_settings_view(self):
        from ui.settings_view import SettingsView
        self.show_frame(SettingsView, self.btn_settings)

    def update_user_display(self):
        from dal import db_dal
        parent_data = db_dal.get_parent_by_id(self.parent_id)
        if parent_data:
            self.parent_name = str(parent_data[1])
            self.lbl_uname.setText(self.parent_name[:14] + ("..." if len(self.parent_name) > 14 else ""))
            new_avatar = create_initials_avatar(self.parent_name, size=38, bg_color="#38BDF8", text_color="#0F172A")
            self.user_avatar.deleteLater()
            self.user_avatar = new_avatar
            self.user_avatar.setParent(self.lbl_uname.parentWidget())
            self.lbl_uname.parentWidget().layout().insertWidget(0, self.user_avatar)

    def refresh_dashboard(self):
        self.fetch_data()
        self.show_frame(ChildrenView, self.btn_children)

    def logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
