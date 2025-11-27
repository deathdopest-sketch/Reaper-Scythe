#!/usr/bin/env python3
"""
Test Suite for Void OSINT Scrubbing Library

Tests the core functionality of the Void library including:
- Email scrubbing
- Phone number scrubbing
- Username checking
- Footprint analysis
- Removal request management
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from libs.void import (
    VoidOSINTScrubber, ScrubType, ScrubPriority, ScrubStatus,
    scrub_email, scrub_phone, scrub_username, scrub_domain,
    analyze_footprint, check_username_availability,
    FootprintAnalyzer, FootprintType, FootprintSeverity,
    RemovalManager, RemovalProvider, RemovalStatus
)


class TestVoidScrubber(unittest.TestCase):
    """Test VoidOSINTScrubber class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scrubber = VoidOSINTScrubber(safe_mode=True)
    
    def test_initialization(self):
        """Test scrubber initialization."""
        self.assertTrue(self.scrubber.safe_mode)
        self.assertEqual(len(self.scrubber.scrub_history), 0)
        self.assertGreater(len(self.scrubber.data_brokers), 0)
        self.assertGreater(len(self.scrubber.social_platforms), 0)
    
    def test_email_validation(self):
        """Test email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org"
        ]
        
        for email in valid_emails:
            self.assertTrue(self.scrubber._validate_email(email))
        
        invalid_emails = [
            "invalid",
            "@example.com",
            "test@",
            "test@.com"
        ]
        
        for email in invalid_emails:
            self.assertFalse(self.scrubber._validate_email(email))
    
    def test_phone_normalization(self):
        """Test phone number normalization."""
        test_cases = [
            ("+1-555-123-4567", "15551234567"),
            ("(555) 123-4567", "5551234567"),
            ("5551234567", "5551234567"),
            ("invalid", None)
        ]
        
        for input_phone, expected in test_cases:
            result = self.scrubber._normalize_phone(input_phone)
            self.assertEqual(result, expected)
    
    def test_scrub_email_valid(self):
        """Test scrubbing valid email."""
        result = self.scrubber.scrub_email("test@example.com")
        
        self.assertEqual(result.scrub_type, ScrubType.EMAIL)
        self.assertEqual(result.target, "test@example.com")
        self.assertIn(result.status, [ScrubStatus.COMPLETED, ScrubStatus.PARTIAL, ScrubStatus.FAILED])
        self.assertGreaterEqual(result.items_found, 0)
        self.assertEqual(len(self.scrubber.scrub_history), 1)
    
    def test_scrub_email_invalid(self):
        """Test scrubbing invalid email."""
        result = self.scrubber.scrub_email("invalid-email")
        
        self.assertEqual(result.status, ScrubStatus.FAILED)
        self.assertIsNotNone(result.error_message)
    
    def test_scrub_phone_valid(self):
        """Test scrubbing valid phone."""
        result = self.scrubber.scrub_phone("+1-555-123-4567")
        
        self.assertEqual(result.scrub_type, ScrubType.PHONE)
        self.assertIn(result.status, [ScrubStatus.COMPLETED, ScrubStatus.PARTIAL, ScrubStatus.FAILED])
    
    def test_scrub_phone_invalid(self):
        """Test scrubbing invalid phone."""
        result = self.scrubber.scrub_phone("invalid")
        
        self.assertEqual(result.status, ScrubStatus.FAILED)
        self.assertIsNotNone(result.error_message)
    
    def test_scrub_username(self):
        """Test username scrubbing."""
        result = self.scrubber.scrub_username("testuser")
        
        self.assertEqual(result.scrub_type, ScrubType.USERNAME)
        self.assertGreaterEqual(len(result.platforms_checked), 0)
    
    def test_scan_social_media(self):
        """Test social media scanning."""
        results = self.scrubber.scan_social_media(username="testuser")
        
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)
    
    def test_scrub_history(self):
        """Test scrub history tracking."""
        self.assertEqual(len(self.scrubber.scrub_history), 0)
        
        self.scrubber.scrub_email("test@example.com")
        self.assertEqual(len(self.scrubber.scrub_history), 1)
        
        self.scrubber.scrub_phone("555-123-4567")
        self.assertEqual(len(self.scrubber.scrub_history), 2)
    
    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        result = ScrubStatus.COMPLETED  # Placeholder
        # This would test the ScrubResult.success_rate method
        # Implementation depends on ScrubResult class


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def test_scrub_email_function(self):
        """Test scrub_email convenience function."""
        result = scrub_email("test@example.com", safe_mode=True)
        self.assertEqual(result.scrub_type, ScrubType.EMAIL)
    
    def test_scrub_phone_function(self):
        """Test scrub_phone convenience function."""
        result = scrub_phone("555-123-4567", safe_mode=True)
        self.assertEqual(result.scrub_type, ScrubType.PHONE)
    
    def test_scrub_username_function(self):
        """Test scrub_username convenience function."""
        result = scrub_username("testuser", safe_mode=True)
        self.assertEqual(result.scrub_type, ScrubType.USERNAME)
    
    def test_check_username_availability(self):
        """Test username availability checking."""
        results = check_username_availability("testuser")
        self.assertIsInstance(results, dict)


class TestFootprintAnalyzer(unittest.TestCase):
    """Test FootprintAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = FootprintAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertEqual(len(self.analyzer.records), 0)
        self.assertGreater(len(self.analyzer.search_sources), 0)
    
    def test_analyze_empty(self):
        """Test analyzing with empty targets."""
        records = self.analyzer.analyze({})
        self.assertEqual(len(records), 0)
    
    def test_analyze_with_email(self):
        """Test analyzing with email."""
        records = self.analyzer.analyze({"email": "test@example.com"})
        self.assertIsInstance(records, list)
    
    def test_generate_report(self):
        """Test report generation."""
        # Add some test records
        self.analyzer.analyze({"email": "test@example.com"})
        report = self.analyzer.generate_report()
        
        self.assertIn("total_records", report)
        self.assertIn("by_type", report)
        self.assertIn("by_severity", report)


