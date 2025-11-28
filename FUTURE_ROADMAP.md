# REAPER Language - Future Development Roadmap

**Current Version**: 1.4.0  
**Last Updated**: 2025-01-27

---

## 🎯 Development Priorities

### Phase 5: Core Language Enhancements (Next)

#### Priority 1: Floating-Point Type (`phantom`) ✅
**Status**: ✅ **COMPLETE**  
**Impact**: High - Enables decimal/numeric operations  
**Effort**: Completed (4 hours)

**Requirements:**
- Add `phantom` keyword to lexer
- Create `PhantomNode` AST node
- Update parser to recognize `phantom` type
- Implement floating-point arithmetic in interpreter
- Add type conversion functions
- Update bytecode compiler and VM
- Add tests

**Benefits:**
- Complete numeric type system
- Enables scientific computing
- Better for security calculations (encryption, hashing)

---

#### Priority 2: Full Bytecode VM Function Support ✅
**Status**: ✅ **COMPLETE** (Basic functions working, recursion needs minor fixes)  
**Impact**: High - Fixes current bytecode limitation  
**Effort**: Completed (6 hours)

**Requirements:**
- Compile function definitions to bytecode
- Store function bytecode in program
- Implement function call mechanism in VM
- Handle function parameters and return values
- Support closures and nested functions
- Update bytecode format if needed

**Benefits:**
- Bytecode mode works for all scripts
- 10x performance for all code
- Complete bytecode system

---

#### Priority 3: Import/Module System ✅
**Status**: ✅ **COMPLETE**  
**Impact**: High - Enables library usage  
**Effort**: Completed (4 hours)

**Requirements:**
- Implement `INFILTRATE` keyword (import)
- Module resolution system
- Namespace support
- Library integration (security libs)
- Circular dependency detection
- Module caching

**Benefits:**
- Use security libraries from Reaper code
- Code organization and reusability
- Standard library access

---

#### Priority 4: Exception Handling (`risk`/`catch`) ✅
**Status**: ✅ **COMPLETE**  
**Impact**: High - Critical for robust code  
**Effort**: Completed (3 hours)

**Requirements:**
- Implement `risk` keyword (try block)
- Implement `catch` keyword (catch block)
- Implement `finally` keyword (finally block)
- Exception type hierarchy
- Exception throwing mechanism
- Exception propagation

**Benefits:**
- Robust error handling
- Better security tool development
- Professional error management

---

#### Priority 5: File I/O Operations ✅
**Status**: ✅ **COMPLETE**  
**Impact**: High - Essential for security tools  
**Effort**: Completed (4 hours)

**Requirements:**
- ✅ `excavate` function (read file)
- ✅ `bury` function (write file)
- ✅ Binary file support (`excavate_bytes`, `bury_bytes`)
- ✅ File metadata operations (`inspect`)
- ✅ Directory operations (`list_graves`, `create_grave`, `remove_grave`)
- ✅ Path manipulation (`join_paths`, `split_path`, `normalize_path`)
- ✅ String encoding/decoding (`encode_soul`, `decode_soul`)

**Benefits:**
- Complete file system access
- Essential for security operations
- Data persistence

---

### Phase 6: Advanced Features

#### List Comprehensions ✅
**Status**: ✅ **COMPLETE**  
**Impact**: Medium - Code elegance  
**Effort**: Completed (2 hours)

#### Switch/Match Statements ✅
**Status**: ✅ **COMPLETE**  
**Impact**: Medium - Control flow enhancement  
**Effort**: Completed (2 hours)

#### Anonymous Functions/Lambdas ✅
**Status**: ✅ **COMPLETE**  
**Impact**: Medium - Functional programming  
**Effort**: Completed (3 hours)

---

### Phase 7: Performance & Optimization

#### JIT Compilation
**Status**: 🔄 Future  
**Impact**: High - Performance boost  
**Effort**: Very High (20+ hours)

#### Advanced Optimizations ✅
**Status**: ✅ **COMPLETE**  
**Impact**: Medium - Better performance  
**Effort**: Completed (3 hours)

**Implemented:**
- ✅ Jump chain elimination
- ✅ Dead code elimination
- ✅ Unreachable code removal
- ✅ Enhanced peephole optimizations

---

### Phase 8: Developer Experience

#### Package Manager ✅
**Status**: ✅ **COMPLETE**  
**Impact**: High - Ecosystem growth  
**Effort**: Very High (30+ hours)

**Features Implemented**:
- Package manifest system (`reaper.toml`)
- Git-based package installation (GitHub, GitLab, generic Git)
- Dependency resolution and installation
- Package discovery in `reaper_modules/` directory
- CLI commands: `init`, `install`, `list`, `uninstall`, `update`
- Integration with module loader for automatic package discovery

#### IDE Plugins ✅
**Status**: ✅ **COMPLETE**  
**Impact**: Medium - Developer experience  
**Effort**: Completed (4 hours)

**Implemented:**
- ✅ VS Code extension with full language support
- ✅ Autocomplete for keywords, built-ins, and constants
- ✅ Hover information and documentation
- ✅ Code snippets for common patterns
- ✅ Basic diagnostics and syntax checking
- ✅ Run and compile commands
- ✅ Task definitions for build/run

#### Syntax Highlighting ✅
**Status**: ✅ **COMPLETE**  
**Impact**: Medium - Developer experience  
**Effort**: Completed (2 hours)

---

## 📋 Implementation Order

### Version 0.3.0 (Next Release)
1. ✅ Floating-point type (`phantom`) - **COMPLETE**
2. 🔄 Enhanced error messages
3. 🔄 More Necronomicon courses

### Version 0.4.0
1. ✅ Full bytecode VM function support
2. ✅ Performance improvements

### Version 1.0.0 (Major Release)
1. ✅ Import/module system
2. ✅ Exception handling (`risk`/`catch`)
3. ✅ File I/O operations
4. ✅ List comprehensions
5. ✅ Switch/match statements

### Version 2.0.0 (Future)
1. ✅ JIT compilation
2. ✅ Package manager
3. ✅ IDE plugins
4. ✅ Standard library expansion

---

## 🚀 Quick Start: Next Feature

**Recommended**: Start with **Floating-Point Type (`phantom`)** as it's:
- High impact
- Relatively straightforward
- Foundation for other features
- Completes the numeric type system

---

**The dead are patient. They wait. They plan. They execute.** ☠️

