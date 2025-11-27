# Reaper Standalone Hacking Language

> **The Undead Programming Language for Security Operations** ☠️

Reaper is being transformed from a Python-based interpreter into a standalone compiled executable language focused on hacking, anonymity, and security operations. The language maintains its unique zombie/death-themed core syntax while adding powerful security-focused libraries.

## 🏗️ Project Structure

This project follows a 6-layer architecture for systematic development:

```
reaper-lang/
├── core/                    # Core language interpreter
│   ├── lexer.py            # Tokenizer
│   ├── parser.py           # AST parser  
│   ├── interpreter.py      # Execution engine
│   └── ...
├── libs/                   # Security libraries (Layer 1)
│   ├── phantom/           # Network operations
│   ├── crypt/             # Cryptography
│   ├── wraith/            # System operations
│   ├── specter/           # Web operations
│   └── shadow/            # Anonymity features
├── bytecode/              # VM and compilation (Layer 3)
├── build/                 # Build scripts and tools
├── stdlib/                # Standard library (Layer 4)
│   ├── graveyard/         # File I/O, databases, etc.
│   └── necronomicon/      # Learning system with AI tutors
├── docs/                  # Documentation (Layer 6)
├── examples/security/     # Security example scripts
└── checkpoints/          # Project state backups
```

## 🎯 Current Status

**Phase 1: Standalone Language Completion** - ✅ COMPLETE
- ✅ Bytecode VM integration with standalone executable
- ✅ Build system with Nuitka
- ✅ Integration tests and verification
- ✅ Bytecode compilation (`--compile-bc`) and execution (`--bytecode`/`--vm`)

**Phase 2: Necronomicon Learning System** - ✅ COMPLETE
- ✅ Core learning system with courses, lessons, challenges
- ✅ Text-based UI with Rich library
- ✅ Progress tracking with SQLite
- ✅ Interactive tutorials and code challenges

**Phase 3: AI Assistant Implementation** - ✅ COMPLETE
- ✅ Hack Benjamin (beginner tutor) - always available
- ✅ Thanatos (advanced expert) - unlockable system
- ✅ Local AI model integration (Ollama support with fallback)
- ✅ Completely anonymous - no corporate API dependencies

**Phase 4: Final Integration** - 🔄 IN PROGRESS
- 🔄 Final documentation updates
- 🔄 End-to-end testing
- 🔄 Release preparation

**Overall Progress**: Phases 1-3 Complete (75%), Phase 4 In Progress

## 🚀 Quick Start

### Development Setup

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd reaper-lang
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements-dev.txt
   ```

2. **Run existing tests**:
   ```bash
   cd core
   python test_runner.py
   ```

3. **Start development**:
   Follow the AI-proof plan in `REAPER_AI_PROOF_PLAN.md`

### Using the Interpreter

**File Execution:**
```bash
python reaper_main.py script.reaper
python reaper_main.py script.reaper arg1 arg2
```

**Interactive REPL:**
```bash
python reaper_main.py
```

**Bytecode Mode (Faster):**
```bash
# Compile to bytecode
python reaper_main.py --compile-bc script.reaper

# Execute bytecode
python reaper_main.py --bytecode script.reaper.bc
```

**Necronomicon Learning System:**
```bash
python reaper_main.py --necronomicon
```

**Thanatos Advanced AI:**
```bash
python reaper_main.py --thanatos
```

## 📚 Documentation

- **Implementation Plan**: `REAPER_AI_PROOF_PLAN.md` - Complete 500+ hour development plan
- **Language Specification**: `core/language_spec.md` - Current language features
- **Grammar**: `core/grammar.md` - Formal grammar definition
- **Project State**: `PROJECT_STATE.md` - Current progress tracking

## 🔧 Development

This project uses an AI-proof development methodology with:
- Detailed task breakdowns with time estimates
- State tracking files for session handoffs
- Checkpoint system for rollback points
- Comprehensive testing at each layer

See `REAPER_AI_PROOF_PLAN.md` for complete development methodology.

## 🎓 Learning System (Necronomicon)

The `necronomicon` library provides:
- **Hack Benjamin**: Beginner AI tutor (always available)
- **Thanatos**: Advanced AI security expert (unlockable after course completion)
- Interactive tutorials and challenges
- Progress tracking with SQLite database
- Code execution sandbox with security limits
- Professional text-based UI

**Launch:**
```bash
python reaper_main.py --necronomicon
```

**Features:**
- Course browser with structured lessons
- Interactive code challenges
- Progress dashboard
- AI-powered hints and guidance
- Local-only AI processing (no external APIs)

## ⚖️ Legal & Ethical

This project is for educational and ethical security research purposes only. All security features include:
- Clear ethical usage guidelines
- Educational warnings in documentation
- Rate limiting to prevent abuse
- No inclusion of actual malware

## 📄 License

MIT License - See `core/LICENSE` for details.

---

**The dead have spoken. The REAPER language rises.** ☠️
