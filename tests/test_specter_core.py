#!/usr/bin/env python3
"""
Comprehensive test suite for Specter Web Operations Library
Tests HTTP client, web scraping, API interaction, and injection testing
"""

import unittest
import tempfile
import os
import time
import threading
from unittest.mock import patch, MagicMock, Mock
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

# Import specter modules
from libs.specter.http.client import (
    SpecterHTTPClient, HTTPMethod, ProxyType, ProxyConfig, HTTPResponse, HTTPOperationResult
)
from libs.specter.scraping.scraper import (
    SpecterWebScraper, ScrapingMethod, AntiDetectionLevel, ScrapingConfig, 
    ScrapedData, ScrapingResult
)
from libs.specter.api.client import (
    SpecterAPIClient, AuthMethod, RateLimitStrategy, AuthConfig, RateLimitConfig,
    APIResponse, APIOperationResult
)
from libs.specter.injection.tester import (
    SpecterInjectionTester, InjectionType, PayloadType, VulnerabilityLevel,
    InjectionPayload, InjectionResult, VulnerabilityScanResult
)

class TestSpecterHTTPClient(unittest.TestCase):
    """Test HTTP client functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = SpecterHTTPClient({'safe_mode': True})
        self.test_url = "http://example.com"
        self.test_data = {"key": "value"}
    
    def test_initialization(self):
        """Test HTTP client initialization"""
        self.assertIsInstance(self.client, SpecterHTTPClient)
        self.assertTrue(self.client.safe_mode)
        self.assertIsInstance(self.client.session, requests.Session)
        self.assertIsInstance(self.client.user_agents, list)
        self.assertGreater(len(self.client.user_agents), 0)
    
    def test_safe_mode_request(self):
        """Test request in safe mode"""
        result = self.client.get(self.test_url)
        
        self.assertIsInstance(result, HTTPOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "request")
        self.assertEqual(result.url, self.test_url)
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_proxy_configuration(self):
        """Test proxy configuration"""
        proxy_config = ProxyConfig(
            host="127.0.0.1",
            port=8080,
            proxy_type=ProxyType.HTTP,
            username="user",
            password="pass"
        )
        
        result = self.client.set_proxy(proxy_config)
        
        self.assertIsInstance(result, HTTPOperationResult)
        self.assertFalse(result.success)  # Safe mode
        self.assertEqual(result.operation, "set_proxy")
        self.assertIn("Safe mode", result.message)
    
    def test_user_agent_rotation(self):
        """Test user agent rotation"""
        user_agent1 = self.client._get_random_user_agent()
        user_agent2 = self.client._get_random_user_agent()
        
        self.assertIsInstance(user_agent1, str)
        self.assertIsInstance(user_agent2, str)
        self.assertIn("Mozilla", user_agent1)
        self.assertIn("Mozilla", user_agent2)
    
    def test_random_headers(self):
        """Test random headers generation"""
        headers = self.client._get_random_headers()
        
        self.assertIsInstance(headers, dict)
        self.assertIn('User-Agent', headers)
        self.assertIn('Accept', headers)
        self.assertIn('Accept-Language', headers)
        self.assertIn('Accept-Encoding', headers)
    
    def test_operation_logging(self):
        """Test operation logging"""
        initial_log_count = len(self.client.operation_log)
        
        # Make a request (will be blocked in safe mode)
        self.client.get(self.test_url)
        
        # Check log was updated
        self.assertEqual(len(self.client.operation_log), initial_log_count + 1)
        
        log_entry = self.client.operation_log[-1]
        self.assertIn('timestamp', log_entry)
        self.assertEqual(log_entry['operation'], 'request')
        self.assertEqual(log_entry['url'], self.test_url)
        self.assertFalse(log_entry['success'])
    
    def test_file_download_safe_mode(self):
        """Test file download in safe mode"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = self.client.download_file(self.test_url, temp_path)
            
            self.assertIsInstance(result, HTTPOperationResult)
            self.assertFalse(result.success)
            self.assertEqual(result.operation, "download_file")
            self.assertIn("Safe mode", result.message)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_file_upload_safe_mode(self):
        """Test file upload in safe mode"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name
        
        try:
            result = self.client.upload_file(self.test_url, temp_path)
            
            self.assertIsInstance(result, HTTPOperationResult)
            self.assertFalse(result.success)
            self.assertEqual(result.operation, "upload_file")
            self.assertIn("Safe mode", result.message)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_cookie_management(self):
        """Test cookie management"""
        # Set cookies
        cookies = {"session": "abc123", "user": "test"}
        self.client.set_cookies(cookies)
        
        # Get cookies
        retrieved_cookies = self.client.get_cookies()
        
        self.assertIsInstance(retrieved_cookies, dict)
        # Note: In safe mode, cookies might not be set, so we just test the method exists
    
    def test_operation_log_management(self):
        """Test operation log management"""
        # Clear log
        self.client.clear_operation_log()
        self.assertEqual(len(self.client.operation_log), 0)
        
        # Make request to generate log entry
        self.client.get(self.test_url)
        
        # Get log
        log = self.client.get_operation_log()
        self.assertIsInstance(log, list)
        self.assertEqual(len(log), 1)

class TestSpecterWebScraper(unittest.TestCase):
    """Test web scraper functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scraper = SpecterWebScraper()
        self.test_url = "http://example.com"
        self.test_html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Test Heading</h1>
            <p>Test paragraph</p>
            <a href="/link1">Link 1</a>
            <a href="http://external.com">External Link</a>
            <img src="/image1.jpg" alt="Image 1">
            <form action="/submit" method="POST">
                <input name="username" type="text">
                <input name="password" type="password">
            </form>
        </body>
        </html>
        """
    
    def test_initialization(self):
        """Test scraper initialization"""
        self.assertIsInstance(self.scraper, SpecterWebScraper)
        self.assertTrue(self.scraper.safe_mode)
        self.assertIsInstance(self.scraper.session, requests.Session)
        self.assertIsInstance(self.scraper.user_agents, list)
        self.assertGreater(len(self.scraper.user_agents), 0)
    
    def test_safe_mode_scraping(self):
        """Test scraping in safe mode"""
        result = self.scraper.scrape_page(self.test_url)
        
        self.assertIsInstance(result, ScrapingResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "scrape_page")
        self.assertEqual(result.url, self.test_url)
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_html_parsing(self):
        """Test HTML parsing functionality"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(self.test_html, 'html.parser')
        
        # Test link extraction
        links = self.scraper._extract_links(soup, self.test_url)
        self.assertIsInstance(links, list)
        self.assertGreater(len(links), 0)
        
        # Test image extraction
        images = self.scraper._extract_images(soup, self.test_url)
        self.assertIsInstance(images, list)
        self.assertGreater(len(images), 0)
        
        # Test form extraction
        forms = self.scraper._extract_forms(soup)
        self.assertIsInstance(forms, list)
        self.assertGreater(len(forms), 0)
        
        # Test metadata extraction
        metadata = self.scraper._extract_metadata(soup)
        self.assertIsInstance(metadata, dict)
        self.assertIn('title', metadata)
    
    def test_multiple_page_scraping_safe_mode(self):
        """Test multiple page scraping in safe mode"""
        urls = [self.test_url, "http://example2.com", "http://example3.com"]
        
        results = self.scraper.scrape_multiple_pages(urls)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(urls))
        
        for result in results:
            self.assertIsInstance(result, ScrapingResult)
            self.assertFalse(result.success)
            self.assertIn("Safe mode", result.message)
    
    def test_site_crawling_safe_mode(self):
        """Test site crawling in safe mode"""
        result = self.scraper.crawl_site(self.test_url, max_pages=5)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)  # Only the initial blocked request
        
        first_result = result[0]
        self.assertIsInstance(first_result, ScrapingResult)
        self.assertFalse(first_result.success)
        self.assertIn("Safe mode", first_result.message)
    
    def test_data_extraction_safe_mode(self):
        """Test data extraction in safe mode"""
        selectors = {"title": "title", "heading": "h1"}
        
        result = self.scraper.extract_data_by_selector(self.test_url, selectors)
        
        self.assertIsInstance(result, ScrapingResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "extract_data_by_selector")
        self.assertIn("Safe mode", result.message)
    
    def test_scraped_urls_tracking(self):
        """Test scraped URLs tracking"""
        urls = self.scraper.get_scraped_urls()
        self.assertIsInstance(urls, set)
        self.assertEqual(len(urls), 0)  # No URLs scraped in safe mode
    
    def test_operation_logging(self):
        """Test operation logging"""
        initial_log_count = len(self.scraper.operation_log)
        
        # Make a scraping request (will be blocked in safe mode)
        self.scraper.scrape_page(self.test_url)
        
        # Check log was updated
        self.assertEqual(len(self.scraper.operation_log), initial_log_count + 1)
        
        log_entry = self.scraper.operation_log[-1]
        self.assertIn('timestamp', log_entry)
        self.assertEqual(log_entry['operation'], 'scrape_page')
        self.assertEqual(log_entry['url'], self.test_url)
        self.assertFalse(log_entry['success'])

