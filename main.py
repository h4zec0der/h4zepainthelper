import sys
import ctypes
from ctypes import wintypes
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QSlider, QLabel, QFileDialog, 
                            QSizePolicy, QMessageBox, QAction)
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, QSize
from PyQt5.QtGui import QPixmap, QPainter, QCursor, QColor
import win32gui
import win32con

class h4zeovrls112122(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_window()
        self.image = None
        self.opacity = 0.5
        self.image_rect = QRectF(0, 0, 300, 300)
        self.fixed = False
        self.draggable = True
        self.drag_position = QPointF()
        self.resize_handle_size = 10
        self.is_resizing = False
        self.resize_corner = None

    def setup_window(self):
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        screen = QApplication.primaryScreen()
        self.setGeometry(screen.geometry())
        self.setMouseTracking(True)

    def set_image(self, image_path):
        try:
            self.image = QPixmap(image_path)
            if not self.image.isNull():
                self.image_rect = QRectF(
                    self.width()/2 - self.image.width()/2,
                    self.height()/2 - self.image.height()/2,
                    self.image.width(),
                    self.image.height()
                )
                self.update()
                return True
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Unable to load image: {str(e)}")
            return False

    def set_opacity(self, value):
        self.opacity = max(0.1, min(1.0, value / 100))
        self.update()

    def fix_position(self):
        self.fixed = True
        self.draggable = False
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        try:
            hwnd = self.winId()
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(
                hwnd, 
                win32con.GWL_EXSTYLE,
                style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            )
        except Exception as e:
            print(f"WinAPI error: {e}")
        
        self.update()

    def get_corners(self):
        rect = self.image_rect
        return [
            rect.topLeft(),     # Top-left
            rect.topRight(),    # Top-right
            rect.bottomLeft(),  # Bottom-left
            rect.bottomRight()  # Bottom-right
        ]

    def is_point_near_corner(self, point):
        corners = self.get_corners()
        for i, corner in enumerate(corners):
            if (point - corner).manhattanLength() < self.resize_handle_size:
                return i  
        return None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.image and not self.image.isNull():
            painter.setOpacity(self.opacity)
            painter.drawPixmap(self.image_rect, self.image, QRectF(self.image.rect()))
        
        if not self.fixed:
            painter.setOpacity(1.0)
            painter.setPen(QColor(255, 0, 0))
            painter.setBrush(QColor(255, 0, 0, 100))
            
            painter.drawRect(self.image_rect)
            
            for corner in self.get_corners():
                painter.drawEllipse(corner, self.resize_handle_size, self.resize_handle_size)
        
        painter.end()

    def mousePressEvent(self, event):
        if self.fixed:
            return
            
        pos = event.pos()
        
        corner_index = self.is_point_near_corner(pos)
        if corner_index is not None:
            self.is_resizing = True
            self.resize_corner = corner_index
            self.drag_position = pos
            return
            
        if self.image_rect.contains(pos):
            self.draggable = True
            self.drag_position = pos - self.image_rect.topLeft()
            return

    def mouseMoveEvent(self, event):
        if self.fixed:
            return
            
        pos = event.pos()
        
        if self.is_resizing and self.resize_corner is not None:
            delta = pos - self.drag_position
            rect = self.image_rect
            
            if self.resize_corner == 0:  # Top-left
                rect.setTopLeft(rect.topLeft() + delta)
            elif self.resize_corner == 1:  # Top-right
                rect.setTopRight(rect.topRight() + delta)
            elif self.resize_corner == 2:  # Bottom-left
                rect.setBottomLeft(rect.bottomLeft() + delta)
            elif self.resize_corner == 3:  # Bottom-right
                rect.setBottomRight(rect.bottomRight() + delta)
            
            if rect.width() < 50:
                rect.setWidth(50)
            if rect.height() < 50:
                rect.setHeight(50)
            
            self.image_rect = rect.normalized()
            self.drag_position = pos
            self.update()
            return
            
        if self.draggable:
            new_pos = pos - self.drag_position
            self.image_rect.moveTo(new_pos)
            self.update()
            return
            
        if self.is_point_near_corner(pos) is not None:
            self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self.draggable = False
        self.is_resizing = False
        self.resize_corner = None

    def nativeEvent(self, eventType, message):
        try:
            msg = wintypes.MSG.from_address(message.__int__())
            if msg.message == win32con.WM_NCHITTEST and self.fixed:
                return True, win32con.HTTRANSPARENT
        except:
            pass
        return super().nativeEvent(eventType, message)

class h76sdfg45dg(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.overlay = h4zeovrls112122()
        self.setup_hotkeys()
        
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(500)

    def setup_ui(self):
        self.setWindowTitle("h4zepaint helper 1.0")
        self.setGeometry(100, 100, 450, 300)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        self.load_btn = QPushButton("📁 Load image")
        self.load_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.load_btn.clicked.connect(self.load_image)
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Transparency:"))
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(50)
        self.opacity_slider.valueChanged.connect(
            lambda v: self.overlay.set_opacity(v)
        )
        opacity_layout.addWidget(self.opacity_slider)
        
        self.opacity_label = QLabel("50%")
        opacity_layout.addWidget(self.opacity_label)
        
        self.show_btn = QPushButton("👁 Show overlay")
        self.show_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-weight: bold;
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.show_btn.clicked.connect(self.show_overlay)
        
        self.fix_btn = QPushButton("🔒 Fix overlay position")
        self.fix_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-weight: bold;
                background-color: #f44336;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.fix_btn.clicked.connect(self.fix_overlay)
        self.fix_btn.setEnabled(False)
        
        self.status_label = QLabel("Status: Waiting for image")
        self.status_label.setStyleSheet("font-style: italic; color: #666;")
        
        hotkey_label = QLabel("Hotkeys:")
        hotkey_label.setStyleSheet("font-weight: bold;")
        
        hotkeys = QLabel("• Ctrl+O - Show overlay\n• Ctrl+H - Hide overlay\n• Ctrl+F - Fix overlay pos")
        hotkeys.setStyleSheet("color: #444;")
        
        layout.addWidget(self.load_btn)
        layout.addLayout(opacity_layout)
        layout.addWidget(self.show_btn)
        layout.addWidget(self.fix_btn)
        layout.addSpacing(20)
        layout.addWidget(self.status_label)
        layout.addSpacing(10)
        layout.addWidget(hotkey_label)
        layout.addWidget(hotkeys)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )

    def setup_hotkeys(self):
        self.show_btn.setShortcut("Ctrl+O")
        self.fix_btn.setShortcut("Ctrl+F")
        
        hide_action = QAction("Hide Overlay", self)
        hide_action.setShortcut("Ctrl+H")
        hide_action.triggered.connect(self.overlay.hide)
        self.addAction(hide_action) 

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open image", "", 
            "Images (*.png *.jpg *.bmp);;All files (*.*)"
        )
        
        if file_name:
            success = self.overlay.set_image(file_name)
            if success:
                self.status_label.setText("Status: Image uploaded. You can change size and position.")
                self.fix_btn.setEnabled(True)
                self.show_overlay()
            else:
                self.status_label.setText("Status: Error uploading image")

    def show_overlay(self):
        if self.overlay.image:
            self.overlay.show()
            self.status_label.setText("Status: Overlay active. Now u can change postion.")
        else:
            self.status_label.setText("Status: Upload image before changing position")

    def fix_overlay(self):
        if self.overlay.image:
            self.overlay.fix_position()
            self.status_label.setText("Status: Overlay fixed! Enjoy!")
            self.fix_btn.setEnabled(False)
            
            QTimer.singleShot(100, lambda: [
                self.overlay.hide(),
                self.overlay.show()
            ])
        else:
            self.status_label.setText("Status: No image to fix")

    def update_status(self):
        if not self.overlay.image:
            self.status_label.setText("Status: Waiting for image upload")
        elif self.overlay.fixed:
            self.status_label.setText("Status: Overlay fixed! Enjoy!")
        elif self.overlay.isVisible():
            self.status_label.setText("Status: Overlay active. Now u can change postion.")

    def closeEvent(self, event):
        self.overlay.close()
        event.accept()

if __name__ == "__main__":
    from PyQt5.QtCore import Qt, QCoreApplication

    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = h76sdfg45dg()
    window.show()
    

    sys.exit(app.exec_())
