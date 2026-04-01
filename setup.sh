#!/bin/bash

# MHSF Triangle Detector - Setup Script
# This script installs dependencies and configures the app to run on system boot
# Run with: bash setup.sh

set -e  # Exit on error

echo "================================"
echo "MHSF Triangle Detector - Setup"
echo "================================"
echo ""

# Determine the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "✓ Project directory: $SCRIPT_DIR"
echo ""

# Step 1: Check if Python 3 is installed
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed"
    echo "Install with: sudo apt-get install python3 python3-pip"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✓ Found: $PYTHON_VERSION"
echo ""

# Step 2: Upgrade pip
echo "[2/5] Updating pip..."
python3 -m pip install --upgrade pip --quiet
echo "✓ pip updated"
echo ""

# Step 3: Install Python dependencies
echo "[3/5] Installing Python dependencies..."
echo "     Installing: PySide6, opencv-python, numpy"
python3 -m pip install PySide6 opencv-python numpy --quiet
echo "✓ Core dependencies installed"
echo ""

# Step 4: Create systemd service file
echo "[4/5] Creating systemd service..."
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
After=network.target display-manager.service

[Service]
Type=simple
User=pi
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/pi/.Xauthority"
ExecStart=/usr/bin/python3 /home/pi/MHSF_Guide/triangle_detector_app_CV.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
EOF
    
    chmod 644 "$SERVICE_FILE"
    systemctl daemon-reload
    echo "✓ Systemd service created: $SERVICE_FILE"
    echo ""
    
    # Ask to enable service
    read -p "Enable auto-start on boot? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl enable triangle-detector.service
        echo "✓ Service enabled for auto-start"
    else
        echo "⊘ Service not enabled (start manually)"
    fi
    echo ""
fi

# Step 5: Create run script wrapper
echo "[5/5] Creating run wrapper script..."
RUN_SCRIPT="$SCRIPT_DIR/run_detector.sh"

cat > "$RUN_SCRIPT" << 'EOF'
#!/bin/bash
# Triangle Detector Run Wrapper
# Provides a convenient way to start the app

cd "$(dirname "$0")"
echo "Starting MHSF Triangle Detector..."
echo "Press Ctrl+C to exit"
echo ""

python3 triangle_detector_app_CV.py
EOF

chmod +x "$RUN_SCRIPT"
echo "✓ Wrapper script created: $RUN_SCRIPT"
echo ""

# Step 6: Summary and next steps
echo "================================"
echo "Setup Complete!"
echo "================================"
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
    echo "3. Auto-start on boot (enabled):"
    echo "   systemctl start triangle-detector"
    echo "   systemctl stop triangle-detector"
    echo "   systemctl status triangle-detector"
    echo ""
    echo "View logs:"
    echo "   journalctl -u triangle-detector -f"
    echo ""
fi

echo "Configuration file: $SCRIPT_DIR/triangle_config.json"
echo "Camera detection range: 0-9"
echo ""
echo "✓ Setup completed successfully!"
