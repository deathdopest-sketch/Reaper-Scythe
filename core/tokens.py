"""
REAPER Language Token Definitions

This module defines all token types used by the REAPER language lexer.
Tokens represent the smallest meaningful units of REAPER source code.
"""

from typing import Any, Optional
from enum import Enum


class TokenType(Enum):
    """Enumeration of all REAPER token types."""
    
    # Type Keywords (11) - Added phantom, specter, shadow
    CORPSE = "CORPSE"
    SOUL = "SOUL"
    CRYPT = "CRYPT"
    GRIMOIRE = "GRIMOIRE"
    TOMB = "TOMB"
    WRAITH = "WRAITH"
    VOID = "VOID"
    ETERNAL = "ETERNAL"
    PHANTOM = "PHANTOM"  # Floating-point type for timing attacks
    SPECTER = "SPECTER"  # Binary data manipulation
    SHADOW = "SHADOW"    # Encrypted/obfuscated strings
    
    # Control Keywords (24) - Added infiltrate, cloak, exploit, breach, risk, catch, finally
    INFECT = "INFECT"
    RAISE = "RAISE"
    HARVEST = "HARVEST"
    REAP = "REAP"
    SHAMBLE = "SHAMBLE"
    DECAY = "DECAY"
    SOULLESS = "SOULLESS"
    SPAWN = "SPAWN"
    IF = "IF"
    OTHERWISE = "OTHERWISE"
    JUDGE = "JUDGE"  # Switch/match statement
    CASE = "CASE"    # Case label
    DEFAULT = "DEFAULT"  # Default case
    FLEE = "FLEE"
    PERSIST = "PERSIST"
    REST = "REST"
    THIS = "THIS"
    FROM = "FROM"
    TO = "TO"
    IN = "IN"
    FOR = "FOR"  # For list comprehensions
    INFILTRATE = "INFILTRATE"  # Import security modules
    CLOAK = "CLOAK"            # Enable anonymity features
    EXPLOIT = "EXPLOIT"        # Try/catch for security operations (legacy)
    BREACH = "BREACH"          # Async operations
    AWAIT = "AWAIT"            # Await async operation
    RISK = "RISK"              # Try block for exception handling
    CATCH = "CATCH"            # Catch block for exception handling
    FINALLY = "FINALLY"        # Finally block for exception handling
    THROW = "THROW"            # Throw/raise exception
    
    # Operators (17) - Added bitwise operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    PERCENT = "PERCENT"
    ASSIGN = "ASSIGN"  # Assignment operator =
    EQ = "EQ"          # Equality operator ==
    NEQ = "NEQ"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    ROT = "ROT"        # Bitwise rotation
    WITHER = "WITHER"  # Bitwise AND
    SPREAD = "SPREAD"  # Bitwise OR
    MUTATE = "MUTATE"  # Bitwise XOR
    INVERT = "INVERT"  # Bitwise NOT
    
    # Logical Operators (3)
    CORRUPT = "CORRUPT"
    INFEST = "INFEST"
    BANISH = "BANISH"
    
    # Compound Assignment (5)
    PLUS_EQ = "PLUS_EQ"
    MINUS_EQ = "MINUS_EQ"
    STAR_EQ = "STAR_EQ"
    SLASH_EQ = "SLASH_EQ"
    PERCENT_EQ = "PERCENT_EQ"
    
    # Delimiters (11)
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    DOT = "DOT"
    ARROW = "ARROW"  # -> for return types
    LAMBDA_ARROW = "LAMBDA_ARROW"  # => for lambdas
    COLON = "COLON"
    
    # Literals (5) - Added hex and binary literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    HEX_LITERAL = "HEX_LITERAL"      # 0x1A2B, 0X1a2b
    BINARY_LITERAL = "BINARY_LITERAL" # 0b1010, 0B1010
    
    # String Interpolation (3)
    STRING_PART = "STRING_PART"
    INTERPOLATION_START = "INTERPOLATION_START"
    INTERPOLATION_END = "INTERPOLATION_END"
    
    # Special (2)
    EOF = "EOF"
    NEWLINE = "NEWLINE"


class Token:
    """
    Represents a single token in REAPER source code.
    
    Attributes:
        type: The type of token (from TokenType enum)
        value: The literal value of the token (for literals and identifiers)
        line: Line number where token appears (1-indexed)
        column: Column number where token appears (1-indexed)
        filename: Source filename (or "<repl>" for interactive mode)
    """
    
    def __init__(
        self, 
        type: TokenType, 
        value: Any = None, 
        line: int = 1, 
        column: int = 1, 
        filename: str = "<unknown>"
    ):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        self.filename = filename
    
    def __repr__(self) -> str:
        """String representation of the token for debugging."""
        if self.value is not None:
            return f"Token({self.type.value}, {repr(self.value)}, {self.filename}:{self.line}:{self.column})"
        else:
            return f"Token({self.type.value}, {self.filename}:{self.line}:{self.column})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        if self.value is not None:
            return f"{self.type.value}({repr(self.value)})"
        else:
            return self.type.value
    
    def __eq__(self, other) -> bool:
        """Equality comparison for tokens."""
        if not isinstance(other, Token):
            return False
        return (
            self.type == other.type and
            self.value == other.value and
            self.line == other.line and
            self.column == other.column and
            self.filename == other.filename
        )


