# REAPER Language VS Code Extension

Full language support for REAPER in Visual Studio Code.

## Features

### ✨ Syntax Highlighting
- Complete keyword highlighting
- String, number, and comment highlighting
- Operator and punctuation highlighting

### 🔍 Autocomplete
- Keyword suggestions
- Built-in function completions with parameter hints
- Built-in constant suggestions
- Context-aware completions

### 💡 Hover Information
- Built-in function documentation
- Constant value information
- Keyword descriptions

### 🐛 Diagnostics
- Basic syntax error detection
- Unclosed string detection
- Incomplete statement warnings

### 📝 Code Snippets
- Function definitions
- Control flow structures
- Loops and conditionals
- Exception handling
- And more!

### ⚡ Commands
- **Run REAPER File**: Execute the current file
- **Compile to Bytecode**: Compile source to bytecode

### 🎯 Task Support
- Pre-configured tasks for running REAPER files
- Support for bytecode execution

## Installation

### From Source

1. Clone the repository
2. Open in VS Code
3. Press `F5` to launch extension development host
4. Or package and install:
   ```bash
   npm install -g vsce
   vsce package
   code --install-extension reaper-language-1.3.0.vsix
   ```

### Configuration

Add to your `settings.json`:

```json
{
  "reaper.enableDiagnostics": true,
  "reaper.enableAutocomplete": true,
  "reaper.executablePath": "python reaper_main.py"
}
```

## Usage

### Running Files

1. Right-click a `.reaper` file in Explorer
2. Select "Run REAPER File"
3. Or use Command Palette: `REAPER: Run REAPER File`

### Compiling to Bytecode

1. Right-click a `.reaper` file
2. Select "Compile to Bytecode"
3. Creates a `.reaper.bc` file

### Snippets

Type snippet prefixes and press `Tab`:
- `infect` → Function definition
- `if` → If-otherwise statement
- `shamble` → For loop
- `decay` → For-each loop
- `judge` → Switch statement
- And more!

## Development

### Building

```bash
npm install
npm run compile
```

### Testing

Press `F5` in VS Code to launch extension development host.

---

**The dead code in style.** ☠️

