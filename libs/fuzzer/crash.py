"""
Crash Analysis Module

Provides crash analysis for fuzzing.
"""

from typing import Dict, Optional, List, Any
import traceback
import sys


class CrashAnalyzer:
    """
    Analyzer for crashes found during fuzzing.
    """
    
    def __init__(self):
        """Initialize crash analyzer."""
        self.crashes: List[Dict[str, Any]] = []
    
    def analyze_crash(self, input_data: bytes, exception: Exception,
                     traceback_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a crash.
        
        Args:
            input_data: Input that caused crash
            exception: Exception that occurred
            traceback_str: Optional traceback string
            
        Returns:
            Crash analysis
        """
        crash_info = {
            'input_hash': self._hash_input(input_data),
            'input_size': len(input_data),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback_str or self._get_traceback(),
            'input_preview': input_data[:100].hex() if len(input_data) > 100 else input_data.hex(),
        }
        
        self.crashes.append(crash_info)
        return crash_info
    
    def _hash_input(self, data: bytes) -> str:
        """Hash input data."""
        import hashlib
        return hashlib.sha256(data).hexdigest()
    
    def _get_traceback(self) -> str:
        """Get current traceback."""
        return ''.join(traceback.format_exception(*sys.exc_info()))
    
    def is_unique_crash(self, crash_info: Dict[str, Any]) -> bool:
        """
        Check if crash is unique.
        
        Args:
            crash_info: Crash information
            
        Returns:
            True if unique
        """
        crash_hash = crash_info['input_hash']
        for existing_crash in self.crashes:
            if existing_crash['input_hash'] == crash_hash:
                return False
        return True
    
    def get_crashes(self) -> List[Dict[str, Any]]:
        """
        Get all crashes.
        
        Returns:
            List of crash information
        """
        return self.crashes
    
    def get_unique_crashes(self) -> List[Dict[str, Any]]:
        """
        Get unique crashes only.
        
        Returns:
            List of unique crashes
        """
        unique = []
        seen_hashes = set()
        
        for crash in self.crashes:
            crash_hash = crash['input_hash']
            if crash_hash not in seen_hashes:
                seen_hashes.add(crash_hash)
                unique.append(crash)
        
        return unique

