"""
REAPER Bytecode Compiler

This module compiles REAPER AST nodes into bytecode instructions
for execution by the virtual machine.
"""

from typing import Any, Dict, List, Optional, Union
from core.ast_nodes import *
from .instructions import OpCode, BytecodeInstruction, BytecodeProgram
from core.reaper_error import ReaperRuntimeError


class BytecodeCompiler:
    """Compiler that converts AST to bytecode."""
    
    def __init__(self):
        self.program = BytecodeProgram()
        self.current_function = None
        self.function_stack: List[str] = []
        self.label_counter = 0
    
    def compile(self, ast: ProgramNode) -> BytecodeProgram:
        """Compile AST program to bytecode."""
        self.program = BytecodeProgram()
        self.current_function = None
        self.function_stack = []
        self.label_counter = 0
        
        # Compile all statements
        for statement in ast.statements:
            self._compile_statement(statement)
        
        # Run optimization passes
        self._peephole_optimize()
        
        return self.program
    
    def _compile_statement(self, node: ASTNode) -> None:
        """Compile a statement node."""
        if isinstance(node, AssignmentNode):
            self._compile_assignment(node)
        elif isinstance(node, ExpressionStatementNode):
            self._compile_expression(node.expression)
            self.program.add_instruction(BytecodeInstruction(OpCode.POP))  # Pop return value
        elif isinstance(node, CallNode):
            # Function call as statement (e.g., raise TestFunction();)
            self._compile_call(node)
            self.program.add_instruction(BytecodeInstruction(OpCode.POP))  # Pop return value
        elif isinstance(node, HarvestNode):
            # Harvest statement (harvest expr1, expr2, ...;)
            # Compile each expression and call harvest builtin
            for expr in node.expressions:
                self._compile_expression(expr)
                self.program.add_instruction(BytecodeInstruction(OpCode.CALL_BUILTIN, "harvest"))
                self.program.add_instruction(BytecodeInstruction(OpCode.POP))  # Pop return value
        elif isinstance(node, IfNode):
            self._compile_if(node)
        elif isinstance(node, ShambleNode):
            self._compile_shamble(node)
        elif isinstance(node, DecayNode):
            self._compile_decay(node)
        elif isinstance(node, SoullessNode):
            self._compile_soulless(node)
        elif isinstance(node, InfectNode):
            self._compile_infect_function(node)
        elif isinstance(node, TombNode):
            self._compile_tomb_class(node)
        elif isinstance(node, ReapNode):
            self._compile_reap_return(node)
        elif isinstance(node, FleeNode):
            self._compile_flee_break(node)
        elif isinstance(node, PersistNode):
            self._compile_persist_continue(node)
        elif isinstance(node, BlockNode):
            self._compile_block(node)
        elif isinstance(node, InfiltrateNode):
            self._compile_infiltrate(node)
        elif isinstance(node, CloakNode):
            self._compile_cloak(node)
        elif isinstance(node, ExploitNode):
            self._compile_exploit(node)
        elif isinstance(node, BreachNode):
            self._compile_breach(node)
        else:
            raise ReaperRuntimeError(f"Unknown statement type: {type(node)}")
    
    def _compile_assignment(self, node: AssignmentNode) -> None:
        """Compile assignment statement."""
        # Compile the value expression
        self._compile_expression(node.value)
        
        # Store to appropriate location
        if isinstance(node.target, VariableNode):
            if node.is_declaration:
                # Variable declaration
                if node.var_type == "shadow":
                    # Convert to secure string
                    self.program.add_instruction(BytecodeInstruction(OpCode.SECURE_STRING))
                
                # Store to local if in function, global otherwise
                if self.current_function:
                    self.program.add_instruction(BytecodeInstruction(OpCode.STORE_LOCAL, node.target.name))
                else:
                    self.program.add_instruction(BytecodeInstruction(OpCode.STORE_GLOBAL, node.target.name))
            else:
                # Regular assignment
                if self.current_function:
                    self.program.add_instruction(BytecodeInstruction(OpCode.STORE_LOCAL, node.target.name))
                else:
                    self.program.add_instruction(BytecodeInstruction(OpCode.STORE_GLOBAL, node.target.name))
        else:
            raise ReaperRuntimeError(f"Unsupported assignment target: {type(node.target)}")
    
    def _compile_expression(self, node: ASTNode) -> None:
        """Compile an expression node."""
        if isinstance(node, NumberNode):
            self._compile_number(node)
        elif isinstance(node, StringNode):
            self._compile_string(node)
        elif isinstance(node, BooleanNode):
            self._compile_boolean(node)
        elif isinstance(node, HexLiteralNode):
            self._compile_hex_literal(node)
        elif isinstance(node, BinaryLiteralNode):
            self._compile_binary_literal(node)
        elif isinstance(node, PhantomLiteralNode):
            self._compile_phantom_literal(node)
        elif isinstance(node, SpecterLiteralNode):
            self._compile_specter_literal(node)
        elif isinstance(node, ShadowLiteralNode):
            self._compile_shadow_literal(node)
        elif isinstance(node, ArrayNode):
            self._compile_array(node)
        elif isinstance(node, DictionaryNode):
            self._compile_dictionary(node)
        elif isinstance(node, VariableNode):
            self._compile_variable(node)
        elif isinstance(node, BinaryOpNode):
            self._compile_binary_op(node)
        elif isinstance(node, ComparisonNode):
            self._compile_comparison(node)
        elif isinstance(node, UnaryOpNode):
            self._compile_unary_op(node)
        elif isinstance(node, CallNode):
            self._compile_call(node)
        elif isinstance(node, MethodCallNode):
            self._compile_method_call(node)
        elif isinstance(node, IndexAccessNode):
            self._compile_index_access(node)
        elif isinstance(node, PropertyAccessNode):
            self._compile_property_access(node)
        elif isinstance(node, VoidNode):
            self._compile_void(node)
        else:
            raise ReaperRuntimeError(f"Unknown expression type: {type(node)}")
    
    def _compile_number(self, node: NumberNode) -> None:
        """Compile number literal."""
        const_index = self.program.add_constant(node.value)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
    
    def _compile_string(self, node: StringNode) -> None:
        """Compile string literal."""
        const_index = self.program.add_constant(node.value)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
    
    def _compile_boolean(self, node: BooleanNode) -> None:
        """Compile boolean literal."""
        const_index = self.program.add_constant(node.value)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
    
    def _compile_hex_literal(self, node: HexLiteralNode) -> None:
        """Compile hex literal."""
        const_index = self.program.add_constant(node.value)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
    
    def _compile_binary_literal(self, node: BinaryLiteralNode) -> None:
        """Compile binary literal."""
        const_index = self.program.add_constant(node.value)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
    
    def _compile_phantom_literal(self, node: PhantomLiteralNode) -> None:
        """Compile phantom literal."""
        const_index = self.program.add_constant(node.value)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
    
    def _compile_specter_literal(self, node: SpecterLiteralNode) -> None:
        """Compile specter literal."""
        const_index = self.program.add_constant(node.value)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
    
    def _compile_shadow_literal(self, node: ShadowLiteralNode) -> None:
        """Compile shadow literal."""
        const_index = self.program.add_constant(node.value)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
        self.program.add_instruction(BytecodeInstruction(OpCode.SECURE_STRING))
    
    def _compile_array(self, node: ArrayNode) -> None:
        """Compile array literal."""
        # Create array with size
        size_const = self.program.add_constant(len(node.elements))
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, size_const))
        self.program.add_instruction(BytecodeInstruction(OpCode.ARRAY_NEW))
        
        # Set elements
        for i, element in enumerate(node.elements):
            # Duplicate array
            self.program.add_instruction(BytecodeInstruction(OpCode.DUP))
            
            # Push index
            index_const = self.program.add_constant(i)
            self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, index_const))
            
            # Compile element value
            self._compile_expression(element)
            
            # Set array element
            self.program.add_instruction(BytecodeInstruction(OpCode.ARRAY_SET))
    
    def _compile_dictionary(self, node: DictionaryNode) -> None:
        """Compile dictionary literal."""
        # Create empty dictionary
        self.program.add_instruction(BytecodeInstruction(OpCode.DICT_NEW))
        
        # Add key-value pairs
        for key, value in node.pairs:
            # Duplicate dictionary
            self.program.add_instruction(BytecodeInstruction(OpCode.DUP))
            
            # Compile key
            self._compile_expression(key)
            
            # Compile value
            self._compile_expression(value)
            
            # Set dictionary entry
            self.program.add_instruction(BytecodeInstruction(OpCode.DICT_SET))
    
    def _compile_variable(self, node: VariableNode) -> None:
        """Compile variable reference."""
        if self.current_function:
            self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_LOCAL, node.name))
        else:
            self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_GLOBAL, node.name))
    
    def _compile_binary_op(self, node: BinaryOpNode) -> None:
        """Compile binary operation."""
        # Try simple constant folding for numeric literals
        if isinstance(node.left, (NumberNode, HexLiteralNode, BinaryLiteralNode, PhantomLiteralNode)) \
           and isinstance(node.right, (NumberNode, HexLiteralNode, BinaryLiteralNode, PhantomLiteralNode)):
            left_val = self._literal_value(node.left)
            right_val = self._literal_value(node.right)
            op = node.operator
            try:
                result = None
                if op == '+':
                    result = left_val + right_val
                elif op == '-':
                    result = left_val - right_val
                elif op == '*':
                    result = left_val * right_val
                elif op == '/':
                    result = left_val / right_val
                elif op == '%':
                    result = left_val % right_val
                elif op == '<<':
                    result = int(left_val) << int(right_val)
                elif op == '>>':
                    result = int(left_val) >> int(right_val)
                elif op == '&':
                    result = int(left_val) & int(right_val)
                elif op == '|':
                    result = int(left_val) | int(right_val)
                elif op == '^':
                    result = int(left_val) ^ int(right_val)
                # If we computed a result, emit a single PUSH_CONST
                if result is not None:
                    const_index = self.program.add_constant(result)
                    self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
                    return
            except Exception:
                # Fall back to normal codegen if folding failed
                pass
        
        # Compile left and right operands normally
        self._compile_expression(node.left)
        self._compile_expression(node.right)
        
        # Map operator to opcode
        opcode_map = {
            '+': OpCode.ADD,
            '-': OpCode.SUB,
            '*': OpCode.MUL,
            '/': OpCode.DIV,
            '%': OpCode.MOD,
            '==': OpCode.EQ,
            '!=': OpCode.NE,
            '<': OpCode.LT,
            '<=': OpCode.LE,
            '>': OpCode.GT,
            '>=': OpCode.GE,
            '&&': OpCode.LOG_AND,
            '||': OpCode.LOG_OR,
            '&': OpCode.BIT_AND,
            '|': OpCode.BIT_OR,
            '^': OpCode.BIT_XOR,
            '<<': OpCode.BIT_SHL,
            '>>': OpCode.BIT_SHR,
            'rot': OpCode.BIT_ROT,
            'wither': OpCode.BIT_SHR,
            'spread': OpCode.BIT_SHL,
            'mutate': OpCode.BIT_XOR,
        }
        
        if node.operator in opcode_map:
            self.program.add_instruction(BytecodeInstruction(opcode_map[node.operator]))
        else:
            raise ReaperRuntimeError(f"Unknown binary operator: {node.operator}")
    
    def _compile_comparison(self, node: ComparisonNode) -> None:
        """Compile comparison operation."""
        # Compile left and right operands
        self._compile_expression(node.left)
        self._compile_expression(node.right)
        
        # Map operator to opcode
        opcode_map = {
            '==': OpCode.EQ,
            '!=': OpCode.NE,
            '<': OpCode.LT,
            '<=': OpCode.LE,
            '>': OpCode.GT,
            '>=': OpCode.GE,
        }
        
        if node.operator in opcode_map:
            self.program.add_instruction(BytecodeInstruction(opcode_map[node.operator]))
        else:
            raise ReaperRuntimeError(f"Unknown comparison operator: {node.operator}")
    
    def _compile_unary_op(self, node: UnaryOpNode) -> None:
        """Compile unary operation."""
        # Compile operand
        self._compile_expression(node.operand)
        
        # Map operator to opcode
        opcode_map = {
            '-': OpCode.NEG,
            '!': OpCode.LOG_NOT,
            '~': OpCode.BIT_NOT,
            'invert': OpCode.BIT_NOT,
        }
        
        if node.operator in opcode_map:
            self.program.add_instruction(BytecodeInstruction(opcode_map[node.operator]))
        else:
            raise ReaperRuntimeError(f"Unknown unary operator: {node.operator}")
    
    def _compile_call(self, node: CallNode) -> None:
        """Compile function call."""
        # Compile arguments first (in reverse order for stack)
        for arg in reversed(node.arguments):
            self._compile_expression(arg)
        
        # Check if built-in function
        builtin_functions = ['harvest', 'curse', 'haunt', 'infect', 'raise', 'reap', 
                           'flee', 'persist', 'rest', 'lesser', 'greater', 'risen', 'dead', 'void',
                           'summon', 'final_rest', 'absolute', 'raise_corpse', 'steal_soul']
        if node.function_name in builtin_functions:
            self.program.add_instruction(BytecodeInstruction(OpCode.CALL_BUILTIN, node.function_name))
        else:
            # User-defined function - call directly with function name
            # Arguments are already on the stack (pushed in reverse order)
            self.program.add_instruction(BytecodeInstruction(OpCode.CALL, node.function_name))
    
    def _compile_method_call(self, node: MethodCallNode) -> None:
        """Compile method call."""
        # Compile object
        self._compile_expression(node.object)
        
        # For now, treat as property access
        if node.method_name == 'curse':
            self.program.add_instruction(BytecodeInstruction(OpCode.CURSE))
        elif node.method_name == 'haunt':
            # Compile arguments
            for arg in node.arguments:
                self._compile_expression(arg)
            self.program.add_instruction(BytecodeInstruction(OpCode.HAUNT))
        else:
            raise ReaperRuntimeError(f"Unknown method: {node.method_name}")
    
    def _compile_index_access(self, node: IndexAccessNode) -> None:
        """Compile index access."""
        # Compile object
        self._compile_expression(node.object)
        
        # Compile index
        self._compile_expression(node.index)
        
        # Get element
        self.program.add_instruction(BytecodeInstruction(OpCode.ARRAY_GET))
    
    def _compile_property_access(self, node: PropertyAccessNode) -> None:
        """Compile property access."""
        # Compile object
        self._compile_expression(node.object)
        
        # Push property name
        const_index = self.program.add_constant(node.property_name)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
        
        # Get property
        self.program.add_instruction(BytecodeInstruction(OpCode.DICT_GET))
    
    def _compile_void(self, node: VoidNode) -> None:
        """Compile void literal."""
        const_index = self.program.add_constant(None)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, const_index))
    
    def _compile_if(self, node: IfNode) -> None:
        """Compile if statement."""
        # Compile condition
        self._compile_expression(node.condition)
        
        # Create labels
        else_label = self._generate_label()
        end_label = self._generate_label()
        
        # Jump to else if condition is false
        self.program.add_instruction(BytecodeInstruction(OpCode.JMP_IF_NOT, else_label))
        
        # Compile if body
        self._compile_statement(node.if_body)
        
        # Jump to end
        self.program.add_instruction(BytecodeInstruction(OpCode.JMP, end_label))
        
        # Set else label
        self._set_label(else_label)
        
        # Compile else body if exists
        if node.else_body:
            self._compile_statement(node.else_body)
        
        # Set end label
        self._set_label(end_label)
    
    def _compile_shamble(self, node: ShambleNode) -> None:
        """Compile shamble loop (for loop)."""
        # Create labels
        loop_label = self._generate_label()
        end_label = self._generate_label()
        
        # Compile start value
        self._compile_expression(node.start)
        
        # Store loop variable
        if self.current_function:
            self.program.add_instruction(BytecodeInstruction(OpCode.STORE_LOCAL, node.variable))
        else:
            self.program.add_instruction(BytecodeInstruction(OpCode.STORE_GLOBAL, node.variable))
        
        # Set loop label
        self._set_label(loop_label)
        
        # Load loop variable
        if self.current_function:
            self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_LOCAL, node.variable))
        else:
            self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_GLOBAL, node.variable))
        
        # Compile end value
        self._compile_expression(node.end)
        
        # Compare loop variable with end value
        self.program.add_instruction(BytecodeInstruction(OpCode.LT))
        
        # Jump to end if condition is false
        self.program.add_instruction(BytecodeInstruction(OpCode.JMP_IF_NOT, end_label))
        
        # Compile body
        self._compile_block(node.body)
        
        # Increment loop variable
        if self.current_function:
            self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_LOCAL, node.variable))
        else:
            self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_GLOBAL, node.variable))
        
        # Push 1
        one_const = self.program.add_constant(1)
        self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, one_const))
        
        # Add 1
        self.program.add_instruction(BytecodeInstruction(OpCode.ADD))
        
        # Store back to loop variable
        if self.current_function:
            self.program.add_instruction(BytecodeInstruction(OpCode.STORE_LOCAL, node.variable))
        else:
            self.program.add_instruction(BytecodeInstruction(OpCode.STORE_GLOBAL, node.variable))
        
        # Jump back to loop start
        self.program.add_instruction(BytecodeInstruction(OpCode.JMP, loop_label))
        
        # Set end label
        self._set_label(end_label)
    
    def _compile_decay(self, node: DecayNode) -> None:
        """Compile decay loop (while loop)."""
        # Create labels
        loop_label = self._generate_label()
        end_label = self._generate_label()
        
        # Set loop label
        self._set_label(loop_label)
        
        # Compile condition
        self._compile_expression(node.condition)
        
        # Jump to end if condition is false
        self.program.add_instruction(BytecodeInstruction(OpCode.JMP_IF_NOT, end_label))
        
        # Compile body
        self._compile_block(node.body)
        
        # Jump back to loop start
        self.program.add_instruction(BytecodeInstruction(OpCode.JMP, loop_label))
        
        # Set end label
        self._set_label(end_label)
    
    def _compile_soulless(self, node: SoullessNode) -> None:
        """Compile soulless loop (infinite loop)."""
        # Create labels
        loop_label = self._generate_label()
        end_label = self._generate_label()
        
        # Set loop label
        self._set_label(loop_label)
        
        # Compile body
        self._compile_block(node.body)
        
        # Jump back to loop start
        self.program.add_instruction(BytecodeInstruction(OpCode.JMP, loop_label))
        
        # Set end label
        self._set_label(end_label)
    
    def _compile_infect_function(self, node: InfectNode) -> None:
        """Compile infect function definition."""
        # If we're in the main program (not nested in another function),
        # we need to skip over the function body during main execution
        # Store the jump instruction index so we can fix it later
        skip_jmp_index = None
        if not self.current_function:
            # In main program - jump over function body
            # We'll set the target after compiling the body
            skip_jmp_index = len(self.program.instructions)
            self.program.add_instruction(BytecodeInstruction(OpCode.JMP, 0))  # Placeholder
        
        # Record function start (AFTER the skip JMP if we added one)
        func_start = len(self.program.instructions)
        
        # Extract parameter names
        param_names = [param[0] for param in node.params]
        
        # Register function with metadata
        self.program.add_function(node.name, func_start, param_names)
        
        # Set current function context
        old_function = self.current_function
        self.current_function = node.name
        self.function_stack.append(node.name)
        
        # Compile function body
        # Parameters will be stored as locals when the function is called
        self._compile_block(node.body)
        
        # Add implicit return if function doesn't end with explicit return
        # (We check if the last instruction is RETURN, but for simplicity, we always add one)
        # The VM will handle this correctly
        self.program.add_instruction(BytecodeInstruction(OpCode.RETURN))
        
        # Fix the jump target if we added one
        if skip_jmp_index is not None:
            skip_target = len(self.program.instructions)
            self.program.instructions[skip_jmp_index].operand = skip_target
        
        # Restore current function context
        self.current_function = old_function
        if self.function_stack:
            self.function_stack.pop()
    
    def _compile_tomb_class(self, node: TombNode) -> None:
        """Compile tomb class definition."""
        # For now, classes are not implemented in bytecode
        pass
    
    def _compile_reap_return(self, node: ReapNode) -> None:
        """Compile reap return statement."""
        if node.value:
            self._compile_expression(node.value)
        else:
            # Push None
            none_const = self.program.add_constant(None)
            self.program.add_instruction(BytecodeInstruction(OpCode.PUSH_CONST, none_const))
        
        self.program.add_instruction(BytecodeInstruction(OpCode.RETURN))
    
    def _compile_flee_break(self, node: FleeNode) -> None:
        """Compile flee break statement."""
        # For now, break is not implemented in bytecode
        pass
    
    def _compile_persist_continue(self, node: PersistNode) -> None:
        """Compile persist continue statement."""
        # For now, continue is not implemented in bytecode
        pass
    
    def _compile_block(self, node: BlockNode) -> None:
        """Compile block statement."""
        for statement in node.statements:
            self._compile_statement(statement)
    
    def _compile_infiltrate(self, node: InfiltrateNode) -> None:
        """Compile infiltrate statement."""
        # For now, infiltrate is not implemented in bytecode
        pass
    
    def _compile_cloak(self, node: CloakNode) -> None:
        """Compile cloak statement."""
        # For now, cloak is not implemented in bytecode
        pass
    
    def _compile_exploit(self, node: ExploitNode) -> None:
        """Compile exploit statement."""
        # For now, exploit is not implemented in bytecode
        pass
    
    def _compile_breach(self, node: BreachNode) -> None:
        """Compile breach statement."""
        # For now, breach is not implemented in bytecode
        pass
    
    def _generate_label(self) -> int:
        """Generate a unique label."""
        self.label_counter += 1
        return self.label_counter
    
    def _set_label(self, label: int) -> None:
        """Set a label at current position."""
        # Labels are handled by the instruction addresses
        pass

    # ---------------------
    # Optimization Passes
    # ---------------------
    def _peephole_optimize(self) -> None:
        """Apply simple peephole optimizations to instruction stream."""
        ins = self.program.instructions
        consts = self.program.constants
        optimized: List[BytecodeInstruction] = []
        i = 0
        while i < len(ins):
            cur = ins[i]
            nxt = ins[i+1] if i + 1 < len(ins) else None
            nxt2 = ins[i+2] if i + 2 < len(ins) else None

            # Remove no-op patterns: DUP followed by POP
            if cur.opcode == OpCode.DUP and nxt and nxt.opcode == OpCode.POP:
                i += 2
                continue

            # Remove dead pushes: PUSH_CONST X followed by POP
            if cur.opcode == OpCode.PUSH_CONST and nxt and nxt.opcode == OpCode.POP:
                i += 2
                continue

            # Fold arithmetic on immediate constants: PUSH_CONST a, PUSH_CONST b, OP
            if (
                cur.opcode == OpCode.PUSH_CONST and
                nxt and nxt.opcode == OpCode.PUSH_CONST and
                nxt2 and nxt2.opcode in (OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD,
                                         OpCode.BIT_AND, OpCode.BIT_OR, OpCode.BIT_XOR,
                                         OpCode.BIT_SHL, OpCode.BIT_SHR)
            ):
                try:
                    a = consts[cur.operand]
                    b = consts[nxt.operand]
                    res = None
                    if nxt2.opcode == OpCode.ADD:
                        res = a + b
                    elif nxt2.opcode == OpCode.SUB:
                        res = a - b
                    elif nxt2.opcode == OpCode.MUL:
                        res = a * b
                    elif nxt2.opcode == OpCode.DIV:
                        res = a / b
                    elif nxt2.opcode == OpCode.MOD:
                        res = a % b
                    elif nxt2.opcode == OpCode.BIT_AND:
                        res = int(a) & int(b)
                    elif nxt2.opcode == OpCode.BIT_OR:
                        res = int(a) | int(b)
                    elif nxt2.opcode == OpCode.BIT_XOR:
                        res = int(a) ^ int(b)
                    elif nxt2.opcode == OpCode.BIT_SHL:
                        res = int(a) << int(b)
                    elif nxt2.opcode == OpCode.BIT_SHR:
                        res = int(a) >> int(b)
                    if res is not None:
                        idx = self.program.add_constant(res)
                        optimized.append(BytecodeInstruction(OpCode.PUSH_CONST, idx))
                        i += 3
                        continue
                except Exception:
                    pass

            # Remove unconditional jump to next instruction
            if cur.opcode == OpCode.JMP and isinstance(cur.operand, int):
                target = cur.operand
                if target == i + 1:
                    i += 1
                    continue

            # Default: keep instruction
            optimized.append(cur)
            i += 1

        self.program.instructions = optimized

    def _literal_value(self, node: ASTNode) -> Union[int, float]:
        """Extract numeric value from literal nodes."""
        if isinstance(node, NumberNode):
            return node.value
        if isinstance(node, HexLiteralNode):
            return node.value
        if isinstance(node, BinaryLiteralNode):
            return node.value
        if isinstance(node, PhantomLiteralNode):
            return node.value
        raise ReaperRuntimeError("Unsupported literal for folding")
