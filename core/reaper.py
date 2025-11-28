#!/usr/bin/env python3
"""
REAPER Language Interpreter - CLI Entry Point

This module provides the command-line interface for the REAPER language interpreter,
including file execution mode and interactive REPL with advanced features.
"""

import argparse
import os
import sys
import signal
from typing import List, Optional, Any
from pathlib import Path
from .emoji_filter import safe_print, filter_for_windows

# Optional readline import (not available on Windows)
try:
    import readline
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

# Import REAPER modules
from .lexer import tokenize
from .parser import parse
from .interpreter import Interpreter
from .environment import Environment
from .reaper_error import (
    ReaperError, ReaperSyntaxError, ReaperRuntimeError, ReaperTypeError,
    ReaperRecursionError, ReaperMemoryError, ReaperIndexError,
    ReaperKeyError, ReaperZeroDivisionError, format_error_with_suggestion
)


def _format_error_message(error_type: str, error: ReaperError, source_lines: Optional[List[str]] = None) -> str:
    """
    Format an error message with enhanced context.
    
    Args:
        error_type: Type of error (e.g., "Syntax Error")
        error: The error object
        source_lines: Source code lines for context
        
    Returns:
        Formatted error message
    """
    lines = []
    lines.append(f"=== {error_type} ===")
    
    # Get available names for suggestions (if runtime error)
    available_names = None
    if isinstance(error, ReaperRuntimeError) and hasattr(error, 'message'):
        error_str = error.message
        if "Available names:" in error_str:
            try:
                names_part = error_str.split("Available names:")[1].strip()
                available_names = [n.strip() for n in names_part.split(",")]
            except:
                pass
    
    # Use the error's format_error method
    formatted = error.format_error(source_lines)
    
    # Add suggestions for undefined variables
    if isinstance(error, ReaperRuntimeError) and "undefined" in error.message.lower():
        if available_names:
            formatted = format_error_with_suggestion(error, source_lines, available_names)
    
    lines.append(formatted)
    lines.append("=" * (len(error_type) + 8))
    
    return "\n".join(lines)


