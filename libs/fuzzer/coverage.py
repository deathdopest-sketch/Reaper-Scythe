"""
Coverage Tracking Module

Provides code coverage tracking for fuzzing.
"""

from typing import Dict, Set, List, Optional
import hashlib


class CoverageTracker:
    """
    Tracks code coverage during fuzzing.
    """
    
    def __init__(self):
        """Initialize coverage tracker."""
        self.covered_blocks: Set[int] = set()
        self.edge_coverage: Set[tuple] = set()
        self.block_hashes: Dict[int, str] = {}
        self.execution_count: Dict[int, int] = {}
    
    def add_block(self, address: int, hash_value: Optional[str] = None) -> bool:
        """
        Add a covered basic block.
        
        Args:
            address: Block address
            hash_value: Optional hash of block
            
        Returns:
            True if this is a new block
        """
        is_new = address not in self.covered_blocks
        self.covered_blocks.add(address)
        
        if hash_value:
            self.block_hashes[address] = hash_value
        
        if address in self.execution_count:
            self.execution_count[address] += 1
        else:
            self.execution_count[address] = 1
        
        return is_new
    
    def add_edge(self, from_addr: int, to_addr: int) -> bool:
        """
        Add a covered edge.
        
        Args:
            from_addr: Source address
            to_addr: Target address
            
        Returns:
            True if this is a new edge
        """
        edge = (from_addr, to_addr)
        is_new = edge not in self.edge_coverage
        self.edge_coverage.add(edge)
        return is_new
    
    def get_coverage(self) -> Dict[str, any]:
        """
        Get coverage statistics.
        
        Returns:
            Coverage statistics
        """
        return {
            'blocks_covered': len(self.covered_blocks),
            'edges_covered': len(self.edge_coverage),
            'total_executions': sum(self.execution_count.values()),
            'unique_blocks': len(self.covered_blocks),
        }
    
    def calculate_hash(self, data: bytes) -> str:
        """
        Calculate hash of input data.
        
        Args:
            data: Input data
            
        Returns:
            Hash string
        """
        return hashlib.sha256(data).hexdigest()
    
    def is_interesting(self, data: bytes) -> bool:
        """
        Check if input is interesting (covers new code).
        
        Args:
            data: Input data
            
        Returns:
            True if input is interesting
        """
        # Simplified - would check if this input leads to new coverage
        return True

