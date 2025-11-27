#!/usr/bin/env python3
"""
Specter Web Scraping Module
Advanced web scraping with anti-detection and browser automation
"""

import requests
import time
import random
import logging
from typing import Optional, List, Dict, Any, Union, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urljoin, urlparse, parse_qs
import re
import json
from bs4 import BeautifulSoup
import threading

logger = logging.getLogger(__name__)

class ScrapingMethod(Enum):
    """Scraping methods"""
    REQUESTS = "requests"
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"

class AntiDetectionLevel(Enum):
    """Anti-detection levels"""
    BASIC = "basic"
    ADVANCED = "advanced"
    STEALTH = "stealth"

@dataclass
class ScrapingConfig:
    """Scraping configuration"""
    method: ScrapingMethod = ScrapingMethod.REQUESTS
    anti_detection: AntiDetectionLevel = AntiDetectionLevel.BASIC
    delay_min: float = 1.0
    delay_max: float = 3.0
    max_retries: int = 3
    timeout: int = 30
    user_agent_rotation: bool = True
    proxy_rotation: bool = False
    javascript_execution: bool = False

@dataclass
class ScrapedData:
    """Scraped data structure"""
    url: str
    title: str
    content: str
    links: List[str]
    images: List[str]
    forms: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: float
    status_code: int

@dataclass
class ScrapingResult:
    """Result of scraping operation"""
    success: bool
    operation: str
    url: str
    message: str
    data: Optional[ScrapedData] = None
    error: Optional[str] = None

