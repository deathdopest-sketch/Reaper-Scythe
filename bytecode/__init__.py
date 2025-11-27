"""
REAPER Bytecode System

This module provides the main interface for the REAPER bytecode system,
including the instruction set, virtual machine, and compiler.
"""

from typing import Any
from .instructions import OpCode, BytecodeInstruction, BytecodeProgram, INSTRUCTION_DOCS
from .vm import ReaperVM, VMStack, VMFrame
from .compiler import BytecodeCompiler

__version__ = "0.1.0"
__author__ = "Reaper Security Team"

__all__ = [
    # Instruction set
    'OpCode', 'BytecodeInstruction', 'BytecodeProgram', 'INSTRUCTION_DOCS',
    
    # Virtual machine
    'ReaperVM', 'VMStack', 'VMFrame',
    
    # Compiler
    'BytecodeCompiler',
    
    # Main functions
    'compile_to_bytecode', 'execute_bytecode', 'create_vm'
]


def compile_to_bytecode(ast) -> BytecodeProgram:
    """
    Compile AST to bytecode program.
    
    Args:
        ast: ProgramNode from the parser
        
    Returns:
        BytecodeProgram ready for execution
    """
    compiler = BytecodeCompiler()
    return compiler.compile(ast)


def execute_bytecode(program: BytecodeProgram, 
                    max_stack_size: int = 10000,
                    execution_timeout: float = 30.0) -> Any:
    """
    Execute a bytecode program.
    
    Args:
        program: BytecodeProgram to execute
        max_stack_size: Maximum stack size
        execution_timeout: Execution timeout in seconds
        
    Returns:
        Result of program execution
    """
    vm = create_vm(max_stack_size=max_stack_size, execution_timeout=execution_timeout)
    vm.load_program(program)
    return vm.execute()


def create_vm(max_stack_size: int = 10000,
              max_call_stack_size: int = 1000,
              execution_timeout: float = 30.0,
              rate_limit_ops_per_second: float = 1000.0,
              rate_limit_burst: int = 100) -> ReaperVM:
    """
    Create a new REAPER virtual machine.
    
    Args:
        max_stack_size: Maximum stack size
        max_call_stack_size: Maximum call stack size
        execution_timeout: Execution timeout in seconds
        rate_limit_ops_per_second: Rate limit for operations per second
        rate_limit_burst: Rate limit burst capacity
        
    Returns:
        Configured ReaperVM instance
    """
    return ReaperVM(
        max_stack_size=max_stack_size,
        max_call_stack_size=max_call_stack_size,
        execution_timeout=execution_timeout,
        rate_limit_ops_per_second=rate_limit_ops_per_second,
        rate_limit_burst=rate_limit_burst
    )


# Example usage and testing
if __name__ == "__main__":
    # Example: Create a simple bytecode program
    program = BytecodeProgram()
    
    # Add some constants
    hello_const = program.add_constant("Hello, Reaper VM!")
    num_const = program.add_constant(42)
    
    # Add instructions
    program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, hello_const))
    program.add_instruction(BytecodeInstruction(OpCode.CALL_BUILTIN, "harvest"))
    program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, num_const))
    program.add_instruction(BytecodeInstruction(OpCode.CALL_BUILTIN, "harvest"))
    
    # Execute the program
    vm = create_vm()
    vm.load_program(program)
    result = vm.execute()
    
    print(f"Program executed successfully. Result: {result}")
