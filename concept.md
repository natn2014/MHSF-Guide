# Triangle Detection from USB Camera Stream - Concept Document

## Project Overview
- **Input**: USB camera stream at 720p 30fps
- **Output**: Triangle detection at 10 fps
- **Target**: Low profile, low cost embedded device

---

## 1. Device Selection: Raspberry Pi

### Platform Comparison

| Aspect | Raspberry Pi 4 (8GB) | Raspberry Pi 5 |
|--------|---------------------|-----------------|
| **Cost** | ~$75-90 | ~$120-150 |
| **CPU** | ARM Cortex-A72 (4-core, 1.5GHz) | ARM Cortex-A76 (4-core, 2.4GHz) |
| **GPU** | VideoCore VI | VideoCore VII |
| **RAM** | 8GB | 8GB/4GB options |
| **Performance** | ~2x slower than Pi5 | ~2.5x faster than Pi4 |
| **Power Consumption** | ~3-6W | ~5-8W |
| **Thermal Profile** | Low (no heatsink needed) | Low (minimal cooling) |
| **Video Decode (HW)** | H.264, H.265 (1080p 30fps) | H.264, H.265 (4K 60fps) |

### Recommendation
- **Budget Priority**: Raspberry Pi 4 (8GB)
- **Performance Priority**: Raspberry Pi 5
- **Sweet Spot**: Pi 4 with careful optimization (sufficient for 10 fps triangle detection)

---

## 2. Device Tree & Boot Configuration

### Raspberry Pi 4 Device Tree
```
Location: /boot/firmware/bcm2711-rpi-4-b.dtb (compiled)
Source: /boot/firmware/overlays/
Key elements for USB camera:
- USB ports configuration
- Camera CSI/USB interface routing
- Memory allocation for video buffering
```

### Critical Settings for Video Processing
```
gpu_mem=256          # GPU memory allocation (128-256MB for video)
gpu_freq=500         # GPU frequency (helps with processing)
arm_freq=1800        # CPU frequency boost
```

### USB Camera Configuration
```
Device: /dev/video0 (typically first USB camera)
Resolution: 720p (1280x720)
Frame Rate: 30fps input, 10fps processing
Format: YUYV or MJPEG
```

---

## 3. Design Concept: Triangle Detection System

### Architecture Overview
```
USB Camera (720p 30fps)
         ↓
   Frame Capture (OpenCV)
         ↓
   Frame Buffer (skip 2 out of 3 for 10fps)
         ↓
   Image Preprocessing
         ↓
   Triangle Detection Module
         ↓
   Results Output
```

### Processing Pipeline

#### 3.1 Frame Capture & Buffering
- Capture at 30fps from USB device
- Store in circular buffer (3-5 frames)
- Process every 3rd frame (10 fps detection)
- Prevents USB bottleneck

#### 3.2 Image Preprocessing
- **Resize**: 1280x720 → 640x360 (faster processing)
- **Color Space**: Convert YUYV → BGR (OpenCV format)
- **Gaussian Blur**: Reduce noise (kernel 5x5)
- **Grayscale**: Convert to single channel
- **Threshold**: Binary threshold for edge detection

#### 3.3 Triangle Detection Methods

##### **Option A: Contour Analysis (Recommended for Pi4)**
- Canny edge detection
- Find contours in image
- Approximate contours to polygons
- Filter by vertex count (3 vertices = triangle)
- Validate: Check area, aspect ratio, hull

```
Pros: CPU-efficient, real-time capable, no ML model needed
Cons: Sensitive to lighting, background clutter
```

##### **Option B: TensorFlow Lite Object Detection**
- Pre-trained COCO model (objects include triangles/shapes)
- Run inference at 10 fps
- Post-process detections

```
Pros: Robust to variations, handles complex backgrounds
Cons: Higher CPU usage, needs ML libraries
```

##### **Option C: Hybrid Approach**
- Contour pre-filtering (fast, eliminates noise)
- ML model confirmation (high accuracy)
- Best of both worlds

