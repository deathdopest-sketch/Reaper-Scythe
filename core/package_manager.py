#!/usr/bin/env python3
"""
REAPER Package Manager

Manages package installation, dependency resolution, and package discovery
for the REAPER language ecosystem.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from urllib.parse import urlparse
import tempfile

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python
    except ImportError:
        tomllib = None

from .reaper_error import ReaperRuntimeError


class PackageManifest:
    """Represents a package manifest (reaper.toml)."""
    
    def __init__(self, data: Dict[str, Any]):
        self.name = data.get("name", "")
        self.version = data.get("version", "0.1.0")
        self.description = data.get("description", "")
        self.author = data.get("author", "")
        self.license = data.get("license", "MIT")
        self.repository = data.get("repository", "")
        self.dependencies = data.get("dependencies", {})
        self.dev_dependencies = data.get("dev_dependencies", {})
        self.main = data.get("main", "main.reaper")
        self.entry_point = data.get("entry_point", "")
        self.keywords = data.get("keywords", [])
        self.requires = data.get("requires", {})  # Runtime requirements (e.g., Python version)
    
    @classmethod
    def from_file(cls, path: Path) -> "PackageManifest":
        """Load manifest from a reaper.toml file."""
        if not path.exists():
            raise ReaperRuntimeError(f"Manifest file not found: {path}")
        
        if tomllib is None:
            raise ReaperRuntimeError(
                "TOML parsing not available. Install tomli: pip install tomli"
            )
        
        with open(path, "rb") as f:
            data = tomllib.load(f)
        
        return cls(data.get("package", {}))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "repository": self.repository,
            "dependencies": self.dependencies,
            "dev_dependencies": self.dev_dependencies,
            "main": self.main,
            "entry_point": self.entry_point,
            "keywords": self.keywords,
            "requires": self.requires,
        }


class ReaperPackageManager:
    """
    Package manager for REAPER language.
    
    Handles:
    - Package installation from GitHub/GitLab
    - Dependency resolution
    - Local package cache
    - Package discovery
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize package manager.
        
        Args:
            base_path: Base path for the project (default: current directory)
        """
        self.base_path = base_path or Path.cwd()
        self.packages_dir = self.base_path / "reaper_modules"
        self.global_packages_dir = Path.home() / ".reaper" / "packages"
        self.manifest_path = self.base_path / "reaper.toml"
        
        # Create directories if they don't exist
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.global_packages_dir.mkdir(parents=True, exist_ok=True)
    
    def init_project(self, name: str, version: str = "0.1.0", author: str = "", 
                     description: str = "") -> None:
        """
        Initialize a new REAPER project with a manifest file.
        
        Args:
            name: Package name
            version: Package version
            author: Package author
            description: Package description
        """
        if self.manifest_path.exists():
            raise ReaperRuntimeError(
                f"Manifest already exists: {self.manifest_path}. "
                "Use 'reaper package update' to modify it."
            )
        
        manifest_data = {
            "package": {
                "name": name,
                "version": version,
                "description": description,
                "author": author,
                "license": "MIT",
                "dependencies": {},
                "dev_dependencies": {},
                "main": "main.reaper",
            }
        }
        
        self._write_manifest(manifest_data)
        print(f"✓ Initialized REAPER project '{name}' v{version}")
        print(f"  Manifest: {self.manifest_path}")
    
    def _write_manifest(self, data: Dict[str, Any]) -> None:
        """Write manifest data to reaper.toml file."""
        # Format as TOML (simplified)
        lines = ["[package]"]
        pkg = data["package"]
        
        for key, value in pkg.items():
            if key == "dependencies" or key == "dev_dependencies":
                if value:
                    lines.append(f"\n[{key}]")
                    for dep_name, dep_version in value.items():
                        lines.append(f'{dep_name} = "{dep_version}"')
            elif isinstance(value, list):
                lines.append(f'{key} = {json.dumps(value)}')
            elif isinstance(value, dict):
                lines.append(f"\n[{key}]")
                for k, v in value.items():
                    lines.append(f'{k} = "{v}"')
            else:
                lines.append(f'{key} = "{value}"')
        
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    
    def install_package(self, package_spec: str, dev: bool = False) -> None:
        """
        Install a package.
        
        Args:
            package_spec: Package specification (e.g., "github:user/repo" or "package-name@version")
            dev: If True, install as dev dependency
        """
        # Parse package spec
        if package_spec.startswith("github:"):
            # GitHub repository
            repo_path = package_spec[7:]  # Remove "github:" prefix
            self._install_from_github(repo_path, dev)
        elif package_spec.startswith("gitlab:"):
            # GitLab repository
            repo_path = package_spec[7:]  # Remove "gitlab:" prefix
            self._install_from_gitlab(repo_path, dev)
        elif package_spec.startswith("git+"):
            # Generic Git repository
            repo_url = package_spec[4:]  # Remove "git+" prefix
            self._install_from_git(repo_url, dev)
        else:
            # Try to resolve as a package name (future: package registry)
            raise ReaperRuntimeError(
                f"Unknown package source: {package_spec}. "
                "Supported formats: github:user/repo, gitlab:user/repo, git+url"
            )
    
    def _install_from_github(self, repo_path: str, dev: bool = False) -> None:
        """Install package from GitHub repository."""
        # Parse repo path (user/repo or user/repo@branch/tag)
        if "@" in repo_path:
            repo_path, ref = repo_path.split("@", 1)
        else:
            ref = "main"
        
        repo_url = f"https://github.com/{repo_path}.git"
        self._install_from_git(repo_url, dev, ref)
    
    def _install_from_gitlab(self, repo_path: str, dev: bool = False) -> None:
        """Install package from GitLab repository."""
        if "@" in repo_path:
            repo_path, ref = repo_path.split("@", 1)
        else:
            ref = "main"
        
        repo_url = f"https://gitlab.com/{repo_path}.git"
        self._install_from_git(repo_url, dev, ref)
    
    def _install_from_git(self, repo_url: str, dev: bool = False, ref: str = "main") -> None:
        """
        Install package from Git repository.
        
        Args:
            repo_url: Git repository URL
            dev: If True, install as dev dependency
            ref: Branch, tag, or commit to checkout
        """
        # Clone to temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            clone_path = tmp_path / "package"
            
            print(f"Cloning {repo_url}...")
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", "--branch", ref, repo_url, str(clone_path)],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                # Try without branch (use default)
                subprocess.run(
                    ["git", "clone", "--depth", "1", repo_url, str(clone_path)],
                    check=True,
                    capture_output=True,
                    text=True
                )
            
            # Load manifest
            manifest_path = clone_path / "reaper.toml"
            if not manifest_path.exists():
                raise ReaperRuntimeError(
                    f"Package manifest (reaper.toml) not found in {repo_url}"
                )
            
            manifest = PackageManifest.from_file(manifest_path)
            package_name = manifest.name or self._extract_package_name_from_url(repo_url)
            
            # Install to local packages directory
            install_path = self.packages_dir / package_name
            if install_path.exists():
                shutil.rmtree(install_path)
            
            shutil.copytree(clone_path, install_path)
            
            # Update project manifest
            self._add_dependency(package_name, repo_url, dev)
            
            # Install dependencies recursively
            if manifest.dependencies:
                print(f"Installing dependencies for {package_name}...")
                for dep_name, dep_spec in manifest.dependencies.items():
                    try:
                        self.install_package(dep_spec, dev=False)
                    except Exception as e:
                        print(f"Warning: Failed to install dependency {dep_name}: {e}")
            
            print(f"✓ Installed {package_name} v{manifest.version}")
    
    def _extract_package_name_from_url(self, url: str) -> str:
        """Extract package name from repository URL."""
        # Extract from URL (e.g., github.com/user/repo -> repo)
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if path.endswith(".git"):
            path = path[:-4]
        parts = path.split("/")
        return parts[-1] if parts else "unknown"
    
    def _add_dependency(self, package_name: str, spec: str, dev: bool = False) -> None:
        """Add dependency to project manifest."""
        if not self.manifest_path.exists():
            # Create minimal manifest
            self.init_project(
                name=self.base_path.name,
                version="0.1.0",
                author="",
                description=""
            )
        
        # Read existing manifest
        if tomllib is None:
            raise ReaperRuntimeError("TOML parsing not available")
        
        with open(self.manifest_path, "rb") as f:
            data = tomllib.load(f)
        
        pkg = data.setdefault("package", {})
        deps_key = "dev_dependencies" if dev else "dependencies"
        deps = pkg.setdefault(deps_key, {})
        deps[package_name] = spec
        
        # Write back
        self._write_manifest(data)
    
    def list_packages(self) -> List[Dict[str, str]]:
        """List installed packages."""
        packages = []
        
        if self.packages_dir.exists():
            for pkg_dir in self.packages_dir.iterdir():
                if pkg_dir.is_dir():
                    manifest_path = pkg_dir / "reaper.toml"
                    if manifest_path.exists():
                        try:
                            manifest = PackageManifest.from_file(manifest_path)
                            packages.append({
                                "name": manifest.name,
                                "version": manifest.version,
                                "path": str(pkg_dir),
                            })
                        except Exception:
                            packages.append({
                                "name": pkg_dir.name,
                                "version": "unknown",
                                "path": str(pkg_dir),
                            })
        
        return packages
    
    def uninstall_package(self, package_name: str) -> None:
        """Uninstall a package."""
        package_path = self.packages_dir / package_name
        if not package_path.exists():
            raise ReaperRuntimeError(f"Package '{package_name}' not found")
        
        shutil.rmtree(package_path)
        
        # Remove from manifest
        if self.manifest_path.exists():
            if tomllib is None:
                return
            
            with open(self.manifest_path, "rb") as f:
                data = tomllib.load(f)
            
            pkg = data.get("package", {})
            for deps_key in ["dependencies", "dev_dependencies"]:
                deps = pkg.get(deps_key, {})
                if package_name in deps:
                    del deps[package_name]
                    self._write_manifest(data)
                    break
        
        print(f"✓ Uninstalled {package_name}")
    
    def update_packages(self) -> None:
        """Update all installed packages."""
        if not self.manifest_path.exists():
            raise ReaperRuntimeError("No manifest file found. Run 'reaper package init' first.")
        
        if tomllib is None:
            raise ReaperRuntimeError("TOML parsing not available")
        
        with open(self.manifest_path, "rb") as f:
            data = tomllib.load(f)
        
        pkg = data.get("package", {})
        all_deps = {}
        all_deps.update(pkg.get("dependencies", {}))
        all_deps.update(pkg.get("dev_dependencies", {}))
        
        for package_name, spec in all_deps.items():
            print(f"Updating {package_name}...")
            try:
                # Uninstall and reinstall
                package_path = self.packages_dir / package_name
                if package_path.exists():
                    shutil.rmtree(package_path)
                
                self.install_package(spec, dev=package_name in pkg.get("dev_dependencies", {}))
            except Exception as e:
                print(f"Warning: Failed to update {package_name}: {e}")
        
        print("✓ All packages updated")
    
    def get_manifest(self) -> Optional[PackageManifest]:
        """Get the current project's manifest."""
        if not self.manifest_path.exists():
            return None
        
        return PackageManifest.from_file(self.manifest_path)

