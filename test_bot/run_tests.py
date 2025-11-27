#!/usr/bin/env python3
"""
Quick test runner script.

Run this to execute all E2E tests and watch the results.
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test_bot.e2e_test_bot import E2ETestBot

if __name__ == '__main__':
    print("=" * 70)
    print("REAPER E2E TEST BOT")
    print("=" * 70)
    print()
    
    bot = E2ETestBot(verbose=True)
    report = bot.run_all_tests()
    
    print()
    print("=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)
    
    # Return exit code
    sys.exit(1 if (report.failed > 0 or report.errors > 0) else 0)

