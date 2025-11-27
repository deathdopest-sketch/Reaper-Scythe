# Phantom Network Operations Library
# Network scanning, packet crafting, DNS operations

__version__ = "0.1.0"
__author__ = "Reaper Security Team"

# Core features implemented in L1-T002
from .scanner import (
    PhantomScanner, ScanType, ScanResult, PortResult, ScanConfig,
    scan_port, scan_ports, scan_range, get_open_ports, get_service_summary
)

from .packet import (
    PhantomPacket, PacketConfig, Protocol,
    create_tcp_packet, create_udp_packet, create_icmp_packet, ping_host
)

from .dns import (
    PhantomDNS, DNSConfig, DNSRecord, DNSRecordType, DNSQueryClass,
    resolve_domain, reverse_lookup, query_dns
)

__all__ = [
    # Scanner
    'PhantomScanner', 'ScanType', 'ScanResult', 'PortResult', 'ScanConfig',
    'scan_port', 'scan_ports', 'scan_range', 'get_open_ports', 'get_service_summary',
    
    # Packet crafting
    'PhantomPacket', 'PacketConfig', 'Protocol',
    'create_tcp_packet', 'create_udp_packet', 'create_icmp_packet', 'ping_host',
    
    # DNS operations
    'PhantomDNS', 'DNSConfig', 'DNSRecord', 'DNSRecordType', 'DNSQueryClass',
    'resolve_domain', 'reverse_lookup', 'query_dns'
]
