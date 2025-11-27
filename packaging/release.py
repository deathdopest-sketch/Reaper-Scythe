"""
Release Packaging Script

Creates release packages for distribution on all platforms.
Combines building, signing, and installer generation.
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from .version import get_version, get_version_string
from .installers import create_installer
from .signing import sign_executable


class ReleasePackager:
    """Create release packages for distribution."""
    
    def __init__(self, dist_dir: str = "dist", build_dir: str = "build"):
        self.dist_dir = Path(dist_dir)
        self.build_dir = Path(build_dir)
        self.version = get_version()
        self.platform = platform.system()
        
    def build_executable(self) -> Path:
        """Build the executable using Nuitka."""
        print("=" * 60)
        print("Building Reaper executable...")
        print("=" * 60)
        
        # Import and run the build script
        build_script = Path("nuitka_build.py")
        if not build_script.exists():
            raise FileNotFoundError("nuitka_build.py not found")
        
        result = subprocess.run(
            [sys.executable, str(build_script)],
            check=False
        )
        
        if result.returncode != 0:
            raise RuntimeError("Build failed")
        
        # Find the built executable
        if self.platform == "Windows":
            exe_path = self.dist_dir / "reaper.exe"
        elif self.platform == "Darwin":
            exe_path = self.dist_dir / "reaper.app"
        else:
            exe_path = self.dist_dir / "reaper"
        
        if not exe_path.exists():
            raise FileNotFoundError(f"Executable not found: {exe_path}")
        
        print(f"✅ Executable built: {exe_path}")
        return exe_path
    
    def sign_executable(self, exe_path: Path) -> bool:
        """Sign the executable (if certificates are available)."""
        print("=" * 60)
        print("Code signing...")
        print("=" * 60)
        
        cert_path = os.environ.get("WINDOWS_CERT_PATH") if self.platform == "Windows" else None
        cert_password = os.environ.get("WINDOWS_CERT_PASSWORD") if self.platform == "Windows" else None
        
        if self.platform == "Windows" and not cert_path:
            print("ℹ️  Skipping code signing (certificate not configured)")
            return True
        
        if self.platform == "Darwin" and not os.environ.get("APPLE_DEVELOPER_ID"):
            print("ℹ️  Skipping code signing (Apple Developer ID not configured)")
            return True
        
        return sign_executable(exe_path, cert_path=cert_path)
    
    def create_installer(self, exe_path: Path) -> Path:
        """Create installer package."""
        print("=" * 60)
        print("Creating installer package...")
        print("=" * 60)
        
        try:
            installer_path = create_installer(self.platform)
            print(f"✅ Installer created: {installer_path}")
            return installer_path
        except Exception as e:
            print(f"⚠️  Installer creation skipped: {e}")
            print("   (This is optional - executable can be distributed without installer)")
            return exe_path
    
    def create_checksums(self, files: List[Path]) -> Dict[Path, str]:
        """Create checksums for release files."""
        print("=" * 60)
        print("Creating checksums...")
        print("=" * 60)
        
        checksums = {}
        
        for file_path in files:
            if not file_path.exists():
                continue
            
            # Use SHA256 for checksums
            try:
                import hashlib
                sha256 = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)
                
                checksum = sha256.hexdigest()
                checksums[file_path] = checksum
                
                # Write checksum file
                checksum_file = file_path.with_suffix(file_path.suffix + ".sha256")
                with open(checksum_file, 'w') as f:
                    f.write(f"{checksum}  {file_path.name}\n")
                
                print(f"✅ {file_path.name}: {checksum[:16]}...")
            except Exception as e:
                print(f"⚠️  Failed to create checksum for {file_path.name}: {e}")
        
        return checksums
    
    def create_release_notes(self, output_dir: Path) -> Path:
        """Create release notes file."""
        notes_content = f"""# Reaper Language v{self.version} Release Notes

