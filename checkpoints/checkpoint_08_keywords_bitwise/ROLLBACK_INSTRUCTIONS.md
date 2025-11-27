# Rollback Instructions - Checkpoint 08

## To Rollback L1-T008: New Keywords and Bitwise Operators

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
rm -rf checkpoints/checkpoint_08_keywords_bitwise/
```

### Step 4: Verify Rollback
- Test that new keywords (infiltrate, cloak, exploit, breach) no longer work
- Test that bitwise operators (rot, wither, spread, mutate, invert) no longer work
- Verify that existing Reaper syntax still works
- Check that parser precedence is back to original state

### What This Rollback Removes
- New keywords: INFILTRATE, CLOAK, EXPLOIT, BREACH
- Bitwise operators: ROT, WITHER, SPREAD, MUTATE, INVERT
- New AST nodes: InfiltrateNode, CloakNode, ExploitNode, BreachNode
- Enhanced lexer identifier parsing for bitwise operators
- New parser statement methods and bitwise operator parsing
- Interpreter visitor methods for new constructs
- Bitwise operation helper methods with 32-bit handling
- Updated parser precedence to include bitwise operations

### After Rollback
- Language core returns to state before L1-T008
- Ready to restart L1-T008 or proceed with different approach
- All security libraries (L1-T001 through L1-T007) remain intact
- New types and literals (L1-T007) remain intact
