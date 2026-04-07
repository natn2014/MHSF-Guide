# MHSF Triangle Detector - Installation Guide

Complete installation and setup guide for desktop systems and Raspberry Pi 5 with **auto-start on reboot configuration**.

---

## 🚀 Quick Start (5 minutes)

### For Windows/Mac/Linux Desktop
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (no PEP 668 issues!)
pip install PySide6 opencv-python numpy

# Run application
python3 triangle_detector_app_CV.py
```

### For Raspberry Pi 5 (with auto-start)
```bash
cd ~/MHSF_Guide
sudo bash setup.sh
```

Then reboot: `sudo reboot`

The app will start automatically when Pi boots.

---

## 💻 Detailed Installation

### Prerequisites

#### For Desktop (Windows/Mac/Linux)
- Python 3.8 or higher
- pip package manager
- USB camera
- Terminal/Command prompt access

#### For Raspberry Pi 5
- Raspberry Pi 5 (recommended 8GB RAM)
- Raspberry Pi OS (Bookworm or newer)
- USB camera connected
- HDMI monitor/display connected
- Internet connection
- microSD card with at least 4GB free space

### Step 0: Verify Python Installation

```bash
python3 --version
# Should show Python 3.8 or higher
```

If Python not installed:
- **Windows**: Download from [python.org](https://www.python.org)
- **macOS**: `brew install python3`
- **Linux**: `sudo apt-get install python3 python3-pip`
- **Raspberry Pi**: Already included with Raspberry Pi OS

---

## 📦 Installation Methods

### Method 1: Automated Setup (Recommended for Pi5)

This fully automated script handles all dependencies and systemd configuration.

#### 1a. Download Project
```bash
cd ~
git clone <your-repo-url> MHSF_Guide
cd MHSF_Guide
```

Or if already downloaded:
```bash
cd ~/MHSF_Guide
```

#### 1b. Run Setup Script

**Without Auto-Start (Desktop):**
```bash
bash setup.sh
```

**With Auto-Start on Reboot (Raspberry Pi 5):**
```bash
sudo bash setup.sh
```

**What the script does:**
- ✅ Step [1/6]: Verifies Python 3 installation
- ✅ Step [2/6]: **Installs build tools** (build-essential, python3-dev, cmake, clang) + system libraries for Pi5
- ✅ Step [3/6]: **Creates isolated Python venv** with `--system-site-packages` (allows system PySide2 access)
- ✅ Step [3b/6]: **Installs python3-pyside2 from Raspbian repository** (no compilation, instant install)
- ✅ Step [4/6]: Updates pip with setuptools & wheel in venv
- ✅ Step [5/6]: **Installs only opencv-python and numpy** in venv (PySide2 from system package)
- ✅ Step [6/6]: Creates systemd service file for auto-start using venv Python
- ✅ Step [7/7]: Creates convenient run wrapper script with venv activation

⏱️ **Installation Time**: ~5-8 minutes total (system PySide2 is instant, no compilation!)

**Why System PySide2 Package:**
- ✅ Official Raspbian package (python3-pyside2)
- ✅ Pre-built and optimized for Pi5 ARM64
- ✅ Zero installation time (already in repository)
- ✅ System package manager handles updates
- ✅ Best stability and compatibility

**Expected output:**
```
================================
MHSF Triangle Detector - Setup
Pi5 Edition with Auto-Start
================================
[1/6] Checking Python installation...
✓ Found: Python 3.11.x
[2/6] Installing system dependencies for Pi5...
     Installing Qt libraries, OpenGL support, build tools, and Python dev...
✓ System dependencies installed
[3/6] Creating Python virtual environment...
✓ Virtual environment created at: /home/pi/MHSF_Guide/.venv
  (with system site-packages enabled for PySide2)
[3b/6] Installing python3-pyside2 from system repository...
✓ System python3-pyside2 installed
[4/6] Updating pip in virtual environment...
✓ pip updated
[5/6] Installing remaining Python dependencies...
     Installing: opencv-python, numpy
     (PySide2 provided by system package, installation takes ~30-60 seconds)
✓ Python dependencies installed successfully
  - OpenCV: installed via pip
  - NumPy: installed via pip
  - PySide2: provided by system package (python3-pyside2)
[6/6] Creating systemd service for auto-start...
✓ Systemd service created: /etc/systemd/system/triangle-detector.service
✓ Service enabled for auto-start on reboot
[7/7] Creating run wrapper script...
✓ Wrapper script created: /home/pi/MHSF_Guide/run_detector.sh

