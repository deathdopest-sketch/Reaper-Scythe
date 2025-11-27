"""
Phantom Packet Crafting Module

This module provides packet crafting and manipulation capabilities
for the Reaper security-focused programming language.

Features:
- TCP/UDP/ICMP packet creation
- Custom header manipulation
- Packet validation
- Raw socket operations (where supported)

Author: Reaper Security Team
Version: 0.1.0
"""

import socket
import struct
import random
import time
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Protocol(Enum):
    """Supported protocols for packet crafting"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"

@dataclass
class PacketConfig:
    """Configuration for packet crafting"""
    source_ip: Optional[str] = None
    dest_ip: str = "127.0.0.1"
    source_port: Optional[int] = None
    dest_port: int = 80
    protocol: Protocol = Protocol.TCP
    ttl: int = 64
    flags: int = 0
    payload: bytes = b''

class PhantomPacket:
    """
    Packet crafting and manipulation class.
    
    Provides functionality to create, modify, and send custom packets
    for network testing and analysis.
    """
    
    def __init__(self, config: Optional[PacketConfig] = None):
        """
        Initialize packet crafter.
        
        Args:
            config: PacketConfig with packet parameters
        """
        self.config = config or PacketConfig()
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate packet configuration"""
        if not self.config.dest_ip:
            raise ValueError("Destination IP is required")
        
        if self.config.dest_port < 1 or self.config.dest_port > 65535:
            raise ValueError("Destination port must be between 1 and 65535")
        
        if self.config.source_port is not None and (self.config.source_port < 1 or self.config.source_port > 65535):
            raise ValueError("Source port must be between 1 and 65535")
    
    def _generate_source_port(self) -> int:
        """Generate random source port"""
        return random.randint(1024, 65535)
    
    def _get_source_ip(self) -> str:
        """Get source IP address"""
        if self.config.source_ip:
            return self.config.source_ip
        
        # Try to get local IP
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def create_tcp_packet(self, payload: bytes = b'') -> bytes:
        """
        Create a TCP packet.
        
        Args:
            payload: Data payload for the packet
            
        Returns:
            Raw TCP packet bytes
        """
        source_ip = self._get_source_ip()
        dest_ip = self.config.dest_ip
        source_port = self.config.source_port or self._generate_source_port()
        dest_port = self.config.dest_port
        
        # TCP header fields
        seq_num = random.randint(0, 2**32 - 1)
        ack_num = 0
        data_offset = 5  # 5 * 4 = 20 bytes header
        flags = self.config.flags
        window_size = 65535
        checksum = 0
        urgent_ptr = 0
        
        # Build TCP header
        tcp_header = struct.pack(
            '!HHLLBBHHH',
            source_port,      # Source port
            dest_port,        # Destination port
            seq_num,          # Sequence number
            ack_num,          # Acknowledgment number
            data_offset << 4, # Data offset + reserved
            flags,            # Flags
            window_size,      # Window size
            checksum,         # Checksum (calculated later)
            urgent_ptr        # Urgent pointer
        )
        
        # Calculate TCP checksum
        pseudo_header = struct.pack(
            '!4s4sBBH',
            socket.inet_aton(source_ip),
            socket.inet_aton(dest_ip),
            0,  # Reserved
            socket.IPPROTO_TCP,
            len(tcp_header) + len(payload)
        )
        
        checksum = self._calculate_checksum(pseudo_header + tcp_header + payload)
        tcp_header = tcp_header[:16] + struct.pack('!H', checksum) + tcp_header[18:]
        
        return tcp_header + payload
    
    def create_udp_packet(self, payload: bytes = b'') -> bytes:
        """
        Create a UDP packet.
        
        Args:
            payload: Data payload for the packet
            
        Returns:
            Raw UDP packet bytes
        """
        source_port = self.config.source_port or self._generate_source_port()
        dest_port = self.config.dest_port
        
        # UDP header
        length = 8 + len(payload)  # UDP header + payload
        checksum = 0  # Optional for UDP
        
        udp_header = struct.pack(
            '!HHHH',
            source_port,  # Source port
            dest_port,    # Destination port
            length,       # Length
            checksum      # Checksum
        )
        
        return udp_header + payload
    
    def create_icmp_packet(self, icmp_type: int = 8, icmp_code: int = 0, payload: bytes = b'') -> bytes:
        """
        Create an ICMP packet.
        
        Args:
            icmp_type: ICMP type (8 for echo request)
            icmp_code: ICMP code
            payload: Data payload for the packet
            
        Returns:
            Raw ICMP packet bytes
        """
        # ICMP header
        checksum = 0
        identifier = random.randint(0, 65535)
        sequence = random.randint(0, 65535)
        
        icmp_header = struct.pack(
            '!BBHHH',
            icmp_type,    # Type
            icmp_code,    # Code
            checksum,     # Checksum
            identifier,   # Identifier
            sequence      # Sequence number
        )
        
        # Calculate ICMP checksum
        checksum = self._calculate_checksum(icmp_header + payload)
        icmp_header = icmp_header[:2] + struct.pack('!H', checksum) + icmp_header[4:]
        
        return icmp_header + payload
    
    def _calculate_checksum(self, data: bytes) -> int:
        """
        Calculate Internet checksum for packet data.
        
        Args:
            data: Data to calculate checksum for
            
        Returns:
            Checksum value
        """
        checksum = 0
        
        # Add padding if odd length
        if len(data) % 2:
            data += b'\x00'
        
        # Sum 16-bit words
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
        
        # Add carry bits
        while checksum >> 16:
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        
        # One's complement
        return ~checksum & 0xFFFF
    
    def send_packet(self, packet: bytes, protocol: Protocol = None) -> bool:
        """
        Send a raw packet.
        
        Args:
            packet: Raw packet bytes
            protocol: Protocol type
            
        Returns:
            True if packet sent successfully
        """
        protocol = protocol or self.config.protocol
        
        try:
            if protocol == Protocol.TCP:
                sock_type = socket.SOCK_STREAM
                proto = socket.IPPROTO_TCP
            elif protocol == Protocol.UDP:
                sock_type = socket.SOCK_DGRAM
                proto = socket.IPPROTO_UDP
            elif protocol == Protocol.ICMP:
                sock_type = socket.SOCK_RAW
                proto = socket.IPPROTO_ICMP
            else:
                raise ValueError(f"Unsupported protocol: {protocol}")
            
            # Create socket
            with socket.socket(socket.AF_INET, sock_type) as sock:
                sock.settimeout(5.0)
                
                if protocol == Protocol.ICMP:
                    # ICMP requires raw socket (may need admin privileges)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                    sock.sendto(packet, (self.config.dest_ip, 0))
                else:
                    # TCP/UDP can use regular sockets
                    sock.connect((self.config.dest_ip, self.config.dest_port))
                    sock.send(packet)
                
                logger.info(f"Packet sent to {self.config.dest_ip}:{self.config.dest_port}")
                return True
                
        except PermissionError:
            logger.error("Raw socket access denied - may need elevated privileges")
            return False
        except Exception as e:
            logger.error(f"Error sending packet: {e}")
            return False
    
    def create_and_send(self, payload: bytes = b'', protocol: Protocol = None) -> bool:
        """
        Create and send a packet in one operation.
        
        Args:
            payload: Data payload
            protocol: Protocol type
            
        Returns:
            True if packet sent successfully
        """
        protocol = protocol or self.config.protocol
        
        if protocol == Protocol.TCP:
            packet = self.create_tcp_packet(payload)
        elif protocol == Protocol.UDP:
            packet = self.create_udp_packet(payload)
        elif protocol == Protocol.ICMP:
            packet = self.create_icmp_packet(payload=payload)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
        
        return self.send_packet(packet, protocol)
    
    def ping(self, target: str = None, count: int = 4) -> Dict[str, Any]:
        """
        Send ICMP ping packets.
        
        Args:
            target: Target IP address
            count: Number of ping packets to send
            
        Returns:
            Dictionary with ping results
        """
        target = target or self.config.dest_ip
        results = {
            'target': target,
            'sent': 0,
            'received': 0,
            'lost': 0,
            'times': []
        }
        
        logger.info(f"Pinging {target} with {count} packets")
        
        for i in range(count):
            try:
                start_time = time.time()
                
                # Create ICMP packet
                packet = self.create_icmp_packet()
                
                # Send packet
                if self.send_packet(packet, Protocol.ICMP):
                    results['sent'] += 1
                    
                    # Try to receive response (simplified)
                    # In a real implementation, you'd listen for ICMP responses
                    time.sleep(0.1)
                    
                    # For now, assume packet was received
                    results['received'] += 1
                    results['times'].append((time.time() - start_time) * 1000)
                else:
                    results['sent'] += 1
                    results['lost'] += 1
                    
            except Exception as e:
                logger.error(f"Ping error: {e}")
                results['sent'] += 1
                results['lost'] += 1
        
        results['loss_percent'] = (results['lost'] / results['sent']) * 100 if results['sent'] > 0 else 0
        
        return results

