"""
REAPER Language Lexer

This module implements the lexical analyzer (tokenizer) for the REAPER language.
It converts source code into a stream of tokens for the parser.
"""

import re
from typing import List, Optional, Tuple
from .tokens import (
    Token, TokenType, KEYWORDS, OPERATORS, DELIMITERS, 
    get_keyword_token_type, get_operator_token_type, get_delimiter_token_type,
    get_builtin_constant_value
)
from .reaper_error import ReaperSyntaxError


class Lexer:
    """
    Lexical analyzer for REAPER source code.
    
    Converts source code into tokens with support for:
    - Keywords and identifiers
    - Operators and delimiters
    - String literals with interpolation
    - Raw strings
    - Comments (single-line and multi-line)
    - Numbers and built-in constants
    - Error handling with line/column tracking
    """
    
    def __init__(self, source: str, filename: str = "<unknown>"):
        """
        Initialize lexer with source code.
        
        Args:
            source: Source code to tokenize
            filename: Source filename for error reporting
        """
        self.source = source
        self.filename = filename
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        
        # Track brace depth for string interpolation
        self.brace_depth = 0
        self.in_string = False
        self.string_quote = None
    
    def tokenize(self) -> List[Token]:
        """
        Tokenize the source code.
        
        Returns:
            List of tokens
            
        Raises:
            ReaperSyntaxError: On lexical errors
        """
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.brace_depth = 0
        self.in_string = False
        self.string_quote = None
        
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()
        
        # Add EOF token
        self._add_token(TokenType.EOF)
        return self.tokens
    
    def _is_at_end(self) -> bool:
        """Check if we've reached the end of source."""
        return self.current >= len(self.source)
    
    def _advance(self) -> str:
        """Advance current position and return character."""
        if self._is_at_end():
            return '\0'
        
        char = self.source[self.current]
        self.current += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def _peek(self) -> str:
        """Peek at current character without advancing."""
        if self._is_at_end():
            return '\0'
        return self.source[self.current]
    
    def _peek_next(self) -> str:
        """Peek at next character without advancing."""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def _match(self, expected: str) -> bool:
        """Match and consume character if it matches expected."""
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        
        self.current += 1
        self.column += 1
        return True
    
    def _add_token(self, token_type: TokenType, value: any = None) -> None:
        """Add token to token list."""
        text = self.source[self.start:self.current]
        if value is None:
            value = text
        
        token = Token(token_type, value, self.line, self.column, self.filename)
        self.tokens.append(token)
    
    def _scan_token(self) -> None:
        """Scan and add next token."""
        char = self._advance()
        
        if char == ' ' or char == '\r' or char == '\t':
            # Skip whitespace
            pass
        elif char == '\n':
            # Add newline token for REPL multi-line detection
            self._add_token(TokenType.NEWLINE)
        elif char == '#':
            self._read_comment()
        elif char in ['"', "'"]:
            self._read_string()
        elif char.isdigit():
            # Move back to the digit we just found
            self.current -= 1
            self._read_number()
        elif char.isalpha() or char == '_':
            self._read_identifier()
        elif char in ['+', '*', '/', '%', '!', '=', '<', '>']:
            self._read_operator()
        elif char == '-':
            # Check if this is a negative number or minus operator
            # Only treat as negative number if preceded by operators/delimiters
            if self._peek().isdigit() and self._is_negative_number_context():
                # Don't advance past the '-' - let _read_number handle it
                self._read_number()
            else:
                self._read_operator()
        elif char in ['{', '}', '(', ')', '[', ']', ';', ',', '.', ':']:
            self._read_delimiter(char)
        else:
            self._error(f"Unexpected character '{char}'")
    
    def _read_comment(self) -> None:
        """Read comment (single-line or multi-line)."""
        if self._peek() == '#':
            # Multi-line comment ##...##
            self._advance()  # consume second '#'
            self._read_multiline_comment()
        else:
            # Single-line comment #...\n
            self._read_singleline_comment()
    
    def _read_singleline_comment(self) -> None:
        """Read single-line comment."""
        while self._peek() != '\n' and not self._is_at_end():
            self._advance()
        # Don't consume the newline - let _scan_token handle it
    
    def _read_multiline_comment(self) -> None:
        """Read multi-line comment."""
        while not self._is_at_end():
            if self._peek() == '#' and self._peek_next() == '#':
                self._advance()  # consume first '#'
                self._advance()  # consume second '#'
                return
            self._advance()
        
        # Unclosed multi-line comment
        self._error("Unclosed multi-line comment")
    
    def _read_string(self) -> None:
        """Read string literal with interpolation support."""
        quote = self.source[self.current - 1]  # The quote we just consumed
        self.in_string = True
        self.string_quote = quote
        
        # Check for raw string
        if self.start > 0 and self.source[self.start - 1] == 'r':
            self._read_raw_string(quote)
            return
        
        # Check if string contains interpolation
        if self._has_interpolation(quote):
            self._read_interpolated_string(quote)
        else:
            self._read_simple_string(quote)
    
    def _has_interpolation(self, quote: str) -> bool:
        """Check if string contains interpolation markers."""
        # Look ahead to see if there's a #{ pattern
        temp_pos = self.current
        while temp_pos < len(self.source) and self.source[temp_pos] != quote:
            if self.source[temp_pos] == '#' and temp_pos + 1 < len(self.source) and self.source[temp_pos + 1] == '{':
                return True
            temp_pos += 1
        return False
    
    def _read_simple_string(self, quote: str) -> None:
        """Read simple string without interpolation."""
        value = ""
        while self._peek() != quote and not self._is_at_end():
            char = self._peek()
            
            if char == '\\':
                # Handle escape sequences
                self._advance()  # consume '\'
                if self._is_at_end():
                    self._error("Unclosed string")
                    return
                
                escaped = self._advance()
                value += self._handle_escape_sequence(escaped)
            else:
                value += self._advance()
        
        if self._is_at_end():
            self._error("Unclosed string")
            return
        
        self._advance()  # consume closing quote
        self._add_token(TokenType.STRING, value)
        self.in_string = False
        self.string_quote = None
    
    def _read_interpolated_string(self, quote: str) -> None:
        """Read string with interpolation support."""
        # For now, implement a simplified version that treats interpolation as regular string
        # This will be enhanced in the parser/interpreter phases
        value = ""
        while self._peek() != quote and not self._is_at_end():
            char = self._peek()
            
            if char == '\\':
                # Handle escape sequences
                self._advance()  # consume '\'
                if self._is_at_end():
                    self._error("Unclosed string")
                    return
                
                escaped = self._advance()
                value += self._handle_escape_sequence(escaped)
            elif char == '#' and self._peek_next() == '{':
                # String interpolation - for now, just treat as regular string
                value += self._advance()  # consume '#'
                value += self._advance()  # consume '{'
            else:
                value += self._advance()
        
        if self._is_at_end():
            self._error("Unclosed string")
            return
        
        self._advance()  # consume closing quote
        self._add_token(TokenType.STRING, value)
        self.in_string = False
        self.string_quote = None
    
    def _read_raw_string(self, quote: str) -> None:
        """Read raw string (no escape processing or interpolation)."""
        value = ""
        
        while self._peek() != quote and not self._is_at_end():
            char = self._advance()
            value += char
        
        if self._is_at_end():
            self._error(f"Unclosed raw string")
            return
        
        self._advance()  # consume closing quote
        self._add_token(TokenType.STRING, value)
        self.in_string = False
        self.string_quote = None
    
    def _read_interpolated_string(self, quote: str) -> None:
        """Read string with interpolation support."""
        value = ""
        
        while self._peek() != quote and not self._is_at_end():
            char = self._peek()
            
            if char == '\\':
                # Handle escape sequences
                self._advance()  # consume '\'
                if self._is_at_end():
                    self._error("Unclosed string")
                    return
                
                escaped = self._advance()
                value += self._handle_escape_sequence(escaped)
            elif char == '#' and self._peek_next() == '{':
                # String interpolation
                if value:  # Add string part if not empty
                    self._add_token(TokenType.STRING_PART, value)
                    value = ""
                
                self._advance()  # consume '#'
                self._advance()  # consume '{'
                self._add_token(TokenType.INTERPOLATION_START)
                
                # Read expression until matching '}'
                self._read_interpolation_expression()
            else:
                value += self._advance()
        
        if self._is_at_end():
            self._error(f"Unclosed string")
            return
        
        # Add final string part
        if value:
            self._add_token(TokenType.STRING_PART, value)
        
        self._advance()  # consume closing quote
        self._add_token(TokenType.INTERPOLATION_END)
        self.in_string = False
        self.string_quote = None
    
    def _read_interpolation_expression(self) -> None:
        """Read expression inside string interpolation."""
        brace_depth = 1  # We already consumed the opening brace
        
        while not self._is_at_end() and brace_depth > 0:
            char = self._peek()
            
            if char == '{':
                brace_depth += 1
                self._advance()
            elif char == '}':
                brace_depth -= 1
                if brace_depth > 0:
                    self._advance()
            elif char == '"' or char == "'":
                # Handle strings inside interpolation
                self._read_string()
            elif char == '#':
                # Handle comments inside interpolation
                self._read_comment()
            else:
                # Regular token
                self._scan_token()
        
        if brace_depth > 0:
            self._error("Unclosed interpolation expression")
    
    def _handle_escape_sequence(self, char: str) -> str:
        """Handle escape sequences in strings."""
        escape_map = {
            'n': '\n',
            't': '\t',
            'r': '\r',
            '"': '"',
            "'": "'",
            '\\': '\\',
            '0': '\0'
        }
        
        if char in escape_map:
            return escape_map[char]
        elif char == 'u':
            # Unicode escape \uXXXX
            return self._read_unicode_escape()
        else:
            # Unknown escape sequence - just return the character
            return char
    
    def _read_unicode_escape(self) -> str:
        """Read Unicode escape sequence \\uXXXX."""
        if self.current + 4 > len(self.source):
            self._error("Incomplete Unicode escape sequence")
            return '?'
        
        hex_digits = self.source[self.current:self.current + 4]
        
        # Validate hex digits
        if not re.match(r'^[0-9A-Fa-f]{4}$', hex_digits):
            self._error(f"Invalid Unicode escape sequence \\u{hex_digits}")
            return '?'
        
        self.current += 4
        self.column += 4
        
        try:
            code_point = int(hex_digits, 16)
            return chr(code_point)
        except ValueError:
            self._error(f"Invalid Unicode code point \\u{hex_digits}")
            return '?'
    
    def _read_number(self) -> None:
        """Read number literal (decimal, hex, or binary)."""
        # Handle negative numbers
        is_negative = False
        if self.source[self.start] == '-':
            is_negative = True
            self._advance()  # consume '-'
        
        # Check for hex or binary literals
        if self.source[self.current] == '0':
            self._advance()  # consume '0'
            if self._peek() in ['x', 'X']:
                self._read_hex_literal(is_negative)
                return
            elif self._peek() in ['b', 'B']:
                self._read_binary_literal(is_negative)
                return
            else:
                # Regular decimal number starting with 0
                self._read_decimal_number(is_negative)
                return
        
        # Regular decimal number
        self._read_decimal_number(is_negative)
    
    def _read_hex_literal(self, is_negative: bool) -> None:
        """Read hexadecimal literal (0x1A2B)."""
        self._advance()  # consume 'x' or 'X'
        
        # Read hex digits
        while self._peek().isdigit() or self._peek().lower() in 'abcdef':
            self._advance()
        
        # Parse hex number
        hex_text = self.source[self.start:self.current]
        if is_negative:
            hex_text = '-' + hex_text
        
        try:
            # Remove '0x' prefix for parsing
            if hex_text.startswith('0x') or hex_text.startswith('0X'):
                hex_text = hex_text[2:]
            elif hex_text.startswith('-0x') or hex_text.startswith('-0X'):
                hex_text = '-' + hex_text[3:]
            
            value = int(hex_text, 16)
            self._add_token(TokenType.HEX_LITERAL, value)
        except ValueError:
            self._error(f"Invalid hexadecimal literal '{hex_text}'")
    
    def _read_binary_literal(self, is_negative: bool) -> None:
        """Read binary literal (0b1010)."""
        self._advance()  # consume 'b' or 'B'
        
        # Read binary digits
        while self._peek() in '01':
            self._advance()
        
        # Parse binary number
        binary_text = self.source[self.start:self.current]
        if is_negative:
            binary_text = '-' + binary_text
        
        try:
            # Remove '0b' prefix for parsing
            if binary_text.startswith('0b') or binary_text.startswith('0B'):
                binary_text = binary_text[2:]
            elif binary_text.startswith('-0b') or binary_text.startswith('-0B'):
                binary_text = '-' + binary_text[3:]
            
            value = int(binary_text, 2)
            self._add_token(TokenType.BINARY_LITERAL, value)
        except ValueError:
            self._error(f"Invalid binary literal '{binary_text}'")
    
    def _read_decimal_number(self, is_negative: bool) -> None:
        """Read decimal number literal (integer or float)."""
        # Read digits
        while self._peek().isdigit():
            self._advance()
        
        # Check for decimal point
        is_float = False
        if self._peek() == '.' and self._peek_next().isdigit():
            is_float = True
            self._advance()  # consume '.'
            # Read fractional digits
            while self._peek().isdigit():
                self._advance()
        
        # Parse number
        if is_negative:
            # For negative numbers, include the '-' in the range
            # But make sure we don't include characters before the '-'
            start_pos = self.start - 1
            if start_pos >= 0 and self.source[start_pos] == '-':
                number_text = self.source[start_pos:self.current]
            else:
                number_text = self.source[self.start:self.current]
        else:
            # For positive numbers, start from the initial position
            number_text = self.source[self.start:self.current]
        
        try:
            if is_float:
                value = float(number_text)
            else:
                value = int(number_text)
            self._add_token(TokenType.NUMBER, value)
        except ValueError:
            self._error(f"Invalid number '{number_text}'")
    
    def _read_identifier(self) -> None:
        """Read identifier or keyword."""
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()
        
        text = self.source[self.start:self.current]
        
        # Check if it's a bitwise operator first
        token_type = get_operator_token_type(text)
        if token_type and token_type in [TokenType.ROT, TokenType.WITHER, TokenType.SPREAD, 
                                       TokenType.MUTATE, TokenType.INVERT]:
            self._add_token(token_type)
            return
        
        # Check if it's a keyword
        token_type = get_keyword_token_type(text)
        if token_type:
            # Handle special cases for built-in constants
            if text in ['DEAD', 'RISEN']:
                value = get_builtin_constant_value(text)
                self._add_token(token_type, value)
            else:
                self._add_token(token_type)
        else:
            # Regular identifier
            self._add_token(TokenType.IDENTIFIER, text)
    
    def _read_operator(self) -> None:
        """Read operator (including compound operators)."""
        char = self.source[self.current - 1]
        
        # Check for compound operators
        if char in ['+', '-', '*', '/', '%'] and self._peek() == '=':
            self._advance()  # consume '='
            compound_op = char + '='
            token_type = get_operator_token_type(compound_op)
            if token_type:
                self._add_token(token_type)
            else:
                self._error(f"Unknown compound operator '{compound_op}'")
        elif char == '=' and self._peek() == '=':
            self._advance()  # consume second '='
            self._add_token(TokenType.EQ)
        elif char == '!' and self._peek() == '=':
            self._advance()  # consume '='
            self._add_token(TokenType.NEQ)
        elif char == '<' and self._peek() == '=':
            self._advance()  # consume '='
            self._add_token(TokenType.LTE)
        elif char == '>' and self._peek() == '=':
            self._advance()  # consume '='
            self._add_token(TokenType.GTE)
        elif char == '-' and self._peek() == '>':
            self._advance()  # consume '>'
            self._add_token(TokenType.ARROW)
        elif char == '=' and self._peek() == '>':
            self._advance()  # consume '>'
            self._add_token(TokenType.LAMBDA_ARROW)
        else:
            # Single character operator
            token_type = get_operator_token_type(char)
            if token_type:
                self._add_token(token_type)
            else:
                self._error(f"Unknown operator '{char}'")
    
    def _is_negative_number_context(self) -> bool:
        """Check if we're in a context where - should be treated as negative number."""
        if self.start == 0:
            return True  # Start of input
        
        # Check if previous token was an operator or delimiter that allows negative numbers
        if len(self.tokens) > 0:
            prev_token = self.tokens[-1]
            if prev_token.type in [TokenType.ASSIGN, TokenType.LPAREN, TokenType.COMMA, 
                                 TokenType.PLUS, TokenType.MINUS, TokenType.STAR, 
                                 TokenType.SLASH, TokenType.PERCENT, TokenType.EQ, 
                                 TokenType.NEQ, TokenType.LT, TokenType.GT,
                                 TokenType.LTE, TokenType.GTE, TokenType.CORRUPT, 
                                 TokenType.INFEST, TokenType.BANISH]:
                return True
        
        return False

    def _read_delimiter(self, char: str) -> None:
        """Read delimiter."""
        token_type = get_delimiter_token_type(char)
        if token_type:
            self._add_token(token_type)
        else:
            self._error(f"Unknown delimiter '{char}'")
    
    def _error(self, message: str) -> None:
        """Raise syntax error with current position."""
        raise ReaperSyntaxError(
            message,
            self.line,
            self.column,
            self.filename
        )


def tokenize(source: str, filename: str = "<unknown>") -> List[Token]:
    """
    Convenience function to tokenize source code.
    
    Args:
        source: Source code to tokenize
        filename: Source filename for error reporting
        
    Returns:
        List of tokens
        
    Raises:
        ReaperSyntaxError: On lexical errors
    """
    lexer = Lexer(source, filename)
    return lexer.tokenize()
