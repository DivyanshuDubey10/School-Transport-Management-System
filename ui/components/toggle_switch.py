# ui/components/toggle_switch.py
from PyQt6.QtWidgets import QWidget, QCheckBox
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._position = 3
        self.anim = QPropertyAnimation(self, b"position")
        self.anim.setDuration(250)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self.stateChanged.connect(self.start_animation)
        
    def get_position(self):
        return self._position
        
    def set_position(self, pos):
        self._position = pos
        self.update()
        
    position = pyqtProperty(float, get_position, set_position)
    
    def start_animation(self, state):
        self.anim.stop()
        if state == 2: # Checked
            self.anim.setEndValue(27)
        else:
            self.anim.setEndValue(3)
        self.anim.start()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        if self.isChecked():
            bg_color = QColor("#10B981") # Green
        else:
            bg_color = QColor("#D1D5DB") # Gray
            
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 13, 13)
        
        # Handle
        handle_color = QColor("#FFFFFF")
        painter.setBrush(QBrush(handle_color))
        painter.drawEllipse(int(self._position), 3, 20, 20)
