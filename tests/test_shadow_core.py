#!/usr/bin/env python3
"""
Comprehensive test suite for Shadow Anonymity Library
Tests Tor integration, VPN automation, MAC spoofing, and traffic obfuscation
"""

import unittest
import tempfile
import os
import sys
import time
import threading
from unittest.mock import patch, MagicMock, Mock
import subprocess
import platform
import requests

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import shadow modules
from libs.shadow.tor.manager import (
    ShadowTorManager, TorCircuitStatus, TorNodeType, TorNode, TorCircuit, TorOperationResult
)
from libs.shadow.vpn.manager import (
    ShadowVPNManager, VPNProtocol, VPNStatus, VPNServer, VPNConfig, VPNOperationResult
)
from libs.shadow.network.manager import (
    ShadowNetworkManager, NetworkInterfaceType, MACAddressFormat, NetworkInterface, NetworkOperationResult
)
from libs.shadow.obfuscation.manager import (
    ShadowObfuscationManager, ObfuscationMethod, FingerprintType, FingerprintProfile, 
    ObfuscationConfig, ObfuscationResult
)

class TestShadowTorManager(unittest.TestCase):
    """Test Tor manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tor_manager = ShadowTorManager({'safe_mode': True})
        self.test_url = "http://example.com"
    
    def test_initialization(self):
        """Test Tor manager initialization"""
        self.assertIsInstance(self.tor_manager, ShadowTorManager)
        self.assertTrue(self.tor_manager.safe_mode)
        self.assertEqual(self.tor_manager.control_port, 9051)
        self.assertEqual(self.tor_manager.socks_port, 9050)
        self.assertIsInstance(self.tor_manager.session, requests.Session)
        self.assertIsInstance(self.tor_manager.operation_log, list)
    
    def test_safe_mode_tor_start(self):
        """Test Tor start in safe mode"""
        result = self.tor_manager.start_tor()
        
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "start_tor")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_tor_stop(self):
        """Test Tor stop in safe mode"""
        result = self.tor_manager.stop_tor()
        
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "stop_tor")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_tor_status(self):
        """Test Tor status check in safe mode"""
        result = self.tor_manager.get_tor_status()
        
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "get_tor_status")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_new_circuit(self):
        """Test new circuit creation in safe mode"""
        result = self.tor_manager.new_circuit()
        
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "new_circuit")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_get_circuits(self):
        """Test circuit retrieval in safe mode"""
        result = self.tor_manager.get_circuits()
        
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "get_circuits")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_close_circuit(self):
        """Test circuit closure in safe mode"""
        result = self.tor_manager.close_circuit("test_circuit")
        
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "close_circuit")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_make_request(self):
        """Test Tor request in safe mode"""
        result = self.tor_manager.make_request(self.test_url)
        
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "make_request")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_check_ip(self):
        """Test IP check in safe mode"""
        result = self.tor_manager.check_ip()
        
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "check_ip")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_user_agent_generation(self):
        """Test user agent generation"""
        user_agent = self.tor_manager._get_random_user_agent()
        
        self.assertIsInstance(user_agent, str)
        self.assertIn("Mozilla", user_agent)
        self.assertGreater(len(user_agent), 50)
    
    def test_operation_logging(self):
        """Test operation logging"""
        initial_log_count = len(self.tor_manager.operation_log)
        
        # Make a request (will be blocked in safe mode)
        self.tor_manager.start_tor()
        
        # Check log was updated
        self.assertEqual(len(self.tor_manager.operation_log), initial_log_count + 1)
        
        log_entry = self.tor_manager.operation_log[-1]
        self.assertIn('timestamp', log_entry)
        self.assertEqual(log_entry['operation'], 'start_tor')
        self.assertFalse(log_entry['success'])

class TestShadowVPNManager(unittest.TestCase):
    """Test VPN manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.vpn_manager = ShadowVPNManager()
        self.test_server = VPNServer(
            name="Test-Server",
            country="Test Country",
            city="Test City",
            ip_address="192.168.1.1",
            port=1194,
            protocol=VPNProtocol.OPENVPN,
            load=50,
            ping=25.0,
            bandwidth=1000,
            features=["P2P", "Streaming"]
        )
    
    def test_initialization(self):
        """Test VPN manager initialization"""
        self.assertIsInstance(self.vpn_manager, ShadowVPNManager)
        self.assertTrue(self.vpn_manager.safe_mode)
        self.assertEqual(self.vpn_manager.status, VPNStatus.DISCONNECTED)
        self.assertIsInstance(self.vpn_manager.servers, list)
        self.assertGreater(len(self.vpn_manager.servers), 0)
        self.assertIsInstance(self.vpn_manager.operation_log, list)
    
    def test_safe_mode_get_servers(self):
        """Test server retrieval in safe mode"""
        result = self.vpn_manager.get_servers()
        
        self.assertIsInstance(result, VPNOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "get_servers")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_find_best_server(self):
        """Test best server search in safe mode"""
        result = self.vpn_manager.find_best_server()
        
        self.assertIsInstance(result, VPNOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "find_best_server")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_connect(self):
        """Test VPN connection in safe mode"""
        result = self.vpn_manager.connect(self.test_server)
        
        self.assertIsInstance(result, VPNOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "connect")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_disconnect(self):
        """Test VPN disconnection in safe mode"""
        result = self.vpn_manager.disconnect()
        
        self.assertIsInstance(result, VPNOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "disconnect")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_get_status(self):
        """Test VPN status check in safe mode"""
        result = self.vpn_manager.get_status()
        
        self.assertIsInstance(result, VPNOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "get_status")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_check_ip(self):
        """Test IP check in safe mode"""
        result = self.vpn_manager.check_ip()
        
        self.assertIsInstance(result, VPNOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "check_ip")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_vpn_server_creation(self):
        """Test VPN server creation"""
        server = VPNServer(
            name="Test",
            country="US",
            city="NYC",
            ip_address="1.2.3.4",
            port=1194,
            protocol=VPNProtocol.OPENVPN,
            load=30,
            ping=20.0,
            bandwidth=2000,
            features=["P2P"]
        )
        
        self.assertEqual(server.name, "Test")
        self.assertEqual(server.country, "US")
        self.assertEqual(server.protocol, VPNProtocol.OPENVPN)
        self.assertFalse(server.is_premium)
    
    def test_vpn_config_creation(self):
        """Test VPN configuration creation"""
        config = VPNConfig(
            server=self.test_server,
            username="testuser",
            password="testpass",
            cipher="AES-256-GCM"
        )
        
        self.assertEqual(config.server, self.test_server)
        self.assertEqual(config.username, "testuser")
        self.assertEqual(config.password, "testpass")
        self.assertEqual(config.cipher, "AES-256-GCM")
    
    def test_operation_logging(self):
        """Test operation logging"""
        # Clear any existing logs first
        self.vpn_manager.clear_operation_log()
        initial_log_count = len(self.vpn_manager.operation_log)
        
        # Make a request (will be blocked in safe mode)
        self.vpn_manager.get_servers()
        
        # Check log was updated
        self.assertEqual(len(self.vpn_manager.operation_log), initial_log_count + 1)
        
        log_entry = self.vpn_manager.operation_log[-1]
        self.assertIn('timestamp', log_entry)
        self.assertEqual(log_entry['operation'], 'get_servers')
        self.assertFalse(log_entry['success'])

