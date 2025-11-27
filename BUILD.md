# Reaper Build System Documentation

This document describes how to build standalone Reaper executables using Nuitka.

## Overview

The Reaper build system uses Nuitka to compile the Python interpreter and all dependencies into a single standalone executable. This creates a binary that can run on the target platform without requiring Python or any external dependencies.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Nuitka (will be installed automatically if missing)
- Platform-specific build tools:
  - **Windows**: Visual C++ Build Tools or Visual Studio
  - **Linux**: gcc, g++ compiler
  - **macOS**: Xcode Command Line Tools

## Quick Start

### Windows

```batch
build.bat
```

### Linux / macOS

```bash
chmod +x build.sh
./build.sh
```

### Manual Build

```bash
python nuitka_build.py
```

## Build Output

After a successful build, the executable will be located in the `dist/` directory:

- **Windows**: `dist/reaper.exe`
- **Linux**: `dist/reaper`
- **macOS**: `dist/reaper.app`

## Build Configuration

### Main Entry Point

The build system uses `reaper_main.py` as the entry point, which wraps the core Reaper interpreter CLI (`core/reaper.py`).

### Included Modules

The build automatically includes:
- `core/` - Core language interpreter (lexer, parser, interpreter, etc.)
- `libs/` - Security libraries (phantom, crypt, wraith, specter, shadow)
- `bytecode/` - Bytecode VM and compiler

### Included Packages

The following Python packages are bundled:
- `cryptography` - Cryptographic operations
- `scapy` - Network packet manipulation
- `requests` - HTTP client
- `PIL` (Pillow) - Image processing
- `numpy` - Numerical operations
- `psutil` - System utilities
- `bs4` (BeautifulSoup) - HTML parsing
- `lxml` - XML/HTML parsing

## Build Options

### Customizing the Build

Edit `nuitka_build.py` to modify build options. Key options:

- `--standalone` - Bundle all dependencies
- `--onefile` - Create single executable
- `--output-dir=dist` - Output directory
- `--output-filename=reaper` - Executable name

### Platform-Specific Options

The build script automatically detects the platform and applies:

**Windows:**
- `--windows-console-mode=force` - Force console window
- `--windows-icon-from-ico=icon.ico` - Custom icon (if available)

**macOS:**
- `--macos-create-app-bundle` - Create .app bundle
- `--macos-app-icon=icon.icns` - Custom icon (if available)

**Linux:**
- `--linux-icon=icon.png` - Custom icon (if available)

## Testing the Build

After building, test the executable:

```bash
# Windows
dist\reaper.exe --version

# Linux/macOS
./dist/reaper --version
```

Run a Reaper script:

```bash
dist/reaper script.reaper
```

## Troubleshooting

### Build Fails with "Nuitka not found"

The build script will automatically install Nuitka if missing. If it fails, install manually:

```bash
pip install nuitka
```

### Build Fails with Compiler Errors

Ensure you have the platform-specific build tools installed:

**Windows:**
- Install Visual Studio Build Tools or Visual Studio with C++ support
- Or install MinGW-w64

**Linux:**
```bash
sudo apt-get install build-essential
# or for other distributions:
sudo yum install gcc gcc-c++ make
```

**macOS:**
```bash
xcode-select --install
```

### Executable is Large

The standalone executable includes all dependencies and can be 30-100MB. This is normal. To reduce size:

1. Remove unused packages from `nuitka_build.py`
2. Enable compression (experimental Nuitka features)
3. Use `--lto` flag for link-time optimization

### Executable Fails to Run

Common issues:

1. **Missing DLLs (Windows)**: Ensure Visual C++ Redistributable is installed
2. **Permission denied (Linux/macOS)**: `chmod +x dist/reaper`
3. **Import errors**: Check that all required packages are included in build

## Advanced Configuration

### Adding Custom Icons

Place icon files in the project root:

- Windows: `icon.ico`
- macOS: `icon.icns`
- Linux: `icon.png`

The build script will automatically use them if present.

### Excluding Modules

To reduce executable size, edit `nuitka_build.py` and remove unused packages from the `include_packages` list.

### Debug Builds

For debugging, remove `--remove-output` from the Nuitka command to keep intermediate files.

## CI/CD Integration

The build system can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Build Reaper
  run: python nuitka_build.py
  
- name: Upload Artifact
  uses: actions/upload-artifact@v2
  with:
    name: reaper-executable
    path: dist/reaper*
