# MHSF Triangle Detector

Professional real-time triangle detection application using USB camera with **angle validation**, GUI feedback system, and **optimized background processing** for Raspberry Pi 5.

## 🎯 Project Overview

MHSF Triangle Detector is a computer vision application designed for **precision triangle detection and positioning** in manufacturing, assembly, and quality control environments. The app captures USB camera streams, detects triangles with angle constraints, evaluates positioning accuracy, and provides visual status feedback.

**Perfect for:**
- Assembly line triangle component detection
- Quality control positioning verification  
- Manufacturing equipment calibration
- Educational computer vision projects

## ✨ Key Features

### 🔍 **Advanced Triangle Detection**
- **Angle Constraints**: Detects only triangles where ALL angles are 50-70° (equilateral/near-equilateral)
- **Real-time Processing**: 30 FPS camera capture with background detection thread
- **Multi-shape Support**: Detects perfect triangles (3 vertices) and rounded-corner triangles (4-5 vertices)
- **Area Filtering**: Adjustable minimum area threshold (1-5000 px²) to ignore small noise

### 📊 **Visual Feedback System**
- **Center Reference Lines**: Green center line + yellow threshold boundaries
- **Detection Visualization**: Blue contours around detected triangles, red center points (centroids)
- **Dual Status Indicators**:
  - **OK (Green)**: Triangle within distance threshold for 2+ consecutive frames
  - **Wait (Red)**: Triangle outside threshold or no detection for 10+ frames
- **Real-time FPS Display**: Shows actual processing frame rate

### 🎯 **Positioning Alignment**
- **Distance Threshold**: Configurable 10-300 pixel range from screen center
- **Hysteresis Logic**: Prevents flickering between OK/Wait states with frame counting
- **Visual Zone Markers**: Yellow lines show acceptance zone boundaries

### ⚙️ **Configurable Controls**
- **Distance Threshold**: How close triangle must be to center line (pixels)
- **Min Triangle Area**: Filter small noise contours
- **Angle Range**: Predefined 50-70° (customizable in code)
- All settings saved to `triangle_config.json` automatically

### 📷 **Multi-Camera Support**
- Auto-detect USB cameras (supports 1-10 cameras)
- Live camera switching via dropdown menu
- No restart required for camera changes

### 🖥️ **Display Options**
- Windowed mode (default)
- Fullscreen mode (toggle via button)
- Maximized window option
- Ideal for kiosk/production displays

### 🎬 **Performance Optimized**
- **Background Detection Thread**: Camera frames display at full 30 FPS while detection runs in background
- **Non-blocking UI**: Never freezes during heavy processing
- **Max FPS Capped**: 60 FPS max per frame limit configuration
- **Smooth Real-time Operation**: Perfect for live monitoring

## 🏗️ System Architecture

```
Camera Input (30 FPS)
        ↓
▁▁▁▁▁▁▁▁▁▁▁▁▁▁ Main UI Thread
│ Frame Display  │ Status Update
│ Status Update  │ FPS Display
│ Camera Control │
▔▔▔▔▔▔▔▔▔▔▔▔▔▔
        ↓ (via signal)
    Detection Results
        ↑
▁▁▁▁▁▁▁▁▁▁▁▁▁▁ Background Detection Thread
│ Grayscale Conv │
│ Edge Detection │
│ Contour Find   │
│ Angle Calc     │
│ Validate Tri   │
▔▔▔▔▔▔▔▔▔▔▔▔▔▔
```

## 💻 System Requirements

### Minimum
- **Python**: 3.8+
- **RAM**: 512MB
- **Storage**: 100MB free
- **Camera**: USB webcam or compatible camera

### Recommended for Pi5 Auto-Start
- **Raspberry Pi 5** (8GB)
- **Raspberry Pi OS** (Bookworm)
- **Display**: HDMI connected
- **Internet**: For package installation

## 📦 Dependencies

