"""
REAPER Binary Analysis Library

This library provides tools for analyzing binaries, disassembly, and reverse engineering:
- Binary parsing (ELF, PE, Mach-O)
- Disassembly integration
- Symbol extraction
- String extraction
- Function analysis
- Control flow graph generation
- Binary patching
- Binary comparison

⚠️ WARNING: This library is for authorized security research only.
Use responsibly and legally. Unauthorized use is illegal.
"""

from .parser import BinaryParser, ELFParser, PEParser, MachOParser
from .disassembler import Disassembler
from .symbols import SymbolExtractor
from .strings import StringExtractor
from .functions import FunctionAnalyzer
from .cfg import ControlFlowGraph
from .patcher import BinaryPatcher
from .comparison import BinaryComparator

__all__ = [
    'BinaryParser',
    'ELFParser',
    'PEParser',
    'MachOParser',
    'Disassembler',
    'SymbolExtractor',
    'StringExtractor',
    'FunctionAnalyzer',
    'ControlFlowGraph',
    'BinaryPatcher',
    'BinaryComparator',
]

__version__ = "0.1.0"

