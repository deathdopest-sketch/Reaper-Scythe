# Wraith System Operations Library
# File manipulation, process control, memory operations, privilege escalation

__version__ = "0.1.0"
__author__ = "Reaper Security Team"

# Core features implemented in L1-T004
from .files.operations import (
    WraithFileManager, FileOperation, SecureDeleteMethod, FileMetadata, FileOperationResult,
    get_file_metadata, secure_delete_file, modify_file_timestamps, hide_file, create_decoy_file
)

from .processes.operations import (
    WraithProcessManager, ProcessState, ProcessPriority, ProcessInfo, ProcessOperationResult,
    get_process_info, list_processes, terminate_process, execute_command
)

from .memory.operations import (
    WraithMemoryManager, MemoryProtection, MemoryType, MemoryRegion, MemoryOperationResult,
    get_memory_regions, read_memory, search_memory
)

from .privilege.operations import (
    WraithPrivilegeManager, PrivilegeLevel, RegistryHive, PrivilegeInfo, 
    RegistryValue, PrivilegeOperationResult,
    get_privilege_info, check_admin_privileges, elevate_privileges
)

__all__ = [
    # File operations
    'WraithFileManager', 'FileOperation', 'SecureDeleteMethod', 'FileMetadata', 'FileOperationResult',
    'get_file_metadata', 'secure_delete_file', 'modify_file_timestamps', 'hide_file', 'create_decoy_file',
    
    # Process operations
    'WraithProcessManager', 'ProcessState', 'ProcessPriority', 'ProcessInfo', 'ProcessOperationResult',
    'get_process_info', 'list_processes', 'terminate_process', 'execute_command',
    
    # Memory operations
    'WraithMemoryManager', 'MemoryProtection', 'MemoryType', 'MemoryRegion', 'MemoryOperationResult',
    'get_memory_regions', 'read_memory', 'search_memory',
    
    # Privilege operations
    'WraithPrivilegeManager', 'PrivilegeLevel', 'RegistryHive', 'PrivilegeInfo', 
    'RegistryValue', 'PrivilegeOperationResult',
    'get_privilege_info', 'check_admin_privileges', 'elevate_privileges'
]

# Will be implemented in L1-T006 and L1-T007
# Core features: secure file ops, process control, memory access
# Advanced features: registry ops, privilege escalation, log manipulation

__all__ = [
    # Will be populated as features are implemented
]
