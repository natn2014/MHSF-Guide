# MHSF Triangle Detector

Real-time triangle detection application using USB camera stream with PySide6 GUI and OpenCV computer vision.

## Features

✅ **Real-time Triangle Detection**
- Detects triangles from USB camera stream (320x480 @ 30fps)
- Uses OpenCV contour analysis for efficient detection
- Adjustable minimum area threshold to detect small/large triangles

✅ **Visual Feedback**
- Green vertical center line reference
- Blue bounding boxes around detected triangles
- Red center points marking triangle centroids
- Status indicator ("OK" / "Wait") at top-right corner

✅ **Positioning Alignment**
- Measures horizontal distance from triangle center to screen center
- Shows "OK" (green) when within distance threshold
- Shows "Wait" (red) when outside threshold
- Useful for assembly line or positioning applications

✅ **Configurable Parameters**
- **Distance Threshold**: 10-300 pixels (how close to center)
- **Minimum Area**: 1-5000 pixels² (triangle size filter)
- All settings persist in `triangle_config.json`

✅ **Multi-Camera Support**
- Auto-detect available USB cameras
- Switch between cameras via dropdown menu
- Hot-swap camera without restarting

✅ **Fullscreen Mode**
- Launches in fullscreen for kiosk/production use
- Press ESC to exit fullscreen

## System Requirements

- **Python**: 3.8+
- **OS**: Windows, macOS, Linux
- **Camera**: USB webcam or compatible camera
- **Display**: Any resolution (scaled automatically)

## Installation

### 1. Clone or Download Project
```bash
cd d:\Dev_AI_env\MHSF_Guide
```

### 2. Install Dependencies
```bash
pip install PySide6 opencv-python numpy
```

### 3. Run Application

**OpenCV-based version (recommended for edge devices):**
```bash
python triangle_detector_app_CV.py
```

**YOLO-based version (higher accuracy, requires more resources):**
```bash
pip install ultralytics
python triangle_detector_app_YOLO.py
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
- YOLO version requires more resources

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

### Switching to YOLO
Use `triangle_detector_app_YOLO.py` - same UI, different backend

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
