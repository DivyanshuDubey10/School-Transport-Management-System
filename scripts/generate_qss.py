import os

os.makedirs('themes', exist_ok=True)

light_qss = """
/* =========================================================
   STMS - LIGHT THEME
   School Transport Management System
   ========================================================= */

QWidget {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 14px;
}

/* Explicit transparent background for labels to avoid weird nesting */
QLabel {
    background: transparent;
    color: #0F172A;
}

/* Primary Window Background */
QMainWindow, QDialog {
    background-color: #F8FAFC;
}

/* =========================
   Sidebar
   ========================= */
#sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

#sidebarButton {
    background-color: transparent;
    color: #0F172A;
    border: none;
    border-radius: 8px;
    padding: 11px 14px;
    text-align: left;
    font-weight: 600;
}
#sidebarButton:hover {
    background-color: #EFF6FF;
    color: #2563EB;
}
#sidebarButton:checked {
    background-color: #2563EB;
    color: #FFFFFF;
}

/* =========================
   Top Bar
   ========================= */
#topBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
}
#pageTitle {
    font-size: 20px;
    font-weight: bold;
    color: #0F172A;
}

/* =========================
   Cards & Stats
   ========================= */
#statCard, QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}
QGroupBox {
    margin-top: 10px;
    padding-top: 15px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 5px;
    color: #0F172A;
    font-weight: bold;
}
#statTitle {
    color: #64748B;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
}
#statValue {
    color: #0F172A;
    font-weight: bold;
    font-size: 26px;
}
#statDesc {
    color: #64748B;
    font-size: 12px;
}

/* =========================
   Buttons
   ========================= */
QPushButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1D4ED8;
}

#actionButton {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    font-weight: bold;
    font-size: 14px;
    padding: 12px 16px;
    text-align: left;
}
#actionButton:hover {
    background-color: #EFF6FF;
    color: #2563EB;
    border-color: #CBD5E1;
}

#secondaryButton {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
}
#secondaryButton:hover {
    background-color: #F1F5F9;
}

#dangerButton {
    background-color: #EF4444;
    color: #FFFFFF;
}
#dangerButton:hover {
    background-color: #DC2626;
}

/* =========================
   Inputs & Combo Boxes
   ========================= */
QLineEdit, QComboBox, QSpinBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #2563EB;
}

/* =========================
   Tables
   ========================= */
QTableWidget {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #E2E8F0;
    selection-background-color: #DBEAFE;
    selection-color: #1E40AF;
}
QHeaderView::section {
    background-color: #F1F5F9;
    color: #334155;
    font-weight: bold;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
    border-right: 1px solid #E2E8F0;
}
QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #E2E8F0;
}

/* =========================
   Scrollbars
   ========================= */
QScrollBar:vertical {
    background: #F1F5F9;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #F1F5F9;
    height: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:horizontal {
    background: #CBD5E1;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #94A3B8;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""

dark_qss = """
/* =========================================================
   STMS - DARK THEME
   School Transport Management System
   ========================================================= */

QWidget {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 14px;
}

QLabel {
    background: transparent;
    color: #F8FAFC;
}

QMainWindow, QDialog {
    background-color: #0F172A;
}

#sidebar {
    background-color: #111827;
    border-right: 1px solid #334155;
}

#sidebarButton {
    background-color: transparent;
    color: #F8FAFC;
    border: none;
    border-radius: 8px;
    padding: 11px 14px;
    text-align: left;
    font-weight: 600;
}
#sidebarButton:hover {
    background-color: #1E293B;
    color: #60A5FA;
}
#sidebarButton:checked {
    background-color: #2563EB;
    color: #FFFFFF;
}

#topBar {
    background-color: #111827;
    border-bottom: 1px solid #334155;
}
#pageTitle {
    font-size: 20px;
    font-weight: bold;
    color: #F8FAFC;
}

#statCard, QGroupBox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
}
QGroupBox {
    margin-top: 10px;
    padding-top: 15px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 5px;
    color: #F8FAFC;
    font-weight: bold;
}
#statTitle {
    color: #94A3B8;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
}
#statValue {
    color: #F8FAFC;
    font-weight: bold;
    font-size: 26px;
}
#statDesc {
    color: #CBD5E1;
    font-size: 12px;
}

QPushButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #3B82F6;
}

#actionButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    font-size: 14px;
    padding: 12px 16px;
    text-align: left;
}
#actionButton:hover {
    background-color: #3B82F6;
}

#secondaryButton {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #475569;
}
#secondaryButton:hover {
    background-color: #334155;
}

#dangerButton {
    background-color: #EF4444;
    color: #FFFFFF;
}
#dangerButton:hover {
    background-color: #F87171;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 8px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #60A5FA;
}

QTableWidget {
    background-color: #111827;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #334155;
    selection-background-color: #1E3A5F;
    selection-color: #FFFFFF;
}
QHeaderView::section {
    background-color: #1E293B;
    color: #F8FAFC;
    font-weight: bold;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #334155;
    border-right: 1px solid #334155;
}
QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #334155;
}

QScrollBar:vertical {
    background: #111827;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #475569;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #64748B;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #111827;
    height: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:horizontal {
    background: #475569;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #64748B;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""

with open('themes/light.qss', 'w') as f:
    f.write(light_qss)

with open('themes/dark.qss', 'w') as f:
    f.write(dark_qss)
