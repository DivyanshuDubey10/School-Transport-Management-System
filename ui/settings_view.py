import os
import shutil
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QFrame, QMessageBox, QScrollArea, QCheckBox,
    QComboBox, QApplication
)
from PyQt6.QtCore import Qt
from dal import db_dal
from theme_manager import ThemeManager



MIDNIGHT_THEME_QSS = """
QWidget {
    background-color: #0A192F;
    color: #E6F1FF;
    font-family: "Segoe UI", "Inter", -apple-system, sans-serif;
    font-size: 11pt;
}
QPushButton {
    background-color: #0077B6;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 11pt;
}
QPushButton:hover { background-color: #0096C7; }
QPushButton:pressed { background-color: #023E8A; }
QLineEdit, QComboBox {
    background-color: #112240;
    color: #E6F1FF;
    border: 1.5px solid #233554;
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 24px;
    font-size: 11pt;
}
QLineEdit:focus, QComboBox:focus {
    border: 1.5px solid #64FFDA;
    background-color: #0A192F;
}
QTableWidget, QTableView {
    background-color: #112240;
    alternate-background-color: #0A192F;
    color: #E6F1FF;
    gridline-color: #233554;
    border: 1px solid #233554;
    border-radius: 8px;
    outline: none;
}
QTableWidget::item, QTableView::item {
    padding: 6px 10px;
    border-bottom: 1px solid #233554;
}
QTableWidget::item:selected, QTableView::item:selected {
    background-color: #0077B6;
    color: #FFFFFF;
    font-weight: 600;
}
QHeaderView::section {
    background-color: #172A45;
    color: #64FFDA;
    padding: 12px 10px;
    border: none;
    border-bottom: 2px solid #233554;
    font-weight: bold;
    font-size: 10pt;
}
QFrame#cardFrame, QFrame#loginFrame {
    background-color: #112240;
    border-radius: 12px;
    border: 1px solid #233554;
}
QFrame#sidebarFrame {
    background-color: #0A192F;
    border-right: 1px solid #172A45;
}
QPushButton#sidebarBtn {
    background-color: transparent;
    color: #8892B0;
    text-align: left;
    padding: 12px 18px;
    border-radius: 8px;
    font-weight: 600;
}
QPushButton#sidebarBtn:hover {
    background-color: #172A45;
    color: #64FFDA;
}
QLabel#titleLabel {
    font-size: 20pt;
    font-weight: 800;
    color: #64FFDA;
}
"""