- **PySide6**: Qt6 GUI framework
- **OpenCV (cv2)**: Computer vision & image processing
- **NumPy**: Numeric computations
- **Python 3.8+** standard libraries (json, time, threading, etc.)

## 📂 Project Structure

```
MHSF_Guide/
├── triangle_detector_app_CV.py    # Main application
├── setup.sh                        # Automated installation script
├── run_detector.sh                 # Quick run wrapper
├── triangle_config.json            # User settings (auto-created)
├── triangle-detector.service       # Systemd service file
├── README.md                        # This file
├── INSTALL_INSTRUCTIONS.md         # Installation guide
└── concept.md                       # Technical documentation
```

## 🚀 Quick Start

### Windows/Mac/Linux Desktop
```bash
python3 triangle_detector_app_CV.py
```

### Raspberry Pi (with auto-start on boot)
```bash
sudo bash setup.sh
```

See [INSTALL_INSTRUCTIONS.md](INSTALL_INSTRUCTIONS.md) for detailed setup.

## ⚙️ Configuration

Edit `triangle_config.json` or use GUI controls:

```json
{
    "distance_threshold": 15,      // pixels from center line
    "min_triangle_area": 10,        // minimum area in pixels²
    "resolution": [320, 480],       // camera capture size
    "camera_id": 0,                 // default camera (0=first)
    "fullscreen_mode": false        // gui startup mode
}
```

## 🎮 Controls

| Button/Key | Function |
|-----------|----------|
| **Distance Threshold Slider** | Adjust acceptance zone (10-300px) |
| **Min Area Spinner** | Filter small noise (1-5000px²) |
| **Camera Dropdown** | Switch active camera |
| **Save Config** | Persist settings to JSON |
| **Fullscreen Toggle** | Switch display mode |
| **ESC** | Exit fullscreen mode |

## 📊 Output Information

### Visual Elements
- **Green Line**: Vertical screen center reference
- **Yellow Lines**: Left/right distance threshold boundaries  
- **Blue Contours**: Detected triangle outlines
- **Red Circles**: Triangle centroids (center points)
- **Status Box** (top-right): OK/Wait indicator
- **FPS Counter** (top-right): Real-time frame rate

### Configuration File Output
- Location: `triangle_config.json`
- Auto-saved when "Save Config" clicked
- Auto-loaded on application startup
- Includes camera, thresholds, and display preferences

## 🔧 Troubleshooting

### No Camera Detected
- Check USB camera is connected
- Try different USB ports
- Run: `ls /dev/video*` (Linux) or check Device Manager (Windows)
- Verify camera permissions

### GUI Not Displaying (Headless)
- Configure X11 forwarding: `ssh -X user@pi`
- Or set `QT_QPA_PLATFORM=offscreen` for background mode

### Low FPS (<20)
- Reduce minimum area threshold
- Increase Canny edge detection thresholds (code modification)
- Close other applications

### Service Won't Auto-Start
- Check status: `systemctl status triangle-detector`
- View logs: `journalctl -u triangle-detector -f`
- Verify DISPLAY=:0 is available
- Ensure run with `sudo bash setup.sh`

## 📖 Advanced Usage

### Custom Angle Range
Edit in `triangle_detector_app_CV.py`:
```python
self.min_angle = 50  # Minimum angle in degrees
self.max_angle = 70  # Maximum angle in degrees
```

### Adjust Edge Detection
```python
self.threshold1 = 80   # Lower threshold (was 50)
self.threshold2 = 200  # Upper threshold (was 150)
```

### Enable Verbose Logging
Run with verbose output:
```bash
python3 triangle_detector_app_CV.py --debug
```

## 🔄 Version History

**v1.0** (Current)
- ✅ Real-time triangle detection with angle constraints
- ✅ Background detection thread for smooth 30 FPS display
- ✅ Raspberry Pi 5 auto-start on reboot
- ✅ Multi-camera support
- ✅ Hysteresis-based status indication
- ✅ Full configuration persistence

## 📝 License

[Specify your license here]