class SpecterWebScraper:
    """Advanced web scraper with anti-detection capabilities"""
    
    def __init__(self, config: Optional[ScrapingConfig] = None):
        """Initialize web scraper
        
        Args:
            config: Scraping configuration
        """
        self.config = config or ScrapingConfig()
        self.safe_mode = True  # Always start in safe mode for scraping
        self.session = requests.Session()
        self.operation_log = []
        self.scraped_urls: Set[str] = set()
        
        # Anti-detection setup
        self._setup_anti_detection()
        
    def _setup_anti_detection(self):
        """Setup anti-detection measures"""
        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        # Setup session headers
        self._update_session_headers()
        
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _update_session_headers(self):
        """Update session headers with random values"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.5', 'en-GB,en;q=0.5', 'en-CA,en;q=0.5']),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Add random headers based on anti-detection level
        if self.config.anti_detection in [AntiDetectionLevel.ADVANCED, AntiDetectionLevel.STEALTH]:
            headers.update({
                'DNT': '1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            })
        
        if self.config.anti_detection == AntiDetectionLevel.STEALTH:
            headers.update({
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            })
        
        self.session.headers.update(headers)
    
    def _log_operation(self, operation: str, url: str, success: bool, message: str):
        """Log scraping operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'url': url,
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"Scraping operation: {operation} on {url} - {message}")
    
    def _random_delay(self):
        """Apply random delay between requests"""
        if self.config.delay_min > 0:
            delay = random.uniform(self.config.delay_min, self.config.delay_max)
            time.sleep(delay)
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract links from HTML"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract image URLs from HTML"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, src)
            images.append(absolute_url)
        return images
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form data from HTML"""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'fields': []
            }
            
            # Extract input fields
            for input_field in form.find_all(['input', 'textarea', 'select']):
                field_data = {
                    'name': input_field.get('name', ''),
                    'type': input_field.get('type', 'text'),
                    'value': input_field.get('value', ''),
                    'required': input_field.has_attr('required')
                }
                form_data['fields'].append(field_data)
            
            forms.append(form_data)
        return forms
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from HTML"""
        metadata = {}
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Extract description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            metadata['description'] = desc_tag.get('content', '')
        
        return metadata
    
    def scrape_page(self, url: str, 
                   extract_links: bool = True,
                   extract_images: bool = True,
                   extract_forms: bool = True,
                   extract_metadata: bool = True) -> ScrapingResult:
        """Scrape a single page
        
        Args:
            url: URL to scrape
            extract_links: Extract links from page
            extract_images: Extract images from page
            extract_forms: Extract forms from page
            extract_metadata: Extract metadata from page
            
        Returns:
            ScrapingResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - page scraping would be performed on {url}")
                self._log_operation("scrape_page", url, False, "Safe mode enabled - operation blocked")
                return ScrapingResult(
                    success=False,
                    operation="scrape_page",
                    url=url,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # Apply random delay
            self._random_delay()
            
            # Update headers for request
            if self.config.user_agent_rotation:
                self._update_session_headers()
            
            # Make request with retries
            for attempt in range(self.config.max_retries):
                try:
                    response = self.session.get(url, timeout=self.config.timeout, verify=False)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < self.config.max_retries - 1:
                        logger.warning(f"Scraping attempt {attempt + 1} failed: {e}")
                        time.sleep(self.config.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data
            scraped_data = ScrapedData(
                url=url,
                title=soup.find('title').get_text().strip() if soup.find('title') else '',
                content=soup.get_text(),
                links=self._extract_links(soup, url) if extract_links else [],
                images=self._extract_images(soup, url) if extract_images else [],
                forms=self._extract_forms(soup) if extract_forms else [],
                metadata=self._extract_metadata(soup) if extract_metadata else {},
                timestamp=time.time(),
                status_code=response.status_code
            )
            
            # Track scraped URL
            self.scraped_urls.add(url)
            
            self._log_operation("scrape_page", url, True, f"Page scraped successfully: {response.status_code}")
            
            return ScrapingResult(
                success=True,
                operation="scrape_page",
                url=url,
                message=f"Page scraped successfully: {response.status_code}",
                data=scraped_data
            )
            
        except Exception as e:
            error_msg = f"Page scraping failed: {e}"
            self._log_operation("scrape_page", url, False, error_msg)
            return ScrapingResult(
                success=False,
                operation="scrape_page",
                url=url,
                message=error_msg,
                error=str(e)
            )
    
    def scrape_multiple_pages(self, urls: List[str], 
                            max_concurrent: int = 3,
                            **kwargs) -> List[ScrapingResult]:
        """Scrape multiple pages concurrently
        
        Args:
            urls: List of URLs to scrape
            max_concurrent: Maximum concurrent requests
            **kwargs: Additional arguments for scrape_page
            
        Returns:
            List of ScrapingResult
        """
        results = []
        
        if self.safe_mode:
            logger.warning(f"Safe mode enabled - multiple page scraping would be performed on {len(urls)} URLs")
            for url in urls:
                self._log_operation("scrape_multiple_pages", url, False, "Safe mode enabled - operation blocked")
                results.append(ScrapingResult(
                    success=False,
                    operation="scrape_multiple_pages",
                    url=url,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                ))
            return results
        
        # Use threading for concurrent requests
        threads = []
        results_lock = threading.Lock()
        
        def scrape_worker(url):
            result = self.scrape_page(url, **kwargs)
            with results_lock:
                results.append(result)
        
        # Start threads
        for url in urls:
            while len(threads) >= max_concurrent:
                # Wait for a thread to complete
                threads = [t for t in threads if t.is_alive()]
                time.sleep(0.1)
            
            thread = threading.Thread(target=scrape_worker, args=(url,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        return results
    
    def crawl_site(self, start_url: str, 
                  max_pages: int = 10,
                  max_depth: int = 2,
                  follow_external: bool = False,
                  **kwargs) -> List[ScrapingResult]:
        """Crawl a website starting from a URL
        
        Args:
            start_url: Starting URL
            max_pages: Maximum pages to crawl
            max_depth: Maximum crawl depth
            follow_external: Follow external links
            **kwargs: Additional arguments for scrape_page
            
        Returns:
            List of ScrapingResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - site crawling would be performed from {start_url}")
                self._log_operation("crawl_site", start_url, False, "Safe mode enabled - operation blocked")
                return [ScrapingResult(
                    success=False,
                    operation="crawl_site",
                    url=start_url,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )]
            
            results = []
            visited_urls = set()
            urls_to_visit = [(start_url, 0)]  # (url, depth)
            
            while urls_to_visit and len(results) < max_pages:
                current_url, depth = urls_to_visit.pop(0)
                
                if current_url in visited_urls or depth > max_depth:
                    continue
                
                visited_urls.add(current_url)
                
                # Scrape current page
                result = self.scrape_page(current_url, **kwargs)
                results.append(result)
                
                if result.success and result.data:
                    # Add new URLs to visit
                    for link in result.data.links:
                        parsed_link = urlparse(link)
                        parsed_start = urlparse(start_url)
                        
                        # Check if we should follow this link
                        if follow_external or parsed_link.netloc == parsed_start.netloc:
                            if link not in visited_urls and depth < max_depth:
                                urls_to_visit.append((link, depth + 1))
                
                # Apply delay between requests
                self._random_delay()
            
            self._log_operation("crawl_site", start_url, True, f"Site crawled: {len(results)} pages")
            
            return results
            
        except Exception as e:
            error_msg = f"Site crawling failed: {e}"
            self._log_operation("crawl_site", start_url, False, error_msg)
            return [ScrapingResult(
                success=False,
                operation="crawl_site",
                url=start_url,
                message=error_msg,
                error=str(e)
            )]
    
    def extract_data_by_selector(self, url: str, 
                               css_selectors: Dict[str, str],
                               xpath_selectors: Optional[Dict[str, str]] = None) -> ScrapingResult:
        """Extract specific data using CSS or XPath selectors
        
        Args:
            url: URL to scrape
            css_selectors: Dictionary of {name: css_selector}
            xpath_selectors: Dictionary of {name: xpath_selector}
            
        Returns:
            ScrapingResult with extracted data
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - data extraction would be performed on {url}")
                self._log_operation("extract_data_by_selector", url, False, "Safe mode enabled - operation blocked")
                return ScrapingResult(
                    success=False,
                    operation="extract_data_by_selector",
                    url=url,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            # First scrape the page
            scrape_result = self.scrape_page(url, extract_links=False, extract_images=False, extract_forms=False)
            
            if not scrape_result.success or not scrape_result.data:
                return scrape_result
            
            # Extract data using selectors
            soup = BeautifulSoup(scrape_result.data.content, 'html.parser')
            extracted_data = {}
            
            # CSS selectors
            for name, selector in css_selectors.items():
                elements = soup.select(selector)
                if elements:
                    extracted_data[name] = [elem.get_text().strip() for elem in elements]
                else:
                    extracted_data[name] = []
            
            # XPath selectors (if lxml is available)
            if xpath_selectors:
                try:
                    from lxml import etree, html
                    tree = html.fromstring(scrape_result.data.content)
                    
                    for name, xpath in xpath_selectors.items():
                        elements = tree.xpath(xpath)
                        if elements:
                            extracted_data[f"{name}_xpath"] = [elem.text_content().strip() if hasattr(elem, 'text_content') else str(elem) for elem in elements]
                        else:
                            extracted_data[f"{name}_xpath"] = []
                except ImportError:
                    logger.warning("lxml not available for XPath selectors")
            
            # Update scraped data with extracted information
            scrape_result.data.metadata['extracted_data'] = extracted_data
            
            self._log_operation("extract_data_by_selector", url, True, f"Data extracted using {len(css_selectors)} selectors")
            
            return scrape_result
            
        except Exception as e:
            error_msg = f"Data extraction failed: {e}"
            self._log_operation("extract_data_by_selector", url, False, error_msg)
            return ScrapingResult(
                success=False,
                operation="extract_data_by_selector",
                url=url,
                message=error_msg,
                error=str(e)
            )
    
    def get_scraped_urls(self) -> Set[str]:
        """Get set of scraped URLs"""
        return self.scraped_urls.copy()
    
    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Get operation log"""
        return self.operation_log.copy()
    
    def clear_operation_log(self):
        """Clear operation log"""
        self.operation_log.clear()

# Convenience functions
def scrape_page(url: str, **kwargs) -> ScrapingResult:
    """Scrape a single page"""
    scraper = SpecterWebScraper()
    return scraper.scrape_page(url, **kwargs)

def crawl_site(start_url: str, **kwargs) -> List[ScrapingResult]:
    """Crawl a website"""
    scraper = SpecterWebScraper()
    return scraper.crawl_site(start_url, **kwargs)

def extract_data(url: str, css_selectors: Dict[str, str], **kwargs) -> ScrapingResult:
    """Extract data using CSS selectors"""
    scraper = SpecterWebScraper()
    return scraper.extract_data_by_selector(url, css_selectors, **kwargs)

# Export main classes and functions
__all__ = [
    'SpecterWebScraper', 'ScrapingMethod', 'AntiDetectionLevel', 'ScrapingConfig', 
    'ScrapedData', 'ScrapingResult', 'scrape_page', 'crawl_site', 'extract_data'
]
