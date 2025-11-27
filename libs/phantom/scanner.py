"""
Phantom Network Operations Library - Core Features

This module provides network scanning, packet crafting, and DNS operations
for the Reaper security-focused programming language.

Features:
- Port scanning (TCP connect, SYN, UDP)
- Packet crafting and manipulation
- DNS operations (queries, zone transfers)
- Safety checks and rate limiting
- Error handling and logging

Author: Reaper Security Team
Version: 0.1.0
"""

import socket
import threading
import time
import logging
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# Configure logging for phantom operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScanType(Enum):
    """Types of port scans available"""
    TCP_CONNECT = "tcp_connect"
    SYN_SCAN = "syn_scan"
    UDP_SCAN = "udp_scan"

class ScanResult(Enum):
    """Port scan result types"""
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    ERROR = "error"

@dataclass
class PortResult:
    """Result of a port scan"""
    port: int
    status: ScanResult
    response_time: float
    service: Optional[str] = None
    banner: Optional[str] = None

@dataclass
class ScanConfig:
    """Configuration for port scanning"""
    timeout: float = 1.0
    threads: int = 10
    rate_limit: float = 0.1  # seconds between scans
    stealth_mode: bool = False
    banner_grab: bool = False

class PhantomScanner:
    """
    Core port scanning functionality for Phantom library.
    
    Provides TCP connect, SYN, and UDP scanning with safety checks,
    rate limiting, and comprehensive error handling.
    """
    
    def __init__(self, config: Optional[ScanConfig] = None):
        """
        Initialize scanner with configuration.
        
        Args:
            config: ScanConfig object with scanning parameters
        """
        self.config = config or ScanConfig()
        self.scan_lock = threading.Lock()
        self.last_scan_time = 0
        self.scan_count = 0
        self.max_scans_per_minute = 100  # Safety limit
        
    def _rate_limit_check(self) -> None:
        """Check if we're within rate limits"""
        current_time = time.time()
        if current_time - self.last_scan_time < self.config.rate_limit:
            time.sleep(self.config.rate_limit)
        
        # Check scan count per minute
        if self.scan_count > self.max_scans_per_minute:
            logger.warning("Rate limit exceeded, pausing scans")
            time.sleep(60)  # Wait a minute
            self.scan_count = 0
            
        self.last_scan_time = current_time
        self.scan_count += 1
    
    def _tcp_connect_scan(self, host: str, port: int) -> PortResult:
        """
        Perform TCP connect scan on a single port.
        
        Args:
            host: Target hostname or IP
            port: Target port number
            
        Returns:
            PortResult with scan results
        """
        start_time = time.time()
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.config.timeout)
                result = sock.connect_ex((host, port))
                
                response_time = time.time() - start_time
                
                if result == 0:
                    # Port is open
                    service = None
                    banner = None
                    
                    if self.config.banner_grab:
                        try:
                            banner = sock.recv(1024).decode('utf-8', errors='ignore')
                            service = self._identify_service(port, banner)
                        except:
                            pass
                    
                    return PortResult(
                        port=port,
                        status=ScanResult.OPEN,
                        response_time=response_time,
                        service=service,
                        banner=banner
                    )
                else:
                    return PortResult(
                        port=port,
                        status=ScanResult.CLOSED,
                        response_time=response_time
                    )
                    
        except socket.timeout:
            return PortResult(
                port=port,
                status=ScanResult.FILTERED,
                response_time=self.config.timeout
            )
        except Exception as e:
            logger.error(f"Error scanning port {port}: {e}")
            return PortResult(
                port=port,
                status=ScanResult.ERROR,
                response_time=time.time() - start_time
            )
    
    def _udp_scan(self, host: str, port: int) -> PortResult:
        """
        Perform UDP scan on a single port.
        
        Args:
            host: Target hostname or IP
            port: Target port number
            
        Returns:
            PortResult with scan results
        """
        start_time = time.time()
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(self.config.timeout)
                
                # Send empty packet
                sock.sendto(b'', (host, port))
                
                try:
                    data, addr = sock.recvfrom(1024)
                    response_time = time.time() - start_time
                    
                    return PortResult(
                        port=port,
                        status=ScanResult.OPEN,
                        response_time=response_time,
                        banner=data.decode('utf-8', errors='ignore')[:100]
                    )
                except socket.timeout:
                    # No response - could be open or filtered
                    return PortResult(
                        port=port,
                        status=ScanResult.FILTERED,
                        response_time=self.config.timeout
                    )
                    
        except Exception as e:
            logger.error(f"Error UDP scanning port {port}: {e}")
            return PortResult(
                port=port,
                status=ScanResult.ERROR,
                response_time=time.time() - start_time
            )
    
    def _identify_service(self, port: int, banner: str) -> Optional[str]:
        """
        Identify service based on port and banner.
        
        Args:
            port: Port number
            banner: Banner string received
            
        Returns:
            Service name if identified
        """
        # Common port mappings
        port_services = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 993: "IMAPS",
            995: "POP3S", 3389: "RDP", 5432: "PostgreSQL", 3306: "MySQL"
        }
        
        # Check port first
        if port in port_services:
            return port_services[port]
        
        # Check banner for service indicators
        banner_lower = banner.lower()
        if "ssh" in banner_lower:
            return "SSH"
        elif "http" in banner_lower:
            return "HTTP"
        elif "ftp" in banner_lower:
            return "FTP"
        elif "smtp" in banner_lower:
            return "SMTP"
        
        return None
    
    def scan_port(self, host: str, port: int, scan_type: ScanType = ScanType.TCP_CONNECT) -> PortResult:
        """
        Scan a single port.
        
        Args:
            host: Target hostname or IP
            port: Port number to scan
            scan_type: Type of scan to perform
            
        Returns:
            PortResult with scan results
        """
        # Rate limiting
        self._rate_limit_check()
        
        # Validate inputs
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        
        if not host or not isinstance(host, str):
            raise ValueError("Host must be a non-empty string")
        
        logger.info(f"Scanning {host}:{port} with {scan_type.value}")
        
        if scan_type == ScanType.TCP_CONNECT:
            return self._tcp_connect_scan(host, port)
        elif scan_type == ScanType.UDP_SCAN:
            return self._udp_scan(host, port)
        elif scan_type == ScanType.SYN_SCAN:
            # SYN scan requires raw sockets (root/admin privileges)
            logger.warning("SYN scan requires elevated privileges, falling back to TCP connect")
            return self._tcp_connect_scan(host, port)
        else:
            raise ValueError(f"Unsupported scan type: {scan_type}")
    
    def scan_ports(self, host: str, ports: List[int], scan_type: ScanType = ScanType.TCP_CONNECT) -> List[PortResult]:
        """
        Scan multiple ports on a host.
        
        Args:
            host: Target hostname or IP
            ports: List of port numbers to scan
            scan_type: Type of scan to perform
            
        Returns:
            List of PortResult objects
        """
        results = []
        
        # Validate inputs
        if not ports:
            raise ValueError("Ports list cannot be empty")
        
        if len(ports) > 1000:
            logger.warning(f"Scanning {len(ports)} ports - this may take a while")
        
        logger.info(f"Scanning {len(ports)} ports on {host}")
        
        # Use threading for concurrent scans
        threads = []
        results_lock = threading.Lock()
        
        def scan_worker(port_list: List[int]):
            """Worker function for threaded scanning"""
            for port in port_list:
                try:
                    result = self.scan_port(host, port, scan_type)
                    with results_lock:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error scanning port {port}: {e}")
                    with results_lock:
                        results.append(PortResult(
                            port=port,
                            status=ScanResult.ERROR,
                            response_time=0.0
                        ))
        
        # Split ports among threads
        ports_per_thread = max(1, len(ports) // self.config.threads)
        for i in range(0, len(ports), ports_per_thread):
            thread_ports = ports[i:i + ports_per_thread]
            thread = threading.Thread(target=scan_worker, args=(thread_ports,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Sort results by port number
        results.sort(key=lambda x: x.port)
        
        logger.info(f"Scan completed: {len(results)} results")
        return results
    
    def scan_range(self, host: str, start_port: int, end_port: int, scan_type: ScanType = ScanType.TCP_CONNECT) -> List[PortResult]:
        """
        Scan a range of ports on a host.
        
        Args:
            host: Target hostname or IP
            start_port: Starting port number
            end_port: Ending port number
            scan_type: Type of scan to perform
            
        Returns:
            List of PortResult objects
        """
        if start_port > end_port:
            raise ValueError("Start port must be <= end port")
        
        ports = list(range(start_port, end_port + 1))
        return self.scan_ports(host, ports, scan_type)
    
    def get_open_ports(self, results: List[PortResult]) -> List[int]:
        """
        Extract open ports from scan results.
        
        Args:
            results: List of PortResult objects
            
        Returns:
            List of open port numbers
        """
        return [result.port for result in results if result.status == ScanResult.OPEN]
    
    def get_service_summary(self, results: List[PortResult]) -> Dict[str, List[int]]:
        """
        Get summary of services found.
        
        Args:
            results: List of PortResult objects
            
        Returns:
            Dictionary mapping service names to port lists
        """
        services = {}
        for result in results:
            if result.status == ScanResult.OPEN and result.service:
                if result.service not in services:
                    services[result.service] = []
                services[result.service].append(result.port)
        
        return services

# Convenience functions for easy access
def scan_port(host: str, port: int, scan_type: ScanType = ScanType.TCP_CONNECT) -> PortResult:
    """Scan a single port"""
    scanner = PhantomScanner()
    return scanner.scan_port(host, port, scan_type)

def scan_ports(host: str, ports: List[int], scan_type: ScanType = ScanType.TCP_CONNECT) -> List[PortResult]:
    """Scan multiple ports"""
    scanner = PhantomScanner()
    return scanner.scan_ports(host, ports, scan_type)

def scan_range(host: str, start_port: int, end_port: int, scan_type: ScanType = ScanType.TCP_CONNECT) -> List[PortResult]:
    """Scan a range of ports"""
    scanner = PhantomScanner()
    return scanner.scan_range(host, start_port, end_port, scan_type)

def get_open_ports(results: List[PortResult]) -> List[int]:
    """Extract open ports from scan results"""
    scanner = PhantomScanner()
    return scanner.get_open_ports(results)

def get_service_summary(results: List[PortResult]) -> Dict[str, List[int]]:
    """Get summary of services found"""
    scanner = PhantomScanner()
    return scanner.get_service_summary(results)

# Export main classes and functions
__all__ = [
    'PhantomScanner', 'ScanType', 'ScanResult', 'PortResult', 'ScanConfig',
    'scan_port', 'scan_ports', 'scan_range', 'get_open_ports', 'get_service_summary'
]
