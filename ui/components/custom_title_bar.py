# ui/components/custom_title_bar.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint

class CustomTitleBar(QWidget):
    def __init__(self, parent, title_text="NeoYatra Transport Portal"):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        # Flush right margin and zero spacing so buttons touch edges
        self.layout.setContentsMargins(15, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setFixedHeight(40)
        
        # Transparent background so it blends, but handles clicks
        self
        
        self.title_label = QLabel(title_text)
        self.title_label
        self.layout.addWidget(self.title_label)
        
        self.layout.addStretch()
        
        # Native Windows Caption Buttons Styling
        from PyQt6.QtGui import QFont
        segoe_font = QFont("Segoe MDL2 Assets", 10)
        
        btn_style = """
            QPushButton { border: none; color: #4B5563; background: transparent; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); color: #FFFFFF; }
        """
        close_style = """
            QPushButton { border: none; color: #4B5563; background: transparent; }
            QPushButton:hover { background-color: #E81123; color: #FFFFFF; }
        """
        
        self.btn_min = QPushButton("\uE921")
        self.btn_min.setFont(segoe_font)
        self.btn_min.setFixedSize(46, 40)
        self.btn_min.setStyleSheet(btn_style)
        self.btn_min.clicked.connect(self.parent.showMinimized)
        
        self.btn_max = QPushButton("\uE922")
        self.btn_max.setFont(segoe_font)
        self.btn_max.setFixedSize(46, 40)
        self.btn_max.setStyleSheet(btn_style)
        self.btn_max.clicked.connect(self.toggle_maximize)
        
        self.btn_close = QPushButton("\uE8BB")
        self.btn_close.setFont(segoe_font)
        self.btn_close.setFixedSize(46, 40)
        self.btn_close.setStyleSheet(close_style)
        self.btn_close.clicked.connect(self.parent.close)
        
        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_max)
        self.layout.addWidget(self.btn_close)
        
        self.start = QPoint(0, 0)
        self.pressing = False
        
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.pressing = True
            self.start = event.globalPosition().toPoint() - self.parent.pos()

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.parent.move(event.globalPosition().toPoint() - self.start)

    def mouseReleaseEvent(self, event):
        self.pressing = False