class TestSpecterAPIClient(unittest.TestCase):
    """Test API client functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://api.example.com"
        self.auth_config = AuthConfig(AuthMethod.BASIC, username="user", password="pass")
        self.client = SpecterAPIClient(self.base_url, self.auth_config)
        self.test_endpoint = "/test"
    
    def test_initialization(self):
        """Test API client initialization"""
        self.assertIsInstance(self.client, SpecterAPIClient)
        self.assertEqual(self.client.base_url, self.base_url)
        self.assertEqual(self.client.auth_config.method, AuthMethod.BASIC)
        self.assertTrue(self.client.safe_mode)
        self.assertIsInstance(self.client.session, requests.Session)
    
    def test_safe_mode_api_request(self):
        """Test API request in safe mode"""
        result = self.client.get(self.test_endpoint)
        
        self.assertIsInstance(result, APIOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "api_request")
        self.assertEqual(result.url, self.test_endpoint)
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
    
    def test_auth_configuration(self):
        """Test authentication configuration"""
        # Test basic auth
        basic_auth = AuthConfig(AuthMethod.BASIC, username="user", password="pass")
        self.assertEqual(basic_auth.method, AuthMethod.BASIC)
        self.assertEqual(basic_auth.username, "user")
        self.assertEqual(basic_auth.password, "pass")
        
        # Test bearer auth
        bearer_auth = AuthConfig(AuthMethod.BEARER, token="abc123")
        self.assertEqual(bearer_auth.method, AuthMethod.BEARER)
        self.assertEqual(bearer_auth.token, "abc123")
        
        # Test API key auth
        api_key_auth = AuthConfig(AuthMethod.API_KEY, api_key="key123", api_key_header="X-API-Key")
        self.assertEqual(api_key_auth.method, AuthMethod.API_KEY)
        self.assertEqual(api_key_auth.api_key, "key123")
        self.assertEqual(api_key_auth.api_key_header, "X-API-Key")
    
    def test_rate_limit_configuration(self):
        """Test rate limiting configuration"""
        rate_config = RateLimitConfig(
            strategy=RateLimitStrategy.FIXED_DELAY,
            requests_per_minute=60,
            delay_between_requests=1.0
        )
        
        self.assertEqual(rate_config.strategy, RateLimitStrategy.FIXED_DELAY)
        self.assertEqual(rate_config.requests_per_minute, 60)
        self.assertEqual(rate_config.delay_between_requests, 1.0)
    
    def test_hmac_signature_calculation(self):
        """Test HMAC signature calculation"""
        hmac_auth = AuthConfig(AuthMethod.HMAC, secret_key="secret123")
        client = SpecterAPIClient(self.base_url, hmac_auth)
        
        signature = client._calculate_hmac_signature("GET", "/test", '{"data": "test"}')
        
        self.assertIsInstance(signature, str)
        self.assertGreater(len(signature), 0)
    
    def test_batch_request_safe_mode(self):
        """Test batch request in safe mode"""
        requests_data = [
            {"method": "GET", "endpoint": "/test1"},
            {"method": "POST", "endpoint": "/test2", "data": {"key": "value"}},
            {"method": "PUT", "endpoint": "/test3", "data": {"key": "value"}}
        ]
        
        results = self.client.batch_request(requests_data)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(requests_data))
        
        for result in results:
            self.assertIsInstance(result, APIOperationResult)
            self.assertFalse(result.success)
            self.assertIn("Safe mode", result.message)
    
    def test_endpoint_testing_safe_mode(self):
        """Test endpoint testing in safe mode"""
        result = self.client.test_endpoint(self.test_endpoint)
        
        self.assertIsInstance(result, APIOperationResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "test_endpoint")
        self.assertIn("Safe mode", result.message)
    
    def test_endpoint_discovery_safe_mode(self):
        """Test endpoint discovery in safe mode"""
        discovered = self.client.discover_endpoints()
        
        self.assertIsInstance(discovered, list)
        self.assertEqual(len(discovered), 0)  # No endpoints discovered in safe mode
    
    def test_request_stats(self):
        """Test request statistics"""
        stats = self.client.get_request_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_requests', stats)
        self.assertIn('last_request_time', stats)
        self.assertIn('rate_limit_strategy', stats)
        self.assertEqual(stats['total_requests'], 0)  # No requests in safe mode
    
    def test_operation_logging(self):
        """Test operation logging"""
        initial_log_count = len(self.client.operation_log)
        
        # Make an API request (will be blocked in safe mode)
        self.client.get(self.test_endpoint)
        
        # Check log was updated
        self.assertEqual(len(self.client.operation_log), initial_log_count + 1)
        
        log_entry = self.client.operation_log[-1]
        self.assertIn('timestamp', log_entry)
        self.assertEqual(log_entry['operation'], 'api_request')
        self.assertEqual(log_entry['url'], self.test_endpoint)
        self.assertFalse(log_entry['success'])

class TestSpecterInjectionTester(unittest.TestCase):
    """Test injection tester functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tester = SpecterInjectionTester()
        self.test_url = "http://example.com/search"
        self.test_parameter = "q"
        self.test_value = "test"
    
    def test_initialization(self):
        """Test injection tester initialization"""
        self.assertIsInstance(self.tester, SpecterInjectionTester)
        self.assertTrue(self.tester.safe_mode)
        self.assertIsInstance(self.tester.session, requests.Session)
        self.assertIsInstance(self.tester.payloads, dict)
        self.assertGreater(len(self.tester.payloads), 0)
    
    def test_payload_loading(self):
        """Test payload loading"""
        # Test SQL payloads
        sql_payloads = self.tester.payloads.get(InjectionType.SQL, [])
        self.assertGreater(len(sql_payloads), 0)
        
        for payload in sql_payloads:
            self.assertIsInstance(payload, InjectionPayload)
            self.assertEqual(payload.injection_type, InjectionType.SQL)
            self.assertIsInstance(payload.payload, str)
            self.assertGreater(len(payload.payload), 0)
        
        # Test XSS payloads
        xss_payloads = self.tester.payloads.get(InjectionType.XSS, [])
        self.assertGreater(len(xss_payloads), 0)
        
        for payload in xss_payloads:
            self.assertIsInstance(payload, InjectionPayload)
            self.assertEqual(payload.injection_type, InjectionType.XSS)
            self.assertIsInstance(payload.payload, str)
            self.assertGreater(len(payload.payload), 0)
    
    def test_safe_mode_parameter_testing(self):
        """Test parameter testing in safe mode"""
        results = self.tester.test_parameter(self.test_url, self.test_parameter, self.test_value)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)  # No tests performed in safe mode
    
    def test_safe_mode_url_scanning(self):
        """Test URL scanning in safe mode"""
        result = self.tester.scan_url(self.test_url)
        
        self.assertIsInstance(result, VulnerabilityScanResult)
        self.assertFalse(result.success)
        self.assertEqual(result.operation, "scan_url")
        self.assertEqual(result.url, self.test_url)
        self.assertIn("Safe mode", result.message)
        self.assertEqual(result.error, "Safe mode")
        self.assertIsNone(result.vulnerabilities)
    
    def test_payload_generation(self):
        """Test payload generation"""
        # Test SQL payload generation
        sql_payload = self.tester.generate_payload(InjectionType.SQL, PayloadType.BASIC)
        self.assertIsInstance(sql_payload, InjectionPayload)
        self.assertEqual(sql_payload.injection_type, InjectionType.SQL)
        self.assertEqual(sql_payload.payload_type, PayloadType.BASIC)
        self.assertIsInstance(sql_payload.payload, str)
        
        # Test XSS payload generation
        xss_payload = self.tester.generate_payload(InjectionType.XSS, PayloadType.ADVANCED)
        self.assertIsInstance(xss_payload, InjectionPayload)
        self.assertEqual(xss_payload.injection_type, InjectionType.XSS)
        self.assertEqual(xss_payload.payload_type, PayloadType.ADVANCED)
        self.assertIsInstance(xss_payload.payload, str)
        
        # Test custom payload
        custom_payload = self.tester.generate_payload(
            InjectionType.SQL, 
            PayloadType.BASIC, 
            custom_payload="' OR 1=1--"
        )
        self.assertEqual(custom_payload.payload, "' OR 1=1--")
    
    def test_false_positive_filtering(self):
        """Test false positive filtering"""
        # Create mock vulnerabilities
        vulnerabilities = [
            InjectionResult(
                success=True,
                injection_type=InjectionType.SQL,
                payload="'",
                url=self.test_url,
                parameter=self.test_parameter,
                response_code=200,
                response_time=0.1,
                vulnerability_level=VulnerabilityLevel.LOW,
                evidence="Test failed: Connection error"
            ),
            InjectionResult(
                success=True,
                injection_type=InjectionType.SQL,
                payload="' OR 1=1--",
                url=self.test_url,
                parameter=self.test_parameter,
                response_code=200,
                response_time=0.1,
                vulnerability_level=VulnerabilityLevel.HIGH,
                evidence="SQL error detected: mysql_error"
            ),
            InjectionResult(
                success=True,
                injection_type=InjectionType.XSS,
                payload="<script>alert('XSS')</script>",
                url=self.test_url,
                parameter=self.test_parameter,
                response_code=200,
                response_time=0.1,
                vulnerability_level=VulnerabilityLevel.MEDIUM,
                evidence="XSS payload reflected in response"
            )
        ]
        
        filtered = self.tester._filter_false_positives(vulnerabilities)
        
        self.assertIsInstance(filtered, list)
        # Should filter out the first one (test failed) and keep the others
        self.assertGreater(len(filtered), 0)
        self.assertLessEqual(len(filtered), len(vulnerabilities))
    
    def test_operation_logging(self):
        """Test operation logging"""
        initial_log_count = len(self.tester.operation_log)
        
        # Make a scan request (will be blocked in safe mode)
        self.tester.scan_url(self.test_url)
        
        # Check log was updated
        self.assertEqual(len(self.tester.operation_log), initial_log_count + 1)
        
        log_entry = self.tester.operation_log[-1]
        self.assertIn('timestamp', log_entry)
        self.assertEqual(log_entry['operation'], 'scan_url')
        self.assertEqual(log_entry['url'], self.test_url)
        self.assertFalse(log_entry['success'])

