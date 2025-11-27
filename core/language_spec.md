# REAPER Language Specification

## Philosophy and Design Principles

REAPER is a zombie/death-themed programming language that combines the power of modern programming constructs with a unique thematic identity. Every aspect of the language is designed to maintain the undead aesthetic while providing practical programming capabilities.

### Core Tenets

1. **Thematic Consistency**: All keywords, operators, and built-in functions follow the zombie/death theme
2. **Explicit Typing**: No implicit type conversions - all conversions must be explicit
3. **Safety First**: Comprehensive error handling, bounds checking, and resource limits
4. **Clarity Over Cleverness**: Code should be readable and maintainable
5. **Performance Awareness**: Resource limits prevent runaway programs

## Type System

REAPER has 8 fundamental types:

### 1. corpse (Integer)
- **Purpose**: Whole numbers only
- **Range**: Limited by Python's int (effectively unlimited)
- **Operations**: All arithmetic, comparison, logical (as 0/1)
- **Examples**: `corpse zombies = 10;`, `corpse health = -5;`

### 1.5. phantom (Floating-Point) ⭐ NEW
- **Purpose**: Decimal numbers for precise calculations
- **Range**: Limited by Python's float (IEEE 754 double precision)
- **Operations**: All arithmetic, comparison
- **Examples**: `phantom pi = 3.14159;`, `phantom rate = 0.05;`

### 2. soul (String)
- **Purpose**: Text data with escape sequence support
- **Max Length**: 1MB per string
- **Operations**: Concatenation (+), indexing, slicing, methods
- **Examples**: `soul message = "Braaaaains";`, `soul name = 'zombie';`

### 3. crypt (Array/List)
- **Purpose**: Ordered collections of values
- **Max Size**: 10,000 elements
- **Operations**: Indexing, slicing, built-in methods
- **Examples**: `crypt horde = [1, 2, 3];`, `crypt empty = [];`

### 4. grimoire (Dictionary/Map)
- **Purpose**: Key-value pairs for data organization
- **Max Size**: 10,000 key-value pairs
- **Access**: `dict{"key"}` syntax only
- **Examples**: `grimoire stats = {"health": 100};`

### 5. wraith (Boolean)
- **Purpose**: True/false values
- **Values**: `DEAD` (false/0), `RISEN` (true/1)
- **Operations**: Logical operators, comparison
- **Examples**: `wraith alive = RISEN;`, `wraith dead = DEAD;`

### 6. tomb (Class Instance)
- **Purpose**: Object-oriented programming
- **Features**: Properties, methods, constructors
- **Examples**: `tomb zombie = spawn Zombie();`

### 7. void (Null/None)
- **Purpose**: Represents absence of value
- **Default**: Uninitialized variables default to `void`
- **Examples**: `soul name;` (defaults to void)

## Operator Precedence Table

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

## Keywords and Built-ins

### Type Keywords
- `corpse` - integer type
- `soul` - string type  
- `crypt` - array type
- `grimoire` - dictionary type
- `tomb` - class type
- `wraith` - boolean type
- `void` - null type
- `eternal` - constant modifier

### Control Flow Keywords
- `infect` - function definition
- `raise` - function call (optional)
- `harvest` - print/output
- `reap` - return
- `shamble` - for loop
- `decay` - foreach loop
- `soulless` - infinite while loop
- `spawn` - class instantiation
- `if` / `otherwise` - conditionals
- `flee` - break
- `persist` - continue
- `rest` - sleep/pause

### Logical Operators
- `corrupt` - logical AND (&&)
- `infest` - logical OR (||)
- `banish` - logical NOT (!)

### Built-in Constants
- `DEAD` - 0 (false)
- `RISEN` - 1 (true)
- `void` - null value

### Built-in Functions (11 total)

#### I/O Functions
- `harvest(...)` - Print variadic arguments to stdout
- `summon()` - Read line from stdin, returns soul
- `final_rest(code)` - Exit program with exit code

#### Type Conversion
- `raise_corpse(soul)` - Convert string to integer
- `steal_soul(corpse)` - Convert integer to string

#### Utility Functions
- `rest(ms)` - Sleep for milliseconds
- `curse(condition, message)` - Assert condition, raise error if false
- `absolute(corpse)` - Absolute value
- `lesser(a, b)` - Minimum of two values
- `greater(a, b)` - Maximum of two values

#### System Variables
- `ritual_args` - Array of command-line arguments

## Scope and Closures

### Lexical Scoping
REAPER uses lexical scoping where inner functions can access variables from outer scopes:

```reaper
infect Outer() {
    corpse x = 10;
    
    infect Inner() {
        harvest x;  // Accesses outer x
    }
    
    raise Inner();
}
```

### Variable Shadowing
- Inner scopes can shadow outer variables
- Built-in constants (DEAD, RISEN, void) cannot be shadowed
- Built-in functions cannot be redefined

### Closures
Functions capture their lexical environment at definition time:

```reaper
infect CreateCounter() -> infect {
    corpse count = DEAD;
    
    infect Counter() -> corpse {
        count = count + RISEN;
        reap count;
    }
    
    reap Counter;
}
```

## Error Types and Handling

### Syntax Errors (ReaperSyntaxError)
- Invalid syntax, missing semicolons, unmatched braces
- Includes line/column information and suggestions
- Example: `corpse x = 5` (missing semicolon)

