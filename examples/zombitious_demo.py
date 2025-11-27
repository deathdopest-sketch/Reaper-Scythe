#!/usr/bin/env python3
"""
Zombitious Digital Identity Library Demo

This script demonstrates the Zombitious library's capabilities for
creating, managing, educating about, and removing digital identities.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.zombitious import (
    create_identity, generate_persona, IdentityType, IdentityStatus,
    learn_identity_basics, learn_identity_creation, learn_identity_removal,
    explain_digital_footprint, explain_opsec,
    remove_identity, burn_identity, delete_accounts,
    IdentityManager
)


def demo_identity_creation():
    """Demonstrate identity creation."""
    print("\n" + "="*60)
    print("IDENTITY CREATION DEMO")
    print("="*60)
    
    print("\n1. Creating a basic anonymous identity:")
    identity = create_identity(IdentityType.ANONYMOUS)
    
    print(f"\n   Identity ID: {identity.identity_id}")
    print(f"   Name: {identity.full_name}")
    print(f"   Email: {identity.email}")
    print(f"   Phone: {identity.phone}")
    print(f"   Age: {identity.age}")
    print(f"   Location: {identity.city}, {identity.state}")
    
    print("\n2. Generating complete persona with social accounts:")
    persona = generate_persona(IdentityType.OPERATIONAL)
    
    print(f"\n   Identity: {persona.full_name}")
    print(f"   Email: {persona.email}")
    print(f"   Social Accounts: {len(persona.social_media_accounts)}")
    for platform, url in list(persona.social_media_accounts.items())[:3]:
        print(f"     - {platform}: {url}")


def demo_education():
    """Demonstrate educational content."""
    print("\n" + "="*60)
    print("EDUCATION MODULE DEMO")
    print("="*60)
    
    print("\n1. Digital Identity Basics:")
    basics = learn_identity_basics()
    for i, line in enumerate(basics["content"][:8], 1):
        print(f"   {line}")
    print("   ... (truncated)")
    
    print("\n2. Creating Identities:")
    creation = learn_identity_creation()
    print(f"   Title: {creation['title']}")
    print(f"   Key principles explained: {len(creation['content'])} items")
    
    print("\n3. Making Identities Disappear:")
    removal = learn_identity_removal()
    print(f"   Title: {removal['title']}")
    print(f"   Strategies covered: {len([c for c in removal['content'] if c.startswith('1.')])}")
    
    print("\n4. Digital Footprint Explanation:")
    footprint_explanation = explain_digital_footprint()
    print(footprint_explanation[:200] + "...")
    
    print("\n5. OpSec Explanation:")
    opsec_explanation = explain_opsec()
    print(opsec_explanation[:200] + "...")


def demo_identity_removal():
    """Demonstrate identity removal."""
    print("\n" + "="*60)
    print("IDENTITY REMOVAL DEMO")
    print("="*60)
    
    print("\n1. Creating identity for removal demo:")
    identity = create_identity(IdentityType.DECOY)
    print(f"   Created: {identity.full_name} ({identity.email})")
    
    print("\n2. Removing identity (safe mode - simulation):")
    removal_result = remove_identity(identity, safe_mode=True)
    
    print(f"   Strategy: {removal_result['strategy']}")
    print(f"   Tasks created: {len(removal_result['tasks_created'])}")
    print(f"   Success rate: {removal_result['success_rate']:.1f}%")
    
    print("\n3. Burning identity completely:")
    burn_result = burn_identity(identity, verify=True, safe_mode=True)
    
    print(f"   Status: {burn_result['status']}")
    print(f"   Verified: {burn_result.get('verified', {}).get('overall_status', 'unknown')}")


def demo_identity_management():
    """Demonstrate identity management."""
    print("\n" + "="*60)
    print("IDENTITY MANAGEMENT DEMO")
    print("="*60)
    
    print("\n1. Creating and registering identity:")
    identity = create_identity(IdentityType.OPERATIONAL)
    manager = IdentityManager()
    profile = manager.register_identity(identity)
    
    print(f"   Registered: {identity.identity_id}")
    print(f"   Health status: {profile.health_status}")
    
    print("\n2. Tracking usage:")
    manager.track_usage(identity.identity_id, "login", "facebook")
    manager.track_usage(identity.identity_id, "post", "twitter")
    manager.track_usage(identity.identity_id, "message", "linkedin")
    
    print(f"   Usage count: {identity.usage_count}")
    print(f"   Last used: {identity.last_used}")
    
    print("\n3. Performing maintenance:")
    maintenance = manager.maintain_identity(identity.identity_id)
    
    print(f"   Maintenance date: {maintenance['date']}")
    print(f"   Tasks: {maintenance['tasks_performed']}")
    
    print("\n4. Auditing identity:")
    audit = manager.audit_identity(identity.identity_id)
    
    print(f"   Status: {audit['status']}")
    print(f"   Usage count: {audit['usage_count']}")
    print(f"   Accounts: {audit['accounts_count']}")
    print(f"   Risk factors: {len(audit['risk_factors'])}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("ZOMBITIOUS DIGITAL IDENTITY LIBRARY DEMONSTRATION")
    print("="*60)
    print("\nThis demo showcases the Zombitious library's capabilities:")
    print("  - Digital identity creation and generation")
    print("  - Educational content on identity management")
    print("  - Identity removal and deletion")
    print("  - Identity management and maintenance")
    print("\nNote: All operations run in SAFE MODE (simulation)")
    print("      No actual accounts are created or deleted")
    
    try:
        demo_identity_creation()
        demo_education()
        demo_identity_removal()
        demo_identity_management()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nKey Features Demonstrated:")
        print("  [OK] Identity creation with realistic personas")
        print("  [OK] Educational content on digital identities")
        print("  [OK] Identity removal strategies")
        print("  [OK] Identity management and tracking")
        print("\nThe Zombitious library provides comprehensive tools")
        print("for understanding, creating, and managing digital identities.")
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

