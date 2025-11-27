"""
Disassembler Module

Provides disassembly capabilities using capstone (if available).
"""

from typing import List, Dict, Optional, Any
import sys


class Disassembler:
    """
    Disassembler for binary code.
    
    Supports multiple architectures.
    """
    
    def __init__(self, arch: str = 'x86_64', mode: Optional[str] = None):
        """
        Initialize disassembler.
        
        Args:
            arch: Target architecture
            mode: Disassembly mode (optional)
        """
        self.arch = arch
        self.mode = mode
        self.capstone = None
        self._init_capstone()
    
    def _init_capstone(self) -> None:
        """Initialize Capstone disassembler if available."""
        try:
            import capstone
            self.capstone = capstone
            
            # Map architecture names
            arch_map = {
                'x86': capstone.CS_ARCH_X86,
                'x86_64': capstone.CS_ARCH_X86,
                'arm': capstone.CS_ARCH_ARM,
                'arm64': capstone.CS_ARCH_ARM64,
                'mips': capstone.CS_ARCH_MIPS,
            }
            
            mode_map = {
                'x86': capstone.CS_MODE_32,
                'x86_64': capstone.CS_MODE_64,
                'arm': capstone.CS_MODE_ARM,
                'arm64': capstone.CS_MODE_ARM,
            }
            
            cs_arch = arch_map.get(self.arch, capstone.CS_ARCH_X86)
            cs_mode = mode_map.get(self.arch, capstone.CS_MODE_64)
            
            self.md = capstone.Cs(cs_arch, cs_mode)
            self.md.detail = True
        except ImportError:
            self.capstone = None
            self.md = None
    
    def disassemble(self, code: bytes, address: int = 0) -> List[Dict[str, Any]]:
        """
        Disassemble code.
        
        Args:
            code: Code bytes to disassemble
            address: Base address for instructions
            
        Returns:
            List of disassembled instructions
        """
        if not self.md:
            # Fallback: return hex dump
            return self._fallback_disassemble(code, address)
        
        instructions = []
        for insn in self.md.disasm(code, address):
            instructions.append({
                'address': insn.address,
                'mnemonic': insn.mnemonic,
                'op_str': insn.op_str,
                'bytes': insn.bytes.hex(),
                'size': insn.size,
            })
        
        return instructions
    
    def _fallback_disassemble(self, code: bytes, address: int) -> List[Dict[str, Any]]:
        """Fallback disassembly when Capstone is not available."""
        instructions = []
        i = 0
        while i < len(code):
            # Simple hex dump
            chunk = code[i:min(i+16, len(code))]
            instructions.append({
                'address': address + i,
                'mnemonic': 'db',
                'op_str': ', '.join(f'0x{b:02x}' for b in chunk),
                'bytes': chunk.hex(),
                'size': len(chunk),
            })
            i += len(chunk)
        return instructions
    
    def disassemble_function(self, code: bytes, address: int = 0) -> List[Dict[str, Any]]:
        """
        Disassemble a function.
        
        Args:
            code: Function code bytes
            address: Function base address
            
        Returns:
            List of instructions
        """
        return self.disassemble(code, address)
    
    def find_pattern(self, code: bytes, pattern: bytes) -> List[int]:
        """
        Find byte pattern in code.
        
        Args:
            code: Code to search
            pattern: Pattern to find
            
        Returns:
            List of offsets where pattern was found
        """
        offsets = []
        start = 0
        while True:
            offset = code.find(pattern, start)
            if offset == -1:
                break
            offsets.append(offset)
            start = offset + 1
        return offsets

