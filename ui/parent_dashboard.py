from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLineEdit, QMessageBox, QSpacerItem, QSizePolicy, QDialog, QFormLayout, QComboBox, QCheckBox, QCalendarWidget)
from PyQt6.QtCore import Qt, QDate, QRect
from PyQt6.QtGui import QPainter, QColor
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database
from dal import db_dal

class CustomCalendarWidget(QCalendarWidget):
    def __init__(self, attendance_map):
        super().__init__()
        self.attendance_map = attendance_map
        
    def paintCell(self, painter, rect, date):
        date_str = date.toString("yyyy-MM-dd")
        status = self.attendance_map.get(date_str)
        
        if status == "Present":
            painter.fillRect(rect, QColor(209, 250, 229)) # light green
        elif status == "Absent":
            painter.fillRect(rect, QColor(254, 226, 226)) # light red
            
        super().paintCell(painter, rect, date)

class AttendanceCalendarDialog(QDialog):
    def __init__(self, parent, student_id, student_name):
        super().__init__(parent)
        self.setWindowTitle(f"Attendance Calendar - {student_name}")
        self.setFixedSize(500, 450)
        self
        
        layout = QVBoxLayout(self)
        
        att_records = db_dal.get_attendance_history_for_student(student_id)
        att_map = {str(r[0]): r[1] for r in att_records}
        
        self.calendar = CustomCalendarWidget(att_map)
        self.calendar.setStyleSheet("QCalendarWidget QWidget { alternate-background- }")
        layout.addWidget(self.calendar)
        
        close_btn = QPushButton("Close Calendar")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("QPushButton { background- color: white; border-radius: 6px; padding: 8px; font-weight: bold; } QPushButton:hover { background- }")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

