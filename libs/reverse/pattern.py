"""
Pattern Matching Module

Provides pattern matching for reverse engineering.
"""

from typing import List, Dict, Optional, Any
import re


class PatternMatcher:
    """
    Pattern matcher for reverse engineering.
    """
    
    def __init__(self):
        """Initialize pattern matcher."""
        self.patterns: Dict[str, bytes] = {}
        self._load_common_patterns()
    
    def _load_common_patterns(self) -> None:
        """Load common patterns."""
        # Common shellcode patterns
        self.patterns['execve'] = b'\x31\xc0\x50\x68\x2f\x2f\x73\x68'
        self.patterns['bind_shell'] = b'\x31\xc0\x31\xdb\x31\xc9'
        self.patterns['reverse_shell'] = b'\x31\xc0\x31\xdb\x31\xc9\x31\xd2'
        
        # Common API patterns
        self.patterns['loadlibrary'] = b'LoadLibrary'
        self.patterns['getprocaddress'] = b'GetProcAddress'
    
    def add_pattern(self, name: str, pattern: bytes) -> None:
        """
        Add custom pattern.
        
        Args:
            name: Pattern name
            pattern: Pattern bytes
        """
        self.patterns[name] = pattern
    
    def find_pattern(self, data: bytes, pattern_name: str) -> List[int]:
        """
        Find pattern in data.
        
        Args:
            data: Data to search
            pattern_name: Pattern name
            
        Returns:
            List of offsets where pattern was found
        """
        if pattern_name not in self.patterns:
            return []
        
        pattern = self.patterns[pattern_name]
        offsets = []
        start = 0
        
        while True:
            offset = data.find(pattern, start)
            if offset == -1:
                break
            offsets.append(offset)
            start = offset + 1
        
        return offsets
    
    def find_all_patterns(self, data: bytes) -> Dict[str, List[int]]:
        """
        Find all patterns in data.
        
        Args:
            data: Data to search
            
        Returns:
            Dictionary mapping pattern names to offsets
        """
        results = {}
        for pattern_name in self.patterns:
            offsets = self.find_pattern(data, pattern_name)
            if offsets:
                results[pattern_name] = offsets
        return results
    
    def match_regex(self, data: bytes, pattern: str) -> List[Dict[str, Any]]:
        """
        Match regex pattern in data.
        
        Args:
            data: Data to search
            pattern: Regex pattern
            
        Returns:
            List of matches
        """
        try:
            text = data.decode('latin-1', errors='ignore')
            matches = []
            for match in re.finditer(pattern, text):
                matches.append({
                    'offset': match.start(),
                    'match': match.group(),
                    'span': match.span(),
                })
            return matches
        except Exception:
            return []

