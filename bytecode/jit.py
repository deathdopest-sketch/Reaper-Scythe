#!/usr/bin/env python3
"""
REAPER JIT Compilation System

This module provides Just-In-Time compilation capabilities for REAPER bytecode,
including hot path detection, profile-guided optimization, and native code generation.
"""

import time
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from collections import defaultdict
from .instructions import OpCode, BytecodeInstruction, BytecodeProgram
from core.reaper_error import ReaperRuntimeError


class ExecutionProfile:
    """Tracks execution statistics for JIT optimization."""
    
    def __init__(self):
        self.instruction_counts: Dict[int, int] = defaultdict(int)  # PC -> count
        self.edge_counts: Dict[Tuple[int, int], int] = defaultdict(int)  # (from, to) -> count
        self.loop_entries: Dict[int, int] = defaultdict(int)  # PC -> entry count
        self.function_calls: Dict[str, int] = defaultdict(int)  # function name -> call count
        self.hot_paths: List[Tuple[List[int], int]] = []  # (path, count)
        self.total_instructions = 0
    
    def record_instruction(self, pc: int) -> None:
        """Record execution of an instruction at PC."""
        self.instruction_counts[pc] += 1
        self.total_instructions += 1
    
    def record_edge(self, from_pc: int, to_pc: int) -> None:
        """Record a control flow edge."""
        self.edge_counts[(from_pc, to_pc)] += 1
    
    def record_loop_entry(self, pc: int) -> None:
        """Record entry into a loop."""
        self.loop_entries[pc] += 1
    
    def record_function_call(self, function_name: str) -> None:
        """Record a function call."""
        self.function_calls[function_name] += 1
    
    def get_hot_instructions(self, threshold: float = 0.1) -> Set[int]:
        """
        Get instructions that are executed frequently.
        
        Args:
            threshold: Minimum fraction of total instructions (0.0-1.0)
            
        Returns:
            Set of PC values for hot instructions
        """
        if self.total_instructions == 0:
            return set()
        
        hot = set()
        min_count = int(self.total_instructions * threshold)
        
        for pc, count in self.instruction_counts.items():
            if count >= min_count:
                hot.add(pc)
        
        return hot
    
    def get_hot_loops(self, threshold: int = 100) -> List[int]:
        """
        Get frequently executed loops.
        
        Args:
            threshold: Minimum entry count
            
        Returns:
            List of PC values for loop entry points
        """
        return [pc for pc, count in self.loop_entries.items() if count >= threshold]
    
    def get_hot_functions(self, threshold: int = 10) -> List[str]:
        """
        Get frequently called functions.
        
        Args:
            threshold: Minimum call count
            
        Returns:
            List of function names
        """
        return [name for name, count in self.function_calls.items() if count >= threshold]
    
    def analyze_hot_paths(self, max_paths: int = 10) -> List[Tuple[List[int], int]]:
        """
        Analyze and return the hottest execution paths.
        
        Args:
            max_paths: Maximum number of paths to return
            
        Returns:
            List of (path, count) tuples, sorted by count
        """
        # Simple path analysis: find sequences of frequently executed instructions
        paths = []
        
        # Group instructions by execution frequency
        sorted_instructions = sorted(
            self.instruction_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Find sequences of hot instructions
        for i in range(min(max_paths, len(sorted_instructions))):
            pc, count = sorted_instructions[i]
            # Check for edges from this instruction
            outgoing_edges = [
                (from_pc, to_pc, edge_count)
                for (from_pc, to_pc), edge_count in self.edge_counts.items()
                if from_pc == pc
            ]
            
            if outgoing_edges:
                # Build path
                path = [pc]
                for from_pc, to_pc, edge_count in sorted(outgoing_edges, key=lambda x: x[2], reverse=True)[:1]:
                    path.append(to_pc)
                paths.append((path, count))
        
        return sorted(paths, key=lambda x: x[1], reverse=True)[:max_paths]


class JITCompiler:
    """
    Just-In-Time compiler for REAPER bytecode.
    
    Provides hot path detection and optimization capabilities.
    """
    
    def __init__(self, enable_jit: bool = True, hot_threshold: float = 0.1):
        """
        Initialize JIT compiler.
        
        Args:
            enable_jit: Whether JIT compilation is enabled
            hot_threshold: Threshold for considering code "hot" (0.0-1.0)
        """
        self.enable_jit = enable_jit
        self.hot_threshold = hot_threshold
        self.profile = ExecutionProfile()
        self.compiled_functions: Dict[str, Callable] = {}
        self.optimized_segments: Dict[int, List[BytecodeInstruction]] = {}
    
    def record_execution(self, pc: int, instruction: BytecodeInstruction, 
                       next_pc: Optional[int] = None) -> None:
        """
        Record instruction execution for profiling.
        
        Args:
            pc: Program counter
            instruction: Instruction being executed
            next_pc: Next program counter (for edge tracking)
        """
        if not self.enable_jit:
            return
        
        self.profile.record_instruction(pc)
        
        if next_pc is not None and next_pc != pc + 1:
            self.profile.record_edge(pc, next_pc)
        
        # Detect loops (JMP backward)
        if instruction.opcode == OpCode.JMP and isinstance(instruction.operand, int):
            target = instruction.operand
            if target < pc:  # Backward jump = loop
                self.profile.record_loop_entry(target)
    
    def record_function_call(self, function_name: str) -> None:
        """Record a function call for profiling."""
        if self.enable_jit:
            self.profile.record_function_call(function_name)
    
    def should_compile(self, pc: int) -> bool:
        """
        Determine if code at PC should be JIT compiled.
        
        Args:
            pc: Program counter
            
        Returns:
            True if code should be compiled
        """
        if not self.enable_jit:
            return False
        
        hot_instructions = self.profile.get_hot_instructions(self.hot_threshold)
        return pc in hot_instructions
    
    def optimize_hot_loop(self, program: BytecodeProgram, loop_start: int, 
                         loop_end: int) -> List[BytecodeInstruction]:
        """
        Optimize a hot loop by generating optimized bytecode.
        
        Args:
            program: Original bytecode program
            loop_start: Starting PC of loop
            loop_end: Ending PC of loop
            
        Returns:
            Optimized instruction sequence
        """
        optimized = []
        instructions = program.instructions[loop_start:loop_end]
        
        # Simple optimizations:
        # 1. Remove redundant stack operations
        # 2. Combine consecutive arithmetic operations
        # 3. Optimize constant expressions
        
        i = 0
        while i < len(instructions):
            inst = instructions[i]
            
            # Combine PUSH_CONST + arithmetic operations
            if (inst.opcode == OpCode.PUSH_CONST and 
                i + 1 < len(instructions)):
                next_inst = instructions[i + 1]
                
                # PUSH_CONST + ADD/SUB/MUL/DIV can be optimized
                if next_inst.opcode in (OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV):
                    # Check if we can fold constants
                    if i + 2 < len(instructions):
                        third_inst = instructions[i + 2]
                        if third_inst.opcode == OpCode.PUSH_CONST:
                            # Constant folding opportunity
                            val1 = inst.operand
                            val2 = third_inst.operand
                            
                            if next_inst.opcode == OpCode.ADD:
                                result = val1 + val2
                            elif next_inst.opcode == OpCode.SUB:
                                result = val1 - val2
                            elif next_inst.opcode == OpCode.MUL:
                                result = val1 * val2
                            elif next_inst.opcode == OpCode.DIV:
                                if val2 == 0:
                                    optimized.append(inst)
                                    optimized.append(next_inst)
                                    optimized.append(third_inst)
                                    i += 3
                                    continue
                                result = val1 / val2
                            else:
                                result = None
                            
                            if result is not None:
                                optimized.append(BytecodeInstruction(OpCode.PUSH_CONST, result))
                                i += 3
                                continue
            
            optimized.append(inst)
            i += 1
        
        return optimized
    
    def compile_hot_function(self, program: BytecodeProgram, function_name: str,
                           function_start: int, function_end: int) -> Optional[Callable]:
        """
        Compile a hot function to native Python code.
        
        Args:
            program: Original bytecode program
            function_name: Name of function
            function_start: Starting PC of function
            function_end: Ending PC of function
            
        Returns:
            Compiled function or None if compilation failed
        """
        # For now, return None (full native compilation would require code generation)
        # This is a placeholder for future implementation
        return None
    
    def get_optimization_suggestions(self) -> Dict[str, Any]:
        """
        Get suggestions for code optimization based on profile.
        
        Returns:
            Dictionary with optimization suggestions
        """
        suggestions = {
            "hot_instructions": list(self.profile.get_hot_instructions(self.hot_threshold)),
            "hot_loops": self.profile.get_hot_loops(),
            "hot_functions": self.profile.get_hot_functions(),
            "total_instructions": self.profile.total_instructions,
            "hot_paths": self.profile.analyze_hot_paths(5),
        }
        
        return suggestions
    
    def reset_profile(self) -> None:
        """Reset execution profile."""
        self.profile = ExecutionProfile()
        self.compiled_functions.clear()
        self.optimized_segments.clear()


class ProfileGuidedOptimizer:
    """
    Profile-guided optimizer that uses execution profiles to optimize bytecode.
    """
    
    def __init__(self, jit_compiler: JITCompiler):
        """
        Initialize optimizer.
        
        Args:
            jit_compiler: JIT compiler instance
        """
        self.jit = jit_compiler
    
    def optimize_program(self, program: BytecodeProgram) -> BytecodeProgram:
        """
        Optimize a bytecode program based on execution profile.
        
        Args:
            program: Original program
            
        Returns:
            Optimized program
        """
        # Get hot paths
        hot_loops = self.jit.profile.get_hot_loops()
        hot_functions = self.jit.profile.get_hot_functions()
        
        # Create optimized program
        optimized = BytecodeProgram()
        optimized.constants = program.constants.copy()
        optimized.globals = program.globals.copy()
        optimized.function_metadata = program.function_metadata.copy()
        
        # For now, just copy instructions (full optimization would require more analysis)
        optimized.instructions = program.instructions.copy()
        
        # Mark optimized segments
        for loop_start in hot_loops:
            # Find loop end (simplified - would need proper CFG analysis)
            loop_end = min(loop_start + 100, len(program.instructions))
            optimized_segment = self.jit.optimize_hot_loop(program, loop_start, loop_end)
            if optimized_segment:
                self.jit.optimized_segments[loop_start] = optimized_segment
        
        return optimized

