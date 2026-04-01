#!/bin/bash

# MHSF Triangle Detector - Run Wrapper
# Simple script to start the triangle detection application
# Usage: bash run_detector.sh

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo "       MHSF Triangle Detector"
echo "=========================================="
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Python version: $(python3 --version)"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import PySide6; import cv2; import numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ Missing dependencies!"
    echo "Run setup first: bash setup.sh"
    exit 1
fi
echo "✓ All dependencies found"
echo ""

# Start the application
echo "Starting application..."
echo "(Press Ctrl+C to exit)"
echo ""

cd "$PROJECT_DIR"
python3 triangle_detector_app_CV.py

echo ""
echo "Application stopped."
