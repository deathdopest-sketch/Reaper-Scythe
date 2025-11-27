"""
REAPER Bytecode Instruction Set

This module defines the custom bytecode instruction set for the REAPER language.
The bytecode is designed for a stack-based virtual machine optimized for
security operations and performance.
"""

from enum import IntEnum
from typing import Any, Dict, List, Optional, Union
import struct


class OpCode(IntEnum):
    """Bytecode operation codes for REAPER VM."""
    
    # Stack Operations
    PUSH_CONST = 0x01      # Push constant value onto stack
    PUSH_LOCAL = 0x02      # Push local variable onto stack
    PUSH_GLOBAL = 0x03     # Push global variable onto stack
    POP = 0x04             # Pop value from stack
    DUP = 0x05             # Duplicate top of stack
    SWAP = 0x06            # Swap top two stack elements
    
    # Arithmetic Operations
    ADD = 0x10             # Addition
    SUB = 0x11             # Subtraction
    MUL = 0x12             # Multiplication
    DIV = 0x13             # Division
    MOD = 0x14             # Modulo
    NEG = 0x15             # Negation
    INC = 0x16             # Increment
    DEC = 0x17             # Decrement
    
    # Bitwise Operations
    BIT_AND = 0x20         # Bitwise AND
    BIT_OR = 0x21          # Bitwise OR
    BIT_XOR = 0x22         # Bitwise XOR
    BIT_NOT = 0x23         # Bitwise NOT
    BIT_SHL = 0x24         # Left shift
    BIT_SHR = 0x25         # Right shift
    BIT_ROT = 0x26         # Rotate bits
    
    # Comparison Operations
    EQ = 0x30              # Equality
    NE = 0x31              # Not equal
    LT = 0x32              # Less than
    LE = 0x33              # Less than or equal
    GT = 0x34              # Greater than
    GE = 0x35              # Greater than or equal
    
    # Logical Operations
    LOG_AND = 0x40         # Logical AND
    LOG_OR = 0x41          # Logical OR
    LOG_NOT = 0x42         # Logical NOT
    
    # Control Flow
    JMP = 0x50             # Unconditional jump
    JMP_IF = 0x51          # Conditional jump (if true)
    JMP_IF_NOT = 0x52      # Conditional jump (if false)
    CALL = 0x53            # Call function
    RETURN = 0x54          # Return from function
    CALL_BUILTIN = 0x55    # Call built-in function
    
    # Variable Operations
    STORE_LOCAL = 0x60     # Store to local variable
    STORE_GLOBAL = 0x61    # Store to global variable
    LOAD_LOCAL = 0x62      # Load from local variable
    LOAD_GLOBAL = 0x63     # Load from global variable
    
    # Array Operations
    ARRAY_NEW = 0x70       # Create new array
    ARRAY_GET = 0x71       # Get array element
    ARRAY_SET = 0x72       # Set array element
    ARRAY_LEN = 0x73       # Get array length
    
    # Dictionary Operations
    DICT_NEW = 0x80        # Create new dictionary
    DICT_GET = 0x81        # Get dictionary value
    DICT_SET = 0x82        # Set dictionary value
    DICT_HAS = 0x83        # Check if key exists
    DICT_KEYS = 0x84       # Get dictionary keys
    
    # String Operations
    STR_CONCAT = 0x90      # String concatenation
    STR_LEN = 0x91         # String length
    STR_SUB = 0x92         # String substring
    
    # Type Operations
    TYPE_CHECK = 0xA0      # Type checking
    TYPE_CONVERT = 0xA1    # Type conversion
    
    # Security Operations
    SECURE_STRING = 0xB0   # Create secure string
    CLEAR_MEMORY = 0xB1    # Clear sensitive memory
    RATE_LIMIT = 0xB2      # Rate limiting check
    
    # Special Operations
    HALT = 0xFF            # Halt execution


