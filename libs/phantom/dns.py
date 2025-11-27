"""
Phantom DNS Operations Module

This module provides DNS query and manipulation capabilities
for the Reaper security-focused programming language.

Features:
- DNS queries (A, AAAA, MX, TXT, NS, CNAME, etc.)
- DNS zone transfer attempts
- Custom DNS server queries
- DNS spoofing helpers (educational)

Author: Reaper Security Team
Version: 0.1.0
"""

import socket
import struct
import random
import logging
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DNSRecordType(Enum):
    """DNS record types"""
    A = 1
    AAAA = 28
    CNAME = 5
    MX = 15
    NS = 2
    PTR = 12
    SOA = 6
    TXT = 16
    SRV = 33
    AXFR = 252  # Zone transfer

class DNSQueryClass(Enum):
    """DNS query classes"""
    IN = 1  # Internet

@dataclass
class DNSRecord:
    """DNS record result"""
    name: str
    record_type: DNSRecordType
    ttl: int
    data: str
    priority: Optional[int] = None  # For MX records

@dataclass
class DNSConfig:
    """Configuration for DNS operations"""
    dns_server: str = "8.8.8.8"
    timeout: float = 5.0
    retries: int = 3
    port: int = 53

class PhantomDNS:
    """
    DNS operations class for Phantom library.
    
    Provides DNS querying, zone transfer attempts, and DNS analysis
    capabilities for network reconnaissance.
    """
    
    def __init__(self, config: Optional[DNSConfig] = None):
        """
        Initialize DNS client.
        
        Args:
            config: DNSConfig with DNS server settings
        """
        self.config = config or DNSConfig()
    
    def _encode_domain_name(self, domain: str) -> bytes:
        """
        Encode domain name for DNS packet.
        
        Args:
            domain: Domain name to encode
            
        Returns:
            Encoded domain name bytes
        """
        encoded = b''
        for part in domain.split('.'):
            encoded += struct.pack('!B', len(part)) + part.encode('utf-8')
        encoded += b'\x00'  # Null terminator
        return encoded
    
    def _decode_domain_name(self, data: bytes, offset: int) -> Tuple[str, int]:
        """
        Decode domain name from DNS packet.
        
        Args:
            data: DNS packet data
            offset: Starting offset
            
        Returns:
            Tuple of (domain_name, new_offset)
        """
        domain_parts = []
        original_offset = offset
        
        while offset < len(data):
            length = data[offset]
            offset += 1
            
            if length == 0:
                break
            
            if length & 0xC0 == 0xC0:  # Compression pointer
                pointer = ((length & 0x3F) << 8) + data[offset]
                offset += 1
                compressed_name, _ = self._decode_domain_name(data, pointer)
                domain_parts.append(compressed_name)
                break
            
            if length > 63:
                raise ValueError("Invalid domain name length")
            
            part = data[offset:offset + length].decode('utf-8')
            domain_parts.append(part)
            offset += length
        
        return '.'.join(domain_parts), offset
    
    def _create_dns_query(self, domain: str, record_type: DNSRecordType, query_id: int = None) -> bytes:
        """
        Create DNS query packet.
        
        Args:
            domain: Domain to query
            record_type: Type of DNS record
            query_id: Query ID (random if None)
            
        Returns:
            DNS query packet bytes
        """
        if query_id is None:
            query_id = random.randint(1, 65535)
        
        # DNS header
        flags = 0x0100  # Standard query, recursion desired
        questions = 1
        answers = 0
        authority = 0
        additional = 0
        
        header = struct.pack(
            '!HHHHHH',
            query_id,    # Transaction ID
            flags,       # Flags
            questions,   # Questions
            answers,     # Answer RRs
            authority,   # Authority RRs
            additional   # Additional RRs
        )
        
        # Question section
        question = self._encode_domain_name(domain)
        question += struct.pack('!HH', record_type.value, DNSQueryClass.IN.value)
        
        return header + question
    
    def _parse_dns_response(self, data: bytes) -> List[DNSRecord]:
        """
        Parse DNS response packet.
        
        Args:
            data: DNS response packet
            
        Returns:
            List of DNSRecord objects
        """
        if len(data) < 12:
            raise ValueError("Invalid DNS packet")
        
        # Parse header
        query_id, flags, questions, answers, authority, additional = struct.unpack('!HHHHHH', data[:12])
        
        records = []
        offset = 12
        
        # Skip question section
        for _ in range(questions):
            _, offset = self._decode_domain_name(data, offset)
            offset += 4  # Skip type and class
        
        # Parse answer section
        for _ in range(answers):
            name, offset = self._decode_domain_name(data, offset)
            
            if offset + 10 > len(data):
                break
            
            record_type, record_class, ttl, data_length = struct.unpack('!HHIH', data[offset:offset + 10])
            offset += 10
            
            if offset + data_length > len(data):
                break
            
            record_data = data[offset:offset + data_length]
            offset += data_length
            
            # Parse record data based on type
            if record_type == DNSRecordType.A.value:
                if len(record_data) == 4:
                    ip = socket.inet_ntoa(record_data)
                    records.append(DNSRecord(name, DNSRecordType.A, ttl, ip))
            elif record_type == DNSRecordType.AAAA.value:
                if len(record_data) == 16:
                    ip = socket.inet_ntop(socket.AF_INET6, record_data)
                    records.append(DNSRecord(name, DNSRecordType.AAAA, ttl, ip))
            elif record_type == DNSRecordType.CNAME.value:
                cname, _ = self._decode_domain_name(data, offset - data_length)
                records.append(DNSRecord(name, DNSRecordType.CNAME, ttl, cname))
            elif record_type == DNSRecordType.MX.value:
                if len(record_data) >= 2:
                    priority = struct.unpack('!H', record_data[:2])[0]
                    mx_host, _ = self._decode_domain_name(data, offset - data_length + 2)
                    records.append(DNSRecord(name, DNSRecordType.MX, ttl, mx_host, priority))
            elif record_type == DNSRecordType.TXT.value:
                txt_data = record_data.decode('utf-8', errors='ignore')
                records.append(DNSRecord(name, DNSRecordType.TXT, ttl, txt_data))
            elif record_type == DNSRecordType.NS.value:
                ns_host, _ = self._decode_domain_name(data, offset - data_length)
                records.append(DNSRecord(name, DNSRecordType.NS, ttl, ns_host))
        
        return records
    
    def query(self, domain: str, record_type: DNSRecordType = DNSRecordType.A) -> List[DNSRecord]:
        """
        Perform DNS query.
        
        Args:
            domain: Domain to query
            record_type: Type of DNS record
            
        Returns:
            List of DNSRecord objects
        """
        logger.info(f"Querying {record_type.name} record for {domain}")
        
        query_packet = self._create_dns_query(domain, record_type)
        
        for attempt in range(self.config.retries):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.settimeout(self.config.timeout)
                    sock.sendto(query_packet, (self.config.dns_server, self.config.port))
                    
                    response, _ = sock.recvfrom(512)
                    records = self._parse_dns_response(response)
                    
                    logger.info(f"Received {len(records)} records")
                    return records
                    
            except socket.timeout:
                logger.warning(f"DNS query timeout (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"DNS query error: {e}")
        
        logger.error(f"DNS query failed after {self.config.retries} attempts")
        return []
    
    def resolve(self, domain: str) -> List[str]:
        """
        Resolve domain to IP addresses.
        
        Args:
            domain: Domain to resolve
            
        Returns:
            List of IP addresses
        """
        records = self.query(domain, DNSRecordType.A)
        return [record.data for record in records if record.record_type == DNSRecordType.A]
    
    def reverse_lookup(self, ip: str) -> List[str]:
        """
        Perform reverse DNS lookup.
        
        Args:
            ip: IP address to lookup
            
        Returns:
            List of domain names
        """
        try:
            # Convert IP to reverse lookup format
            if ':' in ip:  # IPv6
                parts = ip.split(':')
                reverse_domain = '.'.join(reversed(parts)) + '.ip6.arpa'
            else:  # IPv4
                parts = ip.split('.')
                reverse_domain = '.'.join(reversed(parts)) + '.in-addr.arpa'
            
            records = self.query(reverse_domain, DNSRecordType.PTR)
            return [record.data for record in records if record.record_type == DNSRecordType.PTR]
            
        except Exception as e:
            logger.error(f"Reverse lookup error: {e}")
            return []
    
    def get_mx_records(self, domain: str) -> List[DNSRecord]:
        """
        Get MX records for domain.
        
        Args:
            domain: Domain to query
            
        Returns:
            List of MX records
        """
        return self.query(domain, DNSRecordType.MX)
    
    def get_txt_records(self, domain: str) -> List[DNSRecord]:
        """
        Get TXT records for domain.
        
        Args:
            domain: Domain to query
            
        Returns:
            List of TXT records
        """
        return self.query(domain, DNSRecordType.TXT)
    
    def get_ns_records(self, domain: str) -> List[DNSRecord]:
        """
        Get NS records for domain.
        
        Args:
            domain: Domain to query
            
        Returns:
            List of NS records
        """
        return self.query(domain, DNSRecordType.NS)
    
    def zone_transfer(self, domain: str, nameserver: str = None) -> List[DNSRecord]:
        """
        Attempt DNS zone transfer (AXFR).
        
        Args:
            domain: Domain for zone transfer
            nameserver: Nameserver to query (uses configured DNS server if None)
            
        Returns:
            List of DNS records from zone transfer
            
        Note:
            Zone transfers are often restricted for security reasons.
            This is for educational purposes only.
        """
        nameserver = nameserver or self.config.dns_server
        logger.warning(f"Attempting zone transfer for {domain} from {nameserver}")
        
        try:
            # Create AXFR query
            query_packet = self._create_dns_query(domain, DNSRecordType.AXFR)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.config.timeout)
                sock.connect((nameserver, self.config.port))
                
                # Send query
                sock.send(query_packet)
                
                # Receive response
                response = sock.recv(4096)
                records = self._parse_dns_response(response)
                
                logger.info(f"Zone transfer successful: {len(records)} records")
                return records
                
        except Exception as e:
            logger.warning(f"Zone transfer failed: {e}")
            return []
    
    def dns_enumeration(self, domain: str) -> Dict[str, List[DNSRecord]]:
        """
        Perform comprehensive DNS enumeration.
        
        Args:
            domain: Domain to enumerate
            
        Returns:
            Dictionary mapping record types to lists of records
        """
        logger.info(f"Performing DNS enumeration for {domain}")
        
        results = {}
        record_types = [
            DNSRecordType.A,
            DNSRecordType.AAAA,
            DNSRecordType.CNAME,
            DNSRecordType.MX,
            DNSRecordType.NS,
            DNSRecordType.TXT,
            DNSRecordType.SOA
        ]
        
        for record_type in record_types:
            try:
                records = self.query(domain, record_type)
                if records:
                    results[record_type.name] = records
            except Exception as e:
                logger.warning(f"Failed to query {record_type.name} records: {e}")
        
        return results

# Convenience functions
def resolve_domain(domain: str, dns_server: str = "8.8.8.8") -> List[str]:
    """Resolve domain to IP addresses"""
    config = DNSConfig(dns_server=dns_server)
    dns = PhantomDNS(config)
    return dns.resolve(domain)

def reverse_lookup(ip: str, dns_server: str = "8.8.8.8") -> List[str]:
    """Perform reverse DNS lookup"""
    config = DNSConfig(dns_server=dns_server)
    dns = PhantomDNS(config)
    return dns.reverse_lookup(ip)

def query_dns(domain: str, record_type: DNSRecordType, dns_server: str = "8.8.8.8") -> List[DNSRecord]:
    """Perform DNS query"""
    config = DNSConfig(dns_server=dns_server)
    dns = PhantomDNS(config)
    return dns.query(domain, record_type)

# Export main classes and functions
__all__ = [
    'PhantomDNS', 'DNSConfig', 'DNSRecord', 'DNSRecordType', 'DNSQueryClass',
    'resolve_domain', 'reverse_lookup', 'query_dns'
]
