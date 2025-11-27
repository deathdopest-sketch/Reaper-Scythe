# Zombitious Digital Identity Library
# Education, creation, management, and removal of digital identities

__version__ = "0.1.0"
__author__ = "Reaper Security Team"

# Core features
from .identity import (
    DigitalIdentity, IdentityType, IdentityStatus, IdentityGenerator,
    create_identity, generate_persona, create_email_identity,
    create_social_identity, create_phone_identity, manage_identity
)

from .education import (
    IdentityEducator, IdentityConcept, IdentityModule,
    learn_identity_basics, learn_identity_creation, learn_identity_removal,
    get_identity_guide, explain_digital_footprint, explain_opsec
)

from .removal import (
    IdentityRemover, RemovalStrategy, RemovalMethod,
    remove_identity, delete_accounts, cleanup_traces,
    burn_identity, verify_removal, generate_removal_report
)

from .management import (
    IdentityManager, IdentityProfile, ActivityTracker,
    track_identity_usage, maintain_identity, rotate_identity,
    audit_identity, backup_identity_data
)

__all__ = [
    # Core identity
    'DigitalIdentity', 'IdentityType', 'IdentityStatus', 'IdentityGenerator',
    'create_identity', 'generate_persona', 'create_email_identity',
    'create_social_identity', 'create_phone_identity', 'manage_identity',
    
    # Education
    'IdentityEducator', 'IdentityConcept', 'IdentityModule',
    'learn_identity_basics', 'learn_identity_creation', 'learn_identity_removal',
    'get_identity_guide', 'explain_digital_footprint', 'explain_opsec',
    
    # Removal
    'IdentityRemover', 'RemovalStrategy', 'RemovalMethod',
    'remove_identity', 'delete_accounts', 'cleanup_traces',
    'burn_identity', 'verify_removal', 'generate_removal_report',
    
    # Management
    'IdentityManager', 'IdentityProfile', 'ActivityTracker',
    'track_identity_usage', 'maintain_identity', 'rotate_identity',
    'audit_identity', 'backup_identity_data'
]

