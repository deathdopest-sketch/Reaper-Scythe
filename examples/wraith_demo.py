#!/usr/bin/env python3
"""
Wraith Library Demo - Reaper Security Language
Demonstrates system operations: file manipulation, process control, memory operations, and privilege escalation
"""

import os
import tempfile
import time
from libs.wraith.files.operations import (
    WraithFileManager, SecureDeleteMethod, get_file_metadata, 
    secure_delete_file, modify_file_timestamps, hide_file, create_decoy_file
)
from libs.wraith.processes.operations import (
    WraithProcessManager, ProcessPriority, get_process_info, 
    list_processes, terminate_process, execute_command
)
from libs.wraith.memory.operations import (
    WraithMemoryManager, MemoryProtection, get_memory_regions, 
    read_memory, search_memory
)
from libs.wraith.privilege.operations import (
    WraithPrivilegeManager, PrivilegeLevel, RegistryHive, 
    get_privilege_info, check_admin_privileges, elevate_privileges
)

def demo_file_operations():
    """Demonstrate file operations"""
    print("=== FILE OPERATIONS DEMO ===")
    
    # Initialize file manager
    file_manager = WraithFileManager({'safe_mode': True})  # Safe mode for demo
    
    # Create test file
    test_data = b"This is sensitive data that needs secure handling!"
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(test_data)
        temp_file_path = temp_file.name
    
    print(f"Created test file: {temp_file_path}")
    print(f"Test data: {test_data}")
    
    try:
        # Get file metadata
        print("\n--- File Metadata ---")
        metadata = file_manager.get_metadata(temp_file_path)
        print(f"File size: {metadata.size} bytes")
        print(f"Created: {time.ctime(metadata.created)}")
        print(f"Modified: {time.ctime(metadata.modified)}")
        print(f"MD5 checksum: {metadata.checksum_md5}")
        print(f"SHA256 checksum: {metadata.checksum_sha256}")
        
        # Secure delete (safe mode - blocked)
        print("\n--- Secure Delete ---")
        result = file_manager.secure_delete(temp_file_path, SecureDeleteMethod.DOD_STANDARD)
        print(f"Secure delete result: {result.success}")
        print(f"Message: {result.message}")
        
        # Modify timestamps (safe mode - blocked)
        print("\n--- Timestamp Modification ---")
        result = file_manager.modify_metadata(
            temp_file_path,
            created=time.time() - 86400,  # 1 day ago
            modified=time.time() - 3600   # 1 hour ago
        )
        print(f"Timestamp modification result: {result.success}")
        print(f"Message: {result.message}")
        
        # Hide file (safe mode - blocked)
        print("\n--- File Hiding ---")
        result = file_manager.hide_file(temp_file_path)
        print(f"Hide file result: {result.success}")
        print(f"Message: {result.message}")
        
        # Create decoy file
        print("\n--- Decoy File Creation ---")
        decoy_path = temp_file_path + ".decoy"
        result = file_manager.create_decoy_file(decoy_path, b"Decoy content")
        print(f"Decoy creation result: {result.success}")
        print(f"Message: {result.message}")
        
        if result.success:
            print(f"Decoy file created: {decoy_path}")
            with open(decoy_path, 'rb') as f:
                decoy_content = f.read()
            print(f"Decoy content: {decoy_content}")
            os.unlink(decoy_path)
        
        # Operation log
        print("\n--- Operation Log ---")
        log = file_manager.get_operation_log()
        print(f"Total operations logged: {len(log)}")
        for entry in log:
            print(f"  {entry['operation']}: {entry['success']} - {entry['message']}")
    
    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def demo_process_operations():
    """Demonstrate process operations"""
    print("\n=== PROCESS OPERATIONS DEMO ===")
    
    # Initialize process manager
    process_manager = WraithProcessManager({'safe_mode': True})  # Safe mode for demo
    
    current_pid = os.getpid()
    print(f"Current process PID: {current_pid}")
    
    # Get process information
    print("\n--- Process Information ---")
    try:
        info = process_manager.get_process_info(current_pid)
        print(f"Process name: {info.name}")
        print(f"Status: {info.status.value}")
        print(f"CPU usage: {info.cpu_percent}%")
        print(f"Memory usage: {info.memory_percent}%")
        print(f"Memory info: {info.memory_info}")
        print(f"Command line: {info.command_line}")
        print(f"Working directory: {info.working_directory}")
        print(f"Parent PID: {info.parent_pid}")
    except Exception as e:
        print(f"Error getting process info: {e}")
    
    # List processes
    print("\n--- Process Listing ---")
    try:
        processes = process_manager.list_processes()
        print(f"Total processes found: {len(processes)}")
        
        # Show first 5 processes
        for i, proc in enumerate(processes[:5]):
            print(f"  {i+1}. PID {proc.pid}: {proc.name} ({proc.status.value})")
        
        # Filter for Python processes
        python_processes = process_manager.list_processes("python")
        print(f"Python processes found: {len(python_processes)}")
        
    except Exception as e:
        print(f"Error listing processes: {e}")
    
    # Process control operations (safe mode - blocked)
    print("\n--- Process Control ---")
    result = process_manager.terminate_process(current_pid)
    print(f"Terminate process result: {result.success}")
    print(f"Message: {result.message}")
    
    result = process_manager.suspend_process(current_pid)
    print(f"Suspend process result: {result.success}")
    print(f"Message: {result.message}")
    
    result = process_manager.set_process_priority(current_pid, ProcessPriority.HIGH)
    print(f"Set priority result: {result.success}")
    print(f"Message: {result.message}")
    
    # Command execution (safe mode - blocked)
    print("\n--- Command Execution ---")
    result = process_manager.execute_command("echo", ["Hello from Wraith!"])
    print(f"Command execution result: {result.success}")
    print(f"Message: {result.message}")
    
    # Process monitoring
    print("\n--- Process Monitoring ---")
    callback_called = False
    callback_data = []
    
    def monitor_callback(process_info):
        nonlocal callback_called, callback_data
        callback_called = True
        callback_data.append(process_info)
        print(f"Monitor callback: PID {process_info.pid}, CPU {process_info.cpu_percent}%")
    
    result = process_manager.monitor_process(current_pid, monitor_callback, 0.5)
    print(f"Start monitoring result: {result.success}")
    print(f"Message: {result.message}")
    
    if result.success:
        # Wait a bit for monitoring
        time.sleep(1.5)
        
        # Stop monitoring
        stop_result = process_manager.stop_monitoring(current_pid)
        print(f"Stop monitoring result: {stop_result.success}")
        print(f"Callbacks received: {len(callback_data)}")
    
    # Operation log
    print("\n--- Operation Log ---")
    log = process_manager.get_operation_log()
    print(f"Total operations logged: {len(log)}")
    for entry in log:
        print(f"  {entry['operation']}: {entry['success']} - {entry['message']}")

