"""
Geographic Identity Data for Australia and America

Provides country-specific data, generators, and validators for creating
realistic identities in Australia and the United States.
"""

import random
import string
from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


class Country(Enum):
    """Supported countries for identity creation."""
    AUSTRALIA = "australia"
    AMERICA = "america"  # United States
    USA = "usa"  # Alias for AMERICA


@dataclass
class GeographicIdentity:
    """Base geographic identity information."""
    country: Country
    region: str
    city: str
    address: str
    postcode: str
    phone: str
    tax_id: str
    timezone: str
    currency: str


# Australian Data
AUSTRALIAN_STATES = [
    "New South Wales", "Victoria", "Queensland", "Western Australia",
    "South Australia", "Tasmania", "Australian Capital Territory", "Northern Territory"
]

AUSTRALIAN_CITIES = {
    "New South Wales": ["Sydney", "Newcastle", "Wollongong", "Albury", "Wagga Wagga"],
    "Victoria": ["Melbourne", "Geelong", "Ballarat", "Bendigo", "Latrobe"],
    "Queensland": ["Brisbane", "Gold Coast", "Cairns", "Townsville", "Toowoomba"],
    "Western Australia": ["Perth", "Fremantle", "Bunbury", "Geraldton", "Kalgoorlie"],
    "South Australia": ["Adelaide", "Mount Gambier", "Whyalla", "Murray Bridge"],
    "Tasmania": ["Hobart", "Launceston", "Devonport", "Burnie"],
    "Australian Capital Territory": ["Canberra"],
    "Northern Territory": ["Darwin", "Alice Springs", "Palmerston"]
}

AUSTRALIAN_STREET_SUFFIXES = [
    "Street", "Road", "Avenue", "Drive", "Lane", "Court", "Place",
    "Close", "Crescent", "Way", "Terrace", "Grove", "Circuit"
]

AUSTRALIAN_FIRST_NAMES = [
    "Charlotte", "Oliver", "Olivia", "Noah", "Amelia", "Jack", "Isla", "Thomas",
    "Mia", "Lucas", "Ava", "Leo", "Chloe", "Ethan", "Grace", "Henry",
    "Ruby", "Alexander", "Willow", "Mason", "Sophia", "Harrison", "Isabella", "James",
    "Emily", "William", "Zoe", "Benjamin", "Lily", "Hunter", "Matilda", "Oscar",
    "Ella", "Ethan", "Harper", "Max", "Sienna", "Samuel", "Aria", "Logan"
]

AUSTRALIAN_LAST_NAMES = [
    "Smith", "Jones", "Williams", "Brown", "Wilson", "Taylor", "Moore", "Anderson",
    "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
    "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young",
    "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green"
]


# American Data
AMERICAN_STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}

AMERICAN_CITIES = {
    "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"],
    "New York": ["New York City", "Buffalo", "Rochester", "Albany", "Syracuse"],
    "Texas": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"],
    "Florida": ["Miami", "Tampa", "Orlando", "Jacksonville", "Tallahassee"],
    "Illinois": ["Chicago", "Aurora", "Rockford", "Joliet", "Naperville"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron"],
    "Michigan": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Lansing"],
    "Georgia": ["Atlanta", "Augusta", "Columbus", "Savannah", "Athens"],
    "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem"]
}

AMERICAN_STREET_SUFFIXES = [
    "Street", "Avenue", "Road", "Drive", "Lane", "Court", "Place",
    "Boulevard", "Parkway", "Circle", "Way", "Terrace", "Highway"
]

AMERICAN_FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "Michael", "Jennifer", "William", "Linda",
    "David", "Elizabeth", "Richard", "Barbara", "Joseph", "Susan", "Thomas", "Jessica",
    "Christopher", "Sarah", "Charles", "Karen", "Daniel", "Nancy", "Matthew", "Lisa",
    "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley"
]

AMERICAN_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor",
    "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris", "Sanchez",
    "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King"
]


