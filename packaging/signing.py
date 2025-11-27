"""
Code Signing for Reaper Executable

Supports code signing for Windows and macOS executables.
Requires code signing certificates to be configured.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Optional, Dict

class CodeSigner:
    """Base class for code signing."""
    
    def __init__(self, cert_path: Optional[str] = None, cert_password: Optional[str] = None):
        self.cert_path = cert_path
        self.cert_password = cert_password
    
    def sign(self, file_path: Path) -> bool:
        """Sign a file."""
        raise NotImplementedError
    
    def verify(self, file_path: Path) -> bool:
        """Verify signature of a file."""
        raise NotImplementedError


class WindowsCodeSigner(CodeSigner):
    """Code signing for Windows executables using signtool."""
    
    def __init__(self, cert_path: Optional[str] = None, cert_password: Optional[str] = None,
                 timestamp_url: str = "http://timestamp.digicert.com"):
        super().__init__(cert_path, cert_password)
        self.timestamp_url = timestamp_url
    
    def check_dependencies(self) -> bool:
        """Check if signtool is available."""
        # Check if Windows SDK is installed (contains signtool)
        possible_paths = [
            r"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\x86\signtool.exe",
            r"C:\Program Files\Windows Kits\10\bin\x64\signtool.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return True
        
        return shutil.which("signtool") is not None
    
    def sign(self, file_path: Path) -> bool:
        """Sign Windows executable."""
        if not self.check_dependencies():
            print("Warning: signtool not found. Skipping code signing.")
            print("Install Windows SDK to get signtool.exe")
            return False
        
        if not self.cert_path or not os.path.exists(self.cert_path):
            print("Warning: Code signing certificate not found. Skipping code signing.")
            print("Set CERT_PATH environment variable to sign executables.")
            return False
        
        # Find signtool
        signtool_path = None
        possible_paths = [
            r"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\x86\signtool.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                signtool_path = path
                break
        
        if not signtool_path:
            signtool_path = shutil.which("signtool")
        
        if not signtool_path:
            print("Warning: Could not find signtool. Skipping code signing.")
            return False
        
        # Build sign command
        cmd = [
            signtool_path,
            "sign",
            "/f", self.cert_path,
            "/t", self.timestamp_url,
            "/fd", "SHA256",
        ]
        
        if self.cert_password:
            cmd.extend(["/p", self.cert_password])
        
        cmd.append(str(file_path))
        
        try:
            print(f"Signing {file_path.name}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully signed: {file_path}")
                return True
            else:
                print(f"❌ Code signing failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Code signing error: {e}")
            return False
    
    def verify(self, file_path: Path) -> bool:
        """Verify signature of Windows executable."""
        signtool_path = shutil.which("signtool")
        if not signtool_path:
            possible_paths = [
                r"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    signtool_path = path
                    break
        
        if not signtool_path:
            return False
        
        try:
            result = subprocess.run(
                [signtool_path, "verify", "/pa", "/v", str(file_path)],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False


class MacOSCodeSigner(CodeSigner):
    """Code signing for macOS using codesign."""
    
    def __init__(self, cert_path: Optional[str] = None, cert_password: Optional[str] = None,
                 identity: Optional[str] = None):
        super().__init__(cert_path, cert_password)
        self.identity = identity or os.environ.get("APPLE_DEVELOPER_ID")
    
    def check_dependencies(self) -> bool:
        """Check if codesign is available."""
        return shutil.which("codesign") is not None
    
    def sign(self, file_path: Path) -> bool:
        """Sign macOS executable or .app bundle."""
        if not self.check_dependencies():
            print("Warning: codesign not found. Skipping code signing.")
            return False
        
        if not self.identity:
            print("Warning: Code signing identity not found. Skipping code signing.")
            print("Set APPLE_DEVELOPER_ID environment variable or provide identity.")
            return False
        
        try:
            print(f"Signing {file_path.name}...")
            
            # Sign the file/app bundle
            result = subprocess.run(
                [
                    "codesign",
                    "--force",
                    "--deep",
                    "--sign", self.identity,
                    "--options", "runtime",
                    "--timestamp",
                    str(file_path)
                ],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully signed: {file_path}")
                return True
            else:
                print(f"❌ Code signing failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Code signing error: {e}")
            return False
    
    def verify(self, file_path: Path) -> bool:
        """Verify signature of macOS executable."""
        try:
            result = subprocess.run(
                ["codesign", "--verify", "--verbose", str(file_path)],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def notarize(self, file_path: Path, apple_id: Optional[str] = None,
                 app_password: Optional[str] = None) -> bool:
        """Notarize macOS app (requires Apple Developer account)."""
        if not apple_id:
            apple_id = os.environ.get("APPLE_ID")
        if not app_password:
            app_password = os.environ.get("APPLE_APP_PASSWORD")
        
        if not apple_id or not app_password:
            print("Warning: Apple ID credentials not found. Skipping notarization.")
            return False
        
        try:
            print("Submitting for notarization...")
            result = subprocess.run(
                [
                    "xcrun", "notarytool", "submit",
                    str(file_path),
                    "--apple-id", apple_id,
                    "--password", app_password,
                    "--team-id", os.environ.get("APPLE_TEAM_ID", ""),
                    "--wait"
                ],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print("✅ Notarization successful")
                return True
            else:
                print(f"❌ Notarization failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Notarization error: {e}")
            return False


def sign_executable(file_path: Path, platform_name: Optional[str] = None,
                   cert_path: Optional[str] = None, cert_password: Optional[str] = None) -> bool:
    """Sign executable for current or specified platform."""
    if platform_name is None:
        platform_name = platform.system()
    
    if platform_name == "Windows":
        signer = WindowsCodeSigner(
            cert_path=cert_path or os.environ.get("WINDOWS_CERT_PATH"),
            cert_password=cert_password or os.environ.get("WINDOWS_CERT_PASSWORD")
        )
    elif platform_name == "Darwin":
        signer = MacOSCodeSigner(
            identity=os.environ.get("APPLE_DEVELOPER_ID")
        )
    else:
        print(f"Code signing not supported for {platform_name}")
        return False
    
    return signer.sign(file_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python signing.py <executable_path> [cert_path] [cert_password]")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    cert_path = sys.argv[2] if len(sys.argv) > 2 else None
    cert_password = sys.argv[3] if len(sys.argv) > 3 else None
    
    if sign_executable(file_path, cert_path=cert_path, cert_password=cert_password):
        sys.exit(0)
    else:
        sys.exit(1)

