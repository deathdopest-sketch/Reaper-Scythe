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
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize module loader.
        
        Args:
            base_path: Base path for the Reaper project (for finding modules)
        """
        self.base_path = base_path or Path.cwd()
        self.cache = ModuleCache()
        self.loaded_namespaces: Dict[str, Dict[str, Any]] = {}
    
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
            # Determine Python module path
            python_module_path = self._resolve_module_path(module_name)
            
            if not python_module_path:
                raise ReaperRuntimeError(
                    f"Unknown module: '{module_name}'. Available modules: {list(self.SECURITY_LIBRARIES.keys()) + list(self.STANDARD_LIBRARIES.keys())}"
                )
            
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
    
    def clear_cache(self) -> None:
        """Clear module cache (for testing)."""
        self.cache._modules.clear()
        self.loaded_namespaces.clear()

