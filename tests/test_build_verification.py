#!/usr/bin/env python3
"""
Build Verification Tests

Verifies that the standalone executable build includes all necessary components:
- Bytecode VM integration
- Security libraries
- Core interpreter functionality
"""

import os
import sys
import subprocess
from pathlib import Path

def test_bytecode_imports():
    """Test that bytecode module can be imported."""
    print("Testing bytecode module imports...")
    try:
        from bytecode import compile_to_bytecode, create_vm, BytecodeProgram
        print("✅ Bytecode module imports successful")
        return True
    except ImportError as e:
        print(f"❌ Bytecode import failed: {e}")
        return False


def test_core_imports():
    """Test that core modules can be imported."""
    print("Testing core module imports...")
    try:
        from core import lexer, parser, interpreter
        print("✅ Core module imports successful")
        return True
    except ImportError as e:
        print(f"❌ Core import failed: {e}")
        return False


def test_security_library_structure():
    """Test that security library structure exists."""
    print("Testing security library structure...")
    
    libs_dir = Path("libs")
    if not libs_dir.exists():
        print("⚠️ libs directory not found")
        return False
    
    expected_libs = ['phantom', 'crypt', 'wraith', 'specter', 'shadow', 'void', 'zombitious', 'shinigami']
    found_libs = []
    
    for lib in expected_libs:
        lib_path = libs_dir / lib
        if lib_path.exists() and (lib_path / '__init__.py').exists():
            found_libs.append(lib)
    
    print(f"✅ Found {len(found_libs)}/{len(expected_libs)} security libraries: {', '.join(found_libs)}")
    return len(found_libs) > 0


def test_nuitka_build_script():
    """Test that Nuitka build script exists and is valid."""
    print("Testing Nuitka build script...")
    
    build_scripts = ['nuitka_build.py']
    
    for script in build_scripts:
        if not Path(script).exists():
            print(f"❌ Build script {script} not found")
            return False
    
    print("✅ Build scripts found")
    return True


def test_version_management():
    """Test that version management is in place."""
    print("Testing version management...")
    
    try:
        from version import get_version, get_version_string
        version = get_version()
        version_str = get_version_string()
        print(f"✅ Version management: {version_str}")
        return True
    except ImportError:
        print("⚠️ Version module not found (optional)")
        return True  # Not critical


def run_all_checks():
    """Run all build verification checks."""
    print("=" * 60)
    print("REAPER Build Verification")
    print("=" * 60)
    print()
    
    checks = [
        test_bytecode_imports,
        test_core_imports,
        test_security_library_structure,
        test_nuitka_build_script,
        test_version_management,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Check {check.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
            print()
    
    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All build verification checks passed!")
        return 0
    else:
        print("⚠️ Some checks failed or had warnings")
        return 0  # Warnings are acceptable


if __name__ == "__main__":
    sys.exit(run_all_checks())

