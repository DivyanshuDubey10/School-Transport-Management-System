# ui/components/toast.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15) # Margin for drop shadow
        
        self.frame = QFrame()
        self.frame.setObjectName("toastFrame")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.frame.setGraphicsEffect(shadow)
        
        frame_layout = QHBoxLayout(self.frame)
        frame_layout.setContentsMargins(20, 16, 25, 16)
        frame_layout.setSpacing(15)
        
        icon_lbl = QLabel()
        
        self.label = QLabel(self.message)
        self.label
        
        if self.type == "success":
            icon_lbl.setText("✓")
            icon_lbl
            self.frame.setStyleSheet("QFrame#toastFrame { background-color: #ECFDF5; border: 1px solid #A7F3D0; border-left: 6px solid #10B981; border-radius: 8px; }")
        else:
            icon_lbl.setText("⚠")
            icon_lbl
            self.frame.setStyleSheet("QFrame#toastFrame { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 6px solid #EF4444; border-radius: 8px; }")
            
        frame_layout.addWidget(icon_lbl)
        frame_layout.addWidget(self.label)
        
        main_layout.addWidget(self.frame)
        
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
