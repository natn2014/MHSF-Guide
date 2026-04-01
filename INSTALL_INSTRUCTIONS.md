# MHSF Triangle Detector - Installation & Auto-Boot Setup

Complete guide to install the triangle detection application on Raspberry Pi and configure it to run on boot.

## Quick Start (10 minutes)

### 1. On Raspberry Pi Terminal
```bash
cd ~/MHSF_Guide
bash setup.sh
```

Click "Enable auto-start on boot?" when prompted (recommended).

### 2. Verify Installation
```bash
bash run_detector.sh
```

The app should launch in fullscreen. Press **Ctrl+C** to stop.

---

## Detailed Installation

### Prerequisites
- Raspberry Pi 4 (8GB) or Pi 5 with Raspberry Pi OS
- USB camera connected
- Monitor/display connected (or X11 forwarding)
- Internet connection for downloading packages

### Step 1: Download & Navigate
```bash
cd ~/
# If you haven't cloned yet:
git clone <your-repo-url> MHSF_Guide
cd MHSF_Guide
```

### Step 2: Run Setup Script
```bash
bash setup.sh
```

**What this does:**
✓ Checks Python 3 installation  
✓ Updates pip package manager  
✓ Installs PySide6, OpenCV, NumPy  
✓ Creates systemd service file  
✓ Sets up auto-boot configuration  

**Output:** Should show green checkmarks (✓) for each step.

### Step 3: Manual Service Installation (if not run as sudo)

If the setup script was run without `sudo`, manually install the service:

```bash
sudo cp triangle-detector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable triangle-detector.service
```

Verify:
```bash
sudo systemctl status triangle-detector.service
```

---

## Running the Application

### Option 1: Direct Python Execution
```bash
python3 triangle_detector_app_CV.py
```

### Option 2: Using Wrapper Script
```bash
bash run_detector.sh
```

### Option 3: Starting as Service (if configured)
```bash
# Start
sudo systemctl start triangle-detector

# Stop
sudo systemctl stop triangle-detector

# Check status
sudo systemctl status triangle-detector

# View logs
journalctl -u triangle-detector -f

# Disable auto-boot
sudo systemctl disable triangle-detector
```

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
