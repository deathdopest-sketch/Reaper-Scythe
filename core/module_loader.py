"""
REAPER Module Loader

This module handles importing and loading security libraries and modules
for the Reaper language. It provides namespace support and prevents
circular dependencies.
"""

import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from .reaper_error import ReaperRuntimeError
from .lexer import tokenize
from .parser import parse
# Interpreter imported lazily to avoid circular import


class ModuleCache:
    """Cache for loaded modules to prevent re-importing."""
    
    def __init__(self):
        self._modules: Dict[str, Any] = {}
        self._loading: Set[str] = set()  # Track modules currently being loaded
    
    def is_loaded(self, module_name: str) -> bool:
        """Check if module is already loaded."""
        return module_name in self._modules
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """Get loaded module."""
        return self._modules.get(module_name)
    
    def cache_module(self, module_name: str, module: Any) -> None:
        """Cache a loaded module."""
        self._modules[module_name] = module
    
    def is_loading(self, module_name: str) -> bool:
        """Check if module is currently being loaded (circular dependency detection)."""
        return module_name in self._loading
    
    def start_loading(self, module_name: str) -> None:
        """Mark module as being loaded."""
        self._loading.add(module_name)
    
    def finish_loading(self, module_name: str) -> None:
        """Mark module as finished loading."""
        self._loading.discard(module_name)