Release Date: {datetime.now().strftime('%Y-%m-%d')}
Platform: {self.platform}

## Installation

### Windows
1. Run the installer: `reaper-setup-{self.version}.exe`
2. Follow the installation wizard
3. Reaper will be installed to `C:\\Program Files\\Reaper`

### macOS
1. Open `reaper-{self.version}-macos.dmg`
2. Drag Reaper.app to Applications folder
3. Open Applications and run Reaper.app

### Linux
1. Make AppImage executable: `chmod +x reaper-{self.version}-linux.AppImage`
2. Run: `./reaper-{self.version}-linux.AppImage`

## Usage

Run Reaper scripts:
```
reaper script.reaper
```

Interactive REPL:
```
reaper
```

Get help:
```
reaper --help
```

## What's New

See CHANGELOG.md for detailed changes.

## Security Libraries

Reaper includes the following security libraries:
- `phantom`: Network operations (scanning, packet crafting, DNS)
- `crypt`: Cryptography (encryption, hashing, steganography)
- `wraith`: System operations (files, processes, memory)
- `specter`: Web operations (HTTP, scraping, injection testing)
- `shadow`: Anonymity features (Tor, VPN, MAC spoofing)

## Documentation

Full documentation available at:
https://github.com/reaper-lang/reaper/docs

## Support

Report issues at:
https://github.com/reaper-lang/reaper/issues

## Legal

This software is for educational and authorized security testing purposes only.
Unauthorized use is prohibited and may violate laws.
"""
        
        notes_file = output_dir / f"RELEASE_NOTES_v{self.version}.md"
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write(notes_content)
        
        print(f"✅ Release notes created: {notes_file}")
        return notes_file
    
    def package_release(self, sign: bool = True, create_installer_pkg: bool = True) -> Dict:
        """Create complete release package."""
        print("\n" + "=" * 60)
        print(f"Packaging Reaper v{self.version} for {self.platform}")
        print("=" * 60 + "\n")
        
        results = {
            "executable": None,
            "installer": None,
            "checksums": {},
            "release_notes": None,
            "success": False
        }
        
        try:
            # Step 1: Build executable
            exe_path = self.build_executable()
            results["executable"] = exe_path
            
            # Step 2: Sign executable (optional)
            if sign:
                self.sign_executable(exe_path)
            
            # Step 3: Create installer (optional)
            if create_installer_pkg:
                try:
                    installer_path = self.create_installer(exe_path)
                    results["installer"] = installer_path
                except Exception as e:
                    print(f"⚠️  Installer creation failed: {e}")
            
            # Step 4: Create checksums
            files_to_hash = [exe_path]
            if results["installer"]:
                files_to_hash.append(results["installer"])
            results["checksums"] = self.create_checksums(files_to_hash)
            
            # Step 5: Create release notes
            results["release_notes"] = self.create_release_notes(self.dist_dir)
            
            results["success"] = True
            
            print("\n" + "=" * 60)
            print("✅ Release package created successfully!")
            print("=" * 60)
            print(f"\nRelease files in: {self.dist_dir}")
            print(f"  - Executable: {exe_path.name}")
            if results["installer"]:
                print(f"  - Installer: {results['installer'].name}")
            print(f"  - Release notes: {results['release_notes'].name}")
            print(f"  - Checksums: *.sha256 files\n")
            
        except Exception as e:
            print(f"\n❌ Release packaging failed: {e}")
            results["error"] = str(e)
        
        return results


def main():
    """Main entry point for release packaging."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create release package for Reaper")
    parser.add_argument("--no-sign", action="store_true", help="Skip code signing")
    parser.add_argument("--no-installer", action="store_true", help="Skip installer creation")
    
    args = parser.parse_args()
    
    packager = ReleasePackager()
    results = packager.package_release(
        sign=not args.no_sign,
        create_installer_pkg=not args.no_installer
    )
    
    if not results["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()