class BytecodeInstruction:
    """Represents a single bytecode instruction."""
    
    def __init__(self, opcode: OpCode, operand: Optional[Any] = None, 
                 line: int = 0, column: int = 0):
        self.opcode = opcode
        self.operand = operand
        self.line = line
        self.column = column
    
    def __repr__(self) -> str:
        if self.operand is not None:
            return f"{self.opcode.name}({self.operand})"
        return f"{self.opcode.name}"
    
    def to_bytes(self) -> bytes:
        """Convert instruction to byte representation."""
        # Simple encoding: opcode (1 byte) + operand length (1 byte) + operand data
        opcode_bytes = struct.pack('B', self.opcode)
        
        if self.operand is None:
            return opcode_bytes + b'\x00'
        
        # Encode operand based on type
        if isinstance(self.operand, int):
            operand_bytes = struct.pack('>i', self.operand)  # 4-byte signed int
            return opcode_bytes + b'\x04' + operand_bytes
        elif isinstance(self.operand, float):
            operand_bytes = struct.pack('>d', self.operand)  # 8-byte double
            return opcode_bytes + b'\x08' + operand_bytes
        elif isinstance(self.operand, str):
            operand_bytes = self.operand.encode('utf-8')
            length_bytes = struct.pack('>H', len(operand_bytes))  # 2-byte length
            return opcode_bytes + b'\x02' + length_bytes + operand_bytes
        elif isinstance(self.operand, bool):
            operand_bytes = struct.pack('B', 1 if self.operand else 0)
            return opcode_bytes + b'\x01' + operand_bytes
        else:
            # For complex types, serialize as string
            operand_str = str(self.operand)
            operand_bytes = operand_str.encode('utf-8')
            length_bytes = struct.pack('>H', len(operand_bytes))
            return opcode_bytes + b'\x02' + length_bytes + operand_bytes
    
    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0) -> tuple['BytecodeInstruction', int]:
        """Create instruction from byte representation."""
        if offset >= len(data):
            raise ValueError("Insufficient data")
        
        opcode = OpCode(data[offset])
        offset += 1
        
        if offset >= len(data):
            return cls(opcode), offset
        
        operand_type = data[offset]
        offset += 1
        
        operand = None
        if operand_type == 0x00:  # No operand
            pass
        elif operand_type == 0x01:  # Boolean
            if offset >= len(data):
                raise ValueError("Insufficient data for boolean operand")
            operand = bool(data[offset])
            offset += 1
        elif operand_type == 0x02:  # String
            if offset + 2 > len(data):
                raise ValueError("Insufficient data for string length")
            length = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2
            if offset + length > len(data):
                raise ValueError("Insufficient data for string operand")
            operand = data[offset:offset+length].decode('utf-8')
            offset += length
        elif operand_type == 0x04:  # Integer
            if offset + 4 > len(data):
                raise ValueError("Insufficient data for integer operand")
            operand = struct.unpack('>i', data[offset:offset+4])[0]
            offset += 4
        elif operand_type == 0x08:  # Float
            if offset + 8 > len(data):
                raise ValueError("Insufficient data for float operand")
            operand = struct.unpack('>d', data[offset:offset+8])[0]
            offset += 8
        
        return cls(opcode, operand), offset


