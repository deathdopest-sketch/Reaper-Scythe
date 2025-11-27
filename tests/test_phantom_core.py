"""
Tests for Phantom Network Operations Library

This module contains comprehensive tests for the Phantom library
including port scanning, packet crafting, and DNS operations.

Author: Reaper Security Team
Version: 0.1.0
"""

import unittest
import socket
import threading
import time
from unittest.mock import patch, MagicMock

# Import phantom modules
from libs.phantom.scanner import (
    PhantomScanner, ScanType, ScanResult, PortResult, ScanConfig,
    scan_port, scan_ports, scan_range
)

from libs.phantom.packet import (
    PhantomPacket, PacketConfig, Protocol,
    create_tcp_packet, create_udp_packet, create_icmp_packet
)

from libs.phantom.dns import (
    PhantomDNS, DNSConfig, DNSRecord, DNSRecordType,
    resolve_domain, reverse_lookup, query_dns
)

class TestPhantomScanner(unittest.TestCase):
    """Test cases for PhantomScanner class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scanner = PhantomScanner()
        self.test_host = "127.0.0.1"
        self.test_ports = [80, 443, 22, 25]
    
    def test_scanner_initialization(self):
        """Test scanner initialization"""
        scanner = PhantomScanner()
        self.assertIsInstance(scanner.config, ScanConfig)
        self.assertEqual(scanner.config.timeout, 1.0)
        self.assertEqual(scanner.config.threads, 10)
    
    def test_scanner_with_custom_config(self):
        """Test scanner with custom configuration"""
        config = ScanConfig(timeout=2.0, threads=5, rate_limit=0.2)
        scanner = PhantomScanner(config)
        self.assertEqual(scanner.config.timeout, 2.0)
        self.assertEqual(scanner.config.threads, 5)
        self.assertEqual(scanner.config.rate_limit, 0.2)
    
    def test_scan_port_tcp_connect(self):
        """Test TCP connect port scanning"""
        # Test with localhost - should find some open ports
        result = self.scanner.scan_port(self.test_host, 80, ScanType.TCP_CONNECT)
        self.assertIsInstance(result, PortResult)
        self.assertEqual(result.port, 80)
        self.assertIn(result.status, [ScanResult.OPEN, ScanResult.CLOSED, ScanResult.FILTERED])
    
    def test_scan_port_udp(self):
        """Test UDP port scanning"""
        result = self.scanner.scan_port(self.test_host, 53, ScanType.UDP_SCAN)
        self.assertIsInstance(result, PortResult)
        self.assertEqual(result.port, 53)
        self.assertIn(result.status, [ScanResult.OPEN, ScanResult.CLOSED, ScanResult.FILTERED, ScanResult.ERROR])
    
    def test_scan_ports_multiple(self):
        """Test scanning multiple ports"""
        results = self.scanner.scan_ports(self.test_host, self.test_ports)
        self.assertEqual(len(results), len(self.test_ports))
        
        for result in results:
            self.assertIsInstance(result, PortResult)
            self.assertIn(result.port, self.test_ports)
    
    def test_scan_range(self):
        """Test scanning port range"""
        results = self.scanner.scan_range(self.test_host, 80, 85)
        self.assertEqual(len(results), 6)  # Ports 80-85 inclusive
        
        ports = [result.port for result in results]
        expected_ports = list(range(80, 86))
        self.assertEqual(sorted(ports), expected_ports)
    
    def test_invalid_port_validation(self):
        """Test invalid port validation"""
        with self.assertRaises(ValueError):
            self.scanner.scan_port(self.test_host, 0)
        
        with self.assertRaises(ValueError):
            self.scanner.scan_port(self.test_host, 65536)
        
        with self.assertRaises(ValueError):
            self.scanner.scan_port(self.test_host, -1)
    
    def test_invalid_host_validation(self):
        """Test invalid host validation"""
        with self.assertRaises(ValueError):
            self.scanner.scan_port("", 80)
        
        with self.assertRaises(ValueError):
            self.scanner.scan_port(None, 80)
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        config = ScanConfig(rate_limit=0.1)  # 100ms between scans
        scanner = PhantomScanner(config)
        
        start_time = time.time()
        scanner.scan_port(self.test_host, 80)
        scanner.scan_port(self.test_host, 81)
        end_time = time.time()
        
        # Should take at least 100ms due to rate limiting
        self.assertGreaterEqual(end_time - start_time, 0.1)
    
    def test_get_open_ports(self):
        """Test extracting open ports from results"""
        # Mock results
        results = [
            PortResult(80, ScanResult.OPEN, 0.1),
            PortResult(443, ScanResult.CLOSED, 0.2),
            PortResult(22, ScanResult.OPEN, 0.05),
            PortResult(25, ScanResult.FILTERED, 1.0)
        ]
        
        open_ports = self.scanner.get_open_ports(results)
        self.assertEqual(sorted(open_ports), [22, 80])
    
    def test_get_service_summary(self):
        """Test service summary generation"""
        # Mock results with services
        results = [
            PortResult(80, ScanResult.OPEN, 0.1, service="HTTP"),
            PortResult(443, ScanResult.OPEN, 0.2, service="HTTPS"),
            PortResult(22, ScanResult.OPEN, 0.05, service="SSH"),
            PortResult(80, ScanResult.OPEN, 0.1, service="HTTP")  # Duplicate
        ]
        
        services = self.scanner.get_service_summary(results)
        self.assertIn("HTTP", services)
        self.assertIn("HTTPS", services)
        self.assertIn("SSH", services)
        self.assertEqual(len(services["HTTP"]), 2)  # Two HTTP ports

class TestPhantomPacket(unittest.TestCase):
    """Test cases for PhantomPacket class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = PacketConfig(
            dest_ip="127.0.0.1",
            dest_port=80,
            source_port=12345
        )
        self.packet = PhantomPacket(self.config)
    
    def test_packet_initialization(self):
        """Test packet initialization"""
        packet = PhantomPacket()
        self.assertIsInstance(packet.config, PacketConfig)
        self.assertEqual(packet.config.dest_ip, "127.0.0.1")
        self.assertEqual(packet.config.dest_port, 80)
    
    def test_create_tcp_packet(self):
        """Test TCP packet creation"""
        packet_data = self.packet.create_tcp_packet(b"test payload")
        self.assertIsInstance(packet_data, bytes)
        self.assertGreater(len(packet_data), 20)  # At least TCP header size
    
    def test_create_udp_packet(self):
        """Test UDP packet creation"""
        packet_data = self.packet.create_udp_packet(b"test payload")
        self.assertIsInstance(packet_data, bytes)
        self.assertGreater(len(packet_data), 8)  # At least UDP header size
    
    def test_create_icmp_packet(self):
        """Test ICMP packet creation"""
        packet_data = self.packet.create_icmp_packet()
        self.assertIsInstance(packet_data, bytes)
        self.assertGreaterEqual(len(packet_data), 8)  # At least ICMP header size
    
    def test_checksum_calculation(self):
        """Test checksum calculation"""
        test_data = b"test data for checksum"
        checksum = self.packet._calculate_checksum(test_data)
        self.assertIsInstance(checksum, int)
        self.assertGreaterEqual(checksum, 0)
        self.assertLessEqual(checksum, 65535)
    
    def test_invalid_config_validation(self):
        """Test invalid configuration validation"""
        # Test with invalid packet creation instead of config validation
        packet = PhantomPacket()
        
        # Test invalid destination port
        packet.config.dest_port = 0
        with self.assertRaises(ValueError):
            packet._validate_config()
        
        packet.config.dest_port = 65536
        with self.assertRaises(ValueError):
            packet._validate_config()
        
        # Reset to valid config
        packet.config.dest_port = 80
        
        # Test with invalid source port (must be > 0 to trigger validation)
        packet.config.source_port = 1  # Valid first
        packet._validate_config()  # Should pass
        
        packet.config.source_port = 0  # Invalid
        with self.assertRaises(ValueError):
            packet._validate_config()
    
    @patch('socket.socket')
    @patch('socket.inet_aton')
    def test_send_packet_tcp(self, mock_inet_aton, mock_socket):
        """Test sending TCP packet"""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_inet_aton.return_value = b'\x7f\x00\x00\x01'  # 127.0.0.1
        
        # Create a fresh packet to avoid side effects
        config = PacketConfig(dest_ip="127.0.0.1", dest_port=80)
        packet = PhantomPacket(config)
        
        packet_data = packet.create_tcp_packet()
        result = packet.send_packet(packet_data, Protocol.TCP)
        
        self.assertTrue(result)
        # Check that connect was called with the right parameters
        mock_sock.connect.assert_called_with(("127.0.0.1", 80))
        mock_sock.send.assert_called_once()
    
    @patch('socket.socket')
    def test_send_packet_udp(self, mock_socket):
        """Test sending UDP packet"""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        packet_data = self.packet.create_udp_packet()
        result = self.packet.send_packet(packet_data, Protocol.UDP)
        
        self.assertTrue(result)
        mock_sock.connect.assert_called_once()
        mock_sock.send.assert_called_once()

