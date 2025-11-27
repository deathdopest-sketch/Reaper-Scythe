# Shadow Anonymity Library
# Tor integration, VPN automation, MAC spoofing, traffic obfuscation

__version__ = "0.1.0"
__author__ = "Reaper Security Team"

# Core features implemented in L1-T006
from .tor.manager import (
    ShadowTorManager, TorCircuitStatus, TorNodeType, TorNode, TorCircuit, TorOperationResult,
    start_tor_service, check_tor_ip, make_tor_request
)

from .vpn.manager import (
    ShadowVPNManager, VPNProtocol, VPNStatus, VPNServer, VPNConfig, VPNOperationResult,
    find_best_vpn_server, connect_to_vpn, disconnect_vpn, check_vpn_ip
)

from .network.manager import (
    ShadowNetworkManager, NetworkInterfaceType, MACAddressFormat, NetworkInterface, NetworkOperationResult,
    get_network_interfaces, spoof_mac_address, restore_mac_address, randomize_mac_addresses, generate_random_mac
)

from .obfuscation.manager import (
    ShadowObfuscationManager, ObfuscationMethod, FingerprintType, FingerprintProfile, 
    ObfuscationConfig, ObfuscationResult, generate_fingerprint_profile, obfuscate_request,
    randomize_traffic_pattern, generate_tls_fingerprint
)

__all__ = [
    # Tor integration
    'ShadowTorManager', 'TorCircuitStatus', 'TorNodeType', 'TorNode', 'TorCircuit', 'TorOperationResult',
    'start_tor_service', 'check_tor_ip', 'make_tor_request',
    
    # VPN automation
    'ShadowVPNManager', 'VPNProtocol', 'VPNStatus', 'VPNServer', 'VPNConfig', 'VPNOperationResult',
    'find_best_vpn_server', 'connect_to_vpn', 'disconnect_vpn', 'check_vpn_ip',
    
    # Network anonymity
    'ShadowNetworkManager', 'NetworkInterfaceType', 'MACAddressFormat', 'NetworkInterface', 'NetworkOperationResult',
    'get_network_interfaces', 'spoof_mac_address', 'restore_mac_address', 'randomize_mac_addresses', 'generate_random_mac',
    
    # Traffic obfuscation
    'ShadowObfuscationManager', 'ObfuscationMethod', 'FingerprintType', 'FingerprintProfile', 
    'ObfuscationConfig', 'ObfuscationResult', 'generate_fingerprint_profile', 'obfuscate_request',
    'randomize_traffic_pattern', 'generate_tls_fingerprint'
]

# Will be implemented in L1-T010 and L1-T011
# Core features: Tor, VPN, MAC spoofing
# Advanced features: IP rotation, traffic obfuscation, metadata stripping

__all__ = [
    # Will be populated as features are implemented
]
