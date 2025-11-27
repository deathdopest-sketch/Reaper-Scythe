"""
REAPER Stack-Based Virtual Machine

This module implements a stack-based virtual machine for executing
REAPER bytecode with enhanced security features and performance optimizations.
"""

import sys
import time
from typing import Any, Dict, List, Optional, Callable
from .instructions import OpCode, BytecodeInstruction, BytecodeProgram
from core.reaper_error import (
    ReaperRuntimeError, ReaperTypeError, ReaperMemoryError,
    ReaperIndexError, ReaperKeyError, ReaperZeroDivisionError
)
from core.secure_string import SecureString
from core.rate_limiter import TokenBucket


class VMStack:
    """Stack implementation for the VM."""
    
    def __init__(self, max_size: int = 10000):
        self._stack: List[Any] = []
        self.max_size = max_size
    
    def push(self, value: Any) -> None:
        """Push value onto stack."""
        if len(self._stack) >= self.max_size:
            raise ReaperMemoryError(f"Stack overflow: maximum size {self.max_size} exceeded")
        self._stack.append(value)
    
    def pop(self) -> Any:
        """Pop value from stack."""
        if not self._stack:
            raise ReaperRuntimeError("Stack underflow: cannot pop from empty stack")
        return self._stack.pop()
    
    def peek(self, index: int = 0) -> Any:
        """Peek at value on stack without removing it."""
        if index >= len(self._stack):
            raise ReaperRuntimeError(f"Stack index {index} out of bounds")
        return self._stack[-(index + 1)]
    
    def dup(self) -> None:
        """Duplicate top of stack."""
        if not self._stack:
            raise ReaperRuntimeError("Stack underflow: cannot duplicate empty stack")
        self.push(self._stack[-1])
    
    def swap(self) -> None:
        """Swap top two elements on stack."""
        if len(self._stack) < 2:
            raise ReaperRuntimeError("Stack underflow: need at least 2 elements to swap")
        self._stack[-1], self._stack[-2] = self._stack[-2], self._stack[-1]
    
    def size(self) -> int:
        """Get current stack size."""
        return len(self._stack)
    
    def clear(self) -> None:
        """Clear the stack."""
        self._stack.clear()
    
    def __len__(self) -> int:
        return len(self._stack)
    
    def __repr__(self) -> str:
        return f"VMStack(size={len(self._stack)}, max={self.max_size})"


class VMFrame:
    """Stack frame for function calls."""
    
    def __init__(self, return_address: int, locals: Optional[Dict[str, Any]] = None):
        self.return_address = return_address
        self.locals = locals or {}
    
    def __repr__(self) -> str:
        return f"VMFrame(return={self.return_address}, locals={len(self.locals)})"