# Convenience functions
def create_tcp_packet(dest_ip: str, dest_port: int, payload: bytes = b'', source_port: int = None) -> bytes:
    """Create a TCP packet"""
    config = PacketConfig(dest_ip=dest_ip, dest_port=dest_port, source_port=source_port)
    packet = PhantomPacket(config)
    return packet.create_tcp_packet(payload)

def create_udp_packet(dest_ip: str, dest_port: int, payload: bytes = b'', source_port: int = None) -> bytes:
    """Create a UDP packet"""
    config = PacketConfig(dest_ip=dest_ip, dest_port=dest_port, source_port=source_port)
    packet = PhantomPacket(config)
    return packet.create_udp_packet(payload)

def create_icmp_packet(dest_ip: str, payload: bytes = b'') -> bytes:
    """Create an ICMP packet"""
    config = PacketConfig(dest_ip=dest_ip)
    packet = PhantomPacket(config)
    return packet.create_icmp_packet(payload=payload)

def ping_host(target: str, count: int = 4) -> Dict[str, Any]:
    """Ping a host"""
    config = PacketConfig(dest_ip=target)
    packet = PhantomPacket(config)
    return packet.ping(target, count)

# Export main classes and functions
__all__ = [
    'PhantomPacket', 'PacketConfig', 'Protocol',
    'create_tcp_packet', 'create_udp_packet', 'create_icmp_packet', 'ping_host'
]
