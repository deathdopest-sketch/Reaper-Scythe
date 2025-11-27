#!/usr/bin/env python3
"""
Wraith Memory Operations Module
Memory inspection, manipulation, and analysis
"""

import os
import ctypes
import struct
import time
import logging
from typing import Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MemoryProtection(Enum):
    """Memory protection flags"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    READ_WRITE = "read_write"
    READ_EXECUTE = "read_execute"
    READ_WRITE_EXECUTE = "read_write_execute"

class MemoryType(Enum):
    """Memory region types"""
    CODE = "code"
    DATA = "data"
    HEAP = "heap"
    STACK = "stack"
    MAPPED = "mapped"
    SHARED = "shared"
    PRIVATE = "private"

@dataclass
class MemoryRegion:
    """Memory region information"""
    start: int
    end: int
    size: int
    protection: MemoryProtection
    memory_type: MemoryType
    path: Optional[str]
    offset: int
    device: Optional[str]
    inode: Optional[int]

@dataclass
class MemoryOperationResult:
    """Result of memory operation"""
    success: bool
    operation: str
    address: int
    message: str
    data: Optional[bytes] = None
    error: Optional[str] = None

class WraithMemoryManager:
    """Advanced memory operations manager"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize memory manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.safe_mode = self.config.get('safe_mode', True)
        self.max_memory_size = self.config.get('max_memory_size', 1024 * 1024)  # 1MB
        self.operation_log = []
        
    def _log_operation(self, operation: str, address: int, success: bool, message: str):
        """Log memory operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'address': hex(address),
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"Memory operation: {operation} at {hex(address)} - {message}")
    
    def get_memory_regions(self, pid: Optional[int] = None) -> List[MemoryRegion]:
        """Get memory regions for a process
        
        Args:
            pid: Process ID (None for current process)
            
        Returns:
            List of MemoryRegion objects
        """
        regions = []
        
        try:
            if pid is None:
                pid = os.getpid()
            
            # Read /proc/pid/maps on Linux
            if os.name == 'posix':
                maps_file = f"/proc/{pid}/maps"
                if not os.path.exists(maps_file):
                    raise FileNotFoundError(f"Process {pid} not found or no access to maps")
                
                with open(maps_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) < 5:
                            continue
                        
                        # Parse address range
                        addr_range = parts[0].split('-')
                        start = int(addr_range[0], 16)
                        end = int(addr_range[1], 16)
                        size = end - start
                        
                        # Parse permissions
                        perms = parts[1]
                        protection = self._parse_permissions(perms)
                        
                        # Parse offset
                        offset = int(parts[2], 16)
                        
                        # Parse device
                        device = parts[3] if parts[3] != '00:00' else None
                        
                        # Parse inode
                        inode = int(parts[4]) if parts[4] != '0' else None
                        
                        # Parse path
                        path = parts[5] if len(parts) > 5 else None
                        
                        # Determine memory type
                        memory_type = self._determine_memory_type(path, perms)
                        
                        region = MemoryRegion(
                            start=start,
                            end=end,
                            size=size,
                            protection=protection,
                            memory_type=memory_type,
                            path=path,
                            offset=offset,
                            device=device,
                            inode=inode
                        )
                        regions.append(region)
            
            # Windows implementation would use VirtualQueryEx
            elif os.name == 'nt':
                # Basic Windows implementation - return empty list for now
                # Full implementation would require win32api and more complex code
                logger.warning("Windows memory region enumeration not fully implemented")
                regions = []
            
            self._log_operation("get_regions", 0, True, f"Retrieved {len(regions)} memory regions")
            return regions
            
        except Exception as e:
            self._log_operation("get_regions", 0, False, f"Failed to get memory regions: {e}")
            raise
    
    def _parse_permissions(self, perms: str) -> MemoryProtection:
        """Parse memory permissions string"""
        if perms == 'r--':
            return MemoryProtection.READ
        elif perms == 'rw-':
            return MemoryProtection.READ_WRITE
        elif perms == 'r-x':
            return MemoryProtection.READ_EXECUTE
        elif perms == 'rwx':
            return MemoryProtection.READ_WRITE_EXECUTE
        else:
            return MemoryProtection.READ
    
    def _determine_memory_type(self, path: Optional[str], perms: str) -> MemoryType:
        """Determine memory type from path and permissions"""
        if path is None:
            if 'x' in perms:
                return MemoryType.CODE
            else:
                return MemoryType.DATA
        elif '[heap]' in path:
            return MemoryType.HEAP
        elif '[stack]' in path:
            return MemoryType.STACK
        elif path.startswith('/'):
            return MemoryType.MAPPED
        else:
            return MemoryType.DATA
    
    def read_memory(self, address: int, size: int, pid: Optional[int] = None) -> MemoryOperationResult:
        """Read memory from a process
        
        Args:
            address: Memory address
            size: Number of bytes to read
            pid: Process ID (None for current process)
            
        Returns:
            MemoryOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - memory read would be performed at {hex(address)}")
                self._log_operation("read", address, False, "Safe mode enabled - operation blocked")
                return MemoryOperationResult(
                    success=False,
                    operation="read",
                    address=address,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if size > self.max_memory_size:
                raise ValueError(f"Size {size} exceeds maximum allowed {self.max_memory_size}")
            
            if pid is None:
                pid = os.getpid()
            
            # Use ctypes to read memory
            if os.name == 'posix':
                # Use process_vm_readv on Linux
                import ctypes
                from ctypes import c_void_p, c_size_t, c_ssize_t
                
                libc = ctypes.CDLL("libc.so.6")
                
                # Allocate buffer
                buffer = ctypes.create_string_buffer(size)
                
                # Read memory
                result = libc.process_vm_readv(
                    pid,
                    ctypes.byref(buffer),
                    1,
                    ctypes.byref(ctypes.c_void_p(address)),
                    1,
                    0
                )
                
                if result == -1:
                    raise OSError(f"process_vm_readv failed: {os.strerror(ctypes.get_errno())}")
                
                data = buffer.raw[:result]
                
            elif os.name == 'nt':
                # Windows implementation would use ReadProcessMemory
                logger.warning("Windows memory reading not implemented")
                return MemoryOperationResult(
                    success=False,
                    operation="read",
                    address=address,
                    message="Windows memory reading not implemented",
                    error="Not implemented"
                )
            
            self._log_operation("read", address, True, f"Read {len(data)} bytes")
            
            return MemoryOperationResult(
                success=True,
                operation="read",
                address=address,
                message=f"Successfully read {len(data)} bytes",
                data=data
            )
            
        except Exception as e:
            error_msg = f"Memory read failed: {e}"
            self._log_operation("read", address, False, error_msg)
            return MemoryOperationResult(
                success=False,
                operation="read",
                address=address,
                message=error_msg,
                error=str(e)
            )
    
    def write_memory(self, address: int, data: bytes, pid: Optional[int] = None) -> MemoryOperationResult:
        """Write memory to a process
        
        Args:
            address: Memory address
            data: Data to write
            pid: Process ID (None for current process)
            
        Returns:
            MemoryOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - memory write would be performed at {hex(address)}")
                return MemoryOperationResult(
                    success=False,
                    operation="write",
                    address=address,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if len(data) > self.max_memory_size:
                raise ValueError(f"Data size {len(data)} exceeds maximum allowed {self.max_memory_size}")
            
            if pid is None:
                pid = os.getpid()
            
            # Use ctypes to write memory
            if os.name == 'posix':
                # Use process_vm_writev on Linux
                import ctypes
                
                libc = ctypes.CDLL("libc.so.6")
                
                # Write memory
                result = libc.process_vm_writev(
                    pid,
                    ctypes.byref(data),
                    1,
                    ctypes.byref(ctypes.c_void_p(address)),
                    1,
                    0
                )
                
                if result == -1:
                    raise OSError(f"process_vm_writev failed: {os.strerror(ctypes.get_errno())}")
                
            elif os.name == 'nt':
                # Windows implementation would use WriteProcessMemory
                logger.warning("Windows memory writing not implemented")
                return MemoryOperationResult(
                    success=False,
                    operation="write",
                    address=address,
                    message="Windows memory writing not implemented",
                    error="Not implemented"
                )
            
            self._log_operation("write", address, True, f"Wrote {len(data)} bytes")
            
            return MemoryOperationResult(
                success=True,
                operation="write",
                address=address,
                message=f"Successfully wrote {len(data)} bytes"
            )
            
        except Exception as e:
            error_msg = f"Memory write failed: {e}"
            self._log_operation("write", address, False, error_msg)
            return MemoryOperationResult(
                success=False,
                operation="write",
                address=address,
                message=error_msg,
                error=str(e)
            )
    
    def search_memory(self, pattern: bytes, pid: Optional[int] = None, 
                      start_addr: Optional[int] = None, end_addr: Optional[int] = None) -> List[int]:
        """Search for pattern in process memory
        
        Args:
            pattern: Pattern to search for
            pid: Process ID (None for current process)
            start_addr: Start address (None for beginning)
            end_addr: End address (None for end)
            
        Returns:
            List of addresses where pattern was found
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - memory search would be performed")
                return []
            
            if pid is None:
                pid = os.getpid()
            
            regions = self.get_memory_regions(pid)
            matches = []
            
            for region in regions:
                # Skip if outside search range
                if start_addr and region.end <= start_addr:
                    continue
                if end_addr and region.start >= end_addr:
                    continue
                
                # Adjust search range
                search_start = max(region.start, start_addr or region.start)
                search_end = min(region.end, end_addr or region.end)
                
                # Read memory region
                read_result = self.read_memory(search_start, search_end - search_start, pid)
                if not read_result.success:
                    continue
                
                # Search for pattern
                data = read_result.data
                offset = 0
                while True:
                    pos = data.find(pattern, offset)
                    if pos == -1:
                        break
                    matches.append(search_start + pos)
                    offset = pos + 1
            
            self._log_operation("search", 0, True, f"Found {len(matches)} matches")
            return matches
            
        except Exception as e:
            self._log_operation("search", 0, False, f"Memory search failed: {e}")
            return []
    
    def allocate_memory(self, size: int, protection: MemoryProtection = MemoryProtection.READ_WRITE) -> MemoryOperationResult:
        """Allocate memory in current process
        
        Args:
            size: Size to allocate
            protection: Memory protection
            
        Returns:
            MemoryOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - memory allocation would be performed")
                return MemoryOperationResult(
                    success=False,
                    operation="allocate",
                    address=0,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if size > self.max_memory_size:
                raise ValueError(f"Size {size} exceeds maximum allowed {self.max_memory_size}")
            
            # Use ctypes to allocate memory
            if os.name == 'posix':
                import ctypes
                
                libc = ctypes.CDLL("libc.so.6")
                
                # Map protection flags
                prot_map = {
                    MemoryProtection.READ: 0x1,
                    MemoryProtection.WRITE: 0x2,
                    MemoryProtection.EXECUTE: 0x4,
                    MemoryProtection.READ_WRITE: 0x3,
                    MemoryProtection.READ_EXECUTE: 0x5,
                    MemoryProtection.READ_WRITE_EXECUTE: 0x7
                }
                
                prot = prot_map.get(protection, 0x3)
                
                # Allocate memory
                addr = libc.mmap(
                    None,
                    size,
                    prot,
                    0x22,  # MAP_PRIVATE | MAP_ANONYMOUS
                    -1,
                    0
                )
                
                if addr == -1:
                    raise OSError(f"mmap failed: {os.strerror(ctypes.get_errno())}")
                
            elif os.name == 'nt':
                # Windows implementation would use VirtualAlloc
                logger.warning("Windows memory allocation not implemented")
                return MemoryOperationResult(
                    success=False,
                    operation="allocate",
                    address=0,
                    message="Windows memory allocation not implemented",
                    error="Not implemented"
                )
            
            self._log_operation("allocate", addr, True, f"Allocated {size} bytes")
            
            return MemoryOperationResult(
                success=True,
                operation="allocate",
                address=addr,
                message=f"Successfully allocated {size} bytes"
            )
            
        except Exception as e:
            error_msg = f"Memory allocation failed: {e}"
            self._log_operation("allocate", 0, False, error_msg)
            return MemoryOperationResult(
                success=False,
                operation="allocate",
                address=0,
                message=error_msg,
                error=str(e)
            )
    
    def free_memory(self, address: int, size: int) -> MemoryOperationResult:
        """Free allocated memory
        
        Args:
            address: Memory address
            size: Size to free
            
        Returns:
            MemoryOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - memory free would be performed at {hex(address)}")
                return MemoryOperationResult(
                    success=False,
                    operation="free",
                    address=address,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Use ctypes to free memory
            if os.name == 'posix':
                import ctypes
                
                libc = ctypes.CDLL("libc.so.6")
                
                result = libc.munmap(address, size)
                if result == -1:
                    raise OSError(f"munmap failed: {os.strerror(ctypes.get_errno())}")
                
            elif os.name == 'nt':
                # Windows implementation would use VirtualFree
                logger.warning("Windows memory free not implemented")
                return MemoryOperationResult(
                    success=False,
                    operation="free",
                    address=address,
                    message="Windows memory free not implemented",
                    error="Not implemented"
                )
            
            self._log_operation("free", address, True, f"Freed {size} bytes")
            
            return MemoryOperationResult(
                success=True,
                operation="free",
                address=address,
                message=f"Successfully freed {size} bytes"
            )
            
        except Exception as e:
            error_msg = f"Memory free failed: {e}"
            self._log_operation("free", address, False, error_msg)
            return MemoryOperationResult(
                success=False,
                operation="free",
                address=address,
                message=error_msg,
                error=str(e)
            )
    
    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Get operation log"""
        return self.operation_log.copy()
    
    def clear_operation_log(self):
        """Clear operation log"""
        self.operation_log.clear()

# Convenience functions
def get_memory_regions(pid: Optional[int] = None) -> List[MemoryRegion]:
    """Get memory regions"""
    manager = WraithMemoryManager()
    return manager.get_memory_regions(pid)

def read_memory(address: int, size: int, pid: Optional[int] = None) -> MemoryOperationResult:
    """Read memory"""
    manager = WraithMemoryManager()
    return manager.read_memory(address, size, pid)

def search_memory(pattern: bytes, pid: Optional[int] = None, 
                 start_addr: Optional[int] = None, end_addr: Optional[int] = None) -> List[int]:
    """Search memory"""
    manager = WraithMemoryManager()
    return manager.search_memory(pattern, pid, start_addr, end_addr)

# Export main classes and functions
__all__ = [
    'WraithMemoryManager', 'MemoryProtection', 'MemoryType', 'MemoryRegion', 'MemoryOperationResult',
    'get_memory_regions', 'read_memory', 'search_memory'
]
