"""
Windows Memory Operations Module

Provides memory read/write operations for Windows.
"""

from typing import Optional
import ctypes
from ctypes import wintypes


class WindowsMemoryOps:
    """
    Windows memory operations.
    """
    
    def __init__(self, pid: int):
        """
        Initialize Windows memory operations.
        
        Args:
            pid: Target process ID
        """
        self.pid = pid
        self.kernel32 = ctypes.windll.kernel32
        self.h_process = None
        self._open_process()
    
    def _open_process(self) -> bool:
        """Open process handle."""
        PROCESS_ALL_ACCESS = 0x1F0FFF
        self.h_process = self.kernel32.OpenProcess(
            PROCESS_ALL_ACCESS,
            False,
            self.pid
        )
        return self.h_process is not None
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """
        Read memory from process.
        
        Args:
            address: Memory address
            size: Size to read
            
        Returns:
            Memory bytes or None
        """
        if not self.h_process:
            return None
        
        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t(0)
        
        if self.kernel32.ReadProcessMemory(
            self.h_process,
            ctypes.c_void_p(address),
            buffer,
            size,
            ctypes.byref(bytes_read)
        ):
            return buffer.raw[:bytes_read.value]
        
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
        if not self.h_process:
            return False
        
        buffer = ctypes.create_string_buffer(data)
        bytes_written = ctypes.c_size_t(0)
        
        # Change memory protection
        PAGE_EXECUTE_READWRITE = 0x40
        old_protect = wintypes.DWORD(0)
        if not self.kernel32.VirtualProtectEx(
            self.h_process,
            ctypes.c_void_p(address),
            len(data),
            PAGE_EXECUTE_READWRITE,
            ctypes.byref(old_protect)
        ):
            return False
        
        # Write memory
        result = self.kernel32.WriteProcessMemory(
            self.h_process,
            ctypes.c_void_p(address),
            buffer,
            len(data),
            ctypes.byref(bytes_written)
        )
        
        # Restore protection
        self.kernel32.VirtualProtectEx(
            self.h_process,
            ctypes.c_void_p(address),
            len(data),
            old_protect.value,
            ctypes.byref(old_protect)
        )
        
        return result and bytes_written.value == len(data)
    
    def close(self) -> None:
        """Close process handle."""
        if self.h_process:
            self.kernel32.CloseHandle(self.h_process)
            self.h_process = None

