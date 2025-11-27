#!/usr/bin/env python3
"""
Shadow Tor Integration Module
Tor network integration, circuit management, and anonymity features
"""

import requests
import time
import random
import logging
import subprocess
import threading
import json
import os
import tempfile
from typing import Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse
import socket

logger = logging.getLogger(__name__)

class TorCircuitStatus(Enum):
    """Tor circuit status"""
    BUILDING = "building"
    BUILT = "built"
    EXTENDED = "extended"
    FAILED = "failed"
    CLOSED = "closed"

class TorNodeType(Enum):
    """Tor node types"""
    RELAY = "relay"
    EXIT = "exit"
    GUARD = "guard"
    BRIDGE = "bridge"

@dataclass
class TorNode:
    """Tor node information"""
    fingerprint: str
    nickname: str
    node_type: TorNodeType
    country: str
    ip_address: str
    port: int
    bandwidth: int
    uptime: float
    is_exit: bool = False
    is_guard: bool = False

@dataclass
class TorCircuit:
    """Tor circuit information"""
    circuit_id: str
    status: TorCircuitStatus
    nodes: List[TorNode]
    build_time: float
    purpose: str
    flags: List[str]

@dataclass
class TorOperationResult:
    """Result of Tor operation"""
    success: bool
    operation: str
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

class ShadowTorManager:
    """Advanced Tor network manager with anonymity features"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Tor manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.safe_mode = True  # Always start in safe mode for security
        self.tor_process = None
        self.control_port = self.config.get('control_port', 9051)
        self.socks_port = self.config.get('socks_port', 9050)
        self.tor_data_dir = self.config.get('data_dir', None)
        self.operation_log = []
        self.circuits: Dict[str, TorCircuit] = {}
        self.session = requests.Session()
        
        # Setup session with Tor proxy
        self._setup_tor_session()
    
    def _setup_tor_session(self):
        """Setup requests session with Tor proxy"""
        if not self.safe_mode:
            self.session.proxies = {
                'http': f'socks5://127.0.0.1:{self.socks_port}',
                'https': f'socks5://127.0.0.1:{self.socks_port}'
            }
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent for anonymity"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        return random.choice(user_agents)
    
    def _log_operation(self, operation: str, success: bool, message: str):
        """Log Tor operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"Tor operation: {operation} - {message}")
    
    def start_tor(self, tor_executable: Optional[str] = None) -> TorOperationResult:
        """Start Tor process
        
        Args:
            tor_executable: Path to Tor executable
            
        Returns:
            TorOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - Tor process would be started")
                self._log_operation("start_tor", False, "Safe mode enabled - operation blocked")
                return TorOperationResult(
                    success=False,
                    operation="start_tor",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Find Tor executable
            if not tor_executable:
                tor_executable = self._find_tor_executable()
            
            if not tor_executable:
                error_msg = "Tor executable not found"
                self._log_operation("start_tor", False, error_msg)
                return TorOperationResult(
                    success=False,
                    operation="start_tor",
                    message=error_msg,
                    error="Tor executable not found"
                )
            
            # Create Tor configuration
            tor_config = self._create_tor_config()
            
            # Start Tor process
            cmd = [tor_executable, '-f', tor_config]
            self.tor_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for Tor to start
            time.sleep(5)
            
            if self.tor_process.poll() is None:
                self._log_operation("start_tor", True, "Tor process started successfully")
                return TorOperationResult(
                    success=True,
                    operation="start_tor",
                    message="Tor process started successfully"
                )
            else:
                error_msg = "Tor process failed to start"
                self._log_operation("start_tor", False, error_msg)
                return TorOperationResult(
                    success=False,
                    operation="start_tor",
                    message=error_msg,
                    error="Process failed to start"
                )
            
        except Exception as e:
            error_msg = f"Failed to start Tor: {e}"
            self._log_operation("start_tor", False, error_msg)
            return TorOperationResult(
                success=False,
                operation="start_tor",
                message=error_msg,
                error=str(e)
            )
    
    def _find_tor_executable(self) -> Optional[str]:
        """Find Tor executable on system"""
        possible_paths = [
            'tor',
            '/usr/bin/tor',
            '/usr/local/bin/tor',
            'C:\\Program Files\\Tor\\tor.exe',
            'C:\\Program Files (x86)\\Tor\\tor.exe'
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, '--version'], 
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        return None
    
    def _create_tor_config(self) -> str:
        """Create Tor configuration file"""
        config_content = f"""
