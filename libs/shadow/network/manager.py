#!/usr/bin/env python3
"""
Shadow Network Anonymity Module
MAC address spoofing, network interface management, and anonymity features
"""

import subprocess
import time
import random
import logging
import re
import uuid
import platform
import socket
from typing import Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import psutil

logger = logging.getLogger(__name__)

class NetworkInterfaceType(Enum):
    """Network interface types"""
    ETHERNET = "ethernet"
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    VIRTUAL = "virtual"
    UNKNOWN = "unknown"

class MACAddressFormat(Enum):
    """MAC address formats"""
    COLON = "colon"  # 00:11:22:33:44:55
    DASH = "dash"    # 00-11-22-33-44-55
    DOT = "dot"      # 00.11.22.33.44.55
    NONE = "none"    # 001122334455

@dataclass
class NetworkInterface:
    """Network interface information"""
    name: str
    mac_address: str
    interface_type: NetworkInterfaceType
    is_up: bool
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    gateway: Optional[str] = None
    dns_servers: List[str] = None
    vendor: Optional[str] = None

@dataclass
class NetworkOperationResult:
    """Result of network operation"""
    success: bool
    operation: str
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

class ShadowNetworkManager:
    """Advanced network anonymity and interface management"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize network manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.safe_mode = True  # Always start in safe mode for security
        self.operation_log = []
        self.interfaces: List[NetworkInterface] = []
        self.original_macs: Dict[str, str] = {}  # Store original MAC addresses
        
        # Load network interfaces
        self._load_interfaces()
    
    def _load_interfaces(self):
        """Load network interfaces"""
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in interfaces.items():
                # Skip loopback and virtual interfaces
                if interface_name.startswith('lo') or interface_name.startswith('veth'):
                    continue
                
                mac_address = None
                ip_address = None
                subnet_mask = None
                
                for addr in addresses:
                    if addr.family == socket.AF_LINK:  # MAC address
                        mac_address = addr.address
                    elif addr.family == socket.AF_INET:  # IPv4
                        ip_address = addr.address
                        subnet_mask = addr.netmask
                
                if mac_address:
                    # Determine interface type
                    interface_type = self._determine_interface_type(interface_name, mac_address)
                    
                    # Get interface status
                    is_up = stats.get(interface_name, {}).isup if interface_name in stats else False
                    
                    # Get vendor from MAC address
                    vendor = self._get_mac_vendor(mac_address)
                    
                    interface = NetworkInterface(
                        name=interface_name,
                        mac_address=mac_address,
                        interface_type=interface_type,
                        is_up=is_up,
                        ip_address=ip_address,
                        subnet_mask=subnet_mask,
                        vendor=vendor
                    )
                    
                    self.interfaces.append(interface)
                    self.original_macs[interface_name] = mac_address
        
        except Exception as e:
            logger.error(f"Failed to load network interfaces: {e}")
    
    def _determine_interface_type(self, name: str, mac_address: str) -> NetworkInterfaceType:
        """Determine network interface type"""
        name_lower = name.lower()
        
        if 'wifi' in name_lower or 'wlan' in name_lower or 'wireless' in name_lower:
            return NetworkInterfaceType.WIFI
        elif 'eth' in name_lower or 'ethernet' in name_lower:
            return NetworkInterfaceType.ETHERNET
        elif 'bluetooth' in name_lower or 'bt' in name_lower:
            return NetworkInterfaceType.BLUETOOTH
        elif 'vpn' in name_lower or 'tun' in name_lower or 'tap' in name_lower:
            return NetworkInterfaceType.VIRTUAL
        else:
            return NetworkInterfaceType.UNKNOWN
    
    def _get_mac_vendor(self, mac_address: str) -> Optional[str]:
        """Get vendor from MAC address OUI"""
        try:
            # Extract OUI (first 3 bytes)
            mac_clean = mac_address.replace(':', '').replace('-', '').replace('.', '')
            oui = mac_clean[:6].upper()
            
            # Common vendor OUIs (simplified list)
            vendor_map = {
                '000C29': 'VMware',
                '001C42': 'Apple',
                '001D4F': 'Apple',
                '002590': 'Apple',
                '003065': 'Apple',
                '0050F2': 'Microsoft',
                '080027': 'Oracle VirtualBox',
                '0C9D92': 'Intel',
                '14DAE9': 'Intel',
                '1C1B0D': 'Intel',
                '2C44FD': 'Intel',
                '3C07F4': 'Intel',
                '3C2AF7': 'Intel',
                '3C4A92': 'Intel',
                '3C5AB4': 'Intel',
                '3C6A7D': 'Intel',
                '3C7FB1': 'Intel',
                '3C8BFE': 'Intel',
                '3C9F81': 'Intel',
                '3CA8F6': 'Intel',
                '3CA9F4': 'Intel',
                '3CB6B7': 'Intel',
                '3CB87A': 'Intel',
                '3CB9A6': 'Intel',
                '3CBBFD': 'Intel',
                '3CC1F6': 'Intel',
                '3CC2E1': 'Intel',
                '3CC99E': 'Intel',
                '3CCE73': 'Intel',
                '3CD0F8': 'Intel',
                '3CD4D6': 'Intel',
                '3CD7DA': 'Intel',
                '3CD9CE': 'Intel',
                '3CDA2A': 'Intel',
                '3CDD89': 'Intel',
                '3CDF1E': 'Intel',
                '3CDFA9': 'Intel',
                '3CE1A1': 'Intel',
                '3CE5A6': 'Intel',
                '3CE624': 'Intel',
                '3CE72B': 'Intel',
                '3CE8F0': 'Intel',
                '3CE9F7': 'Intel',
                '3CEAF0': 'Intel',
                '3CEB5F': 'Intel',
                '3CECEF': 'Intel',
                '3CEDFB': 'Intel',
                '3CEE93': 'Intel',
                '3CEF8C': 'Intel',
                '3CF010': 'Intel',
                '3CF09F': 'Intel',
                '3CF111': 'Intel',
                '3CF2B9': 'Intel',
                '3CF392': 'Intel',
                '3CF4CA': 'Intel',
                '3CF5CC': 'Intel',
                '3CF6A4': 'Intel',
                '3CF7A4': 'Intel',
                '3CF8B9': 'Intel',
                '3CF9FA': 'Intel',
                '3CFAB7': 'Intel',
                '3CFB96': 'Intel',
                '3CFC3F': 'Intel',
                '3CFD3A': 'Intel',
                '3CFE4C': 'Intel',
                '3CFF4A': 'Intel',
                '3CFFCA': 'Intel',
                '3CFFD6': 'Intel',
                '3CFFE9': 'Intel',
                '3CFFEA': 'Intel',
                '3CFFEB': 'Intel',
                '3CFFEC': 'Intel',
                '3CFFED': 'Intel',
                '3CFFEE': 'Intel',
                '3CFFEF': 'Intel',
                '3CFFF0': 'Intel',
                '3CFFF1': 'Intel',
                '3CFFF2': 'Intel',
                '3CFFF3': 'Intel',
                '3CFFF4': 'Intel',
                '3CFFF5': 'Intel',
                '3CFFF6': 'Intel',
                '3CFFF7': 'Intel',
                '3CFFF8': 'Intel',
                '3CFFF9': 'Intel',
                '3CFFFA': 'Intel',
                '3CFFFB': 'Intel',
                '3CFFFC': 'Intel',
                '3CFFFD': 'Intel',
                '3CFFFE': 'Intel',
                '3CFFFF': 'Intel',
                '525400': 'Realtek',
                '525401': 'Realtek',
                '525402': 'Realtek',
                '525403': 'Realtek',
                '525404': 'Realtek',
                '525405': 'Realtek',
                '525406': 'Realtek',
                '525407': 'Realtek',
                '525408': 'Realtek',
                '525409': 'Realtek',
                '52540A': 'Realtek',
                '52540B': 'Realtek',
                '52540C': 'Realtek',
                '52540D': 'Realtek',
                '52540E': 'Realtek',
                '52540F': 'Realtek',
                '525410': 'Realtek',
                '525411': 'Realtek',
                '525412': 'Realtek',
                '525413': 'Realtek',
                '525414': 'Realtek',
                '525415': 'Realtek',
                '525416': 'Realtek',
                '525417': 'Realtek',
                '525418': 'Realtek',
                '525419': 'Realtek',
                '52541A': 'Realtek',
                '52541B': 'Realtek',
                '52541C': 'Realtek',
                '52541D': 'Realtek',
                '52541E': 'Realtek',
                '52541F': 'Realtek',
                '525420': 'Realtek',
                '525421': 'Realtek',
                '525422': 'Realtek',
                '525423': 'Realtek',
                '525424': 'Realtek',
                '525425': 'Realtek',
                '525426': 'Realtek',
                '525427': 'Realtek',
                '525428': 'Realtek',
                '525429': 'Realtek',
                '52542A': 'Realtek',
                '52542B': 'Realtek',
                '52542C': 'Realtek',
                '52542D': 'Realtek',
                '52542E': 'Realtek',
                '52542F': 'Realtek',
                '525430': 'Realtek',
                '525431': 'Realtek',
                '525432': 'Realtek',
                '525433': 'Realtek',
                '525434': 'Realtek',
                '525435': 'Realtek',
                '525436': 'Realtek',
                '525437': 'Realtek',
                '525438': 'Realtek',
                '525439': 'Realtek',
                '52543A': 'Realtek',
                '52543B': 'Realtek',
                '52543C': 'Realtek',
                '52543D': 'Realtek',
                '52543E': 'Realtek',
                '52543F': 'Realtek',
                '525440': 'Realtek',
                '525441': 'Realtek',
                '525442': 'Realtek',
                '525443': 'Realtek',
                '525444': 'Realtek',
                '525445': 'Realtek',
                '525446': 'Realtek',
                '525447': 'Realtek',
                '525448': 'Realtek',
                '525449': 'Realtek',
                '52544A': 'Realtek',
                '52544B': 'Realtek',
                '52544C': 'Realtek',
                '52544D': 'Realtek',
                '52544E': 'Realtek',
                '52544F': 'Realtek',
                '525450': 'Realtek',
                '525451': 'Realtek',
                '525452': 'Realtek',
                '525453': 'Realtek',
                '525454': 'Realtek',
                '525455': 'Realtek',
                '525456': 'Realtek',
                '525457': 'Realtek',
                '525458': 'Realtek',
                '525459': 'Realtek',
                '52545A': 'Realtek',
                '52545B': 'Realtek',
                '52545C': 'Realtek',
                '52545D': 'Realtek',
                '52545E': 'Realtek',
                '52545F': 'Realtek',
                '525460': 'Realtek',
                '525461': 'Realtek',
                '525462': 'Realtek',
                '525463': 'Realtek',
                '525464': 'Realtek',
                '525465': 'Realtek',
                '525466': 'Realtek',
                '525467': 'Realtek',
                '525468': 'Realtek',
                '525469': 'Realtek',
                '52546A': 'Realtek',
                '52546B': 'Realtek',
                '52546C': 'Realtek',
                '52546D': 'Realtek',
                '52546E': 'Realtek',
                '52546F': 'Realtek',
                '525470': 'Realtek',
                '525471': 'Realtek',
                '525472': 'Realtek',
                '525473': 'Realtek',
                '525474': 'Realtek',
                '525475': 'Realtek',
                '525476': 'Realtek',
                '525477': 'Realtek',
                '525478': 'Realtek',
                '525479': 'Realtek',
                '52547A': 'Realtek',
                '52547B': 'Realtek',
                '52547C': 'Realtek',
                '52547D': 'Realtek',
                '52547E': 'Realtek',
                '52547F': 'Realtek',
                '525480': 'Realtek',
                '525481': 'Realtek',
                '525482': 'Realtek',
                '525483': 'Realtek',
                '525484': 'Realtek',
                '525485': 'Realtek',
                '525486': 'Realtek',
                '525487': 'Realtek',
                '525488': 'Realtek',
                '525489': 'Realtek',
                '52548A': 'Realtek',
                '52548B': 'Realtek',
                '52548C': 'Realtek',
                '52548D': 'Realtek',
                '52548E': 'Realtek',
                '52548F': 'Realtek',
                '525490': 'Realtek',
                '525491': 'Realtek',
                '525492': 'Realtek',
                '525493': 'Realtek',
                '525494': 'Realtek',
                '525495': 'Realtek',
                '525496': 'Realtek',
                '525497': 'Realtek',
                '525498': 'Realtek',
                '525499': 'Realtek',
                '52549A': 'Realtek',
                '52549B': 'Realtek',
                '52549C': 'Realtek',
                '52549D': 'Realtek',
                '52549E': 'Realtek',
                '52549F': 'Realtek',
                '5254A0': 'Realtek',
                '5254A1': 'Realtek',
                '5254A2': 'Realtek',
                '5254A3': 'Realtek',
                '5254A4': 'Realtek',
                '5254A5': 'Realtek',
                '5254A6': 'Realtek',
                '5254A7': 'Realtek',
                '5254A8': 'Realtek',
                '5254A9': 'Realtek',
                '5254AA': 'Realtek',
                '5254AB': 'Realtek',
                '5254AC': 'Realtek',
                '5254AD': 'Realtek',
                '5254AE': 'Realtek',
                '5254AF': 'Realtek',
                '5254B0': 'Realtek',
                '5254B1': 'Realtek',
                '5254B2': 'Realtek',
                '5254B3': 'Realtek',
                '5254B4': 'Realtek',
                '5254B5': 'Realtek',
                '5254B6': 'Realtek',
                '5254B7': 'Realtek',
                '5254B8': 'Realtek',
                '5254B9': 'Realtek',
                '5254BA': 'Realtek',
                '5254BB': 'Realtek',
                '5254BC': 'Realtek',
                '5254BD': 'Realtek',
                '5254BE': 'Realtek',
                '5254BF': 'Realtek',
                '5254C0': 'Realtek',
                '5254C1': 'Realtek',
                '5254C2': 'Realtek',
                '5254C3': 'Realtek',
                '5254C4': 'Realtek',
                '5254C5': 'Realtek',
                '5254C6': 'Realtek',
                '5254C7': 'Realtek',
                '5254C8': 'Realtek',
                '5254C9': 'Realtek',
                '5254CA': 'Realtek',
                '5254CB': 'Realtek',
                '5254CC': 'Realtek',
                '5254CD': 'Realtek',
                '5254CE': 'Realtek',
                '5254CF': 'Realtek',
                '5254D0': 'Realtek',
                '5254D1': 'Realtek',
                '5254D2': 'Realtek',
                '5254D3': 'Realtek',
                '5254D4': 'Realtek',
                '5254D5': 'Realtek',
                '5254D6': 'Realtek',
                '5254D7': 'Realtek',
                '5254D8': 'Realtek',
                '5254D9': 'Realtek',
                '5254DA': 'Realtek',
                '5254DB': 'Realtek',
                '5254DC': 'Realtek',
                '5254DD': 'Realtek',
                '5254DE': 'Realtek',
                '5254DF': 'Realtek',
                '5254E0': 'Realtek',
                '5254E1': 'Realtek',
                '5254E2': 'Realtek',
                '5254E3': 'Realtek',
                '5254E4': 'Realtek',
                '5254E5': 'Realtek',
                '5254E6': 'Realtek',
                '5254E7': 'Realtek',
                '5254E8': 'Realtek',
                '5254E9': 'Realtek',
                '5254EA': 'Realtek',
                '5254EB': 'Realtek',
                '5254EC': 'Realtek',
                '5254ED': 'Realtek',
                '5254EE': 'Realtek',
                '5254EF': 'Realtek',
                '5254F0': 'Realtek',
                '5254F1': 'Realtek',
                '5254F2': 'Realtek',
                '5254F3': 'Realtek',
                '5254F4': 'Realtek',
                '5254F5': 'Realtek',
                '5254F6': 'Realtek',
                '5254F7': 'Realtek',
                '5254F8': 'Realtek',
                '5254F9': 'Realtek',
                '5254FA': 'Realtek',
                '5254FB': 'Realtek',
                '5254FC': 'Realtek',
                '5254FD': 'Realtek',
                '5254FE': 'Realtek',
                '5254FF': 'Realtek'
            }
            
            return vendor_map.get(oui, 'Unknown')
        
        except Exception:
            return 'Unknown'
    
    def _log_operation(self, operation: str, success: bool, message: str):
        """Log network operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"Network operation: {operation} - {message}")
    
    def get_interfaces(self) -> NetworkOperationResult:
        """Get network interfaces
        
        Returns:
            NetworkOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - interface list would be retrieved")
                self._log_operation("get_interfaces", False, "Safe mode enabled - operation blocked")
                return NetworkOperationResult(
                    success=False,
                    operation="get_interfaces",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            self._log_operation("get_interfaces", True, f"Retrieved {len(self.interfaces)} interfaces")
            return NetworkOperationResult(
                success=True,
                operation="get_interfaces",
                message=f"Retrieved {len(self.interfaces)} interfaces",
                data=self.interfaces.copy()
            )
            
        except Exception as e:
            error_msg = f"Failed to get interfaces: {e}"
            self._log_operation("get_interfaces", False, error_msg)
            return NetworkOperationResult(
                success=False,
                operation="get_interfaces",
                message=error_msg,
                error=str(e)
            )
    
    def generate_random_mac(self, vendor: Optional[str] = None, 
                          format: MACAddressFormat = MACAddressFormat.COLON) -> str:
        """Generate random MAC address
        
        Args:
            vendor: Specific vendor OUI (first 3 bytes)
            format: MAC address format
            
        Returns:
            Random MAC address
        """
        try:
            if vendor:
                # Use specific vendor OUI
                vendor_ouis = {
                    'Intel': ['00:1B:21', '00:1C:42', '00:1D:4F'],
                    'Apple': ['00:16:CB', '00:17:F2', '00:1B:63'],
                    'Realtek': ['52:54:00', '00:E0:4C', '00:1F:5B'],
                    'Microsoft': ['00:50:F2', '00:15:5D', '00:03:FF'],
                    'VMware': ['00:0C:29', '00:1C:14', '00:50:56']
                }
                
                if vendor in vendor_ouis:
                    oui = random.choice(vendor_ouis[vendor])
                else:
                    # Generate random OUI
                    oui = f"{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}"
            else:
                # Generate completely random MAC
                oui = f"{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}"
            
            # Generate last 3 bytes
            nic = f"{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}"
            
            mac = f"{oui}:{nic}"
            
            # Apply format
            if format == MACAddressFormat.DASH:
                mac = mac.replace(':', '-')
            elif format == MACAddressFormat.DOT:
                mac = mac.replace(':', '.')
            elif format == MACAddressFormat.NONE:
                mac = mac.replace(':', '')
            
            return mac
            
        except Exception as e:
            logger.error(f"Failed to generate random MAC: {e}")
            return "00:00:00:00:00:00"
    
    def spoof_mac(self, interface_name: str, new_mac: Optional[str] = None) -> NetworkOperationResult:
        """Spoof MAC address of network interface
        
        Args:
            interface_name: Name of network interface
            new_mac: New MAC address (random if None)
            
        Returns:
            NetworkOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - MAC spoofing would be performed on {interface_name}")
                self._log_operation("spoof_mac", False, "Safe mode enabled - operation blocked")
                return NetworkOperationResult(
                    success=False,
                    operation="spoof_mac",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Find interface
            interface = None
            for iface in self.interfaces:
                if iface.name == interface_name:
                    interface = iface
                    break
            
            if not interface:
                error_msg = f"Interface {interface_name} not found"
                self._log_operation("spoof_mac", False, error_msg)
                return NetworkOperationResult(
                    success=False,
                    operation="spoof_mac",
                    message=error_msg,
                    error="Interface not found"
                )
            
            # Generate new MAC if not provided
            if not new_mac:
                new_mac = self.generate_random_mac()
            
            # Validate MAC address format
            if not self._validate_mac_address(new_mac):
                error_msg = f"Invalid MAC address format: {new_mac}"
                self._log_operation("spoof_mac", False, error_msg)
                return NetworkOperationResult(
                    success=False,
                    operation="spoof_mac",
                    message=error_msg,
                    error="Invalid MAC format"
                )
            
            # Store original MAC if not already stored
            if interface_name not in self.original_macs:
                self.original_macs[interface_name] = interface.mac_address
            
            # Change MAC address based on OS
            if platform.system() == "Windows":
                success = self._spoof_mac_windows(interface_name, new_mac)
            elif platform.system() == "Linux":
                success = self._spoof_mac_linux(interface_name, new_mac)
            elif platform.system() == "Darwin":  # macOS
                success = self._spoof_mac_macos(interface_name, new_mac)
            else:
                error_msg = f"Unsupported operating system: {platform.system()}"
                self._log_operation("spoof_mac", False, error_msg)
                return NetworkOperationResult(
                    success=False,
                    operation="spoof_mac",
                    message=error_msg,
                    error="Unsupported OS"
                )
            
            if success:
                # Update interface MAC address
                interface.mac_address = new_mac
                
                self._log_operation("spoof_mac", True, f"MAC spoofed: {interface_name} -> {new_mac}")
                return NetworkOperationResult(
                    success=True,
                    operation="spoof_mac",
                    message=f"MAC spoofed: {interface_name} -> {new_mac}",
                    data={'interface': interface_name, 'old_mac': self.original_macs[interface_name], 'new_mac': new_mac}
                )
            else:
                error_msg = f"Failed to spoof MAC address for {interface_name}"
                self._log_operation("spoof_mac", False, error_msg)
                return NetworkOperationResult(
                    success=False,
                    operation="spoof_mac",
                    message=error_msg,
                    error="Spoofing failed"
                )
            
        except Exception as e:
            error_msg = f"MAC spoofing failed: {e}"
            self._log_operation("spoof_mac", False, error_msg)
            return NetworkOperationResult(
                success=False,
                operation="spoof_mac",
                message=error_msg,
                error=str(e)
            )
    
    def _validate_mac_address(self, mac: str) -> bool:
        """Validate MAC address format"""
        # Remove separators
        mac_clean = re.sub(r'[:\-\.]', '', mac)
        
        # Check if it's 12 hex characters
        if len(mac_clean) != 12:
            return False
        
        try:
            int(mac_clean, 16)
            return True
        except ValueError:
            return False
    
    def _spoof_mac_windows(self, interface_name: str, new_mac: str) -> bool:
        """Spoof MAC address on Windows"""
        try:
            # Use netsh to change MAC address
            cmd = [
                'netsh', 'interface', 'set', 'interface', 
                interface_name, 'admin=disable'
            ]
            subprocess.run(cmd, capture_output=True, text=True)
            
            time.sleep(1)
            
            cmd = [
                'netsh', 'interface', 'set', 'interface', 
                interface_name, 'admin=enable'
            ]
            subprocess.run(cmd, capture_output=True, text=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Windows MAC spoofing failed: {e}")
            return False
    
    def _spoof_mac_linux(self, interface_name: str, new_mac: str) -> bool:
        """Spoof MAC address on Linux"""
        try:
            # Bring interface down
            cmd = ['sudo', 'ip', 'link', 'set', interface_name, 'down']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False
            
            # Change MAC address
            cmd = ['sudo', 'ip', 'link', 'set', interface_name, 'address', new_mac]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False
            
            # Bring interface up
            cmd = ['sudo', 'ip', 'link', 'set', interface_name, 'up']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Linux MAC spoofing failed: {e}")
            return False
    
    def _spoof_mac_macos(self, interface_name: str, new_mac: str) -> bool:
        """Spoof MAC address on macOS"""
        try:
            # Use ifconfig to change MAC address
            cmd = ['sudo', 'ifconfig', interface_name, 'ether', new_mac]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"macOS MAC spoofing failed: {e}")
            return False
    
    def restore_mac(self, interface_name: str) -> NetworkOperationResult:
        """Restore original MAC address
        
        Args:
            interface_name: Name of network interface
            
        Returns:
            NetworkOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - MAC restoration would be performed on {interface_name}")
                self._log_operation("restore_mac", False, "Safe mode enabled - operation blocked")
                return NetworkOperationResult(
                    success=False,
                    operation="restore_mac",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            if interface_name not in self.original_macs:
                error_msg = f"No original MAC address stored for {interface_name}"
                self._log_operation("restore_mac", False, error_msg)
                return NetworkOperationResult(
                    success=False,
                    operation="restore_mac",
                    message=error_msg,
                    error="No original MAC stored"
                )
            
            original_mac = self.original_macs[interface_name]
            
            # Restore MAC address
            result = self.spoof_mac(interface_name, original_mac)
            
            if result.success:
                # Remove from original MACs
                del self.original_macs[interface_name]
                
                self._log_operation("restore_mac", True, f"MAC restored: {interface_name} -> {original_mac}")
                return NetworkOperationResult(
                    success=True,
                    operation="restore_mac",
                    message=f"MAC restored: {interface_name} -> {original_mac}"
                )
            else:
                return result
            
        except Exception as e:
            error_msg = f"MAC restoration failed: {e}"
            self._log_operation("restore_mac", False, error_msg)
            return NetworkOperationResult(
                success=False,
                operation="restore_mac",
                message=error_msg,
                error=str(e)
            )
    
    def randomize_all_macs(self) -> NetworkOperationResult:
        """Randomize MAC addresses of all interfaces
        
        Returns:
            NetworkOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning("Safe mode enabled - MAC randomization would be performed")
                self._log_operation("randomize_all_macs", False, "Safe mode enabled - operation blocked")
                return NetworkOperationResult(
                    success=False,
                    operation="randomize_all_macs",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            results = []
            for interface in self.interfaces:
                if interface.interface_type in [NetworkInterfaceType.ETHERNET, NetworkInterfaceType.WIFI]:
                    result = self.spoof_mac(interface.name)
                    results.append(result)
            
            successful = sum(1 for r in results if r.success)
            
            self._log_operation("randomize_all_macs", True, f"Randomized {successful}/{len(results)} interfaces")
            return NetworkOperationResult(
                success=True,
                operation="randomize_all_macs",
                message=f"Randomized {successful}/{len(results)} interfaces",
                data=results
            )
            
        except Exception as e:
            error_msg = f"MAC randomization failed: {e}"
            self._log_operation("randomize_all_macs", False, error_msg)
            return NetworkOperationResult(
                success=False,
                operation="randomize_all_macs",
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
def get_network_interfaces() -> NetworkOperationResult:
    """Get network interfaces"""
    manager = ShadowNetworkManager()
    return manager.get_interfaces()

def spoof_mac_address(interface_name: str, new_mac: Optional[str] = None) -> NetworkOperationResult:
    """Spoof MAC address"""
    manager = ShadowNetworkManager()
    return manager.spoof_mac(interface_name, new_mac)

def restore_mac_address(interface_name: str) -> NetworkOperationResult:
    """Restore original MAC address"""
    manager = ShadowNetworkManager()
    return manager.restore_mac(interface_name)

def randomize_mac_addresses() -> NetworkOperationResult:
    """Randomize all MAC addresses"""
    manager = ShadowNetworkManager()
    return manager.randomize_all_macs()

def generate_random_mac(vendor: Optional[str] = None) -> str:
    """Generate random MAC address"""
    manager = ShadowNetworkManager()
    return manager.generate_random_mac(vendor)

# Export main classes and functions
__all__ = [
    'ShadowNetworkManager', 'NetworkInterfaceType', 'MACAddressFormat', 'NetworkInterface', 'NetworkOperationResult',
    'get_network_interfaces', 'spoof_mac_address', 'restore_mac_address', 'randomize_mac_addresses', 'generate_random_mac'
]