class AustralianIdentityBuilder:
    """Builder for creating Australian identities."""
    
    @staticmethod
    def get_regions() -> List[str]:
        """Get list of Australian states/territories."""
        return AUSTRALIAN_STATES.copy()
    
    @staticmethod
    def generate_address(state: Optional[str] = None) -> Tuple[str, str, str, str]:
        """
        Generate a realistic Australian address.
        
        Returns: (street_address, city, state, postcode)
        """
        if state is None:
            state = random.choice(AUSTRALIAN_STATES)
        
        city = random.choice(AUSTRALIAN_CITIES.get(state, ["Unknown"]))
        street_number = random.randint(1, 9999)
        street_name = random.choice(AUSTRALIAN_FIRST_NAMES + AUSTRALIAN_LAST_NAMES)
        suffix = random.choice(AUSTRALIAN_STREET_SUFFIXES)
        
        street_address = f"{street_number} {street_name} {suffix}"
        
        # Generate postcode based on state
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
        
        min_post, max_post = postcode_ranges.get(state, (2000, 2999))
        postcode = str(random.randint(min_post, max_post))
        
        return (street_address, city, state, postcode)
    
    @staticmethod
    def generate_phone() -> str:
        """Generate realistic Australian phone number."""
        # Australian format: 04XX XXX XXX (mobile) or (0X) XXXX XXXX (landline)
        if random.random() < 0.7:  # 70% mobile
            area = random.randint(100, 999)
            number = random.randint(100000, 999999)
            return f"04{area} {number // 1000} {number % 1000}"
        else:  # Landline
            area_code = random.choice([2, 3, 7, 8])  # Common area codes
            exchange = random.randint(1000, 9999)
            subscriber = random.randint(1000, 9999)
            return f"0{area_code} {exchange} {subscriber}"
    
    @staticmethod
    def generate_tax_id() -> str:
        """Generate Australian Tax File Number format (9 digits)."""
        # Format: XXX XXX XXX
        return f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
    
    @staticmethod
    def generate_name() -> Tuple[str, str]:
        """Generate realistic Australian name."""
        return (
            random.choice(AUSTRALIAN_FIRST_NAMES),
            random.choice(AUSTRALIAN_LAST_NAMES)
        )


class AmericanIdentityBuilder:
    """Builder for creating American identities."""
    
    @staticmethod
    def get_states() -> Dict[str, str]:
        """Get dictionary of US states and abbreviations."""
        return AMERICAN_STATES.copy()
    
    @staticmethod
    def generate_address(state: Optional[str] = None) -> Tuple[str, str, str, str]:
        """
        Generate a realistic American address.
        
        Returns: (street_address, city, state, zip_code)
        """
        if state is None:
            state = random.choice(list(AMERICAN_STATES.keys()))
        
        state_abbr = AMERICAN_STATES.get(state, "CA")
        city = random.choice(AMERICAN_CITIES.get(state, ["Unknown"]))
        
        street_number = random.randint(1, 9999)
        street_name = random.choice(AMERICAN_FIRST_NAMES + AMERICAN_LAST_NAMES)
        suffix = random.choice(AMERICAN_STREET_SUFFIXES)
        
        street_address = f"{street_number} {street_name} {suffix}"
        
        # Generate ZIP code (5 digits)
        zip_code = f"{random.randint(10000, 99999)}"
        
        return (street_address, city, state, zip_code)
    
    @staticmethod
    def generate_phone(state: Optional[str] = None) -> str:
        """Generate realistic American phone number."""
        # Format: (XXX) XXX-XXXX
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        subscriber = random.randint(1000, 9999)
        return f"({area_code}) {exchange}-{subscriber}"
    
    @staticmethod
    def generate_ssn() -> str:
        """Generate Social Security Number format (XXX-XX-XXXX)."""
        # Format: XXX-XX-XXXX
        # Note: This is educational only - real SSNs have specific rules
        area = random.randint(100, 999)
        group = random.randint(1, 99)
        serial = random.randint(1000, 9999)
        return f"{area:03d}-{group:02d}-{serial:04d}"
    
    @staticmethod
    def generate_name() -> Tuple[str, str]:
        """Generate realistic American name."""
        return (
            random.choice(AMERICAN_FIRST_NAMES),
            random.choice(AMERICAN_LAST_NAMES)
        )


# Convenience functions
def get_australian_regions() -> List[str]:
    """Get list of Australian states/territories."""
    return AustralianIdentityBuilder.get_regions()


def get_american_states() -> Dict[str, str]:
    """Get dictionary of US states and abbreviations."""
    return AmericanIdentityBuilder.get_states()


def generate_australian_address(state: Optional[str] = None) -> Tuple[str, str, str, str]:
    """Generate realistic Australian address."""
    return AustralianIdentityBuilder.generate_address(state)


def generate_american_address(state: Optional[str] = None) -> Tuple[str, str, str, str]:
    """Generate realistic American address."""
    return AmericanIdentityBuilder.generate_address(state)


def generate_australian_phone() -> str:
    """Generate realistic Australian phone number."""
    return AustralianIdentityBuilder.generate_phone()


def generate_american_phone(state: Optional[str] = None) -> str:
    """Generate realistic American phone number."""
    return AmericanIdentityBuilder.generate_phone(state)


def generate_australian_tax_id() -> str:
    """Generate Australian Tax File Number."""
    return AustralianIdentityBuilder.generate_tax_id()


def generate_american_ssn() -> str:
    """Generate American Social Security Number format."""
    return AmericanIdentityBuilder.generate_ssn()


def get_australian_locations() -> Dict[str, List[str]]:
    """Get dictionary of Australian states and their cities."""
    return AUSTRALIAN_CITIES.copy()


def get_american_locations() -> Dict[str, List[str]]:
    """Get dictionary of American states and their cities."""
    return AMERICAN_CITIES.copy()

