"""
Shadow Anonymity Library Demo
Demonstrates Tor integration, VPN automation, MAC spoofing, and traffic obfuscation
"""

import os
import sys
import time
import tempfile

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.shadow.tor.manager import (
    ShadowTorManager, TorCircuitStatus, TorNodeType, TorNode, TorCircuit, TorOperationResult,
    start_tor_service, check_tor_ip, make_tor_request
)
from libs.shadow.vpn.manager import (
    ShadowVPNManager, VPNProtocol, VPNStatus, VPNServer, VPNConfig, VPNOperationResult,
    find_best_vpn_server, connect_to_vpn, disconnect_vpn, check_vpn_ip
)
from libs.shadow.network.manager import (
    ShadowNetworkManager, NetworkInterfaceType, MACAddressFormat, NetworkInterface, NetworkOperationResult,
    get_network_interfaces, spoof_mac_address, restore_mac_address, randomize_mac_addresses, generate_random_mac
)
from libs.shadow.obfuscation.manager import (
    ShadowObfuscationManager, ObfuscationMethod, FingerprintType, FingerprintProfile, 
    ObfuscationConfig, ObfuscationResult, generate_fingerprint_profile, obfuscate_request,
    randomize_traffic_pattern, generate_tls_fingerprint
)

def run_shadow_demo():
    print("--- Shadow Anonymity Library Demo ---")

    # --- Tor Integration Demo ---
    print("\n### Tor Integration Demo ###")
    tor_manager = ShadowTorManager({'safe_mode': True})  # Start in safe mode for demo
    print("Tor manager created with safe mode enabled")

    # Tor service management (safe mode)
    print("\nTor service management (safe mode):")
    start_result = tor_manager.start_tor()
    print(f"  Start Tor: {start_result.success} - {start_result.message}")
    
    stop_result = tor_manager.stop_tor()
    print(f"  Stop Tor: {stop_result.success} - {stop_result.message}")
    
    status_result = tor_manager.get_tor_status()
    print(f"  Tor Status: {status_result.success} - {status_result.message}")

    # Circuit management (safe mode)
    print("\nCircuit management (safe mode):")
    circuit_result = tor_manager.new_circuit()
    print(f"  New circuit: {circuit_result.success} - {circuit_result.message}")
    
    circuits_result = tor_manager.get_circuits()
    print(f"  Get circuits: {circuits_result.success} - {circuits_result.message}")
    
    close_result = tor_manager.close_circuit("test_circuit")
    print(f"  Close circuit: {close_result.success} - {close_result.message}")

    # Tor requests (safe mode)
    print("\nTor requests (safe mode):")
    request_result = tor_manager.make_request("http://example.com")
    print(f"  Make request: {request_result.success} - {request_result.message}")
    
    ip_result = tor_manager.check_ip()
    print(f"  Check IP: {ip_result.success} - {ip_result.message}")

    # User agent rotation
    print("\nUser agent rotation:")
    for i in range(3):
        user_agent = tor_manager._get_random_user_agent()
        print(f"  User agent {i+1}: {user_agent[:50]}...")

    # Operation log
    print("\nTor operation log:")
    log = tor_manager.get_operation_log()
    print(f"  Total operations logged: {len(log)}")
    for entry in log[-2:]:  # Print last 2 entries
        print(f"    {entry['operation']}: {entry['message']}")


    # --- VPN Automation Demo ---
    print("\n### VPN Automation Demo ###")
    vpn_manager = ShadowVPNManager({'safe_mode': True})  # Start in safe mode
    print("VPN manager created with safe mode enabled")

    # Server management (safe mode)
    print("\nServer management (safe mode):")
    servers_result = vpn_manager.get_servers()
    print(f"  Get servers: {servers_result.success} - {servers_result.message}")
    
    best_server_result = vpn_manager.find_best_server()
    print(f"  Find best server: {best_server_result.success} - {best_server_result.message}")
    
    filtered_servers_result = vpn_manager.get_servers(country="United States", premium_only=True)
    print(f"  Filtered servers: {filtered_servers_result.success} - {filtered_servers_result.message}")

    # VPN connection (safe mode)
    print("\nVPN connection (safe mode):")
    test_server = VPNServer(
        name="Demo-Server",
        country="United States",
        city="New York",
        ip_address="198.51.100.1",
        port=1194,
        protocol=VPNProtocol.OPENVPN,
        load=45,
        ping=25.5,
        bandwidth=1000,
        features=["P2P", "Streaming", "Gaming"]
    )
    
    connect_result = vpn_manager.connect(test_server)
    print(f"  Connect to VPN: {connect_result.success} - {connect_result.message}")
    
    status_result = vpn_manager.get_status()
    print(f"  VPN Status: {status_result.success} - {status_result.message}")
    
    disconnect_result = vpn_manager.disconnect()
    print(f"  Disconnect VPN: {disconnect_result.success} - {disconnect_result.message}")

    # IP checking (safe mode)
    print("\nIP checking (safe mode):")
    ip_result = vpn_manager.check_ip()
    print(f"  Check IP: {ip_result.success} - {ip_result.message}")

    # VPN configuration examples
    print("\nVPN configuration examples:")
    basic_config = VPNConfig(server=test_server)
    print(f"  Basic config: {basic_config.server.name} - {basic_config.cipher}")
    
    advanced_config = VPNConfig(
        server=test_server,
        username="demo_user",
        password="demo_pass",
        cipher="AES-256-GCM",
        auth="SHA256"
    )
    print(f"  Advanced config: {advanced_config.username} - {advanced_config.cipher}")

    # VPN operation log
    print("\nVPN operation log:")
    log = vpn_manager.get_operation_log()
    print(f"  Total operations logged: {len(log)}")
    for entry in log[-2:]:  # Print last 2 entries
        print(f"    {entry['operation']}: {entry['message']}")


    # --- Network Anonymity Demo ---
    print("\n### Network Anonymity Demo ###")
    network_manager = ShadowNetworkManager({'safe_mode': True})  # Start in safe mode
    print("Network manager created with safe mode enabled")

    # Interface management (safe mode)
    print("\nInterface management (safe mode):")
    interfaces_result = network_manager.get_interfaces()
    print(f"  Get interfaces: {interfaces_result.success} - {interfaces_result.message}")

    # MAC address operations (safe mode)
    print("\nMAC address operations (safe mode):")
    spoof_result = network_manager.spoof_mac("eth0", "00:11:22:33:44:55")
    print(f"  Spoof MAC: {spoof_result.success} - {spoof_result.message}")
    
    restore_result = network_manager.restore_mac("eth0")
    print(f"  Restore MAC: {restore_result.success} - {restore_result.message}")
    
    randomize_result = network_manager.randomize_all_macs()
    print(f"  Randomize MACs: {randomize_result.success} - {randomize_result.message}")

    # MAC address generation
    print("\nMAC address generation:")
    random_mac = network_manager.generate_random_mac()
    print(f"  Random MAC: {random_mac}")
    
    intel_mac = network_manager.generate_random_mac("Intel")
    print(f"  Intel MAC: {intel_mac}")
    
    apple_mac = network_manager.generate_random_mac("Apple")
    print(f"  Apple MAC: {apple_mac}")
    
    # Different formats
    mac_dash = network_manager.generate_random_mac(format=MACAddressFormat.DASH)
    print(f"  MAC (dash): {mac_dash}")
    
    mac_dot = network_manager.generate_random_mac(format=MACAddressFormat.DOT)
    print(f"  MAC (dot): {mac_dot}")
    
    mac_none = network_manager.generate_random_mac(format=MACAddressFormat.NONE)
    print(f"  MAC (none): {mac_none}")

    # MAC address validation
    print("\nMAC address validation:")
    valid_macs = ["00:11:22:33:44:55", "00-11-22-33-44-55", "00.11.22.33.44.55", "001122334455"]
    for mac in valid_macs:
        is_valid = network_manager._validate_mac_address(mac)
        print(f"  {mac}: {'Valid' if is_valid else 'Invalid'}")
    
    invalid_macs = ["00:11:22:33:44", "00:11:22:33:44:GG", "invalid_mac"]
    for mac in invalid_macs:
        is_valid = network_manager._validate_mac_address(mac)
        print(f"  {mac}: {'Valid' if is_valid else 'Invalid'}")

    # Interface type detection
    print("\nInterface type detection:")
    interface_types = [
        ("wlan0", "WiFi"),
        ("eth0", "Ethernet"),
        ("bluetooth0", "Bluetooth"),
        ("tun0", "Virtual"),
        ("unknown0", "Unknown")
    ]
    for interface_name, expected_type in interface_types:
        detected_type = network_manager._determine_interface_type(interface_name, "00:11:22:33:44:55")
        print(f"  {interface_name}: {detected_type.value}")

    # Vendor detection
    print("\nVendor detection:")
    test_macs = ["00:0C:29:11:22:33", "00:1B:21:11:22:33", "52:54:00:11:22:33", "FF:FF:FF:11:22:33"]
    for mac in test_macs:
        vendor = network_manager._get_mac_vendor(mac)
        print(f"  {mac}: {vendor}")

    # Network operation log
    print("\nNetwork operation log:")
    log = network_manager.get_operation_log()
    print(f"  Total operations logged: {len(log)}")
    for entry in log[-2:]:  # Print last 2 entries
        print(f"    {entry['operation']}: {entry['message']}")


    # --- Traffic Obfuscation Demo ---
    print("\n### Traffic Obfuscation Demo ###")
    obfuscation_config = ObfuscationConfig(
        methods=[ObfuscationMethod.HTTP_HEADERS, ObfuscationMethod.USER_AGENT_ROTATION],
        delay_min=1.0,
        delay_max=3.0,
        user_agent_rotation=True,
        header_randomization=True,
        timing_randomization=True
    )
    obfuscation_manager = ShadowObfuscationManager(obfuscation_config)
    print("Obfuscation manager created with safe mode enabled")

    # Fingerprint profile management (safe mode)
    print("\nFingerprint profile management (safe mode):")
    profiles_result = obfuscation_manager.get_fingerprint_profiles()
    print(f"  Get profiles: {profiles_result.success} - {profiles_result.message}")

    # Fingerprint profile generation
    print("\nFingerprint profile generation:")
    browser_profile = obfuscation_manager.generate_fingerprint_profile(FingerprintType.BROWSER)
    print(f"  Browser profile: {browser_profile.profile_id}")
    print(f"    User agent: {browser_profile.user_agent[:50]}...")
    print(f"    Screen: {browser_profile.screen_resolution}")
    print(f"    Timezone: {browser_profile.timezone}")
    print(f"    Language: {browser_profile.language}")
    print(f"    Platform: {browser_profile.platform}")
    print(f"    Plugins: {len(browser_profile.plugins)} plugins")
    print(f"    Fonts: {len(browser_profile.fonts)} fonts")
    
    device_profile = obfuscation_manager.generate_fingerprint_profile(FingerprintType.DEVICE)
    print(f"  Device profile: {device_profile.profile_id}")
    print(f"    User agent: {device_profile.user_agent[:50]}...")
    print(f"    Screen: {device_profile.screen_resolution}")

    # Fingerprint generation
    print("\nFingerprint generation:")
    canvas_fp = obfuscation_manager._generate_canvas_fingerprint()
    print(f"  Canvas fingerprint: {canvas_fp}")
    
    webgl_fp = obfuscation_manager._generate_webgl_fingerprint()
    print(f"  WebGL fingerprint: {webgl_fp}")
    
    audio_fp = obfuscation_manager._generate_audio_fingerprint()
    print(f"  Audio fingerprint: {audio_fp}")

    # Traffic obfuscation (safe mode)
    print("\nTraffic obfuscation (safe mode):")
    request_result = obfuscation_manager.obfuscate_request("http://example.com")
    print(f"  Obfuscated request: {request_result.success} - {request_result.message}")
    
    requests_data = [
        {"url": "http://example.com", "method": "GET"},
        {"url": "http://test.com", "method": "POST", "data": {"key": "value"}},
        {"url": "http://demo.com", "method": "GET"}
    ]
    pattern_result = obfuscation_manager.obfuscate_traffic_pattern(requests_data)
    print(f"  Traffic pattern obfuscation: {pattern_result.success} - {pattern_result.message}")
    
    domains = ["example.com", "test.com", "demo.com"]
    dns_result = obfuscation_manager.randomize_dns_queries(domains)
    print(f"  DNS query randomization: {dns_result.success} - {dns_result.message}")
    
    tls_result = obfuscation_manager.generate_tls_fingerprint()
    print(f"  TLS fingerprint generation: {tls_result.success} - {tls_result.message}")

    # Header randomization
    print("\nHeader randomization:")
    print("  Before randomization:")
    for key, value in list(obfuscation_manager.session.headers.items())[:3]:
        print(f"    {key}: {value}")
    
    obfuscation_manager._randomize_headers()
    print("  After randomization:")
    for key, value in list(obfuscation_manager.session.headers.items())[:3]:
        print(f"    {key}: {value}")

    # Obfuscation operation log
    print("\nObfuscation operation log:")
    log = obfuscation_manager.get_operation_log()
    print(f"  Total operations logged: {len(log)}")
    for entry in log[-2:]:  # Print last 2 entries
        print(f"    {entry['operation']}: {entry['message']}")


    # --- Convenience Functions Demo ---
    print("\n### Convenience Functions Demo ###")

    print("\nTor convenience functions:")
    result = start_tor_service()
    print(f"  start_tor_service(): {result.success} - {result.message}")
    
    result = check_tor_ip()
    print(f"  check_tor_ip(): {result.success} - {result.message}")
    
    result = make_tor_request("http://example.com")
    print(f"  make_tor_request(): {result.success} - {result.message}")

    print("\nVPN convenience functions:")
    result = find_best_vpn_server()
    print(f"  find_best_vpn_server(): {result.success} - {result.message}")
    
    result = disconnect_vpn()
    print(f"  disconnect_vpn(): {result.success} - {result.message}")
    
    result = check_vpn_ip()
    print(f"  check_vpn_ip(): {result.success} - {result.message}")

    print("\nNetwork convenience functions:")
    result = get_network_interfaces()
    print(f"  get_network_interfaces(): {result.success} - {result.message}")
    
    result = spoof_mac_address("eth0")
    print(f"  spoof_mac_address(): {result.success} - {result.message}")
    
    result = restore_mac_address("eth0")
    print(f"  restore_mac_address(): {result.success} - {result.message}")
    
    result = randomize_mac_addresses()
    print(f"  randomize_mac_addresses(): {result.success} - {result.message}")
    
    mac = generate_random_mac()
    print(f"  generate_random_mac(): {mac}")

    print("\nObfuscation convenience functions:")
    profile = generate_fingerprint_profile(FingerprintType.BROWSER)
    print(f"  generate_fingerprint_profile(): {profile.profile_id}")
    
    result = obfuscate_request("http://example.com")
    print(f"  obfuscate_request(): {result.success} - {result.message}")
    
    result = randomize_traffic_pattern(requests_data)
    print(f"  randomize_traffic_pattern(): {result.success} - {result.message}")
    
    result = generate_tls_fingerprint()
    print(f"  generate_tls_fingerprint(): {result.success} - {result.message}")

    print("\n--- Shadow Anonymity Library Demo Complete ---")

if __name__ == "__main__":
    run_shadow_demo()
