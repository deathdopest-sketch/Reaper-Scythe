"""
REAPER Buffer Type

This module provides buffer types for memory manipulation operations.
Buffers are wrappers around byte arrays that provide safe memory operations.
"""

from typing import Optional, Union
import struct
from .reaper_error import ReaperRuntimeError, ReaperMemoryError, ReaperTypeError


class ReaperBuffer:
    """
    Buffer type for memory manipulation operations.
    
    Provides safe access to raw memory with bounds checking.
    """
    
    def __init__(self, size: int, data: Optional[bytes] = None):
        """
        Initialize buffer.
        
        Args:
            size: Buffer size in bytes
            data: Optional initial data (must be <= size bytes)
        
        Raises:
            ReaperMemoryError: If size exceeds limits
        """
        # Limit buffer size to 10MB
        max_buffer_size = 10 * 1024 * 1024
        if size > max_buffer_size:
            raise ReaperMemoryError(
                f"Buffer size {size} exceeds maximum {max_buffer_size}",
                resource_type="buffer",
                current_size=size,
                max_size=max_buffer_size
            )
        
        self.size = size
        self.data = bytearray(size)
        
        if data:
            if len(data) > size:
                raise ReaperRuntimeError(
                    f"Initial data ({len(data)} bytes) exceeds buffer size ({size} bytes)"
                )
            self.data[:len(data)] = data
    
    def read(self, offset: int, length: int) -> bytes:
        """
        Read bytes from buffer.
        
        Args:
            offset: Starting offset
            length: Number of bytes to read
            
        Returns:
            Bytes read
            
        Raises:
            ReaperRuntimeError: If offset/length out of bounds
        """
        if offset < 0 or offset >= self.size:
            raise ReaperRuntimeError(f"Read offset {offset} out of bounds (0-{self.size-1})")
        
        if length < 0:
            raise ReaperRuntimeError(f"Read length {length} cannot be negative")
        
        end = min(offset + length, self.size)
        return bytes(self.data[offset:end])
    
    def write(self, offset: int, data: bytes) -> None:
        """
        Write bytes to buffer.
        
        Args:
            offset: Starting offset
            data: Bytes to write
            
        Raises:
            ReaperRuntimeError: If offset out of bounds or data too large
        """
        if offset < 0 or offset >= self.size:
            raise ReaperRuntimeError(f"Write offset {offset} out of bounds (0-{self.size-1})")
        
        if offset + len(data) > self.size:
            raise ReaperRuntimeError(
                f"Write would exceed buffer size: {offset} + {len(data)} > {self.size}"
            )
        
        self.data[offset:offset+len(data)] = data
    
    def read_int(self, offset: int, size: int = 4, signed: bool = True, byteorder: str = 'little') -> int:
        """
        Read integer from buffer.
        
        Args:
            offset: Starting offset
            size: Size in bytes (1, 2, 4, or 8)
            signed: Whether signed integer
            byteorder: 'little' or 'big'
            
        Returns:
            Integer value
        """
        if size not in [1, 2, 4, 8]:
            raise ReaperRuntimeError(f"Invalid integer size: {size} (must be 1, 2, 4, or 8)")
        
        if offset + size > self.size:
            raise ReaperRuntimeError(f"Read would exceed buffer: {offset} + {size} > {self.size}")
        
        data = self.read(offset, size)
        return int.from_bytes(data, byteorder=byteorder, signed=signed)
    
    def write_int(self, offset: int, value: int, size: int = 4, signed: bool = True, byteorder: str = 'little') -> None:
        """
        Write integer to buffer.
        
        Args:
            offset: Starting offset
            value: Integer value
            size: Size in bytes (1, 2, 4, or 8)
            signed: Whether signed integer
            byteorder: 'little' or 'big'
        """
        if size not in [1, 2, 4, 8]:
            raise ReaperRuntimeError(f"Invalid integer size: {size} (must be 1, 2, 4, or 8)")
        
        try:
            data = value.to_bytes(size, byteorder=byteorder, signed=signed)
        except OverflowError:
            raise ReaperRuntimeError(f"Value {value} too large for {size}-byte {'signed' if signed else 'unsigned'} integer")
        
        self.write(offset, data)
    
    def to_bytes(self) -> bytes:
        """Convert buffer to bytes."""
        return bytes(self.data)
    
    def __len__(self) -> int:
        """Get buffer size."""
        return self.size
    
    def __getitem__(self, index: Union[int, slice]) -> Union[int, bytes]:
        """Get byte(s) at index."""
        if isinstance(index, slice):
            return bytes(self.data[index])
        return self.data[index]
    
    def __setitem__(self, index: Union[int, slice], value: Union[int, bytes]) -> None:
        """Set byte(s) at index."""
        if isinstance(index, slice):
            if not isinstance(value, bytes):
                raise ReaperTypeError("Slice assignment requires bytes")
            self.data[index] = value
        else:
            if not isinstance(value, int) or value < 0 or value > 255:
                raise ReaperRuntimeError(f"Byte value must be 0-255, got {value}")
            self.data[index] = value
    
    def __repr__(self) -> str:
        return f"ReaperBuffer(size={self.size}, data={self.data[:16].hex()}...)" if self.size > 16 else f"ReaperBuffer(size={self.size}, data={self.data.hex()})"