def create_initials_avatar(name, size=44, bg_color="#D1D5DB", text_color="#111827"):
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
    lbl.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border-radius: {radius}px; font-weight: 800; font-size: 13pt; ")
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
        title_label
        title_box.addWidget(title_label)
        
        sub_label = QLabel("Active student transport profiles, assigned bus routes, and live fee status.")
        sub_label
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # REFRESH Button
        
        # Request Transport Button
        request_btn = QPushButton("REQUEST TRANSPORT")
        request_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        request_btn.setFixedSize(170, 38)
        request_btn.setStyleSheet("QPushButton { background-color: #38BDF8;  border: none; border-radius: 6px; font-weight: bold; font-size: 10pt; } QPushButton:hover { background-color: #0EA5E9; }")
        request_btn.clicked.connect(self.open_request_modal)

        header_layout.addWidget(request_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        main_layout.addLayout(header_layout)

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
            if child[5]: unique_buses.add(child[5])
            if child[4]: total_balance += float(child[4])

        summary_frame = QFrame()
        grid = QGridLayout(summary_frame)
        grid.setContentsMargins(0, 5, 0, 10)
        grid.setSpacing(15)

        def create_kpi_card(title, value, subtext, val_color="#38BDF8"):
            card = QFrame()
            card.setObjectName("statCard")
            card.setStyleSheet("QFrame#cardFrame {   border-radius: 10px; }")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(16, 14, 16, 14)

            lbl_title = QLabel(title)
            lbl_title
            lbl_val = QLabel(str(value))
            lbl_val.setStyleSheet(f"font-size: 20pt; font-weight: 800; color: {val_color}; border: none; margin-top: 2px;")
            lbl_sub = QLabel(subtext)
            lbl_sub

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
        scroll_area

        scroll_content = QWidget()
        scroll_content
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(16)

        scroll_area.setWidget(scroll_content)
        scroll_area.verticalScrollBar().setSingleStep(15)
        main_layout.addWidget(scroll_area)

        self.all_child_widgets = []
        self.populate_cards()

    def open_request_modal(self):
        dialog = RequestTransportDialog(self.parent_dashboard.parent_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.parent_dashboard.refresh_dashboard()

    def populate_cards(self):
        children = self.parent_dashboard.children_records
        if not children:
            no_record_label = QLabel("No student transport records found.")
            no_record_label
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
            s_id, s_name, s_class, _, _, bus_no, drv_name, _, r_name, p_pickup = child
            text_pool = f"{s_name} {s_class} {bus_no} {drv_name} {r_name} {p_pickup}".lower()
            widget.setVisible(query in text_pool)

    def create_child_card(self, child):
        s_id, s_name, s_class, fee_paid, fee_balance, bus_no, drv_name, drv_phone, r_name, p_pickup = child
        
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet("QFrame#cardFrame {   border-radius: 10px; } QFrame#cardFrame:hover {  background- }")
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 16)
        card_layout.setSpacing(14)

        # Row 1: Student Header (SaaS style with Name + Subtext + Status Pill)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        
        name_info_box = QVBoxLayout()
        name_info_box.setSpacing(2)
        
        name_lbl = QLabel(s_name)
        name_lbl
        name_info_box.addWidget(name_lbl)
        
        sub_info_lbl = QLabel(f"Class {s_class}  •  Tenant: STMS-ORG  •  ID: STU-{hash(s_name)%10000:04d}")
        sub_info_lbl
        name_info_box.addWidget(sub_info_lbl)
        
        top_layout.addLayout(name_info_box)
        top_layout.addStretch()
        
        # Get today's attendance status
        from dal import db_dal
        from PyQt6.QtCore import QDate
        today = QDate.currentDate().toString("yyyy-MM-dd")
        att_records = db_dal.get_attendance_history_for_student(s_id)
        today_status = "Not Marked"
        for r in att_records:
            if str(r[0]) == today:
                today_status = r[1]
                break

        status_color = "#D1D5DB" # Default gray
        text_color = "#1F2937"
        if today_status == "Present":
            status_color = "#047857" # Green
            text_color = "#FFFFFF"
        elif today_status == "Absent":
            status_color = "#B91C1C" # Red
            text_color = "#FFFFFF"

        status_pill = QLabel(f"Today: {today_status}")
        status_pill.setStyleSheet(f"font-size: 9.5pt; font-weight: bold; color: {text_color}; background-color: {status_color}; border-radius: 12px; padding: 5px 12px; ")
        top_layout.addWidget(status_pill)
        
        card_layout.addLayout(top_layout)

        # Divider line
        div1 = QFrame()
        div1.setFixedHeight(1)
        div1
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
        bus_title
        left_layout.addWidget(bus_title)
        
        bus_val = QLabel(f"Bus Number:  {bus_no if bus_no else 'Unassigned'}")
        bus_val
        left_layout.addWidget(bus_val)
        
        drv_val = QLabel(f"Driver Name:  {drv_name if drv_name else 'N/A'}")
        drv_val
        left_layout.addWidget(drv_val)
        
        ph_val = QLabel(f"Contact Phone:  {drv_phone if drv_phone else 'N/A'}")
        ph_val
        left_layout.addWidget(ph_val)

        if drv_phone and drv_phone != 'N/A':
            call_btn = QPushButton(f"Call Driver ({drv_phone})")
            call_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            call_btn.setFixedWidth(190)
            call_btn.setStyleSheet("QPushButton { background- color: #38BDF8; border: 1px solid #38BDF8; border-radius: 6px; padding: 5px 12px; font-weight: bold; font-size: 9.5pt; } QPushButton:hover { background-color: #38BDF8;  }")
            call_btn.clicked.connect(lambda checked=False, n=drv_name, p=drv_phone: self.call_driver(n, p))
            left_layout.addWidget(call_btn)

        body_layout.addLayout(left_layout, 0, 0)

        # Right Column: Route & Pickup Point
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        
        route_title = QLabel("ROUTE DETAILS")
        route_title
        right_layout.addWidget(route_title)
        
        rt_val = QLabel(f"Route Path:  {r_name if r_name else 'Unassigned'}")
        rt_val
        right_layout.addWidget(rt_val)
        
        stop_val = QLabel(f"Designated Stop:  {p_pickup if p_pickup else 'Unassigned'}")
        stop_val
        right_layout.addWidget(stop_val)

        # Quick Link to Attendance Calendar
        cal_btn = QPushButton("📅 View Attendance Calendar")
        cal_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cal_btn.setFixedWidth(220)
        cal_btn.setObjectName("primaryButton")
        cal_btn.clicked.connect(lambda checked=False, sid=s_id, sname=s_name: self.open_calendar(sid, sname))
        right_layout.addWidget(cal_btn)

        
        right_layout.addStretch()
        body_layout.addLayout(right_layout, 0, 1)

        card_layout.addLayout(body_layout)

        # Divider line 2
        div2 = QFrame()
        div2.setFixedHeight(1)
        div2
        card_layout.addWidget(div2)

        # Row 3: Fee Status & Payment Action
        foot_layout = QHBoxLayout()
        foot_layout.setSpacing(10)
        
        paid_lbl = QLabel(f"Total Paid: ₹{fee_paid}")
        paid_lbl
        foot_layout.addWidget(paid_lbl)

        fee_bal_val = float(fee_balance)
        if fee_bal_val > 0:
            bal_lbl = QLabel(f"  •   Balance: ₹{fee_balance}")
            bal_lbl
            foot_layout.addWidget(bal_lbl)
            
            foot_layout.addStretch()
            
            pay_btn = QPushButton("Pay Balance")
            pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pay_btn.setObjectName("actionButton")
            pay_btn.clicked.connect(lambda checked=False, student=s_name, bal=fee_balance: self.pay_fee_prompt(student, bal))
            foot_layout.addWidget(pay_btn)
        else:
            bal_lbl = QLabel("  •   Fully Paid")
            bal_lbl
            foot_layout.addWidget(bal_lbl)
            
            foot_layout.addStretch()
            
            clear_pill = QLabel("CLEARED")
            clear_pill
            foot_layout.addWidget(clear_pill)

        card_layout.addLayout(foot_layout)

        return card

    def open_calendar(self, student_id, student_name):
        dialog = AttendanceCalendarDialog(self, student_id, student_name)
        dialog.exec()

    def call_driver(self, driver_name, phone):
        QMessageBox.information(
            self,
            "Driver Contact",
            f"Calling Driver: {driver_name}\nPhone Number: {phone}"
        )

    def pay_fee_prompt(self, student_name, balance):
        QMessageBox.information(
            self,
            "Online Fee Payment",
            f"Fee Payment Portal for {student_name}\nAmount Due: ₹{balance}"
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
        title_label = QLabel("NeoYatra Fleet & Routes")
        title_label
        main_layout.addWidget(title_label)

        sub_label = QLabel("Complete schedule of NeoYatra buses, assigned drivers, and travel paths.")
        sub_label
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        
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
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.buses_table.setColumnWidth(0, 150)
        self.buses_table.setColumnWidth(1, 230)
        self.buses_table.setColumnWidth(2, 170)
        header.setStretchLastSection(True)
        
        self.buses_table.verticalHeader().setDefaultSectionSize(48)
        self.buses_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.buses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.buses_table.setAlternatingRowColors(True)
        self.buses_table.verticalScrollBar().setSingleStep(15)
        self.buses_table.setObjectName("dataTable")
        
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

class AttendanceView(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.parent_dashboard = parent_dashboard
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        
        title = QLabel("Boarding & Attendance Logs")
        title.setObjectName("pageTitle")
        
        sub = QLabel("Daily transport boarding and attendance records.")
        sub
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        
        layout.addLayout(header_layout)
        layout.addWidget(sub)
        layout.addSpacing(15)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll
        
        self.content_widget = QWidget()
        self.content_widget
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setSpacing(20)
        
        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll, 1)
        
        self.load_attendance()

    def load_attendance(self):
        # Clear existing
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        from dal import db_dal
        children = self.parent_dashboard.children_records
        
        if not children:
            lbl = QLabel("No enrolled children found.")
            lbl
            self.content_layout.addWidget(lbl)
            return

        for child in children:
            s_id, s_name, s_class = child[0], child[1], child[2]
            records = db_dal.get_attendance_history_for_student(s_id)
            
            # Card for each child
            card = QFrame()
            card
            card_layout = QVBoxLayout(card)
            
            name_lbl = QLabel(f"{s_name} (Class {s_class})")
            name_lbl
            card_layout.addWidget(name_lbl)
            
            if not records:
                no_rec_lbl = QLabel("No attendance records found.")
                no_rec_lbl
                card_layout.addWidget(no_rec_lbl)
            else:
                table = QTableWidget()
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(["Date", "Status"])
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                table.setObjectName("dataTable")
                table.setRowCount(len(records))
                table.setFixedHeight(min(300, 40 + len(records)*35))
                table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
                table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                
                for r_idx, record in enumerate(records):
                    date_str, status = str(record[0]), record[1]
                    table.setItem(r_idx, 0, QTableWidgetItem(date_str))
                    
                    status_item = QTableWidgetItem(status)
                    if status == "Present":
                        status_item.setForeground(Qt.GlobalColor.green)
                    elif status == "Absent":
                        status_item.setForeground(Qt.GlobalColor.red)
                    table.setItem(r_idx, 1, status_item)
                
                card_layout.addWidget(table)
                
            self.content_layout.addWidget(card)

class SupportTicketsView(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.parent_dashboard = parent_dashboard
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        
        title = QLabel("Helpdesk & Support")
        title.setObjectName("pageTitle")
        
        sub = QLabel("Raise transport issues, feedback, or driver complaints.")
        sub
        
        btn = QPushButton("+ Raise New Ticket")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setObjectName("actionButton")
        btn.setFixedSize(160, 40)
        btn.setObjectName("actionButton")
        btn.clicked.connect(self.raise_ticket)
        
        frame = QFrame()
        frame
        flayout = QVBoxLayout(frame)
        flayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl = QLabel("No Active Tickets")
        icon_lbl
        desc_lbl = QLabel("You don't have any open support tickets.")
        desc_lbl
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flayout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        flayout.addWidget(desc_lbl)
        
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addSpacing(10)
        layout.addWidget(frame, 1)

    def raise_ticket(self):
        QMessageBox.information(
            self,
            "Ticket Raised",
            "Your support ticket has been successfully created. Our helpdesk team will review it and get back to you shortly."
        )

class ParentDashboard(QWidget):
    def __init__(self, parent_id):
        super().__init__()
        self.parent_id = parent_id
        
        self.setWindowTitle("NeoYatra — Parent Portal")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 750)
        
        self.fetch_data()
        self.create_widgets()
        self.show_frame(ChildrenView)

    def fetch_data(self):
        from dal import db_dal
        
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute("SELECT parent_name FROM parent WHERE parent_id = %s", (self.parent_id,))
        result = cursor.fetchone()
        self.parent_name = result[0] if result else "Parent Account"
        connection.close()

        self.children_records = db_dal.get_parent_dashboard_students(self.parent_id)

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
        
        self.user_avatar = create_initials_avatar(self.parent_name, size=38, bg_color="#38BDF8", text_color="#FFFFFF")
        user_card_layout.addWidget(self.user_avatar)
        
        user_text = QVBoxLayout()
        user_text.setSpacing(2)
        self.lbl_uname = QLabel(self.parent_name[:14] + ("..." if len(self.parent_name) > 14 else ""))
        self.lbl_uname.setObjectName("statTitle")
        lbl_urole = QLabel("Parent Account")
        lbl_urole.setObjectName("statDesc")
        user_text.addWidget(self.lbl_uname)
        user_text.addWidget(lbl_urole)
        user_card_layout.addLayout(user_text)
        user_card_layout.addStretch()
        
        self.sidebar_layout.addWidget(user_card)
        self.sidebar_layout.addSpacing(15)

        

        self.btn_children = self.add_sidebar_button("My Children", lambda: self.show_frame(ChildrenView, self.btn_children))
        self.btn_routes = self.add_sidebar_button("Bus Schedules", lambda: self.show_frame(ParentBusSchedule, self.btn_routes))
        self.btn_attendance = self.add_sidebar_button("Boarding Logs", lambda: self.show_frame(AttendanceView, self.btn_attendance))
        self.btn_support = self.add_sidebar_button("Helpdesk & Support", lambda: self.show_frame(SupportTicketsView, self.btn_support))
        
        self.sidebar_layout.addSpacing(15)

        

        self.btn_profile = self.add_sidebar_button("Profile & Security", self.open_profile_view)
        self.btn_settings = self.add_sidebar_button("System Settings", self.open_settings_view)
        self.btn_refresh = self.add_sidebar_button("Refresh Data", self.refresh_dashboard)
        self.btn_logout_sidebar = self.add_sidebar_button("Logout", self.logout)
        
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

        # 2. Right Content Area & Sleek Top Bar
        right_layout = QVBoxLayout()
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
        
        self.header_breadcrumb = QLabel(f"Parent Portal  /  My Children")
        self.header_breadcrumb
        top_bar_layout.addWidget(self.header_breadcrumb)
        
        top_bar_layout.addStretch()

        # Right-side action badge icons (Company / Logout)
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
                btn.setStyleSheet("QPushButton#sidebarBtn {  color: #38BDF8; border-left: 4px solid #38BDF8; font-weight: 800; }")
            else:
                btn.setStyleSheet("QPushButton#sidebarBtn { background-color: transparent;  border: none; font-weight: 600; } QPushButton#sidebarBtn:hover {   }")

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
            elif frame_class == AttendanceView:
                self.header_breadcrumb.setText("Parent Portal  /  Boarding Logs")
            elif frame_class == SupportTicketsView:
                self.header_breadcrumb.setText("Parent Portal  /  Helpdesk & Support")
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
            new_avatar = create_initials_avatar(self.parent_name, size=38, bg_color="#38BDF8", text_color="#FFFFFF")
            self.user_avatar.deleteLater()
            self.user_avatar = new_avatar
            self.user_avatar.setParent(self.lbl_uname.parentWidget())
            self.lbl_uname.parentWidget().layout().insertWidget(0, self.user_avatar)

    def refresh_dashboard(self):
        self.fetch_data()
        self.show_frame(ChildrenView, self.btn_children)

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

class RequestTransportDialog(QDialog):
    def __init__(self, parent_id, parent=None):
        super().__init__(parent)
        self.parent_id = parent_id
        self.dashboard = parent
        self.setWindowTitle("Request Transport Change")
        self.setFixedSize(400, 350)
                
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select child(ren) to change transport for:"))
        
        # Load children
        self.children_checkboxes = []
        children = getattr(self.dashboard.parent_dashboard, 'children_records', [])
        
        if not children:
            layout.addWidget(QLabel("No enrolled children found.", styleSheet="color: #EF4444;"))
        else:
            for child in children:
                # child format is from get_parent_children:
                # (student_id, student_name, student_class, bus_id, route_id, fee_paid, fee_balance, transport_status)
                chk = QCheckBox(f"{child[1]} (Class {child[2]})")
                chk.setProperty("student_id", child[0])
                chk.setStyleSheet("QCheckBox { spacing: 8px; font-size: 11pt; margin-bottom: 5px; } QCheckBox::indicator { width: 18px; height: 18px; }")
                layout.addWidget(chk)
                self.children_checkboxes.append(chk)
                
        form_layout = QFormLayout()
        
        self.pickup_input = QComboBox()
        self.pickup_input
        
        # Populate pickup points
        from dal import db_dal
        points = db_dal.get_all_pickup_points()
        self.pickup_input.addItems(points)
        
        form_layout.addRow("New Pickup Point:", self.pickup_input)
        
        layout.addLayout(form_layout)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        submit_btn = QPushButton("Submit Request")
        submit_btn
        submit_btn.clicked.connect(self.submit_request)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(submit_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)

    def submit_request(self):
        selected_student_ids = []
        for chk in self.children_checkboxes:
            if chk.isChecked():
                selected_student_ids.append(chk.property("student_id"))
                
        if not selected_student_ids:
            QMessageBox.warning(self, "Input Error", "Please select at least one child.")
            return
            
        pickup = self.pickup_input.currentText()
            
        from dal import db_dal
        
        success = True
        for s_id in selected_student_ids:
            if not db_dal.create_change_request(s_id, pickup):
                success = False
                
        if success:
            QMessageBox.information(self, "Success", "Transport change request submitted! Waiting for Admin approval.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to submit some or all requests.")
