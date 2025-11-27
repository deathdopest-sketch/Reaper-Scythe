"""
Binary Comparison Module

Provides utilities for comparing binaries.
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path


class BinaryComparator:
    """
    Comparator for binary files.
    """
    
    def __init__(self, binary1_path: str, binary2_path: str):
        """
        Initialize binary comparator.
        
        Args:
            binary1_path: Path to first binary
            binary2_path: Path to second binary
        """
        self.binary1_path = Path(binary1_path)
        self.binary2_path = Path(binary2_path)
        
        if not self.binary1_path.exists():
            raise FileNotFoundError(f"Binary not found: {binary1_path}")
        if not self.binary2_path.exists():
            raise FileNotFoundError(f"Binary not found: {binary2_path}")
        
        self.data1 = self.binary1_path.read_bytes()
        self.data2 = self.binary2_path.read_bytes()
    
    def compare(self) -> Dict[str, any]:
        """
        Compare two binaries.
        
        Returns:
            Comparison results
        """
        differences = self.find_differences()
        
        return {
            'size1': len(self.data1),
            'size2': len(self.data2),
            'size_match': len(self.data1) == len(self.data2),
            'identical': len(differences) == 0,
            'differences': differences,
            'similarity': self.calculate_similarity(),
        }
    
    def find_differences(self) -> List[Dict[str, any]]:
        """
        Find differences between binaries.
        
        Returns:
            List of differences
        """
        differences = []
        min_size = min(len(self.data1), len(self.data2))
        
        for i in range(min_size):
            if self.data1[i] != self.data2[i]:
                differences.append({
                    'offset': i,
                    'byte1': self.data1[i],
                    'byte2': self.data2[i],
                })
        
        # Check for size differences
        if len(self.data1) != len(self.data2):
            differences.append({
                'offset': min_size,
                'type': 'size_mismatch',
                'size1': len(self.data1),
                'size2': len(self.data2),
            })
        
        return differences
    
    def calculate_similarity(self) -> float:
        """
        Calculate similarity percentage.
        
        Returns:
            Similarity percentage (0-100)
        """
        if len(self.data1) == 0 and len(self.data2) == 0:
            return 100.0
        
        min_size = min(len(self.data1), len(self.data2))
        if min_size == 0:
            return 0.0
        
        matches = sum(1 for i in range(min_size) if self.data1[i] == self.data2[i])
        similarity = (matches / max(len(self.data1), len(self.data2))) * 100.0
        
        return similarity
    
    def diff_hex(self) -> str:
        """
        Generate hex diff output.
        
        Returns:
            Hex diff string
        """
        lines = []
        differences = self.find_differences()
        
        for diff in differences[:100]:  # Limit to first 100 differences
            if 'offset' in diff:
                lines.append(f"Offset 0x{diff['offset']:08x}: "
                           f"0x{diff.get('byte1', 0):02x} -> 0x{diff.get('byte2', 0):02x}")
        
        return '\n'.join(lines)