## 👥 Authors

- **Development**: MHSF Project Team
- **Computer Vision**: OpenCV implementation
- **GUI**: PySide6 framework
- **Platform**: Raspberry Pi 5 optimized

## 🤝 Contributing

Bug reports and feature requests welcome!

## 📞 Support

For issues or questions, consult:
1. [INSTALL_INSTRUCTIONS.md](INSTALL_INSTRUCTIONS.md) - Setup help
2. [concept.md](concept.md) - Technical details
3. Application logs: `journalctl -u triangle-detector -f`

---

**Status**: ✅ Production Ready | **Last Updated**: April 2026

### 2. Install Dependencies
```bash
pip install PySide6 opencv-python numpy
```

### 3. Run Application
```bash
python triangle_detector_app_CV.py
```

## Usage Guide

### Launch Application
```bash
python triangle_detector_app_CV.py
```

The app launches in fullscreen with all controls centered.

### Controls & Settings

#### Camera Selection
- **"Select Camera"** dropdown
- Choose from detected USB cameras
- Changes take effect immediately

#### Detection Parameters
- **Distance Threshold (px)**: 
  - Default: 15 pixels
  - Lower = stricter positioning requirement
  - Range: 10-300

- **Min Area (px²)**:
  - Default: 10 pixels²
  - Lower = detect smaller triangles
  - Range: 1-5000
  - *Tip: Set to 50-100 for small triangles*

#### Save Config
- Click **"Save Config"** to persist settings
- Settings saved to `triangle_config.json`
- Automatically loaded on next launch

### Visual Interpretation

```
┌─────────────────────────────────────────┐
│  🟢 Select Camera: Camera 0      ✓      │
├─────────────────────────────────────────┤
│                                    [OK] │
│              ┃                          │
│      🔵────▲──── 🔴                   │
│      │    ╱ ╲    │    (Green line: center)
│      │   ╱   ╲   │    (Blue box: detection)
│      │  ╱     ╲  │    (Red dot: centroid)
│      └────────┘  │    ([OK]: within threshold)
│              ┃                          │
├─────────────────────────────────────────┤
│ Distance: 15px  Min Area: 10px²  [Save]│
└─────────────────────────────────────────┘
```

## Configuration

### triangle_config.json

Auto-generated on first save. Example:
```json
{
    "distance_threshold": 15,
    "min_triangle_area": 10,
    "resolution": [320, 480],
    "camera_id": 0
}
```

Edit manually to change defaults before launching app.

## Detection Optimization

### For Small Triangles
- Lower **Min Area** to 5-20
- Ensure good lighting
- Keep camera steady

### For Large Triangles Only
- Raise **Min Area** to 500-2000
- Filters out noise and small objects

### For Strict Positioning
- Lower **Distance Threshold** to 10-20
- Triangle must be very close to center line

### For Relaxed Positioning
- Raise **Distance Threshold** to 100-200
- Wide tolerance around center

## Files Description

| File | Purpose |
|------|---------|
| `triangle_detector_app_CV.py` | Main OpenCV-based detection app |
| `triangle_detector_app_YOLO.py` | YOLO8world deep learning variant |
| `triangle_config.json` | Saved user settings (auto-created) |
| `README.md` | This file |
| `concept.md` | Design documentation |

## Architecture

### Class Structure

**VideoDisplayWidget**
- Container for video display
- Manages overlay elements (center line, status label)
- Updates UI in real-time

**CameraWorker**
- Separate thread for camera capture
- Prevents UI freezing during video processing
- Handles camera open/close/switch

**TriangleDetector**
- Core detection logic
- Uses Canny edge detection + contour analysis
- Configurable thresholds and minimum area

**TriangleDetectorApp**
- Main application window
- Coordinates UI, camera, detection
- Manages configuration and save/load

### Processing Pipeline

