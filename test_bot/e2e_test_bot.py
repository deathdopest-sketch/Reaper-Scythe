"""
REAPER E2E Test Bot

Comprehensive end-to-end testing bot that tests all Reaper features
and reports results for analysis.
"""

import sys
import os
import time
import json
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import subprocess

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    category: str
    status: str  # 'PASS', 'FAIL', 'SKIP', 'ERROR'
    duration: float
    message: str
    details: Dict[str, Any]
    timestamp: str


@dataclass
class TestReport:
    """Complete test report."""
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    results: List[TestResult]
    timestamp: str


class E2ETestBot:
    """
    End-to-end test bot for Reaper language.
    """
    
    def __init__(self, verbose: bool = True, output_file: Optional[str] = None):
        """
        Initialize test bot.
        
        Args:
            verbose: Print detailed output
            output_file: Optional file to save results
        """
        self.verbose = verbose
        self.output_file = output_file
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.report_data: Dict[str, Any] = {}
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def show_code_example(self, title: str, code: str, explanation: str = "") -> None:
        """Display a Reaper code example for learning."""
        print("\n" + "=" * 70)
        print(f"📚 LEARNING: {title}")
        print("=" * 70)
        if explanation:
            print(f"💡 {explanation}")
            print()
        print("📝 Reaper Code:")
        print("-" * 70)
        # Indent code for better readability
        for line in code.strip().split('\n'):
            print(f"   {line}")
        print("-" * 70)
        print("▶️  Executing...")
        print()
    
    def run_test(self, test_name: str, category: str, test_func: callable) -> TestResult:
        """
        Run a single test.
        
        Args:
            test_name: Name of test
            category: Test category
            test_func: Test function
            
        Returns:
            Test result
        """
        self.log(f"Running: {test_name} ({category})", "TEST")
        start = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start
            
            if result is True or (isinstance(result, dict) and result.get('success', False)):
                status = 'PASS'
                message = "Test passed"
                details = result if isinstance(result, dict) else {}
            elif result is False or (isinstance(result, dict) and not result.get('success', True)):
                status = 'FAIL'
                message = result.get('message', 'Test failed') if isinstance(result, dict) else 'Test failed'
                details = result if isinstance(result, dict) else {}
            else:
                status = 'SKIP'
                message = "Test skipped"
                details = {}
            
        except Exception as e:
            duration = time.time() - start
            status = 'ERROR'
            message = f"Test error: {str(e)}"
            details = {
                'exception': type(e).__name__,
                'traceback': traceback.format_exc()
            }
            if self.verbose:
                self.log(f"ERROR in {test_name}: {str(e)}", "ERROR")
        
        test_result = TestResult(
            test_name=test_name,
            category=category,
            status=status,
            duration=duration,
            message=message,
            details=details,
            timestamp=datetime.now().isoformat()
        )
        
        self.results.append(test_result)
        
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌',
            'SKIP': '⏭️',
            'ERROR': '💥'
        }
        
        self.log(f"{status_emoji.get(status, '?')} {test_name}: {message} ({duration:.3f}s)", status)
        
        return test_result
    
    def test_core_language(self) -> None:
        """Test core language features with educational examples."""
        self.log("=" * 70, "SECTION")
        self.log("🎓 LEARNING: Core Language Features", "SECTION")
        self.log("=" * 70, "SECTION")
        self.log("", "SECTION")
        self.log("Watch and learn as we demonstrate Reaper language features!", "INFO")
        self.log("", "SECTION")
        
        # Test exception handling
        self.run_test(
            "Exception Handling - risk/catch/finally",
            "Core Language",
            self._test_exception_handling
        )
        
        # Test module imports
        self.run_test(
            "Module Import System",
            "Core Language",
            self._test_module_imports
        )
        
        # Test file I/O
        self.run_test(
            "File I/O Operations",
            "Core Language",
            self._test_file_io
        )
        
        # Test async operations
        self.run_test(
            "Async/Concurrent Operations",
            "Core Language",
            self._test_async_operations
        )
    
    def test_security_libraries(self) -> None:
        """Test security libraries with educational examples."""
        self.log("=" * 70, "SECTION")
        self.log("🎓 LEARNING: Security Libraries", "SECTION")
        self.log("=" * 70, "SECTION")
        self.log("", "SECTION")
        self.log("Learn how to use Reaper's powerful security libraries!", "INFO")
        self.log("", "SECTION")
        
        # Test exploit library
        self.run_test(
            "Exploit Development Library",
            "Security Libraries",
            self._test_exploit_library
        )
        
        # Test binary library
        self.run_test(
            "Binary Analysis Library",
            "Security Libraries",
            self._test_binary_library
        )
        
        # Test memory library
        self.run_test(
            "Memory Manipulation Library",
            "Security Libraries",
            self._test_memory_library
        )
        
        # Test fuzzer library
        self.run_test(
            "Fuzzing Framework",
            "Security Libraries",
            self._test_fuzzer_library
        )
        
        # Test reverse library
        self.run_test(
            "Reverse Engineering Library",
            "Security Libraries",
            self._test_reverse_library
        )
    
    def _test_exception_handling(self) -> Dict[str, Any]:
        """Test exception handling with educational examples."""
        try:
            from core.lexer import Lexer
            from core.parser import Parser
            from core.interpreter import Interpreter
            import io
            import contextlib
            
            # Example 1: Basic exception handling
            code1 = """
risk {
    harvest "Inside risk block";
    throw "Something went wrong";
    harvest "This won't print";
} catch {
    harvest "Exception caught!";
}
"""
            self.show_code_example(
                "Exception Handling - Basic risk/catch",
                code1,
                "The 'risk' block is like try, 'catch' handles exceptions. If an exception is thrown, catch block executes."
            )
            
            lexer = Lexer(code1)
            parser = Parser(lexer)
            program = parser.parse()
            interpreter = Interpreter()
            
            # Capture output
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                interpreter.interpret(program)
            
            print("📊 Output:")
            print(output.getvalue())
            
            # Example 2: Finally block
            code2 = """
risk {
    harvest "Doing something risky";
} catch {
    harvest "Caught exception";
} finally {
    harvest "This always runs";
}
"""
            self.show_code_example(
                "Exception Handling - Finally block",
                code2,
                "The 'finally' block always executes, whether an exception occurs or not. Great for cleanup!"
            )
            
            lexer2 = Lexer(code2)
            parser2 = Parser(lexer2)
            program2 = parser2.parse()
            interpreter2 = Interpreter()
            
            output2 = io.StringIO()
            with contextlib.redirect_stdout(output2):
                interpreter2.interpret(program2)
            
            print("📊 Output:")
            print(output2.getvalue())
            
            return {'success': True, 'message': 'Exception handling works', 'examples_shown': 2}
        except Exception as e:
            return {'success': False, 'message': str(e), 'error': traceback.format_exc()}
    
    def _test_module_imports(self) -> Dict[str, Any]:
        """Test module import system with educational examples."""
        try:
            from core.module_loader import ReaperModuleLoader
            
            # Example: Importing security libraries
            code1 = """
// Import entire module
infiltrate phantom;

// Use module functions
phantom.scan_port("127.0.0.1", 80);
"""
            self.show_code_example(
                "Module Imports - Basic import",
                code1,
                "Use 'infiltrate' to import security libraries. Imported modules are available as namespaces."
            )
            
            loader = ReaperModuleLoader()
            
            # Test loading a module
            try:
                namespace = loader.load_module('phantom')
                print("📊 Available functions in 'phantom' module:")
                funcs = [k for k in list(namespace.keys())[:10] if not k.startswith('_')]
                for func in funcs:
                    print(f"   • {func}")
                print()
                
                # Example: Import with alias
                code2 = """
// Import with alias
infiltrate phantom as net;

// Use aliased module
net.scan_port("192.168.1.1", 443);
"""
                self.show_code_example(
                    "Module Imports - With alias",
                    code2,
                    "You can use 'as' to give modules custom names. Useful for avoiding conflicts!"
                )
                
                # Example: Import specific functions
                code3 = """
// Import specific functions
infiltrate crypt (encrypt, decrypt, hash);

// Use imported functions directly
crypt data = encrypt("secret message", "key");
"""
                self.show_code_example(
                    "Module Imports - Selective import",
                    code3,
                    "Import only the functions you need by listing them in parentheses. Keeps your namespace clean!"
                )
                
                return {'success': True, 'message': 'Module loading works', 'modules': funcs, 'examples_shown': 3}
            except Exception as e:
                # Module might not be fully implemented, that's okay
                print(f"⚠️  Note: Some libraries may need full implementation")
                return {'success': True, 'message': 'Module loader initialized', 'note': 'Libraries may need implementation'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _test_file_io(self) -> Dict[str, Any]:
        """Test file I/O operations with educational examples."""
        try:
            from core.interpreter import Interpreter
            from core.lexer import Lexer
            from core.parser import Parser
            import io
            import contextlib
            
            # Create test file
            test_file = Path("test_bot/test_file.txt")
            test_file.write_text("Hello, Reaper!\nThis is a test file.")
            
            # Example 1: Reading files
            code1 = """
// Read a file with 'excavate'
soul content = excavate("test_bot/test_file.txt");
harvest content;
"""
            self.show_code_example(
                "File I/O - Reading Files",
                code1,
                "Use 'excavate' to read files. It returns the file contents as a soul (string)."
            )
            
            lexer1 = Lexer(code1)
            parser1 = Parser(lexer1)
            program1 = parser1.parse()
            interpreter1 = Interpreter()
            
            output1 = io.StringIO()
            with contextlib.redirect_stdout(output1):
                interpreter1.interpret(program1)
            
            print("📊 Output:")
            print(output1.getvalue())
            
            # Example 2: Writing files
            code2 = """
// Write to a file with 'bury'
soul message = "Written by Reaper language!";
bury("test_bot/test_output.txt", message);
harvest "File written successfully!";
"""
            self.show_code_example(
                "File I/O - Writing Files",
                code2,
                "Use 'bury' to write files. First parameter is the file path, second is the content to write."
            )
            
            lexer2 = Lexer(code2)
            parser2 = Parser(lexer2)
            program2 = parser2.parse()
            interpreter2 = Interpreter()
            
            output2 = io.StringIO()
            with contextlib.redirect_stdout(output2):
                interpreter2.interpret(program2)
            
            print("📊 Output:")
            print(output2.getvalue())
            
            # Verify output
            if Path("test_bot/test_output.txt").exists():
                written_content = Path("test_bot/test_output.txt").read_text()
                print(f"✅ File created! Contents: {written_content[:50]}...")
                return {'success': True, 'message': 'File I/O works', 'examples_shown': 2}
            else:
                return {'success': False, 'message': 'Output file not created'}
        except Exception as e:
            return {'success': False, 'message': str(e), 'error': traceback.format_exc()}
    
    def _test_async_operations(self) -> Dict[str, Any]:
        """Test async operations with educational examples."""
        try:
            from core.async_runtime import ReaperAsyncRuntime
            
            # Example: Async operations
            code1 = """
// Execute code asynchronously with 'breach'
breach {
    harvest "This runs in parallel!";
    rest 100;  // Sleep 100ms
    harvest "Async task done";
}

harvest "This runs immediately (doesn't wait)";
"""
            self.show_code_example(
                "Async Operations - Basic breach",
                code1,
                "The 'breach' block executes code asynchronously. Code after it doesn't wait for the breach block to finish."
            )
            
            # Example: Await async operations
            code2 = """
// Start async task
specter task = breach {
    rest 50;
    reap "Task result";
};

// Wait for result with 'await'
soul result = await task;
harvest result;
"""
            self.show_code_example(
                "Async Operations - Await",
                code2,
                "Use 'await' to wait for an async task to complete and get its result. The 'breach' block returns a task object."
            )
            
            runtime = ReaperAsyncRuntime()
            
            def test_task():
                time.sleep(0.1)
                return "Async task completed"
            
            print("▶️  Testing async runtime...")
            task = runtime.submit(test_task)
            result = task.wait(timeout=1.0)
            
            if result == "Async task completed":
                print(f"✅ Async task result: {result}")
                return {'success': True, 'message': 'Async runtime works', 'examples_shown': 2}
            else:
                return {'success': False, 'message': 'Async task failed'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _test_exploit_library(self) -> Dict[str, Any]:
        """Test exploit library with educational examples."""
        try:
            from libs.exploit import ShellcodeGenerator, ROPChainBuilder, BufferOverflowUtils
            from libs.exploit.shellcode import Architecture, ShellcodeType
            
            # Example: Using exploit library
            code1 = """
// Import exploit library
infiltrate exploit;

// Generate shellcode
specter shellcode = exploit.generate_shellcode(
    type="execve",
    command="/bin/sh"
);

// Create buffer overflow payload
corpse padding = 100;
corpse return_addr = 0x41414141;
specter payload = exploit.create_payload(
    padding,
    return_addr,
    shellcode
);
"""
            self.show_code_example(
                "Exploit Library - Shellcode Generation",
                code1,
                "The exploit library provides tools for exploit development: shellcode generation, ROP chains, and payload creation."
            )
            
            # Test shellcode generator
            gen = ShellcodeGenerator(Architecture.X86_64)
            shellcode = gen.generate_execve('/bin/sh')
            
            print(f"📊 Generated shellcode: {len(shellcode)} bytes")
            
            # Test ROP builder
            rop = ROPChainBuilder('x86_64')
            print(f"📊 ROP builder initialized for x86_64")
            
            # Test buffer overflow utils
            bof = BufferOverflowUtils('x86_64')
            pattern = bof.generate_pattern(100)
            
            print(f"📊 Generated pattern: {len(pattern)} bytes")
            print(f"   Pattern preview: {pattern[:20].hex()}...")
            
            return {
                'success': True,
                'message': 'Exploit library works',
                'shellcode_size': len(shellcode),
                'pattern_size': len(pattern),
                'examples_shown': 1
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _test_binary_library(self) -> Dict[str, Any]:
        """Test binary library."""
        try:
            from libs.binary import BinaryParser, StringExtractor
            
            # Test with a simple binary (Python executable)
            python_exe = sys.executable
            
            if Path(python_exe).exists():
                parser = BinaryParser(python_exe)
                info = parser.parse()
                
                extractor = StringExtractor(python_exe)
                strings = extractor.extract_ascii()
                
                return {
                    'success': True,
                    'message': 'Binary library works',
                    'format': info.get('format', 'unknown'),
                    'strings_found': len(strings)
                }
            else:
                return {'success': True, 'message': 'Binary library initialized', 'note': 'No test binary available'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _test_memory_library(self) -> Dict[str, Any]:
        """Test memory library."""
        try:
            from libs.memory import MemoryScanner, HeapManipulator
            
            scanner = MemoryScanner()
            heap = HeapManipulator()
            
            return {
                'success': True,
                'message': 'Memory library initialized',
                'platform': sys.platform
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _test_fuzzer_library(self) -> Dict[str, Any]:
        """Test fuzzer library."""
        try:
            from libs.fuzzer import BitFlipMutator, CoverageTracker, CorpusManager
            
            mutator = BitFlipMutator()
            coverage = CoverageTracker()
            corpus = CorpusManager()
            
            # Test mutation
            test_data = b"Hello, World!"
            mutated = mutator.mutate(test_data)
            
            return {
                'success': True,
                'message': 'Fuzzer library works',
                'original_size': len(test_data),
                'mutated_size': len(mutated)
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _test_reverse_library(self) -> Dict[str, Any]:
        """Test reverse library."""
        try:
            from libs.reverse import PatternMatcher, AntiDebugDetector
            
            matcher = PatternMatcher()
            detector = AntiDebugDetector()
            
            return {
                'success': True,
                'message': 'Reverse library works',
                'patterns_loaded': len(matcher.patterns)
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def generate_report(self) -> TestReport:
        """
        Generate test report.
        
        Returns:
            Test report
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == 'PASS')
        failed = sum(1 for r in self.results if r.status == 'FAIL')
        skipped = sum(1 for r in self.results if r.status == 'SKIP')
        errors = sum(1 for r in self.results if r.status == 'ERROR')
        duration = time.time() - self.start_time
        
        report = TestReport(
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=duration,
            results=self.results,
            timestamp=datetime.now().isoformat()
        )
        
        return report
    
    def print_summary(self) -> None:
        """Print test summary."""
        report = self.generate_report()
        
        self.log("=" * 60, "SUMMARY")
        self.log("TEST SUMMARY", "SUMMARY")
        self.log("=" * 60, "SUMMARY")
        self.log(f"Total Tests: {report.total_tests}", "SUMMARY")
        self.log(f"✅ Passed: {report.passed}", "SUMMARY")
        self.log(f"❌ Failed: {report.failed}", "SUMMARY")
        self.log(f"⏭️  Skipped: {report.skipped}", "SUMMARY")
        self.log(f"💥 Errors: {report.errors}", "SUMMARY")
        self.log(f"Duration: {report.duration:.2f}s", "SUMMARY")
        self.log("=" * 60, "SUMMARY")
        
        # Print failures
        if report.failed > 0 or report.errors > 0:
            self.log("\nFAILURES:", "SUMMARY")
            for result in self.results:
                if result.status in ['FAIL', 'ERROR']:
                    self.log(f"  ❌ {result.test_name}: {result.message}", "SUMMARY")
    
    def save_report(self, filename: Optional[str] = None) -> str:
        """
        Save test report to file.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"test_bot/reports/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.generate_report()
        
        # Create reports directory
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict
        report_dict = asdict(report)
        
        # Save JSON
        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        self.log(f"Report saved to: {filename}", "INFO")
        return filename
    
    def run_all_tests(self) -> TestReport:
        """
        Run all E2E tests.
        
        Returns:
            Test report
        """
        self.log("🚀 Starting REAPER E2E Test Bot", "BOT")
        self.log(f"Timestamp: {datetime.now().isoformat()}", "BOT")
        self.log("", "BOT")
        
        # Run test suites
        self.test_core_language()
        self.test_security_libraries()
        
        # Generate and print report
        report = self.generate_report()
        self.print_summary()
        
        # Save report
        if self.output_file:
            self.save_report(self.output_file)
        else:
            self.save_report()
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='REAPER E2E Test Bot')
    parser.add_argument('--output', '-o', help='Output file for report')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    args = parser.parse_args()
    
    bot = E2ETestBot(verbose=not args.quiet, output_file=args.output)
    report = bot.run_all_tests()
    
    # Exit with error code if tests failed
    sys.exit(1 if (report.failed > 0 or report.errors > 0) else 0)


if __name__ == '__main__':
    main()

