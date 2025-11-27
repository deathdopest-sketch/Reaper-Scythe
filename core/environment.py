"""
REAPER Language Environment Management

This module implements the environment system for variable and function storage,
including lexical scoping, closures, and built-in constants.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from .tokens import RESERVED_IDENTIFIERS, BUILTIN_CONSTANTS
from .reaper_error import ReaperRuntimeError


class Environment:
    """
    Environment for storing variables, functions, and constants.
    
    Supports lexical scoping with parent environment references,
    constant enforcement, and built-in initialization.
    """
    
    def __init__(self, parent: Optional['Environment'] = None, filename: str = "<unknown>"):
        """
        Initialize environment.
        
        Args:
            parent: Parent environment for lexical scoping
            filename: Source filename for error reporting
        """
        self.parent = parent
        self.filename = filename
        # Storage: {name: (value, type, is_constant, is_builtin)}
        self._storage: Dict[str, Tuple[Any, str, bool, bool]] = {}
        
        # Initialize built-ins if this is the global environment
        if parent is None:
            self._initialize_builtins()
    
    def _initialize_builtins(self) -> None:
        """Initialize built-in constants and functions."""
        # Built-in constants
        self._storage["DEAD"] = (0, "corpse", True, True)
        self._storage["RISEN"] = (1, "corpse", True, True)
        self._storage["void"] = (None, "void", True, True)
        
        # Built-in functions (stored as special markers)
        builtin_functions = [
            "harvest", "rest", "raise_corpse", "steal_soul", 
            "summon", "final_rest", "curse", "absolute", 
            "lesser", "greater", "ritual_args"
        ]
        
        for func_name in builtin_functions:
            self._storage[func_name] = (f"<builtin:{func_name}>", "function", True, True)
    
    def define(
        self, 
        name: str, 
        value: Any, 
        var_type: str, 
        is_constant: bool = False,
        line: int = 0,
        column: int = 0
    ) -> None:
        """
        Define a new variable in this environment.
        
        Args:
            name: Variable name
            value: Variable value
            var_type: Variable type (corpse, soul, crypt, etc.)
            is_constant: Whether variable is constant (eternal)
            line: Line number for error reporting
            column: Column number for error reporting
            
        Raises:
            ReaperRuntimeError: If trying to redefine reserved identifier
        """
        if name in RESERVED_IDENTIFIERS:
            raise ReaperRuntimeError(
                f"Cannot redefine reserved identifier '{name}'",
                line, column, self.filename
            )
        
        self._storage[name] = (value, var_type, is_constant, False)
    
    def get(self, name: str, line: int = 0, column: int = 0) -> Tuple[Any, str]:
        """
        Get variable value and type from environment.
        
        Args:
            name: Variable name
            line: Line number for error reporting
            column: Column number for error reporting
            
        Returns:
            Tuple of (value, type)
            
        Raises:
            ReaperRuntimeError: If variable is undefined
        """
        if name in self._storage:
            value, var_type, _, _ = self._storage[name]
            return value, var_type
        
        # Check parent environment
        if self.parent is not None:
            return self.parent.get(name, line, column)
        
        # Variable not found
        available_names = self.all_names()
        suggestion_msg = ""
        if available_names:
            suggestion_msg = f" Available names: {', '.join(available_names[:5])}"
        
        raise ReaperRuntimeError(
            f"Undefined variable '{name}'{suggestion_msg}",
            line, column, self.filename
        )
    
    def set(
        self, 
        name: str, 
        value: Any, 
        line: int = 0, 
        column: int = 0
    ) -> None:
        """
        Set variable value in environment.
        
        Args:
            name: Variable name
            value: New value
            line: Line number for error reporting
            column: Column number for error reporting
            
        Raises:
            ReaperRuntimeError: If variable is undefined or constant
        """
        if name in self._storage:
            _, var_type, is_constant, is_builtin = self._storage[name]
            
            if is_builtin:
                raise ReaperRuntimeError(
                    f"Cannot modify built-in '{name}'",
                    line, column, self.filename
                )
            
            if is_constant:
                raise ReaperRuntimeError(
                    f"Cannot modify constant '{name}'",
                    line, column, self.filename
                )
            
            self._storage[name] = (value, var_type, is_constant, is_builtin)
            return
        
        # Check parent environment
        if self.parent is not None:
            self.parent.set(name, value, line, column)
            return
        
        # Variable not found
        raise ReaperRuntimeError(
            f"Undefined variable '{name}'",
            line, column, self.filename
        )
    
    def exists(self, name: str) -> bool:
        """
        Check if variable exists in environment or parent chain.
        
        Args:
            name: Variable name
            
        Returns:
            True if variable exists, False otherwise
        """
        if name in self._storage:
            return True
        
        if self.parent is not None:
            return self.parent.exists(name)
        
        return False
    
    def exists_in_current_scope(self, name: str) -> bool:
        """
        Check if variable exists in current environment only (not parent).
        
        Args:
            name: Variable name
            
        Returns:
            True if variable exists in current scope, False otherwise
        """
        return name in self._storage
    
    def all_names(self) -> List[str]:
        """
        Get all variable names in environment and parent chain.
        
        Returns:
            List of all variable names
        """
        names = list(self._storage.keys())
        
        if self.parent is not None:
            parent_names = self.parent.all_names()
            names.extend(parent_names)
        
        return list(set(names))  # Remove duplicates
    
    def current_scope_names(self) -> List[str]:
        """
        Get variable names in current environment only.
        
        Returns:
            List of variable names in current scope
        """
        return list(self._storage.keys())
    
    def get_variable_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a variable.
        
        Args:
            name: Variable name
            
        Returns:
            Dictionary with variable info or None if not found
        """
        if name in self._storage:
            value, var_type, is_constant, is_builtin = self._storage[name]
            return {
                "name": name,
                "value": value,
                "type": var_type,
                "is_constant": is_constant,
                "is_builtin": is_builtin,
                "scope": "current"
            }
        
        if self.parent is not None:
            info = self.parent.get_variable_info(name)
            if info:
                info["scope"] = "parent"
            return info
        
        return None
    
    def set_ritual_args(self, args: List[str]) -> None:
        """
        Set command-line arguments in global environment.
        
        Args:
            args: List of command-line arguments
        """
        if self.parent is None:  # Only set in global environment
            self._storage["ritual_args"] = (args, "crypt", True, True)
        else:
            # Find global environment
            current = self
            while current.parent is not None:
                current = current.parent
            current.set_ritual_args(args)
    
    def get_ritual_args(self) -> List[str]:
        """
        Get command-line arguments from global environment.
        
        Returns:
            List of command-line arguments
        """
        if self.parent is None:  # Global environment
            if "ritual_args" in self._storage:
                return self._storage["ritual_args"][0]
            return []
        else:
            # Find global environment
            current = self
            while current.parent is not None:
                current = current.parent
            return current.get_ritual_args()
    
    def create_child(self, filename: str = "<unknown>") -> 'Environment':
        """
        Create a child environment for lexical scoping.
        
        Args:
            filename: Source filename for child environment
            
        Returns:
            New child environment
        """
        return Environment(parent=self, filename=filename)
    
    def is_global(self) -> bool:
        """
        Check if this is the global environment.
        
        Returns:
            True if global environment, False otherwise
        """
        return self.parent is None
    
    def get_depth(self) -> int:
        """
        Get the depth of this environment in the scope chain.
        
        Returns:
            Depth (0 for global, 1 for first child, etc.)
        """
        depth = 0
        current = self.parent
        while current is not None:
            depth += 1
            current = current.parent
        return depth
    
    def __repr__(self) -> str:
        """String representation of environment."""
        scope_type = "global" if self.is_global() else f"local(depth={self.get_depth()})"
        var_count = len(self._storage)
        return f"Environment({scope_type}, {var_count} variables, {self.filename})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        lines = [f"Environment ({self.filename}):"]
        
        for name, (value, var_type, is_constant, is_builtin) in self._storage.items():
            const_str = " (constant)" if is_constant else ""
            builtin_str = " (builtin)" if is_builtin else ""
            lines.append(f"  {name}: {var_type} = {repr(value)}{const_str}{builtin_str}")
        
        if self.parent is not None:
            lines.append(f"  Parent: {self.parent}")
        
        return "\n".join(lines)


class EnvironmentStack:
    """
    Stack of environments for managing nested scopes during execution.
    """
    
    def __init__(self):
        """Initialize empty environment stack."""
        self._stack: List[Environment] = []
    
    def push(self, environment: Environment) -> None:
        """Push environment onto stack."""
        self._stack.append(environment)
    
    def pop(self) -> Environment:
        """Pop environment from stack."""
        if not self._stack:
            raise RuntimeError("Cannot pop from empty environment stack")
        return self._stack.pop()
    
    def peek(self) -> Environment:
        """Peek at top environment without removing."""
        if not self._stack:
            raise RuntimeError("Cannot peek at empty environment stack")
        return self._stack[-1]
    
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self._stack) == 0
    
    def size(self) -> int:
        """Get stack size."""
        return len(self._stack)
    
    def clear(self) -> None:
        """Clear the stack."""
        self._stack.clear()
    
    def __len__(self) -> int:
        """Get stack size."""
        return len(self._stack)
    
    def __repr__(self) -> str:
        """String representation of stack."""
        return f"EnvironmentStack({len(self._stack)} environments)"
