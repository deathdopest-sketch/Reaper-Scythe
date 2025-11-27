"""
REAPER Language Parser

This module implements a recursive descent parser for the REAPER language.
It converts tokens into an Abstract Syntax Tree (AST) with full operator precedence,
error recovery, and comprehensive syntax support.
"""

from typing import List, Optional, Tuple, Any
from .tokens import Token, TokenType
from .ast_nodes import *
from .reaper_error import ReaperSyntaxError


class Parser:
    """
    Recursive descent parser for REAPER language.
    
    Implements full operator precedence, error recovery, and comprehensive
    syntax support including string interpolation, default parameters, and
    all control structures.
    """
    
    def __init__(self, tokens: List[Token]):
        """
        Initialize parser with tokens.
        
        Args:
            tokens: List of tokens from lexer
        """
        self.tokens = tokens
        self.current = 0
        self.errors: List[ReaperSyntaxError] = []
        self.max_errors = 10
    
    def parse(self) -> ProgramNode:
        """
        Parse tokens into AST.
        
        Returns:
            ProgramNode representing the parsed program
            
        Raises:
            ReaperSyntaxError: On syntax errors (collected up to max_errors)
        """
        self.current = 0
        self.errors = []
        
        statements = []
        
        while not self._is_at_end():
            try:
                # Skip newlines before parsing statement
                self._skip_newlines()
                
                # If we're at EOF after skipping newlines, break
                if self._is_at_end():
                    break
                    
                statement = self._parse_statement()
                if statement:
                    statements.append(statement)
            except ReaperSyntaxError as e:
                self.errors.append(e)
                if len(self.errors) >= self.max_errors:
                    break
                self._synchronize()
        
        if self.errors:
            # Return the first error for now (could be improved to show all)
            raise self.errors[0]
        
        return ProgramNode(statements)
    
    def _is_at_end(self) -> bool:
        """Check if we've reached the end of tokens."""
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        """Peek at current token without consuming."""
        if self.current >= len(self.tokens):
            return self.tokens[-1]  # Return EOF token
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Get previous token."""
        if self.current == 0:
            return self.tokens[0]
        return self.tokens[self.current - 1]
    
    def _advance(self) -> Token:
        """Consume and return current token."""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _skip_newlines(self) -> None:
        """Skip NEWLINE tokens."""
        while self._check(TokenType.NEWLINE):
            self._advance()
    
    def _check(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        if self._is_at_end():
            return False
        return self._peek().type in token_types
    
    def _match(self, *token_types: TokenType) -> bool:
        """Match and consume token if it matches any of the given types."""
        if self._check(*token_types):
            self._advance()
            return True
        return False
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error."""
        if self._check(token_type):
            return self._advance()
        
        token = self._peek()
        raise ReaperSyntaxError(
            message,
            token.line,
            token.column,
            token.filename,
            suggestion=f"Expected {token_type.value}, got {token.type.value}"
        )
    
    def _peek_next(self) -> TokenType:
        """Peek at the next token type without consuming it."""
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1].type
        return TokenType.EOF
    
    def _error(self, message: str) -> None:
        """Report a syntax error."""
        error = ReaperSyntaxError(message, self._peek().line, self._peek().column)
        self.errors.append(error)
        if len(self.errors) >= self.max_errors:
            raise error
    
    def _synchronize(self) -> None:
        """Synchronize parser after error by skipping to next statement boundary."""
        self._advance()
        
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            
            # Skip to next statement boundary
            if self._peek().type in [
                TokenType.INFECT, TokenType.TOMB, TokenType.IF, TokenType.SHAMBLE,
                TokenType.DECAY, TokenType.SOULLESS, TokenType.HARVEST, TokenType.REAP,
                TokenType.FLEE, TokenType.PERSIST, TokenType.CORPSE, TokenType.SOUL,
                TokenType.CRYPT, TokenType.GRIMOIRE, TokenType.TOMB, TokenType.WRAITH,
                TokenType.VOID, TokenType.ETERNAL, TokenType.PHANTOM, TokenType.SPECTER, TokenType.SHADOW
            ]:
                return
            
            self._advance()
    
    # ============================================================================
    # Statement Parsing
    # ============================================================================
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse a statement."""
        # If we're at EOF, return None
        if self._is_at_end():
            return None
        
        if self._match(TokenType.CORPSE, TokenType.SOUL, TokenType.CRYPT, 
                      TokenType.GRIMOIRE, TokenType.WRAITH, 
                      TokenType.VOID, TokenType.ETERNAL, TokenType.PHANTOM, TokenType.SPECTER, TokenType.SHADOW):
            return self._parse_variable_declaration()
        elif self._match(TokenType.INFECT):
            return self._parse_function_definition()
        elif self._match(TokenType.TOMB):
            # Check if this is a variable declaration or class definition
            if self._check(TokenType.IDENTIFIER) and self._peek_next() == TokenType.ASSIGN:
                # tomb x = ... (variable declaration)
                return self._parse_variable_declaration()
            else:
                # tomb ClassName { ... } (class definition)
                return self._parse_class_definition()
        elif self._match(TokenType.IF):
            return self._parse_if_statement()
        elif self._match(TokenType.SHAMBLE):
            return self._parse_shamble_loop()
        elif self._match(TokenType.DECAY):
            return self._parse_decay_loop()
        elif self._match(TokenType.SOULLESS):
            return self._parse_soulless_loop()
        elif self._match(TokenType.HARVEST):
            return self._parse_harvest_statement()
        elif self._match(TokenType.RAISE):
            return self._parse_raise_statement()  # Function call
        elif self._match(TokenType.THROW):
            return self._parse_raise_exception_statement()  # Exception raising
        elif self._match(TokenType.REAP):
            return self._parse_return_statement()
        elif self._match(TokenType.FLEE):
            return self._parse_flee_statement()
        elif self._match(TokenType.PERSIST):
            return self._parse_persist_statement()
        elif self._match(TokenType.REST):
            return self._parse_rest_statement()
        elif self._match(TokenType.INFILTRATE):
            return self._parse_infiltrate_statement()
        elif self._match(TokenType.CLOAK):
            return self._parse_cloak_statement()
        elif self._match(TokenType.RISK):
            return self._parse_risk_statement()
        elif self._match(TokenType.EXPLOIT):
            return self._parse_exploit_statement()  # Legacy support
        elif self._match(TokenType.BREACH):
            return self._parse_breach_statement()
        else:
            # Expression statement
            expr = self._parse_expression()
            if expr:
                self._consume(TokenType.SEMICOLON, "Expected ';' after expression")
            return expr
    
    def _parse_variable_declaration(self) -> AssignmentNode:
        """Parse variable declaration."""
        token = self._previous()
        var_type = token.type.value.lower()
        is_constant = (token.type == TokenType.ETERNAL)
        
        if is_constant:
            # Consume the type keyword after 'eternal'
            if self._match(TokenType.CORPSE, TokenType.SOUL, TokenType.CRYPT,
                          TokenType.GRIMOIRE, TokenType.TOMB, TokenType.WRAITH,
                          TokenType.PHANTOM, TokenType.SPECTER, TokenType.SHADOW):
                type_token = self._previous()
                var_type = type_token.type.value.lower()
            else:
                self._error("Expected type after 'eternal'")
        
        name_token = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        
        # Check if there's an initial value
        if self._match(TokenType.ASSIGN):
            value = self._parse_expression()
        else:
            # No initial value - use void as default
            value = VoidNode(token.line, token.column, token.filename)
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        
        target = VariableNode(name_token.value, name_token.line, name_token.column, name_token.filename)
        return AssignmentNode(target, value, token.line, token.column, token.filename, is_declaration=True, var_type=var_type)
    
    def _parse_class_property(self) -> AssignmentNode:
        """Parse class property declaration (with or without initial value)."""
        token = self._previous()
        var_type = token.type.value.lower()
        is_constant = (token.type == TokenType.ETERNAL)
        
        # Handle eternal keyword
        if token.type == TokenType.ETERNAL:
            if self._match(TokenType.CORPSE, TokenType.SOUL, TokenType.CRYPT,
                          TokenType.GRIMOIRE, TokenType.TOMB, TokenType.WRAITH,
                          TokenType.PHANTOM, TokenType.SPECTER, TokenType.SHADOW):
                type_token = self._previous()
                var_type = type_token.type.value.lower()
            else:
                self._error("Expected type after 'eternal'")
        
        name_token = self._consume(TokenType.IDENTIFIER, "Expected property name")
        
        # Check if there's an initial value
        if self._match(TokenType.ASSIGN):
            value = self._parse_expression()
            self._consume(TokenType.SEMICOLON, "Expected ';' after property declaration")
            
            target = VariableNode(name_token.value, name_token.line, name_token.column, name_token.filename)
            return AssignmentNode(target, value, token.line, token.column, token.filename)
        else:
            # Property without initial value - use void as default
            self._consume(TokenType.SEMICOLON, "Expected ';' after property declaration")
            
            target = VariableNode(name_token.value, name_token.line, name_token.column, name_token.filename)
            void_node = VoidNode(token.line, token.column, token.filename)
            return AssignmentNode(target, void_node, token.line, token.column, token.filename)
    
    def _parse_function_definition(self) -> InfectNode:
        """Parse function definition."""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected function name")
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        
        params = []
        if not self._check(TokenType.RPAREN):
            params = self._parse_parameter_list()
        
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        return_type = None
        if self._match(TokenType.ARROW):
            if self._match(TokenType.CORPSE, TokenType.SOUL, TokenType.CRYPT,
                          TokenType.GRIMOIRE, TokenType.TOMB, TokenType.WRAITH,
                          TokenType.VOID, TokenType.ETERNAL, TokenType.PHANTOM, TokenType.SPECTER, TokenType.SHADOW):
                type_token = self._previous()
                return_type = type_token.type.value.lower()
            else:
                self._error("Expected return type after '->'")
        
        body = self._parse_block()
        
        return InfectNode(
            name_token.value, params, return_type, body,
            name_token.line, name_token.column, name_token.filename
        )
    
    def _parse_parameter_list(self) -> List[Tuple[str, str, Optional[ASTNode]]]:
        """Parse function parameter list."""
        params = []
        
        while True:
            # Parse parameter type
            if self._match(TokenType.CORPSE, TokenType.SOUL, TokenType.CRYPT,
                          TokenType.GRIMOIRE, TokenType.TOMB, TokenType.WRAITH,
                          TokenType.VOID, TokenType.ETERNAL, TokenType.PHANTOM, TokenType.SPECTER, TokenType.SHADOW):
                type_token = self._previous()
                param_type = type_token.type.value.lower()
            else:
                self._error("Expected parameter type")
                break
            
            # Parse parameter name
            name_token = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
            param_name = name_token.value
            
            # Parse default value if present
            default_value = None
            if self._match(TokenType.ASSIGN):
                default_value = self._parse_expression()
            
            params.append((param_name, param_type, default_value))
            
            if not self._match(TokenType.COMMA):
                break
        
        return params
    
    def _parse_class_definition(self) -> TombNode:
        """Parse class definition."""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected class name")
        self._consume(TokenType.LBRACE, "Expected '{' after class name")
        
        properties = []
        methods = []
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._match(TokenType.INFECT):
                # Could be method or constructor
                method = self._parse_function_definition()
                methods.append(method)
            elif self._match(TokenType.CORPSE, TokenType.SOUL, TokenType.CRYPT, 
                           TokenType.GRIMOIRE, TokenType.TOMB, TokenType.WRAITH, 
                           TokenType.VOID, TokenType.ETERNAL, TokenType.PHANTOM, TokenType.SPECTER, TokenType.SHADOW):
                # Property declaration
                prop = self._parse_class_property()
                properties.append(prop)
            else:
                # Skip unknown tokens
                self._advance()
        
        self._consume(TokenType.RBRACE, "Expected '}' after class body")
        
        return TombNode(
            name_token.value, properties, methods,
            name_token.line, name_token.column, name_token.filename
        )
    
    def _parse_if_statement(self) -> IfNode:
        """Parse if statement with else-if chains."""
        self._consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after condition")
        
        if_body = self._parse_block()
        
        elif_conditions = []
        elif_bodies = []
        else_body = None
        
        # Parse else-if chains
        while self._match(TokenType.OTHERWISE):
            if self._match(TokenType.IF):
                self._consume(TokenType.LPAREN, "Expected '(' after 'otherwise if'")
                elif_condition = self._parse_expression()
                self._consume(TokenType.RPAREN, "Expected ')' after condition")
                elif_conditions.append(elif_condition)
                elif_bodies.append(self._parse_block())
            else:
                # Final else
                else_body = self._parse_block()
                break
        
        return IfNode(condition, if_body, elif_conditions, elif_bodies, else_body)
    
    def _parse_shamble_loop(self) -> ShambleNode:
        """Parse shamble (for) loop."""
        var_token = self._consume(TokenType.IDENTIFIER, "Expected loop variable name")
        self._consume(TokenType.FROM, "Expected 'from' after loop variable")
        
        start = self._parse_expression()
        self._consume(TokenType.TO, "Expected 'to' after start value")
        end = self._parse_expression()
        
        body = self._parse_block()
        
        return ShambleNode(
            var_token.value, start, end, body,
            var_token.line, var_token.column, var_token.filename
        )
    
    def _parse_decay_loop(self) -> DecayNode:
        """Parse decay (foreach) loop."""
        var_token = self._consume(TokenType.IDENTIFIER, "Expected loop variable name")
        self._consume(TokenType.IN, "Expected 'in' after loop variable")
        
        iterable = self._parse_expression()
        body = self._parse_block()
        
        return DecayNode(
            var_token.value, iterable, body,
            var_token.line, var_token.column, var_token.filename
        )
    
    def _parse_soulless_loop(self) -> SoullessNode:
        """Parse soulless (infinite while) loop."""
        body = self._parse_block()
        return SoullessNode(body)
    
    def _parse_harvest_statement(self) -> HarvestNode:
        """Parse harvest (print) statement."""
        expressions = []
        
        if not self._check(TokenType.SEMICOLON):
            expressions.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                expressions.append(self._parse_expression())
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after harvest statement")
        return HarvestNode(expressions)
    
    def _parse_raise_statement(self) -> CallNode:
        """Parse raise (function call) statement."""
        # Parse function name
        name_token = self._consume(TokenType.IDENTIFIER, "Expected function name after 'raise'")
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        
        # Parse arguments
        arguments = []
        if not self._check(TokenType.RPAREN):
            arguments.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                arguments.append(self._parse_expression())
        
        self._consume(TokenType.RPAREN, "Expected ')' after arguments")
        self._consume(TokenType.SEMICOLON, "Expected ';' after raise statement")
        
        return CallNode(name_token.value, arguments, name_token.line, name_token.column, name_token.filename)
    
    def _parse_return_statement(self) -> ReapNode:
        """Parse return statement."""
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self._parse_expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after return statement")
        return ReapNode(value)
    
    def _parse_flee_statement(self) -> FleeNode:
        """Parse flee (break) statement."""
        self._consume(TokenType.SEMICOLON, "Expected ';' after flee statement")
        return FleeNode()
    
    def _parse_persist_statement(self) -> PersistNode:
        """Parse persist (continue) statement."""
        self._consume(TokenType.SEMICOLON, "Expected ';' after persist statement")
        return PersistNode()
    
    def _parse_rest_statement(self) -> RestNode:
        """Parse rest (sleep) statement."""
        self._consume(TokenType.LPAREN, "Expected '(' after 'rest'")
        duration = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after duration")
        self._consume(TokenType.SEMICOLON, "Expected ';' after rest statement")
        return RestNode(duration)
    
    def _parse_block(self) -> BlockNode:
        """Parse block of statements."""
        self._consume(TokenType.LBRACE, "Expected '{' before block")
        
        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            # Skip newlines before parsing statement
            self._skip_newlines()
            
            # If we hit the closing brace, break
            if self._check(TokenType.RBRACE):
                break
                
            statement = self._parse_statement()
            if statement:
                statements.append(statement)
        
        self._consume(TokenType.RBRACE, "Expected '}' after block")
        return BlockNode(statements)
    
    # ============================================================================
    # Expression Parsing (with precedence)
    # ============================================================================
    
    def _parse_expression(self) -> ASTNode:
        """Parse expression with assignment precedence."""
        return self._parse_assignment()
    
    def _parse_assignment(self) -> ASTNode:
        """Parse assignment expression (right-associative)."""
        expr = self._parse_logical_or()
        
        if self._match(TokenType.ASSIGN, TokenType.PLUS_EQ, TokenType.MINUS_EQ, 
                      TokenType.STAR_EQ, TokenType.SLASH_EQ, TokenType.PERCENT_EQ):
            operator = self._previous()
            value = self._parse_assignment()  # Right-associative
            
            if operator.type == TokenType.ASSIGN:
                return AssignmentNode(expr, value, operator.line, operator.column, operator.filename)
            else:
                # Compound assignment
                op_map = {
                    TokenType.PLUS_EQ: '+=',
                    TokenType.MINUS_EQ: '-=',
                    TokenType.STAR_EQ: '*=',
                    TokenType.SLASH_EQ: '/=',
                    TokenType.PERCENT_EQ: '%='
                }
                return CompoundAssignmentNode(
                    expr, op_map[operator.type], value,
                    operator.line, operator.column, operator.filename
                )
        
        return expr
    
    def _parse_logical_or(self) -> ASTNode:
        """Parse logical OR (infest) expression."""
        expr = self._parse_logical_and()
        
        while self._match(TokenType.INFEST):
            operator = self._previous()
            right = self._parse_logical_and()
            expr = LogicalOpNode(expr, "infest", right, True, 
                               operator.line, operator.column, operator.filename)
        
        return expr
    
    def _parse_logical_and(self) -> ASTNode:
        """Parse logical AND (corrupt) expression."""
        expr = self._parse_bitwise_or()
        
        while self._match(TokenType.CORRUPT):
            operator = self._previous()
            right = self._parse_bitwise_or()
            expr = LogicalOpNode(expr, "corrupt", right, True,
                               operator.line, operator.column, operator.filename)
        
        return expr
    
    def _parse_bitwise_or(self) -> ASTNode:
        """Parse bitwise OR (spread) expression."""
        expr = self._parse_bitwise_xor()
        
        while self._match(TokenType.SPREAD):
            operator = self._previous()
            right = self._parse_bitwise_xor()
            expr = BinaryOpNode(expr, "spread", right,
                               operator.line, operator.column, operator.filename)
        
        return expr
    
    def _parse_bitwise_xor(self) -> ASTNode:
        """Parse bitwise XOR (mutate) expression."""
        expr = self._parse_bitwise_and()
        
        while self._match(TokenType.MUTATE):
            operator = self._previous()
            right = self._parse_bitwise_and()
            expr = BinaryOpNode(expr, "mutate", right,
                               operator.line, operator.column, operator.filename)
        
        return expr
    
    def _parse_bitwise_and(self) -> ASTNode:
        """Parse bitwise AND (wither) expression."""
        expr = self._parse_bitwise_shift()
        
        while self._match(TokenType.WITHER):
            operator = self._previous()
            right = self._parse_bitwise_shift()
            expr = BinaryOpNode(expr, "wither", right,
                               operator.line, operator.column, operator.filename)
        
        return expr
    
    def _parse_bitwise_shift(self) -> ASTNode:
        """Parse bitwise shift/rotation (rot) expression."""
        expr = self._parse_comparison()
        
        while self._match(TokenType.ROT):
            operator = self._previous()
            right = self._parse_comparison()
            expr = BinaryOpNode(expr, "rot", right,
                               operator.line, operator.column, operator.filename)
        
        return expr
    
    def _parse_comparison(self) -> ASTNode:
        """Parse comparison expression."""
        expr = self._parse_term()
        
        while self._match(TokenType.EQ, TokenType.NEQ, TokenType.LT, 
                         TokenType.GT, TokenType.LTE, TokenType.GTE):
            operator = self._previous()
            right = self._parse_term()
            
            op_map = {
                TokenType.EQ: "==",
                TokenType.NEQ: "!=",
                TokenType.LT: "<",
                TokenType.GT: ">",
                TokenType.LTE: "<=",
                TokenType.GTE: ">="
            }
            
            expr = ComparisonNode(expr, op_map[operator.type], right,
                                operator.line, operator.column, operator.filename)
        
        return expr
    
    def _parse_term(self) -> ASTNode:
        """Parse addition/subtraction expression."""
        expr = self._parse_factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._parse_factor()
            
            op_map = {
                TokenType.PLUS: "+",
                TokenType.MINUS: "-"
            }
            
            expr = BinaryOpNode(expr, op_map[operator.type], right,
                              operator.line, operator.column, operator.filename)
        
        return expr
    
    def _parse_factor(self) -> ASTNode:
        """Parse multiplication/division/modulo expression."""
        expr = self._parse_unary()
        
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous()
            right = self._parse_unary()
            
            op_map = {
                TokenType.STAR: "*",
                TokenType.SLASH: "/",
                TokenType.PERCENT: "%"
            }
            
            expr = BinaryOpNode(expr, op_map[operator.type], right,
                              operator.line, operator.column, operator.filename)
        
        return expr
    
    def _parse_unary(self) -> ASTNode:
        """Parse unary expression."""
        if self._match(TokenType.MINUS, TokenType.BANISH, TokenType.INVERT):
            operator = self._previous()
            right = self._parse_unary()  # Right-associative
            
            op_map = {
                TokenType.MINUS: "-",
                TokenType.BANISH: "banish",
                TokenType.INVERT: "invert"
            }
            
            return UnaryOpNode(op_map[operator.type], right,
                             operator.line, operator.column, operator.filename)
        
        elif self._match(TokenType.AWAIT):
            operator = self._previous()
            expression = self._parse_unary()
            return AwaitNode(expression, operator.line, operator.column, operator.filename)
        
        return self._parse_postfix()
    
    def _parse_postfix(self) -> ASTNode:
        """Parse postfix expression (property access, indexing, method calls)."""
        expr = self._parse_primary()
        
        while True:
            if self._match(TokenType.DOT):
                # Property access - can be identifier or keyword
                if self._match(TokenType.IDENTIFIER):
                    name_token = self._previous()
                elif self._match(TokenType.BANISH, TokenType.CORRUPT, TokenType.INFEST):
                    name_token = self._previous()
                else:
                    self._error("Expected property name")
                    return expr
                expr = PropertyAccessNode(expr, name_token.value,
                                        name_token.line, name_token.column, name_token.filename)
            elif self._match(TokenType.LBRACKET):
                # Index access or slicing
                if self._check(TokenType.COLON):
                    # Slicing
                    expr = self._parse_slice(expr)
                else:
                    # Index access
                    index = self._parse_expression()
                    self._consume(TokenType.RBRACKET, "Expected ']' after index")
                    expr = IndexAccessNode(expr, index)
            elif self._match(TokenType.LPAREN):
                # Function call or method call
                arguments = []
                if not self._check(TokenType.RPAREN):
                    arguments = self._parse_argument_list()
                self._consume(TokenType.RPAREN, "Expected ')' after arguments")
                
                # Check if this is a function call (VariableNode) or method call
                if isinstance(expr, VariableNode):
                    expr = CallNode(expr.name, arguments, expr.line, expr.column, expr.filename)
                elif isinstance(expr, PropertyAccessNode):
                    # Method call on object (e.g., arr.curse())
                    expr = MethodCallNode(expr.object, expr.property_name, arguments)
                else:
                    expr = MethodCallNode(expr, "call", arguments)
            else:
                break
        
        return expr
    
    def _parse_slice(self, object: ASTNode) -> SliceNode:
        """Parse slice expression."""
        start = None
        end = None
        step = None
        
        if not self._check(TokenType.COLON):
            start = self._parse_expression()
        
        self._consume(TokenType.COLON, "Expected ':' in slice")
        
        if not self._check(TokenType.RBRACKET, TokenType.COLON):
            end = self._parse_expression()
        
        if self._match(TokenType.COLON):
            if not self._check(TokenType.RBRACKET):
                step = self._parse_expression()
        
        self._consume(TokenType.RBRACKET, "Expected ']' after slice")
        return SliceNode(object, start, end, step)
    
    def _parse_primary(self) -> ASTNode:
        """Parse primary expression."""
        if self._match(TokenType.NUMBER):
            token = self._previous()
            return NumberNode(token.value, token.line, token.column, token.filename)
        
        elif self._match(TokenType.HEX_LITERAL):
            token = self._previous()
            return HexLiteralNode(token.value, token.line, token.column, token.filename)
        
        elif self._match(TokenType.BINARY_LITERAL):
            token = self._previous()
            return BinaryLiteralNode(token.value, token.line, token.column, token.filename)
        
        elif self._match(TokenType.STRING):
            token = self._previous()
            return StringNode(token.value, token.line, token.column, token.filename)
        
        elif self._match(TokenType.STRING_PART):
            # Start of interpolated string
            return self._parse_interpolated_string()
        
        elif self._match(TokenType.IDENTIFIER):
            token = self._previous()
            return VariableNode(token.value, token.line, token.column, token.filename)
        
        elif self._match(TokenType.THIS):
            token = self._previous()
            return VariableNode("this", token.line, token.column, token.filename)
        
        elif self._match(TokenType.VOID):
            token = self._previous()
            return VoidNode(token.line, token.column, token.filename)
        
        elif self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        elif self._match(TokenType.LBRACKET):
            return self._parse_array_literal()
        
        elif self._match(TokenType.LBRACE):
            return self._parse_dictionary_literal()
        
        elif self._match(TokenType.SPAWN):
            return self._parse_spawn_expression()
        
        else:
            token = self._peek()
            raise ReaperSyntaxError(
                "Expected expression",
                token.line,
                token.column,
                token.filename
            )
    
    def _parse_interpolated_string(self) -> InterpolatedStringNode:
        """Parse interpolated string."""
        parts = []
        
        # First string part
        token = self._previous()
        parts.append(StringNode(token.value, token.line, token.column, token.filename))
        
        # Parse interpolation parts
        while self._match(TokenType.INTERPOLATION_START):
            # Parse expression inside interpolation
            expr = self._parse_expression()
            parts.append(expr)
            
            self._consume(TokenType.INTERPOLATION_END, "Expected '}' after interpolation")
            
            # Parse next string part
            if self._match(TokenType.STRING_PART):
                token = self._previous()
                parts.append(StringNode(token.value, token.line, token.column, token.filename))
        
        return InterpolatedStringNode(parts)
    
    def _parse_array_literal(self) -> ArrayNode:
        """Parse array literal."""
        elements = []
        
        if not self._check(TokenType.RBRACKET):
            elements.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                elements.append(self._parse_expression())
        
        self._consume(TokenType.RBRACKET, "Expected ']' after array")
        return ArrayNode(elements)
    
    def _parse_dictionary_literal(self) -> DictionaryNode:
        """Parse dictionary literal."""
        pairs = []
        
        if not self._check(TokenType.RBRACE):
            key = self._parse_expression()
            self._consume(TokenType.COLON, "Expected ':' after key")
            value = self._parse_expression()
            pairs.append((key, value))
            
            while self._match(TokenType.COMMA):
                key = self._parse_expression()
                self._consume(TokenType.COLON, "Expected ':' after key")
                value = self._parse_expression()
                pairs.append((key, value))
        
        self._consume(TokenType.RBRACE, "Expected '}' after dictionary")
        return DictionaryNode(pairs)
    
    def _parse_spawn_expression(self) -> SpawnNode:
        """Parse spawn (class instantiation) expression."""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected class name after 'spawn'")
        self._consume(TokenType.LPAREN, "Expected '(' after class name")
        
        arguments = []
        if not self._check(TokenType.RPAREN):
            arguments = self._parse_argument_list()
        
        self._consume(TokenType.RPAREN, "Expected ')' after arguments")
        return SpawnNode(name_token.value, arguments, name_token.line, name_token.column, name_token.filename)
    
    def _parse_argument_list(self) -> List[ASTNode]:
        """Parse function call argument list."""
        arguments = []
        
        while True:
            arguments.append(self._parse_expression())
            if not self._match(TokenType.COMMA):
                break
        
        return arguments

    def _parse_infiltrate_statement(self) -> InfiltrateNode:
        """Parse infiltrate statement (import security modules)."""
        # Parse module name (must be identifier)
        module_token = self._consume(TokenType.IDENTIFIER, "Expected module name after 'infiltrate'")
        module_name = module_token.value
        
        alias = None
        symbol_names = []
        
        # Check for 'as' alias
        if self._match(TokenType.IDENTIFIER):
            if self._previous().value == "as":
                alias_token = self._consume(TokenType.IDENTIFIER, "Expected alias name after 'as'")
                alias = alias_token.value
            else:
                # Not 'as', might be start of symbol list - backtrack
                self.current -= 1
        
        # Check for specific symbol imports: infiltrate module (symbol1, symbol2, ...)
        if self._check(TokenType.LPAREN):
            self._advance()  # Consume '('
            if not self._check(TokenType.RPAREN):
                # Parse symbol list
                symbol_token = self._consume(TokenType.IDENTIFIER, "Expected symbol name")
                symbol_names.append(symbol_token.value)
                while self._match(TokenType.COMMA):
                    symbol_token = self._consume(TokenType.IDENTIFIER, "Expected symbol name")
                    symbol_names.append(symbol_token.value)
            self._consume(TokenType.RPAREN, "Expected ')' after symbol list")
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after infiltrate statement")
        return InfiltrateNode(module_name, alias, symbol_names if symbol_names else None,
                            module_token.line, module_token.column, module_token.filename)

    def _parse_cloak_statement(self) -> CloakNode:
        """Parse cloak statement (enable anonymity features)."""
        if self._match(TokenType.IDENTIFIER):
            feature_name = self._previous().value
        else:
            self._error("Expected feature name after 'cloak'")
            return None
        self._consume(TokenType.SEMICOLON, "Expected ';' after cloak statement")
        return CloakNode(feature_name)

    def _parse_risk_statement(self) -> RiskNode:
        """Parse risk statement (try/catch/finally for exception handling)."""
        # Parse the try block
        try_block = self._parse_block()
        
        # Parse catch blocks
        catch_blocks = []
        while self._match(TokenType.CATCH):
            self._consume(TokenType.LPAREN, "Expected '(' after 'catch'")
            
            # Parse exception type (optional)
            exception_type = None
            exception_var = None
            
            if self._match(TokenType.IDENTIFIER):
                exception_type = self._previous().value
                
                # Check if there's a variable name after the type
                if self._match(TokenType.IDENTIFIER):
                    exception_var = self._previous().value
            
            self._consume(TokenType.RPAREN, "Expected ')' after catch clause")
            
            # Parse catch block
            catch_block = self._parse_block()
            catch_blocks.append((exception_type, exception_var, catch_block))
        
        # Parse finally block (optional)
        finally_block = None
        if self._match(TokenType.FINALLY):
            finally_block = self._parse_block()
        
        return RiskNode(try_block, catch_blocks, finally_block)
    
    def _parse_exploit_statement(self) -> ExploitNode:
        """Parse exploit statement (try/catch for security operations - legacy)."""
        # Parse the try block
        try_block = self._parse_block()
        
        # Parse catch blocks (otherwise clauses)
        catch_blocks = []
        while self._match(TokenType.OTHERWISE):
            self._consume(TokenType.LPAREN, "Expected '(' after 'otherwise'")
            if self._match(TokenType.IDENTIFIER):
                exception_name = self._previous().value
            else:
                exception_name = None
            self._consume(TokenType.RPAREN, "Expected ')' after exception name")
            catch_block = self._parse_block()
            catch_blocks.append((exception_name, catch_block))
        
        return ExploitNode(try_block, catch_blocks)

    def _parse_raise_exception_statement(self) -> RaiseExceptionNode:
        """Parse raise exception statement."""
        # Parse exception type (optional identifier)
        exception_type = None
        exception_message = None
        
        if self._match(TokenType.IDENTIFIER):
            exception_type = self._previous().value
        
        # Parse exception message (optional expression)
        if self._check(TokenType.STRING, TokenType.IDENTIFIER, TokenType.NUMBER, 
                      TokenType.LPAREN, TokenType.MINUS, TokenType.BANISH):
            exception_message = self._parse_expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after raise statement")
        
        return RaiseExceptionNode(exception_type, exception_message)
    
    def _parse_breach_statement(self) -> BreachNode:
        """Parse breach statement (async operations)."""
        async_block = self._parse_block()
        return BreachNode(async_block)


def parse(tokens: List[Token]) -> ProgramNode:
    """
    Convenience function to parse tokens into AST.
    
    Args:
        tokens: List of tokens from lexer
        
    Returns:
        ProgramNode representing the parsed program
        
    Raises:
        ReaperSyntaxError: On syntax errors
    """
    parser = Parser(tokens)
    return parser.parse()
