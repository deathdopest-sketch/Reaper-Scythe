"""
REAPER Bytecode Compiler

Compiles a parsed REAPER program (AST) into bytecode for the VM.

The compiled program mirrors the tree-walking interpreter's semantics exactly:
variables live in the interpreter's Environment objects (block scoping,
dynamic scoping for calls), and operators, methods and built-ins call the
interpreter's own implementations at run time. Function, lambda and method
bodies are compiled once and appended after the main program; the VM finds
them by the identity of their AST node.

A few rarely used constructs (imports, async blocks, list comprehensions,
cloak) are evaluated by the interpreter through EXEC_NODE. They contain no
control flow that escapes them, and any user functions they call still run
as bytecode.
"""

from typing import Any, List, Optional, Tuple

from core.ast_nodes import *
from core.reaper_error import ReaperRuntimeError
from .instructions import OpCode, BytecodeInstruction, BytecodeProgram


# Nodes evaluated by the interpreter (see module docstring).
_DELEGATED = (InfiltrateNode, CloakNode, BreachNode, AwaitNode, ListComprehensionNode)


class _Loop:
    """Compile-time loop context for flee (break) / persist (continue)."""

    def __init__(self, scope_depth: int, try_depth: int, has_iterator: bool):
        self.scope_depth = scope_depth
        self.try_depth = try_depth
        self.has_iterator = has_iterator
        self.continue_target: Optional[int] = None
        self.break_jumps: List[int] = []
        self.continue_jumps: List[int] = []


class _Try:
    """Compile-time protected region; finally code is inlined on early exits."""

    def __init__(self, scope_depth: int, finally_block: Optional[BlockNode]):
        self.scope_depth = scope_depth
        self.finally_block = finally_block


