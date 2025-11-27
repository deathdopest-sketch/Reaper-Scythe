# REAPER Language Interpreter

> **The Undead Programming Language** ☠️

REAPER is a zombie/death-themed programming language that combines the power of modern programming constructs with a unique thematic identity. Every aspect of the language is designed to maintain the undead aesthetic while providing practical programming capabilities.

## Features

### 🧟 Core Language Features
- **Static Typing**: 7 fundamental types (corpse, soul, crypt, grimoire, tomb, wraith, void)
- **Object-Oriented**: Classes with constructors, methods, and properties
- **Functional**: Functions with parameters, return values, and closures
- **Control Flow**: Loops, conditionals, and exception handling
- **Collections**: Arrays and dictionaries with built-in methods
- **String Interpolation**: Dynamic string construction with expressions

### 🎯 Advanced Features
- **Bytecode VM**: High-performance bytecode execution (10x faster than interpreter)
- **Bytecode Compilation**: Compile source to bytecode for faster execution
- **Resource Management**: Memory limits, recursion limits, execution timeouts
- **Error Handling**: Comprehensive error types with helpful messages
- **Built-in Functions**: 11 utility functions for common operations
- **Command-Line Interface**: File execution and interactive REPL
- **Tab Completion**: Smart completion for keywords and variables
- **Multi-line Input**: Automatic continuation for complex expressions
- **Necronomicon Learning System**: Interactive courses with AI tutors
- **AI Assistants**: Hack Benjamin (beginner) and Thanatos (advanced)

## Installation

### From Source
```bash
git clone https://github.com/yourusername/reaper-lang.git
cd reaper-lang
python -m pip install -e .
```

### Development Installation
```bash
git clone https://github.com/yourusername/reaper-lang.git
cd reaper-lang
python -m pip install -e .[dev]
```

## Quick Start

### Hello World
```reaper
infect Greet(soul name) {
    harvest "Hello from the graveyard, " + name + "!";
}

raise Greet("mortal");
```

### Variables and Types
```reaper
corpse zombies = 10;
soul message = "The dead walk among us";
wraith is_night = RISEN;
crypt horde = [1, 2, 3, 5, 8];
grimoire stats = {"health": 100, "hunger": 50};
```

### Classes and Objects
```reaper
tomb Zombie {
    corpse health = 100;
    soul name = "Unknown";
    
    infect Zombie(soul zombie_name) {
        this.name = zombie_name;
    }
    
    infect Attack() -> corpse {
        reap 10;
    }
}

tomb zombie = spawn Zombie("Walker");
harvest zombie.name;
```

## Usage

### File Execution
```bash
python reaper_main.py script.reaper
python reaper_main.py script.reaper arg1 arg2
```

### Interactive REPL
```bash
python reaper_main.py
```

**REPL Commands:**
- `.exit` - Exit the REPL
- `.clear` - Clear the environment
- `.help` - Show help
- `.vars` - List all variables
- `.funcs` - List all functions
- `.types <var>` - Show variable type

### Bytecode Mode (Faster Execution)
```bash
# Compile source to bytecode
python reaper_main.py --compile-bc script.reaper

# Execute bytecode (10x faster)
python reaper_main.py --bytecode script.reaper.bc
```

### Necronomicon Learning System
```bash
python reaper_main.py --necronomicon
```

Access interactive courses, tutorials, challenges, and AI tutors (Hack Benjamin and Thanatos).

### Thanatos Advanced AI
```bash
python reaper_main.py --thanatos
```

Launch the advanced security expert AI (requires course completion to unlock).

### Test Runner
```bash
python test_runner.py
```

## Language Reference

### Types
- **corpse**: Integers (whole numbers)
- **soul**: Strings (text data)
- **crypt**: Arrays (ordered collections)
- **grimoire**: Dictionaries (key-value pairs)
- **tomb**: Class instances (objects)
- **wraith**: Booleans (true/false)
- **void**: Null values

### Keywords
- **Type Keywords**: `corpse`, `soul`, `crypt`, `grimoire`, `tomb`, `wraith`, `void`, `eternal`
- **Control Keywords**: `infect`, `raise`, `harvest`, `reap`, `shamble`, `decay`, `soulless`, `spawn`
- **Conditionals**: `if`, `otherwise`, `flee`, `persist`
- **Logical**: `corrupt` (AND), `infest` (OR), `banish` (NOT)
- **Constants**: `DEAD` (0), `RISEN` (1), `void` (null)