================================
Setup Complete!
================================
Virtual Environment: /home/pi/MHSF_Guide/.venv
Dependencies: OpenCV + NumPy via pip, PySide2 from system package

3. Systemd Service (auto-start on reboot):
   Status:  sudo systemctl status triangle-detector
   Start:   sudo systemctl start triangle-detector
   Stop:    sudo systemctl stop triangle-detector
   Restart: sudo systemctl restart triangle-detector

Logs:
   Real-time: sudo journalctl -u triangle-detector -f
   Recent:    sudo journalctl -u triangle-detector -n 50
```

#### 1c. Test Installation

Test the service immediately (without reboot):
```bash
sudo systemctl start triangle-detector

# In another terminal, check logs:
journalctl -u triangle-detector -f

# You should see the app launching
```

Stop for testing:
```bash
sudo systemctl stop triangle-detector
```

#### 1d. Verify Auto-Start on Reboot
```bash
sudo reboot
# App will start automatically after boot
```

---

### Method 2: Manual Installation (Desktop)

For desktop systems that don't need auto-start:

#### 2a. Create Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2b. Install Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install PySide6 opencv-python numpy
```

#### 2c. Run Application
```bash
python3 triangle_detector_app_CV.py
```

---

### Method 3: Manual Systemd Setup (If Auto-Script Failed)

If `setup.sh` with sudo encountered issues:

#### 3a. Install Dependencies Manually
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-dev \
    libgl1-mesa-glx libxkbcommon-x11-0 libdbus-1-3 \
    libfontconfig1 libfreetype6 libx11-6 libxcb1 \
    libwayland-client0

python3 -m pip install --upgrade pip
python3 -m pip install PySide6 opencv-python numpy
```

#### 3b. Create Service File Manually
```bash
sudo nano /etc/systemd/system/triangle-detector.service
```

Paste:
```ini
[Unit]
Description=MHSF Triangle Detector Application
After=network-online.target display-manager.service
Wants=display-manager.service

[Service]
Type=simple
User=pi
Group=pi
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/pi/.Xauthority"
Environment="QT_QPA_PLATFORM=xcb"
Environment="QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/python3/dist-packages/PySide6/Qt/plugins"
Environment="LD_LIBRARY_PATH=/usr/lib/python3/dist-packages/PySide6/Qt/lib:/usr/lib/arm-linux-gnueabihf:/usr/local/lib:$LD_LIBRARY_PATH"
Environment="HOME=/home/pi"
WorkingDirectory=/home/pi/MHSF_Guide
ExecStartPre=/bin/sleep 3
ExecStart=/usr/bin/python3 /home/pi/MHSF_Guide/triangle_detector_app_CV.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=triangle-detector

[Install]
WantedBy=graphical.target
```

Press `Ctrl+O`, `Enter`, `Ctrl+X` to save.

#### 3c. Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable triangle-detector.service
sudo systemctl start triangle-detector.service
```

---

## ▶️ Running the Application

### Option 1: Direct Python (Desktop & Pi)
```bash
python3 triangle_detector_app_CV.py
```

### Option 2: Using Wrapper Script (Desktop & Pi)
```bash
bash run_detector.sh
```

### Option 3: Systemd Service (Pi5 Only)

**Start:**
```bash
sudo systemctl start triangle-detector
```

**Stop:**
```bash
sudo systemctl stop triangle-detector
```

**Check Status:**
```bash
sudo systemctl status triangle-detector
```

**View Real-Time Logs:**
```bash
journalctl -u triangle-detector -f
```

**View Recent Logs:**
```bash
journalctl -u triangle-detector -n 50
```

**Restart:**
```bash
sudo systemctl restart triangle-detector
```

### Option 4: Enable/Disable Auto-Start

**Enable (auto-start on reboot):**
```bash
sudo systemctl enable triangle-detector.service
```