class BytecodeProgram:
    """Represents a complete bytecode program."""
    
    def __init__(self):
        self.instructions: List[BytecodeInstruction] = []
        self.constants: List[Any] = []
        self.functions: Dict[str, int] = {}  # Function name -> instruction index
        self.globals: Dict[str, Any] = {}
    
    def add_instruction(self, instruction: BytecodeInstruction) -> int:
        """Add instruction and return its index."""
        self.instructions.append(instruction)
        return len(self.instructions) - 1
    
    def add_constant(self, value: Any) -> int:
        """Add constant and return its index."""
        self.constants.append(value)
        return len(self.constants) - 1
    
    def add_function(self, name: str, start_index: int):
        """Add function entry point."""
        self.functions[name] = start_index
    
    def to_bytes(self) -> bytes:
        """Convert program to byte representation."""
        # Header: magic number (4 bytes) + version (2 bytes) + instruction count (4 bytes)
        magic = b'REAP'
        version = struct.pack('>H', 1)
        instruction_count = struct.pack('>I', len(self.instructions))
        header = magic + version + instruction_count
        
        # Constants section
        constants_count = struct.pack('>I', len(self.constants))
        constants_data = b''
        for const in self.constants:
            if isinstance(const, str):
                const_bytes = const.encode('utf-8')
                constants_data += b'STR:' + struct.pack('>H', len(const_bytes)) + const_bytes
            elif isinstance(const, int):
                constants_data += b'INT:' + struct.pack('>q', const)
            elif isinstance(const, float):
                constants_data += b'FLT:' + struct.pack('>d', const)
            elif isinstance(const, bool):
                constants_data += b'BOOL' + struct.pack('B', 1 if const else 0)
            elif const is None:
                constants_data += b'NONE'
            else:
                # Convert to string
                const_str = str(const)
                const_bytes = const_str.encode('utf-8')
                constants_data += b'STR:' + struct.pack('>H', len(const_bytes)) + const_bytes
        
        # Instructions section
        instructions_data = b''
        for instruction in self.instructions:
            instructions_data += instruction.to_bytes()
        
        # Functions section
        functions_count = struct.pack('>I', len(self.functions))
        functions_data = b''
        for name, index in self.functions.items():
            name_bytes = name.encode('utf-8')
            functions_data += struct.pack('>H', len(name_bytes)) + name_bytes
            functions_data += struct.pack('>I', index)
        
        return header + constants_count + constants_data + functions_count + functions_data + instructions_data
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'BytecodeProgram':
        """Create program from byte representation."""
        if len(data) < 10:
            raise ValueError("Invalid bytecode data")
        
        # Parse header
        magic = data[:4]
        if magic != b'REAP':
            raise ValueError("Invalid magic number")
        
        version = struct.unpack('>H', data[4:6])[0]
        instruction_count = struct.unpack('>I', data[6:10])[0]
        offset = 10
        
        # Parse constants
        constants_count = struct.unpack('>I', data[offset:offset+4])[0]
        offset += 4
        
        program = cls()
        for _ in range(constants_count):
            if offset >= len(data):
                break
            
            # Read constant type marker
            if offset + 4 > len(data):
                break
            type_marker = data[offset:offset+4]
            offset += 4
            
            if type_marker == b'STR:':
                # String constant
                length = struct.unpack('>H', data[offset:offset+2])[0]
                offset += 2
                if offset + length > len(data):
                    break
                const_value = data[offset:offset+length].decode('utf-8')
                program.constants.append(const_value)
                offset += length
            elif type_marker == b'INT:':
                # Integer constant
                if offset + 8 > len(data):
                    break
                const_value = struct.unpack('>q', data[offset:offset+8])[0]
                program.constants.append(const_value)
                offset += 8
            elif type_marker == b'FLT:':
                # Float constant
                if offset + 8 > len(data):
                    break
                const_value = struct.unpack('>d', data[offset:offset+8])[0]
                program.constants.append(const_value)
                offset += 8
            elif type_marker == b'BOOL':
                # Boolean constant
                if offset + 1 > len(data):
                    break
                const_value = bool(data[offset])
                program.constants.append(const_value)
                offset += 1
            elif type_marker == b'NONE':
                # None constant
                program.constants.append(None)
            else:
                # Unknown type - skip
                break
        
        # Parse functions
        functions_count = struct.unpack('>I', data[offset:offset+4])[0]
        offset += 4
        
        for _ in range(functions_count):
            if offset >= len(data):
                break
            name_length = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2
            if offset + name_length > len(data):
                break
            name = data[offset:offset+name_length].decode('utf-8')
            offset += name_length
            if offset + 4 > len(data):
                break
            index = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            program.functions[name] = index
        
        # Parse instructions
        for _ in range(instruction_count):
            if offset >= len(data):
                break
            instruction, offset = BytecodeInstruction.from_bytes(data, offset)
            program.instructions.append(instruction)
        
        return program


