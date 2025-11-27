"""
Digital Identity Creation and Management Module

Provides tools for creating, managing, and maintaining digital identities.
Includes educational content on how digital identities work.
"""

import random
import string
import re
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


class IdentityType(Enum):
    """Types of digital identities."""
    PERSONAL = "personal"
    CORPORATE = "corporate"
    ANONYMOUS = "anonymous"
    OPERATIONAL = "operational"
    DECOY = "decoy"


class IdentityStatus(Enum):
    """Status of a digital identity."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BURNED = "burned"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"


@dataclass
class DigitalIdentity:
    """Represents a complete digital identity."""
    identity_id: str
    identity_type: IdentityType
    status: IdentityStatus
    
    # Personal information
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    
    # Contact information
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Online presence
    usernames: List[str] = field(default_factory=list)
    social_media_accounts: Dict[str, str] = field(default_factory=dict)
    website_urls: List[str] = field(default_factory=list)
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    notes: str = ""
    
    # Security
    password_hint: Optional[str] = None
    recovery_email: Optional[str] = None
    two_factor_enabled: bool = False


class IdentityGenerator:
    """
    Generator for creating realistic digital identities.
    
    Provides educational insights into identity construction and
    helps create believable personas for security operations.
    """
    
    def __init__(self):
        """Initialize identity generator."""
        self.first_names = [
            "Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Avery",
            "Cameron", "Quinn", "Dakota", "Emery", "Finley", "Hayden", "Jamie"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson"
        ]
        
        self.domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
            "protonmail.com", "mail.com", "icloud.com"
        ]
        
        self.social_platforms = [
            "facebook", "twitter", "instagram", "linkedin", "github",
            "reddit", "pinterest", "tiktok", "snapchat"
        ]
    
    def generate_persona(self, identity_type: IdentityType = IdentityType.ANONYMOUS) -> DigitalIdentity:
        """
        Generate a complete digital persona.
        
        Args:
            identity_type: Type of identity to generate
            
        Returns:
            Complete DigitalIdentity object
        """
        # Generate name
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        full_name = f"{first_name} {last_name}"
        
        # Generate email
        email_username = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}"
        email = f"{email_username}@{random.choice(self.domains)}"
        
        # Generate phone (US format)
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        phone = f"{area_code}-{exchange}-{number}"
        
        # Generate username
        username = f"{first_name.lower()}{random.randint(10, 99)}"
        
        # Generate age and DOB
        age = random.randint(18, 65)
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        dob = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
        
        # Generate address components
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Miami"]
        states = ["NY", "CA", "IL", "TX", "AZ", "FL"]
        countries = ["USA"]
        
        city = random.choice(cities)
        state = random.choice(states)
        country = random.choice(countries)
        zip_code = f"{random.randint(10000, 99999)}"
        
        # Create identity
        identity = DigitalIdentity(
            identity_id=f"id_{random.randint(10000, 99999)}",
            identity_type=identity_type,
            status=IdentityStatus.ACTIVE,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            date_of_birth=dob,
            age=age,
            email=email,
            phone=phone,
            city=city,
            state=state,
            country=country,
            zip_code=zip_code,
            usernames=[username],
            notes=f"Generated {identity_type.value} identity"
        )
        
        return identity
    
    def create_social_accounts(self, identity: DigitalIdentity, 
                              platforms: Optional[List[str]] = None) -> DigitalIdentity:
        """
        Create social media accounts for identity.
        
        Args:
            identity: Identity to add accounts to
            platforms: List of platforms, or None for all
            
        Returns:
            Updated identity with social accounts
        """
        if platforms is None:
            platforms = self.social_platforms
        
        for platform in platforms:
            if identity.usernames:
                username = identity.usernames[0]
            else:
                username = f"{identity.first_name.lower()}{random.randint(10, 99)}"
            
            identity.social_media_accounts[platform] = f"https://{platform}.com/{username}"
        
        return identity
    
    def explain_identity_construction(self) -> Dict[str, Any]:
        """
        Educational content explaining how digital identities are constructed.
        
        Returns:
            Dictionary with educational information
        """
        return {
            "title": "How Digital Identities Work",
            "sections": [
                {
                    "section": "Components of a Digital Identity",
                    "content": [
                        "A digital identity consists of multiple interconnected components:",
                        "1. Personal Information: Name, DOB, address, phone",
                        "2. Email Addresses: Primary and recovery emails",
                        "3. Usernames: Unique identifiers across platforms",
                        "4. Social Media Profiles: Facebook, Twitter, LinkedIn, etc.",
                        "5. Digital Traces: Browser history, cookies, metadata",
                        "6. Behavioral Patterns: Typing patterns, browsing habits"
                    ]
                },
                {
                    "section": "Identity Verification Methods",
                    "content": [
                        "Platforms verify identities through:",
                        "- Email verification",
                        "- Phone number verification (SMS)",
                        "- Social graph verification (connections)",
                        "- Behavioral analysis",
                        "- Device fingerprinting",
                        "- Knowledge-based authentication (security questions)"
                    ]
                },
                {
                    "section": "Creating Believable Identities",
                    "content": [
                        "Key principles for realistic identities:",
                        "1. Consistency: All information should be internally consistent",
                        "2. Timeline: Create realistic history and activity",
                        "3. Plausibility: Information should be believable",
                        "4. Verification: Use methods that platforms expect",
                        "5. Maintenance: Keep identities active and realistic",
                        "6. OpSec: Maintain separation from real identity"
                    ]
                },
                {
                    "section": "Identity Security",
                    "content": [
                        "Protect identities through:",
                        "- Strong, unique passwords",
                        "- Two-factor authentication",
                        "- Secure recovery methods",
                        "- Regular password rotation",
                        "- Minimal cross-platform linking",
                        "- Clean browser profiles"
                    ]
                }
            ]
        }


# Convenience functions
def create_identity(identity_type: IdentityType = IdentityType.ANONYMOUS) -> DigitalIdentity:
    """Create a new digital identity."""
    generator = IdentityGenerator()
    return generator.generate_persona(identity_type)


def generate_persona(identity_type: IdentityType = IdentityType.ANONYMOUS) -> DigitalIdentity:
    """Generate a complete persona with all details."""
    generator = IdentityGenerator()
    identity = generator.generate_persona(identity_type)
    return generator.create_social_accounts(identity)


def create_email_identity(email_domain: Optional[str] = None) -> DigitalIdentity:
    """Create identity focused on email accounts."""
    generator = IdentityGenerator()
    identity = generator.generate_persona(IdentityType.ANONYMOUS)
    
    if email_domain:
        # Use custom domain
        username = f"{identity.first_name.lower()}.{identity.last_name.lower()}"
        identity.email = f"{username}@{email_domain}"
    
    return identity


def create_social_identity(platforms: List[str]) -> DigitalIdentity:
    """Create identity with social media accounts."""
    generator = IdentityGenerator()
    identity = generator.generate_persona(IdentityType.ANONYMOUS)
    return generator.create_social_accounts(identity, platforms)


def create_phone_identity(phone_prefix: Optional[str] = None) -> DigitalIdentity:
    """Create identity focused on phone verification."""
    generator = IdentityGenerator()
    identity = generator.generate_persona(IdentityType.ANONYMOUS)
    
    if phone_prefix:
        # Use custom prefix
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        identity.phone = f"{phone_prefix}-{exchange}-{number}"
    
    return identity


def manage_identity(identity: DigitalIdentity) -> DigitalIdentity:
    """Manage and maintain an identity."""
    identity.last_used = datetime.now()
    identity.usage_count += 1
    return identity

