import sys
import cv2
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                              QHBoxLayout, QComboBox, QFrame)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, QThread, Signal

class CameraWorker(QThread):
    frame_ready = Signal(object)  # tuple: (frame, fps)
    error_signal = Signal(str)
    
    def __init__(self, camera_id=0):
        super().__init__()
        self.running = True
        self.cap = None
        self.camera_id = camera_id
        
    def run(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if not self.cap.isOpened():
                self.error_signal.emit(f"Failed to open camera {self.camera_id}")
                return
            
            # FPS tracking
            frame_times = []
            
            while self.running:
                ret, frame = self.cap.read()
                if ret:
                    current_time = time.time()
                    frame_times.append(current_time)
                    
                    # Keep only last 30 frames for FPS calculation
                    if len(frame_times) > 30:
                        frame_times.pop(0)
                    
                    # Calculate actual FPS
                    if len(frame_times) > 1:
                        fps = len(frame_times) / (frame_times[-1] - frame_times[0])
                    else:
                        fps = 0
                    
                    self.frame_ready.emit((frame, fps))
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


class CameraTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Test - FPS Monitor")
        self.setGeometry(100, 100, 800, 600)
        
        self.camera_worker = None
        self.init_ui()
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
        camera_layout.addStretch()
        
        main_layout.addLayout(camera_layout)
        
        # Video display
        self.video_label = QLabel(self)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setMaximumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setAlignment(Qt.AlignCenter)
        
        video_container = QHBoxLayout()
        video_container.addStretch()
        video_container.addWidget(self.video_label)
        video_container.addStretch()
        main_layout.addLayout(video_container)
        
        # FPS label (overlay on video)
        self.fps_label = QLabel(self)
        self.fps_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 180); color: #00FF00; font-weight: bold; "
            "font-size: 16px; padding: 8px 12px; border-radius: 3px; font-family: 'Courier';"
        )
        self.fps_label.setText("FPS: 0.0")
        self.fps_label.setAlignment(Qt.AlignCenter)
        
        # Info panel
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("Real-time FPS from Camera:"))
        info_layout.addWidget(self.fps_label)
        info_layout.addStretch()
        
        main_layout.addLayout(info_layout)
        
        self.setLayout(main_layout)
    
    def start_camera(self, camera_id):
        """Start camera worker"""
        if self.camera_worker is not None:
            self.camera_worker.stop()
            self.camera_worker.wait()
        
        self.camera_worker = CameraWorker(camera_id)
        self.camera_worker.frame_ready.connect(self.display_frame)
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
    
    def display_frame(self, data):
        """Display frame with FPS"""
        frame, fps = data
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = 3 * w
        
        # Create QImage
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # Display
        self.video_label.setPixmap(pixmap)
        
        # Update FPS label
        self.fps_label.setText(f"FPS: {fps:.1f}")
    
    def closeEvent(self, event):
        """Cleanup on close"""
        if self.camera_worker is not None:
            self.camera_worker.stop()
            self.camera_worker.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = CameraTestApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
