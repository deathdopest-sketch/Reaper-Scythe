# 🎯 REAPER LANGUAGE - Comprehensive Overview
## The Undead Programming Language for Security Operations

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Language Philosophy](#language-philosophy)
3. [Type System](#type-system)
4. [Syntax and Operators](#syntax-and-operators)
5. [Control Flow](#control-flow)
6. [Functions](#functions)
7. [Object-Oriented Programming](#object-oriented-programming)
8. [Collections and Built-in Methods](#collections-and-built-in-methods)
9. [Built-in Functions](#built-in-functions)
10. [Security Libraries](#security-libraries)
11. [Error Handling](#error-handling)
12. [Resource Management](#resource-management)
13. [Examples and Tutorials](#examples-and-tutorials)
14. [Getting Started](#getting-started)

---

## 🎭 Introduction

**REAPER** (The Undead Programming Language) is a unique programming language that combines modern programming constructs with a distinctive zombie/death-themed syntax. Originally designed as a Python-based interpreter, REAPER is being transformed into a standalone compiled executable language focused on hacking, anonymity, and security operations.

### Key Characteristics

- **Thematic Consistency**: Every keyword, operator, and function follows the zombie/death theme
- **Explicit Typing**: Strong static type system with 7 fundamental types
- **Safety First**: Comprehensive error handling, bounds checking, and resource limits
- **Security-Focused**: Built-in security libraries for network operations, cryptography, and anonymity
- **Performance**: Bytecode VM for 10x performance improvement over interpreter
- **Learning System**: Integrated Necronomicon learning system with AI tutors

---

## 🎯 Language Philosophy

### Core Tenets

1. **Thematic Consistency**: All language elements maintain the undead aesthetic
2. **Explicit Typing**: No implicit type conversions - all conversions must be explicit
3. **Safety First**: Comprehensive error handling, bounds checking, and resource limits
4. **Clarity Over Cleverness**: Code should be readable and maintainable
5. **Performance Awareness**: Resource limits prevent runaway programs
6. **Security by Design**: Built-in security features with ethical use guidelines

### Design Principles

- **No Implicit Conversions**: Prevents subtle bugs and makes intent clear
- **Resource Limits**: Memory, recursion, and execution timeouts prevent abuse
- **Type Safety**: Static typing prevents type-related errors
- **Error Messages**: Helpful, contextual error messages guide debugging
- **Extensibility**: Security libraries can be extended without modifying core

---

## 🔢 Type System

REAPER has **8 fundamental types**:

### 1. `corpse` (Integer)
- **Purpose**: Whole numbers only
- **Range**: Limited by Python's int (effectively unlimited)
- **Operations**: All arithmetic, comparison, logical (as 0/1)
- **Examples**: 
  ```reaper
  corpse zombies = 10;
  corpse health = -5;
  corpse count = 0;
  ```

### 1.5. `phantom` (Floating-Point) ⭐ NEW in v0.3.0
- **Purpose**: Decimal numbers for precise calculations
- **Range**: Limited by Python's float (IEEE 754 double precision)
- **Operations**: All arithmetic, comparison
- **Examples**: 
  ```reaper
  phantom pi = 3.14159;
  phantom rate = 0.05;
  phantom temperature = -273.15;
  ```

### 2. `soul` (String)
- **Purpose**: Text data with escape sequence support
- **Max Length**: 1MB per string
- **Operations**: Concatenation (+), indexing, slicing, methods
- **Examples**:
  ```reaper
  soul message = "Braaaaains";
  soul name = 'zombie';
  soul greeting = "Hello " + name;
  ```

### 3. `crypt` (Array/List)
- **Purpose**: Ordered collections of values
- **Max Size**: 10,000 elements
- **Operations**: Indexing, slicing, built-in methods
- **Examples**:
  ```reaper
  crypt horde = [1, 2, 3];
  crypt empty = [];
  crypt mixed = [1, "zombie", RISEN];
  ```

### 4. `grimoire` (Dictionary/Map)
- **Purpose**: Key-value pairs for data organization
- **Max Size**: 10,000 key-value pairs
- **Access**: `dict{"key"}` syntax only (not `.key`)
- **Examples**:
  ```reaper
  grimoire stats = {"health": 100, "hunger": 50};
  grimoire zombie = {"name": "Walker", "speed": 2};
  ```

### 5. `wraith` (Boolean)
- **Purpose**: True/false values
- **Values**: `DEAD` (false/0), `RISEN` (true/1)
- **Operations**: Logical operators, comparison
- **Examples**:
  ```reaper
  wraith alive = RISEN;
  wraith dead = DEAD;
  wraith condition = (10 > 5);
  ```

### 6. `tomb` (Class Instance)
- **Purpose**: Object-oriented programming
- **Features**: Properties, methods, constructors
- **Examples**:
  ```reaper
  tomb zombie = spawn Zombie();
  tomb player = spawn Player("Alice");
  ```

### 7. `void` (Null/None)
- **Purpose**: Represents absence of value
- **Default**: Uninitialized variables default to `void`
- **Examples**:
  ```reaper
  soul name;  # defaults to void
  corpse count;  # defaults to void
  ```

### Type Modifiers

- **`eternal`**: Makes a variable constant (cannot be reassigned)
  ```reaper
  eternal corpse MAX_ZOMBIES = 1000;
  eternal soul LANGUAGE_NAME = "REAPER";
  ```

---

## 🔤 Syntax and Operators

### Operator Precedence (Highest to Lowest)

| Precedence | Operator | Associativity | Description |
|------------|----------|---------------|-------------|
| 1 (Highest) | `.` `[]` `()` | Left | Property access, indexing, function calls |
| 2 | `-` `banish` | Right | Unary negation, logical NOT |
| 3 | `*` `/` `%` | Left | Multiplication, division, modulo |
| 4 | `+` `-` | Left | Addition, subtraction, string concatenation |
| 5 | `==` `!=` `<` `>` `<=` `>=` | Left | Comparison operators |
| 6 | `corrupt` | Left | Logical AND |
| 7 | `infest` | Left | Logical OR |
| 8 (Lowest) | `=` `+=` `-=` `*=` `/=` `%=` | Right | Assignment operators |

### Arithmetic Operators

```reaper
corpse a = 10;
corpse b = 3;

harvest a + b;  # 13 (Addition)
harvest a - b;  # 7 (Subtraction)
harvest a * b;  # 30 (Multiplication)
harvest a / b;  # 3 (Integer division)
harvest a % b;  # 1 (Modulo)
```

### Comparison Operators

```reaper
corpse x = 10;
corpse y = 5;

harvest x == y;  # DEAD (false)
harvest x != y;  # RISEN (true)
harvest x > y;   # RISEN (true)
harvest x < y;   # DEAD (false)
harvest x >= y;  # RISEN (true)
harvest x <= y;  # DEAD (false)
```

### Logical Operators

```reaper
wraith condition1 = RISEN;
wraith condition2 = DEAD;

harvest condition1 corrupt condition2;  # DEAD (AND - both must be RISEN)
harvest condition1 infest condition2;   # RISEN (OR - either is RISEN)
harvest banish condition1;                # DEAD (NOT - inverts)
```

### Bitwise Operators (Advanced)

```reaper
corpse a = 5;  # 0101 in binary
corpse b = 3;  # 0011 in binary

harvest a wither b;   # Bitwise AND
harvest a spread b;   # Bitwise OR
harvest a mutate b;   # Bitwise XOR
harvest invert a;     # Bitwise NOT
harvest a rot 2;      # Bitwise rotation
```

### Assignment Operators

```reaper
corpse x = 10;
x += 5;   # x = 15
x -= 3;   # x = 12
x *= 2;   # x = 24
x /= 4;   # x = 6
x %= 5;   # x = 1
```

### String Concatenation

```reaper
soul first = "Hello";
soul second = "World";
soul combined = first + " " + second;  # "Hello World"
```

### String Interpolation

```reaper
soul name = "zombie";
corpse count = 5;
harvest "There are #{count} #{name}s shambling around";
# Output: There are 5 zombies shambling around
```

---

## 🔀 Control Flow

### Conditionals: `if` / `otherwise`

```reaper
corpse zombie_count = 5;

if (zombie_count > 10) {
    harvest "Zombie apocalypse!";
} otherwise if (zombie_count > 5) {
    harvest "Zombie outbreak!";
} otherwise {
    harvest "Just a few zombies...";
}
```

### For Loop: `shamble`

```reaper
# Count from 1 to 10
shamble i from RISEN to 10 {
    harvest "Zombie #" + i;
}

# Count backwards
shamble i from 10 to RISEN {
    harvest i;
}
```

### Foreach Loop: `decay`

```reaper
crypt horde = [1, 2, 3, 5, 8];
decay zombie in horde {
    harvest "Zombie strength: " + zombie;
}
```

### Infinite Loop: `soulless`

```reaper
soulless {
    # Loop forever until break
    harvest "The dead never rest...";
    if (some_condition) {
        flee;  # Break out of loop
    }
}
```

### Loop Control

- **`flee`**: Break out of loop (like `break`)
  ```reaper
  shamble i from RISEN to 100 {
      if (i > 50) {
          flee;  # Exit loop
      }
      harvest i;
  }
  ```

- **`persist`**: Continue to next iteration (like `continue`)
  ```reaper
  shamble i from RISEN to 10 {
      if (i % 2 == DEAD) {
          persist;  # Skip even numbers
      }
      harvest i;  # Only prints odd numbers
  }
  ```

---

## 🧬 Functions

### Function Definition: `infect`

```reaper
# Basic function
infect Greet(soul name) {
    harvest "Greetings from the graveyard, " + name + "!";
}

# Function with return value
infect Add(corpse a, corpse b) -> corpse {
    reap a + b;
}

# Function with default parameters
infect CreateZombie(soul name, corpse health = 100) {
    harvest "Created " + name + " with " + health + " health";
}

# Calling functions
raise Greet("mortal");
corpse result = raise Add(5, 3);
raise CreateZombie("Walker");  # Uses default health = 100
raise CreateZombie("Runner", 150);  # Override default
```

### Recursive Functions

```reaper
infect Factorial(corpse n) -> corpse {
    if (n <= DEAD) {
        reap RISEN;
    }
    reap n * raise Factorial(n - RISEN);
}

harvest raise Factorial(5);  # Output: 120
```

### Closures

```reaper
infect CreateCounter() -> infect {
    corpse count = DEAD;
    
    infect Counter() -> corpse {
        count = count + RISEN;
        reap count;
    }
    
    reap Counter;
}

infect counter = raise CreateCounter();
harvest raise counter();  # 1
harvest raise counter();  # 2
harvest raise counter();  # 3
```

### Higher-Order Functions

```reaper
infect CreateMultiplier(corpse factor) -> infect {
    infect Multiply(corpse value) -> corpse {
        reap value * factor;
    }
    reap Multiply;
}

infect Double = raise CreateMultiplier(2);
harvest raise Double(5);  # Output: 10
```

---

## 🏛️ Object-Oriented Programming

### Class Definition: `tomb`

```reaper
tomb Zombie {
    # Properties
    corpse health = 100;
    soul name = "Unknown";
    wraith alive = RISEN;
    
    # Constructor
    infect Zombie(soul zombie_name, corpse initial_health = 100) {
        this.name = zombie_name;
        this.health = initial_health;
    }
    
    # Method
    infect Attack(corpse damage) {
        this.health = this.health - damage;
        if (this.health <= DEAD) {
            this.alive = DEAD;
        }
    }
    
    # Getter method
    infect IsAlive() -> wraith {
        reap this.alive;
    }
    
    # Method with return value
    infect GetInfo() -> soul {
        reap "Zombie: " + this.name + ", Health: " + this.health;
    }
}
```

### Class Instantiation: `spawn`

```reaper
tomb zombie1 = spawn Zombie("Walker");
tomb zombie2 = spawn Zombie("Runner", 150);

zombie1.Attack(25);
harvest zombie1.GetInfo();
harvest zombie1.IsAlive();
```

### Property Access

```reaper
# Access properties
harvest zombie1.name;      # "Walker"
harvest zombie1.health;    # 75 (after attack)

# Modify properties
zombie1.health = 200;
```

---

## 📚 Collections and Built-in Methods

### Arrays (`crypt`) - Methods

```reaper
crypt horde = [1, 2, 3];

# Add element to end
horde.entomb(4);              # [1, 2, 3, 4]

# Remove element at index
horde.exhume(0);              # [2, 3, 4]

# Get length
corpse size = horde.curse();  # 3

# Reverse array (in-place)
horde.resurrect();            # [4, 3, 2]

# Check if contains item
wraith has_three = horde.haunt(3);  # RISEN

# Get slice
crypt slice = horde[1:3];     # [3, 2]
```

### Strings (`soul`) - Methods

```reaper
soul text = "Zombie";

# Get length
corpse len = text.curse();         # 6

# Get substring
soul sub = text.slice(0, 3);        # "Zom"

# Convert case
soul lower = text.whisper();        # "zombie"
soul upper = text.scream();         # "ZOMBIE"

# Check if contains substring
wraith has_om = text.haunt("om");   # RISEN

# Split into array
soul phrase = "hello world";
crypt words = phrase.split(" ");    # ["hello", "world"]
```

### Dictionaries (`grimoire`) - Methods

```reaper
grimoire stats = {"health": 100, "hunger": 50};

# Get value (with default)
corpse health = stats.summon("health", 0);  # 100

# Remove key
stats.banish("hunger");              # {"health": 100}

# Get key count
corpse count = stats.curse();        # 1

# Get all keys
crypt keys = stats.inscribe();       # ["health"]

# Get all values
crypt values = stats.possess();      # [100]

# Access value
corpse val = stats{"health"};        # 100
```

---

## 🛠️ Built-in Functions

### I/O Functions

```reaper
# Print to stdout (variadic)
harvest "Hello", "World", 42;  # Prints: Hello World 42

# Read line from stdin
soul input = summon();  # Waits for user input

# Exit program
final_rest(0);  # Exit with code 0
```

### Type Conversion

```reaper
# String to integer
soul num_str = "42";
corpse num = raise_corpse(num_str);  # 42

# String to float
soul float_str = "3.14";
phantom pi = raise_phantom(float_str);  # 3.14

# Integer/float to string
corpse count = 100;
soul str_count = steal_soul(count);  # "100"
phantom rate = 0.05;
soul str_rate = steal_soul(rate);  # "0.05"
```

### Utility Functions

```reaper
# Sleep for milliseconds
rest(1000);  # Sleep for 1 second

# Assert condition
curse(x > 0, "x must be positive");

# Absolute value
corpse abs_val = absolute(-10);  # 10

# Minimum
corpse min_val = lesser(5, 10);  # 5

# Maximum
corpse max_val = greater(5, 10);  # 10
```

### System Variables

```reaper
# Command-line arguments
crypt args = ritual_args;
harvest "Program: " + args[0];
harvest "First arg: " + args[1];
```

---

## 🔒 Security Libraries

REAPER includes 8 security-focused libraries:

### 1. **phantom** - Network Operations
- DNS operations
- Packet crafting and analysis
- Network scanning
- Port detection

### 2. **crypt** - Cryptography
- Encryption/decryption
- Hashing algorithms
- Steganography
- Secure key management

### 3. **wraith** - System Operations
- Process management
- File system operations
- Registry operations (Windows)
- System information gathering

### 4. **specter** - Web Operations
- HTTP/HTTPS requests
- Web scraping
- Cookie management
- Session handling

### 5. **shadow** - Anonymity Features
- Tor integration
- VPN management
- Network obfuscation
- Traffic anonymization

### 6. **void** - OSINT Scrubbing
- Digital footprint removal
- Data broker scrubbing
- Email/phone removal
- Privacy protection

### 7. **zombitious** - Automation
- Task automation
- Script scheduling
- Event handling
- Background processing

### 8. **shinigami** - Advanced Security
- Advanced penetration testing
- Exploit development
- Security auditing
- Vulnerability assessment

**Note**: All security libraries include ethical use guidelines and warnings. Use responsibly and legally.

---

## ⚠️ Error Handling

### Error Types

REAPER provides comprehensive error handling:

1. **ReaperSyntaxError**: Invalid syntax
   - Missing semicolons
   - Unmatched braces/parentheses
   - Invalid token sequences

2. **ReaperRuntimeError**: Runtime errors
   - Undefined variables
   - Type mismatches
   - Invalid operations

3. **ReaperTypeError**: Type errors
   - Incompatible type operations
   - Missing type conversions

4. **ReaperRecursionError**: Recursion limit exceeded (max 1000)

5. **ReaperMemoryError**: Memory limits exceeded
   - String too long (>1MB)
   - Array too large (>10,000)
   - Dictionary too large (>10,000)

6. **ReaperIndexError**: Index out of bounds

7. **ReaperKeyError**: Dictionary key not found

8. **ReaperZeroDivisionError**: Division by zero

### Error Messages

All errors include:
- Line and column number
- Clear error description
- Suggested fixes
- Context information

---

## 🛡️ Resource Management

### Resource Limits

REAPER enforces resource limits to prevent abuse:

- **String Length**: 1MB per string
- **Array Size**: 10,000 elements
- **Dictionary Size**: 10,000 key-value pairs
- **Recursion Depth**: 1,000 calls
- **Execution Timeout**: 30 seconds
- **Stack Size**: Bounded by recursion limit

### Security Features

- **Input Validation**: All user input is validated and sanitized
- **Bounds Checking**: All array/string operations are bounds-checked
- **Type Checking**: Prevents type-related security vulnerabilities
- **Memory Limits**: Prevents DoS attacks
- **Timeout Protection**: Prevents infinite loops

---

## 📖 Examples and Tutorials

### Hello World

```reaper
infect Greet(soul name) {
    harvest "Greetings from the graveyard, " + name + "!";
}

raise Greet("mortal");
```

### Factorial

```reaper
infect Factorial(corpse n) -> corpse {
    if (n <= DEAD) {
        reap RISEN;
    }
    reap n * raise Factorial(n - RISEN);
}

harvest raise Factorial(5);  # 120
```

### Class Example

```reaper
tomb Zombie {
    corpse health = 100;
    soul name = "Unknown";
    
    infect Zombie(soul zombie_name) {
        this.name = zombie_name;
    }
    
    infect Attack() {
        this.health = this.health - 10;
    }
    
    infect IsAlive() -> wraith {
        reap this.health > DEAD;
    }
}

tomb zombie = spawn Zombie("Walker");
zombie.Attack();
harvest zombie.IsAlive();  # RISEN
```

### Array Operations

```reaper
crypt horde = [1, 2, 3, 5, 8];
horde.entomb(13);
harvest horde.curse();  # 6

decay zombie in horde {
    harvest "Zombie strength: " + zombie;
}
```

### String Interpolation

```reaper
soul name = "zombie";
corpse count = 5;
harvest "There are #{count} #{name}s shambling around";
# Output: There are 5 zombies shambling around
```

---

## 🚀 Getting Started

### Installation

Currently in development. Use the Python interpreter:

```bash
python reaper_main.py script.reaper
python reaper_main.py  # Interactive REPL
```

### Interactive REPL

```bash
python reaper_main.py

☠️ REAPER> corpse x = 5;
☠️ REAPER> harvest x;
5
☠️ REAPER> .exit
```

### REPL Commands

- `.exit` - Exit the REPL
- `.clear` - Clear the environment
- `.help` - Show help
- `.vars` - List all variables
- `.funcs` - List all functions
- `.types <var>` - Show variable type

### File Execution

```bash
python reaper_main.py script.reaper
python reaper_main.py script.reaper arg1 arg2
```

### Bytecode Mode

```bash
# Compile to bytecode
python reaper_main.py --compile-bc script.reaper

# Execute bytecode (faster)
python reaper_main.py --bytecode script.reaper.bc
```

### Necronomicon Learning System

```bash
python reaper_main.py --necronomicon
```

Access interactive courses, tutorials, challenges, and AI tutors (Hack Benjamin and Thanatos).

---

## 📚 Additional Resources

### Documentation Files

- **Language Specification**: `core/language_spec.md`
- **Grammar Definition**: `core/grammar.md`
- **Examples**: `core/examples/`
- **Tutorials**: `core/examples/tutorial_*.reaper`

### Project Structure

```
reaper-lang/
├── core/                    # Core language interpreter
│   ├── lexer.py             # Tokenizer
│   ├── parser.py            # AST parser
│   ├── interpreter.py       # Execution engine
│   ├── language_spec.md     # Language specification
│   └── grammar.md           # Formal grammar
├── bytecode/                # Bytecode VM and compiler
│   ├── compiler.py          # AST to bytecode
│   ├── vm.py                # Virtual machine
│   └── instructions.py     # Instruction set
├── libs/                    # Security libraries
│   ├── phantom/            # Network operations
│   ├── crypt/              # Cryptography
│   ├── wraith/             # System operations
│   ├── specter/            # Web operations
│   ├── shadow/             # Anonymity
│   ├── void/               # OSINT scrubbing
│   ├── zombitious/         # Automation
│   └── shinigami/          # Advanced security
├── stdlib/                  # Standard library
│   ├── graveyard/          # File I/O, databases
│   └── necronomicon/       # Learning system
└── examples/                # Example programs
```

---

## 🎓 Learning Path

1. **Basics**: Variables, types, operators
2. **Control Flow**: Conditionals, loops
3. **Functions**: Definition, calling, recursion
4. **Collections**: Arrays, dictionaries, methods
5. **OOP**: Classes, objects, methods
6. **Advanced**: Closures, higher-order functions
7. **Security**: Using security libraries
8. **Bytecode**: Compiling and optimizing

---

## 🔮 Future Features

### Version 1.1 (Planned)
- Floating-point type (`phantom`)
- Enhanced bitwise operators
- List comprehensions
- Switch/match statements

### Version 1.2 (Planned)
- Import/module system
- Exception handling (`risk`/`catch`)
- File I/O operations (`excavate`/`bury`)
- Anonymous functions/lambdas

### Version 2.0 (Future)
- JIT compilation
- Standard library expansion
- Package manager
- IDE plugins
- Syntax highlighting

---

## ⚖️ Legal and Ethical Use

REAPER is designed for:
- Educational purposes
- Ethical security research
- Authorized penetration testing
- Security tool development
- Learning cybersecurity concepts

**DO NOT USE FOR**:
- Unauthorized access
- Malicious activities
- Illegal operations
- Harmful purposes

All security libraries include ethical use warnings and require proper authorization.

---

## 📄 License

MIT License - See `core/LICENSE` for details.

---

## 🤝 Contributing

Contributions welcome! See the project repository for contribution guidelines.

---

## 🎉 Conclusion

REAPER is a unique, powerful, and thematic programming language designed for security operations. With its distinctive syntax, comprehensive type system, and built-in security libraries, REAPER provides a complete platform for learning and practicing cybersecurity concepts.

**The dead have spoken. The REAPER language rises.** ☠️

---

*Last Updated: 2025-01-27*
*Version: 0.2.0*
