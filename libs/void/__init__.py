# Void OSINT Scrubbing Library
# Digital footprint removal, data broker cleanup, privacy protection

__version__ = "0.1.0"
__author__ = "Reaper Security Team"

# Core features
from .scrubber import (
    VoidOSINTScrubber, ScrubType, ScrubPriority, ScrubResult, ScrubStatus,
    scrub_email, scrub_phone, scrub_username, scrub_domain,
    analyze_footprint, remove_from_data_brokers, request_deletion,
    check_username_availability, clean_search_results
)

from .footprint import (
    FootprintAnalyzer, FootprintType, FootprintSeverity, FootprintRecord,
    analyze_digital_footprint, find_exposed_emails, find_exposed_phones,
    find_social_media_accounts, find_domain_registrations, generate_footprint_report
)

from .removal import (
    RemovalManager, RemovalRequest, RemovalStatus, RemovalProvider,
    request_google_removal, request_bing_removal, request_data_broker_removal,
    submit_deletion_request, track_removal_status
)

__all__ = [
    # Core scrubber
    'VoidOSINTScrubber', 'ScrubType', 'ScrubPriority', 'ScrubResult', 'ScrubStatus',
    'scrub_email', 'scrub_phone', 'scrub_username', 'scrub_domain',
    'analyze_footprint', 'remove_from_data_brokers', 'request_deletion',
    'check_username_availability', 'scan_social_media', 'clean_search_results',
    
    # Footprint analysis
    'FootprintAnalyzer', 'FootprintType', 'FootprintSeverity', 'FootprintRecord',
    'analyze_digital_footprint', 'find_exposed_emails', 'find_exposed_phones',
    'find_social_media_accounts', 'find_domain_registrations', 'generate_footprint_report',
    
    # Removal requests
    'RemovalManager', 'RemovalRequest', 'RemovalStatus', 'RemovalProvider',
    'request_google_removal', 'request_bing_removal', 'request_data_broker_removal',
    'submit_deletion_request', 'track_removal_status'
]