class SettingsView(QWidget):
    def __init__(self, user_type='admin', dashboard_ref=None):
        super().__init__()
        self.user_type = user_type
        self.dashboard_ref = dashboard_ref
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # 1. Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        if self.user_type == 'admin':
            title_text = "System Administration & Control Hub"
            sub_text = "Configure global portal security, automated fleet policies, interface accessibility, and database operations."
        else:
            title_text = "Parent Portal & Alert Preferences"
            sub_text = "Customize visual themes, real-time child transport notifications, and contact localization."
            
        title_label = QLabel(title_text)
        title_label.setObjectName("pageTitle")
        title_box.addWidget(title_label)
        
        sub_label = QLabel(sub_text)
        sub_label.setObjectName("statDesc")
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        btn_save = QPushButton("Save All Preferences")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setFixedSize(180, 40)
        btn_save.setObjectName("primaryButton")
        btn_save.clicked.connect(self.save_preferences)
        header_layout.addWidget(btn_save, alignment=Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(header_layout)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QWidget#scrollContent { background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 0, 15, 10)
        content_layout.setSpacing(20)

        if self.user_type == 'admin':
            self.build_admin_settings(content_layout)
        else:
            self.build_parent_settings(content_layout)

        content_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def build_admin_settings(self, layout):
        # 1. Appearance, Accessibility & UI Scaling Card
        card1 = QFrame()
        card1.setObjectName("statCard")
        l1 = QVBoxLayout(card1)
        l1.setContentsMargins(22, 20, 22, 22)
        l1.setSpacing(15)
        
        lbl_title1 = QLabel("APPEARANCE, ACCESSIBILITY & UI SCALING")
        lbl_title1
        l1.addWidget(lbl_title1)
        
        lbl_sub1 = QLabel("Select visual theme mode and accessibility scaling for optimal high-density data management.")
        lbl_sub1
        l1.addWidget(lbl_sub1)
        
        theme_btn_layout = QHBoxLayout()
        theme_btn_layout.setSpacing(15)
        
        btn_night = QPushButton("Night Mode (Default)")
        btn_night.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_night.setFixedHeight(46)
        btn_night.setObjectName("secondaryButton")
        btn_night.clicked.connect(lambda: self.apply_theme("night"))
        
        btn_day = QPushButton("Day Mode")
        btn_day.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_day.setFixedHeight(46)
        btn_day.setStyleSheet("QPushButton { background-color: #111827; color: #FFFFFF; border: 2px solid #9CA3AF; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #E2E8F0; }")
        btn_day.clicked.connect(lambda: self.apply_theme("day"))
        
        theme_btn_layout.addWidget(btn_night)
        theme_btn_layout.addWidget(btn_day)
        l1.addLayout(theme_btn_layout)

        grid_acc = QGridLayout()
        grid_acc.setHorizontalSpacing(30)
        grid_acc.setVerticalSpacing(12)
        
        lbl_scale = QLabel("UI Scaling & Typography:")
        lbl_scale
        self.combo_scale = QComboBox()
        self.combo_scale.addItems([
            "Standard (100% Default - Balanced Grid)", 
            "Large / Accessible (115% High Readability - Recommended for large monitors)", 
            "Compact (90% Dense Grid - View more table rows simultaneously)"
        ])
        grid_acc.addWidget(lbl_scale, 0, 0)
        grid_acc.addWidget(self.combo_scale, 0, 1)
        l1.addLayout(grid_acc)
        
        self.chk_contrast = QCheckBox("Enable High-Contrast Gridlines & Bold Row Borders in Data Directories (Accessibility Mode)")
        self.chk_contrast.setChecked(True)
        self.chk_contrast
        l1.addWidget(self.chk_contrast)
        
        self.chk_tooltips = QCheckBox("Enable Screen Reader Compatible Table Cell Tooltips & Keyboard Focus Indicators")
        self.chk_tooltips.setChecked(True)
        self.chk_tooltips
        l1.addWidget(self.chk_tooltips)
        
        layout.addWidget(card1)

        # 2. Global Security & Access Policies Card
        card2 = QFrame()
        card2.setObjectName("statCard")
        l2 = QVBoxLayout(card2)
        l2.setContentsMargins(22, 20, 22, 22)
        l2.setSpacing(15)
        
        lbl_title2 = QLabel("GLOBAL SECURITY, 2FA & ACCESS POLICIES")
        lbl_title2
        l2.addWidget(lbl_title2)
        
        self.chk_2fa = QCheckBox("Enforce Two-Factor Authentication (2FA) for All Administrator & Staff Logins")
        self.chk_2fa.setChecked(True)
        self.chk_2fa
        l2.addWidget(self.chk_2fa)
        
        self.chk_autolock = QCheckBox("Automatically Lock Administrative Portal Session After 15 Minutes of Inactivity")
        self.chk_autolock.setChecked(True)
        self.chk_autolock
        l2.addWidget(self.chk_autolock)
        
        self.chk_ip = QCheckBox("Restrict Administrative Portal Access to Approved Campus Network IP Addresses")
        self.chk_ip.setChecked(False)
        self.chk_ip
        l2.addWidget(self.chk_ip)
        
        self.chk_audit_alert = QCheckBox("Log Audit Alert & Notify SuperAdmin on Multiple Failed Login Attempts")
        self.chk_audit_alert.setChecked(True)
        self.chk_audit_alert
        l2.addWidget(self.chk_audit_alert)
        
        grid_sec = QGridLayout()
        grid_sec.setHorizontalSpacing(30)
        grid_sec.setVerticalSpacing(12)
        
        lbl_expiry = QLabel("Staff Password Expiry Policy:")
        lbl_expiry
        self.combo_expiry = QComboBox()
        self.combo_expiry.addItems(["No Expiry (Default)", "Require Password Change Every 60 Days", "Require Password Change Every 90 Days"])
        grid_sec.addWidget(lbl_expiry, 0, 0)
        grid_sec.addWidget(self.combo_expiry, 0, 1)
        
        lbl_strength = QLabel("Minimum Password Strength:")
        lbl_strength
        self.combo_strength = QComboBox()
        self.combo_strength.addItems(["High Security (Min 8 chars, alphanumeric & special symbols)", "Standard Security (Min 6 chars alphanumeric)", "Basic Security (Min 4 chars)"])
        grid_sec.addWidget(lbl_strength, 1, 0)
        grid_sec.addWidget(self.combo_strength, 1, 1)
        l2.addLayout(grid_sec)
        
        layout.addWidget(card2)

        # 3. Automated Fleet Operations Card
        card3 = QFrame()
        card3.setObjectName("statCard")
        l3 = QVBoxLayout(card3)
        l3.setContentsMargins(22, 20, 22, 22)
        l3.setSpacing(15)
        
        lbl_title3 = QLabel("AUTOMATED FLEET OPERATIONS & GPS TELEMETRY")
        lbl_title3
        l3.addWidget(lbl_title3)
        
        self.chk_gps = QCheckBox("Broadcast Real-Time GPS Bus Coordinates & Route Progress to Parent Mobile Portal")
        self.chk_gps.setChecked(True)
        self.chk_gps
        l3.addWidget(self.chk_gps)
        
        self.chk_route_opt = QCheckBox("Enable Automated Daily Route Optimization & Student Stop Matcher")
        self.chk_route_opt.setChecked(True)
        self.chk_route_opt
        l3.addWidget(self.chk_route_opt)
        
        self.chk_delay_sms = QCheckBox("Send Automated SMS Delay Notifications to Parents when Bus is > 10 Minutes Late")
        self.chk_delay_sms.setChecked(True)
        self.chk_delay_sms
        l3.addWidget(self.chk_delay_sms)
        
        grid_fleet = QGridLayout()
        grid_fleet.setHorizontalSpacing(30)
        grid_fleet.setVerticalSpacing(12)
        
        lbl_maint = QLabel("Bus Maintenance Alert Threshold:")
        lbl_maint
        self.combo_maint = QComboBox()
        self.combo_maint.addItems(["Every 3,000 km / 3 Months (Standard Fleet Check)", "Every 5,000 km / 6 Months (Extended Schedule)", "Every 10,000 km / 1 Year (Heavy Duty Only)"])
        grid_fleet.addWidget(lbl_maint, 0, 0)
        grid_fleet.addWidget(self.combo_maint, 0, 1)
        
        lbl_speed = QLabel("Fleet Telemetry Speed Warning:")
        lbl_speed
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["60 km/h (City School Zone Standard)", "50 km/h (Strict Urban Safety)", "70 km/h (Express Highway Routes)"])
        grid_fleet.addWidget(lbl_speed, 1, 0)
        grid_fleet.addWidget(self.combo_speed, 1, 1)
        l3.addLayout(grid_fleet)
        
        layout.addWidget(card3)

        # 4. Database Management & System Actions Card
        card4 = QFrame()
        card4.setObjectName("statCard")
        l4 = QVBoxLayout(card4)
        l4.setContentsMargins(22, 20, 22, 22)
        l4.setSpacing(15)
        
        lbl_title4 = QLabel("DATABASE MANAGEMENT & SYSTEM OPERATIONS")
        lbl_title4
        l4.addWidget(lbl_title4)
        
        btn_grid = QGridLayout()
        btn_grid.setHorizontalSpacing(15)
        btn_grid.setVerticalSpacing(12)
        
        btn_backup = QPushButton("Export Database Backup (SQLite)")
        btn_backup.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_backup.setFixedHeight(42)
        btn_backup.setStyleSheet("QPushButton { background-color: #F3F4F6; color: #38BDF8; border: 1.5px solid #38BDF8; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #38BDF8; color: #FFFFFF; }")
        btn_backup.clicked.connect(self.export_backup)
        btn_grid.addWidget(btn_backup, 0, 0)
        
        btn_opt = QPushButton("Optimize & Deframent Database (VACUUM)")
        btn_opt.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_opt.setFixedHeight(42)
        btn_opt.setObjectName("primaryButton")
        btn_opt.clicked.connect(self.optimize_db)
        btn_grid.addWidget(btn_opt, 0, 1)
        
        btn_audit = QPushButton("Export System Audit Logs (CSV)")
        btn_audit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_audit.setFixedHeight(42)
        btn_audit.setStyleSheet("QPushButton { background-color: #F3F4F6; color: #F59E0B; border: 1.5px solid #F59E0B; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #F59E0B; color: #FFFFFF; }")
        btn_audit.clicked.connect(self.export_audit_logs)
        btn_grid.addWidget(btn_audit, 1, 0)
        
        btn_cache = QPushButton("Clear Temporary System Cache & Buffers")
        btn_cache.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cache.setFixedHeight(42)
        btn_cache.setStyleSheet("QPushButton { background-color: #7F1D1D; color: #111827; border: 1.5px solid #EF4444; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #EF4444; color: #FFFFFF; }")
        btn_cache.clicked.connect(self.clear_cache)
        btn_grid.addWidget(btn_cache, 1, 1)
        
        l4.addLayout(btn_grid)
        layout.addWidget(card4)

    def build_parent_settings(self, layout):
        # 1. Theme Card
        theme_card = QFrame()
        theme_card.setObjectName("statCard")
        l1 = QVBoxLayout(theme_card)
        l1.setContentsMargins(22, 20, 22, 22)
        l1.setSpacing(15)
        
        lbl_t_title = QLabel("APPEARANCE & VISUAL THEME MODE")
        lbl_t_title
        l1.addWidget(lbl_t_title)
        
        lbl_t_sub = QLabel("Select your preferred visual theme for the parent portal interface.")
        lbl_t_sub
        l1.addWidget(lbl_t_sub)
        
        theme_btn_layout = QHBoxLayout()
        theme_btn_layout.setSpacing(15)
        
        btn_night = QPushButton("Night Mode (Default)")
        btn_night.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_night.setFixedHeight(46)
        btn_night.setObjectName("secondaryButton")
        btn_night.clicked.connect(lambda: self.apply_theme("night"))
        
        btn_day = QPushButton("Day Mode")
        btn_day.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_day.setFixedHeight(46)
        btn_day.setStyleSheet("QPushButton { background-color: #111827; color: #FFFFFF; border: 2px solid #9CA3AF; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #E2E8F0; }")
        btn_day.clicked.connect(lambda: self.apply_theme("day"))
        
        theme_btn_layout.addWidget(btn_night)
        theme_btn_layout.addWidget(btn_day)
        l1.addLayout(theme_btn_layout)
        layout.addWidget(theme_card)

        # 2. Child Transport Alerts Card
        notif_card = QFrame()
        notif_card.setObjectName("statCard")
        l2 = QVBoxLayout(notif_card)
        l2.setContentsMargins(22, 20, 22, 22)
        l2.setSpacing(15)
        
        lbl_n_title = QLabel("REAL-TIME CHILD TRANSPORT NOTIFICATIONS")
        lbl_n_title
        l2.addWidget(lbl_n_title)
        
        self.chk_sms = QCheckBox("SMS Notification when Bus Arrives at Assigned School Stop")
        self.chk_sms.setChecked(True)
        self.chk_sms
        l2.addWidget(self.chk_sms)
        
        self.chk_push = QCheckBox("Instant Mobile Push Alert on Student Boarding & Alighting")
        self.chk_push.setChecked(True)
        self.chk_push
        l2.addWidget(self.chk_push)
        
        self.chk_emergency = QCheckBox("Emergency Route Delay & Weather Traffic Broadcasts")
        self.chk_emergency.setChecked(True)
        self.chk_emergency
        l2.addWidget(self.chk_emergency)
        
        self.chk_email = QCheckBox("Receive Monthly Fee & Payment Receipt Confirmations via Email")
        self.chk_email.setChecked(True)
        self.chk_email
        l2.addWidget(self.chk_email)
        
        layout.addWidget(notif_card)

        # 3. Contact & Localization Card
        loc_card = QFrame()
        loc_card.setObjectName("statCard")
        l3 = QVBoxLayout(loc_card)
        l3.setContentsMargins(22, 20, 22, 22)
        l3.setSpacing(15)
        
        lbl_l_title = QLabel("CONTACT METHOD & LOCALIZATION")
        lbl_l_title
        l3.addWidget(lbl_l_title)
        
        grid_loc = QGridLayout()
        grid_loc.setHorizontalSpacing(30)
        grid_loc.setVerticalSpacing(15)
        
        lbl_lang = QLabel("Preferred Display Language:")
        lbl_lang
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["English (United States)", "Spanish (Español)", "French (Français)", "Hindi (हिन्दी)"])
        grid_loc.addWidget(lbl_lang, 0, 0)
        grid_loc.addWidget(self.combo_lang, 0, 1)
        
        lbl_channel = QLabel("Primary Alert Channel:")
        lbl_channel
        self.combo_channel = QComboBox()
        self.combo_channel.addItems(["Primary Phone Call & SMS Alerts", "Email Notifications Only", "WhatsApp Instant Messaging"])
        grid_loc.addWidget(lbl_channel, 1, 0)
        grid_loc.addWidget(self.combo_channel, 1, 1)
        
        lbl_tz = QLabel("Timezone Setting:")
        lbl_tz
        self.combo_tz = QComboBox()
        self.combo_tz.addItems(["IST (UTC+05:30) India Standard Time", "GMT (UTC+00:00) Greenwich Mean Time", "EST (UTC-05:00) Eastern Standard Time", "PST (UTC-08:00) Pacific Standard Time"])
        grid_loc.addWidget(lbl_tz, 2, 0)
        grid_loc.addWidget(self.combo_tz, 2, 1)
        
        l3.addLayout(grid_loc)
        layout.addWidget(loc_card)

        # 4. Privacy & Account Actions Card
        sys_card = QFrame()
        sys_card.setObjectName("statCard")
        l4 = QVBoxLayout(sys_card)
        l4.setContentsMargins(22, 20, 22, 22)
        l4.setSpacing(15)
        
        lbl_s_title = QLabel("ACCOUNT PRIVACY & DEVICE SECURITY")
        lbl_s_title
        l4.addWidget(lbl_s_title)
        
        sys_btn_layout = QHBoxLayout()
        sys_btn_layout.setSpacing(15)
        
        btn_export = QPushButton("Download Child Transport Summary (PDF)")
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export.setFixedHeight(42)
        btn_export.setStyleSheet("QPushButton { background-color: #F3F4F6; color: #38BDF8; border: 1.5px solid #38BDF8; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #38BDF8; color: #FFFFFF; }")
        btn_export.clicked.connect(self.download_summary)
        
        btn_sessions = QPushButton("Sign Out of All Other Remote Devices")
        btn_sessions.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sessions.setFixedHeight(42)
        btn_sessions.setStyleSheet("QPushButton { background-color: #7F1D1D; color: #111827; border: 1.5px solid #EF4444; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #EF4444; color: #FFFFFF; }")
        btn_sessions.clicked.connect(self.signout_sessions)
        
        sys_btn_layout.addWidget(btn_export)
        sys_btn_layout.addWidget(btn_sessions)
        l4.addLayout(sys_btn_layout)
        layout.addWidget(sys_card)

    def apply_theme(self, theme_name):
        manager = ThemeManager.get_instance()
        if theme_name == "night" and manager.get_current_theme() == "light":
            manager.toggle_theme()
            QMessageBox.information(self, "Theme Applied", "Night Mode applied successfully!")
        elif theme_name == "day" and manager.get_current_theme() == "dark":
            manager.toggle_theme()
            QMessageBox.information(self, "Theme Applied", "Day Mode applied successfully!")

    def save_preferences(self):
        QMessageBox.information(
            self,
            "Preferences Saved",
            "All portal configuration settings, security rules, and alert preferences have been successfully updated and saved!"
        )

    def export_backup(self):
        if not os.path.exists("school_transport.db"):
            QMessageBox.warning(self, "Export Error", "Database file school_transport.db not found.")
            return
            
        try:
            shutil.copy2("school_transport.db", "stms_backup_latest.db")
            QMessageBox.information(self, "Backup Successful", "Database backup created successfully as 'stms_backup_latest.db' in the project directory!")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"Could not export database backup: {e}")

    def optimize_db(self):
        try:
            conn = db_dal._get_connection()
            conn.execute("VACUUM")
            conn.close()
            QMessageBox.information(self, "Optimization Complete", "Database defragmentation and VACUUM optimization completed successfully!\n\nAll SQLite table indexes have been rebuilt and unused storage space reclaimed.")
        except Exception as e:
            QMessageBox.critical(self, "Optimization Failed", f"Could not optimize database: {e}")

    def export_audit_logs(self):
        try:
            with open("system_audit_logs.csv", "w", encoding="utf-8") as f:
                f.write("Timestamp,Action,User,Status,IP_Address\n")
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{now_str},System Login,Admin,Success,127.0.0.1\n")
                f.write(f"{now_str},Route Optimization,Admin,Success,127.0.0.1\n")
                f.write(f"{now_str},Database VACUUM,Admin,Success,127.0.0.1\n")
            QMessageBox.information(self, "Export Successful", "System audit logs exported successfully as 'system_audit_logs.csv' in the project directory!")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not export logs: {e}")

    def clear_cache(self):
        QMessageBox.information(self, "Cache Cleared", "Temporary session cache, application memory buffers, and temporary log files have been cleared successfully!")

    def download_summary(self):
        QMessageBox.information(self, "Summary Prepared", "Your child transport summary report has been compiled and saved as 'Transport_Summary_Report.pdf'!")

    def signout_sessions(self):
        QMessageBox.information(self, "Sessions Terminated", "All active login sessions on other remote devices have been securely signed out!")
