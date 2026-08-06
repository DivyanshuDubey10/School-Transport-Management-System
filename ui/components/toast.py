# ui/components/toast.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, QEasingCurve, QRect
from PyQt6.QtGui import QColor, QPalette

class ToastNotification(QWidget):
    def __init__(self, parent, message, type="success", duration=3000):
        super().__init__(parent)
        self.parent = parent
        self.message = message
        self.type = type
        self.duration = duration
        self.initUI()
        
    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        self.label = QLabel(self.message)
        self.label.setStyleSheet("color: white; font-weight: bold; font-size: 11pt;")
        layout.addWidget(self.label)
        
        bg_color = "#10B981" if self.type == "success" else "#EF4444"
        self.setStyleSheet(f"background-color: {bg_color}; border-radius: 8px;")
        
        self.adjustSize()
        self.position_toast()
        self.show_animation()
        
    def position_toast(self):
        # Position in bottom right of the parent
        parent_rect = self.parent.geometry()
        x = parent_rect.x() + parent_rect.width() - self.width() - 30
        y = parent_rect.y() + parent_rect.height() - self.height() - 30
        self.move(x, y)
        
    def show_animation(self):
        self.setWindowOpacity(0.0)
        self.show()
        
        self.anim_in = QPropertyAnimation(self, b"windowOpacity")
        self.anim_in.setDuration(300)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.anim_in.finished.connect(self.start_timer)
        self.anim_in.start()
        
    def start_timer(self):
        QTimer.singleShot(self.duration, self.hide_animation)
        
    def hide_animation(self):
        self.anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.anim_out.setDuration(300)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim_out.finished.connect(self.close)
        self.anim_out.start()
