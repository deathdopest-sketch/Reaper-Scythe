#!/bin/bash
# Linux/macOS build script for Reaper executable
# Usage: ./build.sh [package|installer|sign]
#   package   - Full release package (build + installer + checksums)
#   installer - Build + create installer
#   sign      - Build + sign executable
#   (no args) - Build only

set -e

MODE=${1:-build}

echo "Building Reaper executable..."
echo "Mode: $MODE"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check Python version (need 3.8+)
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$python_version 3.8" | awk '{print ($1 < $2)}') == 1 ]]; then
    echo "Error: Python 3.8 or higher is required (found $python_version)"
    exit 1
fi

# Check if Nuitka is installed
if ! python3 -m nuitka --version &> /dev/null; then
    echo "Installing Nuitka..."
    python3 -m pip install nuitka
fi

# Run appropriate mode
if [ "$MODE" == "package" ]; then
    # Full release package
    python3 package.py
elif [ "$MODE" == "installer" ]; then
    # Build + installer
    python3 nuitka_build.py
    python3 -m packaging.installers "$(uname -s)"
elif [ "$MODE" == "sign" ]; then
    # Build + sign
    python3 nuitka_build.py
    if [[ "$OSTYPE" == "darwin"* ]] && [ -n "$APPLE_DEVELOPER_ID" ]; then
        python3 -m packaging.signing dist/reaper.app
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Warning: Code signing not typically used on Linux"
    else
        echo "Warning: Code signing credentials not configured"
    fi
else
    # Build only
    python3 nuitka_build.py
    
    if [ $? -eq 0 ]; then
        echo "Build completed successfully!"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Executable: dist/reaper.app"
        else
            echo "Executable: dist/reaper"
        fi
    else
        echo "Build failed!"
        exit 1
    fi
fi