class ReaperREPL:
    """
    Interactive REPL for REAPER language.
    
    Features:
    - Multi-line input support
    - Command history
    - Tab completion
    - Special commands
    - Persistent environment
    - Syntax highlighting (optional)
    """
    
    def __init__(self):
        """Initialize REPL with environment and settings."""
        self.environment = Environment()
        self.interpreter = Interpreter()
        self.interpreter.global_environment = self.environment
        self.interpreter.environment_stack.clear()
        self.interpreter.environment_stack.push(self.environment)
        
        # Multi-line input tracking
        self.pending_input = ""
        self.brace_depth = 0
        self.paren_depth = 0
        self.bracket_depth = 0
        
        # Setup readline
        self._setup_readline()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
    
    def _setup_readline(self) -> None:
        """Setup readline for history and completion."""
        if not HAS_READLINE:
            return  # Skip readline setup on Windows
        
        # Enable history
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self._completer)
        
        # History file
        history_file = os.path.expanduser("~/.reaper_history")
        try:
            readline.read_history_file(history_file)
        except FileNotFoundError:
            pass
        
        # Save history on exit
        import atexit
        atexit.register(lambda: readline.write_history_file(history_file))
    
    def _completer(self, text: str, state: int) -> Optional[str]:
        """Tab completion for keywords and variables."""
        keywords = [
            "corpse", "soul", "crypt", "grimoire", "tomb", "wraith", "void", "eternal",
            "infect", "raise", "harvest", "reap", "shamble", "decay", "soulless", "spawn",
            "if", "otherwise", "flee", "persist", "corrupt", "infest", "banish", "rest",
            "this", "from", "to", "in", "DEAD", "RISEN"
        ]
        
        # Get available variables
        variables = self.environment.all_names()
        
        # Combine keywords and variables
        completions = keywords + variables
        
        # Filter matches
        matches = [c for c in completions if c.startswith(text)]
        
        if state < len(matches):
            return matches[state]
        return None
    
    def _handle_interrupt(self, signum: int, frame: Any) -> None:
        """Handle Ctrl+C interrupt."""
        safe_print("\n[INTERRUPTED] Interrupted! Use .exit to quit.")
        self.pending_input = ""
        self.brace_depth = 0
        self.paren_depth = 0
        self.bracket_depth = 0
    
    def _is_multiline_input(self, line: str) -> bool:
        """Check if input needs continuation."""
        # Count braces, parentheses, brackets
        for char in line:
            if char == '{':
                self.brace_depth += 1
            elif char == '}':
                self.brace_depth -= 1
            elif char == '(':
                self.paren_depth += 1
            elif char == ')':
                self.paren_depth -= 1
            elif char == '[':
                self.bracket_depth += 1
            elif char == ']':
                self.bracket_depth -= 1
        
        # Check for incomplete statements
        return (self.brace_depth > 0 or self.paren_depth > 0 or 
                self.bracket_depth > 0 or line.strip().endswith('\\'))
    
    def _get_prompt(self) -> str:
        """Get current prompt based on input state."""
        if self.pending_input:
            return "REAPER... "
        else:
            return "REAPER> "
    
    def _handle_special_command(self, line: str) -> bool:
        """Handle special REPL commands. Returns True if handled."""
        command = line.strip()
        
        if command == ".exit":
            safe_print("The reaper has finished harvesting. Farewell!")
            sys.exit(0)
        
        elif command == ".clear":
            self.environment = Environment()
            self.interpreter.global_environment = self.environment
            self.interpreter.environment_stack.clear()
            self.interpreter.environment_stack.push(self.environment)
            safe_print("Environment cleared.")
            return True
        
        elif command == ".help":
            self._show_help()
            return True
        
        elif command == ".vars":
            self._show_variables()
            return True
        
        elif command == ".funcs":
            self._show_functions()
            return True
        
        elif command.startswith(".types "):
            var_name = command[7:].strip()
            self._show_variable_type(var_name)
            return True
        
        return False
    
    def _show_help(self) -> None:
        """Show REPL help."""
        safe_print("""
[REAPER] REAPER Language REPL Commands:

  .exit     - Exit the REPL
  .clear    - Clear the environment
  .help     - Show this help
  .vars     - List all variables
  .funcs    - List all functions
  .types <var> - Show type of variable

Special Features:
  - Multi-line input (automatic continuation)
  - Tab completion for keywords and variables
  - Command history (up/down arrows)
  - Ctrl+C to interrupt current input

Examples:
  corpse x = 5;
  harvest x;
  infect Greet(soul name) { harvest "Hello " + name; }
  raise Greet("mortal");
        """)
    
    def _show_variables(self) -> None:
        """Show all variables in environment."""
        variables = self.environment.current_scope_names()
        if not variables:
            safe_print("No variables defined.")
            return
        
        safe_print("Variables:")
        for var_name in sorted(variables):
            try:
                value, var_type = self.environment.get(var_name)
                safe_print(f"  {var_name}: {var_type} = {repr(value)}")
            except:
                safe_print(f"  {var_name}: <error>")
    
    def _show_functions(self) -> None:
        """Show all functions in environment."""
        variables = self.environment.current_scope_names()
        functions = []
        
        for var_name in variables:
            try:
                value, var_type = self.environment.get(var_name)
                if var_type == "function":
                    functions.append(var_name)
            except:
                pass
        
        if not functions:
            safe_print("No functions defined.")
            return
        
        safe_print("Functions:")
        for func_name in sorted(functions):
            safe_print(f"  {func_name}()")
    
    def _show_variable_type(self, var_name: str) -> None:
        """Show type of specific variable."""
        try:
            value, var_type = self.environment.get(var_name)
            safe_print(f"{var_name}: {var_type} = {repr(value)}")
        except Exception as e:
            safe_print(f"Variable '{var_name}' not found.")
    
    def _execute_code(self, code: str) -> None:
        """Execute REAPER code."""
        try:
            # Tokenize
            tokens = tokenize(code, "<repl>")
            
            # Parse
            program = parse(tokens)
            
            # Execute
            self.interpreter.interpret(program)
            
        except ReaperSyntaxError as e:
            safe_print(_format_error_message("Syntax Error", e, code.split('\n')), file=sys.stderr)
        except ReaperRuntimeError as e:
            safe_print(_format_error_message("Runtime Error", e, code.split('\n')), file=sys.stderr)
        except ReaperTypeError as e:
            safe_print(_format_error_message("Type Error", e, code.split('\n')), file=sys.stderr)
        except ReaperRecursionError as e:
            safe_print(_format_error_message("Recursion Error", e, code.split('\n')), file=sys.stderr)
        except ReaperMemoryError as e:
            safe_print(_format_error_message("Memory Error", e, code.split('\n')), file=sys.stderr)
        except ReaperIndexError as e:
            safe_print(_format_error_message("Index Error", e, code.split('\n')), file=sys.stderr)
        except ReaperKeyError as e:
            safe_print(_format_error_message("Key Error", e, code.split('\n')), file=sys.stderr)
        except ReaperZeroDivisionError as e:
            safe_print(_format_error_message("Division by Zero", e, code.split('\n')), file=sys.stderr)
        except Exception as e:
            safe_print(f"Unexpected Error: {e}", file=sys.stderr)
    
    def run(self) -> None:
        """Run the REPL."""
        safe_print("""
REAPER Language Interpreter
The Undead Programming Language

Type .help for commands, .exit to quit.
        """)
        
        while True:
            try:
                # Get input
                line = input(self._get_prompt())
                
                # Handle special commands
                if line.strip().startswith('.'):
                    if self._handle_special_command(line):
                        continue
                
                # Add to pending input
                self.pending_input += line + "\n"
                
                # Check if we need more input
                if self._is_multiline_input(line):
                    continue
                
                # Execute the complete input
                if self.pending_input.strip():
                    self._execute_code(self.pending_input)
                
                # Reset for next input
                self.pending_input = ""
                self.brace_depth = 0
                self.paren_depth = 0
                self.bracket_depth = 0
                
            except EOFError:
                safe_print("\nThe reaper has finished harvesting. Farewell!")
                break
            except KeyboardInterrupt:
                # Already handled by signal handler
                pass