```

## Version Management

Reaper uses a centralized version management system. The version is defined in `version.py` and automatically used throughout the build and packaging system.

### Checking Version

```bash
python version.py              # Display version string
python -c "from version import get_version; print(get_version())"  # Get version number
```

### Updating Version

Edit `version.py` to update the version:

```python
__version__ = "0.2.1"  # Update version here
__version_info__ = (0, 2, 1)
__release_date__ = "2025-10-30"
```

The version is automatically used in:
- Executable build output
- Installer packages
- Release notes
- CLI `--version` flag

## Packaging System

Reaper includes a comprehensive packaging system for creating distributable installers and release packages.

### Build Modes

The build scripts support multiple modes:

**Windows:**
```batch
build.bat              # Build only
build.bat package      # Full release package
build.bat installer    # Build + installer
build.bat sign         # Build + code signing
```

**Linux/macOS:**
```bash
./build.sh              # Build only
./build.sh package      # Full release package
./build.sh installer    # Build + installer
./build.sh sign         # Build + code signing
```

### Creating Installers

#### Windows Installer (Inno Setup)

The Windows installer requires Inno Setup 5 or 6:

1. Install Inno Setup: https://jrsoftware.org/isinfo.php
2. Build and create installer:

```batch
build.bat installer
```

This creates `dist/reaper-setup-0.2.0.exe`

**Requirements:**
- Inno Setup installed (detected automatically)
- Executable built first (via `build.bat`)

#### macOS Installer (.dmg)

The macOS installer requires `create-dmg`:

```bash
brew install create-dmg
./build.sh installer
```

This creates `dist/reaper-0.2.0-macos.dmg`

**Requirements:**
- `create-dmg` installed via Homebrew
- Executable built first (via `./build.sh`)

#### Linux AppImage

The Linux AppImage requires `appimagetool`:

```bash
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
./build.sh installer
```

This creates `dist/reaper-0.2.0-linux.AppImage`

**Requirements:**
- `appimagetool` installed and in PATH
- Executable built first (via `./build.sh`)

### Code Signing

Code signing provides security and trust for distributed executables.

#### Windows Code Signing

Requires a code signing certificate (.pfx file) and Windows SDK (signtool.exe):

1. Set environment variables:
```batch
set WINDOWS_CERT_PATH=C:\path\to\certificate.pfx
set WINDOWS_CERT_PASSWORD=your_certificate_password
```

2. Build and sign:
```batch
build.bat sign
```

**Requirements:**
- Valid code signing certificate (.pfx)
- Windows SDK installed (contains signtool.exe)
- Certificate password (if protected)

#### macOS Code Signing

Requires Apple Developer ID and certificate:

1. Set environment variable:
```bash
export APPLE_DEVELOPER_ID="Developer ID Application: Your Name (TEAM_ID)"
```

2. Build and sign:
```bash
./build.sh sign
```

**Notarization (Optional):**

For macOS gatekeeper compatibility, you can notarize the signed app:

```bash
export APPLE_ID="your@apple.id"
export APPLE_APP_PASSWORD="app-specific-password"
export APPLE_TEAM_ID="TEAM_ID"

python -m packaging.signing dist/reaper.app
# Then use xcrun notarytool submit for notarization
```

**Requirements:**
- Apple Developer account
- Developer ID certificate installed in Keychain
- Valid Developer ID identity

### Release Packaging

The release packaging system creates complete distribution packages with checksums and release notes.

#### Full Release Package

Create a complete release package (build + installer + checksums + release notes):

```bash
# Windows
build.bat package

# Linux/macOS
./build.sh package
```

Or use the Python script directly:

```bash
python package.py
```

**Package Contents:**
- Built executable
- Installer package (if dependencies available)
- SHA256 checksum files
- Release notes (RELEASE_NOTES_v0.2.0.md)

**Options:**
```bash
python package.py --no-sign       # Skip code signing
python package.py --no-installer  # Skip installer creation
```

### Using the Packaging Module

The packaging system can be used programmatically:

```python
from packaging.release import ReleasePackager

packager = ReleasePackager()
results = packager.package_release(
    sign=True,
    create_installer_pkg=True
)

print(f"Executable: {results['executable']}")
print(f"Installer: {results['installer']}")
```

Or use individual components:

```python
from packaging.installers import create_installer
from packaging.signing import sign_executable

# Create installer
installer = create_installer("Windows")

# Sign executable
sign_executable(Path("dist/reaper.exe"))
```

## Release Distribution

### Recommended Workflow

1. **Update Version** (`version.py`)
2. **Build Executable**: `build.bat` or `./build.sh`
3. **Test Executable**: Verify functionality
4. **Create Release Package**: `build.bat package` or `./build.sh package`
5. **Verify Checksums**: Check generated `.sha256` files
6. **Upload to Distribution**: GitHub Releases, website, etc.

### Release Checklist

- [ ] Version updated in `version.py`
- [ ] Executable builds successfully
- [ ] Tests pass on target platform
- [ ] Installer created (if applicable)
- [ ] Code signing applied (if certificates available)
- [ ] Checksums generated
- [ ] Release notes reviewed
- [ ] Distribution packages uploaded

### Distribution Files

A complete release includes:

```
dist/
├── reaper.exe (or reaper/reaper.app)
├── reaper-setup-0.2.0.exe (Windows installer)
├── reaper-0.2.0-macos.dmg (macOS installer)
├── reaper-0.2.0-linux.AppImage (Linux AppImage)
├── *.sha256 (Checksum files)
└── RELEASE_NOTES_v0.2.0.md
```

## Next Steps

After building the executable:

1. Test it with example Reaper scripts
2. Use the packaging system to create installers
3. Sign the executable for distribution (if certificates available)
4. Create release packages with `package.py`
5. Distribute via GitHub Releases or website

## Support

For build issues:
1. Check Nuitka documentation: https://nuitka.net/doc/
2. Review build errors in console output
3. Ensure all dependencies are properly installed

