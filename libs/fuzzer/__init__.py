"""
REAPER Fuzzing Framework

This library provides advanced fuzzing capabilities:
- Mutation engines
- Coverage tracking
- Crash analysis
- Seed corpus management
- Fuzzing strategies
- Network protocol fuzzing
- File format fuzzing

⚠️ WARNING: This library is for authorized security testing only.
Use responsibly and legally. Unauthorized use is illegal.
"""

from .mutator import MutationEngine, BitFlipMutator, ByteFlipMutator, InsertMutator, DeleteMutator
from .coverage import CoverageTracker
from .crash import CrashAnalyzer
from .corpus import CorpusManager
from .strategy import FuzzingStrategy, RandomStrategy, AFLStrategy
from .network_fuzzer import NetworkFuzzer
from .file_fuzzer import FileFuzzer

__all__ = [
    'MutationEngine',
    'BitFlipMutator',
    'ByteFlipMutator',
    'InsertMutator',
    'DeleteMutator',
    'CoverageTracker',
    'CrashAnalyzer',
    'CorpusManager',
    'FuzzingStrategy',
    'RandomStrategy',
    'AFLStrategy',
    'NetworkFuzzer',
    'FileFuzzer',
]

__version__ = "0.1.0"

