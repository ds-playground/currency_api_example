
import unittest
from unittest.mock import patch
import requests
import sys
import os

# Add the root directory to Python path to find config module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config.app_config import MOCK_FX_RATES

class TestMockFXService(unittest.TestCase):
    """Integration test for mock FX rate service."""
    
    def setUp(self):
        self.base_url = "http://localhost:5001/rate"

    def test_get_all_configured_rates(self):
        """Test that all rates defined in MOCK_FX_RATES are accessible"""
        for ccy_pair, expected_rate in MOCK_FX_RATES.items():
            with self.subTest(ccy_pair=ccy_pair):
                response = requests.get(f"{self.base_url}?ccy_pair={ccy_pair}")
                self.assertEqual(response.status_code, 200, f"Failed to get rate for {ccy_pair}")
                self.assertEqual(float(response.text), expected_rate, 
                               f"Rate mismatch for {ccy_pair}")

    def test_invalid_currency_pair(self):
        """Test handling of invalid currency pairs"""
        invalid_pairs = ["INVALID", "USD", "USDEUR0", "USD/EUR", "ABCDEF"]
        for pair in invalid_pairs:
            with self.subTest(pair=pair):
                response = requests.get(f"{self.base_url}?ccy_pair={pair}")
                self.assertIn(response.status_code, [400, 404],
                               f"Expected 400 or 404 for invalid pair {pair}")

    def test_missing_currency_pair(self):
        """Test handling of missing currency pair parameter"""
        response = requests.get(self.base_url)
        self.assertEqual(response.status_code, 400,
                        "Expected 400 when currency pair is missing")

if __name__ == "__main__":
    unittest.main()
