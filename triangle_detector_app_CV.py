import sys
import cv2
import numpy as np
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QSpinBox, 
                              QHBoxLayout, QPushButton, QComboBox, QGridLayout, QTextEdit, QFrame)
from PySide6.QtGui import QImage, QPixmap, QFont, QColor
from PySide6.QtCore import QTimer, Qt, QThread, Signal, QRect, QSize
import json
import os

class VideoDisplayWidget(QWidget):
    """Container widget that overlays UI elements on video"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(480, 320)
        self.setMaximumSize(480, 320)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video label
        self.video_label = QLabel(self)
        self.video_label.setMinimumSize(480, 320)
        self.video_label.setMaximumSize(480, 320)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        
        # Vertical center line
        self.line_widget = QFrame(self)
        self.line_widget.setStyleSheet("background-color: lime; border: none;")
        self.line_widget.setGeometry(239, 0, 2, 320)
        
        # Status label
        self.status_label = QLabel(self)
        self.status_label.setStyleSheet(
            "background-color: red; color: white; font-weight: bold; "
            "font-size: 14px; padding: 5px 10px; border-radius: 3px;"
        )
        self.status_label.setText("Wait")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.adjustSize()
        self.update_status_position()
    
    def update_status_position(self):
        """Position status label at top right"""
        self.status_label.adjustSize()
        x = 480 - self.status_label.width() - 10
        y = 10
        self.status_label.setGeometry(x, y, self.status_label.width(), self.status_label.height())
    
    def set_status(self, status, is_ok=False):
        """Update status label"""
        self.status_label.setText(status)
        if is_ok:
            self.status_label.setStyleSheet(
                "background-color: lime; color: black; font-weight: bold; "
                "font-size: 14px; padding: 5px 10px; border-radius: 3px;"
            )
        else:
            self.status_label.setStyleSheet(
                "background-color: red; color: white; font-weight: bold; "
                "font-size: 14px; padding: 5px 10px; border-radius: 3px;"
            )
        self.update_status_position()
    
    def set_pixmap(self, pixmap):
        """Set video frame pixmap"""
        self.video_label.setPixmap(pixmap)

class CameraWorker(QThread):
    frame_ready = Signal(np.ndarray)
    error_signal = Signal(str)
    
    def __init__(self, camera_id=0):
        super().__init__()
        self.running = True
        self.cap = None
        self.camera_id = camera_id
        
    def run(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Check if camera opened successfully
            if not self.cap.isOpened():
                self.error_signal.emit(f"Failed to open camera {self.camera_id}")
                return
            
            while self.running:
                ret, frame = self.cap.read()
                if ret:
                    self.frame_ready.emit(frame)
                else:
                    break
        except Exception as e:
            self.error_signal.emit(f"Camera error: {str(e)}")
    
    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
    
    def change_camera(self, camera_id):
        """Change camera without stopping thread"""
        self.camera_id = camera_id
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(camera_id)


class TriangleDetector:
    def __init__(self):
        self.threshold1 = 50
        self.threshold2 = 150
        self.min_area = 10  # Minimum triangle area in pixels
        
    def detect_triangles(self, frame):
        """Detect triangles using contour analysis"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, self.threshold1, self.threshold2)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        triangles = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            area = cv2.contourArea(contour)
            
            # Filter: 3 vertices = triangle, minimum area
            if len(approx) == 3 and area > self.min_area:
                # Calculate centroid
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    triangles.append({
                        'contour': contour,
                        'approx': approx,
                        'center': (cx, cy),
                        'area': area
                    })
        
        return triangles
    
    def get_largest_triangle(self, triangles):
        """Get triangle with largest area"""
        if not triangles:
            return None
        return max(triangles, key=lambda t: t['area'])

class TriangleDetectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MHSF Triangle Detector")
        self.setWindowState(Qt.WindowMaximized)
        
        # Configuration
        self.config_file = "triangle_config.json"
        self.distance_threshold = 15  # pixels
        self.min_triangle_area = 10  # pixels
        self.load_config()
        
        # Initialize detector
        self.detector = TriangleDetector()
        self.detector.min_area = self.min_triangle_area
        self.current_frame = None
        self.triangles = []
        self.latest_triangle = None
        
        # Camera worker
        self.camera_worker = None
        
        # Setup UI
        self.init_ui()
        
        # Start camera
        self.start_camera(0)
    
    def get_available_cameras(self):
        """Detect available cameras"""
        available_cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
            else:
                break
        return available_cameras
    
    def init_ui(self):
        """Initialize UI components"""
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Top control panel - Camera selection
        camera_layout = QHBoxLayout()
        camera_layout.addWidget(QLabel("Select Camera:"))
        
        self.camera_combo = QComboBox()
        available_cameras = self.get_available_cameras()
        for cam_id in available_cameras:
            self.camera_combo.addItem(f"Camera {cam_id}", cam_id)
        
        if not available_cameras:
            self.camera_combo.addItem("No cameras found", -1)
        
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)
        camera_layout.addWidget(self.camera_combo)
        camera_layout.setAlignment(Qt.AlignCenter)
        
        main_layout.addLayout(camera_layout)
        
        # Video display with overlays
        self.video_display = VideoDisplayWidget()
        video_container = QHBoxLayout()
        video_container.addStretch()
        video_container.addWidget(self.video_display)
        video_container.addStretch()
        main_layout.addLayout(video_container)
        
        # Control panel - Distance threshold and Min Area
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Distance Threshold (px):"))
        
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setMinimum(10)
        self.threshold_spinbox.setMaximum(300)
        self.threshold_spinbox.setValue(self.distance_threshold)
        self.threshold_spinbox.valueChanged.connect(self.update_threshold)
        control_layout.addWidget(self.threshold_spinbox)
        
        control_layout.addSpacing(20)
        control_layout.addWidget(QLabel("Min Area (px²):"))
        
        self.min_area_spinbox = QSpinBox()
        self.min_area_spinbox.setMinimum(1)
        self.min_area_spinbox.setMaximum(5000)
        self.min_area_spinbox.setValue(self.min_triangle_area)
        self.min_area_spinbox.valueChanged.connect(self.update_min_area)
        control_layout.addWidget(self.min_area_spinbox)
        
        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save_config)
        control_layout.addWidget(save_btn)
        control_layout.setAlignment(Qt.AlignCenter)
        
        main_layout.addLayout(control_layout)
        
        self.setLayout(main_layout)
    
    def start_camera(self, camera_id):
        """Start camera worker"""
        if self.camera_worker is not None:
            self.camera_worker.stop()
            self.camera_worker.wait()
        
        self.camera_worker = CameraWorker(camera_id)
        self.camera_worker.frame_ready.connect(self.process_frame)
        self.camera_worker.error_signal.connect(self.on_camera_error)
        self.camera_worker.start()
    
    def on_camera_changed(self, index):
        """Handle camera selection change"""
        camera_id = self.camera_combo.currentData()
        if camera_id >= 0:
            self.start_camera(camera_id)
    
    def on_camera_error(self, error_msg):
        """Handle camera error"""
        print(f"ERROR: {error_msg}")
    
    def process_frame(self, frame):
        """Process camera frame"""
        self.current_frame = frame.copy()
        
        # Detect triangles
        self.triangles = self.detector.detect_triangles(frame)
        self.latest_triangle = self.detector.get_largest_triangle(self.triangles)
        
        # Draw on frame
        display_frame = self.draw_on_frame(frame)
        
        # Convert to QPixmap and display
        self.display_frame(display_frame)
    
    def draw_on_frame(self, frame):
        """Draw detected triangles on frame"""
        display_frame = frame.copy()
        
        # Draw triangles
        if self.triangles:
            for triangle in self.triangles:
                cv2.drawContours(display_frame, [triangle['approx']], 0, (255, 0, 0), 2)
                cv2.circle(display_frame, triangle['center'], 5, (0, 0, 255), -1)
        
        return display_frame
    
    def display_frame(self, frame):
        """Display frame on video widget and update status"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = 3 * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_display.set_pixmap(pixmap)
        
        # Calculate distance and update status
        status = "Wait"
        is_ok = False
        
        if self.latest_triangle:
            center_x = w // 2
            triangle_center_x = self.latest_triangle['center'][0]
            distance = abs(triangle_center_x - center_x)
            
            if distance <= self.distance_threshold:
                status = "OK"
                is_ok = True
        
        self.video_display.set_status(status, is_ok)
    
    def update_threshold(self, value):
        """Update distance threshold"""
        self.distance_threshold = value
    
    def update_min_area(self, value):
        """Update minimum triangle area"""
        self.min_triangle_area = value
        self.detector.min_area = value
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            'distance_threshold': self.distance_threshold,
            'min_triangle_area': self.min_triangle_area,
            'resolution': [320, 480],
            'camera_id': self.camera_combo.currentData()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        print("Config saved successfully!")
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.distance_threshold = config.get('distance_threshold', 15)
                    self.min_triangle_area = config.get('min_triangle_area', 10)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def closeEvent(self, event):
        """Cleanup on close"""
        if self.camera_worker is not None:
            self.camera_worker.stop()
            self.camera_worker.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = TriangleDetectorApp()
    window.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
