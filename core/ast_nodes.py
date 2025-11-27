"""
REAPER Language AST Node Definitions

This module defines all Abstract Syntax Tree (AST) node classes for the REAPER language.
Each node represents a different construct in the language and includes position information
for error reporting.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple, Union
from .tokens import Token


class ASTNode(ABC):
    """
    Base class for all AST nodes.
    
    Provides common functionality for position tracking and visitor pattern support.
    """
    
    def __init__(self, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        """
        Initialize AST node.
        
        Args:
            line: Line number where node appears (1-indexed)
            column: Column number where node appears (1-indexed)
            filename: Source filename
        """
        self.line = line
        self.column = column
        self.filename = filename
    
    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern."""
        pass
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"{self.__class__.__name__}({self.filename}:{self.line}:{self.column})"


# ============================================================================
# Literal Nodes
# ============================================================================

class NumberNode(ASTNode):
    """Represents a number literal."""
    
    def __init__(self, value: int, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_number_node(self)
    
    def __repr__(self) -> str:
        return f"NumberNode({self.value}, {self.filename}:{self.line}:{self.column})"


class StringNode(ASTNode):
    """Represents a string literal."""
    
    def __init__(self, value: str, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_string_node(self)
    
    def __repr__(self) -> str:
        return f"StringNode({repr(self.value)}, {self.filename}:{self.line}:{self.column})"


class InterpolatedStringNode(ASTNode):
    """Represents an interpolated string with embedded expressions."""
    
    def __init__(self, parts: List[ASTNode], line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.parts = parts  # List of StringNode and expression nodes
    
    def accept(self, visitor):
        return visitor.visit_interpolated_string_node(self)
    
    def __repr__(self) -> str:
        return f"InterpolatedStringNode({len(self.parts)} parts, {self.filename}:{self.line}:{self.column})"


class HexLiteralNode(ASTNode):
    """Represents a hexadecimal literal (0x1A2B)."""
    
    def __init__(self, value: int, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_hex_literal_node(self)
    
    def __repr__(self) -> str:
        return f"HexLiteralNode(0x{self.value:X}, {self.filename}:{self.line}:{self.column})"


class BinaryLiteralNode(ASTNode):
    """Represents a binary literal (0b1010)."""
    
    def __init__(self, value: int, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_binary_literal_node(self)
    
    def __repr__(self) -> str:
        return f"BinaryLiteralNode(0b{self.value:b}, {self.filename}:{self.line}:{self.column})"


class PhantomLiteralNode(ASTNode):
    """Represents a phantom (floating-point) literal."""
    
    def __init__(self, value: float, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_phantom_literal_node(self)
    
    def __repr__(self) -> str:
        return f"PhantomLiteralNode({self.value}, {self.filename}:{self.line}:{self.column})"


class SpecterLiteralNode(ASTNode):
    """Represents a specter (binary data) literal."""
    
    def __init__(self, value: bytes, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_specter_literal_node(self)
    
    def __repr__(self) -> str:
        return f"SpecterLiteralNode({len(self.value)} bytes, {self.filename}:{self.line}:{self.column})"


class ShadowLiteralNode(ASTNode):
    """Represents a shadow (encrypted/obfuscated) string literal."""
    
    def __init__(self, value: str, encrypted: bool = False, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.value = value
        self.encrypted = encrypted
    
    def accept(self, visitor):
        return visitor.visit_shadow_literal_node(self)
    
    def __repr__(self) -> str:
        return f"ShadowLiteralNode({repr(self.value)}, encrypted={self.encrypted}, {self.filename}:{self.line}:{self.column})"


class BooleanNode(ASTNode):
    """Represents a boolean literal (DEAD/RISEN)."""
    
    def __init__(self, value: bool, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_boolean_node(self)
    
    def __repr__(self) -> str:
        return f"BooleanNode({self.value}, {self.filename}:{self.line}:{self.column})"


class VoidNode(ASTNode):
    """Represents the void (null) value."""
    
    def __init__(self, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
    
    def accept(self, visitor):
        return visitor.visit_void_node(self)
    
    def __repr__(self) -> str:
        return f"VoidNode({self.filename}:{self.line}:{self.column})"


class ArrayNode(ASTNode):
    """Represents an array literal."""
    
    def __init__(self, elements: List[ASTNode], line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.elements = elements
    
    def accept(self, visitor):
        return visitor.visit_array_node(self)
    
    def __repr__(self) -> str:
        return f"ArrayNode({len(self.elements)} elements, {self.filename}:{self.line}:{self.column})"


class ListComprehensionNode(ASTNode):
    """Represents a list comprehension: [expr for item in iterable if condition]."""
    
    def __init__(self, expression: ASTNode, item_name: str, iterable: ASTNode, 
                 condition: Optional[ASTNode] = None, line: int = 0, column: int = 0, 
                 filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.expression = expression  # Expression to evaluate for each item
        self.item_name = item_name    # Variable name for iteration item
        self.iterable = iterable      # Iterable to iterate over
        self.condition = condition    # Optional filter condition
    
    def accept(self, visitor):
        return visitor.visit_list_comprehension_node(self)
    
    def __repr__(self) -> str:
        cond_str = f" if {self.condition}" if self.condition else ""
        return f"ListComprehensionNode({self.item_name} in {self.iterable}{cond_str}, {self.filename}:{self.line}:{self.column})"


class DictionaryNode(ASTNode):
    """Represents a dictionary literal."""
    
    def __init__(self, pairs: List[Tuple[ASTNode, ASTNode]], line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.pairs = pairs  # List of (key, value) tuples
    
    def accept(self, visitor):
        return visitor.visit_dictionary_node(self)
    
    def __repr__(self) -> str:
        return f"DictionaryNode({len(self.pairs)} pairs, {self.filename}:{self.line}:{self.column})"


# ============================================================================
# Variable Nodes
# ============================================================================

class VariableNode(ASTNode):
    """Represents a variable reference."""
    
    def __init__(self, name: str, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_variable_node(self)
    
    def __repr__(self) -> str:
        return f"VariableNode({self.name}, {self.filename}:{self.line}:{self.column})"


class AssignmentNode(ASTNode):
    """Represents a variable assignment."""
    
    def __init__(self, target: ASTNode, value: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>", is_declaration: bool = False, var_type: str = "unknown"):
        super().__init__(line, column, filename)
        self.target = target
        self.value = value
        self.is_declaration = is_declaration
        self.var_type = var_type
    
    def accept(self, visitor):
        return visitor.visit_assignment_node(self)
    
    def __repr__(self) -> str:
        return f"AssignmentNode({self.filename}:{self.line}:{self.column})"


class CompoundAssignmentNode(ASTNode):
    """Represents a compound assignment (+=, -=, etc.)."""
    
    def __init__(self, target: ASTNode, operator: str, value: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.target = target
        self.operator = operator
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_compound_assignment_node(self)
    
    def __repr__(self) -> str:
        return f"CompoundAssignmentNode({self.operator}, {self.filename}:{self.line}:{self.column})"


# ============================================================================
# Operator Nodes
# ============================================================================

class BinaryOpNode(ASTNode):
    """Represents a binary operation."""
    
    def __init__(self, left: ASTNode, operator: str, right: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary_op_node(self)
    
    def __repr__(self) -> str:
        return f"BinaryOpNode({self.operator}, {self.filename}:{self.line}:{self.column})"


class UnaryOpNode(ASTNode):
    """Represents a unary operation."""
    
    def __init__(self, operator: str, operand: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.operator = operator
        self.operand = operand
    
    def accept(self, visitor):
        return visitor.visit_unary_op_node(self)
    
    def __repr__(self) -> str:
        return f"UnaryOpNode({self.operator}, {self.filename}:{self.line}:{self.column})"


class ComparisonNode(ASTNode):
    """Represents a comparison operation."""
    
    def __init__(self, left: ASTNode, operator: str, right: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_comparison_node(self)
    
    def __repr__(self) -> str:
        return f"ComparisonNode({self.operator}, {self.filename}:{self.line}:{self.column})"


class LogicalOpNode(ASTNode):
    """Represents a logical operation (corrupt, infest, banish)."""
    
    def __init__(self, left: ASTNode, operator: str, right: ASTNode, short_circuit: bool = True, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.left = left
        self.operator = operator
        self.right = right
        self.short_circuit = short_circuit
    
    def accept(self, visitor):
        return visitor.visit_logical_op_node(self)
    
    def __repr__(self) -> str:
        return f"LogicalOpNode({self.operator}, {self.filename}:{self.line}:{self.column})"


# ============================================================================
# Access Nodes
# ============================================================================

class IndexAccessNode(ASTNode):
    """Represents array/dictionary index access."""
    
    def __init__(self, object: ASTNode, index: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.object = object
        self.index = index
    
    def accept(self, visitor):
        return visitor.visit_index_access_node(self)
    
    def __repr__(self) -> str:
        return f"IndexAccessNode({self.filename}:{self.line}:{self.column})"


class IndexAssignNode(ASTNode):
    """Represents array/dictionary index assignment."""
    
    def __init__(self, object: ASTNode, index: ASTNode, value: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.object = object
        self.index = index
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_index_assign_node(self)
    
    def __repr__(self) -> str:
        return f"IndexAssignNode({self.filename}:{self.line}:{self.column})"


class SliceNode(ASTNode):
    """Represents array/string slicing."""
    
    def __init__(self, object: ASTNode, start: Optional[ASTNode], end: Optional[ASTNode], step: Optional[ASTNode] = None, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.object = object
        self.start = start
        self.end = end
        self.step = step
    
    def accept(self, visitor):
        return visitor.visit_slice_node(self)
    
    def __repr__(self) -> str:
        return f"SliceNode({self.filename}:{self.line}:{self.column})"


class PropertyAccessNode(ASTNode):
    """Represents object property access."""
    
    def __init__(self, object: ASTNode, property_name: str, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.object = object
        self.property_name = property_name
    
    def accept(self, visitor):
        return visitor.visit_property_access_node(self)
    
    def __repr__(self) -> str:
        return f"PropertyAccessNode({self.property_name}, {self.filename}:{self.line}:{self.column})"


class PropertyAssignNode(ASTNode):
    """Represents object property assignment."""
    
    def __init__(self, object: ASTNode, property_name: str, value: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.object = object
        self.property_name = property_name
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_property_assign_node(self)
    
    def __repr__(self) -> str:
        return f"PropertyAssignNode({self.property_name}, {self.filename}:{self.line}:{self.column})"


class MethodCallNode(ASTNode):
    """Represents object method call."""
    
    def __init__(self, object: ASTNode, method_name: str, arguments: List[ASTNode], line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.object = object
        self.method_name = method_name
        self.arguments = arguments
    
    def accept(self, visitor):
        return visitor.visit_method_call_node(self)
    
    def __repr__(self) -> str:
        return f"MethodCallNode({self.method_name}, {len(self.arguments)} args, {self.filename}:{self.line}:{self.column})"


# ============================================================================
# Control Flow Nodes
# ============================================================================

class JudgeNode(ASTNode):
    """Represents a judge (switch/match) statement."""
    
    def __init__(
        self,
        expression: ASTNode,
        cases: List[Tuple[Optional[ASTNode], ASTNode]],  # List of (value, body) tuples, None for default
        default_body: Optional[ASTNode] = None,
        line: int = 0,
        column: int = 0,
        filename: str = "<unknown>"
    ):
        super().__init__(line, column, filename)
        self.expression = expression  # Expression to match against
        self.cases = cases  # List of (case_value, case_body) tuples
        self.default_body = default_body  # Optional default case body
    
    def accept(self, visitor):
        return visitor.visit_judge_node(self)
    
    def __repr__(self) -> str:
        return f"JudgeNode({len(self.cases)} cases, {self.filename}:{self.line}:{self.column})"


class JudgeNode(ASTNode):
    """Represents a judge (switch/match) statement."""
    
    def __init__(
        self,
        expression: ASTNode,
        cases: List[Tuple[Optional[ASTNode], ASTNode]],  # List of (value, body) tuples, None for default
        default_body: Optional[ASTNode] = None,
        line: int = 0,
        column: int = 0,
        filename: str = "<unknown>"
    ):
        super().__init__(line, column, filename)
        self.expression = expression  # Expression to match against
        self.cases = cases  # List of (case_value, case_body) tuples
        self.default_body = default_body  # Optional default case body
    
    def accept(self, visitor):
        return visitor.visit_judge_node(self)
    
    def __repr__(self) -> str:
        return f"JudgeNode({len(self.cases)} cases, {self.filename}:{self.line}:{self.column})"


class IfNode(ASTNode):
    """Represents an if statement with else-if chains."""
    
    def __init__(
        self, 
        condition: ASTNode, 
        if_body: ASTNode, 
        elif_conditions: List[ASTNode] = None, 
        elif_bodies: List[ASTNode] = None, 
        else_body: Optional[ASTNode] = None,
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>"
    ):
        super().__init__(line, column, filename)
        self.condition = condition
        self.if_body = if_body
        self.elif_conditions = elif_conditions or []
        self.elif_bodies = elif_bodies or []
        self.else_body = else_body
    
    def accept(self, visitor):
        return visitor.visit_if_node(self)
    
    def __repr__(self) -> str:
        return f"IfNode({len(self.elif_conditions)} elifs, {self.filename}:{self.line}:{self.column})"


class ShambleNode(ASTNode):
    """Represents a shamble (for) loop."""
    
    def __init__(self, var_name: str, start: ASTNode, end: ASTNode, body: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.var_name = var_name
        self.start = start
        self.end = end
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_shamble_node(self)
    
    def __repr__(self) -> str:
        return f"ShambleNode({self.var_name}, {self.filename}:{self.line}:{self.column})"


class DecayNode(ASTNode):
    """Represents a decay (foreach) loop."""
    
    def __init__(self, var_name: str, iterable: ASTNode, body: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.var_name = var_name
        self.iterable = iterable
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_decay_node(self)
    
    def __repr__(self) -> str:
        return f"DecayNode({self.var_name}, {self.filename}:{self.line}:{self.column})"


class SoullessNode(ASTNode):
    """Represents a soulless (infinite while) loop."""
    
    def __init__(self, body: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_soulless_node(self)
    
    def __repr__(self) -> str:
        return f"SoullessNode({self.filename}:{self.line}:{self.column})"


class FleeNode(ASTNode):
    """Represents a flee (break) statement."""
    
    def __init__(self, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
    
    def accept(self, visitor):
        return visitor.visit_flee_node(self)
    
    def __repr__(self) -> str:
        return f"FleeNode({self.filename}:{self.line}:{self.column})"


class PersistNode(ASTNode):
    """Represents a persist (continue) statement."""
    
    def __init__(self, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
    
    def accept(self, visitor):
        return visitor.visit_persist_node(self)
    
    def __repr__(self) -> str:
        return f"PersistNode({self.filename}:{self.line}:{self.column})"


# ============================================================================
# Function Nodes
# ============================================================================

class InfectNode(ASTNode):
    """Represents a function definition."""
    
    def __init__(
        self, 
        name: str, 
        params: List[Tuple[str, str, Optional[ASTNode]]], 
        return_type: Optional[str], 
        body: ASTNode,
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>"
    ):
        super().__init__(line, column, filename)
        self.name = name
        self.params = params  # List of (name, type, default_value)
        self.return_type = return_type
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_infect_node(self)
    
    def __repr__(self) -> str:
        return f"InfectNode({self.name}, {len(self.params)} params, {self.filename}:{self.line}:{self.column})"


class CallNode(ASTNode):
    """Represents a function call."""
    
    def __init__(self, function_name: str, arguments: List[ASTNode], line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.function_name = function_name
        self.arguments = arguments
    
    def accept(self, visitor):
        return visitor.visit_call_node(self)
    
    def __repr__(self) -> str:
        return f"CallNode({self.function_name}, {len(self.arguments)} args, {self.filename}:{self.line}:{self.column})"


class ReapNode(ASTNode):
    """Represents a return statement."""
    
    def __init__(self, value: Optional[ASTNode], line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_reap_node(self)
    
    def __repr__(self) -> str:
        return f"ReapNode({self.filename}:{self.line}:{self.column})"


# ============================================================================
# Class Nodes
# ============================================================================

class TombNode(ASTNode):
    """Represents a class definition."""
    
    def __init__(
        self, 
        name: str, 
        properties: List[AssignmentNode], 
        methods: List[InfectNode],
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>"
    ):
        super().__init__(line, column, filename)
        self.name = name
        self.properties = properties
        self.methods = methods
    
    def accept(self, visitor):
        return visitor.visit_tomb_node(self)
    
    def __repr__(self) -> str:
        return f"TombNode({self.name}, {len(self.properties)} props, {len(self.methods)} methods, {self.filename}:{self.line}:{self.column})"


class SpawnNode(ASTNode):
    """Represents a class instantiation."""
    
    def __init__(self, class_name: str, arguments: List[ASTNode], line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.class_name = class_name
        self.arguments = arguments
    
    def accept(self, visitor):
        return visitor.visit_spawn_node(self)
    
    def __repr__(self) -> str:
        return f"SpawnNode({self.class_name}, {len(self.arguments)} args, {self.filename}:{self.line}:{self.column})"


# ============================================================================
# Output Nodes
# ============================================================================

class HarvestNode(ASTNode):
    """Represents a harvest (print) statement."""
    
    def __init__(self, expressions: List[ASTNode], line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.expressions = expressions
    
    def accept(self, visitor):
        return visitor.visit_harvest_node(self)
    
    def __repr__(self) -> str:
        return f"HarvestNode({len(self.expressions)} expressions, {self.filename}:{self.line}:{self.column})"


class RestNode(ASTNode):
    """Represents a rest (sleep) statement."""
    
    def __init__(self, duration: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.duration = duration
    
    def accept(self, visitor):
        return visitor.visit_rest_node(self)
    
    def __repr__(self) -> str:
        return f"RestNode({self.filename}:{self.line}:{self.column})"


# ============================================================================
# Structure Nodes
# ============================================================================

class ProgramNode(ASTNode):
    """Represents the root of a REAPER program."""
    
    def __init__(self, statements: List[ASTNode], line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.statements = statements
    
    def accept(self, visitor):
        return visitor.visit_program_node(self)
    
    def __repr__(self) -> str:
        return f"ProgramNode({len(self.statements)} statements, {self.filename}:{self.line}:{self.column})"


class BlockNode(ASTNode):
    """Represents a block of statements."""
    
    def __init__(self, statements: List[ASTNode], line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.statements = statements
    
    def accept(self, visitor):
        return visitor.visit_block_node(self)


class ExpressionStatementNode(ASTNode):
    """Expression statement node."""
    
    def __init__(self, expression: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_expression_statement_node(self)
    
    def __repr__(self) -> str:
        return f"BlockNode({len(self.statements)} statements, {self.filename}:{self.line}:{self.column})"


class InfiltrateNode(ASTNode):
    """Infiltrate statement node (import security modules)."""
    
    def __init__(self, module_name: str, alias: Optional[str] = None, 
                 symbol_names: Optional[List[str]] = None,
                 line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.module_name = module_name
        self.alias = alias  # Optional alias for the module
        self.symbol_names = symbol_names or []  # Optional list of specific symbols to import
    
    def accept(self, visitor):
        return visitor.visit_infiltrate_node(self)
    
    def __repr__(self) -> str:
        alias_str = f" as {self.alias}" if self.alias else ""
        symbols_str = f" ({', '.join(self.symbol_names)})" if self.symbol_names else ""
        return f"InfiltrateNode({self.module_name}{alias_str}{symbols_str}, {self.filename}:{self.line}:{self.column})"


class CloakNode(ASTNode):
    """Cloak statement node (enable anonymity features)."""
    
    def __init__(self, feature_name: str, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.feature_name = feature_name
    
    def accept(self, visitor):
        return visitor.visit_cloak_node(self)
    
    def __repr__(self) -> str:
        return f"CloakNode({self.feature_name}, {self.filename}:{self.line}:{self.column})"


class ExploitNode(ASTNode):
    """Exploit statement node (try/catch for security operations - legacy)."""
    
    def __init__(self, try_block: List[ASTNode], catch_blocks: List[Tuple[Optional[str], List[ASTNode]]], 
                 line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.try_block = try_block
        self.catch_blocks = catch_blocks  # List of (exception_name, catch_block) tuples
    
    def accept(self, visitor):
        return visitor.visit_exploit_node(self)
    
    def __repr__(self) -> str:
        return f"ExploitNode({len(self.try_block)} try, {len(self.catch_blocks)} catch, {self.filename}:{self.line}:{self.column})"


class RiskNode(ASTNode):
    """Risk statement node (try block for exception handling)."""
    
    def __init__(self, try_block: BlockNode, catch_blocks: List[Tuple[Optional[str], Optional[str], BlockNode]], 
                 finally_block: Optional[BlockNode] = None,
                 line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.try_block = try_block  # BlockNode containing try statements
        self.catch_blocks = catch_blocks  # List of (exception_type, exception_var, catch_block) tuples
        self.finally_block = finally_block  # Optional finally block
    
    def accept(self, visitor):
        return visitor.visit_risk_node(self)
    
    def __repr__(self) -> str:
        finally_str = "with finally" if self.finally_block else "no finally"
        return f"RiskNode({len(self.catch_blocks)} catch, {finally_str}, {self.filename}:{self.line}:{self.column})"


class RaiseExceptionNode(ASTNode):
    """Raise exception statement node."""
    
    def __init__(self, exception_type: Optional[str], exception_message: Optional[ASTNode],
                 line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.exception_type = exception_type  # Exception type name (e.g., "ReaperRuntimeError")
        self.exception_message = exception_message  # Optional message expression
    
    def accept(self, visitor):
        return visitor.visit_raise_exception_node(self)
    
    def __repr__(self) -> str:
        return f"RaiseExceptionNode({self.exception_type}, {self.filename}:{self.line}:{self.column})"


class BreachNode(ASTNode):
    """Breach statement node (async operations)."""
    
    def __init__(self, async_block: BlockNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.async_block = async_block  # BlockNode containing async statements
    
    def accept(self, visitor):
        return visitor.visit_breach_node(self)
    
    def __repr__(self) -> str:
        return f"BreachNode({len(self.async_block.statements)} statements, {self.filename}:{self.line}:{self.column})"


class AwaitNode(ASTNode):
    """Await expression node (wait for async operation)."""
    
    def __init__(self, expression: ASTNode, line: int = 0, column: int = 0, filename: str = "<unknown>"):
        super().__init__(line, column, filename)
        self.expression = expression  # Expression that returns an async task
    
    def accept(self, visitor):
        return visitor.visit_await_node(self)
    
    def __repr__(self) -> str:
        return f"AwaitNode({self.filename}:{self.line}:{self.column})"


# ============================================================================
# Utility Functions
# ============================================================================

def create_node_from_token(node_class, token: Token, *args, **kwargs) -> ASTNode:
    """
    Create an AST node from a token with position information.
    
    Args:
        node_class: The AST node class to instantiate
        token: Token to extract position from
        *args: Additional positional arguments for node constructor
        **kwargs: Additional keyword arguments for node constructor
        
    Returns:
        New AST node instance
    """
    return node_class(
        *args,
        line=token.line,
        column=token.column,
        filename=token.filename,
        **kwargs
    )


def copy_position(from_node: ASTNode, to_node: ASTNode) -> None:
    """
    Copy position information from one node to another.
    
    Args:
        from_node: Source node
        to_node: Target node
    """
    to_node.line = from_node.line
    to_node.column = from_node.column
    to_node.filename = from_node.filename