---

## 4. Required Modules & Libraries

### Core Libraries
```
OpenCV 4.x           # Computer vision & contour detection
NumPy                # Array operations
TensorFlow Lite      # (Optional) ML inference
```

### System Dependencies
```
libatlas-base-dev    # Linear algebra library
libjasper-dev        # Image compression
libtiff5             # TIFF image support
libjasper-dev        # JPEG support
libharfbuzz0b        # Text rendering
libwebp6             # WebP codec
```

### Installation Command
```bash
# Install build tools
sudo apt-get update
sudo apt-get install -y build-essential cmake

# Install OpenCV dependencies
sudo apt-get install -y python3-opencv

# Install ML frameworks (if using TensorFlow)
pip install tensorflow-lite
pip install numpy
```

---

## 5. Implementation Strategy

### Phase 1: Setup & Capture
1. Configure Raspberry Pi 4/5 environment
2. Install OpenCV and dependencies
3. Test USB camera frame capture
4. Implement frame buffering (30fps input → 10fps processing)

### Phase 2: Triangle Detection
1. Implement contour-based detection (OpenCV)
2. Add preprocessing pipeline
3. Tune parameters (threshold values, contour filtering)
4. Test detection accuracy

### Phase 3: Optimization
1. Profile code execution time
2. Resize frames if needed
3. Implement multi-threading for capture/detection
4. Cache processing results

### Phase 4: Deployment
1. Package as service/daemon
2. Add logging & monitoring
3. Test under various lighting conditions
4. Document final hardware requirements

---

## 6. Performance Expectations

### Raspberry Pi 4 Timeline
- Frame capture: ~2ms (30fps)
- Preprocessing (640x360): ~15-20ms
- Triangle detection (contour): ~30-50ms
- **Total per frame**: 50-70ms
- **Achievable FPS**: 14-20 fps (easily meets 10fps target)

### Bottlenecks & Solutions
| Bottleneck | Solution |
|-----------|----------|
| USB bandwidth | Use USB 3.0 camera if available; reduce resolution |
| CPU usage | Downscale images; use GPU acceleration |
| Memory | Limit buffer size; use frame compression |
| Thermal | Add heatsink; reduce gpu_freq if throttling |

---

## 7. GPIO & Camera Interface Reference

### USB Ports (Pi4)
- 4x USB 3.0 (faster, right side)
- 4x USB 2.0 (left side)
- **Recommendation**: Connect camera to USB 3.0 port

### Camera CSI Connector
- Alternative to USB: Official Pi Camera Module (not applicable here - USB camera specified)

### Power Requirements
- Standalone operation: 5V 3A USB-C power supply
- Total system draw: ~5-8W (Pi4 + camera + USB hub)

---

## 8. File Structure & Code Organization

```
project/
├── config/
│   ├── camera_config.json      # Camera parameters
│   └── detection_params.json   # Detection tuning
├── src/
│   ├── camera_capture.py       # USB camera stream handler
│   ├── triangle_detector.py    # Detection logic
│   ├── preprocessing.py        # Image preprocessing
│   └── main.py                 # Main execution loop
├── models/
│   └── (TensorFlow Lite models if used)
├── tests/
│   └── test_detection.py
└── README.md
```

---

## 9. Next Steps

1. **Confirm device choice** (Pi4 or Pi5?)
2. **Procure hardware** + USB camera
3. **Start Phase 1**: Setup & capture testing
4. **Iterate on detection algorithm**
5. **Optimize & deploy**

---

## References & Resources

- [Raspberry Pi Official Documentation](https://www.raspberrypi.com/documentation/)
- [OpenCV Python Documentation](https://docs.opencv.org/4.x/)
- [TensorFlow Lite Model Conversion](https://www.tensorflow.org/lite/guide/get_started)
- GPIO/Device Tree: `/boot/firmware/overlays/README` (on Pi)

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-31  
**Status**: Draft - Concept Phase
