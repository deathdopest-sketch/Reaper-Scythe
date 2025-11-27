#!/usr/bin/env python3
"""
Wraith File Operations Module
Secure file manipulation, metadata modification, and forensic operations
"""

import os
import stat
import time
import random
import hashlib
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class FileOperation(Enum):
    """File operation types"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    COPY = "copy"
    MOVE = "move"
    SECURE_DELETE = "secure_delete"
    METADATA_MODIFY = "metadata_modify"

class SecureDeleteMethod(Enum):
    """Secure deletion methods"""
    SINGLE_PASS = "single_pass"      # Single random overwrite
    DOD_STANDARD = "dod_standard"    # 3-pass DoD standard
    GUTMANN = "gutmann"              # 35-pass Gutmann method
    ZERO_FILL = "zero_fill"          # Fill with zeros
    RANDOM_FILL = "random_fill"      # Fill with random data

@dataclass
class FileMetadata:
    """File metadata information"""
    path: str
    size: int
    created: float
    modified: float
    accessed: float
    permissions: int
    owner: Optional[str] = None
    group: Optional[str] = None
    checksum_md5: Optional[str] = None
    checksum_sha256: Optional[str] = None

@dataclass
class FileOperationResult:
    """Result of file operation"""
    success: bool
    operation: FileOperation
    path: str
    message: str
    metadata: Optional[FileMetadata] = None
    error: Optional[str] = None

class WraithFileManager:
    """Advanced file operations manager"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize file manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.safe_mode = self.config.get('safe_mode', True)
        self.max_file_size = self.config.get('max_file_size', 100 * 1024 * 1024)  # 100MB
        self.operation_log = []
        
    def _validate_path(self, path: Union[str, Path]) -> Path:
        """Validate and normalize file path"""
        path = Path(path).resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
            
        if path.is_dir():
            raise IsADirectoryError(f"Path is directory: {path}")
            
        return path
    
    def _log_operation(self, operation: FileOperation, path: str, success: bool, message: str):
        """Log file operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation.value,
            'path': str(path),
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"File operation: {operation.value} on {path} - {message}")
    
    def get_metadata(self, path: Union[str, Path]) -> FileMetadata:
        """Get comprehensive file metadata
        
        Args:
            path: File path
            
        Returns:
            FileMetadata object
        """
        path = self._validate_path(path)
        stat_info = path.stat()
        
        # Calculate checksums
        md5_hash = None
        sha256_hash = None
        
        try:
            with open(path, 'rb') as f:
                content = f.read()
                md5_hash = hashlib.md5(content).hexdigest()
                sha256_hash = hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.warning(f"Could not calculate checksums for {path}: {e}")
        
        metadata = FileMetadata(
            path=str(path),
            size=stat_info.st_size,
            created=stat_info.st_ctime,
            modified=stat_info.st_mtime,
            accessed=stat_info.st_atime,
            permissions=stat_info.st_mode,
            checksum_md5=md5_hash,
            checksum_sha256=sha256_hash
        )
        
        self._log_operation(FileOperation.READ, str(path), True, "Metadata retrieved")
        return metadata
    
    def secure_delete(self, path: Union[str, Path], method: SecureDeleteMethod = SecureDeleteMethod.DOD_STANDARD) -> FileOperationResult:
        """Securely delete a file with multiple overwrite passes
        
        Args:
            path: File path to delete
            method: Secure deletion method
            
        Returns:
            FileOperationResult
        """
        try:
            path = self._validate_path(path)
            
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - secure delete would be performed on {path}")
                self._log_operation(FileOperation.SECURE_DELETE, str(path), False, "Safe mode enabled - operation blocked")
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.SECURE_DELETE,
                    path=str(path),
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            file_size = path.stat().st_size
            
            # Generate overwrite patterns based on method
            patterns = self._generate_overwrite_patterns(method, file_size)
            
            with open(path, 'r+b') as f:
                for i, pattern in enumerate(patterns):
                    f.seek(0)
                    f.write(pattern)
                    f.flush()
                    os.fsync(f.fileno())
                    logger.debug(f"Overwrite pass {i+1}/{len(patterns)} completed")
            
            # Remove the file
            path.unlink()
            
            self._log_operation(FileOperation.SECURE_DELETE, str(path), True, f"Securely deleted using {method.value}")
            
            return FileOperationResult(
                success=True,
                operation=FileOperation.SECURE_DELETE,
                path=str(path),
                message=f"File securely deleted using {method.value} method"
            )
            
        except Exception as e:
            error_msg = f"Secure delete failed: {e}"
            logger.error(error_msg)
            self._log_operation(FileOperation.SECURE_DELETE, str(path), False, error_msg)
            
            return FileOperationResult(
                success=False,
                operation=FileOperation.SECURE_DELETE,
                path=str(path),
                message=error_msg,
                error=str(e)
            )
    
    def _generate_overwrite_patterns(self, method: SecureDeleteMethod, file_size: int) -> List[bytes]:
        """Generate overwrite patterns for secure deletion"""
        patterns = []
        
        if method == SecureDeleteMethod.SINGLE_PASS:
            patterns.append(os.urandom(file_size))
            
        elif method == SecureDeleteMethod.ZERO_FILL:
            patterns.append(b'\x00' * file_size)
            
        elif method == SecureDeleteMethod.RANDOM_FILL:
            patterns.append(os.urandom(file_size))
            
        elif method == SecureDeleteMethod.DOD_STANDARD:
            # DoD 5220.22-M standard: random, complement, random
            patterns.append(os.urandom(file_size))
            patterns.append(bytes([~b for b in patterns[0]]))
            patterns.append(os.urandom(file_size))
            
        elif method == SecureDeleteMethod.GUTMANN:
            # Gutmann method: 35 passes with specific patterns
            for i in range(35):
                if i < 4 or i > 30:
                    patterns.append(os.urandom(file_size))
                else:
                    # Specific patterns for passes 4-30
                    pattern = bytearray(file_size)
                    for j in range(file_size):
                        pattern[j] = random.randint(0, 255)
                    patterns.append(bytes(pattern))
        
        return patterns
    
    def modify_metadata(self, path: Union[str, Path], 
                       created: Optional[float] = None,
                       modified: Optional[float] = None,
                       accessed: Optional[float] = None) -> FileOperationResult:
        """Modify file timestamps
        
        Args:
            path: File path
            created: Creation timestamp
            modified: Modification timestamp
            accessed: Access timestamp
            
        Returns:
            FileOperationResult
        """
        try:
            path = self._validate_path(path)
            
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - metadata modification would be performed on {path}")
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.METADATA_MODIFY,
                    path=str(path),
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Get current timestamps
            stat_info = path.stat()
            current_times = (stat_info.st_atime, stat_info.st_mtime)
            
            # Prepare new timestamps
            new_times = []
            for i, new_time in enumerate([accessed, modified]):
                if new_time is not None:
                    new_times.append(new_time)
                else:
                    new_times.append(current_times[i])
            
            # Apply timestamp changes
            os.utime(path, tuple(new_times))
            
            # Handle creation time if provided (Windows only)
            if created is not None and os.name == 'nt':
                try:
                    import win32file
                    import win32con
                    import pywintypes
                    
                    handle = win32file.CreateFile(
                        str(path),
                        win32con.GENERIC_WRITE,
                        win32con.FILE_SHARE_WRITE,
                        None,
                        win32con.OPEN_EXISTING,
                        win32con.FILE_ATTRIBUTE_NORMAL,
                        None
                    )
                    
                    win32file.SetFileTime(handle, pywintypes.Time(created), None, None)
                    win32file.CloseHandle(handle)
                    
                except ImportError:
                    logger.warning("win32file not available - creation time not modified")
                except Exception as e:
                    logger.warning(f"Could not modify creation time: {e}")
            
            self._log_operation(FileOperation.METADATA_MODIFY, str(path), True, "Metadata modified")
            
            return FileOperationResult(
                success=True,
                operation=FileOperation.METADATA_MODIFY,
                path=str(path),
                message="File metadata modified successfully",
                metadata=self.get_metadata(path)
            )
            
        except Exception as e:
            error_msg = f"Metadata modification failed: {e}"
            logger.error(error_msg)
            self._log_operation(FileOperation.METADATA_MODIFY, str(path), False, error_msg)
            
            return FileOperationResult(
                success=False,
                operation=FileOperation.METADATA_MODIFY,
                path=str(path),
                message=error_msg,
                error=str(e)
            )
    
    def hide_file(self, path: Union[str, Path]) -> FileOperationResult:
        """Hide file by modifying attributes
        
        Args:
            path: File path
            
        Returns:
            FileOperationResult
        """
        try:
            path = self._validate_path(path)
            
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - file hiding would be performed on {path}")
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.METADATA_MODIFY,
                    path=str(path),
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Hide file (Windows)
            if os.name == 'nt':
                import win32file
                import win32con
                
                win32file.SetFileAttributes(str(path), win32con.FILE_ATTRIBUTE_HIDDEN)
            
            # Hide file (Unix)
            else:
                stat_info = path.stat()
                new_mode = stat_info.st_mode & ~stat.S_IWRITE
                path.chmod(new_mode)
            
            self._log_operation(FileOperation.METADATA_MODIFY, str(path), True, "File hidden")
            
            return FileOperationResult(
                success=True,
                operation=FileOperation.METADATA_MODIFY,
                path=str(path),
                message="File hidden successfully"
            )
            
        except Exception as e:
            error_msg = f"File hiding failed: {e}"
            logger.error(error_msg)
            self._log_operation(FileOperation.METADATA_MODIFY, str(path), False, error_msg)
            
            return FileOperationResult(
                success=False,
                operation=FileOperation.METADATA_MODIFY,
                path=str(path),
                message=error_msg,
                error=str(e)
            )
    
    def create_decoy_file(self, path: Union[str, Path], content: bytes = None) -> FileOperationResult:
        """Create a decoy file with random content
        
        Args:
            path: File path for decoy
            content: Optional content (if None, generates random)
            
        Returns:
            FileOperationResult
        """
        try:
            path = Path(path).resolve()
            
            if content is None:
                content = os.urandom(random.randint(1024, 10240))  # 1KB to 10KB
            
            with open(path, 'wb') as f:
                f.write(content)
            
            self._log_operation(FileOperation.WRITE, str(path), True, "Decoy file created")
            
            return FileOperationResult(
                success=True,
                operation=FileOperation.WRITE,
                path=str(path),
                message="Decoy file created successfully"
            )
            
        except Exception as e:
            error_msg = f"Decoy file creation failed: {e}"
            logger.error(error_msg)
            self._log_operation(FileOperation.WRITE, str(path), False, error_msg)
            
            return FileOperationResult(
                success=False,
                operation=FileOperation.WRITE,
                path=str(path),
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
def get_file_metadata(path: Union[str, Path]) -> FileMetadata:
    """Get file metadata"""
    manager = WraithFileManager()
    return manager.get_metadata(path)

def secure_delete_file(path: Union[str, Path], method: SecureDeleteMethod = SecureDeleteMethod.DOD_STANDARD) -> FileOperationResult:
    """Securely delete a file"""
    manager = WraithFileManager()
    return manager.secure_delete(path, method)

def modify_file_timestamps(path: Union[str, Path], 
                          created: Optional[float] = None,
                          modified: Optional[float] = None,
                          accessed: Optional[float] = None) -> FileOperationResult:
    """Modify file timestamps"""
    manager = WraithFileManager()
    return manager.modify_metadata(path, created, modified, accessed)

def hide_file(path: Union[str, Path]) -> FileOperationResult:
    """Hide a file"""
    manager = WraithFileManager()
    return manager.hide_file(path)

def create_decoy_file(path: Union[str, Path], content: bytes = None) -> FileOperationResult:
    """Create a decoy file"""
    manager = WraithFileManager()
    return manager.create_decoy_file(path, content)

# Export main classes and functions
__all__ = [
    'WraithFileManager', 'FileOperation', 'SecureDeleteMethod', 'FileMetadata', 'FileOperationResult',
    'get_file_metadata', 'secure_delete_file', 'modify_file_timestamps', 'hide_file', 'create_decoy_file'
]
