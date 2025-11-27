"""
Control Flow Graph Module

Provides utilities for generating control flow graphs from binaries.
"""

from typing import List, Dict, Optional, Set, Tuple
from .disassembler import Disassembler
from .functions import FunctionAnalyzer


class ControlFlowGraph:
    """
    Control flow graph generator.
    """
    
    def __init__(self, binary_path: str, function_address: int):
        """
        Initialize CFG generator.
        
        Args:
            binary_path: Path to binary file
            function_address: Address of function to analyze
        """
        self.binary_path = binary_path
        self.function_address = function_address
        self.analyzer = FunctionAnalyzer(binary_path)
        self.function_analysis = self.analyzer.analyze_function(function_address)
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Tuple[int, int]] = []
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate control flow graph.
        
        Returns:
            CFG representation
        """
        instructions = self.function_analysis['instructions']
        
        # Create nodes for each basic block
        basic_blocks = self._identify_basic_blocks(instructions)
        
        # Create edges between basic blocks
        edges = self._create_edges(basic_blocks, instructions)
        
        return {
            'function_address': self.function_address,
            'basic_blocks': basic_blocks,
            'edges': edges,
            'entry': basic_blocks[0]['start'] if basic_blocks else None,
            'exit': basic_blocks[-1]['end'] if basic_blocks else None,
        }
    
    def _identify_basic_blocks(self, instructions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify basic blocks in function.
        
        Args:
            instructions: List of instructions
            
        Returns:
            List of basic blocks
        """
        if not instructions:
            return []
        
        basic_blocks = []
        current_block_start = instructions[0]['address']
        current_instructions = [instructions[0]]
        
        for i in range(1, len(instructions)):
            prev_insn = instructions[i-1]
            curr_insn = instructions[i]
            
            # Check if previous instruction is a branch or call
            mnemonic = prev_insn.get('mnemonic', '').lower()
            is_branch = any(m in mnemonic for m in ['jmp', 'je', 'jne', 'jz', 'jnz', 'ret', 'call'])
            
            if is_branch:
                # End current block
                basic_blocks.append({
                    'start': current_block_start,
                    'end': prev_insn['address'] + prev_insn['size'],
                    'instructions': current_instructions,
                })
                # Start new block
                current_block_start = curr_insn['address']
                current_instructions = [curr_insn]
            else:
                current_instructions.append(curr_insn)
        
        # Add final block
        if current_instructions:
            basic_blocks.append({
                'start': current_block_start,
                'end': instructions[-1]['address'] + instructions[-1]['size'],
                'instructions': current_instructions,
            })
        
        return basic_blocks
    
    def _create_edges(self, basic_blocks: List[Dict[str, Any]], 
                     instructions: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
        """
        Create edges between basic blocks.
        
        Args:
            basic_blocks: List of basic blocks
            instructions: All instructions
            
        Returns:
            List of edges (from_block_index, to_block_index)
        """
        edges = []
        instruction_map = {insn['address']: insn for insn in instructions}
        
        for i, block in enumerate(basic_blocks):
            # Get last instruction in block
            last_insn = block['instructions'][-1]
            mnemonic = last_insn.get('mnemonic', '').lower()
            
            # Check for branches
            if 'jmp' in mnemonic:
                # Unconditional jump - find target
                target = self._extract_jump_target(last_insn)
                if target:
                    target_block = self._find_block_for_address(basic_blocks, target)
                    if target_block is not None:
                        edges.append((i, target_block))
            elif any(m in mnemonic for m in ['je', 'jne', 'jz', 'jnz']):
                # Conditional jump - two edges (taken and not taken)
                target = self._extract_jump_target(last_insn)
                if target:
                    target_block = self._find_block_for_address(basic_blocks, target)
                    if target_block is not None:
                        edges.append((i, target_block))
                # Fall-through edge
                if i + 1 < len(basic_blocks):
                    edges.append((i, i + 1))
            elif 'ret' in mnemonic:
                # Return - no outgoing edges
                pass
            else:
                # Fall-through to next block
                if i + 1 < len(basic_blocks):
                    edges.append((i, i + 1))
        
        return edges
    
    def _extract_jump_target(self, instruction: Dict[str, Any]) -> Optional[int]:
        """Extract jump target from instruction."""
        # Simplified - would parse operand string
        return None
    
    def _find_block_for_address(self, basic_blocks: List[Dict[str, Any]], address: int) -> Optional[int]:
        """Find basic block index containing address."""
        for i, block in enumerate(basic_blocks):
            if block['start'] <= address < block['end']:
                return i
        return None

