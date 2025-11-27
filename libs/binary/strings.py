"""
String Extraction Module

Provides utilities for extracting strings from binaries.
"""

from typing import List, Dict, Optional
import re


class StringExtractor:
    """
    Extractor for strings in binaries.
    """
    
    def __init__(self, binary_path: str, min_length: int = 4):
        """
        Initialize string extractor.
        
        Args:
            binary_path: Path to binary file
            min_length: Minimum string length
        """
        self.binary_path = binary_path
        self.min_length = min_length
        with open(binary_path, 'rb') as f:
            self.data = f.read()
    
    def extract_ascii(self) -> List[Dict[str, Any]]:
        """
        Extract ASCII strings.
        
        Returns:
            List of ASCII strings with offsets
        """
        strings = []
        current_string = bytearray()
        current_offset = 0
        
        for i, byte in enumerate(self.data):
            if 32 <= byte <= 126:  # Printable ASCII
                if not current_string:
                    current_offset = i
                current_string.append(byte)
            else:
                if len(current_string) >= self.min_length:
                    strings.append({
                        'offset': current_offset,
                        'string': current_string.decode('ascii', errors='ignore'),
                        'length': len(current_string),
                        'type': 'ascii',
                    })
                current_string = bytearray()
        
        # Check for string at end of file
        if len(current_string) >= self.min_length:
            strings.append({
                'offset': current_offset,
                'string': current_string.decode('ascii', errors='ignore'),
                'length': len(current_string),
                'type': 'ascii',
            })
        
        return strings
    
    def extract_unicode(self) -> List[Dict[str, Any]]:
        """
        Extract Unicode strings.
        
        Returns:
            List of Unicode strings with offsets
        """
        strings = []
        # Simple UTF-16 LE detection
        i = 0
        while i < len(self.data) - 1:
            if self.data[i] != 0 and 32 <= self.data[i] <= 126:
                # Potential UTF-16 LE string
                current_string = bytearray()
                current_offset = i
                j = i
                while j < len(self.data) - 1:
                    if self.data[j] != 0 and 32 <= self.data[j] <= 126 and self.data[j+1] == 0:
                        current_string.append(self.data[j])
                        j += 2
                    else:
                        break
                
                if len(current_string) >= self.min_length:
                    try:
                        strings.append({
                            'offset': current_offset,
                            'string': current_string.decode('utf-16-le', errors='ignore'),
                            'length': len(current_string),
                            'type': 'unicode',
                        })
                    except:
                        pass
                i = j
            else:
                i += 1
        
        return strings
    
    def extract_all(self) -> List[Dict[str, Any]]:
        """
        Extract all strings (ASCII and Unicode).
        
        Returns:
            List of all strings
        """
        strings = self.extract_ascii()
        strings.extend(self.extract_unicode())
        strings.sort(key=lambda x: x['offset'])
        return strings
    
    def search_strings(self, pattern: str) -> List[Dict[str, Any]]:
        """
        Search for strings matching a pattern.
        
        Args:
            pattern: Regex pattern to search for
            
        Returns:
            List of matching strings
        """
        all_strings = self.extract_all()
        regex = re.compile(pattern, re.IGNORECASE)
        matches = []
        
        for s in all_strings:
            if regex.search(s['string']):
                matches.append(s)
        
        return matches