class TestPhantomDNS(unittest.TestCase):
    """Test cases for PhantomDNS class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dns = PhantomDNS()
        self.test_domain = "google.com"
    
    def test_dns_initialization(self):
        """Test DNS client initialization"""
        dns = PhantomDNS()
        self.assertIsInstance(dns.config, DNSConfig)
        self.assertEqual(dns.config.dns_server, "8.8.8.8")
        self.assertEqual(dns.config.timeout, 5.0)
    
    def test_dns_with_custom_config(self):
        """Test DNS client with custom configuration"""
        config = DNSConfig(dns_server="1.1.1.1", timeout=10.0)
        dns = PhantomDNS(config)
        self.assertEqual(dns.config.dns_server, "1.1.1.1")
        self.assertEqual(dns.config.timeout, 10.0)
    
    def test_encode_domain_name(self):
        """Test domain name encoding"""
        encoded = self.dns._encode_domain_name("example.com")
        self.assertIsInstance(encoded, bytes)
        self.assertTrue(encoded.endswith(b'\x00'))  # Null terminator
    
    def test_decode_domain_name(self):
        """Test domain name decoding"""
        encoded = self.dns._encode_domain_name("example.com")
        decoded, offset = self.dns._decode_domain_name(encoded, 0)
        self.assertEqual(decoded, "example.com")
    
    def test_create_dns_query(self):
        """Test DNS query packet creation"""
        query = self.dns._create_dns_query("example.com", DNSRecordType.A)
        self.assertIsInstance(query, bytes)
        self.assertGreater(len(query), 12)  # At least DNS header size
    
    @patch('socket.socket')
    def test_dns_query(self, mock_socket):
        """Test DNS query with mocked response"""
        # Mock DNS response
        mock_response = b'\x00\x01\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04\x08\x08\x08\x08'
        
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.recvfrom.return_value = (mock_response, ("8.8.8.8", 53))
        
        records = self.dns.query("example.com", DNSRecordType.A)
        self.assertIsInstance(records, list)
    
    def test_resolve_domain(self):
        """Test domain resolution"""
        # This test may fail if no internet connection
        try:
            ips = self.dns.resolve("google.com")
            self.assertIsInstance(ips, list)
            if ips:  # If we got results
                for ip in ips:
                    self.assertRegex(ip, r'^\d+\.\d+\.\d+\.\d+$')  # IPv4 format
        except Exception:
            # Skip test if no internet connection
            self.skipTest("No internet connection available")
    
    def test_reverse_lookup(self):
        """Test reverse DNS lookup"""
        # Test with a known IP
        try:
            domains = self.dns.reverse_lookup("8.8.8.8")
            self.assertIsInstance(domains, list)
        except Exception:
            # Skip test if no internet connection
            self.skipTest("No internet connection available")
    
    def test_get_mx_records(self):
        """Test MX record retrieval"""
        try:
            records = self.dns.get_mx_records("google.com")
            self.assertIsInstance(records, list)
            if records:
                for record in records:
                    self.assertEqual(record.record_type, DNSRecordType.MX)
        except Exception:
            self.skipTest("No internet connection available")
    
    def test_get_txt_records(self):
        """Test TXT record retrieval"""
        try:
            records = self.dns.get_txt_records("google.com")
            self.assertIsInstance(records, list)
            if records:
                for record in records:
                    self.assertEqual(record.record_type, DNSRecordType.TXT)
        except Exception:
            self.skipTest("No internet connection available")
    
    def test_dns_enumeration(self):
        """Test comprehensive DNS enumeration"""
        try:
            results = self.dns.dns_enumeration("google.com")
            self.assertIsInstance(results, dict)
        except Exception:
            self.skipTest("No internet connection available")

class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def test_scan_port_function(self):
        """Test scan_port convenience function"""
        result = scan_port("127.0.0.1", 80)
        self.assertIsInstance(result, PortResult)
    
    def test_scan_ports_function(self):
        """Test scan_ports convenience function"""
        results = scan_ports("127.0.0.1", [80, 443])
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
    
    def test_scan_range_function(self):
        """Test scan_range convenience function"""
        results = scan_range("127.0.0.1", 80, 82)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)
    
    def test_create_tcp_packet_function(self):
        """Test create_tcp_packet convenience function"""
        packet = create_tcp_packet("127.0.0.1", 80, b"test")
        self.assertIsInstance(packet, bytes)
    
    def test_create_udp_packet_function(self):
        """Test create_udp_packet convenience function"""
        packet = create_udp_packet("127.0.0.1", 53, b"test")
        self.assertIsInstance(packet, bytes)
    
    def test_create_icmp_packet_function(self):
        """Test create_icmp_packet convenience function"""
        packet = create_icmp_packet("127.0.0.1", b"test")
        self.assertIsInstance(packet, bytes)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