### Built-in Functions
- `harvest(...)` - Print variadic arguments
- `rest(ms)` - Sleep for milliseconds
- `raise_corpse(soul)` - Convert string to integer
- `steal_soul(corpse)` - Convert integer to string
- `summon()` - Read line from stdin
- `final_rest(code)` - Exit program with code
- `curse(condition, message)` - Assert condition
- `absolute(corpse)` - Absolute value
- `lesser(a, b)` - Minimum of two values
- `greater(a, b)` - Maximum of two values

### Array Methods
- `.entomb(item)` - Append item
- `.exhume(index)` - Remove item at index
- `.curse()` - Get length
- `.resurrect()` - Reverse in place
- `.haunt(item)` - Check if contains item

### String Methods
- `.curse()` - Get length
- `.slice(start, end)` - Get substring
- `.whisper()` - Convert to lowercase
- `.scream()` - Convert to uppercase
- `.haunt(substring)` - Check if contains substring
- `.split(delimiter)` - Split into array

### Dictionary Methods
- `.curse()` - Get key count
- `.summon(key)` - Get value with default
- `.banish(key)` - Remove key
- `.inscribe()` - Get all keys
- `.possess()` - Get all values

## Examples

### Factorial Function
```reaper
infect CollectSouls(corpse n) -> corpse {
    if (n <= DEAD) {
        reap RISEN;
    }
    reap n * CollectSouls(n - RISEN);
}

corpse total = CollectSouls(5);
harvest total;  # Output: 120
```

### String Interpolation
```reaper
soul name = "zombie";
corpse count = 5;
harvest "There are #{count} #{name}s shambling around";
# Output: There are 5 zombies shambling around
```

### Array Operations
```reaper
crypt horde = [1, 2, 3, 5, 8];
horde.entomb(13);
harvest horde.curse();  # Output: 6
harvest horde.haunt(3);  # Output: RISEN
```

### Class with Methods
```reaper
tomb Zombie {
    corpse health = 100;
    
    infect Attack() {
        this.health = this.health - 10;
    }
    
    infect IsAlive() -> wraith {
        reap this.health > DEAD;
    }
}

tomb zombie = spawn Zombie();
zombie.Attack();
harvest zombie.IsAlive();  # Output: RISEN
```

## Project Structure

```
interpreter/
├── reaper.py              # CLI entry point with REPL
├── lexer.py               # Tokenizer
├── tokens.py              # Token definitions
├── parser.py              # AST parser
├── ast_nodes.py           # AST node classes
├── interpreter.py         # Execution engine
├── environment.py         # Scope management
├── reaper_error.py        # Error handling
├── test_runner.py         # Test validation
├── test_examples/         # Test files
├── examples/              # Tutorial programs
├── grammar.md             # Formal grammar
├── language_spec.md       # Language specification
├── setup.py               # Package configuration
├── LICENSE                # MIT License
└── README.md              # This file
```

## Testing

Run the comprehensive test suite:

```bash
python test_runner.py
```

The test suite includes:
- **Core Features**: Variables, functions, classes, loops, conditionals
- **Advanced Features**: Closures, string interpolation, error handling
- **Edge Cases**: Error conditions, resource limits, type checking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the zombie/death theme in programming
- Built with Python 3.8+ compatibility
- Designed for educational and entertainment purposes

## Roadmap

### Version 0.2.0 (Current)
- ✅ Bytecode VM and compiler
- ✅ Necronomicon learning system
- ✅ AI assistants (Hack Benjamin & Thanatos)
- ✅ Bitwise operators
- ✅ Enhanced type system

### Version 1.0 (Planned)
- Floating-point type (`phantom`)
- Import/module system
- Exception handling (`risk`/`catch`)
- File I/O operations
- List comprehensions
- Switch/match statements

### Version 2.0 (Future)
- JIT compilation
- Standard library expansion
- Package manager
- IDE plugins
- Syntax highlighting

---

**The dead have spoken. The REAPER language rises.** ☠️