def compile_to_bytecode_file(source_file: str) -> int:
    """
    Compile a Reaper source file to bytecode file (.reaper.bc).
    
    Args:
        source_file: Path to .reaper source file
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        from bytecode import compile_to_bytecode
        
        # Read source file
        with open(source_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Tokenize
        tokens = tokenize(source, source_file)
        
        # Parse
        program = parse(tokens)
        
        # Compile to bytecode
        bytecode_program = compile_to_bytecode(program)
        
        # Write bytecode file
        bytecode_file = source_file + '.bc'
        with open(bytecode_file, 'wb') as f:
            f.write(bytecode_program.to_bytes())
        
        safe_print(f"✅ Compiled to bytecode: {bytecode_file}")
        return 0
        
    except FileNotFoundError:
        safe_print(f"Error: File '{source_file}' not found.")
        return 1
    except PermissionError:
        safe_print(f"Error: Permission denied reading '{source_file}'.")
        return 1
    except ReaperSyntaxError as e:
        safe_print(f"Syntax Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        safe_print(f"Compilation Error: {e}")
        import traceback
        traceback.print_exc()
        return 2


def run_file_with_bytecode(source: str, filename: str, args: List[str]) -> int:
    """
    Compile and execute Reaper source code using bytecode VM.
    
    Args:
        source: Source code content
        filename: Source file path
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        from bytecode import compile_to_bytecode, create_vm
        from bytecode.instructions import BytecodeProgram
        
        # Tokenize
        tokens = tokenize(source, filename)
        
        # Parse
        program = parse(tokens)
        
        # Compile to bytecode
        bytecode_program = compile_to_bytecode(program)
        
        # Create VM
        vm = create_vm()
        
        # Set command-line arguments as ritual_args (matching interpreter behavior)
        vm.globals['ritual_args'] = args
        vm.globals['__ritual_args__'] = args  # Also set for compatibility
        
        # Load and execute
        vm.load_program(bytecode_program)
        vm.execute()
        
        return 0
        
    except ReaperSyntaxError as e:
        safe_print(f"Syntax Error: {e}", file=sys.stderr)
        return 1
    except ReaperRuntimeError as e:
        safe_print(f"Runtime Error: {e}", file=sys.stderr)
        return 2
    except ReaperTypeError as e:
        safe_print(f"Type Error: {e}", file=sys.stderr)
        return 2
    except ReaperRecursionError as e:
        safe_print(f"Recursion Error: {e}", file=sys.stderr)
        return 2
    except ReaperMemoryError as e:
        safe_print(f"Memory Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        safe_print(f"Bytecode Execution Error: {e}")
        import traceback
        traceback.print_exc()
        return 2


def run_bytecode_file(bytecode_file: str, args: List[str]) -> int:
    """
    Execute a pre-compiled bytecode file.
    
    Args:
        bytecode_file: Path to .reaper.bc file
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        from bytecode import create_vm
        from bytecode.instructions import BytecodeProgram
        
        # Load bytecode file using native serialization
        with open(bytecode_file, 'rb') as f:
            bytecode_data = f.read()
        
        # Deserialize from bytes
        bytecode_program = BytecodeProgram.from_bytes(bytecode_data)
        
        if not isinstance(bytecode_program, BytecodeProgram):
            raise ReaperRuntimeError(f"Invalid bytecode file: {bytecode_file}")
        
        # Create VM
        vm = create_vm()
        
        # Set command-line arguments as ritual_args (matching interpreter behavior)
        # The VM's globals will be used for builtins, ritual_args should be accessible
        vm.globals['ritual_args'] = args
        vm.globals['__ritual_args__'] = args  # Also set this for compatibility
        
        # Load and execute
        vm.load_program(bytecode_program)
        vm.execute()
        
        return 0
        
    except FileNotFoundError:
        safe_print(f"Error: Bytecode file '{bytecode_file}' not found.")
        return 1
    except Exception as e:
        safe_print(f"Bytecode Execution Error: {e}")
        import traceback
        traceback.print_exc()
        return 2


def run_file(filename: str, args: List[str], use_bytecode: bool = False) -> int:
    """
    Run a REAPER file.
    
    Args:
        filename: Path to .reaper file (or .reaper.bc bytecode file)
        args: Command-line arguments to pass to script
        use_bytecode: If True, use bytecode VM; if False, use interpreter
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Check if bytecode file exists (look for .reaper.bc)
        bytecode_file = filename + '.bc' if filename.endswith('.reaper') else (filename if filename.endswith('.bc') else filename + '.bc')
        
        # If using bytecode mode and bytecode file exists, use it
        if use_bytecode and os.path.exists(bytecode_file):
            return run_bytecode_file(bytecode_file, args)
        
        # Read source file
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # If bytecode mode requested, compile and execute with VM
        if use_bytecode:
            return run_file_with_bytecode(source, filename, args)
        
        # Otherwise use interpreter (default)
        # Create interpreter
        interpreter = Interpreter()
        
        # Set module loader's current file for relative imports
        from pathlib import Path
        file_path = Path(filename).resolve()
        interpreter.module_loader.current_file = file_path
        interpreter.module_loader.base_path = file_path.parent
        interpreter.module_loader._update_search_paths()
        
        # Set command-line arguments
        interpreter.global_environment.set_ritual_args(args)
        
        # Tokenize
        tokens = tokenize(source, filename)
        
        # Parse
        program = parse(tokens)
        
        # Execute
        interpreter.interpret(program)
        
        return 0
        
    except FileNotFoundError:
        safe_print(f"Error: File '{filename}' not found.")
        return 1
    except PermissionError:
        safe_print(f"Error: Permission denied reading '{filename}'.")
        return 1
    except UnicodeDecodeError:
        safe_print(f"Error: File '{filename}' contains invalid UTF-8.")
        return 1
    except ReaperSyntaxError as e:
        # Load source lines for context
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except:
            source_lines = None
        safe_print(_format_error_message("Syntax Error", e, source_lines), file=sys.stderr)
        return 1
    except ReaperRuntimeError as e:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except:
            source_lines = None
        safe_print(_format_error_message("Runtime Error", e, source_lines), file=sys.stderr)
        return 2
    except ReaperTypeError as e:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except:
            source_lines = None
        safe_print(_format_error_message("Type Error", e, source_lines), file=sys.stderr)
        return 2
    except ReaperRecursionError as e:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except:
            source_lines = None
        safe_print(_format_error_message("Recursion Error", e, source_lines), file=sys.stderr)
        return 2
    except ReaperMemoryError as e:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except:
            source_lines = None
        safe_print(_format_error_message("Memory Error", e, source_lines), file=sys.stderr)
        return 2
    except ReaperIndexError as e:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except:
            source_lines = None
        safe_print(_format_error_message("Index Error", e, source_lines), file=sys.stderr)
        return 2
    except ReaperKeyError as e:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except:
            source_lines = None
        safe_print(_format_error_message("Key Error", e, source_lines), file=sys.stderr)
        return 2
    except ReaperZeroDivisionError as e:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except:
            source_lines = None
        safe_print(_format_error_message("Division by Zero", e, source_lines), file=sys.stderr)
        return 2
    except Exception as e:
        safe_print(f"Unexpected Error: {e}")
        return 2


def main() -> int:
    """Main entry point for REAPER interpreter."""
    parser = argparse.ArgumentParser(
        description="REAPER Language Interpreter - The Undead Programming Language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reaper.py                    # Start interactive REPL
  python reaper.py script.reaper      # Run REAPER file
  python reaper.py script.reaper arg1 arg2  # Run with arguments
  python reaper.py package init       # Initialize package
  python reaper.py package install github:user/repo  # Install package

The REAPER language features:
  - Zombie/death-themed syntax
  - Static typing with corpse, soul, crypt, grimoire, tomb, wraith, void
  - Functions, classes, loops, conditionals
  - String interpolation and built-in methods
  - Comprehensive error handling and resource limits
        """
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Package manager subcommand
    pkg_parser = subparsers.add_parser('package', help='Package manager commands')
    pkg_subparsers = pkg_parser.add_subparsers(dest='pkg_command', help='Package commands')
    
    # Package init
    init_parser = pkg_subparsers.add_parser('init', help='Initialize a new REAPER project')
    init_parser.add_argument('name', nargs='?', help='Package name')
    init_parser.add_argument('version', nargs='?', default='0.1.0', help='Package version')
    init_parser.add_argument('author', nargs='?', default='', help='Package author')
    init_parser.add_argument('description', nargs='*', help='Package description')
    
    # Package install
    install_parser = pkg_subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('package_spec', help='Package specification (e.g., github:user/repo)')
    install_parser.add_argument('--dev', action='store_true', help='Install as dev dependency')
    
    # Package list
    pkg_subparsers.add_parser('list', help='List installed packages')
    
    # Package uninstall
    uninstall_parser = pkg_subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package_name', help='Package name to uninstall')
    
    # Package update
    pkg_subparsers.add_parser('update', help='Update all packages')
    
    # Regular file execution arguments (when not using package command)
    parser.add_argument(
        'filename',
        nargs='?',
        help='REAPER source file to execute'
    )
    
    parser.add_argument(
        'args',
        nargs='*',
        help='Arguments to pass to the REAPER script'
    )
    
    # Import version information
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from version import get_version_string
        version_str = get_version_string()
    except ImportError:
        version_str = 'REAPER Language Interpreter 0.2.0'
    
    parser.add_argument(
        '--version',
        action='version',
        version=version_str
    )
    
    parser.add_argument(
        '--bytecode', '--vm',
        dest='use_bytecode',
        action='store_true',
        help='Execute using bytecode VM instead of interpreter (faster, but source files remain editable)'
    )
    
    parser.add_argument(
        '--compile-bc',
        dest='compile_bytecode',
        action='store_true',
        help='Compile source file to bytecode (.reaper.bc file) without executing'
    )
    
    parser.add_argument(
        '--necronomicon',
        dest='necronomicon',
        action='store_true',
        help='Launch Necronomicon learning system'
    )
    
    parser.add_argument(
        '--thanatos',
        dest='thanatos',
        action='store_true',
        help='Launch Thanatos advanced security expert (requires course completion)'
    )
    
    args = parser.parse_args()
    
    # Handle package manager commands
    if args.command == 'package':
        try:
            from .package_manager import ReaperPackageManager
            pm = ReaperPackageManager()
            
            if args.pkg_command == 'init':
                name = args.name or Path.cwd().name
                version = args.version or "0.1.0"
                author = args.author or ""
                description = " ".join(args.description) if args.description else ""
                pm.init_project(name, version, author, description)
                return 0
            
            elif args.pkg_command == 'install':
                if not args.package_spec:
                    safe_print("Error: Package specification required")
                    return 1
                pm.install_package(args.package_spec, dev=args.dev)
                return 0
            
            elif args.pkg_command == 'list':
                packages = pm.list_packages()
                if not packages:
                    safe_print("No packages installed")
                else:
                    safe_print(f"Installed packages ({len(packages)}):")
                    for pkg in packages:
                        safe_print(f"  {pkg['name']} v{pkg['version']}")
                return 0
            
            elif args.pkg_command == 'uninstall':
                if not args.package_name:
                    safe_print("Error: Package name required")
                    return 1
                pm.uninstall_package(args.package_name)
                return 0
            
            elif args.pkg_command == 'update':
                pm.update_packages()
                return 0
            
            else:
                pkg_parser.print_help()
                return 0
                
        except Exception as e:
            safe_print(f"Package manager error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    # Check for Thanatos mode (advanced AI)
    if args.thanatos:
        try:
            from stdlib.necronomicon.thanatos_ui import main as thanatos_main
            thanatos_main()
            return 0
        except ImportError as e:
            safe_print(f"Error: Could not launch Thanatos: {e}")
            safe_print("Make sure all dependencies are installed: pip install rich")
            return 1
        except Exception as e:
            safe_print(f"Thanatos Error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    # Check for Necronomicon mode
    if args.necronomicon:
        try:
            from stdlib.necronomicon.ui import main as necronomicon_main
            necronomicon_main()
            return 0
        except ImportError as e:
            safe_print(f"Error: Could not launch Necronomicon: {e}")
            safe_print("Make sure all dependencies are installed: pip install rich")
            return 1
        except Exception as e:
            safe_print(f"Necronomicon Error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    # If package command was used, don't process filename
    if args.command == 'package':
        pass  # Already handled above
    elif args.filename:
        # File execution mode
        if not args.filename.endswith('.reaper'):
            safe_print("Warning: File doesn't have .reaper extension")
        
        # If compile-only mode, just compile to bytecode
        if args.compile_bytecode:
            return compile_to_bytecode_file(args.filename)
        
        return run_file(args.filename, args.args, use_bytecode=args.use_bytecode)
    elif args.command is None:
        # REPL mode
        try:
            repl = ReaperREPL()
            repl.run()
            return 0
        except KeyboardInterrupt:
            safe_print("\nThe reaper has finished harvesting. Farewell!")
            return 0
        except Exception as e:
            safe_print(f"REPL Error: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
