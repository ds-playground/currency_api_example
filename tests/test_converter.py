
import unittest
from unittest.mock import patch
from fx_service import get_fx_rate

class TestCurrencyConverter(unittest.TestCase):
    """Unit tests for currency conversion logic."""

    @patch("requests.get")
    def test_direct_conversion(self, mock_get):
        mock_get.return_value.text = "1.28"
        rate = get_fx_rate("GBP", "USD")
        self.assertEqual(rate, 1.28)

    @patch("requests.get")
    def test_inverse_conversion(self, mock_get):
        mock_get.return_value.text = "1.28"
        rate = get_fx_rate("USD", "GBP")
        self.assertAlmostEqual(rate, 1/1.28)

    @patch("requests.get")
    def test_triangulation(self, mock_get):
        def side_effect(url):
            if "GBPUSD" in url:
                return type("Response", (), {"text": "1.28"})()
            elif "USDCAD" in url:
                return type("Response", (), {"text": "1.25"})()
        mock_get.side_effect = side_effect
        rate = get_fx_rate("GBP", "CAD")
        self.assertAlmostEqual(rate, 1.28 * 1.25)

if __name__ == "__main__":
    unittest.main()
