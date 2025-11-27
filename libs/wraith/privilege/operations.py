#!/usr/bin/env python3
"""
Wraith Privilege Operations Module
Privilege escalation, registry operations, and log manipulation
"""

import os
import sys
import subprocess
import time
import logging
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PrivilegeLevel(Enum):
    """Privilege levels"""
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"
    ROOT = "root"

class RegistryHive(Enum):
    """Windows registry hives"""
    HKEY_CLASSES_ROOT = "HKEY_CLASSES_ROOT"
    HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
    HKEY_LOCAL_MACHINE = "HKEY_LOCAL_MACHINE"
    HKEY_USERS = "HKEY_USERS"
    HKEY_CURRENT_CONFIG = "HKEY_CURRENT_CONFIG"

@dataclass
class PrivilegeInfo:
    """Privilege information"""
    current_user: str
    privilege_level: PrivilegeLevel
    is_admin: bool
    is_root: bool
    groups: List[str]
    capabilities: List[str]

@dataclass
class RegistryValue:
    """Registry value information"""
    name: str
    value_type: str
    data: Any
    size: int

@dataclass
class PrivilegeOperationResult:
    """Result of privilege operation"""
    success: bool
    operation: str
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

class WraithPrivilegeManager:
    """Advanced privilege operations manager"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize privilege manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.safe_mode = self.config.get('safe_mode', True)
        self.operation_log = []
        
    def _log_operation(self, operation: str, success: bool, message: str):
        """Log privilege operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"Privilege operation: {operation} - {message}")
    
    def get_privilege_info(self) -> PrivilegeInfo:
        """Get current privilege information
        
        Returns:
            PrivilegeInfo object
        """
        try:
            current_user = os.getenv('USERNAME') or os.getenv('USER', 'unknown')
            groups = []
            capabilities = []
            is_admin = False
            is_root = False
            privilege_level = PrivilegeLevel.USER
            
            if os.name == 'nt':
                # Windows privilege detection
                try:
                    import ctypes
                    is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                    if is_admin:
                        privilege_level = PrivilegeLevel.ADMIN
                except:
                    pass
                
                # Get user groups
                try:
                    result = subprocess.run(['whoami', '/groups'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'S-1-5-32-544' in line:  # Administrators group
                                is_admin = True
                                privilege_level = PrivilegeLevel.ADMIN
                            if 'S-1-5-18' in line:  # SYSTEM
                                privilege_level = PrivilegeLevel.SYSTEM
                except:
                    pass
            
            elif os.name == 'posix':
                # Unix privilege detection
                is_root = os.geteuid() == 0
                if is_root:
                    privilege_level = PrivilegeLevel.ROOT
                
                # Get user groups
                try:
                    import grp
                    groups = [grp.getgrgid(gid).gr_name 
                            for gid in os.getgroups()]
                except:
                    pass
                
                # Check for sudo capabilities
                try:
                    result = subprocess.run(['sudo', '-l'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        capabilities.append('sudo')
                except:
                    pass
            
            info = PrivilegeInfo(
                current_user=current_user,
                privilege_level=privilege_level,
                is_admin=is_admin,
                is_root=is_root,
                groups=groups,
                capabilities=capabilities
            )
            
            self._log_operation("get_privilege_info", True, "Privilege info retrieved")
            return info
            
        except Exception as e:
            self._log_operation("get_privilege_info", False, f"Failed to get privilege info: {e}")
            raise
    
    def check_admin_privileges(self) -> bool:
        """Check if running with admin privileges
        
        Returns:
            True if admin privileges available
        """
        try:
            if os.name == 'nt':
                import ctypes
                result = ctypes.windll.shell32.IsUserAnAdmin()
                return bool(result)
            elif os.name == 'posix':
                return os.geteuid() == 0
            return False
        except:
            return False
    
    def elevate_privileges(self, method: str = "uac") -> PrivilegeOperationResult:
        """Attempt to elevate privileges
        
        Args:
            method: Elevation method (uac, sudo, etc.)
            
        Returns:
            PrivilegeOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - privilege elevation would be attempted")
                self._log_operation("elevate", False, "Safe mode enabled - operation blocked")
                return PrivilegeOperationResult(
                    success=False,
                    operation="elevate",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if os.name == 'nt':
                # Windows UAC elevation
                if method == "uac":
                    try:
                        import ctypes
                        from ctypes import wintypes
                        
                        # Get current executable
                        exe_path = sys.executable
                        
                        # Run with UAC elevation
                        result = ctypes.windll.shell32.ShellExecuteW(
                            None,
                            "runas",
                            exe_path,
                            " ".join(sys.argv),
                            None,
                            1
                        )
                        
                        if result > 32:  # Success
                            self._log_operation("elevate", True, "UAC elevation successful")
                            return PrivilegeOperationResult(
                                success=True,
                                operation="elevate",
                                message="UAC elevation successful"
                            )
                        else:
                            error_msg = f"UAC elevation failed with code {result}"
                            self._log_operation("elevate", False, error_msg)
                            return PrivilegeOperationResult(
                                success=False,
                                operation="elevate",
                                message=error_msg,
                                error=f"UAC error {result}"
                            )
                    except Exception as e:
                        error_msg = f"UAC elevation failed: {e}"
                        self._log_operation("elevate", False, error_msg)
                        return PrivilegeOperationResult(
                            success=False,
                            operation="elevate",
                            message=error_msg,
                            error=str(e)
                        )
            
            elif os.name == 'posix':
                # Unix sudo elevation
                if method == "sudo":
                    try:
                        result = subprocess.run(['sudo', 'whoami'], 
                                              capture_output=True, text=True)
                        if result.returncode == 0 and 'root' in result.stdout:
                            self._log_operation("elevate", True, "Sudo elevation successful")
                            return PrivilegeOperationResult(
                                success=True,
                                operation="elevate",
                                message="Sudo elevation successful"
                            )
                        else:
                            error_msg = "Sudo elevation failed"
                            self._log_operation("elevate", False, error_msg)
                            return PrivilegeOperationResult(
                                success=False,
                                operation="elevate",
                                message=error_msg,
                                error="Sudo failed"
                            )
                    except Exception as e:
                        error_msg = f"Sudo elevation failed: {e}"
                        self._log_operation("elevate", False, error_msg)
                        return PrivilegeOperationResult(
                            success=False,
                            operation="elevate",
                            message=error_msg,
                            error=str(e)
                        )
            
            error_msg = f"Unsupported elevation method: {method}"
            self._log_operation("elevate", False, error_msg)
            return PrivilegeOperationResult(
                success=False,
                operation="elevate",
                message=error_msg,
                error="Unsupported method"
            )
            
        except Exception as e:
            error_msg = f"Privilege elevation failed: {e}"
            self._log_operation("elevate", False, error_msg)
            return PrivilegeOperationResult(
                success=False,
                operation="elevate",
                message=error_msg,
                error=str(e)
            )
    
    def read_registry_key(self, hive: RegistryHive, key_path: str, 
                         value_name: Optional[str] = None) -> PrivilegeOperationResult:
        """Read Windows registry key/value
        
        Args:
            hive: Registry hive
            key_path: Registry key path
            value_name: Value name (None for default value)
            
        Returns:
            PrivilegeOperationResult
        """
        try:
            if os.name != 'nt':
                return PrivilegeOperationResult(
                    success=False,
                    operation="read_registry",
                    message="Registry operations only supported on Windows",
                    error="Not Windows"
                )
            
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - registry read would be performed: {hive.value}\\{key_path}")
                return PrivilegeOperationResult(
                    success=False,
                    operation="read_registry",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            import winreg
            
            # Map hive names
            hive_map = {
                RegistryHive.HKEY_CLASSES_ROOT: winreg.HKEY_CLASSES_ROOT,
                RegistryHive.HKEY_CURRENT_USER: winreg.HKEY_CURRENT_USER,
                RegistryHive.HKEY_LOCAL_MACHINE: winreg.HKEY_LOCAL_MACHINE,
                RegistryHive.HKEY_USERS: winreg.HKEY_USERS,
                RegistryHive.HKEY_CURRENT_CONFIG: winreg.HKEY_CURRENT_CONFIG
            }
            
            hive_handle = hive_map[hive]
            
            with winreg.OpenKey(hive_handle, key_path) as key:
                if value_name is None:
                    value_name = ""
                
                try:
                    value_data, value_type = winreg.QueryValueEx(key, value_name)
                    
                    registry_value = RegistryValue(
                        name=value_name,
                        value_type=str(value_type),
                        data=value_data,
                        size=len(str(value_data))
                    )
                    
                    self._log_operation("read_registry", True, f"Registry value read: {hive.value}\\{key_path}")
                    
                    return PrivilegeOperationResult(
                        success=True,
                        operation="read_registry",
                        message="Registry value read successfully",
                        data=registry_value
                    )
                    
                except FileNotFoundError:
                    error_msg = f"Registry value not found: {value_name}"
                    self._log_operation("read_registry", False, error_msg)
                    return PrivilegeOperationResult(
                        success=False,
                        operation="read_registry",
                        message=error_msg,
                        error="Value not found"
                    )
            
        except Exception as e:
            error_msg = f"Registry read failed: {e}"
            self._log_operation("read_registry", False, error_msg)
            return PrivilegeOperationResult(
                success=False,
                operation="read_registry",
                message=error_msg,
                error=str(e)
            )
    
    def write_registry_key(self, hive: RegistryHive, key_path: str, 
                          value_name: str, value_data: Any, 
                          value_type: int = None) -> PrivilegeOperationResult:
        """Write Windows registry key/value
        
        Args:
            hive: Registry hive
            key_path: Registry key path
            value_name: Value name
            value_data: Value data
            value_type: Value type (None for auto-detect)
            
        Returns:
            PrivilegeOperationResult
        """
        try:
            if os.name != 'nt':
                return PrivilegeOperationResult(
                    success=False,
                    operation="write_registry",
                    message="Registry operations only supported on Windows",
                    error="Not Windows"
                )
            
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - registry write would be performed: {hive.value}\\{key_path}")
                return PrivilegeOperationResult(
                    success=False,
                    operation="write_registry",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            import winreg
            
            # Map hive names
            hive_map = {
                RegistryHive.HKEY_CLASSES_ROOT: winreg.HKEY_CLASSES_ROOT,
                RegistryHive.HKEY_CURRENT_USER: winreg.HKEY_CURRENT_USER,
                RegistryHive.HKEY_LOCAL_MACHINE: winreg.HKEY_LOCAL_MACHINE,
                RegistryHive.HKEY_USERS: winreg.HKEY_USERS,
                RegistryHive.HKEY_CURRENT_CONFIG: winreg.HKEY_CURRENT_CONFIG
            }
            
            hive_handle = hive_map[hive]
            
            # Auto-detect value type if not specified
            if value_type is None:
                if isinstance(value_data, str):
                    value_type = winreg.REG_SZ
                elif isinstance(value_data, int):
                    value_type = winreg.REG_DWORD
                elif isinstance(value_data, bytes):
                    value_type = winreg.REG_BINARY
                else:
                    value_type = winreg.REG_SZ
            
            with winreg.CreateKey(hive_handle, key_path) as key:
                winreg.SetValueEx(key, value_name, 0, value_type, value_data)
            
            self._log_operation("write_registry", True, f"Registry value written: {hive.value}\\{key_path}")
            
            return PrivilegeOperationResult(
                success=True,
                operation="write_registry",
                message="Registry value written successfully"
            )
            
        except Exception as e:
            error_msg = f"Registry write failed: {e}"
            self._log_operation("write_registry", False, error_msg)
            return PrivilegeOperationResult(
                success=False,
                operation="write_registry",
                message=error_msg,
                error=str(e)
            )
    
    def delete_registry_key(self, hive: RegistryHive, key_path: str, 
                           value_name: Optional[str] = None) -> PrivilegeOperationResult:
        """Delete Windows registry key/value
        
        Args:
            hive: Registry hive
            key_path: Registry key path
            value_name: Value name (None to delete entire key)
            
        Returns:
            PrivilegeOperationResult
        """
        try:
            if os.name != 'nt':
                return PrivilegeOperationResult(
                    success=False,
                    operation="delete_registry",
                    message="Registry operations only supported on Windows",
                    error="Not Windows"
                )
            
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - registry delete would be performed: {hive.value}\\{key_path}")
                return PrivilegeOperationResult(
                    success=False,
                    operation="delete_registry",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            import winreg
            
            # Map hive names
            hive_map = {
                RegistryHive.HKEY_CLASSES_ROOT: winreg.HKEY_CLASSES_ROOT,
                RegistryHive.HKEY_CURRENT_USER: winreg.HKEY_CURRENT_USER,
                RegistryHive.HKEY_LOCAL_MACHINE: winreg.HKEY_LOCAL_MACHINE,
                RegistryHive.HKEY_USERS: winreg.HKEY_USERS,
                RegistryHive.HKEY_CURRENT_CONFIG: winreg.HKEY_CURRENT_CONFIG
            }
            
            hive_handle = hive_map[hive]
            
            if value_name is None:
                # Delete entire key
                winreg.DeleteKey(hive_handle, key_path)
                operation_desc = "Registry key deleted"
            else:
                # Delete specific value
                with winreg.OpenKey(hive_handle, key_path) as key:
                    winreg.DeleteValue(key, value_name)
                operation_desc = "Registry value deleted"
            
            self._log_operation("delete_registry", True, f"{operation_desc}: {hive.value}\\{key_path}")
            
            return PrivilegeOperationResult(
                success=True,
                operation="delete_registry",
                message=f"{operation_desc} successfully"
            )
            
        except Exception as e:
            error_msg = f"Registry delete failed: {e}"
            self._log_operation("delete_registry", False, error_msg)
            return PrivilegeOperationResult(
                success=False,
                operation="delete_registry",
                message=error_msg,
                error=str(e)
            )
    
    def clear_event_logs(self, log_names: Optional[List[str]] = None) -> PrivilegeOperationResult:
        """Clear Windows event logs
        
        Args:
            log_names: List of log names (None for all)
            
        Returns:
            PrivilegeOperationResult
        """
        try:
            if os.name != 'nt':
                return PrivilegeOperationResult(
                    success=False,
                    operation="clear_logs",
                    message="Event log operations only supported on Windows",
                    error="Not Windows"
                )
            
            if self.safe_mode:
                logger.warning("Safe mode enabled - event log clearing would be performed")
                return PrivilegeOperationResult(
                    success=False,
                    operation="clear_logs",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if log_names is None:
                log_names = ["Application", "System", "Security"]
            
            cleared_logs = []
            
            for log_name in log_names:
                try:
                    result = subprocess.run([
                        'wevtutil', 'cl', log_name
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        cleared_logs.append(log_name)
                    else:
                        logger.warning(f"Failed to clear log {log_name}: {result.stderr}")
                        
                except Exception as e:
                    logger.warning(f"Error clearing log {log_name}: {e}")
            
            if cleared_logs:
                self._log_operation("clear_logs", True, f"Cleared {len(cleared_logs)} event logs")
                return PrivilegeOperationResult(
                    success=True,
                    operation="clear_logs",
                    message=f"Successfully cleared {len(cleared_logs)} event logs",
                    data=cleared_logs
                )
            else:
                error_msg = "Failed to clear any event logs"
                self._log_operation("clear_logs", False, error_msg)
                return PrivilegeOperationResult(
                    success=False,
                    operation="clear_logs",
                    message=error_msg,
                    error="No logs cleared"
                )
            
        except Exception as e:
            error_msg = f"Event log clearing failed: {e}"
            self._log_operation("clear_logs", False, error_msg)
            return PrivilegeOperationResult(
                success=False,
                operation="clear_logs",
                message=error_msg,
                error=str(e)
            )
    
    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Get operation log"""
        return self.operation_log.copy()
    
    def clear_operation_log(self):
        """Clear operation log"""
        self.operation_log.clear()

# Convenience functions
def get_privilege_info() -> PrivilegeInfo:
    """Get privilege information"""
    manager = WraithPrivilegeManager()
    return manager.get_privilege_info()

def check_admin_privileges() -> bool:
    """Check admin privileges"""
    manager = WraithPrivilegeManager()
    return manager.check_admin_privileges()

def elevate_privileges(method: str = "uac") -> PrivilegeOperationResult:
    """Elevate privileges"""
    manager = WraithPrivilegeManager()
    return manager.elevate_privileges(method)

# Export main classes and functions
__all__ = [
    'WraithPrivilegeManager', 'PrivilegeLevel', 'RegistryHive', 'PrivilegeInfo', 
    'RegistryValue', 'PrivilegeOperationResult',
    'get_privilege_info', 'check_admin_privileges', 'elevate_privileges'
]
