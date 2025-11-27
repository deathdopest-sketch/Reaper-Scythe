# Shinigami Identity Transformation Library
# Creating new identities in Australia and America, disappearing old identities
# Inspired by the death god who guides souls and transforms identities

__version__ = "0.1.0"
__author__ = "Reaper Security Team"

# Core features
from .creation import (
    IdentityCreator, GeographicIdentity, CountryIdentity,
    create_australian_identity, create_american_identity,
    generate_australian_documents, generate_american_documents,
    validate_australian_identity, validate_american_identity,
    build_identity_backstory, create_identity_history
)

from .disappearance import (
    IdentityEraser, ErasureStrategy, ErasureMethod, ErasureStatus,
    disappear_identity, erase_digital_traces, erase_physical_traces,
    burn_old_identity, transform_identity, complete_identity_death,
    verify_erasure, generate_erasure_report, plan_disappearance
)

from .geographic import (
    AustralianIdentityBuilder, AmericanIdentityBuilder,
    get_australian_regions, get_american_states,
    generate_australian_address, generate_american_address,
    generate_australian_phone, generate_american_phone,
    generate_australian_tax_id, generate_american_ssn,
    get_australian_locations, get_american_locations
)

from .legal import (
    LegalFramework, LegalGuidance, LegalRisk,
    get_australian_legal_info, get_american_legal_info,
    assess_legal_risks, get_identity_law_guidance,
    check_legal_compliance, generate_legal_disclaimer
)

__all__ = [
    # Creation
    'IdentityCreator', 'GeographicIdentity', 'CountryIdentity',
    'create_australian_identity', 'create_american_identity',
    'generate_australian_documents', 'generate_american_documents',
    'validate_australian_identity', 'validate_american_identity',
    'build_identity_backstory', 'create_identity_history',
    
    # Disappearance
    'IdentityEraser', 'ErasureStrategy', 'ErasureMethod', 'ErasureStatus',
    'disappear_identity', 'erase_digital_traces', 'erase_physical_traces',
    'burn_old_identity', 'transform_identity', 'complete_identity_death',
    'verify_erasure', 'generate_erasure_report', 'plan_disappearance',
    
    # Geographic
    'AustralianIdentityBuilder', 'AmericanIdentityBuilder',
    'get_australian_regions', 'get_american_states',
    'generate_australian_address', 'generate_american_address',
    'generate_australian_phone', 'generate_american_phone',
    'generate_australian_tax_id', 'generate_american_ssn',
    'get_australian_locations', 'get_american_locations',
    
    # Legal
    'LegalFramework', 'LegalGuidance', 'LegalRisk',
    'get_australian_legal_info', 'get_american_legal_info',
    'assess_legal_risks', 'get_identity_law_guidance',
    'check_legal_compliance', 'generate_legal_disclaimer'
]

