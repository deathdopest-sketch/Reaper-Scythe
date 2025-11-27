#!/usr/bin/env python3
"""
Phantom Library Demo Script

This script demonstrates the core features of the Phantom network operations library
including port scanning, packet crafting, and DNS operations.

Usage: python phantom_demo.py

Author: Reaper Security Team
Version: 0.1.0
"""

import sys
import time
from libs.phantom import (
    PhantomScanner, ScanType, ScanResult, ScanConfig,
    PhantomPacket, PacketConfig, Protocol,
    PhantomDNS, DNSConfig, DNSRecordType,
    scan_port, scan_ports, ping_host, resolve_domain
)

def demo_port_scanning():
    """Demonstrate port scanning capabilities"""
    print("=" * 60)
    print("PHANTOM PORT SCANNING DEMO")
    print("=" * 60)
    
    # Create scanner with custom configuration
    config = ScanConfig(timeout=2.0, threads=5, rate_limit=0.1)
    scanner = PhantomScanner(config)
    
    target = "127.0.0.1"  # Localhost for demo
    ports = [22, 80, 443, 8080, 3389]  # Common ports
    
    print(f"Scanning {target} on ports: {ports}")
    print("-" * 40)
    
    # Scan individual ports
    for port in ports:
        result = scanner.scan_port(target, port, ScanType.TCP_CONNECT)
        status_icon = "✓" if result.status == ScanResult.OPEN else "✗"
        print(f"{status_icon} Port {port:4d}: {result.status.value:8s} ({result.response_time:.3f}s)")
    
    print("\nScanning port range 80-85...")
    results = scanner.scan_range(target, 80, 85)
    
    open_ports = scanner.get_open_ports(results)
    services = scanner.get_service_summary(results)
    
    print(f"Open ports found: {open_ports}")
    if services:
        print("Services detected:")
        for service, ports in services.items():
            print(f"  {service}: {ports}")

def demo_packet_crafting():
    """Demonstrate packet crafting capabilities"""
    print("\n" + "=" * 60)
    print("PHANTOM PACKET CRAFTING DEMO")
    print("=" * 60)
    
    # Create packet configuration
    config = PacketConfig(
        dest_ip="127.0.0.1",
        dest_port=80,
        source_port=12345
    )
    packet = PhantomPacket(config)
    
    print("Creating custom packets...")
    print("-" * 40)
    
    # Create different packet types
    tcp_packet = packet.create_tcp_packet(b"GET / HTTP/1.1\r\n\r\n")
    udp_packet = packet.create_udp_packet(b"Hello UDP!")
    icmp_packet = packet.create_icmp_packet()
    
    print(f"TCP packet size:  {len(tcp_packet)} bytes")
    print(f"UDP packet size:  {len(udp_packet)} bytes")
    print(f"ICMP packet size: {len(icmp_packet)} bytes")
    
    # Demonstrate ping functionality
    print("\nPing test (4 packets)...")
    ping_results = packet.ping("127.0.0.1", 4)
    
    print(f"Target: {ping_results['target']}")
    print(f"Sent: {ping_results['sent']}, Received: {ping_results['received']}")
    print(f"Lost: {ping_results['lost']} ({ping_results['loss_percent']:.1f}%)")
    
    if ping_results['times']:
        avg_time = sum(ping_results['times']) / len(ping_results['times'])
        print(f"Average response time: {avg_time:.1f}ms")

def demo_dns_operations():
    """Demonstrate DNS operations"""
    print("\n" + "=" * 60)
    print("PHANTOM DNS OPERATIONS DEMO")
    print("=" * 60)
    
    # Create DNS client
    dns_config = DNSConfig(dns_server="8.8.8.8", timeout=5.0)
    dns = PhantomDNS(dns_config)
    
    test_domains = ["google.com", "github.com", "stackoverflow.com"]
    
    print("DNS Resolution Tests:")
    print("-" * 40)
    
    for domain in test_domains:
        try:
            print(f"\nResolving {domain}...")
            
            # A records
            a_records = dns.query(domain, DNSRecordType.A)
            if a_records:
                ips = [record.data for record in a_records]
                print(f"  A records: {', '.join(ips[:3])}{'...' if len(ips) > 3 else ''}")
            
            # MX records
            mx_records = dns.get_mx_records(domain)
            if mx_records:
                mx_list = [f"{record.data} (pri:{record.priority})" for record in mx_records[:2]]
                print(f"  MX records: {', '.join(mx_list)}{'...' if len(mx_records) > 2 else ''}")
            
            # TXT records
            txt_records = dns.get_txt_records(domain)
            if txt_records:
                print(f"  TXT records: {len(txt_records)} found")
            
        except Exception as e:
            print(f"  Error resolving {domain}: {e}")
    
    # Reverse DNS lookup
    print(f"\nReverse DNS lookup for 8.8.8.8...")
    try:
        reverse_results = dns.reverse_lookup("8.8.8.8")
        if reverse_results:
            print(f"  Result: {reverse_results[0]}")
        else:
            print("  No reverse DNS record found")
    except Exception as e:
        print(f"  Error: {e}")

def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print("\n" + "=" * 60)
    print("PHANTOM CONVENIENCE FUNCTIONS DEMO")
    print("=" * 60)
    
    print("Using convenience functions for quick operations...")
    print("-" * 40)
    
    # Quick port scan
    print("Quick port scan:")
    result = scan_port("127.0.0.1", 80)
    print(f"  Port 80: {result.status.value}")
    
    # Quick DNS resolution
    print("\nQuick DNS resolution:")
    try:
        ips = resolve_domain("google.com")
        if ips:
            print(f"  google.com -> {ips[0]}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Quick ping
    print("\nQuick ping test:")
    try:
        ping_result = ping_host("127.0.0.1", 2)
        print(f"  Ping to 127.0.0.1: {ping_result['received']}/{ping_result['sent']} packets")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    """Main demo function"""
    print("PHANTOM NETWORK OPERATIONS LIBRARY DEMO")
    print("Reaper Security Language - Core Features")
    print(f"Python version: {sys.version}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all demos
        demo_port_scanning()
        demo_packet_crafting()
        demo_dns_operations()
        demo_convenience_functions()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("The Phantom library provides comprehensive network operations")
        print("capabilities for security testing and network analysis.")
        print("\nFeatures demonstrated:")
        print("✓ Port scanning (TCP/UDP)")
        print("✓ Packet crafting and manipulation")
        print("✓ DNS queries and resolution")
        print("✓ Network connectivity testing")
        print("✓ Rate limiting and safety checks")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
