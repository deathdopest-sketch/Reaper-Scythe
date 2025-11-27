# REAPER Language Grammar (EBNF)

## Overview
This document defines the complete formal grammar for the REAPER programming language using Extended Backus-Naur Form (EBNF).

## Terminal Symbols

### Keywords
```
corpse, soul, crypt, grimoire, tomb, wraith, void, eternal,
infect, raise, harvest, reap, shamble, decay, soulless, spawn,
if, otherwise, flee, persist, corrupt, infest, banish, rest,
this, from, to, in, DEAD, RISEN
```

### Operators
```
+ - * / % == != < > <= >= = += -= *= /= %=
corrupt infest banish
```

### Delimiters
```
{ } ( ) [ ] ; , . -> :
```

### Literals
```
NUMBER ::= [0-9]+ | -[0-9]+
STRING ::= "([^"\\]|\\.)*" | '([^'\\]|\\.)*'
RAW_STRING ::= r"([^"]*)" | r'([^']*)'
IDENTIFIER ::= [a-zA-Z_][a-zA-Z0-9_]*
```

### Special Tokens
```
EOF, NEWLINE, STRING_PART, INTERPOLATION_START, INTERPOLATION_END
```

## Non-Terminal Symbols

### Program Structure
```
program ::= statement*
statement ::= variable_declaration
            | function_definition
            | class_definition
            | if_statement
            | shamble_loop
            | decay_loop
            | soulless_loop
            | harvest_statement
            | return_statement
            | flee_statement
            | persist_statement
            | expression_statement
            | block
```

### Variable Declarations
```
variable_declaration ::= type_specifier IDENTIFIER "=" expression ";"
                       | "eternal" type_specifier IDENTIFIER "=" expression ";"

type_specifier ::= "corpse" | "soul" | "crypt" | "grimoire" | "tomb" | "wraith"
```

### Function Definitions
```
function_definition ::= "infect" IDENTIFIER "(" parameter_list ")" return_type? block

parameter_list ::= parameter ("," parameter)*
parameter ::= type_specifier IDENTIFIER ("=" expression)?
return_type ::= "->" type_specifier
```

### Class Definitions
```
class_definition ::= "tomb" IDENTIFIER "{" class_member* "}"

class_member ::= variable_declaration
               | function_definition
               | constructor_definition

constructor_definition ::= "infect" IDENTIFIER "(" parameter_list ")" block
```

### Control Flow
```
if_statement ::= "if" "(" expression ")" block else_clause?

else_clause ::= "otherwise" "if" "(" expression ")" block else_clause?
              | "otherwise" block

shamble_loop ::= "shamble" IDENTIFIER "from" expression "to" expression block

decay_loop ::= "decay" IDENTIFIER "in" expression block

soulless_loop ::= "soulless" block

block ::= "{" statement* "}"
```

### Statements
```
harvest_statement ::= "harvest" expression ("," expression)* ";"

return_statement ::= "reap" expression? ";"

flee_statement ::= "flee" ";"

persist_statement ::= "persist" ";"

expression_statement ::= expression ";"
```

### Expressions (Precedence Order)
```
expression ::= assignment

assignment ::= logical_or ("=" | "+=" | "-=" | "*=" | "/=" | "%=") assignment
              | logical_or

logical_or ::= logical_and ("infest" logical_and)*

logical_and ::= comparison ("corrupt" comparison)*

comparison ::= term (("==" | "!=" | "<" | ">" | "<=" | ">=") term)*

term ::= factor (("+" | "-") factor)*

factor ::= unary (("*" | "/" | "%") unary)*

unary ::= ("-" | "banish") unary
        | postfix

postfix ::= primary ("." IDENTIFIER
                   | "[" expression "]"
                   | "[" slice "]"
                   | "(" argument_list? ")")*

primary ::= NUMBER
          | STRING
          | interpolated_string
          | RAW_STRING
          | "DEAD"
          | "RISEN"
          | "void"
          | IDENTIFIER
          | "(" expression ")"
          | array_literal
          | dictionary_literal
          | "spawn" IDENTIFIER "(" argument_list? ")"
```

### String Interpolation
```
interpolated_string ::= STRING_PART interpolation_part*

interpolation_part ::= INTERPOLATION_START expression INTERPOLATION_END STRING_PART
```

### Literals
```
array_literal ::= "[" (expression ("," expression)*)? "]"

dictionary_literal ::= "{" (key_value_pair ("," key_value_pair)*)? "}"

key_value_pair ::= expression ":" expression

slice ::= expression? ":" expression? (":" expression?)?

argument_list ::= expression ("," expression)*
```

## Operator Precedence (Highest to Lowest)

1. **Postfix**: `.` (property access), `[]` (indexing), `()` (function call)
2. **Unary**: `-` (negation), `banish` (NOT)
3. **Multiplicative**: `*`, `/`, `%`
4. **Additive**: `+`, `-`
5. **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
6. **Logical AND**: `corrupt`
7. **Logical OR**: `infest`
8. **Assignment**: `=`, `+=`, `-=`, `*=`, `/=`, `%=`

## Associativity Rules

- **Left-associative**: `+`, `-`, `*`, `/`, `%`, `corrupt`, `infest`, `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Right-associative**: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, unary operators
- **Non-associative**: comparison operators (chaining not supported)

## Examples

### Variable Declaration
```
corpse zombies = 10;
soul message = "Braaaaains";
crypt horde = [1, 2, 3];
eternal corpse MAX_ZOMBIES = 1000;
```

### Function Definition
```
infect Bite(corpse victim) -> corpse {
    reap victim + RISEN;
}

infect Greet(soul name = "mortal") {
    harvest "Hello " + name;
}
```

### Class Definition
```
tomb Zombie {
    corpse health = 100;
    soul moan = "Braaaaains";
    
    infect Zombie(corpse initial_health = 100) {
        this.health = initial_health;
    }
    
    infect Attack() {
        this.health = this.health - 10;
    }
}
```

### Control Flow
```
if (hunger > 50) {
    harvest "Hungry...";
} otherwise if (hunger > 20) {
    harvest "Getting hungry";
} otherwise {
    harvest "Satisfied";
}

shamble i from RISEN to 10 {
    harvest i;
}

decay zombie in horde {
    zombie.Attack();
}
```

### String Interpolation
```
soul name = "zombie";
corpse count = 5;
harvest "There are #{count} #{name}s shambling around";
```

### Array and Dictionary Literals
```
crypt numbers = [1, 2, 3, 5, 8];
grimoire stats = {"health": 100, "hunger": 50, "speed": 2};
```

## Grammar Notes

1. **Semicolons**: Required after all statements except block statements
2. **Comments**: `#` for single-line, `##...##` for multi-line (not part of grammar)
3. **String Interpolation**: Handled at lexer level, parsed as special tokens
4. **Method Chaining**: Supported through postfix operators
5. **Default Parameters**: Must come after non-default parameters
6. **Built-in Functions**: Treated as special identifiers, cannot be redefined
7. **Type System**: Static typing with explicit type declarations
8. **Scope**: Lexical scoping with closures supported
