# ui/components/circular_progress.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRectF, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

class CircularProgress(QWidget):
    def __init__(self, parent=None, value=0, max_value=100, color="#38BDF8", title=""):
        super().__init__(parent)
        self.target_value = value
        self.max_value = max_value
        self.color = color
        self.title = title
        
        self.setFixedSize(160, 160)
        self._current_value = 0.0
        
        self.anim = QPropertyAnimation(self, b"current_value")
        self.anim.setDuration(1500)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def set_value(self, val, max_val=None):
        if max_val is not None:
            self.max_value = max_val
        self.target_value = val
        self.anim.setStartValue(self._current_value)
        self.anim.setEndValue(val)
        self.anim.start()
        
    def get_current_value(self):
        return self._current_value
        
    def set_current_value(self, val):
        self._current_value = val
        self.update()
        
    current_value = pyqtProperty(float, get_current_value, set_current_value)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        margin = 15
        rect = QRectF(margin, margin, width - margin * 2, height - margin * 2)
        
        # Background ring
        pen_bg = QPen(QColor("#1E293B"))
        pen_bg.setWidth(12)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect.toRect(), 0, 360 * 16)
        
        # Foreground ring (progress)
        if self.max_value > 0:
            percentage = self._current_value / self.max_value
        else:
            percentage = 0
            
        span_angle = int(-percentage * 360 * 16)
        
        pen_fg = QPen(QColor(self.color))
        pen_fg.setWidth(12)
        pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_fg)
        painter.drawArc(rect.toRect(), 90 * 16, span_angle)
        
        # Draw Value
        painter.setPen(QColor("#F8FAFC"))
        font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        painter.setFont(font)
        
        # We can format it nicely
        if self.max_value == 100 and not self.title:
            text = f"{int(self._current_value)}%"
        else:
            text = f"{int(self._current_value)}"
            
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        
        # Draw Title
        if self.title:
            font_title = QFont("Segoe UI", 9, QFont.Weight.Bold)
            painter.setFont(font_title)
            painter.setPen(QColor("#94A3B8"))
            title_rect = QRectF(rect.x(), rect.y() + 30, rect.width(), rect.height())
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, self.title)