class TestShadowNetworkManager(unittest.TestCase):
    """Test network manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.network_manager = ShadowNetworkManager({'safe_mode': True})
    
    def test_initialization(self):
        """Test network manager initialization"""
        self.assertIsInstance(self.network_manager, ShadowNetworkManager)
        self.assertTrue(self.network_manager.safe_mode)
        self.assertIsInstance(self.network_manager.interfaces, list)
        self.assertIsInstance(self.network_manager.original_macs, dict)
        self.assertIsInstance(self.network_manager.operation_log, list)
    
    def test_safe_mode_get_interfaces(self):
        """Test interface retrieval in safe mode"""
        result = self.network_manager.get_interfaces()
        
        self.assertIsInstance(result, NetworkOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "get_interfaces")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_spoof_mac(self):
        """Test MAC spoofing in safe mode"""
        result = self.network_manager.spoof_mac("eth0")
        
        self.assertIsInstance(result, NetworkOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "spoof_mac")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_restore_mac(self):
        """Test MAC restoration in safe mode"""
        result = self.network_manager.restore_mac("eth0")
        
        self.assertIsInstance(result, NetworkOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "restore_mac")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_randomize_macs(self):
        """Test MAC randomization in safe mode"""
        result = self.network_manager.randomize_all_macs()
        
        self.assertIsInstance(result, NetworkOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "randomize_all_macs")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_mac_address_generation(self):
        """Test MAC address generation"""
        mac = self.network_manager.generate_random_mac()
        
        self.assertIsInstance(mac, str)
        self.assertRegex(mac, r'^[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}$')
        
        # Test with vendor
        mac_intel = self.network_manager.generate_random_mac("Intel")
        self.assertIsInstance(mac_intel, str)
        self.assertRegex(mac_intel, r'^[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}$')
        
        # Test different formats
        mac_dash = self.network_manager.generate_random_mac(format=MACAddressFormat.DASH)
        self.assertRegex(mac_dash, r'^[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}$')
        
        mac_dot = self.network_manager.generate_random_mac(format=MACAddressFormat.DOT)
        self.assertRegex(mac_dot, r'^[0-9A-F]{2}\.[0-9A-F]{2}\.[0-9A-F]{2}\.[0-9A-F]{2}\.[0-9A-F]{2}\.[0-9A-F]{2}$')
        
        mac_none = self.network_manager.generate_random_mac(format=MACAddressFormat.NONE)
        self.assertRegex(mac_none, r'^[0-9A-F]{12}$')
    
    def test_mac_address_validation(self):
        """Test MAC address validation"""
        # Valid MAC addresses
        valid_macs = [
            "00:11:22:33:44:55",
            "00-11-22-33-44-55",
            "00.11.22.33.44.55",
            "001122334455"
        ]
        
        for mac in valid_macs:
            self.assertTrue(self.network_manager._validate_mac_address(mac))
        
        # Invalid MAC addresses
        invalid_macs = [
            "00:11:22:33:44",  # Too short
            "00:11:22:33:44:55:66",  # Too long
            "00:11:22:33:44:GG",  # Invalid characters
            "invalid_mac"  # Not hex
        ]
        
        for mac in invalid_macs:
            self.assertFalse(self.network_manager._validate_mac_address(mac))
    
    def test_interface_type_detection(self):
        """Test interface type detection"""
        # Test WiFi interface
        wifi_type = self.network_manager._determine_interface_type("wlan0", "00:11:22:33:44:55")
        self.assertEqual(wifi_type, NetworkInterfaceType.WIFI)
        
        # Test Ethernet interface
        eth_type = self.network_manager._determine_interface_type("eth0", "00:11:22:33:44:55")
        self.assertEqual(eth_type, NetworkInterfaceType.ETHERNET)
        
        # Test Bluetooth interface
        bt_type = self.network_manager._determine_interface_type("bluetooth0", "00:11:22:33:44:55")
        self.assertEqual(bt_type, NetworkInterfaceType.BLUETOOTH)
        
        # Test Virtual interface
        vpn_type = self.network_manager._determine_interface_type("tun0", "00:11:22:33:44:55")
        self.assertEqual(vpn_type, NetworkInterfaceType.VIRTUAL)
        
        # Test Unknown interface
        unknown_type = self.network_manager._determine_interface_type("unknown0", "00:11:22:33:44:55")
        self.assertEqual(unknown_type, NetworkInterfaceType.UNKNOWN)
    
    def test_vendor_detection(self):
        """Test vendor detection from MAC address"""
        # Test known vendor
        vendor = self.network_manager._get_mac_vendor("00:0C:29:11:22:33")
        self.assertEqual(vendor, "VMware")
        
        # Test unknown vendor
        vendor = self.network_manager._get_mac_vendor("FF:FF:FF:11:22:33")
        self.assertEqual(vendor, "Unknown")
    
    def test_operation_logging(self):
        """Test operation logging"""
        initial_log_count = len(self.network_manager.operation_log)
        
        # Make a request (will be blocked in safe mode)
        self.network_manager.get_interfaces()
        
        # Check log was updated
        self.assertEqual(len(self.network_manager.operation_log), initial_log_count + 1)
        
        log_entry = self.network_manager.operation_log[-1]
        self.assertIn('timestamp', log_entry)
        self.assertEqual(log_entry['operation'], 'get_interfaces')
        self.assertFalse(log_entry['success'])

class TestShadowObfuscationManager(unittest.TestCase):
    """Test obfuscation manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.obfuscation_manager = ShadowObfuscationManager()
        self.test_url = "http://example.com"
    
    def test_initialization(self):
        """Test obfuscation manager initialization"""
        self.assertIsInstance(self.obfuscation_manager, ShadowObfuscationManager)
        self.assertTrue(self.obfuscation_manager.safe_mode)
        self.assertIsInstance(self.obfuscation_manager.fingerprint_profiles, list)
        self.assertGreater(len(self.obfuscation_manager.fingerprint_profiles), 0)
        self.assertIsInstance(self.obfuscation_manager.session, requests.Session)
        self.assertIsInstance(self.obfuscation_manager.operation_log, list)
    
    def test_safe_mode_obfuscate_request(self):
        """Test obfuscated request in safe mode"""
        result = self.obfuscation_manager.obfuscate_request(self.test_url)
        
        self.assertIsInstance(result, ObfuscationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "obfuscate_request")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_obfuscate_traffic_pattern(self):
        """Test traffic pattern obfuscation in safe mode"""
        requests_data = [{"url": "http://example.com", "method": "GET"}]
        result = self.obfuscation_manager.obfuscate_traffic_pattern(requests_data)
        
        self.assertIsInstance(result, ObfuscationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "obfuscate_traffic_pattern")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_randomize_dns_queries(self):
        """Test DNS query randomization in safe mode"""
        domains = ["example.com", "test.com"]
        result = self.obfuscation_manager.randomize_dns_queries(domains)
        
        self.assertIsInstance(result, ObfuscationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "randomize_dns_queries")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_generate_tls_fingerprint(self):
        """Test TLS fingerprint generation in safe mode"""
        result = self.obfuscation_manager.generate_tls_fingerprint()
        
        self.assertIsInstance(result, ObfuscationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "generate_tls_fingerprint")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_safe_mode_get_fingerprint_profiles(self):
        """Test fingerprint profile retrieval in safe mode"""
        result = self.obfuscation_manager.get_fingerprint_profiles()
        
        self.assertIsInstance(result, ObfuscationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "get_fingerprint_profiles")
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_fingerprint_profile_generation(self):
        """Test fingerprint profile generation"""
        profile = self.obfuscation_manager.generate_fingerprint_profile(FingerprintType.BROWSER)
        
        self.assertIsInstance(profile, FingerprintProfile)
        self.assertEqual(profile.fingerprint_type, FingerprintType.BROWSER)
        self.assertIsInstance(profile.user_agent, str)
        self.assertIn("Mozilla", profile.user_agent)
        self.assertIsInstance(profile.screen_resolution, str)
        self.assertIsInstance(profile.timezone, str)
        self.assertIsInstance(profile.language, str)
        self.assertIsInstance(profile.platform, str)
        self.assertIsInstance(profile.plugins, list)
        self.assertIsInstance(profile.fonts, list)
        self.assertIsInstance(profile.canvas_fingerprint, str)
        self.assertIsInstance(profile.webgl_fingerprint, str)
        self.assertIsInstance(profile.audio_fingerprint, str)
    
    def test_fingerprint_generation(self):
        """Test fingerprint generation methods"""
        # Test canvas fingerprint
        canvas_fp = self.obfuscation_manager._generate_canvas_fingerprint()
        self.assertIsInstance(canvas_fp, str)
        self.assertEqual(len(canvas_fp), 32)  # MD5 hash length
        
        # Test WebGL fingerprint
        webgl_fp = self.obfuscation_manager._generate_webgl_fingerprint()
        self.assertIsInstance(webgl_fp, str)
        self.assertEqual(len(webgl_fp), 64)  # SHA256 hash length
        
        # Test audio fingerprint
        audio_fp = self.obfuscation_manager._generate_audio_fingerprint()
        self.assertIsInstance(audio_fp, str)
        self.assertEqual(len(audio_fp), 40)  # SHA1 hash length
    
    def test_header_randomization(self):
        """Test header randomization"""
        # Store original headers
        original_headers = self.obfuscation_manager.session.headers.copy()
        
        # Randomize headers
        self.obfuscation_manager._randomize_headers()
        
        # Check that headers were updated
        new_headers = self.obfuscation_manager.session.headers
        self.assertIn('Accept', new_headers)
        self.assertIn('Accept-Language', new_headers)
        self.assertIn('Accept-Encoding', new_headers)
        self.assertIn('Connection', new_headers)
        self.assertIn('Upgrade-Insecure-Requests', new_headers)
    
    def test_operation_logging(self):
        """Test operation logging"""
        initial_log_count = len(self.obfuscation_manager.operation_log)
        
        # Make a request (will be blocked in safe mode)
        self.obfuscation_manager.obfuscate_request(self.test_url)
        
        # Check log was updated
        self.assertEqual(len(self.obfuscation_manager.operation_log), initial_log_count + 1)
        
        log_entry = self.obfuscation_manager.operation_log[-1]
        self.assertIn('timestamp', log_entry)
        self.assertEqual(log_entry['operation'], 'obfuscate_request')
        self.assertFalse(log_entry['success'])

