"""
Identity Creation Module for Australia and America

Provides tools for creating new identities with proper geographic
and cultural context for Australia and the United States.
"""

import random
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from .geographic import (
    Country, AustralianIdentityBuilder, AmericanIdentityBuilder,
    generate_australian_address, generate_american_address,
    generate_australian_phone, generate_american_phone,
    generate_australian_tax_id, generate_american_ssn
)


class IdentityType(Enum):
    """Types of identities that can be created."""
    COMPLETE = "complete"  # Full identity with all documents
    BASIC = "basic"  # Basic identity info only
    DOCUMENT_ONLY = "document_only"  # Just documents
    BACKSTORY = "backstory"  # Identity with detailed history


@dataclass
class CountryIdentity:
    """Represents a complete geographic identity."""
    country: Country
    first_name: str
    last_name: str
    date_of_birth: str
    age: int
    
    # Address
    street_address: str
    city: str
    state: str
    postcode: str
    
    # Contact
    phone: str
    email: Optional[str] = None
    
    # Identification
    tax_id: Optional[str] = None
    ssn: Optional[str] = None
    driver_license: Optional[str] = None
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    backstory: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert identity to dictionary."""
        return {
            "country": self.country.value,
            "name": f"{self.first_name} {self.last_name}",
            "date_of_birth": self.date_of_birth,
            "age": self.age,
            "address": {
                "street": self.street_address,
                "city": self.city,
                "state": self.state,
                "postcode": self.postcode
            },
            "contact": {
                "phone": self.phone,
                "email": self.email
            },
            "identification": {
                "tax_id": self.tax_id,
                "ssn": self.ssn,
                "driver_license": self.driver_license
            },
            "backstory": self.backstory,
            "created": self.created_date.isoformat()
        }


class IdentityCreator:
    """
    Creator for new geographic identities in Australia and America.
    
    Provides tools to create realistic identities with proper
    cultural and geographic context.
    """
    
    def __init__(self):
        """Initialize identity creator."""
        self.aus_builder = AustralianIdentityBuilder()
        self.usa_builder = AmericanIdentityBuilder()
    
    def create_australian_identity(
        self,
        state: Optional[str] = None,
        age_range: Optional[tuple] = None,
        include_email: bool = True,
        include_documents: bool = True
    ) -> CountryIdentity:
        """
        Create a complete Australian identity.
        
        Args:
            state: Specific Australian state (optional)
            age_range: Tuple of (min_age, max_age) for generated age
            include_email: Whether to generate email address
            include_documents: Whether to generate tax ID and documents
        """
        # Generate name
        first_name, last_name = self.aus_builder.generate_name()
        
        # Generate age and DOB
        if age_range is None:
            age_range = (18, 75)
        age = random.randint(age_range[0], age_range[1])
        
        # Generate date of birth
        birth_date = datetime.now() - timedelta(days=age * 365 + random.randint(0, 364))
        dob = birth_date.strftime("%d/%m/%Y")  # Australian date format
        
        # Generate address
        street, city, state_name, postcode = generate_australian_address(state)
        
        # Generate contact
        phone = generate_australian_phone()
        email = None
        if include_email:
            email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(['gmail.com', 'yahoo.com.au', 'outlook.com'])}"
        
        # Generate documents
        tax_id = None
        if include_documents:
            tax_id = generate_australian_tax_id()
            # Australian driver license format: State + 8 digits
            license_prefix = state_name[:2].upper() if state_name else "NS"
            driver_license = f"{license_prefix}{random.randint(10000000, 99999999)}"
        else:
            driver_license = None
        
        return CountryIdentity(
            country=Country.AUSTRALIA,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            age=age,
            street_address=street,
            city=city,
            state=state_name,
            postcode=postcode,
            phone=phone,
            email=email,
            tax_id=tax_id,
            driver_license=driver_license
        )
    
    def create_american_identity(
        self,
        state: Optional[str] = None,
        age_range: Optional[tuple] = None,
        include_email: bool = True,
        include_documents: bool = True
    ) -> CountryIdentity:
        """
        Create a complete American identity.
        
        Args:
            state: Specific US state (optional)
            age_range: Tuple of (min_age, max_age) for generated age
            include_email: Whether to generate email address
            include_documents: Whether to generate SSN and documents
        """
        # Generate name
        first_name, last_name = self.usa_builder.generate_name()
        
        # Generate age and DOB
        if age_range is None:
            age_range = (18, 75)
        age = random.randint(age_range[0], age_range[1])
        
        # Generate date of birth (US format)
        birth_date = datetime.now() - timedelta(days=age * 365 + random.randint(0, 364))
        dob = birth_date.strftime("%m/%d/%Y")  # American date format
        
        # Generate address
        street, city, state_name, zip_code = generate_american_address(state)
        
        # Generate contact
        phone = generate_american_phone(state)
        email = None
        if include_email:
            email = f"{first_name.lower()}{random.randint(1,999)}.{last_name.lower()}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com'])}"
        
        # Generate documents
        ssn = None
        if include_documents:
            ssn = generate_american_ssn()
            # US driver license format varies by state, simplified version
            state_abbr = self.usa_builder.get_states().get(state_name, "CA")
            driver_license = f"{state_abbr}{random.randint(1000000, 9999999)}"
        else:
            driver_license = None
        
        return CountryIdentity(
            country=Country.AMERICA,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            age=age,
            street_address=street,
            city=city,
            state=state_name,
            postcode=zip_code,
            phone=phone,
            email=email,
            ssn=ssn,
            driver_license=driver_license
        )


def create_australian_identity(
    state: Optional[str] = None,
    age_range: Optional[tuple] = None,
    include_documents: bool = True
) -> CountryIdentity:
    """Create a complete Australian identity."""
    creator = IdentityCreator()
    return creator.create_australian_identity(
        state=state,
        age_range=age_range,
        include_documents=include_documents
    )


def create_american_identity(
    state: Optional[str] = None,
    age_range: Optional[tuple] = None,
    include_documents: bool = True
) -> CountryIdentity:
    """Create a complete American identity."""
    creator = IdentityCreator()
    return creator.create_american_identity(
        state=state,
        age_range=age_range,
        include_documents=include_documents
    )


def generate_australian_documents(identity: CountryIdentity) -> Dict[str, str]:
    """Generate additional Australian documents for an identity."""
    return {
        "tax_file_number": identity.tax_id or generate_australian_tax_id(),
        "driver_license": identity.driver_license or f"{identity.state[:2].upper()}{random.randint(10000000, 99999999)}",
        "medicare_number": f"{random.randint(1000, 9999)} {random.randint(100000, 999999)} {random.randint(1, 9)}",
        "passport_number": f"N{random.randint(1000000, 9999999)}",
    }


def generate_american_documents(identity: CountryIdentity) -> Dict[str, str]:
    """Generate additional American documents for an identity."""
    state_abbr = AmericanIdentityBuilder.get_states().get(identity.state, "CA")
    return {
        "ssn": identity.ssn or generate_american_ssn(),
        "driver_license": identity.driver_license or f"{state_abbr}{random.randint(1000000, 9999999)}",
        "passport_number": f"{random.randint(100000000, 999999999)}",
    }


def validate_australian_identity(identity: CountryIdentity) -> tuple[bool, List[str]]:
    """Validate an Australian identity for consistency."""
    errors = []
    
    # Check postcode matches state
    postcode_ranges = {
        "New South Wales": (2000, 2999),
        "Victoria": (3000, 3999),
        "Queensland": (4000, 4999),
        "South Australia": (5000, 5999),
        "Western Australia": (6000, 6799),
        "Tasmania": (7000, 7999),
        "Northern Territory": (800, 899),
        "Australian Capital Territory": (200, 299)
    }
    
    try:
        postcode_num = int(identity.postcode)
        min_p, max_p = postcode_ranges.get(identity.state, (2000, 2999))
        if not (min_p <= postcode_num <= max_p):
            errors.append(f"Postcode {identity.postcode} doesn't match state {identity.state}")
    except ValueError:
        errors.append(f"Invalid postcode format: {identity.postcode}")
    
    # Check date format (DD/MM/YYYY)
    try:
        datetime.strptime(identity.date_of_birth, "%d/%m/%Y")
    except ValueError:
        errors.append(f"Invalid date format: {identity.date_of_birth}")
    
    # Check phone format
    if not identity.phone.replace(" ", "").replace("-", "").isdigit():
        errors.append(f"Invalid phone format: {identity.phone}")
    
    return (len(errors) == 0, errors)


def validate_american_identity(identity: CountryIdentity) -> tuple[bool, List[str]]:
    """Validate an American identity for consistency."""
    errors = []
    
    # Check ZIP code format (5 digits)
    if not identity.postcode.isdigit() or len(identity.postcode) != 5:
        errors.append(f"Invalid ZIP code format: {identity.postcode}")
    
    # Check date format (MM/DD/YYYY)
    try:
        datetime.strptime(identity.date_of_birth, "%m/%d/%Y")
    except ValueError:
        errors.append(f"Invalid date format: {identity.date_of_birth}")
    
    # Check phone format
    phone_clean = identity.phone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
    if not phone_clean.isdigit() or len(phone_clean) != 10:
        errors.append(f"Invalid phone format: {identity.phone}")
    
    # Check SSN format if present
    if identity.ssn:
        ssn_parts = identity.ssn.split("-")
        if len(ssn_parts) != 3 or not all(p.isdigit() for p in ssn_parts):
            errors.append(f"Invalid SSN format: {identity.ssn}")
    
    return (len(errors) == 0, errors)


def build_identity_backstory(identity: CountryIdentity, depth: str = "medium") -> Dict[str, Any]:
    """
    Build a detailed backstory for an identity.
    
    Args:
        identity: The identity to build backstory for
        depth: "basic", "medium", or "detailed"
    """
    backstory = {
        "education": {
            "high_school": f"Graduated from {identity.city} High School, {identity.state}",
            "year": (datetime.now().year - identity.age) + random.randint(16, 18)
        },
        "employment": {
            "current_job": random.choice([
                "Retail Associate", "Office Assistant", "Customer Service Representative",
                "Delivery Driver", "Warehouse Worker", "Food Service"
            ]),
            "employer": f"{identity.city} {random.choice(['Services', 'Group', 'Industries'])}"
        },
        "family": {
            "status": random.choice(["Single", "Married", "Divorced", "Widowed"]),
            "children": random.randint(0, 2) if identity.age > 25 else 0
        },
        "interests": random.sample([
            "Reading", "Gaming", "Sports", "Music", "Movies", "Cooking",
            "Travel", "Photography", "Fitness", "Art"
        ], k=random.randint(2, 4))
    }
    
    if depth == "detailed":
        backstory.update({
            "medical": {
                "blood_type": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
                "allergies": random.sample(["None", "Peanuts", "Dust", "Pollen"], k=1)[0]
            },
            "previous_addresses": [],
            "online_presence": {
                "social_media": random.choice(["Minimal", "Active", "Private"]),
                "shopping_history": random.choice(["Rare", "Moderate", "Frequent"])
            }
        })
    
    return backstory


def create_identity_history(identity: CountryIdentity, years: int = 5) -> List[Dict[str, Any]]:
    """Create a historical timeline for an identity."""
    history = []
    current_year = datetime.now().year
    
    for year_offset in range(years, 0, -1):
        year = current_year - year_offset
        history.append({
            "year": year,
            "event": random.choice([
                f"Moved to {identity.city}, {identity.state}",
                f"Started working at {random.choice(['local', 'national'])} company",
                "Completed education",
                "Got driver's license",
                "Opened bank account",
                "Registered to vote"
            ])
        })
    
    return history

