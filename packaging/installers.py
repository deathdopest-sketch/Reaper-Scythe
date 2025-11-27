"""
Installer Generation for Reaper Executable

Supports:
- Windows: Inno Setup (.exe installer)
- macOS: create-dmg (.dmg disk image)
- Linux: AppImage (portable application)
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Optional, Dict, List
from .version import get_version, get_version_info

class InstallerGenerator:
    """Base class for installer generation."""
    
    def __init__(self, dist_dir: str = "dist", build_dir: str = "build"):
        self.dist_dir = Path(dist_dir)
        self.build_dir = Path(build_dir)
        self.version = get_version()
        self.version_info = get_version_info()
    
    def check_dependencies(self) -> bool:
        """Check if required tools are installed."""
        raise NotImplementedError
    
    def generate(self, executable_path: Path) -> Path:
        """Generate installer package."""
        raise NotImplementedError


class WindowsInstaller(InstallerGenerator):
    """Generate Windows installer using Inno Setup."""
    
    def __init__(self, dist_dir: str = "dist", build_dir: str = "build"):
        super().__init__(dist_dir, build_dir)
        self.iss_template = """
[Setup]
AppName=Reaper Language
AppVersion={version}
AppPublisher=Reaper Language Project
AppPublisherURL=https://github.com/reaper-lang/reaper
AppSupportURL=https://github.com/reaper-lang/reaper/issues
AppUpdatesURL=https://github.com/reaper-lang/reaper/releases
DefaultDirName={{autopf}}\\Reaper
DefaultGroupName=Reaper Language
AllowNoIcons=yes
LicenseFile=
OutputDir={output_dir}
OutputBaseFilename=reaper-setup-{version}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "{source_exe}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "examples\\*"; DestDir: "{{app}}\\examples"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: InstallExamples
Source: "docs\\*"; DestDir: "{{app}}\\docs"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: InstallDocs

[Icons]
Name: "{{group}}\\Reaper Language"; Filename: "{{app}}\\reaper.exe"
Name: "{{group}}\\{{cm:UninstallProgram,Reaper Language}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\Reaper Language"; Filename: "{{app}}\\reaper.exe"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\Reaper Language"; Filename: "{{app}}\\reaper.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\reaper.exe"; Description: "{{cm:LaunchProgram,Reaper Language}}"; Flags: nowait postinstall skipifsilent

[Code]
function InstallExamples: Boolean;
begin
  Result := True; // Can add checkbox logic
end;

function InstallDocs: Boolean;
begin
  Result := True; // Can add checkbox logic
end;
"""
    
    def check_dependencies(self) -> bool:
        """Check if Inno Setup is installed."""
        # Check common Inno Setup installation paths
        possible_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return True
        
        # Check PATH
        if shutil.which("iscc"):
            return True
        
        return False
    
    def generate(self, executable_path: Path) -> Path:
        """Generate Windows .exe installer using Inno Setup."""
        if not self.check_dependencies():
            raise RuntimeError(
                "Inno Setup not found. Please install Inno Setup 5 or 6 from:\n"
                "https://jrsoftware.org/isinfo.php"
            )
        
        # Find Inno Setup compiler
        iscc_path = None
        possible_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                iscc_path = path
                break
        
        if not iscc_path:
            iscc_path = shutil.which("iscc")
        
        if not iscc_path:
            raise RuntimeError("Could not find Inno Setup compiler (ISCC.exe)")
        
        # Create temporary .iss file
        iss_file = self.build_dir / "reaper.iss"
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare template
        iss_content = self.iss_template.format(
            version=self.version,
            output_dir=str(self.dist_dir.absolute()),
            source_exe=str(executable_path.absolute())
        )
        
        with open(iss_file, 'w', encoding='utf-8') as f:
            f.write(iss_content)
        
        # Compile installer
        print(f"Compiling Windows installer with Inno Setup...")
        result = subprocess.run(
            [iscc_path, str(iss_file)],
            cwd=self.build_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Inno Setup compilation failed:\n{result.stderr}")
        
        installer_path = self.dist_dir / f"reaper-setup-{self.version}.exe"
        if not installer_path.exists():
            raise RuntimeError("Installer was not created successfully")
        
        print(f"✅ Windows installer created: {installer_path}")
        return installer_path


class MacOSInstaller(InstallerGenerator):
    """Generate macOS .dmg disk image using create-dmg."""
    
    def check_dependencies(self) -> bool:
        """Check if create-dmg is installed."""
        return shutil.which("create-dmg") is not None
    
    def generate(self, executable_path: Path) -> Path:
        """Generate macOS .dmg installer."""
        if not self.check_dependencies():
            raise RuntimeError(
                "create-dmg not found. Install with:\n"
                "brew install create-dmg"
            )
        
        # Create .app bundle structure if needed
        app_name = "Reaper.app"
        app_path = self.dist_dir / app_name
        
        if not app_path.exists():
            # If we have a .app bundle, use it; otherwise create one
            if executable_path.suffix == ".app" or executable_path.name.endswith(".app"):
                # Copy .app bundle
                shutil.copytree(executable_path, app_path)
            else:
                # Create minimal .app bundle
                app_path.mkdir(parents=True)
                contents_dir = app_path / "Contents"
                contents_dir.mkdir()
                
                macos_dir = contents_dir / "MacOS"
                macos_dir.mkdir()
                
                # Copy executable
                shutil.copy(executable_path, macos_dir / "reaper")
                
                # Create Info.plist
                info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>reaper</string>
    <key>CFBundleIdentifier</key>
    <string>com.reaperlang.reaper</string>
    <key>CFBundleName</key>
    <string>Reaper</string>
    <key>CFBundleVersion</key>
    <string>{self.version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{self.version}</string>
</dict>
</plist>"""
                with open(contents_dir / "Info.plist", 'w') as f:
                    f.write(info_plist)
        
        # Create DMG
        dmg_name = f"reaper-{self.version}-macos.dmg"
        dmg_path = self.dist_dir / dmg_name
        
        print(f"Creating macOS DMG installer...")
        result = subprocess.run(
            [
                "create-dmg",
                "--volname", "Reaper Language",
                "--volicon", "",  # Add icon if available
                "--window-pos", "200", "120",
                "--window-size", "600", "400",
                "--icon-size", "100",
                "--icon", app_name, "175", "190",
                "--hide-extension", app_name,
                "--app-drop-link", "425", "190",
                str(dmg_path),
                str(app_path)
            ],
            cwd=self.dist_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"DMG creation failed:\n{result.stderr}")
        
        if not dmg_path.exists():
            raise RuntimeError("DMG was not created successfully")
        
        print(f"✅ macOS DMG created: {dmg_path}")
        return dmg_path


