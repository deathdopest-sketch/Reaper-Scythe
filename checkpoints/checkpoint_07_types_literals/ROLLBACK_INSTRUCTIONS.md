# Rollback Instructions - Checkpoint 07

## To Rollback L1-T007: New Types and Literals

### Step 1: Revert Core Language Files
```bash
# Revert tokens.py
git checkout HEAD~1 -- core/tokens.py

# Revert ast_nodes.py  
git checkout HEAD~1 -- core/ast_nodes.py

# Revert lexer.py
git checkout HEAD~1 -- core/lexer.py

# Revert parser.py
git checkout HEAD~1 -- core/parser.py

# Revert interpreter.py
git checkout HEAD~1 -- core/interpreter.py

# Revert environment.py
git checkout HEAD~1 -- core/environment.py

# Revert reaper.py
git checkout HEAD~1 -- core/reaper.py
```

### Step 2: Revert Project State Files
```bash
# Revert project state tracking files
git checkout HEAD~1 -- PROJECT_STATE.md
git checkout HEAD~1 -- SESSION_HANDOFF.md
git checkout HEAD~1 -- TASK_QUEUE.md
git checkout HEAD~1 -- COMPLETED_TASKS.md
```

### Step 3: Remove Checkpoint Directory
```bash
rm -rf checkpoints/checkpoint_07_types_literals/
```

### Step 4: Verify Rollback
- Test that hex literals (0x1A2B) no longer work
- Test that binary literals (0b10101010) no longer work
- Test that new types (phantom, specter, shadow) are not recognized
- Verify that floating-point numbers still work (3.14)

### What This Rollback Removes
- New type keywords: PHANTOM, SPECTER, SHADOW
- Hex literal support: 0x1A2B
- Binary literal support: 0b10101010
- Enhanced floating-point parsing
- New AST nodes for literal types
- Parser recognition of new types
- Interpreter visitor methods for new literals
- Fixed relative imports in core modules
- Added _error method to parser

### After Rollback
- Language core returns to state before L1-T007
- Ready to restart L1-T007 or proceed with different approach
- All security libraries (L1-T001 through L1-T006) remain intact