def demo_memory_operations():
    """Demonstrate memory operations"""
    print("\n=== MEMORY OPERATIONS DEMO ===")
    
    # Initialize memory manager
    memory_manager = WraithMemoryManager({'safe_mode': True})  # Safe mode for demo
    
    # Get memory regions
    print("\n--- Memory Regions ---")
    try:
        regions = memory_manager.get_memory_regions()
        print(f"Memory regions found: {len(regions)}")
        
        if regions:
            for i, region in enumerate(regions[:3]):  # Show first 3 regions
                print(f"  Region {i+1}:")
                print(f"    Address: 0x{region.start:x} - 0x{region.end:x}")
                print(f"    Size: {region.size} bytes")
                print(f"    Protection: {region.protection.value}")
                print(f"    Type: {region.memory_type.value}")
                if region.path:
                    print(f"    Path: {region.path}")
        else:
            print("  No memory regions available (Windows limitation)")
    
    except Exception as e:
        print(f"Error getting memory regions: {e}")
    
    # Memory read/write operations (safe mode - blocked)
    print("\n--- Memory Operations ---")
    test_address = 0x1000
    test_data = b"Test memory data"
    
    result = memory_manager.read_memory(test_address, 1024)
    print(f"Memory read result: {result.success}")
    print(f"Message: {result.message}")
    
    result = memory_manager.write_memory(test_address, test_data)
    print(f"Memory write result: {result.success}")
    print(f"Message: {result.message}")
    
    # Memory search (safe mode - blocked)
    print("\n--- Memory Search ---")
    matches = memory_manager.search_memory(b"search pattern")
    print(f"Memory search matches: {len(matches)}")
    
    # Memory allocation/free (safe mode - blocked)
    print("\n--- Memory Allocation ---")
    result = memory_manager.allocate_memory(4096, MemoryProtection.READ_WRITE)
    print(f"Memory allocation result: {result.success}")
    print(f"Message: {result.message}")
    
    result = memory_manager.free_memory(test_address, 4096)
    print(f"Memory free result: {result.success}")
    print(f"Message: {result.message}")
    
    # Operation log
    print("\n--- Operation Log ---")
    log = memory_manager.get_operation_log()
    print(f"Total operations logged: {len(log)}")
    for entry in log:
        print(f"  {entry['operation']}: {entry['success']} - {entry['message']}")

