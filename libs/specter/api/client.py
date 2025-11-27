#!/usr/bin/env python3
"""
Specter API Operations Module
Advanced API interaction with authentication, rate limiting, and security features
"""

import requests
import time
import random
import logging
import json
import base64
import hmac
import hashlib
from typing import Optional, List, Dict, Any, Union, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlencode, parse_qs
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AuthMethod(Enum):
    """Authentication methods"""
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH1 = "oauth1"
    OAUTH2 = "oauth2"
    HMAC = "hmac"
    JWT = "jwt"

class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    NONE = "none"
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ADAPTIVE = "adaptive"

@dataclass
class AuthConfig:
    """Authentication configuration"""
    method: AuthMethod
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    api_key_param: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    consumer_key: Optional[str] = None
    consumer_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    secret_key: Optional[str] = None

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    strategy: RateLimitStrategy = RateLimitStrategy.FIXED_DELAY
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    delay_between_requests: float = 1.0
    max_retries: int = 3
    backoff_factor: float = 2.0

@dataclass
class APIResponse:
    """API response data"""
    status_code: int
    headers: Dict[str, str]
    data: Any
    text: str
    url: str
    elapsed_time: float
    timestamp: float

@dataclass
class APIOperationResult:
    """Result of API operation"""
    success: bool
    operation: str
    url: str
    message: str
    response: Optional[APIResponse] = None
    error: Optional[str] = None