class ReaperVM:
    """Stack-based virtual machine for REAPER bytecode."""
    
    def __init__(self, 
                 max_stack_size: int = 10000,
                 max_call_stack_size: int = 1000,
                 execution_timeout: float = 30.0,
                 rate_limit_ops_per_second: float = 1000.0,
                 rate_limit_burst: int = 100):
        """Initialize the REAPER VM."""
        self.stack = VMStack(max_stack_size)
        self.call_stack: List[VMFrame] = []
        self.max_call_stack_size = max_call_stack_size
        
        # Execution state
        self.pc = 0  # Program counter
        self.program: Optional[BytecodeProgram] = None
        self.globals: Dict[str, Any] = {}
        self.builtins: Dict[str, Callable] = {}
        
        # Resource limits
        self.execution_timeout = execution_timeout
        self.start_time = 0
        self.instruction_count = 0
        self.max_instructions = 1000000
        
        # Rate limiting
        self.rate_limiter = TokenBucket(rate_limit_ops_per_second, rate_limit_burst)
        
        # Security features
        self.secure_strings: List[SecureString] = []
        
        # Initialize built-in functions
        self._initialize_builtins()
    
    def _initialize_builtins(self) -> None:
        """Initialize built-in functions."""
        self.builtins = {
            "harvest": self._builtin_harvest,
            "curse": self._builtin_curse,
            "haunt": self._builtin_haunt,
            "infect": self._builtin_infect,
            "raise": self._builtin_raise,
            "reap": self._builtin_reap,
            "flee": self._builtin_flee,
            "persist": self._builtin_persist,
            "rest": self._builtin_rest,
            "lesser": self._builtin_lesser,
            "greater": self._builtin_greater,
            "risen": self._builtin_risen,
            "dead": self._builtin_dead,
            "void": self._builtin_void,
        }
    
    def load_program(self, program: BytecodeProgram) -> None:
        """Load a bytecode program into the VM."""
        self.program = program
        # Merge program globals with existing VM globals (preserves ritual_args and other runtime globals)
        self.globals.update(program.globals)
        self.pc = 0
        self.stack.clear()
        self.call_stack.clear()
        self.instruction_count = 0
    
    def execute(self) -> Any:
        """Execute the loaded program."""
        if not self.program:
            raise ReaperRuntimeError("No program loaded")
        
        self.start_time = time.time()
        
        try:
            while self.pc < len(self.program.instructions):
                self._check_timeout()
                # self._check_rate_limit()  # Disabled for now
                
                instruction = self.program.instructions[self.pc]
                self._execute_instruction(instruction)
                
                self.pc += 1
                self.instruction_count += 1
                
                if self.instruction_count >= self.max_instructions:
                    raise ReaperRuntimeError("Maximum instruction count exceeded")
            
            # Return top of stack if anything remains
            if self.stack.size() > 0:
                return self.stack.pop()
            return None
            
        finally:
            self._cleanup_secure_strings()
    
    def _execute_instruction(self, instruction: BytecodeInstruction) -> None:
        """Execute a single instruction."""
        opcode = instruction.opcode
        operand = instruction.operand
        
        try:
            if opcode == OpCode.PUSH_CONST:
                if operand is None:
                    raise ReaperRuntimeError("PUSH_CONST requires operand")
                const_index = operand
                if const_index >= len(self.program.constants):
                    raise ReaperRuntimeError(f"Constant index {const_index} out of bounds")
                self.stack.push(self.program.constants[const_index])
                
            elif opcode == OpCode.PUSH_LOCAL:
                if operand is None:
                    raise ReaperRuntimeError("PUSH_LOCAL requires operand")
                var_name = operand
                if not self.call_stack:
                    raise ReaperRuntimeError("No active function frame")
                frame = self.call_stack[-1]
                if var_name not in frame.locals:
                    raise ReaperRuntimeError(f"Local variable '{var_name}' not found")
                self.stack.push(frame.locals[var_name])
                
            elif opcode == OpCode.PUSH_GLOBAL:
                if operand is None:
                    raise ReaperRuntimeError("PUSH_GLOBAL requires operand")
                var_name = operand
                if var_name not in self.globals:
                    raise ReaperRuntimeError(f"Global variable '{var_name}' not found")
                self.stack.push(self.globals[var_name])
                
            elif opcode == OpCode.POP:
                self.stack.pop()
                
            elif opcode == OpCode.DUP:
                self.stack.dup()
                
            elif opcode == OpCode.SWAP:
                self.stack.swap()
                
            elif opcode == OpCode.ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._add(a, b))
                
            elif opcode == OpCode.SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._sub(a, b))
                
            elif opcode == OpCode.MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._mul(a, b))
                
            elif opcode == OpCode.DIV:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._div(a, b))
                
            elif opcode == OpCode.MOD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._mod(a, b))
                
            elif opcode == OpCode.NEG:
                a = self.stack.pop()
                self.stack.push(self._neg(a))
                
            elif opcode == OpCode.BIT_AND:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._bit_and(a, b))
                
            elif opcode == OpCode.BIT_OR:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._bit_or(a, b))
                
            elif opcode == OpCode.BIT_XOR:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._bit_xor(a, b))
                
            elif opcode == OpCode.BIT_NOT:
                a = self.stack.pop()
                self.stack.push(self._bit_not(a))
                
            elif opcode == OpCode.EQ:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._eq(a, b))
                
            elif opcode == OpCode.NE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._ne(a, b))
                
            elif opcode == OpCode.LT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._lt(a, b))
                
            elif opcode == OpCode.LE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._le(a, b))
                
            elif opcode == OpCode.GT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._gt(a, b))
                
            elif opcode == OpCode.GE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._ge(a, b))
                
            elif opcode == OpCode.LOG_AND:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._log_and(a, b))
                
            elif opcode == OpCode.LOG_OR:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(self._log_or(a, b))
                
            elif opcode == OpCode.LOG_NOT:
                a = self.stack.pop()
                self.stack.push(self._log_not(a))
                
            elif opcode == OpCode.JMP:
                if operand is None:
                    raise ReaperRuntimeError("JMP requires operand")
                self.pc = operand - 1  # -1 because pc will be incremented
                
            elif opcode == OpCode.JMP_IF:
                if operand is None:
                    raise ReaperRuntimeError("JMP_IF requires operand")
                if self.stack.pop():
                    self.pc = operand - 1  # -1 because pc will be incremented
                
            elif opcode == OpCode.JMP_IF_NOT:
                if operand is None:
                    raise ReaperRuntimeError("JMP_IF_NOT requires operand")
                if not self.stack.pop():
                    self.pc = operand - 1  # -1 because pc will be incremented
                
            elif opcode == OpCode.CALL:
                # Get function name from operand
                if not operand or not isinstance(operand, str):
                    raise ReaperRuntimeError("CALL requires function name as operand")
                
                func_name = operand
                
                # Check if it's a bytecode function
                if func_name in self.program.functions:
                    # Bytecode function - get metadata
                    func_start = self.program.functions[func_name]
                    func_metadata = self.program.function_metadata.get(func_name, {})
                    param_names = func_metadata.get('param_names', [])
                    param_count = func_metadata.get('param_count', 0)
                    
                    # Check call stack size
                    if len(self.call_stack) >= self.max_call_stack_size:
                        raise ReaperMemoryError(f"Call stack overflow: maximum depth {self.max_call_stack_size} exceeded")
                    
                    # Pop arguments from stack (they were pushed in reverse order)
                    # So we need to reverse them to get correct order
                    args = []
                    for _ in range(param_count):
                        if self.stack.size() == 0:
                            raise ReaperRuntimeError(f"Function '{func_name}' requires {param_count} arguments, but stack is empty")
                        args.insert(0, self.stack.pop())  # Insert at beginning to reverse order
                    
                    # Create new frame with return address
                    return_address = self.pc + 1  # Return to next instruction
                    frame = VMFrame(return_address, {})
                    
                    # Set up local variables for parameters
                    for i, param_name in enumerate(param_names):
                        if i < len(args):
                            frame.locals[param_name] = args[i]
                        else:
                            # Missing argument - will be handled by default values if any
                            # For now, set to None
                            frame.locals[param_name] = None
                    
                    # Push frame onto call stack
                    self.call_stack.append(frame)
                    
                    # Jump to function start
                    self.pc = func_start - 1  # -1 because pc will be incremented
                    
                elif func_name in self.globals:
                    # Check if it's a built-in function marker
                    func = self.globals[func_name]
                    if isinstance(func, str) and func.startswith("<builtin:"):
                        builtin_name = func[9:-1]  # Extract name from "<builtin:name>"
                        if builtin_name in self.builtins:
                            # Built-in function - pop arguments (assume no args for now)
                            result = self.builtins[builtin_name]()
                            self.stack.push(result)
                        else:
                            raise ReaperRuntimeError(f"Built-in function '{builtin_name}' not found")
                    else:
                        raise ReaperRuntimeError(
                            f"Function '{func_name}' is not a bytecode function. "
                            f"User-defined functions must be compiled to bytecode."
                        )
                else:
                    raise ReaperRuntimeError(f"Function '{func_name}' not found")
                
            elif opcode == OpCode.RETURN:
                if not self.call_stack:
                    # Return from main program - end execution
                    self.pc = len(self.program.instructions)
                    return
                
                # Pop return value if present (top of stack)
                return_value = None
                if self.stack.size() > 0:
                    return_value = self.stack.pop()
                
                # Pop frame and restore PC
                frame = self.call_stack.pop()
                self.pc = frame.return_address - 1  # -1 because pc will be incremented
                
                # Push return value back onto stack for caller
                if return_value is not None:
                    self.stack.push(return_value)
                else:
                    # Implicit return None
                    self.stack.push(None)
                
            elif opcode == OpCode.CALL_BUILTIN:
                if operand is None:
                    raise ReaperRuntimeError("CALL_BUILTIN requires operand")
                func_name = operand
                if func_name not in self.builtins:
                    raise ReaperRuntimeError(f"Built-in function '{func_name}' not found")
                
                # Call built-in function (no arguments for now)
                result = self.builtins[func_name]()
                self.stack.push(result)
                
            elif opcode == OpCode.STORE_LOCAL:
                if operand is None:
                    raise ReaperRuntimeError("STORE_LOCAL requires operand")
                var_name = operand
                if not self.call_stack:
                    raise ReaperRuntimeError("No active function frame")
                
                value = self.stack.pop()
                frame = self.call_stack[-1]
                frame.locals[var_name] = value
                
            elif opcode == OpCode.STORE_GLOBAL:
                if operand is None:
                    raise ReaperRuntimeError("STORE_GLOBAL requires operand")
                var_name = operand
                value = self.stack.pop()
                self.globals[var_name] = value
                
            elif opcode == OpCode.ARRAY_NEW:
                if operand is None:
                    raise ReaperRuntimeError("ARRAY_NEW requires operand")
                size = operand
                if not isinstance(size, int) or size < 0:
                    raise ReaperTypeError("Array size must be non-negative integer")
                self.stack.push([None] * size)
                
            elif opcode == OpCode.ARRAY_GET:
                index = self.stack.pop()
                array = self.stack.pop()
                if not isinstance(array, list):
                    raise ReaperTypeError("Expected array for ARRAY_GET")
                if not isinstance(index, int):
                    raise ReaperTypeError("Expected integer index for ARRAY_GET")
                if index < 0 or index >= len(array):
                    raise ReaperIndexError(f"Array index {index} out of bounds")
                self.stack.push(array[index])
                
            elif opcode == OpCode.ARRAY_SET:
                value = self.stack.pop()
                index = self.stack.pop()
                array = self.stack.pop()
                if not isinstance(array, list):
                    raise ReaperTypeError("Expected array for ARRAY_SET")
                if not isinstance(index, int):
                    raise ReaperTypeError("Expected integer index for ARRAY_SET")
                if index < 0 or index >= len(array):
                    raise ReaperIndexError(f"Array index {index} out of bounds")
                array[index] = value
                self.stack.push(array)
                
            elif opcode == OpCode.ARRAY_LEN:
                array = self.stack.pop()
                if not isinstance(array, list):
                    raise ReaperTypeError("Expected array for ARRAY_LEN")
                self.stack.push(len(array))
                
            elif opcode == OpCode.DICT_NEW:
                self.stack.push({})
                
            elif opcode == OpCode.DICT_GET:
                key = self.stack.pop()
                dictionary = self.stack.pop()
                if not isinstance(dictionary, dict):
                    raise ReaperTypeError("Expected dictionary for DICT_GET")
                if key not in dictionary:
                    raise ReaperKeyError(f"Key '{key}' not found in dictionary")
                self.stack.push(dictionary[key])
                
            elif opcode == OpCode.DICT_SET:
                value = self.stack.pop()
                key = self.stack.pop()
                dictionary = self.stack.pop()
                if not isinstance(dictionary, dict):
                    raise ReaperTypeError("Expected dictionary for DICT_SET")
                dictionary[key] = value
                self.stack.push(dictionary)
                
            elif opcode == OpCode.DICT_HAS:
                key = self.stack.pop()
                dictionary = self.stack.pop()
                if not isinstance(dictionary, dict):
                    raise ReaperTypeError("Expected dictionary for DICT_HAS")
                self.stack.push(key in dictionary)
                
            elif opcode == OpCode.STR_CONCAT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.push(str(a) + str(b))
                
            elif opcode == OpCode.STR_LEN:
                string = self.stack.pop()
                self.stack.push(len(str(string)))
                
            elif opcode == OpCode.SECURE_STRING:
                string = self.stack.pop()
                secure_string = SecureString.from_plain(str(string))
                self.secure_strings.append(secure_string)
                self.stack.push(secure_string)
                
            elif opcode == OpCode.CLEAR_MEMORY:
                self._cleanup_secure_strings()
                
            elif opcode == OpCode.RATE_LIMIT:
                if not self.rate_limiter.try_acquire(1.0):
                    raise ReaperRuntimeError("Rate limit exceeded")
                
            elif opcode == OpCode.HALT:
                self.pc = len(self.program.instructions)  # End execution
                
            else:
                raise ReaperRuntimeError(f"Unknown opcode: {opcode}")
                
        except Exception as e:
            raise ReaperRuntimeError(f"Error executing {opcode.name} at PC {self.pc}: {e}")
    
    def _check_timeout(self) -> None:
        """Check execution timeout."""
        if time.time() - self.start_time > self.execution_timeout:
            raise ReaperRuntimeError("Execution timeout exceeded")
    
    def _check_rate_limit(self) -> None:
        """Check rate limiting."""
        # Only check rate limiting every 100 instructions to avoid overhead
        if self.instruction_count % 100 == 0:
            if not self.rate_limiter.try_acquire(100.0):
                raise ReaperRuntimeError("Rate limit exceeded")
    
    def _cleanup_secure_strings(self) -> None:
        """Clean up secure strings."""
        for secure_string in self.secure_strings:
            try:
                secure_string.clear()
            except Exception:
                pass
        self.secure_strings.clear()
    
    # Arithmetic operations
    def _add(self, a: Any, b: Any) -> Any:
        """Addition operation."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a + b
        elif isinstance(a, str) or isinstance(b, str):
            return str(a) + str(b)
        elif isinstance(a, list) and isinstance(b, list):
            return a + b
        else:
            raise ReaperTypeError(f"Cannot add {type(a)} and {type(b)}")
    
    def _sub(self, a: Any, b: Any) -> Any:
        """Subtraction operation."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a - b
        else:
            raise ReaperTypeError(f"Cannot subtract {type(a)} and {type(b)}")
    
    def _mul(self, a: Any, b: Any) -> Any:
        """Multiplication operation."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a * b
        elif isinstance(a, str) and isinstance(b, int):
            return a * b
        elif isinstance(a, int) and isinstance(b, str):
            return b * a
        else:
            raise ReaperTypeError(f"Cannot multiply {type(a)} and {type(b)}")
    
    def _div(self, a: Any, b: Any) -> Any:
        """Division operation."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if b == 0:
                raise ReaperZeroDivisionError("Division by zero")
            return a / b
        else:
            raise ReaperTypeError(f"Cannot divide {type(a)} and {type(b)}")
    
    def _mod(self, a: Any, b: Any) -> Any:
        """Modulo operation."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if b == 0:
                raise ReaperZeroDivisionError("Modulo by zero")
            return a % b
        else:
            raise ReaperTypeError(f"Cannot modulo {type(a)} and {type(b)}")
    
    def _neg(self, a: Any) -> Any:
        """Negation operation."""
        if isinstance(a, (int, float)):
            return -a
        else:
            raise ReaperTypeError(f"Cannot negate {type(a)}")
    
    # Bitwise operations
    def _bit_and(self, a: Any, b: Any) -> Any:
        """Bitwise AND operation."""
        if isinstance(a, int) and isinstance(b, int):
            return a & b
        else:
            raise ReaperTypeError(f"Cannot bitwise AND {type(a)} and {type(b)}")
    
    def _bit_or(self, a: Any, b: Any) -> Any:
        """Bitwise OR operation."""
        if isinstance(a, int) and isinstance(b, int):
            return a | b
        else:
            raise ReaperTypeError(f"Cannot bitwise OR {type(a)} and {type(b)}")
    
    def _bit_xor(self, a: Any, b: Any) -> Any:
        """Bitwise XOR operation."""
        if isinstance(a, int) and isinstance(b, int):
            return a ^ b
        else:
            raise ReaperTypeError(f"Cannot bitwise XOR {type(a)} and {type(b)}")
    
    def _bit_not(self, a: Any) -> Any:
        """Bitwise NOT operation."""
        if isinstance(a, int):
            return ~a & 0xFFFFFFFF  # 32-bit mask
        else:
            raise ReaperTypeError(f"Cannot bitwise NOT {type(a)}")
    
    # Comparison operations
    def _eq(self, a: Any, b: Any) -> bool:
        """Equality comparison."""
        return a == b
    
    def _ne(self, a: Any, b: Any) -> bool:
        """Not equal comparison."""
        return a != b
    
    def _lt(self, a: Any, b: Any) -> bool:
        """Less than comparison."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a < b
        elif isinstance(a, str) and isinstance(b, str):
            return a < b
        else:
            raise ReaperTypeError(f"Cannot compare {type(a)} < {type(b)}")
    
    def _le(self, a: Any, b: Any) -> bool:
        """Less than or equal comparison."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a <= b
        elif isinstance(a, str) and isinstance(b, str):
            return a <= b
        else:
            raise ReaperTypeError(f"Cannot compare {type(a)} <= {type(b)}")
    
    def _gt(self, a: Any, b: Any) -> bool:
        """Greater than comparison."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a > b
        elif isinstance(a, str) and isinstance(b, str):
            return a > b
        else:
            raise ReaperTypeError(f"Cannot compare {type(a)} > {type(b)}")
    
    def _ge(self, a: Any, b: Any) -> bool:
        """Greater than or equal comparison."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a >= b
        elif isinstance(a, str) and isinstance(b, str):
            return a >= b
        else:
            raise ReaperTypeError(f"Cannot compare {type(a)} >= {type(b)}")
    
    # Logical operations
    def _log_and(self, a: Any, b: Any) -> bool:
        """Logical AND operation."""
        return bool(a) and bool(b)
    
    def _log_or(self, a: Any, b: Any) -> bool:
        """Logical OR operation."""
        return bool(a) or bool(b)
    
    def _log_not(self, a: Any) -> bool:
        """Logical NOT operation."""
        return not bool(a)
    
    # Built-in functions
    def _builtin_harvest(self) -> None:
        """Built-in harvest function (print)."""
        if self.stack.size() > 0:
            value = self.stack.pop()
            print(value)
        return None
    
    def _builtin_curse(self) -> Any:
        """Built-in curse function (length)."""
        if self.stack.size() == 0:
            raise ReaperRuntimeError("curse() requires an argument")
        value = self.stack.pop()
        if isinstance(value, (str, list, dict)):
            return len(value)
        else:
            raise ReaperTypeError(f"curse() not supported for {type(value)}")
    
    def _builtin_haunt(self) -> bool:
        """Built-in haunt function (contains)."""
        if self.stack.size() < 2:
            raise ReaperRuntimeError("haunt() requires two arguments")
        key = self.stack.pop()
        container = self.stack.pop()
        if isinstance(container, (list, dict, str)):
            return key in container
        else:
            raise ReaperTypeError(f"haunt() not supported for {type(container)}")
    
    def _builtin_infect(self) -> Any:
        """Built-in infect function (input)."""
        return input()
    
    def _builtin_raise(self) -> Any:
        """Built-in raise function (random)."""
        import random
        return random.random()
    
    def _builtin_reap(self) -> Any:
        """Built-in reap function (return top of stack)."""
        if self.stack.size() > 0:
            return self.stack.pop()
        return None
    
    def _builtin_flee(self) -> None:
        """Built-in flee function (break)."""
        raise ReaperRuntimeError("flee() not implemented in VM")
    
    def _builtin_persist(self) -> None:
        """Built-in persist function (continue)."""
        raise ReaperRuntimeError("persist() not implemented in VM")
    
    def _builtin_rest(self) -> None:
        """Built-in rest function (sleep)."""
        import time
        if self.stack.size() > 0:
            seconds = self.stack.pop()
            if isinstance(seconds, (int, float)):
                time.sleep(seconds)
            else:
                raise ReaperTypeError("rest() requires numeric argument")
    
    def _builtin_lesser(self) -> Any:
        """Built-in lesser function (min)."""
        if self.stack.size() < 2:
            raise ReaperRuntimeError("lesser() requires two arguments")
        b = self.stack.pop()
        a = self.stack.pop()
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return min(a, b)
        else:
            raise ReaperTypeError(f"lesser() not supported for {type(a)} and {type(b)}")
    
    def _builtin_greater(self) -> Any:
        """Built-in greater function (max)."""
        if self.stack.size() < 2:
            raise ReaperRuntimeError("greater() requires two arguments")
        b = self.stack.pop()
        a = self.stack.pop()
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return max(a, b)
        else:
            raise ReaperTypeError(f"greater() not supported for {type(a)} and {type(b)}")
    
    def _builtin_risen(self) -> int:
        """Built-in risen function (1)."""
        return 1
    
    def _builtin_dead(self) -> int:
        """Built-in dead function (0)."""
        return 0
    
    def _builtin_void(self) -> None:
        """Built-in void function (None)."""
        return None
