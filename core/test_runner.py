#!/usr/bin/env python3
"""
REAPER Language Test Runner

This script automatically runs all test files in the test_examples directory
and validates their output against expected results.
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of a single test."""
    filename: str
    passed: bool
    expected: str
    actual: str
    error_type: Optional[str] = None
    error_message: Optional[str] = None


class TestRunner:
    """Test runner for REAPER language tests."""
    
    def __init__(self, test_dir: str = "test_examples"):
        """
        Initialize test runner.
        
        Args:
            test_dir: Directory containing test files
        """
        self.test_dir = Path(test_dir)
        self.results: List[TestResult] = []
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'reset': '\033[0m',
            'bold': '\033[1m'
        }
    
    def _colorize(self, text: str, color: str) -> str:
        """Add color to text if terminal supports it."""
        if sys.stdout.isatty():
            return f"{self.colors[color]}{text}{self.colors['reset']}"
        return text
    
    def _parse_test_file(self, filepath: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse test file to extract expected output or error.
        
        Args:
            filepath: Path to test file
            
        Returns:
            Tuple of (expected_output, expected_error_type)
        """
        expected_output = None
        expected_error = None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for all EXPECT: comments
            expect_matches = re.findall(r'#\s*EXPECT:\s*(.*?)(?:\n|$)', content)
            if expect_matches:
                expected_output = '\n'.join(match.strip() for match in expect_matches)
            
            # Look for ERROR: comment
            error_match = re.search(r'#\s*ERROR:\s*(.*?)(?:\n|$)', content, re.DOTALL)
            if error_match:
                expected_error = error_match.group(1).strip()
            
        except Exception as e:
            print(f"Error reading test file {filepath}: {e}")
        
        return expected_output, expected_error
    
    def _run_test(self, filepath: Path) -> TestResult:
        """
        Run a single test file.
        
        Args:
            filepath: Path to test file
            
        Returns:
            TestResult object
        """
        expected_output, expected_error = self._parse_test_file(filepath)
        
        try:
            # Run the REAPER interpreter
            result = subprocess.run(
                [sys.executable, "reaper.py", str(filepath)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            actual_output = result.stdout.strip()
            actual_error = result.stderr.strip()
            
            # Determine if test passed
            if expected_error:
                # Test expects an error
                if result.returncode != 0 and expected_error.lower() in actual_error.lower():
                    return TestResult(
                        filename=filepath.name,
                        passed=True,
                        expected=f"ERROR: {expected_error}",
                        actual=f"ERROR: {actual_error}",
                        error_type=expected_error
                    )
                else:
                    return TestResult(
                        filename=filepath.name,
                        passed=False,
                        expected=f"ERROR: {expected_error}",
                        actual=f"OUTPUT: {actual_output}\nERROR: {actual_error}",
                        error_type=expected_error,
                        error_message=actual_error
                    )
            else:
                # Test expects normal output
                if result.returncode == 0 and actual_output == expected_output:
                    return TestResult(
                        filename=filepath.name,
                        passed=True,
                        expected=expected_output or "",
                        actual=actual_output
                    )
                else:
                    return TestResult(
                        filename=filepath.name,
                        passed=False,
                        expected=expected_output or "",
                        actual=actual_output,
                        error_message=actual_error if result.returncode != 0 else None
                    )
        
        except subprocess.TimeoutExpired:
            return TestResult(
                filename=filepath.name,
                passed=False,
                expected=expected_output or f"ERROR: {expected_error}",
                actual="TIMEOUT: Test exceeded 30 second limit",
                error_message="Timeout"
            )
        except Exception as e:
            return TestResult(
                filename=filepath.name,
                passed=False,
                expected=expected_output or f"ERROR: {expected_error}",
                actual=f"EXCEPTION: {str(e)}",
                error_message=str(e)
            )
    
    def run_all_tests(self) -> None:
        """Run all tests in the test directory."""
        if not self.test_dir.exists():
            print(f"Test directory '{self.test_dir}' not found!")
            return
        
        # Find all .reaper test files
        test_files = list(self.test_dir.glob("*.reaper"))
        
        if not test_files:
            print(f"No .reaper test files found in '{self.test_dir}'!")
            return
        
        print(f"Running {len(test_files)} tests...")
        print()
        
        # Run each test
        for test_file in sorted(test_files):
            print(f"Testing {test_file.name}...", end=" ")
            result = self._run_test(test_file)
            self.results.append(result)
            
            if result.passed:
                print(self._colorize("PASS", "green"))
            else:
                print(self._colorize("FAIL", "red"))
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self) -> None:
        """Print test summary."""
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        
        print()
        print("=" * 60)
        print(f"Test Summary: {passed} passed, {failed} failed, {len(self.results)} total")
        print("=" * 60)
        
        if failed > 0:
            print()
            print(self._colorize("Failed Tests:", "red"))
            print("-" * 40)
            
            for result in self.results:
                if not result.passed:
                    print(f"\n{self._colorize(result.filename, 'bold')}:")
                    print(f"  Expected: {result.expected}")
                    print(f"  Actual:   {result.actual}")
                    if result.error_message:
                        print(f"  Error:    {result.error_message}")
        
        # Overall result
        if failed == 0:
            print()
            print(self._colorize("SUCCESS: All tests passed! The REAPER language is working correctly.", "green"))
            sys.exit(0)
        else:
            print()
            print(self._colorize(f"FAILED: {failed} test(s) failed. Please check the implementation.", "red"))
            sys.exit(1)


def main():
    """Main entry point for test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run REAPER language tests")
    parser.add_argument(
        "--test-dir",
        default="test_examples",
        help="Directory containing test files (default: test_examples)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output for each test"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(args.test_dir)
    runner.run_all_tests()


if __name__ == "__main__":
    main()