def demo_privilege_operations():
    """Demonstrate privilege operations"""
    print("\n=== PRIVILEGE OPERATIONS DEMO ===")
    
    # Initialize privilege manager
    privilege_manager = WraithPrivilegeManager({'safe_mode': True})  # Safe mode for demo
    
    # Get privilege information
    print("\n--- Privilege Information ---")
    try:
        info = privilege_manager.get_privilege_info()
        print(f"Current user: {info.current_user}")
        print(f"Privilege level: {info.privilege_level.value}")
        print(f"Is admin: {info.is_admin}")
        print(f"Is root: {info.is_root}")
        print(f"Groups: {info.groups}")
        print(f"Capabilities: {info.capabilities}")
    except Exception as e:
        print(f"Error getting privilege info: {e}")
    
    # Check admin privileges
    print("\n--- Admin Privilege Check ---")
    is_admin = privilege_manager.check_admin_privileges()
    print(f"Has admin privileges: {is_admin}")
    
    # Privilege elevation (safe mode - blocked)
    print("\n--- Privilege Elevation ---")
    result = privilege_manager.elevate_privileges("uac")
    print(f"UAC elevation result: {result.success}")
    print(f"Message: {result.message}")
    
    result = privilege_manager.elevate_privileges("sudo")
    print(f"Sudo elevation result: {result.success}")
    print(f"Message: {result.message}")
    
    # Registry operations (Windows only, safe mode - blocked)
    if os.name == 'nt':
        print("\n--- Registry Operations ---")
        result = privilege_manager.read_registry_key(
            RegistryHive.HKEY_CURRENT_USER,
            "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer"
        )
        print(f"Registry read result: {result.success}")
        print(f"Message: {result.message}")
        
        result = privilege_manager.write_registry_key(
            RegistryHive.HKEY_CURRENT_USER,
            "Software\\TestKey",
            "TestValue",
            "test data"
        )
        print(f"Registry write result: {result.success}")
        print(f"Message: {result.message}")
        
        result = privilege_manager.delete_registry_key(
            RegistryHive.HKEY_CURRENT_USER,
            "Software\\TestKey"
        )
        print(f"Registry delete result: {result.success}")
        print(f"Message: {result.message}")
        
        # Event log operations
        print("\n--- Event Log Operations ---")
        result = privilege_manager.clear_event_logs()
        print(f"Clear event logs result: {result.success}")
        print(f"Message: {result.message}")
    else:
        print("\n--- Registry Operations ---")
        print("Registry operations only available on Windows")
    
    # Operation log
    print("\n--- Operation Log ---")
    log = privilege_manager.get_operation_log()
    print(f"Total operations logged: {len(log)}")
    for entry in log:
        print(f"  {entry['operation']}: {entry['success']} - {entry['message']}")

def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print("\n=== CONVENIENCE FUNCTIONS DEMO ===")
    
    # File convenience functions
    print("\n--- File Convenience Functions ---")
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test data for convenience functions")
        temp_file_path = temp_file.name
    
    try:
        metadata = get_file_metadata(temp_file_path)
        print(f"File metadata: {metadata.size} bytes")
        
        result = secure_delete_file(temp_file_path)
        print(f"Secure delete: {result.success}")
        
        result = modify_file_timestamps(temp_file_path)
        print(f"Modify timestamps: {result.success}")
        
        result = hide_file(temp_file_path)
        print(f"Hide file: {result.success}")
        
        decoy_path = temp_file_path + ".decoy"
        result = create_decoy_file(decoy_path)
        print(f"Create decoy: {result.success}")
        if os.path.exists(decoy_path):
            os.unlink(decoy_path)
    
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    # Process convenience functions
    print("\n--- Process Convenience Functions ---")
    current_pid = os.getpid()
    
    info = get_process_info(current_pid)
    print(f"Process info: PID {info.pid}, Name {info.name}")
    
    processes = list_processes()
    print(f"Total processes: {len(processes)}")
    
    result = terminate_process(current_pid)
    print(f"Terminate process: {result.success}")
    
    result = execute_command("echo", ["Hello"])
    print(f"Execute command: {result.success}")
    
    # Memory convenience functions
    print("\n--- Memory Convenience Functions ---")
    regions = get_memory_regions()
    print(f"Memory regions: {len(regions)}")
    
    result = read_memory(0x1000, 1024)
    print(f"Read memory: {result.success}")
    
    matches = search_memory(b"pattern")
    print(f"Search memory matches: {len(matches)}")
    
    # Privilege convenience functions
    print("\n--- Privilege Convenience Functions ---")
    info = get_privilege_info()
    print(f"Privilege info: User {info.current_user}, Level {info.privilege_level.value}")
    
    is_admin = check_admin_privileges()
    print(f"Admin privileges: {is_admin}")
    
    result = elevate_privileges("uac")
    print(f"Elevate privileges: {result.success}")

if __name__ == "__main__":
    print("Wraith Library Demo - Reaper Security Language")
    print("=" * 50)
    
    try:
        demo_file_operations()
        demo_process_operations()
        demo_memory_operations()
        demo_privilege_operations()
        demo_convenience_functions()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
