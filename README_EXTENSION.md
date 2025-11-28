# REAPER Language VS Code Extension

Complete IDE support for the REAPER programming language in Visual Studio Code.

**Publisher**: DeathDopest  
**© 2025 DeathAIAUS. All rights reserved.**

## Features

### 🎨 Syntax Highlighting
- Full keyword, operator, and type highlighting
- String interpolation support
- Number formats (decimal, hex, binary, float)
- Comment highlighting

### 🔍 IntelliSense
- **Autocomplete**: Keywords, built-in functions, and constants
- **Hover Information**: Documentation for built-ins and keywords
- **Parameter Hints**: Function signatures with parameters

### 📝 Code Snippets
Pre-configured snippets for common patterns:
- `infect` - Function definition
- `if` - If-otherwise statement
- `shamble` - For loop
- `decay` - For-each loop
- `judge` - Switch statement
- `risk` - Exception handling
- `lambda` - Anonymous functions
- And more!

### 🐛 Diagnostics
- Basic syntax error detection
- Unclosed string detection
- Incomplete statement warnings

### ⚡ Commands
- **Run REAPER File**: Execute current file
- **Compile to Bytecode**: Compile source to bytecode

### 🎯 Tasks
Pre-configured tasks for:
- Running REAPER files
- Compiling to bytecode
- Running bytecode files

## Installation

### Development Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Compile TypeScript:
   ```bash
   npm run compile
   ```
4. Press `F5` in VS Code to launch extension development host

### Packaging for Distribution

```bash
npm install -g vsce
vsce package
```

This creates a `.vsix` file that can be installed:
```bash
code --install-extension reaper-language-1.3.0.vsix
```

## Configuration

Add to your VS Code `settings.json`:

```json
{
  "reaper.enableDiagnostics": true,
  "reaper.enableAutocomplete": true,
  "reaper.executablePath": "python reaper_main.py"
}
```

## Usage

### Running Files

1. **Right-click** a `.reaper` file → "Run REAPER File"
2. **Command Palette** (`Ctrl+Shift+P`) → "REAPER: Run REAPER File"
3. **Keyboard**: Use task runner (`Ctrl+Shift+B`)

### Snippets

Type the snippet prefix and press `Tab`:
- `infect` → Function template
- `if` → If-otherwise template
- `shamble` → For loop template
- `decay` → For-each template
- `judge` → Switch template
- `risk` → Exception handling template

### Autocomplete

Start typing and VS Code will suggest:
- Keywords (corpse, soul, infect, etc.)
- Built-in functions (harvest, excavate, etc.)
- Built-in constants (DEAD, RISEN, void)

## File Structure

```
.
├── src/
│   └── extension.ts          # Main extension code
├── syntaxes/
│   └── reaper.tmLanguage.json # TextMate grammar
├── snippets/
│   └── reaper.json          # Code snippets
├── package.json             # Extension manifest
├── tsconfig.json            # TypeScript config
└── language-configuration.json # Language config
```

## Development

### Building

```bash
npm install
npm run compile
```

### Watching for Changes

```bash
npm run watch
```

### Testing

1. Open this folder in VS Code
2. Press `F5` to launch extension development host
3. Open a `.reaper` file to test features

## Features in Detail

### Autocomplete Provider

Provides completions for:
- All REAPER keywords
- Built-in functions with parameter hints
- Built-in constants
- Context-aware suggestions

### Hover Provider

Shows documentation when hovering over:
- Built-in functions
- Built-in constants
- Keywords

### Diagnostic Provider

Performs basic syntax checking:
- Unclosed strings
- Incomplete statements
- Common syntax errors

### Command Provider

Registers commands:
- `reaper.runFile` - Execute REAPER file
- `reaper.compileBytecode` - Compile to bytecode

## Contributing

To add new features:
1. Edit `src/extension.ts` for functionality
2. Edit `snippets/reaper.json` for snippets
3. Edit `syntaxes/reaper.tmLanguage.json` for syntax
4. Run `npm run compile` to build
5. Test with `F5` in VS Code

---

**The dead code in style.** ☠️