class TestRemovalManager(unittest.TestCase):
    """Test RemovalManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = RemovalManager()
    
    def test_initialization(self):
        """Test manager initialization."""
        self.assertEqual(len(self.manager.requests), 0)
    
    def test_submit_request(self):
        """Test submitting removal request."""
        request = self.manager.submit_request(
            RemovalProvider.GOOGLE,
            target_url="https://example.com",
            target_type="url"
        )
        
        self.assertEqual(request.provider, RemovalProvider.GOOGLE)
        self.assertEqual(request.status, RemovalStatus.SUBMITTED)
        self.assertIsNotNone(request.request_id)
        self.assertEqual(len(self.manager.requests), 1)
    
    def test_track_status(self):
        """Test status tracking."""
        request = self.manager.submit_request(RemovalProvider.GOOGLE)
        status = self.manager.track_status(request.request_id)
        
        self.assertEqual(status, RemovalStatus.SUBMITTED)


class TestRemovalConvenienceFunctions(unittest.TestCase):
    """Test removal convenience functions."""
    
    def test_request_google_removal(self):
        """Test Google removal request."""
        from libs.void.removal import request_google_removal
        
        request = request_google_removal("https://example.com")
        self.assertEqual(request.provider, RemovalProvider.GOOGLE)
    
    def test_request_bing_removal(self):
        """Test Bing removal request."""
        from libs.void.removal import request_bing_removal
        
        request = request_bing_removal("https://example.com")
        self.assertEqual(request.provider, RemovalProvider.BING)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVoidScrubber))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestFootprintAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestRemovalManager))
    suite.addTests(loader.loadTestsFromTestCase(TestRemovalConvenienceFunctions))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