class ReaperModuleLoader:
    """
    Module loader for Reaper language.
    
    Handles importing security libraries and making them available
    in the Reaper execution environment.
    """
    
    # Map of Reaper module names to Python module paths
    SECURITY_LIBRARIES = {
        "phantom": "libs.phantom",
        "crypt": "libs.crypt",
        "wraith": "libs.wraith",
        "specter": "libs.specter",
        "shadow": "libs.shadow",
        "void": "libs.void",
        "zombitious": "libs.zombitious",
        "shinigami": "libs.shinigami",
    }
    
    # Standard library modules
    STANDARD_LIBRARIES = {
        "graveyard": "stdlib.graveyard",
    }
    
    # Graveyard submodules (for direct import like graveyard.time_utils)
    GRAVEYARD_MODULES = {
        "graveyard.time_utils": "stdlib.graveyard.time_utils",
        "graveyard.math_utils": "stdlib.graveyard.math_utils",
        "graveyard.string_utils": "stdlib.graveyard.string_utils",
        "graveyard.collection_utils": "stdlib.graveyard.collection_utils",
        "graveyard.random_utils": "stdlib.graveyard.random_utils",
    }
    
    def __init__(self, base_path: Optional[Path] = None, current_file: Optional[Path] = None):
        """
        Initialize module loader.
        
        Args:
            base_path: Base path for the Reaper project (for finding modules)
            current_file: Path to the current file being executed (for relative imports)
        """
        self.base_path = base_path or Path.cwd()
        self.current_file = current_file
        self.cache = ModuleCache()
        self.loaded_namespaces: Dict[str, Dict[str, Any]] = {}
        self._update_search_paths()
    
    def _update_search_paths(self) -> None:
        """Update module search paths based on current file and base path."""
        self.module_search_paths = [
            self.base_path,
            self.base_path / "modules",
            self.base_path / "lib",
            self.base_path / "reaper_modules",  # Package manager directory
        ]
        
        # Add current file's directory if available
        if self.current_file:
            current_dir = self.current_file.parent
            if current_dir not in self.module_search_paths:
                self.module_search_paths.insert(0, current_dir)
    
    def load_module(self, module_name: str, alias: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a module and return its namespace.
        
        Args:
            module_name: Name of the module to load
            alias: Optional alias for the module namespace
            
        Returns:
            Dictionary containing module's exported symbols
            
        Raises:
            ReaperRuntimeError: If module cannot be loaded
        """
        # Check for circular dependency
        if self.cache.is_loading(module_name):
            raise ReaperRuntimeError(
                f"Circular dependency detected: module '{module_name}' is already being loaded"
            )
        
        # Check cache first
        if self.cache.is_loaded(module_name):
            module = self.cache.get_module(module_name)
            namespace = self._create_namespace(module)
            
            # Store in namespace cache with alias if provided
            ns_name = alias or module_name
            self.loaded_namespaces[ns_name] = namespace
            return namespace
        
        # Mark as loading
        self.cache.start_loading(module_name)
        
        try:
            # Try to resolve as Python module first
            python_module_path = self._resolve_module_path(module_name)
            
            if python_module_path:
                # Import the Python module
                try:
                    module = importlib.import_module(python_module_path)
                except ImportError as e:
                    raise ReaperRuntimeError(
                        f"Failed to import module '{module_name}': {str(e)}"
                    )
                
                # Cache the module
                self.cache.cache_module(module_name, module)
                
                # Create namespace
                namespace = self._create_namespace(module)
                
                # Store in namespace cache
                ns_name = alias or module_name
                self.loaded_namespaces[ns_name] = namespace
                
                return namespace
            
            # Try to find and load .reaper file
            reaper_file = self._find_reaper_module(module_name)
            
            if reaper_file:
                # Load .reaper file as module
                namespace = self._load_reaper_module(reaper_file, module_name)
                
                # Cache the module (store the namespace as the "module")
                self.cache.cache_module(module_name, namespace)
                
                # Store in namespace cache
                ns_name = alias or module_name
                self.loaded_namespaces[ns_name] = namespace
                
                return namespace
            
            # Module not found
            available = list(self.SECURITY_LIBRARIES.keys()) + list(self.STANDARD_LIBRARIES.keys())
            raise ReaperRuntimeError(
                f"Unknown module: '{module_name}'. Available modules: {available}. "
                f"Also searched for .reaper files in: {[str(p) for p in self.module_search_paths]}"
            )
            
        finally:
            # Mark as finished loading
            self.cache.finish_loading(module_name)
    
    def _resolve_module_path(self, module_name: str) -> Optional[str]:
        """
        Resolve Reaper module name to Python module path.
        
        Args:
            module_name: Reaper module name
            
        Returns:
            Python module path or None if not found
        """
        # Check security libraries
        if module_name in self.SECURITY_LIBRARIES:
            return self.SECURITY_LIBRARIES[module_name]
        
        # Check standard libraries
        if module_name in self.STANDARD_LIBRARIES:
            return self.STANDARD_LIBRARIES[module_name]
        
        # Check graveyard submodules
        if module_name in self.GRAVEYARD_MODULES:
            return self.GRAVEYARD_MODULES[module_name]
        
        # Try direct import (for future custom modules)
        # For now, return None if not found
        return None
    
    def _create_namespace(self, module: Any) -> Dict[str, Any]:
        """
        Create a namespace dictionary from a Python module.
        
        Args:
            module: Python module object
            
        Returns:
            Dictionary of exported symbols
        """
        namespace = {}
        
        # Get all public attributes (not starting with _)
        for attr_name in dir(module):
            if not attr_name.startswith('_'):
                try:
                    attr_value = getattr(module, attr_name)
                    namespace[attr_name] = attr_value
                except Exception:
                    # Skip attributes that can't be accessed
                    pass
        
        # Also check for __all__ if defined
        if hasattr(module, '__all__'):
            for name in module.__all__:
                if hasattr(module, name):
                    try:
                        namespace[name] = getattr(module, name)
                    except Exception:
                        pass
        
        return namespace
    
    def get_namespace(self, namespace_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a loaded namespace.
        
        Args:
            namespace_name: Name of the namespace
            
        Returns:
            Namespace dictionary or None if not found
        """
        return self.loaded_namespaces.get(namespace_name)
    
    def import_symbols(self, module_name: str, symbol_names: List[str], 
                      namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Import specific symbols from a module.
        
        Args:
            module_name: Name of the module
            symbol_names: List of symbol names to import
            namespace: Optional namespace to import into (default: global)
            
        Returns:
            Dictionary of imported symbols
        """
        # Load the module
        module_namespace = self.load_module(module_name)
        
        # Extract requested symbols
        imported = {}
        missing = []
        
        for symbol_name in symbol_names:
            if symbol_name in module_namespace:
                imported[symbol_name] = module_namespace[symbol_name]
            else:
                missing.append(symbol_name)
        
        if missing:
            raise ReaperRuntimeError(
                f"Symbols not found in module '{module_name}': {', '.join(missing)}"
            )
        
        return imported
    
    def _find_reaper_module(self, module_name: str) -> Optional[Path]:
        """
        Find a .reaper file for the given module name.
        
        Args:
            module_name: Name of the module to find
            
        Returns:
            Path to .reaper file or None if not found
        """
        # Convert module name to file path (e.g., "utils.math" -> "utils/math.reaper")
        module_parts = module_name.split('.')
        
        # Try different search paths
        for search_path in self.module_search_paths:
            # Try as direct file name
            direct_path = search_path / f"{module_name}.reaper"
            if direct_path.exists() and direct_path.is_file():
                return direct_path
            
            # Try as path components
            file_path = search_path
            for part in module_parts:
                file_path = file_path / part
            
            # Try with .reaper extension
            reaper_file = file_path.with_suffix('.reaper')
            if reaper_file.exists() and reaper_file.is_file():
                return reaper_file
            
            # Try as directory with __init__.reaper
            init_file = file_path / "__init__.reaper"
            if init_file.exists() and init_file.is_file():
                return init_file
            
            # Also check subdirectories for the module name
            if search_path.exists() and search_path.is_dir():
                for subdir in search_path.iterdir():
                    if subdir.is_dir():
                        # Check if module file exists in this subdirectory
                        module_file = subdir / f"{module_name}.reaper"
                        if module_file.exists() and module_file.is_file():
                            return module_file
                        
                        # For package manager: check if subdir is a package and contains the module
                        # (e.g., reaper_modules/my_package/utils.reaper)
                        if search_path.name == "reaper_modules":
                            # Also check for __init__.reaper in package (package name matches module)
                            init_file = subdir / "__init__.reaper"
                            if init_file.exists() and module_name == subdir.name:
                                return init_file
        
        # Try relative to current file if available
        if self.current_file:
            current_dir = self.current_file.parent
            # Try direct file
            relative_path = current_dir / f"{module_name}.reaper"
            if relative_path.exists() and relative_path.is_file():
                return relative_path
            
            # Try as path components
            file_path = current_dir
            for part in module_parts:
                file_path = file_path / part
            
            reaper_file = file_path.with_suffix('.reaper')
            if reaper_file.exists() and reaper_file.is_file():
                return reaper_file
        
        return None
    
    def _load_reaper_module(self, file_path: Path, module_name: str) -> Dict[str, Any]:
        """
        Load a .reaper file as a module and return its namespace.
        
        Args:
            file_path: Path to the .reaper file
            module_name: Name of the module
            
        Returns:
            Dictionary containing module's exported symbols
            
        Raises:
            ReaperRuntimeError: If module cannot be loaded
        """
        # Lazy import to avoid circular dependency
        from .interpreter import Interpreter
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            raise ReaperRuntimeError(
                f"Failed to read module file '{file_path}': {str(e)}"
            )
        
        # Create a new interpreter for this module
        # Use a separate environment to isolate module scope
        module_interpreter = Interpreter()
        
        # Update module loader's base path and current file for nested imports
        module_interpreter.module_loader.base_path = file_path.parent
        module_interpreter.module_loader.current_file = file_path
        module_interpreter.module_loader._update_search_paths()
        
        try:
            # Tokenize
            tokens = tokenize(source, str(file_path))
            
            # Parse
            program = parse(tokens)
            
            # Execute in isolated environment
            module_interpreter.interpret(program)
            
            # Extract exported symbols from the module's global environment
            # For now, export all top-level definitions (functions and variables)
            namespace = {}
            module_env = module_interpreter.global_environment
            
            # Get all symbols from the environment
            # Note: This accesses internal _storage, but it's the cleanest way
            # to extract module exports without modifying the environment API
            for name, (value, var_type, is_constant, is_builtin) in module_env._storage.items():
                # Skip built-ins and private symbols (starting with _)
                # Also skip special markers like "<builtin:...>"
                if (not is_builtin and 
                    not name.startswith('_') and 
                    not (isinstance(value, str) and value.startswith('<builtin:'))):
                    # Functions are stored as InfectNode objects, keep them as-is
                    # Variables are stored as their values, keep them as-is
                    namespace[name] = value
            
            return namespace
            
        except Exception as e:
            raise ReaperRuntimeError(
                f"Failed to load Reaper module '{module_name}' from '{file_path}': {str(e)}"
            )
    
    def clear_cache(self) -> None:
        """Clear module cache (for testing)."""
        self.cache._modules.clear()
        self.loaded_namespaces.clear()

