"""
REAPER Reverse Engineering Library

This library provides advanced reverse engineering tools:
- Decompiler integration
- Pattern matching
- API hooking
- Unpacking utilities
- Anti-debugging detection
- Code obfuscation analysis

⚠️ WARNING: This library is for authorized security research only.
Use responsibly and legally. Unauthorized use is illegal.
"""

from .decompiler import Decompiler
from .pattern import PatternMatcher
from .hooking import APIHooker
from .unpacking import Unpacker
from .antidebug import AntiDebugDetector
from .obfuscation import ObfuscationAnalyzer

__all__ = [
    'Decompiler',
    'PatternMatcher',
    'APIHooker',
    'Unpacker',
    'AntiDebugDetector',
    'ObfuscationAnalyzer',
]

__version__ = "0.1.0"

