import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QSpinBox, 
                              QHBoxLayout, QPushButton, QComboBox, QGridLayout, QTextEdit, QFrame)
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor
from PyQt5.QtCore import QTimer, Qt, QThread, Signal, QRect, QSize
import json
import os
import time

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
        
        # Vertical center line (green)
        self.line_widget = QFrame(self)
        self.line_widget.setStyleSheet("background-color: lime; border: none;")
        self.line_widget.setGeometry(239, 0, 2, 320)
        
        # Left offset line (yellow)
        self.left_line_widget = QFrame(self)
        self.left_line_widget.setStyleSheet("background-color: yellow; border: none;")
        self.left_line_widget.setGeometry(224, 0, 2, 320)  # Default: center - 15
        
        # Right offset line (yellow)
        self.right_line_widget = QFrame(self)
        self.right_line_widget.setStyleSheet("background-color: yellow; border: none;")
        self.right_line_widget.setGeometry(254, 0, 2, 320)  # Default: center + 15
        
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
        
        # FPS label (top right)
        self.fps_label = QLabel(self)
        self.fps_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 180); color: #00FF00; font-weight: bold; "
            "font-size: 12px; padding: 3px 8px; border-radius: 3px; font-family: 'Courier';"
        )
        self.fps_label.setText("FPS: 0.0")
        self.fps_label.setAlignment(Qt.AlignCenter)
        self.update_fps_position()
    
    def update_status_position(self):
        """Position status label at top right"""
        self.status_label.adjustSize()
        x = 480 - self.status_label.width() - 10
        y = 10
        self.status_label.setGeometry(x, y, self.status_label.width(), self.status_label.height())
    
    def update_fps_position(self):
        """Position FPS label at top right, below status"""
        self.fps_label.adjustSize()
        x = 480 - self.fps_label.width() - 10
        y = 50  # Below status label
        self.fps_label.setGeometry(x, y, self.fps_label.width(), self.fps_label.height())
    
    def set_fps(self, fps):
        """Update FPS label"""
        self.fps_label.setText(f"FPS: {fps:.1f}")
        self.update_fps_position()
    
    def update_offset_lines(self, distance_threshold):
        """Update position of yellow offset lines based on distance_threshold"""
        center_x = 239  # Center of 480px width
        left_x = max(0, center_x - distance_threshold)
        right_x = min(478, center_x + distance_threshold)  # 478 to keep line within bounds
        
        self.left_line_widget.setGeometry(left_x, 0, 2, 320)
        self.right_line_widget.setGeometry(right_x, 0, 2, 320)
    
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
            self.cap.set(cv2.CAP_PROP_FPS, 60)
            
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


class DetectionWorker(QThread):
    """Worker thread for triangle detection to prevent blocking UI"""
    detection_ready = Signal(list, object)  # Emits (triangles, latest_triangle)
    
    def __init__(self, detector):
        super().__init__()
        self.running = True
        self.detector = detector
        self.current_frame = None
        self.frame_lock = False
        
    def set_frame(self, frame):
        """Set frame for detection"""
        self.current_frame = frame.copy()
        self.frame_lock = False
    
    def run(self):
        while self.running:
            if self.current_frame is not None and not self.frame_lock:
                self.frame_lock = True
                frame = self.current_frame
                
                # Perform detection on this thread
                triangles = self.detector.detect_triangles(frame)
                latest_triangle = self.detector.get_largest_triangle(triangles)
                
                # Emit results back to main thread
                self.detection_ready.emit(triangles, latest_triangle)
            else:
                # Small sleep to prevent CPU spinning
                self.msleep(1)
    
    def stop(self):
        self.running = False
        self.wait()