class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def test_tor_convenience_functions(self):
        """Test Tor convenience functions"""
        from libs.shadow.tor.manager import start_tor_service, check_tor_ip, make_tor_request
        
        # Test start_tor_service
        result = start_tor_service()
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test check_tor_ip
        result = check_tor_ip()
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test make_tor_request
        result = make_tor_request("http://example.com")
        self.assertIsInstance(result, TorOperationResult)
        self.assertFalse(result.success)  # Safe mode
    
    def test_vpn_convenience_functions(self):
        """Test VPN convenience functions"""
        from libs.shadow.vpn.manager import find_best_vpn_server, connect_to_vpn, disconnect_vpn, check_vpn_ip
        
        # Test find_best_vpn_server
        result = find_best_vpn_server()
        self.assertIsInstance(result, VPNOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test connect_to_vpn
        server = VPNServer(
            name="Test", country="US", city="NYC", ip_address="1.2.3.4",
            port=1194, protocol=VPNProtocol.OPENVPN, load=50, ping=25.0,
            bandwidth=1000, features=["P2P"]
        )
        result = connect_to_vpn(server)
        self.assertIsInstance(result, VPNOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test disconnect_vpn
        result = disconnect_vpn()
        self.assertIsInstance(result, VPNOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test check_vpn_ip
        result = check_vpn_ip()
        self.assertIsInstance(result, VPNOperationResult)
        self.assertFalse(result.success)  # Safe mode
    
    def test_network_convenience_functions(self):
        """Test network convenience functions"""
        from libs.shadow.network.manager import (
            get_network_interfaces, spoof_mac_address, restore_mac_address, 
            randomize_mac_addresses, generate_random_mac
        )
        
        # Test get_network_interfaces
        result = get_network_interfaces()
        self.assertIsInstance(result, NetworkOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test spoof_mac_address
        result = spoof_mac_address("eth0")
        self.assertIsInstance(result, NetworkOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test restore_mac_address
        result = restore_mac_address("eth0")
        self.assertIsInstance(result, NetworkOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test randomize_mac_addresses
        result = randomize_mac_addresses()
        self.assertIsInstance(result, NetworkOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test generate_random_mac
        mac = generate_random_mac()
        self.assertIsInstance(mac, str)
        self.assertRegex(mac, r'^[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}$')
    
    def test_obfuscation_convenience_functions(self):
        """Test obfuscation convenience functions"""
        from libs.shadow.obfuscation.manager import (
            generate_fingerprint_profile, obfuscate_request, 
            randomize_traffic_pattern, generate_tls_fingerprint
        )
        
        # Test generate_fingerprint_profile
        profile = generate_fingerprint_profile(FingerprintType.BROWSER)
        self.assertIsInstance(profile, FingerprintProfile)
        self.assertEqual(profile.fingerprint_type, FingerprintType.BROWSER)
        
        # Test obfuscate_request
        result = obfuscate_request("http://example.com")
        self.assertIsInstance(result, ObfuscationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test randomize_traffic_pattern
        requests_data = [{"url": "http://example.com", "method": "GET"}]
        result = randomize_traffic_pattern(requests_data)
        self.assertIsInstance(result, ObfuscationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test generate_tls_fingerprint
        result = generate_tls_fingerprint()
        self.assertIsInstance(result, ObfuscationResult)
        self.assertFalse(result.success)  # Safe mode

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
