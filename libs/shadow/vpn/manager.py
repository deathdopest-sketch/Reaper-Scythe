#!/usr/bin/env python3
"""
Shadow VPN Automation Module
VPN connection management, server selection, and automation
"""

import subprocess
import time
import random
import logging
import json
import os
import tempfile
import threading
from typing import Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import requests

logger = logging.getLogger(__name__)

class VPNProtocol(Enum):
    """VPN protocols"""
    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"
    IPSEC = "ipsec"
    SSTP = "sstp"
    L2TP = "l2tp"

class VPNStatus(Enum):
    """VPN connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    FAILED = "failed"

@dataclass
class VPNServer:
    """VPN server information"""
    name: str
    country: str
    city: str
    ip_address: str
    port: int
    protocol: VPNProtocol
    load: int  # Server load percentage
    ping: float  # Ping time in ms
    bandwidth: int  # Available bandwidth
    features: List[str]  # Server features
    is_premium: bool = False

@dataclass
class VPNConfig:
    """VPN configuration"""
    server: VPNServer
    username: Optional[str] = None
    password: Optional[str] = None
    private_key: Optional[str] = None
    public_key: Optional[str] = None
    ca_cert: Optional[str] = None
    client_cert: Optional[str] = None
    client_key: Optional[str] = None
    cipher: str = "AES-256-GCM"
    auth: str = "SHA256"

@dataclass
class VPNOperationResult:
    """Result of VPN operation"""
    success: bool
    operation: str
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

class ShadowVPNManager:
    """Advanced VPN manager with automation and server selection"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize VPN manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.safe_mode = True  # Always start in safe mode for security
        self.current_connection = None
        self.vpn_process = None
        self.operation_log = []
        self.servers: List[VPNServer] = []
        self.status = VPNStatus.DISCONNECTED
        
        # Load VPN servers
        self._load_vpn_servers()
    
    def _load_vpn_servers(self):
        """Load VPN server list"""
        # Sample VPN servers for demonstration
        self.servers = [
            VPNServer(
                name="US-East-1",
                country="United States",
                city="New York",
                ip_address="198.51.100.1",
                port=1194,
                protocol=VPNProtocol.OPENVPN,
                load=45,
                ping=25.5,
                bandwidth=1000,
                features=["P2P", "Streaming", "Gaming"],
                is_premium=False
            ),
            VPNServer(
                name="EU-West-1",
                country="Netherlands",
                city="Amsterdam",
                ip_address="203.0.113.1",
                port=1194,
                protocol=VPNProtocol.OPENVPN,
                load=32,
                ping=18.2,
                bandwidth=2000,
                features=["P2P", "Streaming", "Torrenting"],
                is_premium=True
            ),
            VPNServer(
                name="AS-Pacific-1",
                country="Japan",
                city="Tokyo",
                ip_address="192.0.2.1",
                port=51820,
                protocol=VPNProtocol.WIREGUARD,
                load=67,
                ping=45.8,
                bandwidth=500,
                features=["Gaming", "Streaming"],
                is_premium=False
            ),
            VPNServer(
                name="EU-Central-1",
                country="Germany",
                city="Frankfurt",
                ip_address="198.18.0.1",
                port=1194,
                protocol=VPNProtocol.OPENVPN,
                load=28,
                ping=12.1,
                bandwidth=1500,
                features=["P2P", "Streaming", "Gaming", "Torrenting"],
                is_premium=True
            ),
            VPNServer(
                name="US-West-1",
                country="United States",
                city="Los Angeles",
                ip_address="203.0.113.2",
                port=51820,
                protocol=VPNProtocol.WIREGUARD,
                load=55,
                ping=35.2,
                bandwidth=800,
                features=["Streaming", "Gaming"],
                is_premium=False
            )
        ]
    
    def _log_operation(self, operation: str, success: bool, message: str):
        """Log VPN operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"VPN operation: {operation} - {message}")
    
    def get_servers(self, country: Optional[str] = None, 
                   protocol: Optional[VPNProtocol] = None,
                   premium_only: bool = False) -> VPNOperationResult:
        """Get VPN servers
        
        Args:
            country: Filter by country
            protocol: Filter by protocol
            premium_only: Only premium servers
            
        Returns:
            VPNOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - server list would be retrieved")
                self._log_operation("get_servers", False, "Safe mode enabled - operation blocked")
                return VPNOperationResult(
                    success=False,
                    operation="get_servers",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            filtered_servers = self.servers.copy()
            
            # Apply filters
            if country:
                filtered_servers = [s for s in filtered_servers if s.country.lower() == country.lower()]
            
            if protocol:
                filtered_servers = [s for s in filtered_servers if s.protocol == protocol]
            
            if premium_only:
                filtered_servers = [s for s in filtered_servers if s.is_premium]
            
            # Sort by load (lowest first)
            filtered_servers.sort(key=lambda x: x.load)
            
            self._log_operation("get_servers", True, f"Retrieved {len(filtered_servers)} servers")
            return VPNOperationResult(
                success=True,
                operation="get_servers",
                message=f"Retrieved {len(filtered_servers)} servers",
                data=filtered_servers
            )
            
        except Exception as e:
            error_msg = f"Failed to get servers: {e}"
            self._log_operation("get_servers", False, error_msg)
            return VPNOperationResult(
                success=False,
                operation="get_servers",
                message=error_msg,
                error=str(e)
            )
    
    def find_best_server(self, country: Optional[str] = None,
                        protocol: Optional[VPNProtocol] = None,
                        max_load: int = 80,
                        max_ping: float = 100.0) -> VPNOperationResult:
        """Find best VPN server based on criteria
        
        Args:
            country: Preferred country
            protocol: Preferred protocol
            max_load: Maximum server load
            max_ping: Maximum ping time
            
        Returns:
            VPNOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - best server search would be performed")
                self._log_operation("find_best_server", False, "Safe mode enabled - operation blocked")
                return VPNOperationResult(
                    success=False,
                    operation="find_best_server",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Filter servers by criteria
            candidates = []
            for server in self.servers:
                if server.load > max_load:
                    continue
                if server.ping > max_ping:
                    continue
                if country and server.country.lower() != country.lower():
                    continue
                if protocol and server.protocol != protocol:
                    continue
                
                candidates.append(server)
            
            if not candidates:
                error_msg = "No servers match the criteria"
                self._log_operation("find_best_server", False, error_msg)
                return VPNOperationResult(
                    success=False,
                    operation="find_best_server",
                    message=error_msg,
                    error="No matching servers"
                )
            
            # Score servers (lower is better)
            def score_server(server):
                load_score = server.load * 0.4
                ping_score = server.ping * 0.3
                bandwidth_score = (1000 - min(server.bandwidth, 1000)) * 0.3
                return load_score + ping_score + bandwidth_score
            
            # Sort by score
            candidates.sort(key=score_server)
            best_server = candidates[0]
            
            self._log_operation("find_best_server", True, f"Best server: {best_server.name}")
            return VPNOperationResult(
                success=True,
                operation="find_best_server",
                message=f"Best server: {best_server.name}",
                data=best_server
            )
            
        except Exception as e:
            error_msg = f"Failed to find best server: {e}"
            self._log_operation("find_best_server", False, error_msg)
            return VPNOperationResult(
                success=False,
                operation="find_best_server",
                message=error_msg,
                error=str(e)
            )
    
    def connect(self, server: VPNServer, config: Optional[VPNConfig] = None) -> VPNOperationResult:
        """Connect to VPN server
        
        Args:
            server: VPN server to connect to
            config: VPN configuration
            
        Returns:
            VPNOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - VPN connection to {server.name} would be established")
                self._log_operation("connect", False, "Safe mode enabled - operation blocked")
                return VPNOperationResult(
                    success=False,
                    operation="connect",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if self.status == VPNStatus.CONNECTED:
                error_msg = "Already connected to VPN"
                self._log_operation("connect", False, error_msg)
                return VPNOperationResult(
                    success=False,
                    operation="connect",
                    message=error_msg,
                    error="Already connected"
                )
            
            self.status = VPNStatus.CONNECTING
            
            # Create configuration
            if not config:
                config = VPNConfig(server=server)
            
            # Start VPN connection based on protocol
            if server.protocol == VPNProtocol.OPENVPN:
                result = self._connect_openvpn(config)
            elif server.protocol == VPNProtocol.WIREGUARD:
                result = self._connect_wireguard(config)
            else:
                error_msg = f"Unsupported protocol: {server.protocol}"
                self._log_operation("connect", False, error_msg)
                return VPNOperationResult(
                    success=False,
                    operation="connect",
                    message=error_msg,
                    error="Unsupported protocol"
                )
            
            if result:
                self.status = VPNStatus.CONNECTED
                self.current_connection = server
                self._log_operation("connect", True, f"Connected to {server.name}")
                return VPNOperationResult(
                    success=True,
                    operation="connect",
                    message=f"Connected to {server.name}"
                )
            else:
                self.status = VPNStatus.FAILED
                error_msg = f"Failed to connect to {server.name}"
                self._log_operation("connect", False, error_msg)
                return VPNOperationResult(
                    success=False,
                    operation="connect",
                    message=error_msg,
                    error="Connection failed"
                )
            
        except Exception as e:
            self.status = VPNStatus.FAILED
            error_msg = f"VPN connection failed: {e}"
            self._log_operation("connect", False, error_msg)
            return VPNOperationResult(
                success=False,
                operation="connect",
                message=error_msg,
                error=str(e)
            )
    
    def _connect_openvpn(self, config: VPNConfig) -> bool:
        """Connect using OpenVPN
        
        Args:
            config: VPN configuration
            
        Returns:
            True if connection successful
        """
        try:
            # Create OpenVPN configuration file
            ovpn_config = f"""
client
dev tun
proto udp
remote {config.server.ip_address} {config.server.port}
resolv-retry infinite
nobind
persist-key
persist-tun
cipher {config.cipher}
auth {config.auth}
verb 3
"""
            
            if config.ca_cert:
                ovpn_config += f"ca {config.ca_cert}\n"
            if config.client_cert:
                ovpn_config += f"cert {config.client_cert}\n"
            if config.client_key:
                ovpn_config += f"key {config.client_key}\n"
            
            # Write config to temporary file
            config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ovpn', delete=False)
            config_file.write(ovpn_config)
            config_file.close()
            
            # Start OpenVPN process
            cmd = ['openvpn', '--config', config_file.name]
            self.vpn_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for connection
            time.sleep(5)
            
            # Check if process is still running
            if self.vpn_process.poll() is None:
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"OpenVPN connection failed: {e}")
            return False
    
    def _connect_wireguard(self, config: VPNConfig) -> bool:
        """Connect using WireGuard
        
        Args:
            config: VPN configuration
            
        Returns:
            True if connection successful
        """
        try:
            # Create WireGuard configuration
            wg_config = f"""
[Interface]
PrivateKey = {config.private_key or 'YOUR_PRIVATE_KEY'}
Address = 10.0.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = {config.public_key or 'YOUR_PUBLIC_KEY'}
Endpoint = {config.server.ip_address}:{config.server.port}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
            
            # Write config to temporary file
            config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False)
            config_file.write(wg_config)
            config_file.close()
            
            # Start WireGuard process
            interface_name = f"wg{random.randint(0, 999)}"
            cmd = ['wg-quick', 'up', config_file.name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"WireGuard connection failed: {e}")
            return False
    
    def disconnect(self) -> VPNOperationResult:
        """Disconnect from VPN
        
        Returns:
            VPNOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - VPN disconnection would be performed")
                self._log_operation("disconnect", False, "Safe mode enabled - operation blocked")
                return VPNOperationResult(
                    success=False,
                    operation="disconnect",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if self.status != VPNStatus.CONNECTED:
                error_msg = "Not connected to VPN"
                self._log_operation("disconnect", False, error_msg)
                return VPNOperationResult(
                    success=False,
                    operation="disconnect",
                    message=error_msg,
                    error="Not connected"
                )
            
            self.status = VPNStatus.DISCONNECTING
            
            # Stop VPN process
            if self.vpn_process and self.vpn_process.poll() is None:
                self.vpn_process.terminate()
                self.vpn_process.wait(timeout=10)
            
            self.status = VPNStatus.DISCONNECTED
            self.current_connection = None
            self.vpn_process = None
            
            self._log_operation("disconnect", True, "VPN disconnected successfully")
            return VPNOperationResult(
                success=True,
                operation="disconnect",
                message="VPN disconnected successfully"
            )
            
        except Exception as e:
            error_msg = f"VPN disconnection failed: {e}"
            self._log_operation("disconnect", False, error_msg)
            return VPNOperationResult(
                success=False,
                operation="disconnect",
                message=error_msg,
                error=str(e)
            )
    
    def get_status(self) -> VPNOperationResult:
        """Get VPN connection status
        
        Returns:
            VPNOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - VPN status check would be performed")
                self._log_operation("get_status", False, "Safe mode enabled - operation blocked")
                return VPNOperationResult(
                    success=False,
                    operation="get_status",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            status_data = {
                'status': self.status.value,
                'current_connection': self.current_connection.name if self.current_connection else None,
                'process_running': self.vpn_process.poll() is None if self.vpn_process else False
            }
            
            self._log_operation("get_status", True, f"Status: {self.status.value}")
            return VPNOperationResult(
                success=True,
                operation="get_status",
                message=f"Status: {self.status.value}",
                data=status_data
            )
            
        except Exception as e:
            error_msg = f"Failed to get VPN status: {e}"
            self._log_operation("get_status", False, error_msg)
            return VPNOperationResult(
                success=False,
                operation="get_status",
                message=error_msg,
                error=str(e)
            )
    
    def check_ip(self) -> VPNOperationResult:
        """Check current IP address
        
        Returns:
            VPNOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - IP check would be performed")
                self._log_operation("check_ip", False, "Safe mode enabled - operation blocked")
                return VPNOperationResult(
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
                    response = requests.get(service, timeout=10)
                    if response.status_code == 200:
                        ip_data = response.json()
                        self._log_operation("check_ip", True, f"Current IP: {ip_data}")
                        return VPNOperationResult(
                            success=True,
                            operation="check_ip",
                            message="IP check successful",
                            data=ip_data
                        )
                except Exception:
                    continue
            
            error_msg = "Failed to check IP from any service"
            self._log_operation("check_ip", False, error_msg)
            return VPNOperationResult(
                success=False,
                operation="check_ip",
                message=error_msg,
                error="All services failed"
            )
            
        except Exception as e:
            error_msg = f"IP check failed: {e}"
            self._log_operation("check_ip", False, error_msg)
            return VPNOperationResult(
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
def find_best_vpn_server(country: Optional[str] = None, protocol: Optional[VPNProtocol] = None) -> VPNOperationResult:
    """Find best VPN server"""
    manager = ShadowVPNManager()
    return manager.find_best_server(country, protocol)

def connect_to_vpn(server: VPNServer, config: Optional[VPNConfig] = None) -> VPNOperationResult:
    """Connect to VPN server"""
    manager = ShadowVPNManager()
    return manager.connect(server, config)

def disconnect_vpn() -> VPNOperationResult:
    """Disconnect from VPN"""
    manager = ShadowVPNManager()
    return manager.disconnect()

def check_vpn_ip() -> VPNOperationResult:
    """Check IP through VPN"""
    manager = ShadowVPNManager()
    return manager.check_ip()

# Export main classes and functions
__all__ = [
    'ShadowVPNManager', 'VPNProtocol', 'VPNStatus', 'VPNServer', 'VPNConfig', 'VPNOperationResult',
    'find_best_vpn_server', 'connect_to_vpn', 'disconnect_vpn', 'check_vpn_ip'
]
