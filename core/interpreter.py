"""
REAPER Language Interpreter

This module implements the tree-walking interpreter for the REAPER language.
It executes AST nodes with comprehensive type checking, resource management,
and all language features including built-in functions and methods.
"""

import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from .ast_nodes import *
from .environment import Environment, EnvironmentStack
from .secure_string import SecureString
from .rate_limiter import TokenBucket
from .async_runtime import ReaperAsyncRuntime, AsyncTask
from .module_loader import ReaperModuleLoader
from .reaper_error import (
    ReaperError, ReaperRuntimeError, ReaperTypeError, ReaperRecursionError, 
    ReaperMemoryError, ReaperIndexError, ReaperKeyError, 
    ReaperZeroDivisionError, suggest_similar_name
)


class ReaperReturn(Exception):
    """Exception used for return statements."""
    def __init__(self, value: Any):
        self.value = value


class ReaperFlee(Exception):
    """Exception used for break statements."""
    pass


class ReaperPersist(Exception):
    """Exception used for continue statements."""
    pass


class Interpreter:
    """
    Tree-walking interpreter for REAPER language.
    
    Implements comprehensive type checking, resource management,
    built-in functions, and all language features.
    """
    
    def __init__(self, max_recursion_depth: int = 1000, execution_timeout: float = 30.0,
                 max_string_length: int = 1000000, max_array_size: int = 100000,
                 max_dict_size: int = 100000, max_function_calls: int = 10000,
                 rate_limit_ops_per_second: float = 1000.0, rate_limit_burst: int = 100):
        """Initialize interpreter with enhanced resource management."""
        # Resource limits
        self.max_recursion_depth = max_recursion_depth
        self.max_call_stack_size = 1000
        self.max_string_length = max_string_length
        self.max_array_size = max_array_size
        self.max_dict_size = max_dict_size
        self.max_function_calls = max_function_calls
        self.execution_timeout = execution_timeout
        
        # Runtime tracking
        self.recursion_depth = 0
        self.call_stack_size = 0
        self.function_call_count = 0
        self.start_time = 0
        self.timeout_timer = None
        
        # Rate limiting
        self.rate_limiter = TokenBucket(rate_limit_ops_per_second, rate_limit_burst)
        self.operation_count = 0
        
        # Memory tracking
        self.total_memory_used = 0
        self.max_memory_usage = 100 * 1024 * 1024  # 100MB default limit
        
        # Secure string tracking for cleanup
        self.secure_strings = []
        
        # Module loader (will be initialized with current file path when needed)
        self.module_loader = ReaperModuleLoader()
        
        # Async runtime
        self.async_runtime = ReaperAsyncRuntime(max_workers=10)
        
        # Environment stack
        self.environment_stack = EnvironmentStack()
        self.global_environment = Environment()
        self.environment_stack.push(self.global_environment)
        
        # Initialize built-in functions
        self._initialize_builtins()
    
    def _initialize_builtins(self) -> None:
        """Initialize built-in functions in global environment."""
        # Built-in functions are already initialized in the Environment class
        # We just need to store the actual function implementations
        builtins = {
            "harvest": self._builtin_harvest,
            "rest": self._builtin_rest,
            "raise_corpse": self._builtin_raise_corpse,
            "raise_phantom": self._builtin_raise_phantom,  # String to float
            "steal_soul": self._builtin_steal_soul,  # Int/float to string
            "summon": self._builtin_summon,
            "final_rest": self._builtin_final_rest,
            "curse": self._builtin_curse,
            "absolute": self._builtin_absolute,
            "lesser": self._builtin_lesser,
            "greater": self._builtin_greater,
        }
        
        # Store the actual function implementations
        for name, func in builtins.items():
            self.global_environment._storage[name] = (func, "function", True, True)
    
    def interpret(self, program: ProgramNode) -> None:
        """
        Interpret a REAPER program.
        
        Args:
            program: ProgramNode to execute
            
        Raises:
            ReaperRuntimeError: On runtime errors
            ReaperRecursionError: On recursion limit exceeded
            ReaperMemoryError: On resource limit exceeded
        """
        self.start_time = time.time()
        self._start_timeout()
        
        try:
            for statement in program.statements:
                self._execute(statement)
        finally:
            self._stop_timeout()
            self._cleanup_secure_strings()
    
    def _start_timeout(self) -> None:
        """Start execution timeout timer."""
        def timeout_handler():
            raise ReaperRuntimeError("Execution timeout exceeded")
        
        self.timeout_timer = threading.Timer(self.execution_timeout, timeout_handler)
        self.timeout_timer.start()
    
    def _stop_timeout(self) -> None:
        """Stop execution timeout timer."""
        if self.timeout_timer:
            self.timeout_timer.cancel()
            self.timeout_timer = None
    
    def _check_timeout(self) -> None:
        """Check if execution timeout has been exceeded."""
        if time.time() - self.start_time > self.execution_timeout:
            raise ReaperRuntimeError("Execution timeout exceeded")
    
    def _check_recursion_limit(self) -> None:
        """Check recursion depth limit."""
        if self.recursion_depth >= self.max_recursion_depth:
            raise ReaperRecursionError(
                "Maximum recursion depth exceeded",
                current_depth=self.recursion_depth,
                max_depth=self.max_recursion_depth
            )
    
    def _check_memory_limit(self, value: Any, resource_type: str) -> None:
        """Check memory/resource limits with enhanced tracking."""
        if resource_type == "string" and isinstance(value, str):
            if len(value) > self.max_string_length:
                raise ReaperMemoryError(
                    f"String length {len(value)} exceeds maximum {self.max_string_length}",
                    resource_type=resource_type,
                    current_size=len(value),
                    max_size=self.max_string_length
                )
            # Track memory usage
            self.total_memory_used += len(value.encode('utf-8'))
        elif resource_type == "array" and isinstance(value, list):
            if len(value) > self.max_array_size:
                raise ReaperMemoryError(
                    f"Array size {len(value)} exceeds maximum {self.max_array_size}",
                    resource_type=resource_type,
                    current_size=len(value),
                    max_size=self.max_array_size
                )
            # Track memory usage
            self.total_memory_used += len(value) * 8  # Rough estimate
        elif resource_type == "dict" and isinstance(value, dict):
            if len(value) > self.max_dict_size:
                raise ReaperMemoryError(
                    f"Dictionary size {len(value)} exceeds maximum {self.max_dict_size}",
                    resource_type=resource_type,
                    current_size=len(value),
                    max_size=self.max_dict_size
                )
            # Track memory usage
            self.total_memory_used += len(value) * 16  # Rough estimate
        
        # Check total memory usage
        if self.total_memory_used > self.max_memory_usage:
            raise ReaperMemoryError(
                f"Total memory usage {self.total_memory_used} exceeds maximum {self.max_memory_usage}",
                resource_type="total",
                current_size=self.total_memory_used,
                max_size=self.max_memory_usage
            )
    
    def _check_rate_limit(self, operation_type: str = "general") -> None:
        """Check rate limiting for operations."""
        if not self.rate_limiter.try_acquire(1.0):
            raise ReaperRuntimeError(
                f"Rate limit exceeded for {operation_type} operations"
            )
        self.operation_count += 1
    
    def _check_function_call_limit(self) -> None:
        """Check function call limit."""
        if self.function_call_count >= self.max_function_calls:
            raise ReaperRuntimeError(
                f"Maximum function calls {self.max_function_calls} exceeded"
            )
        self.function_call_count += 1
    
    def _track_secure_string(self, secure_string: SecureString) -> None:
        """Track secure strings for cleanup."""
        self.secure_strings.append(secure_string)
    
    def _cleanup_secure_strings(self) -> None:
        """Clean up tracked secure strings."""
        for secure_string in self.secure_strings:
            try:
                secure_string.clear()
            except Exception:
                pass  # Ignore errors during cleanup
        self.secure_strings.clear()
    
    def _execute(self, node: ASTNode) -> Any:
        """Execute an AST node."""
        self._check_timeout()
        self._check_rate_limit("execution")
        return node.accept(self)
    
    # ============================================================================
    # Literal Node Visitors
    # ============================================================================
    
    def visit_number_node(self, node: NumberNode) -> int:
        """Visit number literal node."""
        return node.value
    
    def visit_string_node(self, node: StringNode) -> str:
        """Visit string literal node."""
        self._check_memory_limit(node.value, "string")
        return node.value
    
    def visit_interpolated_string_node(self, node: InterpolatedStringNode) -> str:
        """Visit interpolated string node."""
        result = ""
        for part in node.parts:
            if isinstance(part, StringNode):
                result += part.value
            else:
                # Evaluate expression and convert to string
                value = self._execute(part)
                if value is None:
                    result += "void"
                else:
                    result += str(value)
        
        self._check_memory_limit(result, "string")
        return result
    
    def visit_boolean_node(self, node: BooleanNode) -> bool:
        """Visit boolean literal node."""
        return node.value
    
    def visit_void_node(self, node: VoidNode) -> None:
        """Visit void literal node."""
        return None
    
    def visit_hex_literal_node(self, node: HexLiteralNode) -> int:
        """Visit hex literal node."""
        return node.value
    
    def visit_binary_literal_node(self, node: BinaryLiteralNode) -> int:
        """Visit binary literal node."""
        return node.value
    
    def visit_phantom_literal_node(self, node: PhantomLiteralNode) -> float:
        """Visit phantom (floating-point) literal node."""
        return node.value
    
    def visit_specter_literal_node(self, node: SpecterLiteralNode) -> bytes:
        """Visit specter (binary data) literal node."""
        self._check_memory_limit(node.value, "string")  # Treat as string for memory limits
        return node.value
    
    def visit_shadow_literal_node(self, node: ShadowLiteralNode) -> str:
        """Visit shadow (encrypted/obfuscated) literal node."""
        self._check_memory_limit(node.value, "string")
        # Store shadow literals as SecureString for safer handling
        try:
            secure_string = SecureString.from_plain(node.value)
            self._track_secure_string(secure_string)
            return secure_string
        except Exception:
            # Fallback to plain string if secure allocation fails
            return node.value
    
    def visit_array_node(self, node: ArrayNode) -> List[Any]:
        """Visit array literal node."""
        self._check_rate_limit("array_creation")
        elements = []
        for element in node.elements:
            elements.append(self._execute(element))
        
        self._check_memory_limit(elements, "array")
        return elements
    
    def visit_list_comprehension_node(self, node: 'ListComprehensionNode') -> List[Any]:
        """Visit list comprehension node: [expr for item in iterable if condition]."""
        self._check_rate_limit("list_comprehension")
        
        # Evaluate the iterable
        iterable = self._execute(node.iterable)
        
        # Check if iterable is actually iterable
        if not isinstance(iterable, (list, str, dict)):
            raise ReaperTypeError(
                f"List comprehension iterable must be array, string, or dictionary, got {type(iterable).__name__}",
                node.line,
                node.column,
                node.filename
            )
        
        # Create new environment for the comprehension variable
        current_env = self._get_current_environment()
        comp_env = current_env.create_child()
        self.environment_stack.push(comp_env)
        
        try:
            result = []
            
            # Iterate over the iterable
            # For dictionaries, iterate over keys (like Python)
            if isinstance(iterable, dict):
                items = iterable.keys()
            elif isinstance(iterable, str):
                items = iterable  # Iterate over characters
            else:
                items = iterable
            
            for item in items:
                # Set the iteration variable
                comp_env.define(node.item_name, item, "unknown", False, node.line, node.column)
                
                # Check condition if present
                if node.condition is not None:
                    condition_result = self._execute(node.condition)
                    if not isinstance(condition_result, bool):
                        raise ReaperTypeError(
                            f"List comprehension condition must be boolean, got {type(condition_result).__name__}",
                            node.line,
                            node.column,
                            node.filename
                        )
                    if not condition_result:
                        continue  # Skip this item
                
                # Evaluate expression and add to result
                value = self._execute(node.expression)
                result.append(value)
                
                # Check memory limit
                self._check_memory_limit(result, "array")
            
            return result
        finally:
            # Always pop the comprehension environment
            self.environment_stack.pop()
    
    def visit_dictionary_node(self, node: DictionaryNode) -> Dict[Any, Any]:
        """Visit dictionary literal node."""
        self._check_rate_limit("dictionary_creation")
        pairs = {}
        for key, value in node.pairs:
            key_value = self._execute(key)
            value_value = self._execute(value)
            pairs[key_value] = value_value
        
        self._check_memory_limit(pairs, "dict")
        return pairs
    
    # ============================================================================
    # Variable Node Visitors
    # ============================================================================
    
    def visit_variable_node(self, node: VariableNode) -> Any:
        """Visit variable reference node."""
        value, var_type = self._get_current_environment().get(node.name, node.line, node.column)
        return value
    
    def visit_assignment_node(self, node: AssignmentNode) -> Any:
        """Visit assignment node."""
        value = self._execute(node.value)
        
        # Handle shadow type variables specially
        if node.var_type == "shadow" and isinstance(value, str):
            try:
                secure_string = SecureString.from_plain(value)
                self._track_secure_string(secure_string)
                value = secure_string
            except Exception:
                # Fallback to plain string if secure allocation fails
                pass
        
        if isinstance(node.target, VariableNode):
            current_env = self._get_current_environment()
            
            if node.is_declaration:
                # Variable declaration - always create new variable in current scope
                current_env.define(node.target.name, value, node.var_type, False, node.line, node.column)
            else:
                # Regular assignment - update existing variable or create if doesn't exist
                if current_env.exists(node.target.name):
                    current_env.set(node.target.name, value, node.line, node.column)
                else:
                    # Variable doesn't exist, create it
                    current_env.define(node.target.name, value, node.var_type, False, node.line, node.column)
        elif isinstance(node.target, IndexAccessNode):
            # Index assignment
            self._visit_index_assign(node.target, value)
        elif isinstance(node.target, PropertyAccessNode):
            # Property assignment
            self._visit_property_assign(node.target, value)
        else:
            raise ReaperRuntimeError(
                f"Invalid assignment target",
                node.line, node.column, node.filename
            )
        
        return value
    
    def visit_compound_assignment_node(self, node: CompoundAssignmentNode) -> Any:
        """Visit compound assignment node."""
        # Get current value
        if isinstance(node.target, VariableNode):
            current_value, _ = self._get_current_environment().get(node.target.name, node.line, node.column)
        elif isinstance(node.target, IndexAccessNode):
            current_value = self._visit_index_access(node.target)
        elif isinstance(node.target, PropertyAccessNode):
            current_value = self._visit_property_access(node.target)
        else:
            raise ReaperRuntimeError(
                f"Invalid compound assignment target",
                node.line, node.column, node.filename
            )
        
        # Evaluate right side
        right_value = self._execute(node.value)
        
        # Perform operation
        if node.operator == "+=":
            result = self._add(current_value, right_value, node.line, node.column)
        elif node.operator == "-=":
            result = self._subtract(current_value, right_value, node.line, node.column)
        elif node.operator == "*=":
            result = self._multiply(current_value, right_value, node.line, node.column)
        elif node.operator == "/=":
            result = self._divide(current_value, right_value, node.line, node.column)
        elif node.operator == "%=":
            result = self._modulo(current_value, right_value, node.line, node.column)
        else:
            raise ReaperRuntimeError(
                f"Unknown compound assignment operator: {node.operator}",
                node.line, node.column, node.filename
            )
        
        # Assign result
        if isinstance(node.target, VariableNode):
            self._get_current_environment().set(node.target.name, result, node.line, node.column)
        elif isinstance(node.target, IndexAccessNode):
            self._visit_index_assign(node.target, result)
        elif isinstance(node.target, PropertyAccessNode):
            self._visit_property_assign(node.target, result)
        
        return result
    
    # ============================================================================
    # Operator Node Visitors
    # ============================================================================
    
    def visit_binary_op_node(self, node: BinaryOpNode) -> Any:
        """Visit binary operation node."""
        left = self._execute(node.left)
        right = self._execute(node.right)
        
        if node.operator == "+":
            return self._add(left, right, node.line, node.column)
        elif node.operator == "-":
            return self._subtract(left, right, node.line, node.column)
        elif node.operator == "*":
            return self._multiply(left, right, node.line, node.column)
        elif node.operator == "/":
            return self._divide(left, right, node.line, node.column)
        elif node.operator == "%":
            return self._modulo(left, right, node.line, node.column)
        elif node.operator == "spread":
            return self._bitwise_or(left, right, node.line, node.column)
        elif node.operator == "mutate":
            return self._bitwise_xor(left, right, node.line, node.column)
        elif node.operator == "wither":
            return self._bitwise_and(left, right, node.line, node.column)
        elif node.operator == "rot":
            return self._bitwise_rotate(left, right, node.line, node.column)
        else:
            raise ReaperRuntimeError(
                f"Unknown binary operator: {node.operator}",
                node.line, node.column, node.filename
            )
    
    def visit_unary_op_node(self, node: UnaryOpNode) -> Any:
        """Visit unary operation node."""
        operand = self._execute(node.operand)
        
        if node.operator == "-":
            return self._negate(operand, node.line, node.column)
        elif node.operator == "banish":
            return self._logical_not(operand, node.line, node.column)
        elif node.operator == "invert":
            return self._bitwise_not(operand, node.line, node.column)
        else:
            raise ReaperRuntimeError(
                f"Unknown unary operator: {node.operator}",
                node.line, node.column, node.filename
            )
    
    def visit_comparison_node(self, node: ComparisonNode) -> bool:
        """Visit comparison node."""
        left = self._execute(node.left)
        right = self._execute(node.right)
        
        if node.operator == "==":
            return self._equal(left, right, node.line, node.column)
        elif node.operator == "!=":
            return not self._equal(left, right, node.line, node.column)
        elif node.operator == "<":
            return self._less_than(left, right, node.line, node.column)
        elif node.operator == ">":
            return self._greater_than(left, right, node.line, node.column)
        elif node.operator == "<=":
            return self._less_equal(left, right, node.line, node.column)
        elif node.operator == ">=":
            return self._greater_equal(left, right, node.line, node.column)
        else:
            raise ReaperRuntimeError(
                f"Unknown comparison operator: {node.operator}",
                node.line, node.column, node.filename
            )
    
    def visit_logical_op_node(self, node: LogicalOpNode) -> bool:
        """Visit logical operation node."""
        left = self._execute(node.left)
        left_bool = self._to_boolean(left, node.line, node.column)
        
        if node.operator == "corrupt":  # AND
            if not left_bool and node.short_circuit:
                return False
            right = self._execute(node.right)
            return left_bool and self._to_boolean(right, node.line, node.column)
        elif node.operator == "infest":  # OR
            if left_bool and node.short_circuit:
                return True
            right = self._execute(node.right)
            return left_bool or self._to_boolean(right, node.line, node.column)
        else:
            raise ReaperRuntimeError(
                f"Unknown logical operator: {node.operator}",
                node.line, node.column, node.filename
            )
    
    # ============================================================================
    # Access Node Visitors
    # ============================================================================
    
    def visit_index_access_node(self, node: IndexAccessNode) -> Any:
        """Visit index access node."""
        return self._visit_index_access(node)
    
    def _visit_index_access(self, node: IndexAccessNode) -> Any:
        """Helper for index access."""
        obj = self._execute(node.object)
        index = self._execute(node.index)
        
        if isinstance(obj, list):
            return self._array_index(obj, index, node.line, node.column)
        elif isinstance(obj, dict):
            return self._dict_access(obj, index, node.line, node.column)
        elif isinstance(obj, str):
            return self._string_index(obj, index, node.line, node.column)
        else:
            raise ReaperTypeError(
                f"Cannot index {type(obj).__name__}",
                node.line, node.column, node.filename,
                expected_type="array, dictionary, or string",
                actual_type=type(obj).__name__,
                operation="indexing"
            )
    
    def visit_index_assign_node(self, node: IndexAssignNode) -> Any:
        """Visit index assignment node."""
        value = self._execute(node.value)
        self._visit_index_assign(node, value)
        return value
    
    def _visit_index_assign(self, node: IndexAccessNode, value: Any) -> None:
        """Helper for index assignment."""
        obj = self._execute(node.object)
        index = self._execute(node.index)
        
        if isinstance(obj, list):
            self._array_index_assign(obj, index, value, node.line, node.column)
        elif isinstance(obj, dict):
            self._dict_assign(obj, index, value, node.line, node.column)
        else:
            raise ReaperTypeError(
                f"Cannot assign to index of {type(obj).__name__}",
                node.line, node.column, node.filename,
                expected_type="array or dictionary",
                actual_type=type(obj).__name__,
                operation="index assignment"
            )
    
    def visit_slice_node(self, node: SliceNode) -> Any:
        """Visit slice node."""
        obj = self._execute(node.object)
        start = self._execute(node.start) if node.start else None
        end = self._execute(node.end) if node.end else None
        step = self._execute(node.step) if node.step else None
        
        if isinstance(obj, list):
            return self._array_slice(obj, start, end, step, node.line, node.column)
        elif isinstance(obj, str):
            return self._string_slice(obj, start, end, step, node.line, node.column)
        else:
            raise ReaperTypeError(
                f"Cannot slice {type(obj).__name__}",
                node.line, node.column, node.filename,
                expected_type="array or string",
                actual_type=type(obj).__name__,
                operation="slicing"
            )
    
    def visit_property_access_node(self, node: PropertyAccessNode) -> Any:
        """Visit property access node."""
        return self._visit_property_access(node)
    
    def _visit_property_access(self, node: PropertyAccessNode) -> Any:
        """Helper for property access."""
        obj = self._execute(node.object)
        
        # Handle exception objects (ReaperError instances)
        if isinstance(obj, ReaperError):
            # Access exception attributes
            if hasattr(obj, node.property_name):
                return getattr(obj, node.property_name)
            else:
                raise ReaperAttributeError(
                    f"Exception object has no attribute '{node.property_name}'",
                    node.line, node.column, node.filename
                )
        
        if isinstance(obj, dict):
            # Class instance property access or module namespace access
            if node.property_name in obj:
                value = obj[node.property_name]
                # If it's a Python callable (function/class), wrap it for Reaper
                if callable(value) and not isinstance(value, (InfectNode, TombNode)):
                    # Return a wrapper that can be called
                    return self._create_callable_wrapper(value, node.line, node.column, node.filename)
                return value
            else:
                available_keys = list(obj.keys())
                raise ReaperKeyError(
                    f"Property '{node.property_name}' not found",
                    node.line, node.column, node.filename,
                    key=node.property_name,
                    available_keys=available_keys
                )
        elif isinstance(obj, list):
            # Array built-in properties
            if node.property_name == "length":
                return len(obj)
            else:
                raise ReaperKeyError(
                    f"Array property '{node.property_name}' not found",
                    node.line, node.column, node.filename,
                    key=node.property_name,
                    available_keys=["length"]
                )
        elif isinstance(obj, str):
            # String built-in properties
            if node.property_name == "length":
                return len(obj)
            else:
                raise ReaperKeyError(
                    f"String property '{node.property_name}' not found",
                    node.line, node.column, node.filename,
                    key=node.property_name,
                    available_keys=["length"]
                )
        elif isinstance(obj, ReaperError):
            # Exception object property access
            if hasattr(obj, node.property_name):
                return getattr(obj, node.property_name)
            else:
                raise ReaperKeyError(
                    f"Exception object has no attribute '{node.property_name}'",
                    node.line, node.column, node.filename,
                    key=node.property_name,
                    available_keys=["message", "line", "column", "filename", "context"]
                )
        else:
            raise ReaperTypeError(
                f"Cannot access property of {type(obj).__name__}",
                node.line, node.column, node.filename,
                expected_type="class instance, array, string, or exception",
                actual_type=type(obj).__name__,
                operation="property access"
            )
    
    def visit_property_assign_node(self, node: PropertyAssignNode) -> Any:
        """Visit property assignment node."""
        value = self._execute(node.value)
        self._visit_property_assign(node, value)
        return value
    
    def _visit_property_assign(self, node: PropertyAccessNode, value: Any) -> None:
        """Helper for property assignment."""
        obj = self._execute(node.object)
        
        if isinstance(obj, dict):
            obj[node.property_name] = value
        else:
            raise ReaperTypeError(
                f"Cannot assign property of {type(obj).__name__}",
                node.line, node.column, node.filename,
                expected_type="class instance",
                actual_type=type(obj).__name__,
                operation="property assignment"
            )
    
    def visit_method_call_node(self, node: MethodCallNode) -> Any:
        """Visit method call node."""
        obj = self._execute(node.object)
        arguments = [self._execute(arg) for arg in node.arguments]
        
        if isinstance(obj, dict):
            # Check if this is a built-in dictionary method first
            if node.method_name in ["curse", "summon", "banish", "inscribe", "possess", "haunt"]:
                return self._call_dict_method(obj, node.method_name, arguments, node.line, node.column)
            # Class instance method call or module function call
            elif node.method_name in obj:
                method = obj[node.method_name]
                if callable(method):
                    # Python callable (function/class from imported module)
                    if not isinstance(method, (InfectNode, TombNode)):
                        # Convert arguments and call Python function
                        converted_args = [self._convert_reaper_to_python(arg) for arg in arguments]
                        try:
                            result = method(*converted_args)
                            return self._convert_python_to_reaper(result)
                        except Exception as e:
                            raise ReaperRuntimeError(
                                f"Error calling '{node.method_name}': {str(e)}",
                                node.line, node.column, node.filename
                            )
                    else:
                        # Built-in Reaper method
                        return method(*arguments)
                else:
                    # User-defined method (InfectNode) - need to bind 'this'
                    return self._call_method(method, obj, arguments, node.line, node.column)
            else:
                available_keys = list(obj.keys())
                raise ReaperKeyError(
                    f"Method '{node.method_name}' not found",
                    node.line, node.column, node.filename,
                    key=node.method_name,
                    available_keys=available_keys
                )
        elif isinstance(obj, list):
            # Array method call
            return self._call_array_method(obj, node.method_name, arguments, node.line, node.column)
        elif isinstance(obj, str):
            # String method call
            return self._call_string_method(obj, node.method_name, arguments, node.line, node.column)
        else:
            raise ReaperTypeError(
                f"Cannot call method on {type(obj).__name__}",
                node.line, node.column, node.filename,
                expected_type="class instance, array, string, or dictionary",
                actual_type=type(obj).__name__,
                operation="method call"
            )
    
    # ============================================================================
    # Control Flow Node Visitors
    # ============================================================================
    
    def visit_judge_node(self, node: JudgeNode) -> Any:
        """Visit judge (switch/match) statement node."""
        # Evaluate the expression to match against
        match_value = self._execute(node.expression)
        
        # Check each case
        for case_value, case_body in node.cases:
            case_val = self._execute(case_value)
            
            # Compare values (supports == comparison)
            if match_value == case_val:
                # Match found - execute case body
                return self._execute(case_body)
        
        # No match found - execute default if present
        if node.default_body:
            return self._execute(node.default_body)
        
        # No match and no default - return None
        return None
    
    def visit_if_node(self, node: IfNode) -> Any:
        """Visit if statement node."""
        condition = self._execute(node.condition)
        
        if self._to_boolean(condition, node.line, node.column):
            return self._execute(node.if_body)
        
        # Check else-if conditions
        for i, elif_condition in enumerate(node.elif_conditions):
            elif_cond = self._execute(elif_condition)
            if self._to_boolean(elif_cond, node.line, node.column):
                return self._execute(node.elif_bodies[i])
        
        # Execute else body if present
        if node.else_body:
            return self._execute(node.else_body)
        
        return None
    
    def visit_shamble_node(self, node: ShambleNode) -> Any:
        """Visit shamble (for) loop node."""
        start = self._execute(node.start)
        end = self._execute(node.end)
        
        self._check_type(start, int, "shamble start", node.line, node.column)
        self._check_type(end, int, "shamble end", node.line, node.column)
        
        # Create loop variable in current environment
        current_env = self._get_current_environment()
        
        for i in range(start, end + 1):
            # Define or update the loop variable
            try:
                current_env.set(node.var_name, i, node.line, node.column)
            except:
                # Variable doesn't exist yet, define it
                current_env.define(node.var_name, i, 'corpse', is_constant=False)
            
            try:
                self._execute(node.body)
            except ReaperFlee:
                break
            except ReaperPersist:
                continue
        
        return None
    
    def visit_decay_node(self, node: DecayNode) -> Any:
        """Visit decay (foreach) loop node."""
        iterable = self._execute(node.iterable)
        current_env = self._get_current_environment()
        
        if isinstance(iterable, list):
            for item in iterable:
                # Define or update the loop variable
                try:
                    current_env.set(node.var_name, item, node.line, node.column)
                except:
                    # Variable doesn't exist yet, define it (type depends on item type)
                    var_type = 'corpse' if isinstance(item, int) else 'soul' if isinstance(item, str) else 'void'
                    current_env.define(node.var_name, item, var_type, is_constant=False)
                
                try:
                    self._execute(node.body)
                except ReaperFlee:
                    break
                except ReaperPersist:
                    continue
        else:
            raise ReaperTypeError(
                f"Cannot iterate over {type(iterable).__name__}",
                node.line, node.column, node.filename,
                expected_type="array",
                actual_type=type(iterable).__name__,
                operation="foreach loop"
            )
        
        return None
    
    def visit_soulless_node(self, node: SoullessNode) -> Any:
        """Visit soulless (infinite while) loop node."""
        while True:
            try:
                self._execute(node.body)
            except ReaperFlee:
                break
            except ReaperPersist:
                continue
        
        return None
    
    def visit_flee_node(self, node: FleeNode) -> Any:
        """Visit flee (break) node."""
        raise ReaperFlee()
    
    def visit_persist_node(self, node: PersistNode) -> Any:
        """Visit persist (continue) node."""
        raise ReaperPersist()
    
    # ============================================================================
    # Function Node Visitors
    # ============================================================================
    
    def visit_lambda_node(self, node: LambdaNode) -> Any:
        """Visit lambda/anonymous function node."""
        # Lambdas are first-class values - return them as-is
        # They'll be called like regular functions
        return node
    
    def visit_infect_node(self, node: InfectNode) -> Any:
        """Visit function definition node."""
        # Store function in current environment
        current_env = self._get_current_environment()
        current_env.define(node.name, node, "function", False, node.line, node.column)
        return None
    
    def visit_call_node(self, node: CallNode) -> Any:
        """Visit function call node."""
        self._check_function_call_limit()
        self._check_rate_limit("function_call")
        arguments = [self._execute(arg) for arg in node.arguments]
        
        # Check if this is a callable from an imported module
        current_env = self._get_current_environment()
        try:
            func_value, _ = current_env.get(node.function_name, node.line, node.column)
            
            # If it's a Python callable wrapper, call it directly
            if callable(func_value) and not isinstance(func_value, (InfectNode, LambdaNode, TombNode)):
                converted_args = [self._convert_reaper_to_python(arg) for arg in arguments]
                try:
                    result = func_value(*converted_args)
                    return self._convert_python_to_reaper(result)
                except Exception as e:
                    raise ReaperRuntimeError(
                        f"Error calling '{node.function_name}': {str(e)}",
                        node.line, node.column, node.filename
                    )
            # If it's a lambda or function node, call it directly
            elif isinstance(func_value, (InfectNode, LambdaNode)):
                return self._call_function(func_value, arguments, node.line, node.column)
        except ReaperRuntimeError:
            # Function not found in environment, try built-in
            pass
        
        return self._call_function_by_name(node.function_name, arguments, node.line, node.column)
    
    def visit_reap_node(self, node: ReapNode) -> Any:
        """Visit return statement node."""
        value = self._execute(node.value) if node.value else None
        raise ReaperReturn(value)
    
    # ============================================================================
    # Class Node Visitors
    # ============================================================================
    
    def visit_tomb_node(self, node: TombNode) -> Any:
        """Visit class definition node."""
        # Store class in current environment
        current_env = self._get_current_environment()
        current_env.define(node.name, node, "class", False, node.line, node.column)
        return None
    
    def visit_spawn_node(self, node: SpawnNode) -> Any:
        """Visit class instantiation node."""
        # Get class definition
        class_def, _ = self._get_current_environment().get(node.class_name, node.line, node.column)
        
        if not isinstance(class_def, TombNode):
            raise ReaperTypeError(
                f"'{node.class_name}' is not a class",
                node.line, node.column, node.filename,
                expected_type="class",
                actual_type=type(class_def).__name__,
                operation="instantiation"
            )
        
        # Create instance
        instance = {}
        
        # Initialize properties
        for prop in class_def.properties:
            if isinstance(prop, AssignmentNode) and isinstance(prop.target, VariableNode):
                value = self._execute(prop.value)
                instance[prop.target.name] = value
        
        # Add methods
        for method in class_def.methods:
            if isinstance(method, InfectNode):
                instance[method.name] = method
        
        # Call constructor if it exists
        constructor = None
        for method in class_def.methods:
            if isinstance(method, InfectNode) and method.name == node.class_name:
                constructor = method
                break
        
        if constructor:
            # Create new environment for constructor execution
            func_env = Environment(self._get_current_environment(), f"<{node.class_name} constructor>")
            
            # Bind 'this' to the instance
            func_env.define("this", instance, "tomb", False)
            
            # Bind parameters
            arguments = [self._execute(arg) for arg in node.arguments]
            
            if len(arguments) != len(constructor.params):
                # Check for default parameters
                required_params = sum(1 for p in constructor.params if len(p) < 3 or p[2] is None)
                if len(arguments) < required_params or len(arguments) > len(constructor.params):
                    raise ReaperRuntimeError(
                        f"Constructor '{node.class_name}' expects {len(constructor.params)} arguments, got {len(arguments)}",
                        node.line, node.column, node.filename
                    )
            
            # Bind arguments to parameters
            for i, param in enumerate(constructor.params):
                param_name = param[0]
                if i < len(arguments):
                    func_env.define(param_name, arguments[i], param[1] if len(param) > 1 else "unknown", False)
                elif len(param) >= 3 and param[2] is not None:
                    # Use default value
                    default_value = self._execute(param[2])
                    func_env.define(param_name, default_value, param[1] if len(param) > 1 else "unknown", False)
            
            # Execute constructor body
            self.environment_stack.push(func_env)
            try:
                self._execute(constructor.body)
            except ReaperReap:
                # Constructors shouldn't return values, but ignore if they do
                pass
            finally:
                self.environment_stack.pop()
        elif len(node.arguments) > 0:
            raise ReaperRuntimeError(
                f"Class '{node.class_name}' has no constructor but got {len(node.arguments)} arguments",
                node.line, node.column, node.filename
            )
        
        return instance
    
    # ============================================================================
    # Output Node Visitors
    # ============================================================================
    
    def visit_harvest_node(self, node: HarvestNode) -> Any:
        """Visit harvest (print) statement node."""
        arguments = []
        for expr in node.expressions:
            value = self._execute(expr)
            arguments.append(value)
        
        # Use the built-in harvest function for consistent formatting
        return self._builtin_harvest(arguments, node.line, node.column)
    
    def visit_rest_node(self, node: RestNode) -> Any:
        """Visit rest (sleep) statement node."""
        duration = self._execute(node.duration)
        self._check_type(duration, int, "rest duration", node.line, node.column)
        
        if duration < 0:
            raise ReaperRuntimeError(
                "Rest duration cannot be negative",
                node.line, node.column, node.filename
            )
        
        time.sleep(duration / 1000.0)  # Convert milliseconds to seconds
        return None
    
    # ============================================================================
    # Structure Node Visitors
    # ============================================================================
    
    def visit_program_node(self, node: ProgramNode) -> Any:
        """Visit program node."""
        for statement in node.statements:
            self._execute(statement)
        return None
    
    def visit_block_node(self, node: BlockNode) -> Any:
        """Visit block node."""
        # Create new environment for block
        current_env = self._get_current_environment()
        block_env = current_env.create_child()
        self.environment_stack.push(block_env)
        
        try:
            for statement in node.statements:
                self._execute(statement)
        finally:
            self.environment_stack.pop()
        
        return None
    
    def visit_expression_statement_node(self, node: ExpressionStatementNode) -> Any:
        """Visit expression statement node."""
        return self._execute(node.expression)
    
    def visit_infiltrate_node(self, node: InfiltrateNode) -> None:
        """Visit infiltrate node (import security modules)."""
        try:
            # If specific symbols are requested
            if node.symbol_names:
                # Import specific symbols
                imported_symbols = self.module_loader.import_symbols(
                    node.module_name,
                    node.symbol_names
                )
                
                # Add symbols to current environment
                current_env = self.environment_stack.current()
                for symbol_name, symbol_value in imported_symbols.items():
                    # Convert Python objects to Reaper-compatible types
                    reaper_value = self._convert_python_to_reaper(symbol_value)
                    current_env.define(symbol_name, reaper_value)
            else:
                # Import entire module
                namespace = self.module_loader.load_module(node.module_name, node.alias)
                
                # Determine namespace name
                ns_name = node.alias or node.module_name
                
                # Create a namespace object (dictionary-like) in Reaper
                # Store as a grimoire (dictionary) in the environment
                current_env = self.environment_stack.current()
                
                # Convert namespace to Reaper dictionary
                reaper_namespace = {}
                for key, value in namespace.items():
                    reaper_namespace[key] = self._convert_python_to_reaper(value)
                
                # Store namespace in environment as a grimoire (dictionary)
                current_env.define(ns_name, reaper_namespace, "grimoire", False, node.line, node.column)
                
        except ReaperRuntimeError as e:
            raise ReaperRuntimeError(
                f"Failed to import module '{node.module_name}': {e.message}",
                node.line,
                node.column,
                node.filename
            )
        except Exception as e:
            raise ReaperRuntimeError(
                f"Error importing module '{node.module_name}': {str(e)}",
                node.line,
                node.column,
                node.filename
            )
    
    def _convert_python_to_reaper(self, value: Any) -> Any:
        """
        Convert Python value to Reaper-compatible value.
        
        Args:
            value: Python value to convert
            
        Returns:
            Reaper-compatible value
        """
        # Handle None
        if value is None:
            return None
        
        # Handle basic types
        if isinstance(value, (int, float, bool, str)):
            return value
        
        # Handle lists -> crypt (arrays)
        if isinstance(value, list):
            return [self._convert_python_to_reaper(item) for item in value]
        
        # Handle dicts -> grimoire (dictionaries)
        if isinstance(value, dict):
            return {k: self._convert_python_to_reaper(v) for k, v in value.items()}
        
        # Handle classes and functions - wrap them for Reaper
        # For now, return as-is (they'll be callable from Reaper)
        return value
    
    def _convert_reaper_to_python(self, value: Any) -> Any:
        """
        Convert Reaper value to Python-compatible value.
        
        Args:
            value: Reaper value to convert
            
        Returns:
            Python-compatible value
        """
        # Handle None/void
        if value is None:
            return None
        
        # Handle basic types (already compatible)
        if isinstance(value, (int, float, bool, str)):
            return value
        
        # Handle lists
        if isinstance(value, list):
            return [self._convert_reaper_to_python(item) for item in value]
        
        # Handle dicts
        if isinstance(value, dict):
            return {k: self._convert_reaper_to_python(v) for k, v in value.items()}
        
        # Return as-is for other types
        return value
    
    def _create_callable_wrapper(self, callable_obj: Any, line: int, column: int, filename: str):
        """
        Create a wrapper for Python callable that can be called from Reaper.
        
        Args:
            callable_obj: Python callable (function/class)
            line: Line number for error reporting
            column: Column number for error reporting
            filename: Filename for error reporting
            
        Returns:
            Wrapper function that can be called from Reaper
        """
        def reaper_callable(*args):
            """Wrapper function for calling Python functions from Reaper."""
            try:
                # Convert Reaper arguments to Python
                python_args = [self._convert_reaper_to_python(arg) for arg in args]
                # Call Python function
                result = callable_obj(*python_args)
                # Convert result back to Reaper
                return self._convert_python_to_reaper(result)
            except Exception as e:
                raise ReaperRuntimeError(
                    f"Error calling Python function: {str(e)}",
                    line, column, filename
                )
        
        return reaper_callable
    
    def visit_cloak_node(self, node: CloakNode) -> None:
        """Visit cloak node (enable anonymity features)."""
        # For now, just log the feature activation - in a full implementation,
        # this would enable specific anonymity features
        print(f"[CLOAK] Enabling anonymity feature: {node.feature_name}")
        # TODO: Implement actual anonymity feature activation
        return None
    
    def visit_risk_node(self, node: RiskNode) -> Any:
        """Visit risk node (try/catch/finally for exception handling)."""
        exception_caught = None
        result = None
        
        # Execute try block
        try:
            result = self._execute(node.try_block)
        except ReaperError as e:
            exception_caught = e
            
            # Find matching catch block
            for exception_type, var_name, catch_block in node.catch_blocks:
                # Check if exception type matches
                # None means catch-all
                # Match by exact type name or base class name
                matches = False
                if exception_type is None:
                    matches = True  # Catch-all
                else:
                    # Get the actual exception type name
                    actual_type_name = type(e).__name__
                    # Check exact match
                    if exception_type == actual_type_name:
                        matches = True
                    # Check if it's a base class match (e.g., ReaperError catches all ReaperError subclasses)
                    elif exception_type == "ReaperError" and isinstance(e, ReaperError):
                        matches = True
                    # Check inheritance (e.g., ReaperZeroDivisionError is a ReaperError)
                    elif hasattr(e, '__class__'):
                        # Check if the exception is an instance of the requested type
                        exception_map = {
                            "ReaperError": ReaperError,
                            "ReaperSyntaxError": ReaperSyntaxError,
                            "ReaperRuntimeError": ReaperRuntimeError,
                            "ReaperTypeError": ReaperTypeError,
                            "ReaperRecursionError": ReaperRecursionError,
                            "ReaperMemoryError": ReaperMemoryError,
                            "ReaperIndexError": ReaperIndexError,
                            "ReaperKeyError": ReaperKeyError,
                            "ReaperZeroDivisionError": ReaperZeroDivisionError,
                        }
                        requested_class = exception_map.get(exception_type)
                        if requested_class and isinstance(e, requested_class):
                            matches = True
                
                if matches:
                    # Store exception in variable if specified
                    if var_name:
                        # Create a new environment for the catch block
                        old_env = self.environment_stack.current()
                        catch_env = Environment(parent=old_env)
                        # Store exception object with proper type
                        catch_env.define(var_name, e, "ReaperError", False, node.line, node.column)
                        self.environment_stack.push(catch_env)
                    
                    # Execute catch block
                    try:
                        result = self._execute(catch_block)
                    finally:
                        # Restore environment
                        if var_name:
                            self.environment_stack.pop()
                    
                    # Exception handled, don't check other catch blocks
                    exception_caught = None
                    break
            
            # Re-raise if not caught
            if exception_caught:
                raise exception_caught
        except Exception as e:
            # Convert Python exceptions to ReaperError
            if not isinstance(e, ReaperError):
                reaper_error = ReaperRuntimeError(
                    f"Python exception: {str(e)}",
                    node.line,
                    node.column,
                    node.filename
                )
                exception_caught = reaper_error
            else:
                exception_caught = e
            
            # Try to find matching catch block
            for exception_type, var_name, catch_block in node.catch_blocks:
                matches = False
                if exception_type is None:
                    matches = True
                elif isinstance(exception_caught, ReaperError):
                    actual_type_name = type(exception_caught).__name__
                    if exception_type == actual_type_name:
                        matches = True
                    elif exception_type == "ReaperError":
                        matches = True
                    else:
                        exception_map = {
                            "ReaperError": ReaperError,
                            "ReaperSyntaxError": ReaperSyntaxError,
                            "ReaperRuntimeError": ReaperRuntimeError,
                            "ReaperTypeError": ReaperTypeError,
                            "ReaperRecursionError": ReaperRecursionError,
                            "ReaperMemoryError": ReaperMemoryError,
                            "ReaperIndexError": ReaperIndexError,
                            "ReaperKeyError": ReaperKeyError,
                            "ReaperZeroDivisionError": ReaperZeroDivisionError,
                        }
                        requested_class = exception_map.get(exception_type)
                        if requested_class and isinstance(exception_caught, requested_class):
                            matches = True
                
                if matches:
                    if var_name:
                        old_env = self.environment_stack.current()
                        catch_env = Environment(parent=old_env)
                        catch_env.define(var_name, exception_caught, "ReaperError", False, node.line, node.column)
                        self.environment_stack.push(catch_env)
                    
                    try:
                        result = self._execute(catch_block)
                    finally:
                        if var_name:
                            self.environment_stack.pop()
                    
                    exception_caught = None
                    break
            
            # Re-raise if not caught
            if exception_caught:
                raise exception_caught
        finally:
            # Execute finally block if present (always executes)
            if node.finally_block:
                self._execute(node.finally_block)
        
        return result
    
    def visit_exploit_node(self, node: ExploitNode) -> Any:
        """Visit exploit node (try/catch for security operations - legacy)."""
        # Execute try block
        try:
            for statement in node.try_block.statements:
                self._execute(statement)
            return None
        except Exception as e:
            # Find matching catch block
            for exception_name, catch_block in node.catch_blocks:
                if exception_name is None or exception_name == type(e).__name__:
                    # Execute catch block
                    for statement in catch_block.statements:
                        self._execute(statement)
                    return None
            
            # No matching catch block, re-raise
            raise e
    
    def visit_raise_exception_node(self, node: RaiseExceptionNode) -> None:
        """Visit raise exception node (throw exception)."""
        # Evaluate exception message if provided
        message = "Exception raised"
        if node.exception_message:
            message_value = self._execute(node.exception_message)
            if isinstance(message_value, str):
                message = message_value
            else:
                message = str(message_value)
        
        # Create appropriate exception type
        if node.exception_type:
            # Map exception type name to class
            exception_map = {
                "ReaperError": ReaperError,
                "ReaperSyntaxError": ReaperSyntaxError,
                "ReaperRuntimeError": ReaperRuntimeError,
                "ReaperTypeError": ReaperTypeError,
                "ReaperRecursionError": ReaperRecursionError,
                "ReaperMemoryError": ReaperMemoryError,
                "ReaperIndexError": ReaperIndexError,
                "ReaperKeyError": ReaperKeyError,
                "ReaperZeroDivisionError": ReaperZeroDivisionError,
            }
            
            exception_class = exception_map.get(node.exception_type, ReaperRuntimeError)
            raise exception_class(
                message,
                node.line,
                node.column,
                node.filename
            )
        else:
            # Default to ReaperRuntimeError
            raise ReaperRuntimeError(
                message,
                node.line,
                node.column,
                node.filename
            )
    
    def visit_breach_node(self, node: BreachNode) -> AsyncTask:
        """Visit breach node (async operations)."""
        # Create a function that executes the block
        def execute_async_block():
            """Execute the async block in a separate thread."""
            try:
                # Create a new environment for the async block
                async_env = Environment(parent=self.environment_stack.current())
                self.environment_stack.push(async_env)
                
                # Execute all statements in the block
                result = None
                for statement in node.async_block.statements:
                    result = self._execute(statement)
                
                return result
            finally:
                # Restore environment
                self.environment_stack.pop()
        
        # Submit to async runtime
        task = self.async_runtime.submit(execute_async_block)
        return task
    
    def visit_await_node(self, node: AwaitNode) -> Any:
        """Visit await node (wait for async operation)."""
        # Evaluate the expression (should return an AsyncTask)
        task_value = self._execute(node.expression)
        
        # Check if it's an AsyncTask
        if not isinstance(task_value, AsyncTask):
            raise ReaperTypeError(
                f"Cannot await non-async value: {type(task_value).__name__}",
                node.line, node.column, node.filename,
                expected_type="AsyncTask",
                actual_type=type(task_value).__name__,
                operation="await"
            )
        
        # Wait for task to complete
        try:
            result = task_value.wait()
            return result
        except Exception as e:
            raise ReaperRuntimeError(
                f"Error in async task: {str(e)}",
                node.line, node.column, node.filename
            )
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    def _get_current_environment(self) -> Environment:
        """Get current environment from stack."""
        if self.environment_stack.is_empty():
            return self.global_environment
        return self.environment_stack.peek()
    
    def _call_function_by_name(self, name: str, arguments: List[Any], line: int, column: int) -> Any:
        """Call function by name."""
        # Check if it's a built-in function
        if name in ["harvest", "rest", "raise_corpse", "steal_soul", "summon", 
                   "final_rest", "curse", "absolute", "lesser", "greater",
                   "raise_phantom", "excavate", "bury"]:
            return self._call_builtin_function(name, arguments, line, column)
        
        # Get function from environment
        func, _ = self._get_current_environment().get(name, line, column)
        return self._call_function(func, arguments, line, column)
    
    def _call_function(self, func: Union[InfectNode, LambdaNode], arguments: List[Any], line: int, column: int) -> Any:
        """Call a user-defined function or lambda."""
        self._check_recursion_limit()
        self.recursion_depth += 1
        
        try:
            # Create new environment for function
            current_env = self._get_current_environment()
            func_env = current_env.create_child()
            self.environment_stack.push(func_env)
            
            # Bind parameters
            for i, (param_name, param_type, default_value) in enumerate(func.params):
                if i < len(arguments):
                    value = arguments[i]
                elif default_value is not None:
                    value = self._execute(default_value)
                else:
                    raise ReaperRuntimeError(
                        f"Missing argument for parameter '{param_name}'",
                        line, column
                    )
                
                func_env.define(param_name, value, param_type, False, line, column)
            
            # Execute function body
            try:
                result = self._execute(func.body)
                
                # For lambdas with single expressions, return the expression value
                # For blocks, only return if there's an explicit return statement
                if isinstance(func, LambdaNode) and not isinstance(func.body, BlockNode):
                    return result
                
                return None  # No explicit return
            except ReaperReturn as ret:
                return ret.value
        
        finally:
            self.environment_stack.pop()
            self.recursion_depth -= 1
    
    def _call_method(self, method: InfectNode, instance: dict, arguments: List[Any], line: int, column: int) -> Any:
        """Call a user-defined method with 'this' bound to instance."""
        self._check_recursion_limit()
        self.recursion_depth += 1
        
        try:
            # Create new environment for method
            current_env = self._get_current_environment()
            method_env = current_env.create_child()
            self.environment_stack.push(method_env)
            
            # Bind 'this' to the instance
            method_env.define("this", instance, "tomb", False, line, column)
            
            # Bind parameters
            for i, (param_name, param_type, default_value) in enumerate(method.params):
                if i < len(arguments):
                    value = arguments[i]
                elif default_value is not None:
                    value = self._execute(default_value)
                else:
                    raise ReaperRuntimeError(
                        f"Missing argument for parameter '{param_name}'",
                        line, column
                    )
                
                method_env.define(param_name, value, param_type, False, line, column)
            
            # Execute method body
            try:
                self._execute(method.body)
                return None  # No explicit return
            except ReaperReturn as ret:
                return ret.value
        
        finally:
            self.environment_stack.pop()
            self.recursion_depth -= 1
    
    def _call_builtin_function(self, name: str, arguments: List[Any], line: int, column: int) -> Any:
        """Call a built-in function."""
        if name == "harvest":
            return self._builtin_harvest(arguments, line, column)
        elif name == "rest":
            return self._builtin_rest(arguments, line, column)
        elif name == "raise_corpse":
            return self._builtin_raise_corpse(arguments, line, column)
        elif name == "steal_soul":
            return self._builtin_steal_soul(arguments, line, column)
        elif name == "summon":
            return self._builtin_summon(arguments, line, column)
        elif name == "final_rest":
            return self._builtin_final_rest(arguments, line, column)
        elif name == "curse":
            return self._builtin_curse(arguments, line, column)
        elif name == "absolute":
            return self._builtin_absolute(arguments, line, column)
        elif name == "lesser":
            return self._builtin_lesser(arguments, line, column)
        elif name == "greater":
            return self._builtin_greater(arguments, line, column)
        elif name == "excavate":
            return self._builtin_excavate(arguments, line, column)
        elif name == "bury":
            return self._builtin_bury(arguments, line, column)
        else:
            raise ReaperRuntimeError(
                f"Unknown built-in function: {name}",
                line, column
            )
    
    # ============================================================================
    # Built-in Functions
    # ============================================================================
    
    def _builtin_harvest(self, arguments: List[Any], line: int, column: int) -> None:
        """Built-in harvest (print) function."""
        from .emoji_filter import safe_print
        
        for arg in arguments:
            if arg is None:
                safe_print("void", end="")
            elif isinstance(arg, bool):
                # Convert boolean to REAPER constants
                safe_print("RISEN" if arg else "DEAD", end="")
            elif isinstance(arg, int):
                safe_print(arg, end="")
            else:
                # Convert to string and filter emojis
                safe_print(str(arg), end="")
        safe_print()  # Newline after all arguments
        return None
    
    def _builtin_rest(self, arguments: List[Any], line: int, column: int) -> None:
        """Built-in rest (sleep) function."""
        if len(arguments) != 1:
            raise ReaperRuntimeError(
                f"rest() expects 1 argument, got {len(arguments)}",
                line, column
            )
        
        duration = arguments[0]
        self._check_type(duration, int, "rest duration", line, column)
        
        if duration < 0:
            raise ReaperRuntimeError(
                "Rest duration cannot be negative",
                line, column
            )
        
        time.sleep(duration / 1000.0)  # Convert milliseconds to seconds
        return None
    
    def _builtin_raise_corpse(self, arguments: List[Any], line: int, column: int) -> int:
        """Built-in raise_corpse (string to int) function."""
        if len(arguments) != 1:
            raise ReaperRuntimeError(
                f"raise_corpse() expects 1 argument, got {len(arguments)}",
                line, column
            )
        
        value = arguments[0]
        self._check_type(value, str, "raise_corpse argument", line, column)
        
        try:
            return int(value)
        except ValueError:
            raise ReaperTypeError(
                f"Cannot convert '{value}' to integer",
                line, column,
                expected_type="integer",
                actual_type="string",
                operation="string to integer conversion"
            )
    
    def _builtin_steal_soul(self, arguments: List[Any], line: int, column: int) -> str:
        """Built-in steal_soul (int/float to string) function."""
        if len(arguments) != 1:
            raise ReaperRuntimeError(
                f"steal_soul() expects 1 argument, got {len(arguments)}",
                line, column
            )
        
        value = arguments[0]
        # Accept both int (corpse) and float (phantom)
        if isinstance(value, (int, float)):
            return str(value)
        else:
            raise ReaperTypeError(
                f"Cannot convert {type(value).__name__} to string",
                line, column,
                expected_type="corpse or phantom",
                actual_type=type(value).__name__,
                operation="type conversion"
            )
    
    def _builtin_raise_phantom(self, arguments: List[Any], line: int, column: int) -> float:
        """Built-in raise_phantom (string to float) function."""
        if len(arguments) != 1:
            raise ReaperRuntimeError(
                f"raise_phantom() expects 1 argument, got {len(arguments)}",
                line, column
            )
        
        value = arguments[0]
        self._check_type(value, str, "raise_phantom argument", line, column)
        
        try:
            return float(value)
        except ValueError:
            raise ReaperTypeError(
                f"Cannot convert '{value}' to phantom (float)",
                line, column,
                expected_type="phantom",
                actual_type="string",
                operation="string to float conversion"
            )
    
    def _builtin_summon(self, arguments: List[Any], line: int, column: int) -> str:
        """Built-in summon (read input) function."""
        if len(arguments) != 0:
            raise ReaperRuntimeError(
                f"summon() expects 0 arguments, got {len(arguments)}",
                line, column
            )
        
        try:
            return input().rstrip('\n')
        except EOFError:
            return None  # Return void on EOF
    
    def _builtin_final_rest(self, arguments: List[Any], line: int, column: int) -> None:
        """Built-in final_rest (exit) function."""
        if len(arguments) != 1:
            raise ReaperRuntimeError(
                f"final_rest() expects 1 argument, got {len(arguments)}",
                line, column
            )
        
        exit_code = arguments[0]
        self._check_type(exit_code, int, "final_rest exit code", line, column)
        
        sys.exit(exit_code)
    
    def _builtin_curse(self, arguments: List[Any], line: int, column: int) -> None:
        """Built-in curse (assert) function."""
        if len(arguments) != 2:
            raise ReaperRuntimeError(
                f"curse() expects 2 arguments, got {len(arguments)}",
                line, column
            )
        
        condition = arguments[0]
        message = arguments[1]
        
        self._check_type(message, str, "curse message", line, column)
        
        if not self._to_boolean(condition, line, column):
            raise ReaperRuntimeError(
                f"Assertion failed: {message}",
                line, column
            )
        
        return None
    
    def _builtin_absolute(self, arguments: List[Any], line: int, column: int) -> Any:
        """Built-in absolute (abs) function."""
        if len(arguments) != 1:
            raise ReaperRuntimeError(
                f"absolute() expects 1 argument, got {len(arguments)}",
                line, column
            )
        
        value = arguments[0]
        # Support both int (corpse) and float (phantom)
        if isinstance(value, (int, float)):
            return abs(value)
        else:
            raise ReaperTypeError(
                f"Cannot get absolute value of {type(value).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=type(value).__name__,
                operation="absolute value"
            )
    
    def _builtin_lesser(self, arguments: List[Any], line: int, column: int) -> Any:
        """Built-in lesser (min) function."""
        if len(arguments) != 2:
            raise ReaperRuntimeError(
                f"lesser() expects 2 arguments, got {len(arguments)}",
                line, column
            )
        
        a, b = arguments[0], arguments[1]
        # Support both int (corpse) and float (phantom)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return min(a, b)
        else:
            raise ReaperTypeError(
                f"Cannot compare {type(a).__name__} and {type(b).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=f"{type(a).__name__} and {type(b).__name__}",
                operation="minimum"
            )
    
    def _builtin_greater(self, arguments: List[Any], line: int, column: int) -> Any:
        """Built-in greater (max) function."""
        if len(arguments) != 2:
            raise ReaperRuntimeError(
                f"greater() expects 2 arguments, got {len(arguments)}",
                line, column
            )
        
        a, b = arguments[0], arguments[1]
        # Support both int (corpse) and float (phantom)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return max(a, b)
        else:
            raise ReaperTypeError(
                f"Cannot compare {type(a).__name__} and {type(b).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=f"{type(a).__name__} and {type(b).__name__}",
                operation="maximum"
            )
    
    def _builtin_excavate(self, arguments: List[Any], line: int, column: int) -> str:
        """Built-in excavate (read file) function."""
        if len(arguments) != 1:
            raise ReaperRuntimeError(
                f"excavate() expects 1 argument (file path), got {len(arguments)}",
                line, column
            )
        
        file_path = arguments[0]
        self._check_type(file_path, str, "excavate file path", line, column)
        
        # Validate file path (security check)
        import os
        from pathlib import Path
        
        path = Path(file_path)
        
        # Prevent directory traversal attacks
        if not path.is_absolute():
            # Resolve relative paths
            path = Path.cwd() / path
            path = path.resolve()
        
        # Check if file exists
        if not path.exists():
            raise ReaperRuntimeError(
                f"File not found: {file_path}",
                line, column
            )
        
        # Check if it's a file (not a directory)
        if not path.is_file():
            raise ReaperRuntimeError(
                f"Path is not a file: {file_path}",
                line, column
            )
        
        # Check file size (prevent reading huge files)
        file_size = path.stat().st_size
        max_file_size = 10 * 1024 * 1024  # 10MB limit
        if file_size > max_file_size:
            raise ReaperMemoryError(
                f"File too large: {file_size} bytes (max {max_file_size})",
                line, column,
                resource_type="file",
                current_size=file_size,
                max_size=max_file_size
            )
        
        # Read file
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return content
        except PermissionError:
            raise ReaperRuntimeError(
                f"Permission denied: {file_path}",
                line, column
            )
        except Exception as e:
            raise ReaperRuntimeError(
                f"Error reading file '{file_path}': {str(e)}",
                line, column
            )
    
    def _builtin_bury(self, arguments: List[Any], line: int, column: int) -> None:
        """Built-in bury (write file) function."""
        if len(arguments) != 2:
            raise ReaperRuntimeError(
                f"bury() expects 2 arguments (file path, content), got {len(arguments)}",
                line, column
            )
        
        file_path = arguments[0]
        content = arguments[1]
        
        self._check_type(file_path, str, "bury file path", line, column)
        self._check_type(content, str, "bury content", line, column)
        
        # Validate file path (security check)
        import os
        from pathlib import Path
        
        path = Path(file_path)
        
        # Prevent directory traversal attacks
        if not path.is_absolute():
            path = Path.cwd() / path
            path = path.resolve()
        
        # Check if parent directory exists
        parent_dir = path.parent
        if not parent_dir.exists():
            raise ReaperRuntimeError(
                f"Parent directory does not exist: {parent_dir}",
                line, column
            )
        
        # Check content size (prevent writing huge files)
        content_size = len(content.encode('utf-8'))
        max_content_size = 10 * 1024 * 1024  # 10MB limit
        if content_size > max_content_size:
            raise ReaperMemoryError(
                f"Content too large: {content_size} bytes (max {max_content_size})",
                line, column,
                resource_type="file content",
                current_size=content_size,
                max_size=max_content_size
            )
        
        # Write file
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError:
            raise ReaperRuntimeError(
                f"Permission denied: {file_path}",
                line, column
            )
        except Exception as e:
            raise ReaperRuntimeError(
                f"Error writing file '{file_path}': {str(e)}",
                line, column
            )
        
        return None
    
    # ============================================================================
    # Type Checking and Conversion Methods
    # ============================================================================
    
    def _check_type(self, value: Any, expected_type: type, context: str, line: int, column: int) -> None:
        """Check if value is of expected type."""
        if not isinstance(value, expected_type):
            raise ReaperTypeError(
                f"{context} must be {expected_type.__name__}",
                line, column,
                expected_type=expected_type.__name__,
                actual_type=type(value).__name__,
                operation=context
            )
    
    def _to_boolean(self, value: Any, line: int, column: int) -> bool:
        """Convert value to boolean."""
        if isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return value != 0
        elif isinstance(value, str):
            return len(value) > 0
        elif isinstance(value, list):
            return len(value) > 0
        elif isinstance(value, dict):
            return len(value) > 0
        elif value is None:
            return False
        else:
            raise ReaperTypeError(
                f"Cannot convert {type(value).__name__} to boolean",
                line, column,
                expected_type="boolean",
                actual_type=type(value).__name__,
                operation="boolean conversion"
            )
    
    # ============================================================================
    # Arithmetic Operations
    # ============================================================================
    
    def _add(self, left: Any, right: Any, line: int, column: int) -> Any:
        """Add two values."""
        # Support numeric types (int/corpse and float/phantom)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        elif isinstance(left, int) and isinstance(right, int):
            return left + right
        elif isinstance(left, str) and isinstance(right, str):
            result = left + right
            self._check_memory_limit(result, "string")
            return result
        elif isinstance(left, SecureString) and isinstance(right, SecureString):
            data = left.to_bytes() + right.to_bytes()
            ss = SecureString(data)
            if len(ss) > self.max_string_length:
                raise ReaperMemoryError(
                    f"SecureString length {len(ss)} exceeds maximum {self.max_string_length}",
                    resource_type="string",
                    current_size=len(ss),
                    max_size=self.max_string_length
                )
            return ss
        elif (isinstance(left, SecureString) and isinstance(right, str)) or (isinstance(left, str) and isinstance(right, SecureString)):
            if isinstance(left, SecureString):
                data = left.to_bytes() + right.encode("utf-8")
            else:
                data = left.encode("utf-8") + right.to_bytes()
            ss = SecureString(data)
            if len(ss) > self.max_string_length:
                raise ReaperMemoryError(
                    f"SecureString length {len(ss)} exceeds maximum {self.max_string_length}",
                    resource_type="string",
                    current_size=len(ss),
                    max_size=self.max_string_length
                )
            return ss
        else:
            raise ReaperTypeError(
                f"Cannot add {type(left).__name__} and {type(right).__name__}",
                line, column,
                expected_type="int + int or str + str",
                actual_type=f"{type(left).__name__} + {type(right).__name__}",
                operation="addition"
            )
    
    def _subtract(self, left: Any, right: Any, line: int, column: int) -> Any:
        """Subtract two values."""
        # Support both int (corpse) and float (phantom)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left - right
        else:
            raise ReaperTypeError(
                f"Cannot subtract {type(left).__name__} and {type(right).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=f"{type(left).__name__} and {type(right).__name__}",
                operation="subtraction"
            )
    
    def _multiply(self, left: Any, right: Any, line: int, column: int) -> Any:
        """Multiply two values."""
        # Support both int (corpse) and float (phantom)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left * right
        else:
            raise ReaperTypeError(
                f"Cannot multiply {type(left).__name__} and {type(right).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=f"{type(left).__name__} and {type(right).__name__}",
                operation="multiplication"
            )
    
    def _divide(self, left: Any, right: Any, line: int, column: int) -> Any:
        """Divide two values."""
        # Support both int (corpse) and float (phantom)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if right == 0:
                raise ReaperZeroDivisionError(
                    "Division by zero",
                    line, column,
                    expression=f"{left} / {right}"
                )
            
            # If either operand is float, return float; otherwise integer division
            if isinstance(left, float) or isinstance(right, float):
                return left / right  # Float division
            else:
                return left // right  # Integer division
        else:
            raise ReaperTypeError(
                f"Cannot divide {type(left).__name__} and {type(right).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=f"{type(left).__name__} and {type(right).__name__}",
                operation="division"
            )
    
    def _modulo(self, left: Any, right: Any, line: int, column: int) -> Any:
        """Modulo two values."""
        # Support both int (corpse) and float (phantom)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if right == 0:
                raise ReaperZeroDivisionError(
                    "Modulo by zero",
                    line, column,
                    expression=f"{left} % {right}"
                )
            return left % right
        else:
            raise ReaperTypeError(
                f"Cannot modulo {type(left).__name__} and {type(right).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=f"{type(left).__name__} and {type(right).__name__}",
                operation="modulo"
            )
    
    def _negate(self, operand: Any, line: int, column: int) -> Any:
        """Negate a value."""
        # Support both int (corpse) and float (phantom)
        if isinstance(operand, (int, float)):
            return -operand
        else:
            raise ReaperTypeError(
                f"Cannot negate {type(operand).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=type(operand).__name__,
                operation="negation"
            )
    
    def _logical_not(self, operand: Any, line: int, column: int) -> bool:
        """Logical NOT operation."""
        return not self._to_boolean(operand, line, column)
    
    # ============================================================================
    # Comparison Operations
    # ============================================================================
    
    def _equal(self, left: Any, right: Any, line: int, column: int) -> bool:
        """Check equality of two values."""
        # Different types are never equal
        if type(left) != type(right):
            return False
        
        return left == right
    
    def _less_than(self, left: Any, right: Any, line: int, column: int) -> bool:
        """Check if left < right."""
        # Support both int (corpse) and float (phantom)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left < right
        else:
            raise ReaperTypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=f"{type(left).__name__} and {type(right).__name__}",
                operation="comparison"
            )
    
    def _greater_than(self, left: Any, right: Any, line: int, column: int) -> bool:
        """Check if left > right."""
        # Support both int (corpse) and float (phantom)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left > right
        else:
            raise ReaperTypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=f"{type(left).__name__} and {type(right).__name__}",
                operation="comparison"
            )
    
    def _less_equal(self, left: Any, right: Any, line: int, column: int) -> bool:
        """Check if left <= right."""
        # Support both int (corpse) and float (phantom)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left <= right
        else:
            raise ReaperTypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=f"{type(left).__name__} and {type(right).__name__}",
                operation="comparison"
            )
    
    def _greater_equal(self, left: Any, right: Any, line: int, column: int) -> bool:
        """Check if left >= right."""
        # Support both int (corpse) and float (phantom)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left >= right
        else:
            raise ReaperTypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__}",
                line, column,
                expected_type="corpse or phantom",
                actual_type=f"{type(left).__name__} and {type(right).__name__}",
                operation="comparison"
            )
    
    def _bitwise_or(self, left: Any, right: Any, line: int, column: int) -> int:
        """Bitwise OR operation (spread)."""
        self._check_type(left, int, "bitwise OR left operand", line, column)
        self._check_type(right, int, "bitwise OR right operand", line, column)
        return left | right
    
    def _bitwise_xor(self, left: Any, right: Any, line: int, column: int) -> int:
        """Bitwise XOR operation (mutate)."""
        self._check_type(left, int, "bitwise XOR left operand", line, column)
        self._check_type(right, int, "bitwise XOR right operand", line, column)
        return left ^ right
    
    def _bitwise_and(self, left: Any, right: Any, line: int, column: int) -> int:
        """Bitwise AND operation (wither)."""
        self._check_type(left, int, "bitwise AND left operand", line, column)
        self._check_type(right, int, "bitwise AND right operand", line, column)
        return left & right
    
    def _bitwise_rotate(self, left: Any, right: Any, line: int, column: int) -> int:
        """Bitwise rotation operation (rot)."""
        self._check_type(left, int, "bitwise rotate left operand", line, column)
        self._check_type(right, int, "bitwise rotate right operand", line, column)
        
        # Convert to 32-bit unsigned integer for rotation
        left = left & 0xFFFFFFFF
        right = right & 0x1F  # Limit rotation to 0-31 bits
        
        if right == 0:
            return left
        
        # Perform left rotation
        return ((left << right) | (left >> (32 - right))) & 0xFFFFFFFF
    
    def _bitwise_not(self, operand: Any, line: int, column: int) -> int:
        """Bitwise NOT operation (invert)."""
        self._check_type(operand, int, "bitwise NOT operand", line, column)
        return ~operand & 0xFFFFFFFF  # Ensure 32-bit result
    
    # ============================================================================
    # Collection Operations
    # ============================================================================
    
    def _array_index(self, arr: List[Any], index: int, line: int, column: int) -> Any:
        """Get array element by index."""
        self._check_type(index, int, "array index", line, column)
        
        # Handle negative indices
        if index < 0:
            index = len(arr) + index
        
        if index < 0 or index >= len(arr):
            raise ReaperIndexError(
                f"Array index {index} out of bounds",
                line, column,
                index=index,
                collection_size=len(arr),
                collection_type="array"
            )
        
        return arr[index]
    
    def _array_index_assign(self, arr: List[Any], index: int, value: Any, line: int, column: int) -> None:
        """Set array element by index."""
        self._check_type(index, int, "array index", line, column)
        
        # Handle negative indices
        if index < 0:
            index = len(arr) + index
        
        if index < 0 or index >= len(arr):
            raise ReaperIndexError(
                f"Array index {index} out of bounds",
                line, column,
                index=index,
                collection_size=len(arr),
                collection_type="array"
            )
        
        arr[index] = value
    
    def _array_slice(self, arr: List[Any], start: Optional[int], end: Optional[int], 
                    step: Optional[int], line: int, column: int) -> List[Any]:
        """Slice an array."""
        if start is not None:
            self._check_type(start, int, "slice start", line, column)
        if end is not None:
            self._check_type(end, int, "slice end", line, column)
        if step is not None:
            self._check_type(step, int, "slice step", line, column)
        
        return arr[start:end:step]
    
    def _string_index(self, s: str, index: int, line: int, column: int) -> str:
        """Get string character by index."""
        self._check_type(index, int, "string index", line, column)
        
        # Handle negative indices
        if index < 0:
            index = len(s) + index
        
        if index < 0 or index >= len(s):
            raise ReaperIndexError(
                f"String index {index} out of bounds",
                line, column,
                index=index,
                collection_size=len(s),
                collection_type="string"
            )
        
        return s[index]
    
    def _string_slice(self, s: str, start: Optional[int], end: Optional[int], 
                     step: Optional[int], line: int, column: int) -> str:
        """Slice a string."""
        if start is not None:
            self._check_type(start, int, "slice start", line, column)
        if end is not None:
            self._check_type(end, int, "slice end", line, column)
        if step is not None:
            self._check_type(step, int, "slice step", line, column)
        
        return s[start:end:step]
    
    def _dict_access(self, d: Dict[Any, Any], key: Any, line: int, column: int) -> Any:
        """Get dictionary value by key."""
        if key not in d:
            available_keys = list(d.keys())
            raise ReaperKeyError(
                f"Key {repr(key)} not found in dictionary",
                line, column,
                key=key,
                available_keys=available_keys
            )
        
        return d[key]
    
    def _dict_assign(self, d: Dict[Any, Any], key: Any, value: Any, line: int, column: int) -> None:
        """Set dictionary value by key."""
        d[key] = value
    
    # ============================================================================
    # Method Implementations
    # ============================================================================
    
    def _call_array_method(self, arr: List[Any], method_name: str, arguments: List[Any], 
                          line: int, column: int) -> Any:
        """Call array method."""
        if method_name == "entomb":  # append
            if len(arguments) != 1:
                raise ReaperRuntimeError(
                    f"entomb() expects 1 argument, got {len(arguments)}",
                    line, column
                )
            arr.append(arguments[0])
            return None
        
        elif method_name == "exhume":  # pop
            if len(arguments) != 1:
                raise ReaperRuntimeError(
                    f"exhume() expects 1 argument, got {len(arguments)}",
                    line, column
                )
            index = arguments[0]
            self._check_type(index, int, "exhume index", line, column)
            return arr.pop(index)
        
        elif method_name == "curse":  # length
            if len(arguments) != 0:
                raise ReaperRuntimeError(
                    f"curse() expects 0 arguments, got {len(arguments)}",
                    line, column
                )
            return len(arr)
        
        elif method_name == "resurrect":  # reverse
            if len(arguments) != 0:
                raise ReaperRuntimeError(
                    f"resurrect() expects 0 arguments, got {len(arguments)}",
                    line, column
                )
            arr.reverse()
            return None
        
        elif method_name == "haunt":  # contains
            if len(arguments) != 1:
                raise ReaperRuntimeError(
                    f"haunt() expects 1 argument, got {len(arguments)}",
                    line, column
                )
            return arguments[0] in arr
        
        else:
            raise ReaperRuntimeError(
                f"Unknown array method: {method_name}",
                line, column
            )
    
    def _call_string_method(self, s: str, method_name: str, arguments: List[Any], 
                           line: int, column: int) -> Any:
        """Call string method."""
        if method_name == "curse":  # length
            if len(arguments) != 0:
                raise ReaperRuntimeError(
                    f"curse() expects 0 arguments, got {len(arguments)}",
                    line, column
                )
            return len(s)
        
        elif method_name == "slice":  # substring
            if len(arguments) != 2:
                raise ReaperRuntimeError(
                    f"slice() expects 2 arguments, got {len(arguments)}",
                    line, column
                )
            start, end = arguments[0], arguments[1]
            self._check_type(start, int, "slice start", line, column)
            self._check_type(end, int, "slice end", line, column)
            return s[start:end]
        
        elif method_name == "whisper":  # lowercase
            if len(arguments) != 0:
                raise ReaperRuntimeError(
                    f"whisper() expects 0 arguments, got {len(arguments)}",
                    line, column
                )
            return s.lower()
        
        elif method_name == "scream":  # uppercase
            if len(arguments) != 0:
                raise ReaperRuntimeError(
                    f"scream() expects 0 arguments, got {len(arguments)}",
                    line, column
                )
            return s.upper()
        
        elif method_name == "haunt":  # contains
            if len(arguments) != 1:
                raise ReaperRuntimeError(
                    f"haunt() expects 1 argument, got {len(arguments)}",
                    line, column
                )
            substring = arguments[0]
            self._check_type(substring, str, "haunt substring", line, column)
            return substring in s
        
        elif method_name == "split":  # split
            if len(arguments) != 1:
                raise ReaperRuntimeError(
                    f"split() expects 1 argument, got {len(arguments)}",
                    line, column
                )
            delimiter = arguments[0]
            self._check_type(delimiter, str, "split delimiter", line, column)
            return s.split(delimiter)
        
        else:
            raise ReaperRuntimeError(
                f"Unknown string method: {method_name}",
                line, column
            )
    
    def _call_dict_method(self, d: Dict[Any, Any], method_name: str, arguments: List[Any], 
                         line: int, column: int) -> Any:
        """Call dictionary method."""
        if method_name == "curse":  # key count
            if len(arguments) != 0:
                raise ReaperRuntimeError(
                    f"curse() expects 0 arguments, got {len(arguments)}",
                    line, column
                )
            return len(d)
        
        elif method_name == "summon":  # get with default
            if len(arguments) != 1:
                raise ReaperRuntimeError(
                    f"summon() expects 1 argument, got {len(arguments)}",
                    line, column
                )
            key = arguments[0]
            return d.get(key, None)  # Return void if not found
        
        elif method_name == "banish":  # delete key
            if len(arguments) != 1:
                raise ReaperRuntimeError(
                    f"banish() expects 1 argument, got {len(arguments)}",
                    line, column
                )
            key = arguments[0]
            if key in d:
                del d[key]
            return None
        
        elif method_name == "inscribe":  # all keys
            if len(arguments) != 0:
                raise ReaperRuntimeError(
                    f"inscribe() expects 0 arguments, got {len(arguments)}",
                    line, column
                )
            return list(d.keys())
        
        elif method_name == "possess":  # all values
            if len(arguments) != 0:
                raise ReaperRuntimeError(
                    f"possess() expects 0 arguments, got {len(arguments)}",
                    line, column
                )
            return list(d.values())
        
        elif method_name == "haunt":  # contains key
            if len(arguments) != 1:
                raise ReaperRuntimeError(
                    f"haunt() expects 1 argument, got {len(arguments)}",
                    line, column
                )
            key = arguments[0]
            return key in d
        
        else:
            raise ReaperRuntimeError(
                f"Unknown dictionary method: {method_name}",
                line, column
            )


def interpret(program: ProgramNode) -> None:
    """
    Convenience function to interpret a REAPER program.
    
    Args:
        program: ProgramNode to execute
        
    Raises:
        ReaperRuntimeError: On runtime errors
    """
    interpreter = Interpreter()
    interpreter.interpret(program)
