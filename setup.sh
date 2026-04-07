#!/bin/bash

# MHSF Triangle Detector - Setup Script for Raspberry Pi 5
# This script installs dependencies and configures the app to run on system boot
# Run with: bash setup.sh or sudo bash setup.sh

set -e  # Exit on error

echo "================================"
echo "MHSF Triangle Detector - Setup"
echo "Pi5 Edition with Auto-Start"
echo "================================"
echo ""

# Determine the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "✓ Project directory: $SCRIPT_DIR"
echo ""

# Step 1: Check if Python 3 is installed
echo "[1/7] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed"
    echo "Install with: sudo apt-get install python3 python3-pip python3-dev"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✓ Found: $PYTHON_VERSION"
echo ""

# Step 2: Install system dependencies (Pi5 requirements for PyQt5/Qt)
echo "[2/7] Installing system dependencies for Pi5..."
if [[ $EUID -eq 0 ]]; then
    echo "     Installing Qt libraries, OpenGL support, build tools, and Python dev..."
    apt-get update -qq
    apt-get install -y -qq \
        build-essential python3-dev cmake \
        libgl1-mesa-glx libxkbcommon-x11-0 libxkbcommon0 libdbus-1-3 libfontconfig1 libfreetype6 libharfbuzz0b \
        libjpeg62-turbo libpng16-16 libtiff6 libpulse0 libssl3 libzstd1 \
        libx11-6 libxext6 libxrender1 libxcb1 libxcb-glx0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
        libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-sync1 libxcb-util1 libxcb-xfixes0 \
        libxcb-xinerama0 libxcb-xinput0 libxcb-xkb1 libwayland-client0 \
        libwebkit2gtk-4.0-dev clang libclang-dev > /dev/null 2>&1
    echo "✓ System dependencies installed"
    
    # Install system PyQt5 from Raspbian repository (within same step for brevity)
    echo ""
    echo "     Installing python3-pyqt5 from Raspbian repository..."
    apt-get install -y -qq python3-pyqt5 > /dev/null 2>&1
    echo "✓ System python3-pyqt5 installed"
else
    echo "⚠ Skipping system dependencies (requires sudo)"
    echo "  To complete setup including auto-start, run:"
    echo "  sudo bash setup.sh"
    echo ""
fi
echo ""

# Step 3: Create Python Virtual Environment
echo "[3/7] Creating Python virtual environment..."
VENV_PATH="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_PATH" ]; then
    # Create venv with --system-site-packages to access system python3-pyqt5
    python3 -m venv --system-site-packages "$VENV_PATH"
    echo "✓ Virtual environment created at: $VENV_PATH"
    echo "  (with system site-packages enabled for PyQt5)"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Step 4: Upgrade pip in virtual environment
echo "[4/7] Updating pip in virtual environment..."
"$VENV_PATH/bin/python3" -m pip install --upgrade pip setuptools wheel --quiet 2>/dev/null || true
echo "✓ pip updated"
echo ""

# Step 5: Install remaining Python dependencies in virtual environment
echo "[5/7] Installing remaining Python dependencies..."
echo "     Installing: numpy, opencv-python"
echo "     (PyQt5 provided by system package, installation takes ~30-60 seconds)"

# Install numpy first (opencv-python depends on it)
"$VENV_PATH/bin/python3" -m pip install \
    --default-timeout=1000 \
    numpy --quiet

if [ $? -ne 0 ]; then
    echo "⚠ NumPy installation failed, retrying..."
    "$VENV_PATH/bin/python3" -m pip install \
        --default-timeout=1000 \
        --retries 5 \
        numpy
fi

# Then install opencv-python
"$VENV_PATH/bin/python3" -m pip install \
    --default-timeout=1000 \
    opencv-python --quiet

if [ $? -eq 0 ]; then
    echo "✓ Python dependencies installed successfully"
    echo "  - NumPy: installed via pip"
    echo "  - OpenCV: installed via pip"
    echo "  - PyQt5: provided by system package (python3-pyqt5)"
else
    echo ""
    echo "⚠ OpenCV installation failed, retrying..."
    # Fallback retry
    "$VENV_PATH/bin/python3" -m pip install \
        --default-timeout=1000 \
        --retries 5 \
        opencv-python
    echo "✓ Python dependencies installed"
fi

