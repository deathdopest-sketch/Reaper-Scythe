# Bytecode VM Limitations

**Version**: 0.2.0  
**Last Updated**: 2025-01-27

## Known Limitations

### User-Defined Functions

The bytecode VM currently has limited support for user-defined functions. When a script contains user-defined functions (defined with `infect`), the bytecode execution mode may not work correctly.

**Workaround**: Use interpreter mode (default) instead of bytecode mode for scripts with user-defined functions:

```bash
# Use interpreter (works with all features)
python reaper_main.py script.reaper

# Bytecode mode (limited - may not work with user-defined functions)
python reaper_main.py --bytecode script.reaper.bc
```

### What Works

✅ **Bytecode Compilation**: All scripts can be compiled to bytecode  
✅ **Bytecode Execution**: Works for scripts without user-defined functions  
✅ **Built-in Functions**: All built-in functions work in bytecode mode  
✅ **Interpreter Mode**: Full support for all language features

### What's Limited

⚠️ **User-Defined Functions**: Function calls to user-defined functions may not work in bytecode execution mode  
⚠️ **Function Definitions**: Function definitions are compiled but execution may fail

## Technical Details

The bytecode compiler can compile function definitions and function calls, but the bytecode VM needs additional work to:
1. Store function bytecode in the program
2. Execute function bytecode when called
3. Handle function parameters and return values

This is planned for a future release.

## Future Improvements

- Full bytecode support for user-defined functions
- Function inlining optimizations
- Better error messages for unsupported features
- Automatic fallback to interpreter mode when needed

---

**Note**: The interpreter mode supports all language features and is the recommended mode for development and scripts with user-defined functions.

