#!/usr/bin/env python3
"""
Version Management for Reaper Language

Centralized version information for the Reaper standalone hacking language.
Used by build system, packaging, and runtime to display version information.
"""

__version__ = "0.9.0"
__version_info__ = (0, 9, 0)
__release_date__ = "2025-01-27"
__build_number__ = None  # Set during build process

def get_version():
    """Get version string."""
    return __version__

def get_version_info():
    """Get version tuple."""
    return __version_info__

def get_full_version():
    """Get full version string with build info if available."""
    version = __version__
    if __build_number__:
        version += f".{__build_number__}"
    return version

def get_version_string():
    """Get formatted version string for display."""
    version = f"Reaper Language v{__version__}"
    if __release_date__:
        version += f" ({__release_date__})"
    if __build_number__:
        version += f" [build {__build_number__}]"
    return version

if __name__ == "__main__":
    print(get_version_string())

