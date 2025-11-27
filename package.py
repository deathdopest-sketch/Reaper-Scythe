#!/usr/bin/env python3
"""
Simple Release Packaging Script

Entry point for creating release packages. This script handles
building, signing, and packaging Reaper for distribution.

Usage:
    python package.py              # Full release package
    python package.py --build     # Build only
    python package.py --installer  # Build + installer only
    python package.py --no-sign    # Skip code signing
"""

import sys
import os

# Add packaging to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from packaging.release import ReleasePackager, main

if __name__ == "__main__":
    main()

