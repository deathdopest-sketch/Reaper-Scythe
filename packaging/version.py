"""
Version management for packaging system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from version import get_version, get_version_info, get_full_version, get_version_string
except ImportError:
    # Fallback if version.py not found
    def get_version():
        return "0.2.0"
    
    def get_version_info():
        return (0, 2, 0)
    
    def get_full_version():
        return "0.2.0"
    
    def get_version_string():
        return "Reaper Language v0.2.0"

__all__ = ['get_version', 'get_version_info', 'get_full_version', 'get_version_string']

