# Rollback Instructions - Checkpoint 01

## If You Need to Rollback to Before Project Structure Setup

### Step 1: Restore Original Structure
```powershell
# Remove new directories
Remove-Item -Path "libs", "bytecode", "build", "stdlib", "docs", "examples", "checkpoints" -Recurse -Force

# Move core contents back to interpreter
New-Item -ItemType Directory -Path "interpreter" -Force
Move-Item -Path "core\*" -Destination "interpreter\" -Force
Remove-Item -Path "core" -Force
```

### Step 2: Remove State Tracking Files
```powershell
Remove-Item -Path "PROJECT_STATE.md", "SESSION_HANDOFF.md", "TASK_QUEUE.md", "COMPLETED_TASKS.md", "ISSUES_LOG.md", "DECISIONS_LOG.md", "RESOURCES.md" -Force
```

### Step 3: Remove Requirements Files
```powershell
Remove-Item -Path "requirements.txt", "requirements-dev.txt" -Force
```

### Step 4: Restore Original README
```powershell
# Restore original README.md from core/README.md if needed
```

### Step 5: Verify Restoration
```powershell
cd interpreter
python test_runner.py
```

## What This Rollback Will Lose
- All new directory structure
- State tracking system
- Development environment setup
- Documentation structure
- Requirements files

## What This Rollback Will Restore
- Original interpreter/ directory structure
- All existing Reaper functionality
- Original test suite (should pass)
- Original README.md

## When to Use This Rollback
- If the reorganization broke critical functionality
- If you need to start over with a different approach
- If the new structure is causing too many issues

## Alternative: Partial Rollback
If only some parts are problematic:
1. Fix specific issues instead of full rollback
2. Keep the new structure but fix import paths
3. Update test files to work with new structure
4. Install missing dependencies
