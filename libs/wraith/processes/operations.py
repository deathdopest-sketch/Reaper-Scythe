#!/usr/bin/env python3
"""
Wraith Process Operations Module
Process control, injection, monitoring, and manipulation
"""

import os
import psutil
import subprocess
import threading
import time
import logging
from typing import Optional, List, Dict, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ProcessState(Enum):
    """Process states"""
    RUNNING = "running"
    SLEEPING = "sleeping"
    DISK_SLEEP = "disk_sleep"
    STOPPED = "stopped"
    TRACING_STOP = "tracing_stop"
    ZOMBIE = "zombie"
    DEAD = "dead"
    WAKE_KILL = "wake_kill"
    WAKING = "waking"
    IDLE = "idle"
    LOCKED = "locked"
    WAITING = "waiting"

class ProcessPriority(Enum):
    """Process priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    REALTIME = "realtime"

@dataclass
class ProcessInfo:
    """Process information"""
    pid: int
    name: str
    status: ProcessState
    cpu_percent: float
    memory_percent: float
    memory_info: Dict[str, Any]
    create_time: float
    parent_pid: Optional[int]
    command_line: Optional[str]
    executable: Optional[str]
    working_directory: Optional[str]
    environment: Dict[str, str]

@dataclass
class ProcessOperationResult:
    """Result of process operation"""
    success: bool
    operation: str
    pid: int
    message: str
    error: Optional[str] = None
    data: Optional[Any] = None

class WraithProcessManager:
    """Advanced process operations manager"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize process manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.safe_mode = self.config.get('safe_mode', True)
        self.max_processes = self.config.get('max_processes', 100)
        self.operation_log = []
        self.monitored_processes = {}
        
    def _log_operation(self, operation: str, pid: int, success: bool, message: str):
        """Log process operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'pid': pid,
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"Process operation: {operation} on PID {pid} - {message}")
    
    def get_process_info(self, pid: int) -> ProcessInfo:
        """Get comprehensive process information
        
        Args:
            pid: Process ID
            
        Returns:
            ProcessInfo object
        """
        try:
            process = psutil.Process(pid)
            
            # Get process state
            try:
                status = ProcessState(process.status())
            except ValueError:
                status = ProcessState.RUNNING  # Default fallback
            
            # Get memory info
            memory_info = process.memory_info()
            memory_dict = {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent()
            }
            
            # Get command line
            try:
                cmdline = ' '.join(process.cmdline())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                cmdline = None
            
            # Get executable path
            try:
                executable = process.exe()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                executable = None
            
            # Get working directory
            try:
                cwd = process.cwd()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                cwd = None
            
            # Get environment
            try:
                env = process.environ()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                env = {}
            
            info = ProcessInfo(
                pid=pid,
                name=process.name(),
                status=status,
                cpu_percent=process.cpu_percent(),
                memory_percent=process.memory_percent(),
                memory_info=memory_dict,
                create_time=process.create_time(),
                parent_pid=process.ppid() if process.ppid() else None,
                command_line=cmdline,
                executable=executable,
                working_directory=cwd,
                environment=env
            )
            
            self._log_operation("get_info", pid, True, "Process info retrieved")
            return info
            
        except psutil.NoSuchProcess:
            raise ProcessLookupError(f"Process {pid} not found")
        except psutil.AccessDenied:
            raise PermissionError(f"Access denied to process {pid}")
        except Exception as e:
            self._log_operation("get_info", pid, False, f"Failed to get process info: {e}")
            raise
    
    def list_processes(self, name_filter: Optional[str] = None) -> List[ProcessInfo]:
        """List all processes with optional name filtering
        
        Args:
            name_filter: Optional process name filter
            
        Returns:
            List of ProcessInfo objects
        """
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    if name_filter and name_filter.lower() not in proc.info['name'].lower():
                        continue
                    
                    process_info = self.get_process_info(proc.info['pid'])
                    processes.append(process_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self._log_operation("list_processes", 0, True, f"Listed {len(processes)} processes")
            return processes
            
        except Exception as e:
            self._log_operation("list_processes", 0, False, f"Failed to list processes: {e}")
            raise
    
    def terminate_process(self, pid: int, force: bool = False) -> ProcessOperationResult:
        """Terminate a process
        
        Args:
            pid: Process ID
            force: Force termination
            
        Returns:
            ProcessOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - process termination would be performed on PID {pid}")
                self._log_operation("terminate", pid, False, "Safe mode enabled - operation blocked")
                return ProcessOperationResult(
                    success=False,
                    operation="terminate",
                    pid=pid,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            process = psutil.Process(pid)
            
            if force:
                process.kill()
                method = "killed"
            else:
                process.terminate()
                method = "terminated"
            
            self._log_operation("terminate", pid, True, f"Process {method}")
            
            return ProcessOperationResult(
                success=True,
                operation="terminate",
                pid=pid,
                message=f"Process {method} successfully"
            )
            
        except psutil.NoSuchProcess:
            error_msg = f"Process {pid} not found"
            self._log_operation("terminate", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="terminate",
                pid=pid,
                message=error_msg,
                error="Process not found"
            )
        except psutil.AccessDenied:
            error_msg = f"Access denied to process {pid}"
            self._log_operation("terminate", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="terminate",
                pid=pid,
                message=error_msg,
                error="Access denied"
            )
        except Exception as e:
            error_msg = f"Process termination failed: {e}"
            self._log_operation("terminate", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="terminate",
                pid=pid,
                message=error_msg,
                error=str(e)
            )
    
    def suspend_process(self, pid: int) -> ProcessOperationResult:
        """Suspend a process
        
        Args:
            pid: Process ID
            
        Returns:
            ProcessOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - process suspension would be performed on PID {pid}")
                return ProcessOperationResult(
                    success=False,
                    operation="suspend",
                    pid=pid,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            process = psutil.Process(pid)
            process.suspend()
            
            self._log_operation("suspend", pid, True, "Process suspended")
            
            return ProcessOperationResult(
                success=True,
                operation="suspend",
                pid=pid,
                message="Process suspended successfully"
            )
            
        except psutil.NoSuchProcess:
            error_msg = f"Process {pid} not found"
            self._log_operation("suspend", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="suspend",
                pid=pid,
                message=error_msg,
                error="Process not found"
            )
        except psutil.AccessDenied:
            error_msg = f"Access denied to process {pid}"
            self._log_operation("suspend", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="suspend",
                pid=pid,
                message=error_msg,
                error="Access denied"
            )
        except Exception as e:
            error_msg = f"Process suspension failed: {e}"
            self._log_operation("suspend", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="suspend",
                pid=pid,
                message=error_msg,
                error=str(e)
            )
    
    def resume_process(self, pid: int) -> ProcessOperationResult:
        """Resume a suspended process
        
        Args:
            pid: Process ID
            
        Returns:
            ProcessOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - process resumption would be performed on PID {pid}")
                return ProcessOperationResult(
                    success=False,
                    operation="resume",
                    pid=pid,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            process = psutil.Process(pid)
            process.resume()
            
            self._log_operation("resume", pid, True, "Process resumed")
            
            return ProcessOperationResult(
                success=True,
                operation="resume",
                pid=pid,
                message="Process resumed successfully"
            )
            
        except psutil.NoSuchProcess:
            error_msg = f"Process {pid} not found"
            self._log_operation("resume", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="resume",
                pid=pid,
                message=error_msg,
                error="Process not found"
            )
        except psutil.AccessDenied:
            error_msg = f"Access denied to process {pid}"
            self._log_operation("resume", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="resume",
                pid=pid,
                message=error_msg,
                error="Access denied"
            )
        except Exception as e:
            error_msg = f"Process resumption failed: {e}"
            self._log_operation("resume", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="resume",
                pid=pid,
                message=error_msg,
                error=str(e)
            )
    
    def set_process_priority(self, pid: int, priority: ProcessPriority) -> ProcessOperationResult:
        """Set process priority
        
        Args:
            pid: Process ID
            priority: Priority level
            
        Returns:
            ProcessOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - priority change would be performed on PID {pid}")
                return ProcessOperationResult(
                    success=False,
                    operation="set_priority",
                    pid=pid,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            process = psutil.Process(pid)
            
            # Map priority to psutil constants
            priority_map = {
                ProcessPriority.LOW: psutil.BELOW_NORMAL_PRIORITY_CLASS,
                ProcessPriority.NORMAL: psutil.NORMAL_PRIORITY_CLASS,
                ProcessPriority.HIGH: psutil.HIGH_PRIORITY_CLASS,
                ProcessPriority.REALTIME: psutil.REALTIME_PRIORITY_CLASS
            }
            
            process.nice(priority_map[priority])
            
            self._log_operation("set_priority", pid, True, f"Priority set to {priority.value}")
            
            return ProcessOperationResult(
                success=True,
                operation="set_priority",
                pid=pid,
                message=f"Process priority set to {priority.value}"
            )
            
        except psutil.NoSuchProcess:
            error_msg = f"Process {pid} not found"
            self._log_operation("set_priority", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="set_priority",
                pid=pid,
                message=error_msg,
                error="Process not found"
            )
        except psutil.AccessDenied:
            error_msg = f"Access denied to process {pid}"
            self._log_operation("set_priority", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="set_priority",
                pid=pid,
                message=error_msg,
                error="Access denied"
            )
        except Exception as e:
            error_msg = f"Priority setting failed: {e}"
            self._log_operation("set_priority", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="set_priority",
                pid=pid,
                message=error_msg,
                error=str(e)
            )
    
    def execute_command(self, command: str, args: Optional[List[str]] = None, 
                       timeout: Optional[int] = None) -> ProcessOperationResult:
        """Execute a command and return result
        
        Args:
            command: Command to execute
            args: Command arguments
            timeout: Timeout in seconds
            
        Returns:
            ProcessOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - command execution would be performed: {command}")
                return ProcessOperationResult(
                    success=False,
                    operation="execute",
                    pid=0,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            cmd_args = [command]
            if args:
                cmd_args.extend(args)
            
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            self._log_operation("execute", result.pid, True, f"Command executed: {command}")
            
            return ProcessOperationResult(
                success=True,
                operation="execute",
                pid=result.pid,
                message=f"Command executed successfully (exit code: {result.returncode})",
                data={
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            )
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out: {command}"
            self._log_operation("execute", 0, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="execute",
                pid=0,
                message=error_msg,
                error="Timeout"
            )
        except Exception as e:
            error_msg = f"Command execution failed: {e}"
            self._log_operation("execute", 0, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="execute",
                pid=0,
                message=error_msg,
                error=str(e)
            )
    
    def monitor_process(self, pid: int, callback: Callable[[ProcessInfo], None], 
                       interval: float = 1.0) -> ProcessOperationResult:
        """Monitor a process with callback
        
        Args:
            pid: Process ID to monitor
            callback: Callback function for process updates
            interval: Monitoring interval in seconds
            
        Returns:
            ProcessOperationResult
        """
        try:
            if pid in self.monitored_processes:
                return ProcessOperationResult(
                    success=False,
                    operation="monitor",
                    pid=pid,
                    message="Process already being monitored",
                    error="Already monitored"
                )
            
            # Check if process exists
            try:
                psutil.Process(pid)
            except psutil.NoSuchProcess:
                return ProcessOperationResult(
                    success=False,
                    operation="monitor",
                    pid=pid,
                    message="Process not found",
                    error="Process not found"
                )
            
            def monitor_worker():
                while pid in self.monitored_processes:
                    try:
                        process_info = self.get_process_info(pid)
                        callback(process_info)
                        time.sleep(interval)
                    except ProcessLookupError:
                        # Process no longer exists
                        break
                    except Exception as e:
                        logger.error(f"Monitor error for PID {pid}: {e}")
                        break
                
                # Clean up monitoring
                if pid in self.monitored_processes:
                    del self.monitored_processes[pid]
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
            monitor_thread.start()
            
            self.monitored_processes[pid] = {
                'thread': monitor_thread,
                'callback': callback,
                'interval': interval
            }
            
            self._log_operation("monitor", pid, True, "Process monitoring started")
            
            return ProcessOperationResult(
                success=True,
                operation="monitor",
                pid=pid,
                message="Process monitoring started"
            )
            
        except Exception as e:
            error_msg = f"Process monitoring failed: {e}"
            self._log_operation("monitor", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="monitor",
                pid=pid,
                message=error_msg,
                error=str(e)
            )
    
    def stop_monitoring(self, pid: int) -> ProcessOperationResult:
        """Stop monitoring a process
        
        Args:
            pid: Process ID
            
        Returns:
            ProcessOperationResult
        """
        try:
            if pid not in self.monitored_processes:
                return ProcessOperationResult(
                    success=False,
                    operation="stop_monitor",
                    pid=pid,
                    message="Process not being monitored",
                    error="Not monitored"
                )
            
            del self.monitored_processes[pid]
            
            self._log_operation("stop_monitor", pid, True, "Process monitoring stopped")
            
            return ProcessOperationResult(
                success=True,
                operation="stop_monitor",
                pid=pid,
                message="Process monitoring stopped"
            )
            
        except Exception as e:
            error_msg = f"Stop monitoring failed: {e}"
            self._log_operation("stop_monitor", pid, False, error_msg)
            return ProcessOperationResult(
                success=False,
                operation="stop_monitor",
                pid=pid,
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
def get_process_info(pid: int) -> ProcessInfo:
    """Get process information"""
    manager = WraithProcessManager()
    return manager.get_process_info(pid)

def list_processes(name_filter: Optional[str] = None) -> List[ProcessInfo]:
    """List processes"""
    manager = WraithProcessManager()
    return manager.list_processes(name_filter)

def terminate_process(pid: int, force: bool = False) -> ProcessOperationResult:
    """Terminate a process"""
    manager = WraithProcessManager()
    return manager.terminate_process(pid, force)

def execute_command(command: str, args: Optional[List[str]] = None, 
                   timeout: Optional[int] = None) -> ProcessOperationResult:
    """Execute a command"""
    manager = WraithProcessManager()
    return manager.execute_command(command, args, timeout)

# Export main classes and functions
__all__ = [
    'WraithProcessManager', 'ProcessState', 'ProcessPriority', 'ProcessInfo', 'ProcessOperationResult',
    'get_process_info', 'list_processes', 'terminate_process', 'execute_command'
]
