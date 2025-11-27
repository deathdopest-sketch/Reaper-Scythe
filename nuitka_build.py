#!/usr/bin/env python3
"""
Nuitka Build Configuration Script for Reaper

This script configures and runs Nuitka to compile the Reaper interpreter
into a standalone executable with all dependencies bundled.
"""

import os
import sys
import subprocess
import platform

# Import version information
try:
    from version import get_version, get_version_string
except ImportError:
    def get_version():
        return "0.2.0"
    def get_version_string():
        return "Reaper Language v0.2.0"

def check_nuitka():
    """Check if Nuitka is installed."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Nuitka version: {result.stdout.strip()}")
            return True
        return False
    except Exception:
        return False

def install_nuitka():
    """Install Nuitka if not present."""
    print("Installing Nuitka...")
    subprocess.run([sys.executable, "-m", "pip", "install", "nuitka"], check=True)
    print("Nuitka installed successfully!")

def get_platform_specific_options():
    """Get platform-specific Nuitka options."""
    system = platform.system()
    options = []
    
    if system == "Windows":
        options.extend([
            "--windows-console-mode=force",  # Force console window
            "--windows-icon-from-ico=icon.ico" if os.path.exists("icon.ico") else "",
        ])
    elif system == "Darwin":  # macOS
        options.extend([
            "--macos-create-app-bundle",
            "--macos-app-icon=icon.icns" if os.path.exists("icon.icns") else "",
        ])
    elif system == "Linux":
        options.extend([
            "--linux-icon=icon.png" if os.path.exists("icon.png") else "",
        ])
    
    # Filter out empty strings
    return [opt for opt in options if opt]

def build_reaper():
    """Build Reaper executable with Nuitka."""
    
    # Check if Nuitka is installed
    if not check_nuitka():
        print("Nuitka not found. Installing...")
        install_nuitka()
    
    # Get platform-specific options
    platform_opts = get_platform_specific_options()
    
    # Base Nuitka options
    nuitka_cmd = [
        sys.executable, "-m", "nuitka",
        
        # Main module
        "reaper_main.py",
        
        # Standalone mode (bundle all dependencies)
        "--standalone",
        
        # Include all modules
        "--include-module=core",
        "--include-module=libs",
        "--include-module=bytecode",
        
        # Include data files
        "--include-data-dir=libs=libs",
        "--include-data-dir=core=core",
        "--include-data-dir=bytecode=bytecode",
        
        # Remove debug output
        "--remove-output",
        
        # Enable progress bar
        "--show-progress",
        "--show-memory",
        
        # Output directory
        "--output-dir=dist",
        
        # Binary name
        "--output-filename=reaper",
        
        # Include packages
        "--include-package=cryptography",
        "--include-package=scapy",
        "--include-package=requests",
        "--include-package=PIL",
        "--include-package=numpy",
        "--include-package=psutil",
        "--include-package=bs4",
        "--include-package=lxml",
        
        # Python version
        f"--python-version={sys.version_info.major}.{sys.version_info.minor}",
        
        # Onefile mode (single executable)
        "--onefile",
        
        # Platform-specific options
    ] + platform_opts
    
    # Filter out empty strings
    nuitka_cmd = [arg for arg in nuitka_cmd if arg]
    
    version = get_version()
    version_string = get_version_string()
    
    print("=" * 60)
    print(version_string)
    print("Building Reaper executable with Nuitka...")
    print("=" * 60)
    print(f"Command: {' '.join(nuitka_cmd)}")
    print()
    
    try:
        result = subprocess.run(nuitka_cmd, check=True)
        print("\n✅ Build successful!")
        print(f"Executable location: dist/reaper{'.exe' if platform.system() == 'Windows' else ''}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with exit code {e.returncode}")
        return 1
    except KeyboardInterrupt:
        print("\n\nBuild interrupted by user")
        return 1

if __name__ == "__main__":
    sys.exit(build_reaper())

