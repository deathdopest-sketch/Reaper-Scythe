# REAPER E2E Test Bot

Comprehensive end-to-end testing bot for the Reaper programming language.

## Usage

### Quick Run
```bash
python test_bot/run_tests.py
```

### With Options
```bash
python test_bot/e2e_test_bot.py --output reports/my_report.json
```

### Quiet Mode
```bash
python test_bot/e2e_test_bot.py --quiet
```

## What It Tests

### Core Language Features
- Exception handling (risk/catch/finally)
- Module import system
- File I/O operations
- Async/concurrent operations

### Security Libraries
- Exploit development library
- Binary analysis library
- Memory manipulation library
- Fuzzing framework
- Reverse engineering library

## Output

The bot generates:
1. Real-time console output showing test progress
2. JSON report file with detailed results
3. Summary statistics

## Report Format

Reports are saved as JSON with:
- Test results (pass/fail/skip/error)
- Duration for each test
- Error messages and tracebacks
- Detailed test information