# Tor configuration for Shadow library
SocksPort {self.socks_port}
ControlPort {self.control_port}
DataDirectory {self.tor_data_dir or tempfile.mkdtemp()}
CookieAuthentication 1
CookieAuthFile {self.tor_data_dir or tempfile.mkdtemp()}/control_auth_cookie
"""
        
        config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.torrc', delete=False)
        config_file.write(config_content)
        config_file.close()
        
        return config_file.name
    
    def stop_tor(self) -> TorOperationResult:
        """Stop Tor process
        
        Returns:
            TorOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - Tor process would be stopped")
                self._log_operation("stop_tor", False, "Safe mode enabled - operation blocked")
                return TorOperationResult(
                    success=False,
                    operation="stop_tor",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if self.tor_process and self.tor_process.poll() is None:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=10)
                
                self._log_operation("stop_tor", True, "Tor process stopped successfully")
                return TorOperationResult(
                    success=True,
                    operation="stop_tor",
                    message="Tor process stopped successfully"
                )
            else:
                error_msg = "No running Tor process to stop"
                self._log_operation("stop_tor", False, error_msg)
                return TorOperationResult(
                    success=False,
                    operation="stop_tor",
                    message=error_msg,
                    error="No running process"
                )
            
        except Exception as e:
            error_msg = f"Failed to stop Tor: {e}"
            self._log_operation("stop_tor", False, error_msg)
            return TorOperationResult(
                success=False,
                operation="stop_tor",
                message=error_msg,
                error=str(e)
            )
    
    def get_tor_status(self) -> TorOperationResult:
        """Get Tor process status
        
        Returns:
            TorOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - Tor status check would be performed")
                self._log_operation("get_tor_status", False, "Safe mode enabled - operation blocked")
                return TorOperationResult(
                    success=False,
                    operation="get_tor_status",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if self.tor_process and self.tor_process.poll() is None:
                status_data = {
                    'running': True,
                    'pid': self.tor_process.pid,
                    'socks_port': self.socks_port,
                    'control_port': self.control_port
                }
                
                self._log_operation("get_tor_status", True, "Tor is running")
                return TorOperationResult(
                    success=True,
                    operation="get_tor_status",
                    message="Tor is running",
                    data=status_data
                )
            else:
                status_data = {'running': False}
                self._log_operation("get_tor_status", True, "Tor is not running")
                return TorOperationResult(
                    success=True,
                    operation="get_tor_status",
                    message="Tor is not running",
                    data=status_data
                )
            
        except Exception as e:
            error_msg = f"Failed to get Tor status: {e}"
            self._log_operation("get_tor_status", False, error_msg)
            return TorOperationResult(
                success=False,
                operation="get_tor_status",
                message=error_msg,
                error=str(e)
            )
    
    def new_circuit(self) -> TorOperationResult:
        """Create new Tor circuit
        
        Returns:
            TorOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - new circuit would be created")
                self._log_operation("new_circuit", False, "Safe mode enabled - operation blocked")
                return TorOperationResult(
                    success=False,
                    operation="new_circuit",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Simulate circuit creation
            circuit_id = f"circuit_{int(time.time())}"
            circuit = TorCircuit(
                circuit_id=circuit_id,
                status=TorCircuitStatus.BUILDING,
                nodes=[],
                build_time=time.time(),
                purpose="general",
                flags=[]
            )
            
            self.circuits[circuit_id] = circuit
            
            self._log_operation("new_circuit", True, f"New circuit {circuit_id} created")
            return TorOperationResult(
                success=True,
                operation="new_circuit",
                message=f"New circuit {circuit_id} created",
                data=circuit
            )
            
        except Exception as e:
            error_msg = f"Failed to create new circuit: {e}"
            self._log_operation("new_circuit", False, error_msg)
            return TorOperationResult(
                success=False,
                operation="new_circuit",
                message=error_msg,
                error=str(e)
            )
    
    def get_circuits(self) -> TorOperationResult:
        """Get all Tor circuits
        
        Returns:
            TorOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - circuit list would be retrieved")
                self._log_operation("get_circuits", False, "Safe mode enabled - operation blocked")
                return TorOperationResult(
                    success=False,
                    operation="get_circuits",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            circuits_data = list(self.circuits.values())
            
            self._log_operation("get_circuits", True, f"Retrieved {len(circuits_data)} circuits")
            return TorOperationResult(
                success=True,
                operation="get_circuits",
                message=f"Retrieved {len(circuits_data)} circuits",
                data=circuits_data
            )
            
        except Exception as e:
            error_msg = f"Failed to get circuits: {e}"
            self._log_operation("get_circuits", False, error_msg)
            return TorOperationResult(
                success=False,
                operation="get_circuits",
                message=error_msg,
                error=str(e)
            )
    
    def close_circuit(self, circuit_id: str) -> TorOperationResult:
        """Close a Tor circuit
        
        Args:
            circuit_id: Circuit ID to close
            
        Returns:
            TorOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - circuit {circuit_id} would be closed")
                self._log_operation("close_circuit", False, "Safe mode enabled - operation blocked")
                return TorOperationResult(
                    success=False,
                    operation="close_circuit",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if circuit_id in self.circuits:
                del self.circuits[circuit_id]
                self._log_operation("close_circuit", True, f"Circuit {circuit_id} closed")
                return TorOperationResult(
                    success=True,
                    operation="close_circuit",
                    message=f"Circuit {circuit_id} closed"
                )
            else:
                error_msg = f"Circuit {circuit_id} not found"
                self._log_operation("close_circuit", False, error_msg)
                return TorOperationResult(
                    success=False,
                    operation="close_circuit",
                    message=error_msg,
                    error="Circuit not found"
                )
            
        except Exception as e:
            error_msg = f"Failed to close circuit {circuit_id}: {e}"
            self._log_operation("close_circuit", False, error_msg)
            return TorOperationResult(
                success=False,
                operation="close_circuit",
                message=error_msg,
                error=str(e)
            )
    
    def make_request(self, url: str, method: str = 'GET', 
                    data: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None) -> TorOperationResult:
        """Make HTTP request through Tor
        
        Args:
            url: Target URL
            method: HTTP method
            data: Request data
            headers: Additional headers
            
        Returns:
            TorOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - Tor request would be made to {url}")
                self._log_operation("make_request", False, "Safe mode enabled - operation blocked")
                return TorOperationResult(
                    success=False,
                    operation="make_request",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Update headers
            request_headers = {}
            if headers:
                request_headers.update(headers)
            
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                data=data,
                headers=request_headers,
                timeout=30
            )
            
            response_data = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'url': response.url
            }
            
            self._log_operation("make_request", True, f"Request to {url} successful: {response.status_code}")
            return TorOperationResult(
                success=True,
                operation="make_request",
                message=f"Request successful: {response.status_code}",
                data=response_data
            )
            
        except Exception as e:
            error_msg = f"Tor request failed: {e}"
            self._log_operation("make_request", False, error_msg)
            return TorOperationResult(
                success=False,
                operation="make_request",
                message=error_msg,
                error=str(e)
            )
    
    def check_ip(self) -> TorOperationResult:
        """Check current IP address through Tor
        
        Returns:
            TorOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - IP check would be performed")
                self._log_operation("check_ip", False, "Safe mode enabled - operation blocked")
                return TorOperationResult(
                    success=False,
                    operation="check_ip",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Use a service to check IP
            ip_services = [
                'https://httpbin.org/ip',
                'https://api.ipify.org?format=json',
                'https://ipinfo.io/json'
            ]
            
            for service in ip_services:
                try:
                    response = self.session.get(service, timeout=10)
                    if response.status_code == 200:
                        ip_data = response.json()
                        self._log_operation("check_ip", True, f"Current IP: {ip_data}")
                        return TorOperationResult(
                            success=True,
                            operation="check_ip",
                            message="IP check successful",
                            data=ip_data
                        )
                except Exception:
                    continue
            
            error_msg = "Failed to check IP from any service"
            self._log_operation("check_ip", False, error_msg)
            return TorOperationResult(
                success=False,
                operation="check_ip",
                message=error_msg,
                error="All services failed"
            )
            
        except Exception as e:
            error_msg = f"IP check failed: {e}"
            self._log_operation("check_ip", False, error_msg)
            return TorOperationResult(
                success=False,
                operation="check_ip",
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
def start_tor_service(config: Optional[Dict[str, Any]] = None) -> TorOperationResult:
    """Start Tor service"""
    manager = ShadowTorManager(config)
    return manager.start_tor()

def check_tor_ip() -> TorOperationResult:
    """Check IP through Tor"""
    manager = ShadowTorManager()
    return manager.check_ip()

def make_tor_request(url: str, **kwargs) -> TorOperationResult:
    """Make request through Tor"""
    manager = ShadowTorManager()
    return manager.make_request(url, **kwargs)

# Export main classes and functions
__all__ = [
    'ShadowTorManager', 'TorCircuitStatus', 'TorNodeType', 'TorNode', 'TorCircuit', 'TorOperationResult',
    'start_tor_service', 'check_tor_ip', 'make_tor_request'
]
