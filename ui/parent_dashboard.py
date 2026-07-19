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
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()

        self.logout_button = QPushButton("Logout")
        self.logout_button.setFixedWidth(100)
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)

        main_layout.addLayout(header_layout)

        title2_label = QLabel("Your Children's Transport Details")
        title2_label.setStyleSheet("font-size: 20px; font-weight: bold;")
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

        if not self.children_records:
            no_record_label = QLabel("No records found for your children.")
            no_record_label.setStyleSheet("font-size: 16px;")
            self.scroll_layout.addWidget(no_record_label)
        else:
            for child in self.children_records:
                self.create_child_card(child)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

    def create_child_card(self, child):
        # child format based on DAL: s.student_name, s.student_class, s.fee_status, b.bus_number, b.driver_name, b.driver_phone, r.route_name, p.pickup_point
        # Let's adjust according to DAL get_parent_dashboard_students response order:
        s_name, s_class, fee_paid, fee_balance, bus_no, drv_name, drv_phone, r_name, p_pickup = child
        
        card = QFrame()
        card.setStyleSheet("background-color: #333333; border-radius: 10px; border: 1px solid #444444;")
        
        card_layout = QGridLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        # Child Header
        header_label = QLabel(f"{s_name} (Class {s_class})")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; border: none;")
        card_layout.addWidget(header_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Fee Details
        fee_frame = QFrame()
        fee_frame.setStyleSheet("border: none;")
        fee_layout = QVBoxLayout(fee_frame)
        fee_layout.setContentsMargins(0, 0, 0, 0)
        
        fee_paid_label = QLabel(f"Fee Paid: ${fee_paid}")
        fee_paid_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ff00;")
        fee_layout.addWidget(fee_paid_label, alignment=Qt.AlignmentFlag.AlignRight)

        fee_balance_color = "#ff4444" if float(fee_balance) > 0 else "#00ff00"
        fee_balance_label = QLabel(f"Fee Balance: ${fee_balance}")
        fee_balance_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {fee_balance_color};")
        fee_layout.addWidget(fee_balance_label, alignment=Qt.AlignmentFlag.AlignRight)

        card_layout.addWidget(fee_frame, 0, 1, Qt.AlignmentFlag.AlignRight)

        # Bus Details
        bus_frame = QFrame()
        bus_frame.setStyleSheet("border: none;")
        bus_layout = QVBoxLayout(bus_frame)
        bus_layout.setContentsMargins(0, 0, 0, 0)
        
        bus_layout.addWidget(QLabel("<u>Bus Details:</u>"))
        bus_layout.addWidget(QLabel(f"Bus Number: {bus_no if bus_no else 'N/A'}"))
        bus_layout.addWidget(QLabel(f"Driver: {drv_name if drv_name else 'N/A'}"))
        bus_layout.addWidget(QLabel(f"Contact: {drv_phone if drv_phone else 'N/A'}"))
        card_layout.addWidget(bus_frame, 1, 0)

        # Route Details
        route_frame = QFrame()
        route_frame.setStyleSheet("border: none;")
        route_layout = QVBoxLayout(route_frame)
        route_layout.setContentsMargins(0, 0, 0, 0)

        route_layout.addWidget(QLabel("<u>Route Details:</u>"))
        route_layout.addWidget(QLabel(f"Route: {r_name if r_name else 'N/A'}"))
        route_layout.addWidget(QLabel(f"Pickup/Drop: {p_pickup if p_pickup else 'N/A'}"))
        card_layout.addWidget(route_frame, 1, 1)

        self.scroll_layout.addWidget(card)

    def logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
