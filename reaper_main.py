#!/usr/bin/env python3
"""
REAPER Standalone Executable Entry Point

This is the main entry point for the standalone compiled Reaper interpreter.
It imports and wraps the core Reaper CLI to create a standalone executable.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main Reaper CLI
from core.reaper import main

if __name__ == "__main__":
    sys.exit(main())

