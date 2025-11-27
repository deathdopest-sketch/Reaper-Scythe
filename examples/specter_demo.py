#!/usr/bin/env python3
"""
Specter Web Operations Library Demo
Demonstrates HTTP client, web scraping, API interaction, and injection testing
"""

import os
import sys
import time
import tempfile

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.specter.http.client import (
    SpecterHTTPClient, HTTPMethod, ProxyType, ProxyConfig, HTTPResponse, HTTPOperationResult,
    make_request, get_url, post_data as http_post_data, download_file
)
from libs.specter.scraping.scraper import (
    SpecterWebScraper, ScrapingMethod, AntiDetectionLevel, ScrapingConfig, 
    ScrapedData, ScrapingResult, scrape_page, crawl_site, extract_data
)
from libs.specter.api.client import (
    SpecterAPIClient, AuthMethod, RateLimitStrategy, AuthConfig, RateLimitConfig,
    APIResponse, APIOperationResult, create_api_client, test_api_endpoint, make_api_request
)
from libs.specter.injection.tester import (
    SpecterInjectionTester, InjectionType, PayloadType, VulnerabilityLevel,
    InjectionPayload, InjectionResult, VulnerabilityScanResult,
    test_sql_injection, test_xss_injection, scan_for_vulnerabilities,
    generate_sql_payload, generate_xss_payload
)

