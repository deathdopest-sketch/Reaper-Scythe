# Bytecode VM Status

**Status**: Experimental. Use the interpreter (the default) for real work.

## What was fixed

- The compiler's optimisation passes (`_peephole_optimize`, `_optimize_jumps`,
  `_eliminate_dead_code`) deleted instructions without remapping jump targets or
  function offsets, and two of them removed every function body as "unreachable".
  They are disabled until they rewrite offsets after removal.
- Built-in calls received their arguments in reverse order (e.g. `bury(path, content)`
  wrote to a file named after the content). Fixed.
- `lesser`, `greater`, `curse`, `haunt`, `rest` read from the stack instead of their
  arguments and crashed. Fixed.
- `excavate_bytes`, `bury_bytes`, `inspect`, `list_graves`, `create_grave`,
  `remove_grave`, `join_paths`, `split_path`, `normalize_path`, `encode_soul`,
  `decode_soul` were registered but never defined, so the VM crashed on startup.
  They now delegate to the interpreter's implementations.
- Scripts using features the compiler can't emit (e.g. array methods like `.curse()`)
  fall back to the interpreter with a warning instead of crashing.

## Known gaps

Output matches the interpreter for 25 of 48 scripts in `core/test_examples` and
`core/test_*.reaper`. Known problems:

- Recursion (`factorial.reaper`) hits "Maximum instruction count exceeded".
- `else if` chains underflow the stack.
- `flee` (break), `persist` (continue), `infiltrate`, and `tomb` classes compile to nothing.
- `void` values aren't printed by `harvest`.
- Runtime errors (key, bounds, type, undefined variable) are reported differently or not at all.
- `curse(x)` as a builtin returns the length; the interpreter's `curse` builtin takes 2 arguments.

## Usage

```bash
python reaper_main.py script.reaper              # interpreter (recommended)
python reaper_main.py --bytecode script.reaper   # experimental VM
```