**Disable (don't auto-start):**
```bash
sudo systemctl disable triangle-detector.service
```

**Current Status:**
```bash
systemctl is-enabled triangle-detector.service
# Returns: enabled or disabled
```

---

## ⚙️ System Requirements Recap

### Disk Space
- Raspberry Pi OS: ~3GB
- Dependencies: ~500MB
- MHSF Guide project: ~20MB
- **Total: 4GB minimum** recommended

### RAM
- Minimum: 512MB (app only uses ~100-200MB)
- Recommended: 2GB+ for smooth operation
- Pi5 8GB: Overkill but recommended for reliability

### Network
- Internet needed only during installation for packages
- Can run offline after dependencies installed

---

## 🔧 Configuration

### First Time Launch

GUI defaults:
- Camera: Auto-detect first camera
- Resolution: 320x480
- Distance Threshold: 15 pixels
- Min Area: 10 pixels²
- Fullscreen: OFF

### Saving Custom Settings

1. Adjust sliders in GUI
2. Click "Save Config" button
3. Settings saved to `triangle_config.json`

Settings auto-load on restart.

### Edit Configuration Directly

Edit `triangle_config.json`:
```json
{
    "distance_threshold": 15,
    "min_triangle_area": 10,
    "resolution": [320, 480],
    "camera_id": 0,
    "fullscreen_mode": false
}
```

---

## 🐛 Troubleshooting

### Issue: PEP 668 - externally-managed-environment Error

**Error message:**
```
error: externally-managed-environment

× This environment is externally managed
```

**Root cause:**
Modern versions of Raspberry Pi OS (and Debian) use PEP 668 to prevent system pip from conflicting with system package manager.

**Solution 1: Use Virtual Environment (Recommended)**
```bash
# Desktop/Manual setup
python3 -m venv venv
source venv/bin/activate  # or: source .venv/bin/activate
pip install PySide6 opencv-python numpy
```

**Solution 2: Automated Setup Script (for Pi5)**
```bash
cd ~/MHSF_Guide
sudo bash setup.sh
# Automatically creates and uses virtual environment!
```

The setup.sh script automatically:
- Creates a `.venv` directory
- Installs all packages in the isolated environment
- Configures systemd service to use venv Python
- Wraps run script to activate venv before execution

**Solution 3: System-Wide Installation (Not Recommended)**
If you absolutely need system-wide installation:
```bash
python3 -m pip install --break-system-packages PySide6 opencv-python numpy
```
⚠️ **Warning**: This bypasses PEP 668 safety checks and can cause conflicts with system updates.

---

### Issue: PySide Installation - Choosing Between PySide2 vs PySide6

**Which version for Raspberry Pi 5?**

| Criteria | PySide2 (System) | PySide2 (pip) | PySide6 |
|----------|------------------|---------------|---------|
| **Source** | Raspbian package | npm/pip wheels | pip wheels/source |
| **Installation** | ✅ System manager | Pre-built wheels | May compile |
| **Time** | ✅ Instant | 1-2 min | 5-10 min |
| **ARM64 Support** | ✅ Official | ✅ Yes | ⚠️ 6.6.x+ only |
| **Memory** | ✅ ~50MB | ~50MB | ⚠️ ~150MB |
| **System Updates** | ✅ Managed | Via pip | Manual |
| **Recommended** | ✅ YES | Alternative | Avoid on Pi5 |

**Setup Script Default: System python3-pyside2 (BEST CHOICE)**
- Uses Raspbian's official python3-pyside2 package
- Instant installation (no compilation)
- Automatically updated with system updates
- Perfect for Pi5 deployment

**How it works:**
1. Creates venv with `--system-site-packages`
2. Installs system `python3-pyside2` via apt-get
3. Installs opencv and numpy via pip in venv
4. Best of both worlds: official package + isolated environment

To manually install system PySide2:
```bash
sudo apt-get install python3-pyside2

# Then create venv with system-site-packages
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install opencv-python numpy
```

---

### Issue: PySide Installation - Manual Alternatives

**Alternative 1: PySide2 5.15.x from pip (if no system package)**
```bash
python3 -m venv venv
source venv/bin/activate
pip install 'PySide2>=5.15.0' opencv-python numpy
```

**Alternative 2: PySide6 (not recommended for Pi5)**
```bash
sudo apt-get install -y build-essential python3-dev cmake clang libclang-dev
python3 -m venv venv
source venv/bin/activate
pip install --default-timeout=1000 'PySide6>=6.6.0' opencv-python numpy
```

---

### Issue: PySide6 - "Could Not Find a Version That Satisfies the Requirement"

**Error message:**
```
ERROR: Could not find a version that satisfies the requirement PySide6
```

**Root cause:**
- PySide6 <6.6.x lacks ARM64 pre-built wheels (requires compilation)
- PySide6 requires build tools and more time on Pi5
- This is why **PySide2 is recommended** for Pi5

**Solution 1: Switch to PySide2 (Recommended)**
```bash
# PySide2 has pre-built ARM wheels for ALL versions
pip install 'PySide2>=5.15.0' opencv-python numpy
# Installation: ~1-2 minutes, no compilation!
```

**Solution 2: Use PySide6 with Extended Build Time**
```bash
# Install build dependencies first
sudo apt-get install -y build-essential python3-dev cmake clang libclang-dev

# Then install PySide6 6.6.x or newer
pip install --default-timeout=1000 'PySide6>=6.6.0' opencv-python numpy
# Installation: ~5-10 minutes with compilation
```

**Troubleshooting:**
- **"Could not find a version"**: Update pip: `pip install --upgrade pip`
- **Out of memory**: Use PySide2 (lighter) or add swap
- **Check what installed**: `python3 -c "import PySide2; print(PySide2.__version__ if 'PySide2' in dir() else 'Not installed')"`

---

### Issue: No Module Named PySide2

### Issue: No Camera Detected

**Check camera connection:**
```bash
# Linux/Pi
ls /dev/video*
v4l2-ctl --list-devices

# Windows
# Check Device Manager → Cameras

# macOS
# System Settings → Privacy & Security → Camera
```

**Test camera:**
```bash
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAILED')"
```

### Issue: GUI Not Displaying (Headless Pi)

**Enable X11 Forwarding:**
```bash
ssh -X user@raspberrypi.local
python3 triangle_detector_app_CV.py
```

**Or use Remote Desktop:**
- Enable VNC on Pi: `sudo raspi-config` → Interfacing Options → VNC
- Connect via VNC from another machine

### Issue: Service Won't Start

**Check logs:**
```bash
journalctl -u triangle-detector -f
```

**Common issues:**
- DISPLAY=:0 not available (display not connected)
- User `pi` doesn't exist (check username)
- Permissions issue (use `sudo`)

**Solution:**
```bash
# Ensure DISPLAY is set
echo $DISPLAY

# If empty, set manually:
export DISPLAY=:0
sudo systemctl restart triangle-detector
```

### Issue: Low FPS Performance

**Increase Canny thresholds** (edit `triangle_detector_app_CV.py`):
```python
self.threshold1 = 100  # was 80
self.threshold2 = 220  # was 200
```

**Reduce minimum area:**
Adjust "Min Area" slider to higher value via GUI

**Close background apps:**
```bash
killall firefox chromium gedit
```

### Issue: Permissions Denied on Service File

**Solution:**
```bash
sudo chown pi:pi /etc/systemd/system/triangle-detector.service
sudo chmod 644 /etc/systemd/system/triangle-detector.service
```

---

## 📊 Verification Checklist

After installation, verify each step:

- [ ] Python 3.8+ installed: `python3 --version`
- [ ] pip working: `pip --version`
- [ ] PySide6 installed: `python3 -c "import PySide6; print('OK')"`
- [ ] OpenCV installed: `python3 -c "import cv2; print('OK')"`
- [ ] NumPy installed: `python3 -c "import numpy; print('OK')"`
- [ ] Camera detected: `python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"`
- [ ] App launches: `python3 triangle_detector_app_CV.py`
- [ ] Service enabled (Pi): `systemctl is-enabled triangle-detector.service`
- [ ] Service starts (Pi): `sudo systemctl start triangle-detector`
- [ ] Logs available (Pi): `journalctl -u triangle-detector | head -5`

✅ All checked? **Installation complete!**

---

## 📞 Support Resources

| Issue | Resource |
|-------|----------|
| General questions | See README.md |
| Technical details | See concept.md |
| Configuration | Edit triangle_config.json or use GUI |
| Performance | Check logs: `journalctl -u triangle-detector -f` |
| Camera issues | Run test: `python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"` |

---

**Status**: ✅ Ready for Production | **Last Updated**: April 2026

---

## Auto-Boot Configuration

### Enable Auto-Start
```bash
sudo systemctl enable triangle-detector.service
sudo systemctl start triangle-detector.service
```

### Test Auto-Boot
```bash
sudo reboot
# App should start automatically after system boots
```

### Verify Auto-Boot is Active
```bash
sudo systemctl is-enabled triangle-detector.service
# Output: enabled
```

### View Startup Logs
```bash
journalctl -u triangle-detector -n 50  # Last 50 lines
journalctl -u triangle-detector -f      # Follow (real-time)
journalctl -u triangle-detector --since today
```

### Disable Auto-Boot
```bash
sudo systemctl disable triangle-detector.service
```

---

## Troubleshooting

### "Command not found: python3"
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
bash setup.sh
```

### "No module named 'PySide6'"
```bash
python3 -m pip install --upgrade PySide6
```

### "Cannot open camera"
```bash
# Check camera connection
ls /dev/video*
# Should show: /dev/video0 (or video1, etc.)

# Test with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
# Should print: True
```

### "Service failed to start"
```bash
# Check service logs
journalctl -u triangle-detector -10

# Manual test
python3 /home/pi/MHSF_Guide/triangle_detector_app_CV.py
```

### "Permission denied" on service
The service runs as user `pi`. Ensure:
- Pi user owns the project directory: `sudo chown -R pi:pi ~/MHSF_Guide`
- Camera device is accessible: `sudo usermod -aG video pi`
- Restart service: `sudo systemctl restart triangle-detector`

### "Display not showing" over SSH
Use X11 forwarding:
```bash
ssh -X pi@<pi-ip>
python3 triangle_detector_app_CV.py
```

Or use VNC:
```bash
sudo apt-get install vncserver
vncserver
# Then connect with VNC viewer
```

---

## File Structure After Setup

```
~/MHSF_Guide/
├── setup.sh                          # Main setup script
├── run_detector.sh                   # Simple run wrapper
├── triangle-detector.service         # Systemd service file
├── triangle_detector_app_CV.py       # OpenCV version (main)
├── triangle_config.json              # Config (created on first run)
├── README.md                         # User documentation
└── INSTALL_INSTRUCTIONS.md           # This file
```

---

## Configuration Files

### triangle_config.json
Located in project directory. Created on first "Save Config":

```json
{
    "distance_threshold": 15,
    "min_triangle_area": 10,
    "resolution": [320, 480],
    "camera_id": 0
}
```

Edit before first run to set defaults:
```bash
nano triangle_config.json
```

### Systemd Service (/etc/systemd/system/triangle-detector.service)
Auto-created or manually placed there. Controls:
- Which user runs the app (default: `pi`)
- Display configuration
- Restart behavior
- Log output

Edit with:
```bash
sudo nano /etc/systemd/system/triangle-detector.service
```

After editing:
```bash
sudo systemctl daemon-reload
sudo systemctl restart triangle-detector
```

---

## Performance Tuning

### For Raspberry Pi 5
App runs at ~20+ fps naturally. To optimize:

```bash
# Disable desktop effects
# In Raspberry Pi settings: Preferences > Appearance > Effects: None

# Reduce resolution in triangle_config.json (if needed)
# "resolution": [240, 320]  # Instead of [320, 480]
```

### Monitor Resource Usage
```bash
# While app is running in another terminal:
watch -n 1 'ps aux | grep python'
top  # Press 'q' to quit
vcgencmd measure_temp  # CPU temperature
```

---

## Uninstall / Cleanup

### Disable Service
```bash
sudo systemctl disable triangle-detector.service
sudo systemctl stop triangle-detector.service
sudo rm /etc/systemd/system/triangle-detector.service
sudo systemctl daemon-reload
```

### Remove Installation
```bash
python3 -m pip uninstall PySide6 opencv-python numpy -y
rm -rf ~/MHSF_Guide
```

---

## Support & Debugging

### Collect Diagnostic Info
```bash
# Run diagnostic script
python3 << 'EOF'
import platform
import sys
import cv2
print(f"Python: {sys.version}")
print(f"OS: {platform.system()}")
print(f"OpenCV: {cv2.__version__}")
try:
    from PySide6 import QtCore
    print(f"PySide6: {QtCore.__version__}")
except: pass
print(f"Camera 0: {cv2.VideoCapture(0).isOpened()}")
EOF
```

### Full System Logs
```bash
journalctl -u triangle-detector --since "1 hour ago" > ~/detector_logs.txt
cat ~/detector_logs.txt
```

---

## Next Steps

1. ✅ **Installation complete** - App configured for auto-boot
2. ⚙️ **Launch app** - `bash run_detector.sh`
3. 🎯 **Adjust settings** - Use spinbox controls in app
4. 💾 **Save configuration** - Click "Save Config" button
5. 🚀 **Deploy** - Reboot to verify auto-start works

---

**Questions?** Check README.md for usage and troubleshooting guides.