# Instruction set documentation
INSTRUCTION_DOCS = {
    OpCode.PUSH_CONST: "Push constant value onto stack",
    OpCode.PUSH_LOCAL: "Push local variable onto stack",
    OpCode.PUSH_GLOBAL: "Push global variable onto stack",
    OpCode.POP: "Pop value from stack",
    OpCode.DUP: "Duplicate top of stack",
    OpCode.SWAP: "Swap top two stack elements",
    OpCode.ADD: "Addition: pop two values, push sum",
    OpCode.SUB: "Subtraction: pop two values, push difference",
    OpCode.MUL: "Multiplication: pop two values, push product",
    OpCode.DIV: "Division: pop two values, push quotient",
    OpCode.MOD: "Modulo: pop two values, push remainder",
    OpCode.NEG: "Negation: pop value, push negative",
    OpCode.INC: "Increment: pop value, push incremented value",
    OpCode.DEC: "Decrement: pop value, push decremented value",
    OpCode.BIT_AND: "Bitwise AND: pop two values, push result",
    OpCode.BIT_OR: "Bitwise OR: pop two values, push result",
    OpCode.BIT_XOR: "Bitwise XOR: pop two values, push result",
    OpCode.BIT_NOT: "Bitwise NOT: pop value, push result",
    OpCode.BIT_SHL: "Left shift: pop two values, push result",
    OpCode.BIT_SHR: "Right shift: pop two values, push result",
    OpCode.BIT_ROT: "Rotate bits: pop two values, push result",
    OpCode.EQ: "Equality: pop two values, push boolean result",
    OpCode.NE: "Not equal: pop two values, push boolean result",
    OpCode.LT: "Less than: pop two values, push boolean result",
    OpCode.LE: "Less than or equal: pop two values, push boolean result",
    OpCode.GT: "Greater than: pop two values, push boolean result",
    OpCode.GE: "Greater than or equal: pop two values, push boolean result",
    OpCode.LOG_AND: "Logical AND: pop two values, push boolean result",
    OpCode.LOG_OR: "Logical OR: pop two values, push boolean result",
    OpCode.LOG_NOT: "Logical NOT: pop value, push boolean result",
    OpCode.JMP: "Unconditional jump to instruction index",
    OpCode.JMP_IF: "Conditional jump if top of stack is true",
    OpCode.JMP_IF_NOT: "Conditional jump if top of stack is false",
    OpCode.CALL: "Call function at instruction index",
    OpCode.RETURN: "Return from function",
    OpCode.CALL_BUILTIN: "Call built-in function",
    OpCode.STORE_LOCAL: "Store top of stack to local variable",
    OpCode.STORE_GLOBAL: "Store top of stack to global variable",
    OpCode.LOAD_LOCAL: "Load local variable onto stack",
    OpCode.LOAD_GLOBAL: "Load global variable onto stack",
    OpCode.ARRAY_NEW: "Create new array with given size",
    OpCode.ARRAY_GET: "Get array element at index",
    OpCode.ARRAY_SET: "Set array element at index",
    OpCode.ARRAY_LEN: "Get array length",
    OpCode.DICT_NEW: "Create new dictionary",
    OpCode.DICT_GET: "Get dictionary value for key",
    OpCode.DICT_SET: "Set dictionary value for key",
    OpCode.DICT_HAS: "Check if dictionary has key",
    OpCode.DICT_KEYS: "Get dictionary keys",
    OpCode.STR_CONCAT: "String concatenation",
    OpCode.STR_LEN: "String length",
    OpCode.STR_SUB: "String substring",
    OpCode.TYPE_CHECK: "Type checking",
    OpCode.TYPE_CONVERT: "Type conversion",
    OpCode.SECURE_STRING: "Create secure string",
    OpCode.CLEAR_MEMORY: "Clear sensitive memory",
    OpCode.RATE_LIMIT: "Rate limiting check",
    OpCode.HALT: "Halt execution",
}