class BytecodeCompiler:
    """Compiles REAPER AST nodes to bytecode."""

    def __init__(self):
        self.program = BytecodeProgram()
        self._pending: List[Tuple[int, Any]] = []  # (const index, function-like node)
        self._const_index = {}
        self._scope_depth = 0
        self._loops: List[_Loop] = []
        self._tries: List[_Try] = []
        self._node = None  # node providing positions for emitted instructions

    # ------------------------------------------------------------------ driver

    def compile(self, ast: ProgramNode) -> BytecodeProgram:
        """Compile a ProgramNode into a BytecodeProgram."""
        self.program = BytecodeProgram()
        self._pending = []
        self._const_index = {}
        for statement in ast.statements:
            self._statement(statement)
        self._emit(OpCode.HALT)

        # Function bodies go after the main program; compiling one can queue more.
        compiled = set()
        while self._pending:
            const_index, node = self._pending.pop(0)
            if const_index in compiled:
                continue
            compiled.add(const_index)
            self._compile_function_body(const_index, node)
        return self.program

    # --------------------------------------------------------------- emitting

    def _emit(self, opcode: OpCode, operand: Any = None, node: Any = None) -> int:
        source = node or self._node
        instruction = BytecodeInstruction(
            opcode, operand,
            getattr(source, "line", 0) or 0,
            getattr(source, "column", 0) or 0,
        )
        instruction.filename = getattr(source, "filename", None)
        return self.program.add_instruction(instruction)

    def _here(self) -> int:
        return len(self.program.instructions)

    def _patch(self, index: int, target: int) -> None:
        instruction = self.program.instructions[index]
        if instruction.opcode == OpCode.FOR_ITER:
            name, mode, _ = instruction.operand
            instruction.operand = (name, mode, target)
        else:
            instruction.operand = target

    def _const(self, value: Any) -> int:
        """Index of a literal constant, shared between identical literals."""
        key = (type(value), value)
        index = self._const_index.get(key)
        if index is None:
            index = self.program.add_constant(value)
            self._const_index[key] = index
        return index

    def _function_const(self, node: Any) -> int:
        index = self.program.add_constant(node)
        self._pending.append((index, node))
        return index

    # ------------------------------------------------------------ statements

    def _statement(self, node: ASTNode) -> None:
        previous, self._node = self._node, node
        try:
            self._compile_statement(node)
        finally:
            self._node = previous

    def _compile_statement(self, node: ASTNode) -> None:
        if isinstance(node, BlockNode):
            self._block(node)
        elif isinstance(node, AssignmentNode):
            self._assignment(node, keep_value=False)
        elif isinstance(node, CompoundAssignmentNode):
            self._compound_assignment(node, keep_value=False)
        elif isinstance(node, (IndexAssignNode, PropertyAssignNode)):
            self._target_assign(node, keep_value=False)
        elif isinstance(node, HarvestNode):
            for expression in node.expressions:
                self._expression(expression)
            self._emit(OpCode.HARVEST, len(node.expressions))
        elif isinstance(node, IfNode):
            self._if(node)
        elif isinstance(node, ShambleNode):
            self._shamble(node)
        elif isinstance(node, DecayNode):
            self._decay(node)
        elif isinstance(node, SoullessNode):
            self._soulless(node)
        elif isinstance(node, JudgeNode):
            self._judge(node)
        elif isinstance(node, FleeNode):
            self._loop_exit(is_break=True)
        elif isinstance(node, PersistNode):
            self._loop_exit(is_break=False)
        elif isinstance(node, ReapNode):
            self._reap(node)
        elif isinstance(node, (InfectNode, TombNode)):
            if isinstance(node, TombNode):
                const_index = self.program.add_constant(node)
                for method in node.methods:
                    if isinstance(method, InfectNode):
                        self._function_const(method)
            else:
                const_index = self._function_const(node)
            self._emit(OpCode.DEFINE_FUNCTION, const_index)
        elif isinstance(node, RiskNode):
            self._risk(node)
        elif isinstance(node, ExploitNode):
            self._exploit(node)
        elif isinstance(node, RaiseExceptionNode):
            self._raise_exception(node)
        elif isinstance(node, RestNode):
            self._expression(node.duration)
            self._emit(OpCode.REST)
        elif isinstance(node, ExpressionStatementNode):
            self._expression(node.expression)
            self._emit(OpCode.POP)
        else:
            # Any expression used as a statement.
            self._expression(node)
            self._emit(OpCode.POP)

    def _block(self, node: BlockNode) -> None:
        self._emit(OpCode.PUSH_SCOPE)
        self._scope_depth += 1
        for statement in node.statements:
            self._statement(statement)
        self._scope_depth -= 1
        self._emit(OpCode.POP_SCOPE)

    def _body(self, node: ASTNode) -> None:
        """Compile a loop/branch body, which the interpreter executes as a node."""
        self._statement(node)

    def _assignment(self, node: AssignmentNode, keep_value: bool) -> None:
        self._expression(node.value)
        if node.var_type == "shadow":
            self._emit(OpCode.SECURE_STRING)
        target = node.target
        if isinstance(target, VariableNode):
            if keep_value:
                self._emit(OpCode.DUP)
            if node.is_declaration:
                self._emit(OpCode.DEFINE_NAME, (target.name, node.var_type))
            else:
                self._emit(OpCode.STORE_NAME, (target.name, node.var_type))
        elif isinstance(target, IndexAccessNode):
            if keep_value:
                self._emit(OpCode.DUP)
            self._index_store(target)
        elif isinstance(target, PropertyAccessNode):
            if keep_value:
                self._emit(OpCode.DUP)
            self._property_store(target)
        else:
            self._raise_runtime("Invalid assignment target")

    def _index_store(self, target: IndexAccessNode) -> None:
        # value is already on the stack; the interpreter evaluates obj, index after it
        self._expression(target.object)
        self._expression(target.index)
        self._emit(OpCode.INDEX_SET, node=target)

    def _property_store(self, target: PropertyAccessNode) -> None:
        self._expression(target.object)
        self._emit(OpCode.PROP_SET, target.property_name, node=target)

    def _target_assign(self, node: ASTNode, keep_value: bool) -> None:
        self._expression(node.value)
        if keep_value:
            self._emit(OpCode.DUP)
        self._expression(node.object)
        if isinstance(node, IndexAssignNode):
            self._expression(node.index)
            self._emit(OpCode.INDEX_SET)
        else:
            self._emit(OpCode.PROP_SET, node.property_name)

    def _compound_assignment(self, node: CompoundAssignmentNode, keep_value: bool) -> None:
        operators = {"+=": "+", "-=": "-", "*=": "*", "/=": "/", "%=": "%"}
        target = node.target
        if not isinstance(target, (VariableNode, IndexAccessNode, PropertyAccessNode)):
            self._raise_runtime("Invalid compound assignment target")
            return
        self._expression(target)                  # current value
        self._expression(node.value)
        operator = operators.get(node.operator)
        if operator is None:
            self._raise_runtime(f"Unknown compound assignment operator: {node.operator}")
            return
        self._emit(OpCode.BINARY_OP, operator)
        if keep_value:
            self._emit(OpCode.DUP)
        if isinstance(target, VariableNode):
            self._emit(OpCode.SET_NAME, target.name)
        elif isinstance(target, IndexAccessNode):
            self._index_store(target)             # re-evaluates obj/index, like the interpreter
        else:
            self._property_store(target)

    def _if(self, node: IfNode) -> None:
        end_jumps = []
        branches = [(node.condition, node.if_body)]
        branches += list(zip(node.elif_conditions or [], node.elif_bodies or []))
        for condition, body in branches:
            self._expression(condition)
            self._emit(OpCode.TO_BOOL, node=node)
            skip = self._emit(OpCode.JMP_IF_NOT, 0)
            self._body(body)
            end_jumps.append(self._emit(OpCode.JMP, 0))
            self._patch(skip, self._here())
        if node.else_body:
            self._body(node.else_body)
        for jump in end_jumps:
            self._patch(jump, self._here())

    def _loop(self, body: ASTNode, has_iterator: bool, var_name: Optional[str] = None,
              mode: Optional[str] = None) -> None:
        loop = _Loop(self._scope_depth, len(self._tries), has_iterator)
        self._loops.append(loop)
        top = self._here()
        loop.continue_target = top
        advance = self._emit(OpCode.FOR_ITER, (var_name, mode, 0)) if has_iterator else None
        self._body(body)
        self._emit(OpCode.JMP, top)
        exit_pc = self._here()
        if advance is not None:
            self._patch(advance, exit_pc)
        # break: an iterator, if any, is still on the stack
        if has_iterator and loop.break_jumps:
            skip = self._emit(OpCode.JMP, 0)
            pop_pc = self._here()
            self._emit(OpCode.POP)
            for jump in loop.break_jumps:
                self._patch(jump, pop_pc)
            self._patch(skip, self._here())
        else:
            for jump in loop.break_jumps:
                self._patch(jump, exit_pc)
        for jump in loop.continue_jumps:
            self._patch(jump, top)
        self._loops.pop()

    def _shamble(self, node: ShambleNode) -> None:
        self._expression(node.start)
        self._expression(node.end)
        self._emit(OpCode.ITER_RANGE)
        self._loop(node.body, True, node.var_name, "range")

    def _decay(self, node: DecayNode) -> None:
        self._expression(node.iterable)
        self._emit(OpCode.ITER_LIST)
        self._loop(node.body, True, node.var_name, "decay")

    def _soulless(self, node: SoullessNode) -> None:
        self._loop(node.body, False)

    def _judge(self, node: JudgeNode) -> None:
        self._expression(node.expression)
        end_jumps = []
        for case_value, case_body in node.cases:
            self._emit(OpCode.DUP)
            self._expression(case_value)
            self._emit(OpCode.EQ)                 # plain ==, as the interpreter does
            skip = self._emit(OpCode.JMP_IF_NOT, 0)
            self._emit(OpCode.POP)
            self._body(case_body)
            end_jumps.append(self._emit(OpCode.JMP, 0))
            self._patch(skip, self._here())
        self._emit(OpCode.POP)
        if node.default_body:
            self._body(node.default_body)
        for jump in end_jumps:
            self._patch(jump, self._here())

    def _unwind_to(self, scope_depth: int, try_depth: int) -> None:
        """Leave try regions (running their finally code) and scopes for an early exit."""
        for region in reversed(self._tries[try_depth:]):
            while self._scope_depth > region.scope_depth:
                self._emit(OpCode.POP_SCOPE)
                self._scope_depth -= 1
            self._emit(OpCode.POP_TRY)
            if region.finally_block is not None:
                saved_tries = self._tries
                self._tries = self._tries[:self._tries.index(region)]
                self._body(region.finally_block)
                self._tries = saved_tries
        while self._scope_depth > scope_depth:
            self._emit(OpCode.POP_SCOPE)
            self._scope_depth -= 1

    def _loop_exit(self, is_break: bool) -> None:
        if not self._loops:
            self._emit(OpCode.RAISE_FLOW, "flee" if is_break else "persist")
            return
        loop = self._loops[-1]
        saved_depth = self._scope_depth
        self._unwind_to(loop.scope_depth, loop.try_depth)
        jump = self._emit(OpCode.JMP, 0)
        (loop.break_jumps if is_break else loop.continue_jumps).append(jump)
        self._scope_depth = saved_depth

    def _reap(self, node: ReapNode) -> None:
        if node.value is not None:
            self._expression(node.value)
        else:
            self._emit(OpCode.PUSH_CONST, self._const(None))
        if self._tries:
            # Run enclosing finally blocks; RETURN_VALUE itself unwinds scopes.
            saved_depth = self._scope_depth
            self._unwind_to(self._scope_depth, 0)
            self._scope_depth = saved_depth
        self._emit(OpCode.RETURN_VALUE)

    def _risk(self, node: RiskNode) -> None:
        outer = None
        if node.finally_block is not None:
            # Errors escaping the catch blocks must still run finally.
            outer = self._emit(OpCode.SETUP_TRY, 0)
            self._tries.append(_Try(self._scope_depth, node.finally_block))
        handler = self._emit(OpCode.SETUP_TRY, 0)
        self._tries.append(_Try(self._scope_depth, None))
        self._body(node.try_block)
        self._tries.pop()
        self._emit(OpCode.POP_TRY)
        done = [self._emit(OpCode.JMP, 0)]

        # Handler: the exception is on the stack.
        self._patch(handler, self._here())
        self._emit(OpCode.WRAP_EXC, node=node)
        for exception_type, var_name, catch_block in node.catch_blocks:
            self._emit(OpCode.MATCH_EXC, (exception_type, "risk"))
            skip = self._emit(OpCode.JMP_IF_NOT, 0)
            if var_name:
                self._emit(OpCode.PUSH_SCOPE)
                self._scope_depth += 1
                self._emit(OpCode.DEFINE_NAME, (var_name, "ReaperError"), node=node)
            else:
                self._emit(OpCode.POP)
            self._body(catch_block)
            if var_name:
                self._scope_depth -= 1
                self._emit(OpCode.POP_SCOPE)
            done.append(self._emit(OpCode.JMP, 0))
            self._patch(skip, self._here())
        self._emit(OpCode.RERAISE)

        for jump in done:
            self._patch(jump, self._here())
        if outer is not None:
            self._tries.pop()
            self._emit(OpCode.POP_TRY)
            self._body(node.finally_block)
            skip_handler = self._emit(OpCode.JMP, 0)
            self._patch(outer, self._here())
            self._body(node.finally_block)
            self._emit(OpCode.RERAISE)
            self._patch(skip_handler, self._here())

    def _exploit(self, node: ExploitNode) -> None:
        handler = self._emit(OpCode.SETUP_TRY, 0)
        self._tries.append(_Try(self._scope_depth, None))
        for statement in node.try_block.statements:
            self._statement(statement)
        self._tries.pop()
        self._emit(OpCode.POP_TRY)
        done = [self._emit(OpCode.JMP, 0)]
        self._patch(handler, self._here())
        for exception_name, catch_block in node.catch_blocks:
            self._emit(OpCode.MATCH_EXC, (exception_name, "exploit"))
            skip = self._emit(OpCode.JMP_IF_NOT, 0)
            self._emit(OpCode.POP)
            for statement in catch_block.statements:
                self._statement(statement)
            done.append(self._emit(OpCode.JMP, 0))
            self._patch(skip, self._here())
        self._emit(OpCode.RERAISE)
        for jump in done:
            self._patch(jump, self._here())

    def _raise_exception(self, node: RaiseExceptionNode) -> None:
        if node.exception_message is not None:
            self._expression(node.exception_message)
        self._emit(OpCode.RAISE_EXC, (node.exception_type, node.exception_message is not None))

    def _raise_runtime(self, message: str) -> None:
        self._emit(OpCode.PUSH_CONST, self._const(message))
        self._emit(OpCode.RAISE_EXC, ("ReaperRuntimeError", True))

    # ----------------------------------------------------------- functions

    def _compile_function_body(self, const_index: int, node: Any) -> None:
        entry = self._here()
        self.program.function_entries[const_index] = entry
        saved = (self._scope_depth, self._loops, self._tries, self._node)
        self._scope_depth, self._loops, self._tries, self._node = 0, [], [], node
        if isinstance(node, LambdaNode) and not isinstance(node.body, BlockNode):
            self._expression(node.body)
            self._emit(OpCode.RETURN_VALUE)
        else:
            self._statement(node.body)
            self._emit(OpCode.PUSH_CONST, self._const(None))
            self._emit(OpCode.RETURN_VALUE)
        self._scope_depth, self._loops, self._tries, self._node = saved
        name = getattr(node, "name", None)
        if name and name not in self.program.functions:
            self.program.add_function(name, entry, [p[0] for p in node.params])

    # ---------------------------------------------------------- expressions

    def _expression(self, node: ASTNode) -> None:
        previous, self._node = self._node, node
        try:
            self._compile_expression(node)
        finally:
            self._node = previous

    def _compile_expression(self, node: ASTNode) -> None:
        if isinstance(node, (NumberNode, BooleanNode, HexLiteralNode,
                             BinaryLiteralNode, PhantomLiteralNode)):
            self._emit(OpCode.PUSH_CONST, self._const(node.value))
        elif isinstance(node, VoidNode):
            self._emit(OpCode.PUSH_CONST, self._const(None))
        elif isinstance(node, (StringNode, SpecterLiteralNode)):
            self._emit(OpCode.LOAD_STR, self._const(node.value))
        elif isinstance(node, ShadowLiteralNode):
            self._emit(OpCode.LOAD_STR, self._const(node.value))
            self._emit(OpCode.SECURE_STRING)
        elif isinstance(node, InterpolatedStringNode):
            for part in node.parts:
                if isinstance(part, StringNode):
                    self._emit(OpCode.PUSH_CONST, self._const(part.value))
                else:
                    self._expression(part)
            self._emit(OpCode.BUILD_STRING, len(node.parts))
        elif isinstance(node, ArrayNode):
            for element in node.elements:
                self._expression(element)
            self._emit(OpCode.BUILD_ARRAY, len(node.elements))
        elif isinstance(node, DictionaryNode):
            for key, value in node.pairs:
                self._expression(key)
                self._expression(value)
            self._emit(OpCode.BUILD_DICT, len(node.pairs))
        elif isinstance(node, VariableNode):
            self._emit(OpCode.LOAD_NAME, node.name)
        elif isinstance(node, AssignmentNode):
            self._assignment(node, keep_value=True)
        elif isinstance(node, CompoundAssignmentNode):
            self._compound_assignment(node, keep_value=True)
        elif isinstance(node, (IndexAssignNode, PropertyAssignNode)):
            self._target_assign(node, keep_value=True)
        elif isinstance(node, BinaryOpNode):
            self._expression(node.left)
            self._expression(node.right)
            self._emit(OpCode.BINARY_OP, node.operator)
        elif isinstance(node, UnaryOpNode):
            self._expression(node.operand)
            self._emit(OpCode.UNARY_OP, node.operator)
        elif isinstance(node, ComparisonNode):
            self._expression(node.left)
            self._expression(node.right)
            self._emit(OpCode.COMPARE_OP, node.operator)
        elif isinstance(node, LogicalOpNode):
            self._logical(node)
        elif isinstance(node, IndexAccessNode):
            self._expression(node.object)
            self._expression(node.index)
            self._emit(OpCode.INDEX_GET)
        elif isinstance(node, SliceNode):
            self._expression(node.object)
            for part in (node.start, node.end, node.step):
                if part is not None:
                    self._expression(part)
            self._emit(OpCode.SLICE, (node.start is not None, node.end is not None,
                                      node.step is not None))
        elif isinstance(node, PropertyAccessNode):
            self._expression(node.object)
            self._emit(OpCode.PROP_GET, node.property_name)
        elif isinstance(node, MethodCallNode):
            self._expression(node.object)
            for argument in node.arguments:
                self._expression(argument)
            self._emit(OpCode.CALL_METHOD, (node.method_name, len(node.arguments)))
        elif isinstance(node, CallNode):
            for argument in node.arguments:
                self._expression(argument)
            self._emit(OpCode.CALL_NAME, (node.function_name, len(node.arguments)))
        elif isinstance(node, LambdaNode):
            self._emit(OpCode.PUSH_CONST, self._function_const(node))
        elif isinstance(node, SpawnNode):
            self._emit(OpCode.SPAWN, self.program.add_constant(node))
        elif isinstance(node, _DELEGATED):
            self._emit(OpCode.EXEC_NODE, self.program.add_constant(node))
        elif isinstance(node, (InfectNode, TombNode, BlockNode, IfNode, ShambleNode,
                               DecayNode, SoullessNode, JudgeNode, RiskNode, ExploitNode,
                               HarvestNode, RestNode, FleeNode, PersistNode, ReapNode,
                               RaiseExceptionNode, ExpressionStatementNode)):
            # Statements evaluate to void when used for their value.
            self._statement(node)
            self._emit(OpCode.PUSH_CONST, self._const(None))
        else:
            raise ReaperRuntimeError(
                f"Bytecode compiler: unsupported node {type(node).__name__}",
                getattr(node, "line", 0), getattr(node, "column", 0))

    def _logical(self, node: LogicalOpNode) -> None:
        self._expression(node.left)
        self._emit(OpCode.TO_BOOL, node=node)
        if node.operator not in ("corrupt", "infest"):
            self._raise_runtime(f"Unknown logical operator: {node.operator}")
            return
        if not node.short_circuit:
            self._expression(node.right)
            self._emit(OpCode.TO_BOOL, node=node)
            self._emit(OpCode.LOG_AND if node.operator == "corrupt" else OpCode.LOG_OR)
            return
        self._emit(OpCode.DUP)
        jump = self._emit(OpCode.JMP_IF_NOT if node.operator == "corrupt" else OpCode.JMP_IF, 0)
        self._emit(OpCode.POP)
        self._expression(node.right)
        self._emit(OpCode.TO_BOOL, node=node)
        self._patch(jump, self._here())