### Runtime Errors (ReaperRuntimeError)
- Division by zero, undefined variables, type mismatches
- Includes stack trace and variable state
- Example: `corpse x; harvest x + 5;` (x is void)

### Type Errors (ReaperTypeError)
- Attempting operations on incompatible types
- Shows expected vs actual types
- Example: `corpse x = 5; soul y = "hello"; harvest x + y;`

### Resource Errors
- **ReaperRecursionError**: Max recursion depth (1000) exceeded
- **ReaperMemoryError**: String/array/dict size limits exceeded
- **ReaperIndexError**: Array/string index out of bounds
- **ReaperKeyError**: Dictionary key not found
- **ReaperZeroDivisionError**: Division or modulo by zero

## Design Decisions and Rationale

### Why No Implicit Type Conversion?
Explicit conversions prevent subtle bugs and make code intent clear:
```reaper
corpse x = 5;
soul y = "10";
// harvest x + y;  // ERROR - must be explicit
harvest x + raise_corpse(y);  // OK - explicit conversion
```

### Why Dictionary Access with {}?
Consistency with arrays and avoiding method call confusion:
```reaper
grimoire stats = {"health": 100};
harvest stats{"health"};  // Clear indexing
// harvest stats.health;  // Would conflict with methods
```

### Why Integer Division Only?
Simplicity and predictability - no floating-point precision issues:
```reaper
corpse result = 5 / 2;  // Always 2, never 2.5
```

### Why Short-Circuit Evaluation?
Performance and safety - don't evaluate unnecessary expressions:
```reaper
if (x != DEAD corrupt (10 / x > 2)) {  // Won't divide by zero if x is DEAD
    harvest "Safe division";
}
```

## Code Examples

### Hello World
```reaper
infect Greet(soul name) {
    harvest "Greetings from the graveyard, " + name;
}

raise Greet("mortal");
```

### Factorial Function
```reaper
infect CollectSouls(corpse n) -> corpse {
    if (n <= DEAD) {
        reap RISEN;
    }
    reap n * CollectSouls(n - RISEN);
}

corpse total = CollectSouls(5);
harvest total;  // Output: 120
```

### Class with Methods
```reaper
tomb Zombie {
    corpse health = 100;
    soul moan = "Braaaaains";
    
    infect Zombie(corpse initial_health = 100) {
        this.health = initial_health;
    }
    
    infect Attack() {
        this.health = this.health - 10;
    }
    
    infect IsAlive() -> wraith {
        reap this.health > DEAD;
    }
}

tomb zombie = spawn Zombie(150);
zombie.Attack();
harvest zombie.IsAlive();  // Output: RISEN
```

### Array Operations
```reaper
crypt horde = [1, 2, 3, 5, 8];

# Add new zombie
horde.entomb(13);

# Check horde size
harvest horde.curse();  // Output: 6

# Process each zombie
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

## Comparison with Other Languages

### vs Python
- **Similarities**: Indentation-based blocks, dynamic typing concepts
- **Differences**: Explicit type declarations, no implicit conversions, themed keywords
- **Performance**: Similar interpreter performance, but with resource limits

### vs JavaScript
- **Similarities**: C-style syntax, object-oriented features
- **Differences**: Static typing, no prototype inheritance, themed operators
- **Safety**: More type safety, explicit error handling

### vs C/Java
- **Similarities**: Explicit typing, semicolon-terminated statements
- **Differences**: No manual memory management, built-in collections, themed syntax

## Performance Characteristics

### Benchmarks
- **Startup Time**: < 500ms for typical programs
- **Execution Speed**: ~1000 operations per second
- **Memory Usage**: Bounded by resource limits
- **Recursion**: Max depth 1000 calls

### Resource Limits
- **String Length**: 1MB per string
- **Array Size**: 10,000 elements
- **Dictionary Size**: 10,000 key-value pairs
- **Recursion Depth**: 1000 calls
- **Execution Timeout**: 30 seconds

## Security Measures

### Input Validation
- All user input is validated and sanitized
- Bounds checking on all array/string operations
- Type checking prevents injection attacks

### Resource Protection
- Memory limits prevent DoS attacks
- Timeout prevents infinite loops
- Recursion limits prevent stack overflow

### Error Handling
- All errors are caught and reported gracefully
- No crashes on malformed input
- Helpful error messages guide users to fixes

## Future Roadmap

### Version 1.1 (Planned)
- Floating-point type (`phantom`)
- Bitwise operators (`rot`, `wither`, `spread`, `mutate`, `invert`)
- List comprehensions
- Switch/match statements

### Version 1.2 (Planned)
- Import/module system (`summon module`)
- Exception handling (`risk`/`catch`)
- File I/O operations (`excavate`/`bury`)
- Anonymous functions/lambdas

### Version 2.0 (Future)
- Compiler to bytecode
- JIT compilation
- Standard library expansion
- Package manager
- IDE plugins

## Getting Started

### Installation
```bash
# Future: pip install reaper-lang
python reaper.py script.reaper
```

### REPL Usage
```bash
python reaper.py
☠️ REAPER> corpse x = 5;
☠️ REAPER> harvest x;
5
☠️ REAPER> .exit
```

### File Execution
```bash
python reaper.py hello.reaper
# Executes hello.reaper and displays output
```

This specification provides the complete foundation for implementing and using the REAPER programming language. All features are designed to work together cohesively while maintaining the unique undead theme.