class TriangleDetector:
    def __init__(self):
        self.threshold1 = 50
        self.threshold2 = 150
        self.min_area = 10  # Minimum triangle area in pixels
        self.min_angle = 50  # Minimum angle in degrees
        self.max_angle = 70  # Maximum angle in degrees
    
    def calculate_angles(self, points):
        """Calculate angles (in degrees) from three triangle vertices"""
        if len(points) != 3:
            return None
        
        p1, p2, p3 = [tuple(p[0]) for p in points]
        
        # Calculate vectors for each angle
        # Angle at p1
        v1_a = np.array(p2) - np.array(p1)
        v1_b = np.array(p3) - np.array(p1)
        angle1 = self.angle_between_vectors(v1_a, v1_b)
        
        # Angle at p2
        v2_a = np.array(p1) - np.array(p2)
        v2_b = np.array(p3) - np.array(p2)
        angle2 = self.angle_between_vectors(v2_a, v2_b)
        
        # Angle at p3
        v3_a = np.array(p1) - np.array(p3)
        v3_b = np.array(p2) - np.array(p3)
        angle3 = self.angle_between_vectors(v3_a, v3_b)
        
        return [angle1, angle2, angle3]
    
    def angle_between_vectors(self, v1, v2):
        """Calculate angle (in degrees) between two vectors"""
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle_rad = np.arccos(cos_angle)
        angle_deg = np.degrees(angle_rad)
        return angle_deg
    
    def is_valid_angle_range(self, angles):
        """Check if all angles are within the valid range (50-70 degrees)"""
        if angles is None or len(angles) != 3:
            return False
        return all(self.min_angle <= angle <= self.max_angle for angle in angles)
        
    def is_triangle_like(self, approx, hull):
        """Check if approximation or hull is triangle-like (3 main corners with valid angles)"""
        # Accept exact triangles (3 vertices) with valid angles
        if len(approx) == 3:
            angles = self.calculate_angles(approx)
            if self.is_valid_angle_range(angles):
                return True
        
        # Accept shapes with 4-5 vertices if convex hull is triangle with valid angles
        # (indicates rounded corners)
        if len(hull) == 3 and 3 <= len(approx) <= 5:
            angles = self.calculate_angles(hull)
            if self.is_valid_angle_range(angles):
                return True
        
        return False
    
    def detect_triangles(self, frame):
        """Detect triangles using contour analysis (including rounded corners)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, self.threshold1, self.threshold2)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        triangles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Skip small contours
            if area <= self.min_area:
                continue
            
            # Get convex hull to detect fundamental shape
            hull = cv2.convexHull(contour)
            
            # Try strict approximation first (perfect triangles)
            approx_strict = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            
            # Try lenient approximation (rounded corners)
            approx_lenient = cv2.approxPolyDP(contour, 0.05 * cv2.arcLength(contour, True), True)
            
            # Use strict first, fall back to lenient
            approx = approx_strict if len(approx_strict) <= 5 else approx_lenient
            
            # Check if it's triangle-like
            if self.is_triangle_like(approx, hull):
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
        
        # Configuration
        self.config_file = "triangle_config.json"
        self.distance_threshold = 15  # pixels
        self.min_triangle_area = 10  # pixels
        self.fullscreen_mode = False  # Default to windowed mode
        self.load_config()
        
        # Initialize detector
        self.detector = TriangleDetector()
        self.detector.min_area = self.min_triangle_area
        self.current_frame = None
        self.triangles = []
        self.latest_triangle = None
        
        # Status stability counters
        self.ok_frame_count = 0  # Frames with triangle within threshold
        self.wait_frame_count = 0  # Frames without triangle or outside threshold
        self.ok_threshold = 2  # Need 2 consecutive frames to show OK
        self.wait_threshold = 10  # Need 10 consecutive frames to show Wait
        self.current_status = "Wait"  # Start with Wait
        
        # FPS tracking
        self.frame_times = []
        self.fps = 0
        self.frame_start_time = time.time()
        self.max_fps = 60
        self.frame_interval = 1.0 / self.max_fps
        self.last_frame_time = 0
        
        # Camera worker
        self.camera_worker = None
        
        # Detection worker (separate thread for processing)
        self.detection_worker = DetectionWorker(self.detector)
        self.detection_worker.detection_ready.connect(self.on_detection_ready)
        self.detection_worker.start()
        
        # Setup UI
        self.init_ui()
        
        # Apply window state (windowed by default, or fullscreen if saved)
        if self.fullscreen_mode:
            self.showFullScreen()
        else:
            self.setWindowState(Qt.WindowMaximized)
        
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
        
        # Initialize offset lines with current distance threshold
        self.video_display.update_offset_lines(self.distance_threshold)
        
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
        
        # Fullscreen toggle button
        self.fullscreen_btn = QPushButton("Fullscreen: OFF")
        self.fullscreen_btn.setMaximumWidth(120)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        control_layout.addWidget(self.fullscreen_btn)
        
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
        """Receive camera frame and pass to detection worker"""
        # Enforce maximum FPS
        current_time = time.time()
        time_since_last_frame = current_time - self.last_frame_time
        
        if time_since_last_frame < self.frame_interval:
            return  # Skip this frame to maintain max FPS
        
        self.last_frame_time = current_time
        self.current_frame = frame.copy()
        
        # Calculate FPS
        self.frame_times.append(current_time)
        
        # Keep only last 30 frames for FPS calculation
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        
        if len(self.frame_times) > 1:
            self.fps = len(self.frame_times) / (self.frame_times[-1] - self.frame_times[0])
        
        # Pass frame to detection worker instead of detecting here
        self.detection_worker.set_frame(frame)
        
        # Display frame immediately (without waiting for detection)
        display_frame = frame.copy()
        self.display_frame_quick(display_frame)
    
    def on_detection_ready(self, triangles, latest_triangle):
        """Callback when detection is complete"""
        self.triangles = triangles
        self.latest_triangle = latest_triangle
    
    def draw_on_frame(self, frame):
        """Draw detected triangles on frame"""
        display_frame = frame.copy()
        
        # Draw triangles
        if self.triangles:
            for triangle in self.triangles:
                cv2.drawContours(display_frame, [triangle['approx']], 0, (255, 0, 0), 2)
                cv2.circle(display_frame, triangle['center'], 5, (0, 0, 255), -1)
        
        return display_frame
    
    def display_frame_quick(self, frame):
        """Display frame immediately with latest detection results"""
        # Draw triangles
        display_frame = self.draw_on_frame(frame)
        
        # Convert to QPixmap and display
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = 3 * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_display.set_pixmap(pixmap)
        
        # Check if triangle is within acceptance zone
        triangle_ok = False
        
        if self.latest_triangle:
            center_x = w // 2
            triangle_center_x = self.latest_triangle['center'][0]
            distance = abs(triangle_center_x - center_x)
            
            if distance <= self.distance_threshold:
                triangle_ok = True
        
        # Update frame counters for status stability
        if triangle_ok:
            self.ok_frame_count += 1
            self.wait_frame_count = 0  # Reset wait counter
            
            # Show OK status after threshold frames
            if self.ok_frame_count >= self.ok_threshold:
                self.current_status = "OK"
        else:
            self.wait_frame_count += 1
            self.ok_frame_count = 0  # Reset OK counter
            
            # Show Wait status after threshold frames
            if self.wait_frame_count >= self.wait_threshold:
                self.current_status = "Wait"
        
        # Update display with current stable status
        is_ok = self.current_status == "OK"
        self.video_display.set_status(self.current_status, is_ok)
        
        # Update FPS display
        self.video_display.set_fps(self.fps)
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen_mode = not self.fullscreen_mode
        
        if self.fullscreen_mode:
            self.showFullScreen()
            self.fullscreen_btn.setText("Fullscreen: ON")
        else:
            self.showNormal()
            self.setWindowState(Qt.WindowMaximized)
            self.fullscreen_btn.setText("Fullscreen: OFF")
    
    def update_threshold(self, value):
        """Update distance threshold"""
        self.distance_threshold = value
        # Update offset lines
        self.video_display.update_offset_lines(value)
    
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
            'camera_id': self.camera_combo.currentData(),
            'fullscreen_mode': self.fullscreen_mode
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
                    self.fullscreen_mode = config.get('fullscreen_mode', False)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def closeEvent(self, event):
        """Cleanup on close"""
        if self.camera_worker is not None:
            self.camera_worker.stop()
            self.camera_worker.wait()
        
        if self.detection_worker is not None:
            self.detection_worker.stop()
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = TriangleDetectorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
