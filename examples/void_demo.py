#!/usr/bin/env python3
"""
Void OSINT Scrubbing Library Demo

This script demonstrates the Void library's capabilities for
removing digital footprints and scrubbing OSINT data.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.void import (
    VoidOSINTScrubber, ScrubType, ScrubPriority,
    analyze_digital_footprint, scrub_email, scrub_phone, scrub_username,
    check_username_availability, find_exposed_emails,
    request_google_removal, request_data_broker_removal
)


def demo_email_scrubbing():
    """Demonstrate email scrubbing."""
    print("\n" + "="*60)
    print("EMAIL SCRUBBING DEMO")
    print("="*60)
    
    test_email = "example@email.com"
    
    print(f"\n1. Scrubbing email: {test_email}")
    print("   (Safe mode - read-only checks)")
    
    result = scrub_email(test_email, safe_mode=True)
    
    print(f"\n   Status: {result.status.value}")
    print(f"   Platforms checked: {len(result.platforms_checked)}")
    print(f"   Items found: {result.items_found}")
    print(f"   Items removed: {result.items_removed}")
    print(f"   Success rate: {result.success_rate():.1f}%")
    
    if result.platforms_checked:
        print(f"\n   Platforms checked:")
        for platform in result.platforms_checked[:5]:
            print(f"     - {platform}")


def demo_phone_scrubbing():
    """Demonstrate phone number scrubbing."""
    print("\n" + "="*60)
    print("PHONE NUMBER SCRUBBING DEMO")
    print("="*60)
    
    test_phone = "+1-555-123-4567"
    
    print(f"\n1. Scrubbing phone: {test_phone}")
    
    result = scrub_phone(test_phone, safe_mode=True)
    
    print(f"\n   Status: {result.status.value}")
    print(f"   Platforms checked: {len(result.platforms_checked)}")
    print(f"   Items found: {result.items_found}")
    
    if result.error_message:
        print(f"   Error: {result.error_message}")


def demo_username_checking():
    """Demonstrate username checking."""
    print("\n" + "="*60)
    print("USERNAME AVAILABILITY CHECK DEMO")
    print("="*60)
    
    test_username = "testuser123"
    
    print(f"\n1. Checking username: {test_username}")
    print("   (Checking across social media platforms)")
    
    availability = check_username_availability(test_username)
    
    print(f"\n   Platforms checked: {len(availability)}")
    print(f"\n   Availability status:")
    for platform, is_taken in list(availability.items())[:5]:
        status = "TAKEN" if is_taken else "AVAILABLE"
        print(f"     - {platform}: {status}")


def demo_footprint_analysis():
    """Demonstrate digital footprint analysis."""
    print("\n" + "="*60)
    print("DIGITAL FOOTPRINT ANALYSIS DEMO")
    print("="*60)
    
    print("\n1. Analyzing footprint for sample data:")
    print("   Email: user@example.com")
    print("   Username: testuser")
    print("   Phone: +1-555-123-4567")
    
    report = analyze_digital_footprint(
        email="user@example.com",
        username="testuser",
        phone="+1-555-123-4567"
    )
    
    print(f"\n   Analysis Results:")
    print(f"     - Total records found: {report.get('total_records', 0)}")
    print(f"     - Records by type: {report.get('by_type', {})}")
    print(f"     - Critical records: {report.get('critical_count', 0)}")
    print(f"     - Removable records: {report.get('removable_count', 0)}")


def demo_removal_requests():
    """Demonstrate removal request functionality."""
    print("\n" + "="*60)
    print("REMOVAL REQUEST DEMO")
    print("="*60)
    
    print("\n1. Requesting Google search result removal")
    
    try:
        google_request = request_google_removal("https://example.com/remove-this")
        print(f"\n   Request ID: {google_request.request_id}")
        print(f"   Status: {google_request.status.value}")
        print(f"   Provider: {google_request.provider.value}")
        print(f"   Submitted: {google_request.submitted_date}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Requesting data broker removal")
    
    try:
        broker_request = request_data_broker_removal(
            "whitepages",
            "user@example.com",
            "email"
        )
        print(f"\n   Request ID: {broker_request.request_id}")
        print(f"   Status: {broker_request.status.value}")
        print(f"   Provider: {broker_request.provider.value}")
    except Exception as e:
        print(f"   Error: {e}")


def demo_comprehensive_scrubber():
    """Demonstrate comprehensive scrubber."""
    print("\n" + "="*60)
    print("COMPREHENSIVE SCRUBBER DEMO")
    print("="*60)
    
    scrubber = VoidOSINTScrubber(safe_mode=True)
    
    print("\n1. Creating scrubber instance")
    print(f"   Safe mode: {scrubber.safe_mode}")
    print(f"   Data brokers tracked: {len(scrubber.data_brokers)}")
    print(f"   Social platforms tracked: {len(scrubber.social_platforms)}")
    
    print("\n2. Scanning social media")
    social_results = scrubber.scan_social_media(
        email="user@example.com",
        username="testuser"
    )
    
    print(f"\n   Results: {len(social_results)} platforms checked")
    for platform, exists in list(social_results.items())[:5]:
        status = "FOUND" if exists else "NOT FOUND"
        print(f"     - {platform}: {status}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("VOID OSINT SCRUBBING LIBRARY DEMONSTRATION")
    print("="*60)
    print("\nThis demo showcases the Void library's capabilities for:")
    print("  - Email and phone number scrubbing")
    print("  - Username checking across platforms")
    print("  - Digital footprint analysis")
    print("  - Removal request management")
    print("\nNote: All operations run in SAFE MODE (read-only)")
    print("      No actual deletions or modifications are performed")
    
    try:
        demo_email_scrubbing()
        demo_phone_scrubbing()
        demo_username_checking()
        demo_footprint_analysis()
        demo_removal_requests()
        demo_comprehensive_scrubber()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nKey Features Demonstrated:")
        print("  [OK] Email scrubbing from data brokers")
        print("  [OK] Phone number removal requests")
        print("  [OK] Username availability checking")
        print("  [OK] Digital footprint analysis")
        print("  [OK] Removal request tracking")
        print("\nThe Void library provides comprehensive OSINT scrubbing")
        print("capabilities for privacy protection and footprint removal.")
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

