# Specter Web Operations Library
# HTTP client, web scraping, API interaction, injection testing

__version__ = "0.1.0"
__author__ = "Reaper Security Team"

# Core features implemented in L1-T005
from .http.client import (
    SpecterHTTPClient, HTTPMethod, ProxyType, ProxyConfig, HTTPResponse, HTTPOperationResult,
    make_request, get_url, post_data, download_file
)

from .scraping.scraper import (
    SpecterWebScraper, ScrapingMethod, AntiDetectionLevel, ScrapingConfig, 
    ScrapedData, ScrapingResult, scrape_page, crawl_site, extract_data
)

from .api.client import (
    SpecterAPIClient, AuthMethod, RateLimitStrategy, AuthConfig, RateLimitConfig,
    APIResponse, APIOperationResult, create_api_client, test_api_endpoint, make_api_request
)

from .injection.tester import (
    SpecterInjectionTester, InjectionType, PayloadType, VulnerabilityLevel,
    InjectionPayload, InjectionResult, VulnerabilityScanResult,
    test_sql_injection, test_xss_injection, scan_for_vulnerabilities,
    generate_sql_payload, generate_xss_payload
)

__all__ = [
    # HTTP client
    'SpecterHTTPClient', 'HTTPMethod', 'ProxyType', 'ProxyConfig', 'HTTPResponse', 'HTTPOperationResult',
    'make_request', 'get_url', 'post_data', 'download_file',
    
    # Web scraping
    'SpecterWebScraper', 'ScrapingMethod', 'AntiDetectionLevel', 'ScrapingConfig', 
    'ScrapedData', 'ScrapingResult', 'scrape_page', 'crawl_site', 'extract_data',
    
    # API interaction
    'SpecterAPIClient', 'AuthMethod', 'RateLimitStrategy', 'AuthConfig', 'RateLimitConfig',
    'APIResponse', 'APIOperationResult', 'create_api_client', 'test_api_endpoint', 'make_api_request',
    
    # Injection testing
    'SpecterInjectionTester', 'InjectionType', 'PayloadType', 'VulnerabilityLevel',
    'InjectionPayload', 'InjectionResult', 'VulnerabilityScanResult',
    'test_sql_injection', 'test_xss_injection', 'scan_for_vulnerabilities',
    'generate_sql_payload', 'generate_xss_payload'
]

# Will be implemented in L1-T008 and L1-T009
# Core features: HTTP client, web scraping, API framework
# Advanced features: session management, JS execution, injection testing

__all__ = [
    # Will be populated as features are implemented
]
