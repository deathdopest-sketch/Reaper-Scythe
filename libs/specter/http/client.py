#!/usr/bin/env python3
"""
Specter HTTP Operations Module
Advanced HTTP client with custom headers, session management, and stealth features
"""

import requests
import time
import random
import logging
from typing import Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urljoin, urlparse
import ssl
import socket

logger = logging.getLogger(__name__)

class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"

class ProxyType(Enum):
    """Proxy types"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"

@dataclass
class ProxyConfig:
    """Proxy configuration"""
    host: str
    port: int
    proxy_type: ProxyType
    username: Optional[str] = None
    password: Optional[str] = None

@dataclass
class HTTPResponse:
    """HTTP response data"""
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    url: str
    elapsed_time: float
    cookies: Dict[str, str]
    encoding: str

@dataclass
class HTTPOperationResult:
    """Result of HTTP operation"""
    success: bool
    operation: str
    url: str
    message: str
    response: Optional[HTTPResponse] = None
    error: Optional[str] = None

class SpecterHTTPClient:
    """Advanced HTTP client with stealth and security features"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize HTTP client
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.safe_mode = self.config.get('safe_mode', True)
        self.user_agents = self.config.get('user_agents', self._get_default_user_agents())
        self.timeout = self.config.get('timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1)
        self.operation_log = []
        
        # Session management
        self.session = requests.Session()
        self._setup_session()
        
    def _get_default_user_agents(self) -> List[str]:
        """Get default user agents for rotation"""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
    
    def _setup_session(self):
        """Setup session with default configuration"""
        # Set default headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Set timeout
        self.session.timeout = self.timeout
        
        # Disable SSL verification warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _log_operation(self, operation: str, url: str, success: bool, message: str):
        """Log HTTP operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'url': url,
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"HTTP operation: {operation} on {url} - {message}")
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.user_agents)
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Get random headers to avoid detection"""
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': random.choice([
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            ]),
            'Accept-Language': random.choice([
                'en-US,en;q=0.5',
                'en-US,en;q=0.9',
                'en-GB,en;q=0.5',
                'en-CA,en;q=0.5'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': random.choice(['1', '0']),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Randomly add some optional headers
        if random.random() < 0.3:
            headers['Cache-Control'] = 'no-cache'
        if random.random() < 0.2:
            headers['Pragma'] = 'no-cache'
        
        return headers
    
    def set_proxy(self, proxy_config: ProxyConfig) -> HTTPOperationResult:
        """Set proxy configuration
        
        Args:
            proxy_config: Proxy configuration
            
        Returns:
            HTTPOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - proxy configuration would be set")
                self._log_operation("set_proxy", "", False, "Safe mode enabled - operation blocked")
                return HTTPOperationResult(
                    success=False,
                    operation="set_proxy",
                    url="",
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Build proxy URL
            if proxy_config.username and proxy_config.password:
                proxy_url = f"{proxy_config.proxy_type.value}://{proxy_config.username}:{proxy_config.password}@{proxy_config.host}:{proxy_config.port}"
            else:
                proxy_url = f"{proxy_config.proxy_type.value}://{proxy_config.host}:{proxy_config.port}"
            
            # Set proxy
            self.session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            self._log_operation("set_proxy", proxy_url, True, "Proxy configured successfully")
            
            return HTTPOperationResult(
                success=True,
                operation="set_proxy",
                url=proxy_url,
                message="Proxy configured successfully"
            )
            
        except Exception as e:
            error_msg = f"Proxy configuration failed: {e}"
            self._log_operation("set_proxy", "", False, error_msg)
            return HTTPOperationResult(
                success=False,
                operation="set_proxy",
                url="",
                message=error_msg,
                error=str(e)
            )
    
    def request(self, method: HTTPMethod, url: str, 
                headers: Optional[Dict[str, str]] = None,
                data: Optional[Union[str, Dict[str, Any], bytes]] = None,
                params: Optional[Dict[str, Any]] = None,
                cookies: Optional[Dict[str, str]] = None,
                timeout: Optional[int] = None,
                allow_redirects: bool = True,
                verify_ssl: bool = False,
                use_random_headers: bool = True) -> HTTPOperationResult:
        """Make HTTP request
        
        Args:
            method: HTTP method
            url: Target URL
            headers: Custom headers
            data: Request data
            params: URL parameters
            cookies: Cookies to send
            timeout: Request timeout
            allow_redirects: Allow redirects
            verify_ssl: Verify SSL certificates
            use_random_headers: Use random headers for stealth
            
        Returns:
            HTTPOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - HTTP request would be made to {url}")
                self._log_operation("request", url, False, "Safe mode enabled - operation blocked")
                return HTTPOperationResult(
                    success=False,
                    operation="request",
                    url=url,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Prepare headers
            request_headers = {}
            if use_random_headers:
                request_headers.update(self._get_random_headers())
            if headers:
                request_headers.update(headers)
            
            # Set cookies
            if cookies:
                for name, value in cookies.items():
                    self.session.cookies.set(name, value)
            
            # Make request with retries
            for attempt in range(self.max_retries + 1):
                try:
                    start_time = time.time()
                    
                    response = self.session.request(
                        method=method.value,
                        url=url,
                        headers=request_headers,
                        data=data,
                        params=params,
                        timeout=timeout or self.timeout,
                        allow_redirects=allow_redirects,
                        verify=verify_ssl
                    )
                    
                    elapsed_time = time.time() - start_time
                    
                    # Create response object
                    http_response = HTTPResponse(
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        content=response.content,
                        text=response.text,
                        url=response.url,
                        elapsed_time=elapsed_time,
                        cookies=dict(response.cookies),
                        encoding=response.encoding
                    )
                    
                    self._log_operation("request", url, True, f"Request successful: {response.status_code}")
                    
                    return HTTPOperationResult(
                        success=True,
                        operation="request",
                        url=url,
                        message=f"Request successful: {response.status_code}",
                        response=http_response
                    )
                    
                except requests.exceptions.RequestException as e:
                    if attempt < self.max_retries:
                        logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise
            
        except Exception as e:
            error_msg = f"HTTP request failed: {e}"
            self._log_operation("request", url, False, error_msg)
            return HTTPOperationResult(
                success=False,
                operation="request",
                url=url,
                message=error_msg,
                error=str(e)
            )
    
    def get(self, url: str, **kwargs) -> HTTPOperationResult:
        """Make GET request"""
        return self.request(HTTPMethod.GET, url, **kwargs)
    
    def post(self, url: str, data: Optional[Union[str, Dict[str, Any], bytes]] = None, **kwargs) -> HTTPOperationResult:
        """Make POST request"""
        return self.request(HTTPMethod.POST, url, data=data, **kwargs)
    
    def put(self, url: str, data: Optional[Union[str, Dict[str, Any], bytes]] = None, **kwargs) -> HTTPOperationResult:
        """Make PUT request"""
        return self.request(HTTPMethod.PUT, url, data=data, **kwargs)
    
    def delete(self, url: str, **kwargs) -> HTTPOperationResult:
        """Make DELETE request"""
        return self.request(HTTPMethod.DELETE, url, **kwargs)
    
    def head(self, url: str, **kwargs) -> HTTPOperationResult:
        """Make HEAD request"""
        return self.request(HTTPMethod.HEAD, url, **kwargs)
    
    def options(self, url: str, **kwargs) -> HTTPOperationResult:
        """Make OPTIONS request"""
        return self.request(HTTPMethod.OPTIONS, url, **kwargs)
    
    def patch(self, url: str, data: Optional[Union[str, Dict[str, Any], bytes]] = None, **kwargs) -> HTTPOperationResult:
        """Make PATCH request"""
        return self.request(HTTPMethod.PATCH, url, data=data, **kwargs)
    
    def download_file(self, url: str, file_path: str, 
                     chunk_size: int = 8192) -> HTTPOperationResult:
        """Download file from URL
        
        Args:
            url: File URL
            file_path: Local file path
            chunk_size: Chunk size for download
            
        Returns:
            HTTPOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - file download would be performed from {url}")
                self._log_operation("download_file", url, False, "Safe mode enabled - operation blocked")
                return HTTPOperationResult(
                    success=False,
                    operation="download_file",
                    url=url,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Make request with stream
            response = self.session.get(url, stream=True, verify=False)
            response.raise_for_status()
            
            # Download file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            
            self._log_operation("download_file", url, True, f"File downloaded to {file_path}")
            
            return HTTPOperationResult(
                success=True,
                operation="download_file",
                url=url,
                message=f"File downloaded successfully to {file_path}"
            )
            
        except Exception as e:
            error_msg = f"File download failed: {e}"
            self._log_operation("download_file", url, False, error_msg)
            return HTTPOperationResult(
                success=False,
                operation="download_file",
                url=url,
                message=error_msg,
                error=str(e)
            )
    
    def upload_file(self, url: str, file_path: str, 
                   field_name: str = 'file',
                   additional_data: Optional[Dict[str, Any]] = None) -> HTTPOperationResult:
        """Upload file to URL
        
        Args:
            url: Upload URL
            file_path: Local file path
            field_name: Form field name
            additional_data: Additional form data
            
        Returns:
            HTTPOperationResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - file upload would be performed to {url}")
                self._log_operation("upload_file", url, False, "Safe mode enabled - operation blocked")
                return HTTPOperationResult(
                    success=False,
                    operation="upload_file",
                    url=url,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Prepare files and data
            files = {field_name: open(file_path, 'rb')}
            data = additional_data or {}
            
            try:
                response = self.session.post(url, files=files, data=data, verify=False)
                response.raise_for_status()
                
                # Create response object
                http_response = HTTPResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    content=response.content,
                    text=response.text,
                    url=response.url,
                    elapsed_time=0,  # Not measured for uploads
                    cookies=dict(response.cookies),
                    encoding=response.encoding
                )
                
                self._log_operation("upload_file", url, True, f"File uploaded successfully: {response.status_code}")
                
                return HTTPOperationResult(
                    success=True,
                    operation="upload_file",
                    url=url,
                    message=f"File uploaded successfully: {response.status_code}",
                    response=http_response
                )
                
            finally:
                files[field_name].close()
            
        except Exception as e:
            error_msg = f"File upload failed: {e}"
            self._log_operation("upload_file", url, False, error_msg)
            return HTTPOperationResult(
                success=False,
                operation="upload_file",
                url=url,
                message=error_msg,
                error=str(e)
            )
    
    def get_cookies(self) -> Dict[str, str]:
        """Get current cookies"""
        return dict(self.session.cookies)
    
    def set_cookies(self, cookies: Dict[str, str]):
        """Set cookies"""
        for name, value in cookies.items():
            self.session.cookies.set(name, value)
    
    def clear_cookies(self):
        """Clear all cookies"""
        self.session.cookies.clear()
    
    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Get operation log"""
        return self.operation_log.copy()
    
    def clear_operation_log(self):
        """Clear operation log"""
        self.operation_log.clear()

# Convenience functions
def make_request(method: HTTPMethod, url: str, **kwargs) -> HTTPOperationResult:
    """Make HTTP request"""
    client = SpecterHTTPClient()
    return client.request(method, url, **kwargs)

def get_url(url: str, **kwargs) -> HTTPOperationResult:
    """Make GET request"""
    client = SpecterHTTPClient()
    return client.get(url, **kwargs)

def post_data(url: str, data: Optional[Union[str, Dict[str, Any], bytes]] = None, **kwargs) -> HTTPOperationResult:
    """Make POST request"""
    client = SpecterHTTPClient()
    return client.post(url, data=data, **kwargs)

def download_file(url: str, file_path: str, **kwargs) -> HTTPOperationResult:
    """Download file"""
    client = SpecterHTTPClient()
    return client.download_file(url, file_path, **kwargs)

# Export main classes and functions
__all__ = [
    'SpecterHTTPClient', 'HTTPMethod', 'ProxyType', 'ProxyConfig', 'HTTPResponse', 'HTTPOperationResult',
    'make_request', 'get_url', 'post_data', 'download_file'
]
