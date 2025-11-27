"""
Binary Patching Module

Provides utilities for patching binaries.
"""

from typing import List, Dict, Optional
from pathlib import Path


class BinaryPatcher:
    """
    Patcher for binary files.
    """
    
    def __init__(self, binary_path: str):
        """
        Initialize binary patcher.
        
        Args:
            binary_path: Path to binary file
        """
        self.binary_path = Path(binary_path)
        if not self.binary_path.exists():
            raise FileNotFoundError(f"Binary not found: {binary_path}")
        
        self.data = bytearray(self.binary_path.read_bytes())
        self.backup_path = self.binary_path.with_suffix(self.binary_path.suffix + '.bak')
    
    def create_backup(self) -> None:
        """Create backup of original binary."""
        if not self.backup_path.exists():
            self.backup_path.write_bytes(self.data)
    
    def patch_bytes(self, offset: int, new_bytes: bytes) -> None:
        """
        Patch bytes at offset.
        
        Args:
            offset: Offset to patch
            new_bytes: New bytes to write
        """
        if offset + len(new_bytes) > len(self.data):
            raise ValueError(f"Patch would exceed file size: {offset} + {len(new_bytes)} > {len(self.data)}")
        
        self.data[offset:offset+len(new_bytes)] = new_bytes
    
    def patch_instruction(self, address: int, new_instruction: bytes) -> None:
        """
        Patch instruction at address.
        
        Args:
            address: Instruction address
            new_instruction: New instruction bytes
        """
        # Convert address to file offset (simplified - would need proper mapping)
        offset = address  # Placeholder
        self.patch_bytes(offset, new_instruction)
    
    def nop_patch(self, offset: int, size: int) -> None:
        """
        NOP out bytes at offset.
        
        Args:
            offset: Offset to patch
            size: Number of bytes to NOP
        """
        nop_bytes = b'\x90' * size  # NOP instruction for x86/x86-64
        self.patch_bytes(offset, nop_bytes)
    
    def save(self, output_path: Optional[str] = None) -> None:
        """
        Save patched binary.
        
        Args:
            output_path: Output path (default: overwrite original)
        """
        if output_path:
            Path(output_path).write_bytes(self.data)
        else:
            self.binary_path.write_bytes(self.data)
    
    def restore_backup(self) -> None:
        """Restore from backup."""
        if self.backup_path.exists():
            self.data = bytearray(self.backup_path.read_bytes())
            self.save()