# Keyword mapping from string literals to token types
KEYWORDS = {
    # Type keywords
    "corpse": TokenType.CORPSE,
    "soul": TokenType.SOUL,
    "crypt": TokenType.CRYPT,
    "grimoire": TokenType.GRIMOIRE,
    "tomb": TokenType.TOMB,
    "wraith": TokenType.WRAITH,
    "void": TokenType.VOID,
    "eternal": TokenType.ETERNAL,
    "phantom": TokenType.PHANTOM,  # Floating-point type
    "specter": TokenType.SPECTER,  # Binary data type
    "shadow": TokenType.SHADOW,    # Encrypted string type
    
    # Control keywords
    "infect": TokenType.INFECT,
    "raise": TokenType.RAISE,
    "harvest": TokenType.HARVEST,
    "reap": TokenType.REAP,
    "shamble": TokenType.SHAMBLE,
    "decay": TokenType.DECAY,
    "soulless": TokenType.SOULLESS,
    "spawn": TokenType.SPAWN,
    "if": TokenType.IF,
    "otherwise": TokenType.OTHERWISE,
    "judge": TokenType.JUDGE,  # Switch/match statement
    "case": TokenType.CASE,    # Case label
    "default": TokenType.DEFAULT,  # Default case
    "flee": TokenType.FLEE,
    "persist": TokenType.PERSIST,
    "rest": TokenType.REST,
    "this": TokenType.THIS,
    "from": TokenType.FROM,
    "to": TokenType.TO,
    "in": TokenType.IN,
    "for": TokenType.FOR,  # For list comprehensions
    "infiltrate": TokenType.INFILTRATE,  # Import security modules
    "cloak": TokenType.CLOAK,            # Enable anonymity features
    "exploit": TokenType.EXPLOIT,        # Try/catch for security operations (legacy)
    "breach": TokenType.BREACH,          # Async operations
    "await": TokenType.AWAIT,            # Await async operation
    "risk": TokenType.RISK,              # Try block for exception handling
    "catch": TokenType.CATCH,            # Catch block for exception handling
    "finally": TokenType.FINALLY,        # Finally block for exception handling
    "throw": TokenType.THROW,            # Throw/raise exception
    
    # Logical operators
    "corrupt": TokenType.CORRUPT,
    "infest": TokenType.INFEST,
    "banish": TokenType.BANISH,
    
    # Built-in constants
    "DEAD": TokenType.NUMBER,  # Special case: DEAD is a number literal (0)
    "RISEN": TokenType.NUMBER,  # Special case: RISEN is a number literal (1)
}

# Operator mapping from string literals to token types
OPERATORS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERCENT,
    "=": TokenType.ASSIGN,  # Assignment operator
    "==": TokenType.EQ,     # Equality operator
    "!=": TokenType.NEQ,
    "<": TokenType.LT,
    ">": TokenType.GT,
    "<=": TokenType.LTE,
    ">=": TokenType.GTE,
    "+=": TokenType.PLUS_EQ,
    "-=": TokenType.MINUS_EQ,
    "*=": TokenType.STAR_EQ,
    "/=": TokenType.SLASH_EQ,
    "%=": TokenType.PERCENT_EQ,
    # Bitwise operators
    "rot": TokenType.ROT,        # Bitwise rotation
    "wither": TokenType.WITHER,  # Bitwise AND
    "spread": TokenType.SPREAD,  # Bitwise OR
    "mutate": TokenType.MUTATE,  # Bitwise XOR
    "invert": TokenType.INVERT,  # Bitwise NOT
}

# Delimiter mapping from string literals to token types
DELIMITERS = {
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
    "->": TokenType.ARROW,
    "=>": TokenType.LAMBDA_ARROW,  # Lambda/anonymous function arrow
    ":": TokenType.COLON,
}

# Built-in constant values
BUILTIN_CONSTANTS = {
    "DEAD": 0,
    "RISEN": 1,
}

# Reserved identifiers that cannot be redefined
RESERVED_IDENTIFIERS = {
    "DEAD", "RISEN", "void",
    "harvest", "rest", "raise_corpse", "steal_soul", 
    "summon", "final_rest", "curse", "absolute", 
    "lesser", "greater", "ritual_args",
    "excavate", "bury"
}


def is_keyword(identifier: str) -> bool:
    """Check if an identifier is a REAPER keyword."""
    return identifier in KEYWORDS


def is_reserved(identifier: str) -> bool:
    """Check if an identifier is reserved (keyword or built-in)."""
    return identifier in KEYWORDS or identifier in RESERVED_IDENTIFIERS


def get_keyword_token_type(identifier: str) -> Optional[TokenType]:
    """Get the token type for a keyword identifier."""
    return KEYWORDS.get(identifier)


def get_operator_token_type(operator: str) -> Optional[TokenType]:
    """Get the token type for an operator string."""
    return OPERATORS.get(operator)


def get_delimiter_token_type(delimiter: str) -> Optional[TokenType]:
    """Get the token type for a delimiter string."""
    return DELIMITERS.get(delimiter)


def get_builtin_constant_value(identifier: str) -> Optional[Any]:
    """Get the value for a built-in constant identifier."""
    return BUILTIN_CONSTANTS.get(identifier)
