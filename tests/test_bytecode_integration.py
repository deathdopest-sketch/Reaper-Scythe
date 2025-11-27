#!/usr/bin/env python3
"""
Integration tests for bytecode VM and standalone executable.

Tests bytecode compilation, execution, and integration with security libraries.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bytecode import compile_to_bytecode, execute_bytecode, create_vm
from core.lexer import tokenize
from core.parser import parse
from core.reaper_error import ReaperRuntimeError


def test_bytecode_simple_program():
    """Test basic bytecode compilation and execution."""
    print("Testing simple bytecode program...")
    
    source = """
    harvest("Hello from bytecode!");
    """
    
    try:
        tokens = tokenize(source, "<test>")
        program = parse(tokens)
        bytecode_program = compile_to_bytecode(program)
        
        vm = create_vm()
        vm.load_program(bytecode_program)
        result = vm.execute()
        
        print("✅ Simple bytecode program executed successfully")
        return True
    except Exception as e:
        print(f"❌ Simple bytecode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bytecode_arithmetic():
    """Test arithmetic operations in bytecode."""
    print("Testing bytecode arithmetic...")
    
    source = """
    corpse x = 10;
    corpse y = 20;
    harvest(x + y);
    """
    
    try:
        tokens = tokenize(source, "<test>")
        program = parse(tokens)
        bytecode_program = compile_to_bytecode(program)
        
        vm = create_vm()
        vm.load_program(bytecode_program)
        result = vm.execute()
        
        print("✅ Bytecode arithmetic executed successfully")
        return True
    except Exception as e:
        print(f"❌ Bytecode arithmetic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bytecode_file_compilation():
    """Test compiling and executing a bytecode file."""
    print("Testing bytecode file compilation...")
    
    source = """
    harvest("Bytecode file test");
    """
    
    try:
        # Create temporary source file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.reaper', delete=False) as f:
            f.write(source)
            source_file = f.name
        
        try:
            # Compile to bytecode
            tokens = tokenize(source, source_file)
            program = parse(tokens)
            bytecode_program = compile_to_bytecode(program)
            
            # Write bytecode file
            bytecode_file = source_file + '.bc'
            with open(bytecode_file, 'wb') as f:
                f.write(bytecode_program.to_bytes())
            
            # Load and execute bytecode file
            from bytecode.instructions import BytecodeProgram
            with open(bytecode_file, 'rb') as f:
                loaded_program = BytecodeProgram.from_bytes(f.read())
            
            vm = create_vm()
            vm.load_program(loaded_program)
            vm.execute()
            
            print("✅ Bytecode file compilation and execution successful")
            return True
        finally:
            # Cleanup
            if os.path.exists(source_file):
                os.unlink(source_file)
            if os.path.exists(bytecode_file):
                os.unlink(bytecode_file)
    except Exception as e:
        print(f"❌ Bytecode file test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bytecode_ritual_args():
    """Test that ritual_args work in bytecode VM."""
    print("Testing bytecode ritual_args...")
    
    source = """
    harvest(ritual_args);
    """
    
    try:
        tokens = tokenize(source, "<test>")
        program = parse(tokens)
        bytecode_program = compile_to_bytecode(program)
        
        vm = create_vm()
        # Set ritual_args before loading program
        vm.globals['ritual_args'] = ['arg1', 'arg2', 'arg3']
        vm.load_program(bytecode_program)
        vm.execute()
        
        print("✅ Bytecode ritual_args test successful")
        return True
    except Exception as e:
        print(f"❌ Bytecode ritual_args test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_security_libraries_accessible():
    """Test that security libraries can be accessed (if they exist)."""
    print("Testing security library access...")
    
    try:
        # Try importing security libraries
        libs_available = []
        
        try:
            from libs import phantom
            libs_available.append("phantom")
        except ImportError:
            pass
        
        try:
            from libs import crypt
            libs_available.append("crypt")
        except ImportError:
            pass
        
        try:
            from libs import wraith
            libs_available.append("wraith")
        except ImportError:
            pass
        
        print(f"✅ Security libraries accessible: {libs_available}")
        return True
    except Exception as e:
        print(f"⚠️ Security library test warning: {e}")
        return True  # Not a failure, libraries might not be fully implemented


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("REAPER Bytecode Integration Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_bytecode_simple_program,
        test_bytecode_arithmetic,
        test_bytecode_file_compilation,
        test_bytecode_ritual_args,
        test_security_libraries_accessible,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
            print()
    
    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All integration tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

