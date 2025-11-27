# Rollback Instructions - Checkpoint 02 Phantom Library

If you need to rollback the Phantom Network Library implementation:

## Files to Delete
```bash
# Core library files
rm -rf libs/phantom/

# Test files
rm tests/test_phantom_core.py

# Demo files
rm examples/phantom_demo.py
```

## Files to Revert
```bash
# Reset phantom module to empty state
echo "# Phantom Network Operations Library
# Network scanning, packet crafting, DNS operations

__version__ = \"0.1.0\"
__author__ = \"Reaper Security Team\"

# Will be implemented in L1-T002 and L1-T003
# Core features: port scanning, packet crafting, DNS
# Advanced features: proxy support, sniffing, SSL/TLS

__all__ = [
    # Will be populated as features are implemented
]" > libs/phantom/__init__.py
```

## State Files to Update
1. **PROJECT_STATE.md**: Remove L1-T002 completion, set active task back to L1-T002
2. **COMPLETED_TASKS.md**: Remove L1-T002 entry, update statistics
3. **TASK_QUEUE.md**: Move L1-T002 back to pending tasks

## Verification
After rollback:
- `python -c "import libs.phantom"` should work but show empty module
- No phantom-related tests should exist
- Project state should show L1-T002 as pending

## Recovery
To re-implement Phantom library:
1. Follow L1-T002 task plan in `REAPER_AI_PROOF_PLAN.md`
2. Implement scanner.py, packet.py, dns.py modules
3. Create comprehensive test suite
4. Update all state tracking files
5. Create checkpoint 02 again
