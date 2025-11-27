"""
REAPER Memory Manipulation Library

This library provides advanced memory operations:
- Process memory reading/writing
- DLL injection (Windows)
- Shared library injection (Linux)
- Memory scanning
- Memory protection manipulation
- Heap manipulation
- Memory forensics

⚠️ WARNING: This library is for authorized security research only.
Use responsibly and legally. Unauthorized use is illegal.
"""

import sys

if sys.platform == 'win32':
    from .windows_injection import WindowsInjector
    from .windows_memory import WindowsMemoryOps
    __all__ = ['WindowsInjector', 'WindowsMemoryOps']
elif sys.platform.startswith('linux'):
    from .linux_injection import LinuxInjector
    from .linux_memory import LinuxMemoryOps
    __all__ = ['LinuxInjector', 'LinuxMemoryOps']
else:
    __all__ = []

from .scanner import MemoryScanner
from .heap import HeapManipulator
from .forensics import MemoryForensics

__all__.extend([
    'MemoryScanner',
    'HeapManipulator',
    'MemoryForensics',
])

__version__ = "0.1.0"