```
USB Camera (30fps)
    ↓
Frame Capture (CameraWorker)
    ↓
Triangle Detection (TriangleDetector)
    ├─ Grayscale conversion
    ├─ Gaussian blur (noise reduction)
    ├─ Canny edge detection
    ├─ Contour finding
    └─ Polygon approximation (3 vertices?)
    ↓
Distance Measurement
    ├─ Find triangle centroid
    ├─ Calculate distance to center line
    └─ Compare with threshold
    ↓
Status Update & Rendering
    ├─ Draw detections on frame
    ├─ Update status label
    └─ Display at 30fps

```

## Troubleshooting

### Camera Not Detected
- Check USB connection
- Try different USB port
- Verify camera works in other applications (Zoom, Skype)
- Run: `python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"`

### No Triangles Detected
- **Lighting**: Ensure good lighting on triangle
- **Contrast**: Triangle should have clear edge definition
- **Min Area too high**: Lower the slider to 1-5
- **Camera angle**: Position triangle perpendicular to camera
- **Triangle definition**: Shape must have 3 clear vertices

### Detection is Delayed
- Standard behavior with fullscreen mode
- First frame always shows from previous frame
- Latency ~33ms per frame (30fps)

### App Crashes on Startup
- Verify camera is accessible: `cv2.VideoCapture(0).isOpened()`
- Check Python version: `python --version` (3.8+ required)
- Reinstall dependencies: `pip install --upgrade PySide6 opencv-python`

### Status Always Shows "Wait"
- Increase **Distance Threshold** value
- Verify triangle is actually being detected (watch for blue box)
- Move triangle closer to center line

## Performance Notes

### CPU Usage
- CPU: ~15-25% (single core) on modern systems
- GPU: Not used (OpenCV CPU-based)
- Memory: ~100-150 MB

### Raspberry Pi 5 Compatibility
✅ **Supported** - runs at 20+ fps
- Adjust resolution or Min Area for slower devices

### Optimization Tips
- Reduce min area if missing small triangles
- Increase blur kernel size (default 5x5) for noisy cameras
- Lower Canny thresholds (50, 150) for edge-heavy scenes

## Examples & Use Cases

### Assembly Line Positioning
- Set **Distance Threshold**: 20-30 (strict alignment)
- Set **Min Area**: 100-200 (filter small defects)
- Monitor "OK" status for pass/fail

### Quality Inspection
- Set **Min Area**: 10 (detect all triangular marks)
- Count detections in status bar
- Verify correct number and position

### Calibration & Testing
- Set **Min Area**: 1 (maximum sensitivity)
- Set **Distance Threshold**: 300 (very relaxed)
- Capture all possible triangles for analysis

## Development & Extension

### Adding Custom Detection
Edit `TriangleDetector.detect_triangles()`:
```python
# Add additional filter: aspect ratio
if len(approx) == 3 and area > self.min_area:
    # Calculate bounding rectangle
    x, y, w, h = cv2.boundingRect(approx)
    aspect_ratio = float(w) / h
    
    # Only keep near-equilateral triangles
    if 0.7 < aspect_ratio < 1.3:
        # ... rest of code
```

### Custom Config
Edit `triangle_config.json` before running:
```json
{
    "distance_threshold": 25,
    "min_triangle_area": 50,
    "camera_id": 1
}
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-01 | Initial release with OpenCV detection |
| 1.1 | 2026-04-01 | Added adjustable min area threshold |
| 1.2 | 2026-04-01 | Added fullscreen mode |

## License

Open source - Free to use and modify

## Support

For issues or questions:
1. Check **Troubleshooting** section above
2. Verify all dependencies: `pip list | grep -E "PySide6|opencv|numpy"`
3. Test with sample video or different camera

## Credits

- **PySide6**: Qt framework for Python
- **OpenCV**: Computer vision library
- **NumPy**: Numerical computing
- **YOLO**: Optional deep learning backend

---

**Quick Start:**
```bash
pip install PySide6 opencv-python numpy
python triangle_detector_app_CV.py
```

Press **ESC** to exit fullscreen.
