from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QScrollArea
from PyQt6.QtCore import Qt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import connect_database

class ParentDashboard(QWidget):
    def __init__(self, parent_id):
        super().__init__()
        self.parent_id = parent_id
        
        self.setWindowTitle("Parent Dashboard")
        self.setFixedSize(900, 600)
        
        self.fetch_data()
        self.create_widgets()

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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Frame
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(f"Welcome, {self.parent_name}")
        self.title_label.setObjectName("titleLabel")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()

        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setFixedWidth(120)
        self.refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_button)

        self.logout_button = QPushButton("🚪 Logout")
        self.logout_button.setFixedWidth(100)
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)

        main_layout.addLayout(header_layout)

        title2_label = QLabel("Your Children's Transport Details")
        title2_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        title2_label.setContentsMargins(0, 10, 0, 10)
        main_layout.addWidget(title2_label)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        self.populate_cards()

    def populate_cards(self):
        # Clear existing cards
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        if not self.children_records:
            no_record_label = QLabel("No records found for your children.")
            no_record_label.setStyleSheet("font-size: 16px; color: #A6ADC8;")
            no_record_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            empty_frame = QFrame()
            empty_frame.setObjectName("cardFrame")
            empty_layout = QVBoxLayout(empty_frame)
            empty_layout.setContentsMargins(30, 30, 30, 30)
            empty_layout.addWidget(no_record_label)
            
            self.scroll_layout.addWidget(empty_frame)
        else:
            for child in self.children_records:
                self.create_child_card(child)

    def refresh_data(self):
        self.fetch_data()
        self.title_label.setText(f"Welcome, {self.parent_name}")
        self.populate_cards()

    def create_child_card(self, child):
        # child format based on DAL: s.student_name, s.student_class, s.fee_paid, s.fee_balance, b.bus_number, b.driver_name, b.driver_phone, r.route_name, p.pickup_point
        s_name, s_class, fee_paid, fee_balance, bus_no, drv_name, drv_phone, r_name, p_pickup = child
        
        card = QFrame()
        card.setObjectName("cardFrame")
        
        card_layout = QGridLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # Child Header
        header_label = QLabel(f"👤 {s_name} (Class {s_class})")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #89B4FA; border: none;")
        card_layout.addWidget(header_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Fee Details
        fee_frame = QFrame()
        fee_frame.setStyleSheet("border: none;")
        fee_layout = QVBoxLayout(fee_frame)
        fee_layout.setContentsMargins(0, 0, 0, 0)
        fee_layout.setSpacing(5)
        
        fee_paid_label = QLabel(f"💰 Fee Paid: ₹{fee_paid}")
        fee_paid_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #A6E3A1;")
        fee_layout.addWidget(fee_paid_label, alignment=Qt.AlignmentFlag.AlignRight)

        fee_balance_val = float(fee_balance)
        fee_balance_color = "#F38BA8" if fee_balance_val > 0 else "#A6E3A1"
        fee_balance_text = f"Balance Due: ₹{fee_balance}" if fee_balance_val > 0 else "Fully Paid"
        fee_balance_label = QLabel(f"📊 {fee_balance_text}")
        fee_balance_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {fee_balance_color};")
        fee_layout.addWidget(fee_balance_label, alignment=Qt.AlignmentFlag.AlignRight)

        card_layout.addWidget(fee_frame, 0, 1, Qt.AlignmentFlag.AlignRight)

        # Bus Details
        bus_frame = QFrame()
        bus_frame.setStyleSheet("border: none;")
        bus_layout = QVBoxLayout(bus_frame)
        bus_layout.setContentsMargins(0, 0, 0, 0)
        bus_layout.setSpacing(5)
        
        bus_title = QLabel("🚌 Bus Details")
        bus_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
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

        route_title = QLabel("📍 Route Details")
        route_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        route_layout.addWidget(route_title)
        
        route_layout.addWidget(QLabel(f"Route: {r_name if r_name else 'N/A'}"))
        route_layout.addWidget(QLabel(f"Pickup/Drop: {p_pickup if p_pickup else 'N/A'}"))
        card_layout.addWidget(route_frame, 1, 1)

        self.scroll_layout.addWidget(card)

    def logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
