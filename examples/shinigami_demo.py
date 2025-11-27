#!/usr/bin/env python3
"""
Shinigami Library Demo

Demonstrates identity creation for Australia and America,
and identity disappearance/erasure capabilities.

WARNING: This is for educational purposes only.
Creating false identities or using false documents is illegal.
Always consult with legal professionals.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.shinigami.creation import create_australian_identity, create_american_identity
from libs.shinigami.disappearance import disappear_identity, ErasureStrategy
from libs.shinigami.legal import generate_legal_disclaimer, get_australian_legal_info
from libs.shinigami.geographic import get_australian_regions, get_american_states


def print_separator():
    """Print visual separator."""
    print("\n" + "=" * 60 + "\n")


def demo_australian_identity():
    """Demonstrate Australian identity creation."""
    print("AUSTRALIAN IDENTITY CREATION")
    print_separator()
    
    # Create basic identity
    print("Creating Australian identity in Victoria...")
    aus_identity = create_australian_identity(
        state="Victoria",
        age_range=(25, 35),
        include_documents=True
    )
    
    print(f"\nName: {aus_identity.first_name} {aus_identity.last_name}")
    print(f"Age: {aus_identity.age}")
    print(f"Date of Birth: {aus_identity.date_of_birth}")
    print(f"Address: {aus_identity.street_address}")
    print(f"         {aus_identity.city}, {aus_identity.state} {aus_identity.postcode}")
    print(f"Phone: {aus_identity.phone}")
    if aus_identity.email:
        print(f"Email: {aus_identity.email}")
    if aus_identity.tax_id:
        print(f"Tax ID: {aus_identity.tax_id}")
    if aus_identity.driver_license:
        print(f"Driver License: {aus_identity.driver_license}")
    
    print_separator()


def demo_american_identity():
    """Demonstrate American identity creation."""
    print("AMERICAN IDENTITY CREATION")
    print_separator()
    
    # Create identity in California
    print("Creating American identity in California...")
    usa_identity = create_american_identity(
        state="California",
        age_range=(28, 40),
        include_documents=True
    )
    
    print(f"\nName: {usa_identity.first_name} {usa_identity.last_name}")
    print(f"Age: {usa_identity.age}")
    print(f"Date of Birth: {usa_identity.date_of_birth}")
    print(f"Address: {usa_identity.street_address}")
    print(f"         {usa_identity.city}, {usa_identity.state} {usa_identity.postcode}")
    print(f"Phone: {usa_identity.phone}")
    if usa_identity.email:
        print(f"Email: {usa_identity.email}")
    if usa_identity.ssn:
        print(f"SSN: {usa_identity.ssn}")
    if usa_identity.driver_license:
        print(f"Driver License: {usa_identity.driver_license}")
    
    print_separator()


def demo_disappearance():
    """Demonstrate identity disappearance planning."""
    print("IDENTITY DISAPPEARANCE PLANNING")
    print_separator()
    
    # Create sample identity data
    identity_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "accounts": ["social_media", "email", "banking", "shopping"],
        "data_brokers": True,
        "physical_documents": True
    }
    
    print("Creating disappearance plan (COMPLETE strategy)...")
    plan = disappear_identity(identity_data, ErasureStrategy.COMPLETE)
    
    print(f"\nStrategy: {plan['strategy']}")
    print(f"Timeline: {plan['timeline_days']} days")
    print(f"Risk Level: {plan['risk_level']}")
    print(f"\nTasks ({len(plan['tasks'])} total):")
    for i, task in enumerate(plan['tasks'], 1):
        print(f"\n{i}. {task['method'].upper()}")
        print(f"   Description: {task['description']}")
        print(f"   Priority: {task['priority']}/5")
        print(f"   Estimated Time: {task['estimated_time']}")
        if task['legal_considerations']:
            print(f"   Legal Considerations:")
            for consideration in task['legal_considerations']:
                print(f"     - {consideration}")
    
    print("\n\nRecommendations:")
    for rec in plan['recommendations']:
        print(f"  - {rec}")
    
    print_separator()


def demo_legal_info():
    """Demonstrate legal information."""
    print("LEGAL INFORMATION")
    print_separator()
    
    aus_info = get_australian_legal_info("identity")
    print("AUSTRALIA - Identity Laws:")
    print(f"Legal Status: {aus_info.legal_status}")
    print("\nRequirements:")
    for req in aus_info.requirements:
        print(f"  - {req}")
    print("\nRestrictions:")
    for res in aus_info.restrictions:
        print(f"  - {res}")
    
    print_separator()
    
    disclaimer = generate_legal_disclaimer("shinigami")
    print("LEGAL DISCLAIMER:")
    print(disclaimer)
    
    print_separator()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("SHINIGAMI LIBRARY DEMONSTRATION")
    print("=" * 60)
    print("\nWARNING: For educational purposes only.")
    print("Creating false identities or documents is ILLEGAL.")
    print("Always consult with legal professionals.\n")
    
    try:
        demo_australian_identity()
        demo_american_identity()
        demo_disappearance()
        demo_legal_info()
        
        print("\n✅ Demo completed successfully!")
        print("\nRemember: This library is for educational purposes only.")
        print("All identity operations must comply with applicable laws.")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

