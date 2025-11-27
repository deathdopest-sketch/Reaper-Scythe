"""
Linux Memory Operations Module

Provides memory read/write operations for Linux.
"""

from typing import Optional
import os


class LinuxMemoryOps:
    """
    Linux memory operations.
    """
    
    def __init__(self, pid: int):
        """
        Initialize Linux memory operations.
        
        Args:
            pid: Target process ID
        """
        self.pid = pid
        self.mem_path = f"/proc/{pid}/mem"
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """
        Read memory from process.
        
        Args:
            address: Memory address
            size: Size to read
            
        Returns:
            Memory bytes or None
        """
        try:
            with open(self.mem_path, 'rb') as f:
                f.seek(address)
                return f.read(size)
        except (OSError, PermissionError):
            return None
    
    def write_memory(self, address: int, data: bytes) -> bool:
        """
        Write memory to process.
        
        Args:
            address: Memory address
            data: Data to write
            
        Returns:
            True if successful
        """
        try:
            with open(self.mem_path, 'wb') as f:
                f.seek(address)
                f.write(data)
            return True
        except (OSError, PermissionError):
            return False

