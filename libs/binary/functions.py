"""
Function Analysis Module

Provides utilities for analyzing functions in binaries.
"""

from typing import List, Dict, Optional, Any
from .disassembler import Disassembler
from .parser import BinaryParser


class FunctionAnalyzer:
    """
    Analyzer for binary functions.
    """
    
    def __init__(self, binary_path: str):
        """
        Initialize function analyzer.
        
        Args:
            binary_path: Path to binary file
        """
        self.binary_path = binary_path
        self.parser = BinaryParser(binary_path)
        self.binary_info = self.parser.parse()
        self.disassembler = Disassembler(
            arch=self.binary_info['header'].get('arch', 'x86_64')
        )
    
    def analyze_function(self, address: int, size: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze a function at a given address.
        
        Args:
            address: Function address
            size: Function size (optional)
            
        Returns:
            Function analysis results
        """
        # Read function code
        with open(self.binary_path, 'rb') as f:
            f.seek(address)
            if size:
                code = f.read(size)
            else:
                # Try to determine function size (simplified)
                code = f.read(1024)  # Read up to 1KB
        
        # Disassemble
        instructions = self.disassembler.disassemble(code, address)
        
        # Analyze
        analysis = {
            'address': address,
            'size': len(code),
            'instructions': instructions,
            'instruction_count': len(instructions),
            'calls': self._find_calls(instructions),
            'branches': self._find_branches(instructions),
            'complexity': self._calculate_complexity(instructions),
        }
        
        return analysis
    
    def _find_calls(self, instructions: List[Dict[str, Any]]) -> List[int]:
        """Find function calls in instructions."""
        calls = []
        for insn in instructions:
            if 'call' in insn.get('mnemonic', '').lower():
                calls.append(insn['address'])
        return calls
    
    def _find_branches(self, instructions: List[Dict[str, Any]]) -> List[int]:
        """Find branch instructions."""
        branches = []
        branch_mnemonics = ['jmp', 'je', 'jne', 'jz', 'jnz', 'jl', 'jg', 'jle', 'jge']
        for insn in instructions:
            if any(m in insn.get('mnemonic', '').lower() for m in branch_mnemonics):
                branches.append(insn['address'])
        return branches
    
    def _calculate_complexity(self, instructions: List[Dict[str, Any]]) -> int:
        """Calculate function complexity (simplified cyclomatic complexity)."""
        complexity = 1  # Base complexity
        for insn in instructions:
            mnemonic = insn.get('mnemonic', '').lower()
            if any(m in mnemonic for m in ['jmp', 'je', 'jne', 'jz', 'jnz', 'call']):
                complexity += 1
        return complexity

