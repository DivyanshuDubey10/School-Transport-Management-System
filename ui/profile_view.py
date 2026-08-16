from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt
from dal import db_dal
from theme_manager import apply_shadow


def create_initials_avatar(name, size=54, bg_color="#2563EB", text_color="#FFFFFF"):
    lbl = QLabel()
    lbl.setFixedSize(size, size)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    parts = name.strip().split()
    if len(parts) >= 2:
        initials = (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1 and len(parts[0]) > 0:
        initials = parts[0][:2].upper()
    else:
        initials = "US"
    lbl.setText(initials)
    radius = size // 2
    lbl.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; font-weight: 900; font-size: 16pt; border-radius: {radius}px; border: none;")
    return lbl


class ProfileView(QWidget):
    def __init__(self, user_type, user_id=1, dashboard_ref=None):
        super().__init__()
        self.user_type = user_type  # 'admin' or 'parent'
        self.user_id = user_id
        self.dashboard_ref = dashboard_ref
        
        self.init_ui()
        self.load_profile_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # 1. Page Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        title_label = QLabel("Personal Profile & Security")
        title_label.setObjectName("pageTitle")
        title_box.addWidget(title_label)
        
        sub_label = QLabel("Manage your account identity, contact credentials, and security password.")
        sub_label.setObjectName("statDesc")
        title_box.addWidget(sub_label)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()


        main_layout.addLayout(header_layout)

        # Scroll Area for forms
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QWidget#scrollContent { background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 0, 15, 10)
        content_layout.setSpacing(20)

        # 2. Executive Profile Banner
        banner_card = QFrame()
        banner_card.setObjectName("statCard")
        apply_shadow(banner_card)
        banner_layout = QHBoxLayout(banner_card)
        banner_layout.setContentsMargins(20, 18, 20, 18)
        banner_layout.setSpacing(16)
        
        self.avatar_container = QHBoxLayout()
        self.avatar_lbl = create_initials_avatar("User Profile", size=60, bg_color="#2563EB")
        banner_layout.addWidget(self.avatar_lbl)
        
        banner_text = QVBoxLayout()
        banner_text.setSpacing(4)
        self.banner_name_lbl = QLabel("Loading Name...")
        self.banner_name_lbl
        self.banner_role_lbl = QLabel("System Role")
        self.banner_role_lbl
        banner_text.addWidget(self.banner_name_lbl)
        banner_text.addWidget(self.banner_role_lbl)
        banner_layout.addLayout(banner_text)
        
        banner_layout.addStretch()
        
        status_pill = QLabel("Verified Active")
        status_pill
        banner_layout.addWidget(status_pill)
        
        content_layout.addWidget(banner_card)

        # 3. Personal Information Edit Form
        form_card = QFrame()
        form_card.setObjectName("statCard")
        apply_shadow(form_card)
        form_card_layout = QVBoxLayout(form_card)
        form_card_layout.setContentsMargins(22, 20, 22, 22)
        form_card_layout.setSpacing(15)
        
        sec1_title = QLabel("PERSONAL DETAILS & CREDENTIALS")
        sec1_title
        form_card_layout.addWidget(sec1_title)
        
        grid_form = QGridLayout()
        grid_form.setHorizontalSpacing(30)
        grid_form.setVerticalSpacing(15)
        
        lbl_name = QLabel("Full / Guardian Name:")
        lbl_name
        self.entry_name = QLineEdit()
        self.entry_name.setPlaceholderText("Enter your full legal name...")
        grid_form.addWidget(lbl_name, 0, 0)
        grid_form.addWidget(self.entry_name, 0, 1)
        
        lbl_user = QLabel("Account Username:")
        lbl_user
        self.entry_username = QLineEdit()
        self.entry_username.setPlaceholderText("Enter login username...")
        grid_form.addWidget(lbl_user, 1, 0)
        grid_form.addWidget(self.entry_username, 1, 1)
        
        # Parent specific fields
        self.lbl_phone = QLabel("Contact Phone:")
        self.lbl_phone
        self.entry_phone = QLineEdit()
        self.entry_phone.setPlaceholderText("Enter primary mobile number...")
        
        self.lbl_addr = QLabel("Home Address:")
        self.lbl_addr
        self.entry_addr = QLineEdit()
        self.entry_addr.setPlaceholderText("Enter residential address...")
        
        self.lbl_pickup = QLabel("Assigned Pickup Stop:")
        self.lbl_pickup
        self.entry_pickup = QLineEdit()
        self.entry_pickup.setPlaceholderText("Designated bus stop location...")
        
        if self.user_type == 'parent':
            grid_form.addWidget(self.lbl_phone, 2, 0)
            grid_form.addWidget(self.entry_phone, 2, 1)
            grid_form.addWidget(self.lbl_addr, 3, 0)
            grid_form.addWidget(self.entry_addr, 3, 1)
            grid_form.addWidget(self.lbl_pickup, 4, 0)
            grid_form.addWidget(self.entry_pickup, 4, 1)
        else:
            self.lbl_phone.hide()
            self.entry_phone.hide()
            self.lbl_addr.hide()
            self.entry_addr.hide()
            self.lbl_pickup.hide()
            self.entry_pickup.hide()
            
        form_card_layout.addLayout(grid_form)
        content_layout.addWidget(form_card)

        # 4. Security & Password Update Card
        sec_card = QFrame()
        sec_card.setObjectName("statCard")
        apply_shadow(sec_card)
        sec_layout = QVBoxLayout(sec_card)
        sec_layout.setContentsMargins(22, 20, 22, 22)
        sec_layout.setSpacing(15)
        
        sec2_title = QLabel("SECURITY & PASSWORD CHANGE")
        sec2_title
        sec_layout.addWidget(sec2_title)
        
        sec_sub = QLabel("Leave password fields blank if you do not wish to change your current login password.")
        sec_sub
        sec_layout.addWidget(sec_sub)
        
        grid_sec = QGridLayout()
        grid_sec.setHorizontalSpacing(30)
        grid_sec.setVerticalSpacing(15)
        
        lbl_new_pw = QLabel("New Password:")
        lbl_new_pw
        self.entry_new_pw = QLineEdit()
        self.entry_new_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_new_pw.setPlaceholderText("Enter new secure password (optional)...")
        grid_sec.addWidget(lbl_new_pw, 0, 0)
        grid_sec.addWidget(self.entry_new_pw, 0, 1)
        
        lbl_confirm_pw = QLabel("Confirm Password:")
        lbl_confirm_pw
        self.entry_confirm_pw = QLineEdit()
        self.entry_confirm_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_confirm_pw.setPlaceholderText("Re-type new password...")
        grid_sec.addWidget(lbl_confirm_pw, 1, 0)
        grid_sec.addWidget(self.entry_confirm_pw, 1, 1)
        
        sec_layout.addLayout(grid_sec)
        content_layout.addWidget(sec_card)

        # 5. Action Buttons Footer
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        btn_reset = QPushButton("Reset Form")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setFixedSize(140, 42)
        btn_reset.setStyleSheet("QPushButton { background-color: #D1D5DB; color: #111827; border: none; border-radius: 8px; font-weight: bold; font-size: 10.5pt; } QPushButton:hover { background-color: #9CA3AF; }")
        btn_reset.clicked.connect(self.load_profile_data)
        action_layout.addWidget(btn_reset)
        
        btn_save = QPushButton("Save Profile Changes")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setFixedSize(220, 42)
        btn_save.setObjectName("primaryButton")
        btn_save.clicked.connect(self.save_profile)
        action_layout.addWidget(btn_save)
        
        content_layout.addLayout(action_layout)
        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def load_profile_data(self):
        self.entry_new_pw.clear()
        self.entry_confirm_pw.clear()
        
        if self.user_type == 'admin':
            admin_data = db_dal.get_admin_by_id(self.user_id)
            if admin_data:
                uname = admin_data[1]
                fname = admin_data[3]
                self.entry_name.setText(fname)
                self.entry_username.setText(uname)
                self.banner_name_lbl.setText(fname)
                self.banner_role_lbl.setText("System Administrator • Tenant: STMS-ORG")
                
                new_avatar = create_initials_avatar(fname, size=60, bg_color="#2563EB")
                self.avatar_lbl.deleteLater()
                self.avatar_lbl = new_avatar
                self.avatar_lbl.setParent(self)
                self.banner_name_lbl.parentWidget().layout().insertWidget(0, self.avatar_lbl)
        else:
            parent_data = db_dal.get_parent_by_id(self.user_id)
            if parent_data:
                pname = str(parent_data[1])
                phone = str(parent_data[2])
                addr = str(parent_data[3])
                pickup = str(parent_data[4])
                uname = str(parent_data[5])
                
                self.entry_name.setText(pname)
                self.entry_phone.setText(phone)
                self.entry_addr.setText(addr)
                self.entry_pickup.setText(pickup)
                self.entry_username.setText(uname)
                self.banner_name_lbl.setText(pname)
                self.banner_role_lbl.setText("Registered Parent Portal Account")
                
                new_avatar = create_initials_avatar(pname, size=60, bg_color="#38BDF8", text_color="#FFFFFF")
                self.avatar_lbl.deleteLater()
                self.avatar_lbl = new_avatar
                self.avatar_lbl.setParent(self)
                self.banner_name_lbl.parentWidget().layout().insertWidget(0, self.avatar_lbl)

    def save_profile(self):
        name = self.entry_name.text().strip()
        username = self.entry_username.text().strip()
        new_pw = self.entry_new_pw.text().strip()
        confirm_pw = self.entry_confirm_pw.text().strip()
        
        if not name or not username:
            QMessageBox.warning(self, "Validation Error", "Name and Username fields cannot be empty.")
            return
            
        if new_pw or confirm_pw:
            if new_pw != confirm_pw:
                QMessageBox.warning(self, "Security Warning", "New Password and Confirm Password do not match!")
                return
            if len(new_pw) < 4:
                QMessageBox.warning(self, "Security Warning", "Password must be at least 4 characters long.")
                return
        
        if self.user_type == 'admin':
            success = db_dal.update_admin_profile(self.user_id, username, name, password=new_pw if new_pw else None)
            if success:
                QMessageBox.information(self, "Success", "Admin Profile updated successfully!\n\nYour changes have been saved to the secure database.")
                self.load_profile_data()
                if self.dashboard_ref and hasattr(self.dashboard_ref, "update_user_display"):
                    self.dashboard_ref.update_user_display()
            else:
                QMessageBox.critical(self, "Update Failed", "Could not update profile. The username might already be taken by another account.")
        else:
            phone = self.entry_phone.text().strip()
            addr = self.entry_addr.text().strip()
            pickup = self.entry_pickup.text().strip()
            
            if not phone or not addr or not pickup:
                QMessageBox.warning(self, "Validation Error", "Please complete all contact and address fields.")
                return
                
            success = db_dal.update_parent_profile(self.user_id, name, phone, addr, pickup, username, password=new_pw if new_pw else None)
            if success:
                QMessageBox.information(self, "Success", "Parent Account updated successfully!\n\nYour contact details and preferences are now live.")
                self.load_profile_data()
                if self.dashboard_ref and hasattr(self.dashboard_ref, "update_user_display"):
                    self.dashboard_ref.update_user_display()
            else:
                QMessageBox.critical(self, "Update Failed", "Could not update profile. The phone number or username might already be in use.")