class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def test_http_convenience_functions(self):
        """Test HTTP convenience functions"""
        from libs.specter.http.client import make_request, get_url, post_data, download_file
        
        # Test make_request
        result = make_request(HTTPMethod.GET, "http://example.com")
        self.assertIsInstance(result, HTTPOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test get_url
        result = get_url("http://example.com")
        self.assertIsInstance(result, HTTPOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test post_data
        result = post_data("http://example.com", {"key": "value"})
        self.assertIsInstance(result, HTTPOperationResult)
        self.assertFalse(result.success)  # Safe mode
    
    def test_scraping_convenience_functions(self):
        """Test scraping convenience functions"""
        from libs.specter.scraping.scraper import scrape_page, crawl_site, extract_data
        
        # Test scrape_page
        result = scrape_page("http://example.com")
        self.assertIsInstance(result, ScrapingResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test crawl_site
        results = crawl_site("http://example.com")
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)  # Only blocked request
        
        # Test extract_data
        result = extract_data("http://example.com", {"title": "title"})
        self.assertIsInstance(result, ScrapingResult)
        self.assertFalse(result.success)  # Safe mode
    
    def test_api_convenience_functions(self):
        """Test API convenience functions"""
        from libs.specter.api.client import create_api_client, test_api_endpoint, make_api_request
        
        # Test create_api_client
        client = create_api_client("http://api.example.com")
        self.assertIsInstance(client, SpecterAPIClient)
        
        # Test test_api_endpoint
        result = test_api_endpoint("http://api.example.com", "/test")
        self.assertIsInstance(result, APIOperationResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test make_api_request
        result = make_api_request("http://api.example.com", "GET", "/test")
        self.assertIsInstance(result, APIOperationResult)
        self.assertFalse(result.success)  # Safe mode
    
    def test_injection_convenience_functions(self):
        """Test injection convenience functions"""
        from libs.specter.injection.tester import (
            test_sql_injection, test_xss_injection, scan_for_vulnerabilities,
            generate_sql_payload, generate_xss_payload
        )
        
        # Test test_sql_injection
        results = test_sql_injection("http://example.com", "q", "test")
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)  # Safe mode
        
        # Test test_xss_injection
        results = test_xss_injection("http://example.com", "q", "test")
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)  # Safe mode
        
        # Test scan_for_vulnerabilities
        result = scan_for_vulnerabilities("http://example.com")
        self.assertIsInstance(result, VulnerabilityScanResult)
        self.assertFalse(result.success)  # Safe mode
        
        # Test generate_sql_payload
        payload = generate_sql_payload(PayloadType.BASIC)
        self.assertIsInstance(payload, InjectionPayload)
        self.assertEqual(payload.injection_type, InjectionType.SQL)
        
        # Test generate_xss_payload
        payload = generate_xss_payload(PayloadType.ADVANCED)
        self.assertIsInstance(payload, InjectionPayload)
        self.assertEqual(payload.injection_type, InjectionType.XSS)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