class LinuxInstaller(InstallerGenerator):
    """Generate Linux AppImage."""
    
    def check_dependencies(self) -> bool:
        """Check if required tools are available."""
        return True  # Basic tools should be available
    
    def generate(self, executable_path: Path) -> Path:
        """Generate Linux AppImage."""
        appimage_name = f"reaper-{self.version}-linux.AppImage"
        appimage_path = self.dist_dir / appimage_name
        
        # Create AppDir structure
        appdir = self.build_dir / "AppDir"
        if appdir.exists():
            shutil.rmtree(appdir)
        
        appdir.mkdir(parents=True)
        
        # Create usr/bin and copy executable
        usr_bin = appdir / "usr" / "bin"
        usr_bin.mkdir(parents=True)
        shutil.copy(executable_path, usr_bin / "reaper")
        os.chmod(usr_bin / "reaper", 0o755)
        
        # Create AppRun script
        apprun = appdir / "AppRun"
        with open(apprun, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("HERE=\"$(dirname \"$(readlink -f \"${0}\")\")\"\n")
            f.write("exec \"${HERE}/usr/bin/reaper\" \"$@\"\n")
        os.chmod(apprun, 0o755)
        
        # Create .desktop file
        desktop = appdir / "reaper.desktop"
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=Reaper Language
Comment=Reaper Standalone Hacking Language
Exec=reaper
Icon=reaper
Categories=Development;
"""
        with open(desktop, 'w') as f:
            f.write(desktop_content)
        
        # Check for appimagetool
        appimagetool = shutil.which("appimagetool")
        if not appimagetool:
            print("Warning: appimagetool not found. Install from:")
            print("  https://github.com/AppImage/AppImageKit/releases")
            print("Or use: wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage")
            print("       chmod +x appimagetool-x86_64.AppImage")
            raise RuntimeError("appimagetool is required to create AppImage")
        
        # Generate AppImage
        print(f"Creating Linux AppImage...")
        result = subprocess.run(
            [appimagetool, str(appdir), str(appimage_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"AppImage creation failed:\n{result.stderr}")
        
        if not appimage_path.exists():
            raise RuntimeError("AppImage was not created successfully")
        
        # Make executable
        os.chmod(appimage_path, 0o755)
        
        print(f"✅ Linux AppImage created: {appimage_path}")
        return appimage_path


def create_installer(platform_name: Optional[str] = None) -> Path:
    """Create installer for the current or specified platform."""
    if platform_name is None:
        platform_name = platform.system()
    
    dist_dir = Path("dist")
    
    # Find executable
    if platform_name == "Windows":
        executable = dist_dir / "reaper.exe"
    elif platform_name == "Darwin":
        executable = dist_dir / "reaper.app"
    elif platform_name == "Linux":
        executable = dist_dir / "reaper"
    else:
        raise ValueError(f"Unsupported platform: {platform_name}")
    
    if not executable.exists():
        raise FileNotFoundError(
            f"Executable not found: {executable}\n"
            "Please build the executable first using nuitka_build.py"
        )
    
    # Create appropriate installer
    if platform_name == "Windows":
        generator = WindowsInstaller()
    elif platform_name == "Darwin":
        generator = MacOSInstaller()
    elif platform_name == "Linux":
        generator = LinuxInstaller()
    else:
        raise ValueError(f"Unsupported platform: {platform_name}")
    
    return generator.generate(executable)


if __name__ == "__main__":
    import sys
    platform_name = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        installer_path = create_installer(platform_name)
        print(f"\n✅ Installer created: {installer_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

