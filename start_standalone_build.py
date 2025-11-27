#!/usr/bin/env python3
"""
REAPER Standalone Build - Quick Start Script

This script helps you get started with the standalone build process.
It checks prerequisites and guides you through the first steps.
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🎯 REAPER STANDALONE BUILD - QUICK START")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("1. Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_nuitka():
    """Check if Nuitka is installed."""
    print("\n2. Checking Nuitka installation...")
    try:
        result = subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ Nuitka {version} - Installed")
            return True
        else:
            print("   ❌ Nuitka not found - Run: pip install nuitka")
            return False
    except Exception as e:
        print(f"   ❌ Error checking Nuitka: {e}")
        return False

def check_build_tools():
    """Check platform-specific build tools."""
    print("\n3. Checking build tools...")
    system = platform.system().lower()
    
    if system == "windows":
        print("   Windows detected - Checking for Visual Studio Build Tools...")
        # Check for Visual Studio Build Tools
        vs_paths = [
            r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools",
            r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools",
            r"C:\Program Files\Microsoft Visual Studio\2019\BuildTools",
            r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools"
        ]
        
        found = False
        for path in vs_paths:
            if os.path.exists(path):
                print(f"   ✅ Visual Studio Build Tools found at {path}")
                found = True
                break
        
        if not found:
            print("   ⚠️  Visual Studio Build Tools not found")
            print("   Install from: https://visualstudio.microsoft.com/downloads/")
            return False
            
    elif system == "linux":
        print("   Linux detected - Checking for build-essential...")
        try:
            result = subprocess.run(["gcc", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ GCC found - build-essential installed")
                return True
            else:
                print("   ❌ GCC not found - Run: sudo apt install build-essential")
                return False
        except FileNotFoundError:
            print("   ❌ GCC not found - Run: sudo apt install build-essential")
            return False
            
    elif system == "darwin":
        print("   macOS detected - Checking for Xcode Command Line Tools...")
        try:
            result = subprocess.run(["xcode-select", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ Xcode Command Line Tools found")
                return True
            else:
                print("   ❌ Xcode Command Line Tools not found")
                print("   Run: xcode-select --install")
                return False
        except FileNotFoundError:
            print("   ❌ Xcode Command Line Tools not found")
            print("   Run: xcode-select --install")
            return False
    
    return True

def check_disk_space():
    """Check available disk space."""
    print("\n4. Checking disk space...")
    try:
        if platform.system().lower() == "windows":
            import shutil
            total, used, free = shutil.disk_usage("C:\\")
        else:
            import shutil
            total, used, free = shutil.disk_usage("/")
        
        free_gb = free // (1024**3)
        if free_gb >= 10:
            print(f"   ✅ {free_gb} GB free space - Sufficient")
            return True
        else:
            print(f"   ⚠️  {free_gb} GB free space - May need more space")
            return False
    except Exception as e:
        print(f"   ⚠️  Could not check disk space: {e}")
        return True

def create_build_structure():
    """Create the build directory structure."""
    print("\n5. Creating build directory structure...")
    
    build_dirs = [
        "build",
        "build/windows",
        "build/linux", 
        "build/macos",
        "build/dist",
        "build/temp",
        "build/logs"
    ]
    
    for dir_path in build_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created {dir_path}/")
    
    return True

def create_requirements_build():
    """Create requirements-build.txt file."""
    print("\n6. Creating requirements-build.txt...")
    
    requirements = """# REAPER Standalone Build Requirements
# Core dependencies
nuitka>=1.8.0

# UI libraries (for Necronomicon)
rich>=13.0.0

# AI model support (optional, for local AI models)
# Install Ollama separately: https://ollama.ai
# ollama>=0.1.0  # Uncomment if using Ollama Python client

# Build tools
setuptools>=65.0.0
wheel>=0.40.0

# Platform-specific dependencies
# Windows
pywin32>=306; sys_platform == "win32"

# Linux
# No additional dependencies

# macOS
# No additional dependencies
"""
    
    with open("requirements-build.txt", "w") as f:
        f.write(requirements)
    
    print("   ✅ Created requirements-build.txt")
    return True

def create_build_script():
    """Create the main build script."""
    print("\n7. Creating build.py script...")
    
    build_script = '''#!/usr/bin/env python3
"""
REAPER Standalone Build Script

This script builds standalone executables for Windows, Linux, and macOS.
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def main():
    """Main build function."""
    print("🎯 REAPER Standalone Build Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("core/reaper.py").exists():
        print("❌ Error: Must be run from REAPER project root")
        return 1
    
    # Get platform
    system = platform.system().lower()
    print(f"Building for: {system}")
    
    # Build command
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--output-dir=build",
        "--output-filename=reaper",
        "--enable-plugin=rich",
        "--include-package=core",
        "--include-package=bytecode", 
        "--include-package=stdlib",
        "--include-package=libs",
        "reaper_main.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ Build completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open("build.py", "w") as f:
        f.write(build_script)
    
    # Make it executable on Unix systems
    if platform.system().lower() != "windows":
        os.chmod("build.py", 0o755)
    
    print("   ✅ Created build.py")
    return True

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Install build requirements:")
    print("   pip install -r requirements-build.txt")
    print()
    print("2. Start with Layer 1, Task 1:")
    print("   Read REAPER_STANDALONE_BUILD_PLAN.md")
    print("   Begin L1-T001: Build Environment Setup")
    print()
    print("3. Test the build script:")
    print("   python build.py")
    print()
    print("4. Follow the plan systematically:")
    print("   - Complete each layer in order")
    print("   - Create checkpoints regularly")
    print("   - Update state files")
    print("   - Celebrate milestones!")
    print()
    print("📚 Documentation:")
    print("- REAPER_STANDALONE_BUILD_PLAN.md - Complete plan")
    print("- STANDALONE_BUILD_STATE.md - Current status")
    print("- STANDALONE_TASK_QUEUE.md - All tasks")
    print("- STANDALONE_ISSUES_LOG.md - Issues tracking")
    print("- STANDALONE_DECISIONS_LOG.md - Decision log")
    print()
    print("🚀 Ready to build the ultimate standalone hacking language!")
    print()

def main():
    """Main function."""
    print_header()
    
    # Check prerequisites
    checks = [
        check_python_version(),
        check_nuitka(),
        check_build_tools(),
        check_disk_space()
    ]
    
    if not all(checks):
        print("\n❌ Some prerequisites are missing. Please install them and try again.")
        return 1
    
    # Create build structure
    create_build_structure()
    create_requirements_build()
    create_build_script()
    
    print_next_steps()
    return 0

if __name__ == "__main__":
    sys.exit(main())