# Verify all required modules are available
echo ""
echo "     Verifying module imports..."
echo "     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
"$VENV_PATH/bin/python3" -c "import json; import numpy; import cv2; print(''); print('  ✓ json: OK'); print('  ✓ numpy: OK'); print('  ✓ cv2 (OpenCV): OK'); print('')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠ Warning: Some modules failed to import. Checking individually..."
    "$VENV_PATH/bin/python3" -c "import json" 2>/dev/null && echo "  ✓ json available" || echo "  ✗ json NOT available"
    "$VENV_PATH/bin/python3" -c "import numpy" 2>/dev/null && echo "  ✓ numpy available" || echo "  ✗ numpy NOT available - Try: pip install numpy"
    "$VENV_PATH/bin/python3" -c "import cv2" 2>/dev/null && echo "  ✓ cv2 available" || echo "  ✗ cv2 NOT available - Try: pip install opencv-python"
    exit 1
fi

echo ""

# Step 6: Create systemd service file
echo "[6/7] Creating systemd service for auto-start..."
SERVICE_FILE="/etc/systemd/system/triangle-detector.service"

# Check if running with sudo for systemd installation
if [[ $EUID -ne 0 ]]; then
    echo "⚠ Skipping systemd service (requires sudo)"
    echo "  To install service manually, run:"
    echo "  sudo bash setup.sh"
    echo ""
else
    cat > "$SERVICE_FILE" << 'EOF'
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
Environment="HOME=/home/pi"
WorkingDirectory=/home/pi/MHSF_Guide
ExecStartPre=/bin/sleep 3
ExecStart=/home/pi/MHSF_Guide/.venv/bin/python3 /home/pi/MHSF_Guide/triangle_detector_app_CV.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=triangle-detector

[Install]
WantedBy=graphical.target
EOF
    
    chmod 644 "$SERVICE_FILE"
    systemctl daemon-reload
    echo "✓ Systemd service created: $SERVICE_FILE"
    echo ""
    
    # Enable service for auto-start
    systemctl enable triangle-detector.service
    echo "✓ Service enabled for auto-start on reboot"
    echo ""
fi

# Step 7: Create run script wrapper
echo "[7/7] Creating run wrapper script..."
RUN_SCRIPT="$SCRIPT_DIR/run_detector.sh"

cat > "$RUN_SCRIPT" << 'EOF'
#!/bin/bash
# Triangle Detector Run Wrapper
# Provides a convenient way to start the app

cd "$(dirname "$0")"
echo "Starting MHSF Triangle Detector..."
echo "Press Ctrl+C to exit"
echo ""

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "⚠ Warning: Virtual environment not found. Install dependencies first with: bash setup.sh"
fi
echo ""

# Ensure display environment is set
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
fi

if [ -z "$XAUTHORITY" ]; then
    export XAUTHORITY=/home/pi/.Xauthority
fi

export QT_QPA_PLATFORM=xcb
# QT plugin path for PySide2 (will work from venv)
if [ -d ".venv/lib/python*/site-packages/PySide2/Qt/plugins" ]; then
    export QT_QPA_PLATFORM_PLUGIN_PATH=".venv/lib/python*/site-packages/PySide2/Qt/plugins"
fi

python3 triangle_detector_app_CV.py
EOF

chmod +x "$RUN_SCRIPT"
echo "✓ Wrapper script created: $RUN_SCRIPT"
echo ""

# Summary
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Virtual Environment: $VENV_PATH"
echo "Dependencies installed in isolated venv"
echo ""
echo "Options to run the app:"
echo ""
echo "1. Direct run:"
echo "   cd $SCRIPT_DIR"
echo "   python3 triangle_detector_app_CV.py"
echo ""
echo "2. Use wrapper script:"
echo "   bash $RUN_SCRIPT"
echo ""

if [[ $EUID -eq 0 ]]; then
    echo "3. Systemd Service (auto-start on reboot):"
    echo "   Status:  sudo systemctl status triangle-detector"
    echo "   Start:   sudo systemctl start triangle-detector"
    echo "   Stop:    sudo systemctl stop triangle-detector"
    echo "   Restart: sudo systemctl restart triangle-detector"
    echo ""
    echo "Logs:"
    echo "   Real-time: sudo journalctl -u triangle-detector -f"
    echo "   Recent:    sudo journalctl -u triangle-detector -n 50"
    echo ""
    echo "✓ AUTO-START ON REBOOT CONFIGURED"
else
    echo "⚠ Run with sudo for complete setup:"
    echo "   sudo bash setup.sh"
    echo ""
fi

echo "Configuration file: $SCRIPT_DIR/triangle_config.json"
echo "Camera range: 0-9"
echo ""
echo "✓ Setup successfully completed!"