def run_specter_demo():
    print("--- Specter Web Operations Library Demo ---")

    # --- HTTP Client Demo ---
    print("\n### HTTP Client Demo ###")
    http_client = SpecterHTTPClient({'safe_mode': True})  # Start in safe mode for demo

    test_url = "http://httpbin.org/get"
    print(f"Testing HTTP client with URL: {test_url}")

    # GET request (safe mode)
    print("\nMaking GET request (safe mode):")
    get_result = http_client.get(test_url)
    print(f"  GET result: {get_result.success} - {get_result.message}")

    # POST request (safe mode)
    print("\nMaking POST request (safe mode):")
    post_data_dict = {"key": "value", "test": "data"}
    post_result = http_client.post("http://httpbin.org/post", data=post_data_dict)
    print(f"  POST result: {post_result.success} - {post_result.message}")

    # Proxy configuration (safe mode)
    print("\nConfiguring proxy (safe mode):")
    proxy_config = ProxyConfig(
        host="127.0.0.1",
        port=8080,
        proxy_type=ProxyType.HTTP,
        username="user",
        password="pass"
    )
    proxy_result = http_client.set_proxy(proxy_config)
    print(f"  Proxy config result: {proxy_result.success} - {proxy_result.message}")

    # File download (safe mode)
    print("\nFile download (safe mode):")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_path = temp_file.name
    
    download_result = http_client.download_file("http://httpbin.org/robots.txt", temp_path)
    print(f"  Download result: {download_result.success} - {download_result.message}")
    
    # Clean up
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # User agent rotation
    print("\nUser agent rotation:")
    for i in range(3):
        user_agent = http_client._get_random_user_agent()
        print(f"  User agent {i+1}: {user_agent[:50]}...")

    # Random headers
    print("\nRandom headers generation:")
    headers = http_client._get_random_headers()
    for key, value in list(headers.items())[:3]:
        print(f"  {key}: {value}")

    # Operation log
    print("\nOperation log:")
    log = http_client.get_operation_log()
    print(f"  Total operations logged: {len(log)}")
    for entry in log[-2:]:  # Show last 2 entries
        print(f"    {entry['operation']} on {entry['url']}: {entry['message']}")


    # --- Web Scraping Demo ---
    print("\n### Web Scraping Demo ###")
    scraper = SpecterWebScraper(ScrapingConfig(
        method=ScrapingMethod.REQUESTS,
        anti_detection=AntiDetectionLevel.BASIC,
        delay_min=1.0,
        delay_max=2.0
    ))

    test_scrape_url = "http://httpbin.org/html"
    print(f"Testing web scraper with URL: {test_scrape_url}")

    # Single page scraping (safe mode)
    print("\nSingle page scraping (safe mode):")
    scrape_result = scraper.scrape_page(test_scrape_url)
    print(f"  Scrape result: {scrape_result.success} - {scrape_result.message}")

    # Multiple page scraping (safe mode)
    print("\nMultiple page scraping (safe mode):")
    urls_to_scrape = [
        "http://httpbin.org/html",
        "http://httpbin.org/json",
        "http://httpbin.org/xml"
    ]
    multi_results = scraper.scrape_multiple_pages(urls_to_scrape, max_concurrent=2)
    print(f"  Multi-scrape results: {len(multi_results)} pages attempted")
    for i, result in enumerate(multi_results):
        print(f"    Page {i+1}: {result.success} - {result.message}")

    # Site crawling (safe mode)
    print("\nSite crawling (safe mode):")
    crawl_results = scraper.crawl_site(test_scrape_url, max_pages=3, max_depth=1)
    print(f"  Crawl results: {len(crawl_results)} pages crawled")
    for i, result in enumerate(crawl_results):
        print(f"    Page {i+1}: {result.success} - {result.message}")

    # Data extraction (safe mode)
    print("\nData extraction (safe mode):")
    selectors = {
        "title": "title",
        "headings": "h1, h2, h3",
        "links": "a",
        "images": "img"
    }
    extract_result = scraper.extract_data_by_selector(test_scrape_url, selectors)
    print(f"  Extract result: {extract_result.success} - {extract_result.message}")

    # Scraped URLs tracking
    print("\nScraped URLs tracking:")
    scraped_urls = scraper.get_scraped_urls()
    print(f"  Total URLs scraped: {len(scraped_urls)}")

    # Operation log
    print("\nScraping operation log:")
    log = scraper.get_operation_log()
    print(f"  Total operations logged: {len(log)}")
    for entry in log[-2:]:  # Show last 2 entries
        print(f"    {entry['operation']} on {entry['url']}: {entry['message']}")


    # --- API Client Demo ---
    print("\n### API Client Demo ###")
    
    # Test different authentication methods
    print("\nAuthentication configurations:")
    
    # Basic auth
    basic_auth = AuthConfig(AuthMethod.BASIC, username="user", password="pass")
    print(f"  Basic auth: {basic_auth.method.value} - {basic_auth.username}")
    
    # Bearer token
    bearer_auth = AuthConfig(AuthMethod.BEARER, token="abc123token")
    print(f"  Bearer auth: {bearer_auth.method.value} - {bearer_auth.token[:10]}...")
    
    # API key
    api_key_auth = AuthConfig(AuthMethod.API_KEY, api_key="key123", api_key_header="X-API-Key")
    print(f"  API key auth: {api_key_auth.method.value} - {api_key_auth.api_key}")
    
    # HMAC
    hmac_auth = AuthConfig(AuthMethod.HMAC, secret_key="secret123")
    print(f"  HMAC auth: {hmac_auth.method.value} - secret key configured")

    # Rate limiting configurations
    print("\nRate limiting configurations:")
    
    fixed_delay_config = RateLimitConfig(
        strategy=RateLimitStrategy.FIXED_DELAY,
        requests_per_minute=60,
        delay_between_requests=1.0
    )
    print(f"  Fixed delay: {fixed_delay_config.strategy.value} - {fixed_delay_config.delay_between_requests}s delay")
    
    exponential_backoff_config = RateLimitConfig(
        strategy=RateLimitStrategy.EXPONENTIAL_BACKOFF,
        requests_per_minute=30,
        backoff_factor=2.0
    )
    print(f"  Exponential backoff: {exponential_backoff_config.strategy.value} - factor {exponential_backoff_config.backoff_factor}")

    # API client operations (safe mode)
    api_client = SpecterAPIClient("http://api.example.com", basic_auth, fixed_delay_config)
    print(f"\nAPI client created for: {api_client.base_url}")

    # API requests (safe mode)
    print("\nAPI requests (safe mode):")
    get_result = api_client.get("/users")
    print(f"  GET /users: {get_result.success} - {get_result.message}")
    
    post_result = api_client.post("/users", {"name": "test", "email": "test@example.com"})
    print(f"  POST /users: {post_result.success} - {post_result.message}")
    
    put_result = api_client.put("/users/1", {"name": "updated"})
    print(f"  PUT /users/1: {put_result.success} - {put_result.message}")
    
    delete_result = api_client.delete("/users/1")
    print(f"  DELETE /users/1: {delete_result.success} - {delete_result.message}")

    # Batch requests (safe mode)
    print("\nBatch requests (safe mode):")
    batch_requests = [
        {"method": "GET", "endpoint": "/users"},
        {"method": "GET", "endpoint": "/posts"},
        {"method": "GET", "endpoint": "/comments"}
    ]
    batch_results = api_client.batch_request(batch_requests, max_concurrent=2)
    print(f"  Batch results: {len(batch_results)} requests")
    for i, result in enumerate(batch_results):
        print(f"    Request {i+1}: {result.success} - {result.message}")

    # Endpoint testing (safe mode)
    print("\nEndpoint testing (safe mode):")
    test_result = api_client.test_endpoint("/health")
    print(f"  Health check: {test_result.success} - {test_result.message}")

    # Endpoint discovery (safe mode)
    print("\nEndpoint discovery (safe mode):")
    discovered = api_client.discover_endpoints(["/", "/api", "/v1", "/docs"])
    print(f"  Discovered endpoints: {len(discovered)}")

    # Request statistics
    print("\nRequest statistics:")
    stats = api_client.get_request_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Operation log
    print("\nAPI operation log:")
    log = api_client.get_operation_log()
    print(f"  Total operations logged: {len(log)}")
    for entry in log[-2:]:  # Show last 2 entries
        print(f"    {entry['operation']} on {entry['url']}: {entry['message']}")


    # --- Injection Testing Demo ---
    print("\n### Injection Testing Demo ###")
    injection_tester = SpecterInjectionTester()

    test_injection_url = "http://example.com/search"
    test_param = "q"
    test_value = "test"
    
    print(f"Testing injection vulnerabilities on: {test_injection_url}?{test_param}={test_value}")

    # Payload overview
    print("\nAvailable payloads:")
    for injection_type, payloads in injection_tester.payloads.items():
        print(f"  {injection_type.value.upper()}: {len(payloads)} payloads")
        for payload in payloads[:2]:  # Show first 2 payloads
            print(f"    - {payload.description}: {payload.payload[:30]}...")

    # Parameter testing (safe mode)
    print("\nParameter testing (safe mode):")
    sql_results = injection_tester.test_parameter(test_injection_url, test_param, test_value, [InjectionType.SQL])
    print(f"  SQL injection tests: {len(sql_results)} tests performed")
    
    xss_results = injection_tester.test_parameter(test_injection_url, test_param, test_value, [InjectionType.XSS])
    print(f"  XSS injection tests: {len(xss_results)} tests performed")

    # URL scanning (safe mode)
    print("\nURL vulnerability scanning (safe mode):")
    scan_result = injection_tester.scan_url(test_injection_url)
    print(f"  Scan result: {scan_result.success} - {scan_result.message}")
    if scan_result.vulnerabilities:
        print(f"  Vulnerabilities found: {len(scan_result.vulnerabilities)}")
        for vuln in scan_result.vulnerabilities[:3]:  # Show first 3
            print(f"    - {vuln.injection_type.value}: {vuln.vulnerability_level.value} - {vuln.evidence}")

    # Payload generation
    print("\nPayload generation:")
    
    # SQL payloads
    basic_sql = injection_tester.generate_payload(InjectionType.SQL, PayloadType.BASIC)
    print(f"  Basic SQL payload: {basic_sql.payload}")
    
    time_based_sql = injection_tester.generate_payload(InjectionType.SQL, PayloadType.TIME_BASED)
    print(f"  Time-based SQL payload: {time_based_sql.payload}")
    
    union_sql = injection_tester.generate_payload(InjectionType.SQL, PayloadType.UNION_BASED)
    print(f"  Union-based SQL payload: {union_sql.payload}")

    # XSS payloads
    basic_xss = injection_tester.generate_payload(InjectionType.XSS, PayloadType.BASIC)
    print(f"  Basic XSS payload: {basic_xss.payload}")
    
    advanced_xss = injection_tester.generate_payload(InjectionType.XSS, PayloadType.ADVANCED)
    print(f"  Advanced XSS payload: {advanced_xss.payload}")

    # Custom payloads
    custom_sql = injection_tester.generate_payload(
        InjectionType.SQL, 
        PayloadType.BASIC, 
        custom_payload="'; DROP TABLE users--"
    )
    print(f"  Custom SQL payload: {custom_sql.payload}")

    # Vulnerability levels
    print("\nVulnerability levels:")
    for level in VulnerabilityLevel:
        print(f"  {level.value.upper()}: {level.value}")

    # Operation log
    print("\nInjection testing operation log:")
    log = injection_tester.get_operation_log()
    print(f"  Total operations logged: {len(log)}")
    for entry in log[-2:]:  # Show last 2 entries
        print(f"    {entry['operation']} on {entry['url']}: {entry['message']}")


    # --- Convenience Functions Demo ---
    print("\n### Convenience Functions Demo ###")
    
    print("\nHTTP convenience functions:")
    # These will all be in safe mode
    result = get_url("http://example.com")
    print(f"  get_url(): {result.success} - {result.message}")
    
    result = http_post_data("http://example.com", {"key": "value"})
    print(f"  http_post_data(): {result.success} - {result.message}")

    print("\nScraping convenience functions:")
    result = scrape_page("http://example.com")
    print(f"  scrape_page(): {result.success} - {result.message}")
    
    results = crawl_site("http://example.com", max_pages=2)
    print(f"  crawl_site(): {len(results)} pages")

    print("\nAPI convenience functions:")
    client = create_api_client("http://api.example.com")
    print(f"  create_api_client(): {type(client).__name__}")
    
    result = test_api_endpoint("http://api.example.com", "/test")
    print(f"  test_api_endpoint(): {result.success} - {result.message}")

    print("\nInjection convenience functions:")
    results = test_sql_injection("http://example.com", "q", "test")
    print(f"  test_sql_injection(): {len(results)} tests")
    
    results = test_xss_injection("http://example.com", "q", "test")
    print(f"  test_xss_injection(): {len(results)} tests")
    
    result = scan_for_vulnerabilities("http://example.com")
    print(f"  scan_for_vulnerabilities(): {result.success} - {result.message}")
    
    payload = generate_sql_payload(PayloadType.BASIC)
    print(f"  generate_sql_payload(): {payload.payload}")
    
    payload = generate_xss_payload(PayloadType.ADVANCED)
    print(f"  generate_xss_payload(): {payload.payload}")

    print("\n--- Specter Web Operations Library Demo Complete ---")

if __name__ == "__main__":
    run_specter_demo()