class SpecterAPIClient:
    """Advanced API client with authentication and rate limiting"""
    
    def __init__(self, base_url: str, 
                 auth_config: Optional[AuthConfig] = None,
                 rate_limit_config: Optional[RateLimitConfig] = None):
        """Initialize API client
        
        Args:
            base_url: Base URL for API
            auth_config: Authentication configuration
            rate_limit_config: Rate limiting configuration
        """
        self.base_url = base_url.rstrip('/')
        self.auth_config = auth_config or AuthConfig(AuthMethod.NONE)
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.safe_mode = True  # Always start in safe mode
        self.session = requests.Session()
        self.operation_log = []
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit_lock = threading.Lock()
        
        # Setup session
        self._setup_session()
    
    def _setup_session(self):
        """Setup session with authentication"""
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Specter-API-Client/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Setup authentication
        self._setup_authentication()
        
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _setup_authentication(self):
        """Setup authentication based on config"""
        if self.auth_config.method == AuthMethod.BASIC:
            if self.auth_config.username and self.auth_config.password:
                credentials = f"{self.auth_config.username}:{self.auth_config.password}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                self.session.headers['Authorization'] = f"Basic {encoded_credentials}"
        
        elif self.auth_config.method == AuthMethod.BEARER:
            if self.auth_config.token:
                self.session.headers['Authorization'] = f"Bearer {self.auth_config.token}"
        
        elif self.auth_config.method == AuthMethod.API_KEY:
            if self.auth_config.api_key:
                if self.auth_config.api_key_header:
                    self.session.headers[self.auth_config.api_key_header] = self.auth_config.api_key
        
        elif self.auth_config.method == AuthMethod.HMAC:
            # HMAC will be calculated per request
            pass
    
    def _log_operation(self, operation: str, url: str, success: bool, message: str):
        """Log API operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'url': url,
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"API operation: {operation} on {url} - {message}")
    
    def _apply_rate_limiting(self):
        """Apply rate limiting based on strategy"""
        with self.rate_limit_lock:
            current_time = time.time()
            
            if self.rate_limit_config.strategy == RateLimitStrategy.FIXED_DELAY:
                if self.last_request_time > 0:
                    elapsed = current_time - self.last_request_time
                    if elapsed < self.rate_limit_config.delay_between_requests:
                        time.sleep(self.rate_limit_config.delay_between_requests - elapsed)
            
            elif self.rate_limit_config.strategy == RateLimitStrategy.EXPONENTIAL_BACKOFF:
                if self.request_count > 0:
                    delay = self.rate_limit_config.delay_between_requests * (self.rate_limit_config.backoff_factor ** self.request_count)
                    time.sleep(min(delay, 60))  # Cap at 60 seconds
            
            self.last_request_time = time.time()
            self.request_count += 1
    
    def _calculate_hmac_signature(self, method: str, url: str, data: str = "") -> str:
        """Calculate HMAC signature for request"""
        if not self.auth_config.secret_key:
            raise ValueError("Secret key required for HMAC authentication")
        
        # Create signature string
        timestamp = str(int(time.time()))
        signature_string = f"{method.upper()}{url}{data}{timestamp}"
        
        # Calculate HMAC
        signature = hmac.new(
            self.auth_config.secret_key.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _make_request(self, method: str, endpoint: str,
                     data: Optional[Union[Dict[str, Any], str, bytes]] = None,
                     params: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None,
                     timeout: Optional[int] = None) -> APIOperationResult:
        """Make API request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: URL parameters
            headers: Additional headers
            timeout: Request timeout
            
        Returns:
            APIOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - API request would be made to {endpoint}")
                self._log_operation("api_request", endpoint, False, "Safe mode enabled - operation blocked")
                return APIOperationResult(
                    success=False,
                    operation="api_request",
                    url=endpoint,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Apply rate limiting
            self._apply_rate_limiting()
            
            # Build URL
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            # Prepare headers
            request_headers = {}
            if headers:
                request_headers.update(headers)
            
            # Handle HMAC authentication
            if self.auth_config.method == AuthMethod.HMAC:
                data_str = json.dumps(data) if isinstance(data, dict) else str(data) if data else ""
                signature = self._calculate_hmac_signature(method, url, data_str)
                request_headers['X-Signature'] = signature
                request_headers['X-Timestamp'] = str(int(time.time()))
            
            # Handle API key in parameters
            if self.auth_config.method == AuthMethod.API_KEY and self.auth_config.api_key_param:
                if params is None:
                    params = {}
                params[self.auth_config.api_key_param] = self.auth_config.api_key
            
            # Make request with retries
            for attempt in range(self.rate_limit_config.max_retries):
                try:
                    start_time = time.time()
                    
                    response = self.session.request(
                        method=method,
                        url=url,
                        data=data,
                        params=params,
                        headers=request_headers,
                        timeout=timeout or 30,
                        verify=False
                    )
                    
                    elapsed_time = time.time() - start_time
                    
                    # Parse response data
                    try:
                        response_data = response.json()
                    except (ValueError, json.JSONDecodeError):
                        response_data = response.text
                    
                    # Create response object
                    api_response = APIResponse(
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        data=response_data,
                        text=response.text,
                        url=response.url,
                        elapsed_time=elapsed_time,
                        timestamp=time.time()
                    )
                    
                    self._log_operation("api_request", endpoint, True, f"Request successful: {response.status_code}")
                    
                    return APIOperationResult(
                        success=True,
                        operation="api_request",
                        url=endpoint,
                        message=f"Request successful: {response.status_code}",
                        response=api_response
                    )
                    
                except requests.exceptions.RequestException as e:
                    if attempt < self.rate_limit_config.max_retries - 1:
                        logger.warning(f"API request attempt {attempt + 1} failed: {e}")
                        time.sleep(self.rate_limit_config.delay_between_requests * (attempt + 1))
                        continue
                    else:
                        raise
            
        except Exception as e:
            error_msg = f"API request failed: {e}"
            self._log_operation("api_request", endpoint, False, error_msg)
            return APIOperationResult(
                success=False,
                operation="api_request",
                url=endpoint,
                message=error_msg,
                error=str(e)
            )
    
    def get(self, endpoint: str, **kwargs) -> APIOperationResult:
        """Make GET request"""
        return self._make_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Union[Dict[str, Any], str, bytes]] = None, **kwargs) -> APIOperationResult:
        """Make POST request"""
        return self._make_request('POST', endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Union[Dict[str, Any], str, bytes]] = None, **kwargs) -> APIOperationResult:
        """Make PUT request"""
        return self._make_request('PUT', endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> APIOperationResult:
        """Make DELETE request"""
        return self._make_request('DELETE', endpoint, **kwargs)
    
    def patch(self, endpoint: str, data: Optional[Union[Dict[str, Any], str, bytes]] = None, **kwargs) -> APIOperationResult:
        """Make PATCH request"""
        return self._make_request('PATCH', endpoint, data=data, **kwargs)
    
    def head(self, endpoint: str, **kwargs) -> APIOperationResult:
        """Make HEAD request"""
        return self._make_request('HEAD', endpoint, **kwargs)
    
    def options(self, endpoint: str, **kwargs) -> APIOperationResult:
        """Make OPTIONS request"""
        return self._make_request('OPTIONS', endpoint, **kwargs)
    
    def batch_request(self, requests: List[Dict[str, Any]], 
                     max_concurrent: int = 5) -> List[APIOperationResult]:
        """Make multiple requests concurrently
        
        Args:
            requests: List of request dictionaries with keys: method, endpoint, data, params, headers
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of APIOperationResult
        """
        results = []
        
        if self.safe_mode:
            logger.warning(f"Safe mode enabled - batch request would be performed with {len(requests)} requests")
            for req in requests:
                self._log_operation("batch_request", req.get('endpoint', ''), False, "Safe mode enabled - operation blocked")
                results.append(APIOperationResult(
                    success=False,
                    operation="batch_request",
                    url=req.get('endpoint', ''),
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                ))
            return results
        
        # Use threading for concurrent requests
        threads = []
        results_lock = threading.Lock()
        
        def request_worker(request_data):
            result = self._make_request(**request_data)
            with results_lock:
                results.append(result)
        
        # Start threads
        for req in requests:
            while len(threads) >= max_concurrent:
                # Wait for a thread to complete
                threads = [t for t in threads if t.is_alive()]
                time.sleep(0.1)
            
            thread = threading.Thread(target=request_worker, args=(req,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        return results
    
    def test_endpoint(self, endpoint: str, 
                     expected_status: int = 200,
                     timeout: int = 10) -> APIOperationResult:
        """Test API endpoint availability
        
        Args:
            endpoint: API endpoint to test
            expected_status: Expected HTTP status code
            timeout: Request timeout
            
        Returns:
            APIOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - endpoint test would be performed on {endpoint}")
                self._log_operation("test_endpoint", endpoint, False, "Safe mode enabled - operation blocked")
                return APIOperationResult(
                    success=False,
                    operation="test_endpoint",
                    url=endpoint,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Make HEAD request to test endpoint
            result = self.head(endpoint, timeout=timeout)
            
            if result.success and result.response:
                if result.response.status_code == expected_status:
                    result.message = f"Endpoint test passed: {result.response.status_code}"
                else:
                    result.success = False
                    result.message = f"Endpoint test failed: expected {expected_status}, got {result.response.status_code}"
                    result.error = f"Status code mismatch: {result.response.status_code}"
            
            return result
            
        except Exception as e:
            error_msg = f"Endpoint test failed: {e}"
            self._log_operation("test_endpoint", endpoint, False, error_msg)
            return APIOperationResult(
                success=False,
                operation="test_endpoint",
                url=endpoint,
                message=error_msg,
                error=str(e)
            )
    
    def discover_endpoints(self, base_endpoints: List[str] = None) -> List[str]:
        """Discover API endpoints
        
        Args:
            base_endpoints: List of base endpoints to test
            
        Returns:
            List of discovered endpoints
        """
        if base_endpoints is None:
            base_endpoints = ['/', '/api', '/v1', '/v2', '/docs', '/swagger', '/openapi']
        
        discovered = []
        
        if self.safe_mode:
            logger.warning(f"Safe mode enabled - endpoint discovery would be performed")
            self._log_operation("discover_endpoints", "", False, "Safe mode enabled - operation blocked")
            return discovered
        
        for endpoint in base_endpoints:
            result = self.test_endpoint(endpoint)
            if result.success:
                discovered.append(endpoint)
        
        self._log_operation("discover_endpoints", "", True, f"Discovered {len(discovered)} endpoints")
        
        return discovered
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get request statistics"""
        return {
            'total_requests': self.request_count,
            'last_request_time': self.last_request_time,
            'rate_limit_strategy': self.rate_limit_config.strategy.value,
            'requests_per_minute': self.rate_limit_config.requests_per_minute,
            'requests_per_hour': self.rate_limit_config.requests_per_hour
        }
    
    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Get operation log"""
        return self.operation_log.copy()
    
    def clear_operation_log(self):
        """Clear operation log"""
        self.operation_log.clear()

# Convenience functions
def create_api_client(base_url: str, auth_config: Optional[AuthConfig] = None) -> SpecterAPIClient:
    """Create API client"""
    return SpecterAPIClient(base_url, auth_config)

def test_api_endpoint(base_url: str, endpoint: str, auth_config: Optional[AuthConfig] = None) -> APIOperationResult:
    """Test API endpoint"""
    client = SpecterAPIClient(base_url, auth_config)
    return client.test_endpoint(endpoint)

def make_api_request(base_url: str, method: str, endpoint: str, 
                   data: Optional[Union[Dict[str, Any], str, bytes]] = None,
                   auth_config: Optional[AuthConfig] = None) -> APIOperationResult:
    """Make API request"""
    client = SpecterAPIClient(base_url, auth_config)
    return client._make_request(method, endpoint, data=data)

# Export main classes and functions
__all__ = [
    'SpecterAPIClient', 'AuthMethod', 'RateLimitStrategy', 'AuthConfig', 'RateLimitConfig',
    'APIResponse', 'APIOperationResult', 'create_api_client', 'test_api_endpoint', 'make_api_request'
]
