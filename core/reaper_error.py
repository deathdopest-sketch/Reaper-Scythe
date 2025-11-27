"""
REAPER Language Error Classes

This module defines custom exception classes for the REAPER language interpreter.
All errors include rich context information for better debugging experience.
"""

import sys
from typing import Any, List, Optional, Dict


class ReaperError(Exception):
    """Base class for all REAPER language errors."""
    
    def __init__(
        self, 
        message: str, 
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>",
        context: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename
        self.context = context
    
    def __str__(self) -> str:
        """String representation of the error."""
        if self.line > 0 and self.column > 0:
            return f"{self.filename}:{self.line}:{self.column}: {self.message}"
        else:
            return self.message
    
    def format_error(self, source_lines: Optional[List[str]] = None) -> str:
        """
        Format error with rich context information.
        
        Args:
            source_lines: List of source code lines for context
            
        Returns:
            Formatted error message with context
        """
        lines = []
        
        # Header with location
        if self.line > 0 and self.column > 0:
            lines.append(f"Error at {self.filename}:{self.line}:{self.column}")
        else:
            lines.append(f"Error in {self.filename}")
        
        lines.append(f"  {self.message}")
        
        # Add source context if available
        if source_lines and self.line > 0 and self.line <= len(source_lines):
            source_line = source_lines[self.line - 1]
            lines.append("")
            lines.append(f"  {self.line:3d} | {source_line}")
            
            # Add pointer to error location
            if self.column > 0:
                pointer = " " * (self.column + 7) + "^"
                lines.append(pointer)
        
        # Add additional context if provided
        if self.context:
            lines.append("")
            lines.append(f"  Context: {self.context}")
        
        return "\n".join(lines)


class ReaperSyntaxError(ReaperError):
    """Syntax error during parsing."""
    
    def __init__(
        self, 
        message: str, 
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>",
        context: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(message, line, column, filename, context)
        self.suggestion = suggestion
    
    def format_error(self, source_lines: Optional[List[str]] = None) -> str:
        """Format syntax error with suggestion."""
        error_msg = super().format_error(source_lines)
        
        if self.suggestion:
            error_msg += f"\n  Suggestion: {self.suggestion}"
        
        return error_msg


class ReaperRuntimeError(ReaperError):
    """Runtime error during execution."""
    
    def __init__(
        self, 
        message: str, 
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>",
        context: Optional[str] = None,
        stack_trace: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(message, line, column, filename, context)
        self.stack_trace = stack_trace or []
    
    def format_error(self, source_lines: Optional[List[str]] = None) -> str:
        """Format runtime error with stack trace."""
        error_msg = super().format_error(source_lines)
        
        if self.stack_trace:
            error_msg += "\n\nStack trace:"
            for i, frame in enumerate(self.stack_trace):
                func_name = frame.get('function', '<unknown>')
                line_num = frame.get('line', 0)
                filename = frame.get('filename', '<unknown>')
                error_msg += f"\n  {i+1}. {func_name} at {filename}:{line_num}"
        
        return error_msg


class ReaperTypeError(ReaperError):
    """Type error during execution."""
    
    def __init__(
        self, 
        message: str, 
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>",
        context: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_type: Optional[str] = None,
        operation: Optional[str] = None
    ):
        super().__init__(message, line, column, filename, context)
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.operation = operation
    
    def format_error(self, source_lines: Optional[List[str]] = None) -> str:
        """Format type error with type information."""
        error_msg = super().format_error(source_lines)
        
        if self.operation:
            error_msg += f"\n  Operation: {self.operation}"
        
        if self.expected_type and self.actual_type:
            error_msg += f"\n  Expected: {self.expected_type}"
            error_msg += f"\n  Actual: {self.actual_type}"
        
        return error_msg


class ReaperRecursionError(ReaperError):
    """Recursion depth limit exceeded."""
    
    def __init__(
        self, 
        message: str, 
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>",
        context: Optional[str] = None,
        current_depth: int = 0,
        max_depth: int = 1000
    ):
        super().__init__(message, line, column, filename, context)
        self.current_depth = current_depth
        self.max_depth = max_depth
    
    def format_error(self, source_lines: Optional[List[str]] = None) -> str:
        """Format recursion error with depth information."""
        error_msg = super().format_error(source_lines)
        error_msg += f"\n  Current depth: {self.current_depth}"
        error_msg += f"\n  Maximum depth: {self.max_depth}"
        return error_msg


class ReaperMemoryError(ReaperError):
    """Memory/resource limit exceeded."""
    
    def __init__(
        self, 
        message: str, 
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>",
        context: Optional[str] = None,
        resource_type: Optional[str] = None,
        current_size: int = 0,
        max_size: int = 0
    ):
        super().__init__(message, line, column, filename, context)
        self.resource_type = resource_type
        self.current_size = current_size
        self.max_size = max_size
    
    def format_error(self, source_lines: Optional[List[str]] = None) -> str:
        """Format memory error with resource information."""
        error_msg = super().format_error(source_lines)
        
        if self.resource_type:
            error_msg += f"\n  Resource: {self.resource_type}"
        
        if self.max_size > 0:
            error_msg += f"\n  Current size: {self.current_size}"
            error_msg += f"\n  Maximum size: {self.max_size}"
        
        return error_msg


class ReaperIndexError(ReaperError):
    """Index out of bounds error."""
    
    def __init__(
        self, 
        message: str, 
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>",
        context: Optional[str] = None,
        index: int = 0,
        collection_size: int = 0,
        collection_type: Optional[str] = None
    ):
        super().__init__(message, line, column, filename, context)
        self.index = index
        self.collection_size = collection_size
        self.collection_type = collection_type
    
    def format_error(self, source_lines: Optional[List[str]] = None) -> str:
        """Format index error with bounds information."""
        error_msg = super().format_error(source_lines)
        
        if self.collection_type:
            error_msg += f"\n  Collection type: {self.collection_type}"
        
        error_msg += f"\n  Index: {self.index}"
        error_msg += f"\n  Collection size: {self.collection_size}"
        
        return error_msg


class ReaperKeyError(ReaperError):
    """Dictionary key not found error."""
    
    def __init__(
        self, 
        message: str, 
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>",
        context: Optional[str] = None,
        key: Any = None,
        available_keys: Optional[List[Any]] = None
    ):
        super().__init__(message, line, column, filename, context)
        self.key = key
        self.available_keys = available_keys or []
    
    def format_error(self, source_lines: Optional[List[str]] = None) -> str:
        """Format key error with available keys."""
        error_msg = super().format_error(source_lines)
        
        if self.key is not None:
            error_msg += f"\n  Missing key: {repr(self.key)}"
        
        if self.available_keys:
            # Show up to 5 available keys
            keys_preview = self.available_keys[:5]
            keys_str = ", ".join(repr(k) for k in keys_preview)
            if len(self.available_keys) > 5:
                keys_str += f" (and {len(self.available_keys) - 5} more)"
            error_msg += f"\n  Available keys: {keys_str}"
        
        return error_msg


class ReaperZeroDivisionError(ReaperError):
    """Division by zero error."""
    
    def __init__(
        self, 
        message: str, 
        line: int = 0, 
        column: int = 0, 
        filename: str = "<unknown>",
        context: Optional[str] = None,
        expression: Optional[str] = None
    ):
        super().__init__(message, line, column, filename, context)
        self.expression = expression
    
    def format_error(self, source_lines: Optional[List[str]] = None) -> str:
        """Format division by zero error."""
        error_msg = super().format_error(source_lines)
        
        if self.expression:
            error_msg += f"\n  Expression: {self.expression}"
        
        return error_msg


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.
    Used for "did you mean?" suggestions.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Edit distance between strings
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def suggest_similar_name(target: str, candidates: List[str], max_distance: int = 2) -> Optional[str]:
    """
    Suggest a similar name from candidates based on Levenshtein distance.
    
    Args:
        target: The name that wasn't found
        candidates: List of available names
        max_distance: Maximum edit distance to consider
        
    Returns:
        Most similar name if found, None otherwise
    """
    if not candidates:
        return None
    
    best_match = None
    best_distance = max_distance + 1
    
    for candidate in candidates:
        distance = levenshtein_distance(target, candidate)
        if distance < best_distance and distance <= max_distance:
            # Only suggest if distance is less than half the target length
            if distance < len(target) / 2:
                best_match = candidate
                best_distance = distance
    
    return best_match


def format_error_with_suggestion(
    error: ReaperError, 
    source_lines: Optional[List[str]] = None,
    available_names: Optional[List[str]] = None
) -> str:
    """
    Format error with "did you mean?" suggestion if applicable.
    
    Args:
        error: The error to format
        source_lines: Source code lines for context
        available_names: Available variable/function names for suggestions
        
    Returns:
        Formatted error message with suggestion
    """
    error_msg = error.format_error(source_lines)
    
    # Add suggestion for undefined variable/function errors
    if isinstance(error, ReaperRuntimeError) and "undefined" in error.message.lower():
        if available_names and hasattr(error, 'message'):
            # Extract variable name from error message (simple heuristic)
            words = error.message.split()
            for word in words:
                if word.isidentifier() and word not in ['undefined', 'variable', 'function']:
                    suggestion = suggest_similar_name(word, available_names)
                    if suggestion:
                        error_msg += f"\n  Did you mean: {suggestion}?"
                    break
    
    return error_msg
