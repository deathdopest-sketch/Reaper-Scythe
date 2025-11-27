# Rollback Instructions - Checkpoint 11: Bytecode Compiler Optimizations

To revert the project to the state before the implementation of compiler optimizations (L1-T011), follow these steps:

1.  **Revert Compiler File**:
    -   Revert `bytecode/compiler.py` to its state before L1-T011 (remove `_peephole_optimize()` and constant folding in `_compile_binary_op`, remove `_literal_value` helper).

2.  **Delete Checkpoint Directory**:
    -   Delete the entire directory: `checkpoints/checkpoint_11_compiler_optimizations/`

3.  **Revert Project State Tracking Files**:
    -   Revert `PROJECT_STATE.md` to its state before L1-T011.
    -   Revert `SESSION_HANDOFF.md` to its state before L1-T011.
    -   Revert `COMPLETED_TASKS.md` to its state before L1-T011.

**Verification**:
After performing these steps, verify that the bytecode compiler no longer includes optimization passes and returns to the state after L1-T010.

