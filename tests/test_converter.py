import unittest
from unittest.mock import patch, Mock
from fx_service import get_fx_rate, round_money

class TestCurrencyConverter(unittest.TestCase):
    """Unit tests for currency conversion logic."""

    @patch("fx_service.requests.get")
    def test_get_fx_rate_direct_pair(self, mock_get):
        mock_response = Mock()
        mock_response.text = "1.28"  # GBPUSD
        mock_get.return_value = mock_response

        rate = get_fx_rate("GBP", "USD")
        self.assertEqual(rate, 1.28)

    @patch("fx_service.requests.get")
    def test_get_fx_rate_inverse_pair(self, mock_get):
        mock_response = Mock()
        mock_response.text = "1.28"  # GBPUSD
        mock_get.return_value = mock_response

        rate = get_fx_rate("USD", "GBP")
        self.assertAlmostEqual(rate, 1 / 1.28)

    @patch("fx_service.requests.get")
    def test_get_fx_rate_triangulation(self, mock_get):
        mock_response_1 = Mock()
        mock_response_1.text = "1.10"  # EURUSD

        mock_response_2 = Mock()
        mock_response_2.text = "1.25"  # USDCAD

        mock_get.side_effect = [mock_response_1, mock_response_2]

        rate = get_fx_rate("EUR", "CAD")
        self.assertAlmostEqual(rate, 1.10 * 1.25)

    @patch("fx_service.requests.get")
    def test_get_fx_rate_unsupported_pair(self, mock_get):
        with self.assertRaises(ValueError) as context:
            get_fx_rate("GBP", "CHF")  # Not in DIRECT_PAIRS and can't triangulate
        self.assertIn("Unsupported currency pair", str(context.exception))

    def test_round_money_half_up(self):
        self.assertEqual(round_money(110.345), 110.35)
        self.assertEqual(round_money(110.344), 110.34)
        self.assertEqual(round_money(-1.145), -1.15)
        self.assertEqual(round_money(-1.144), -1.14)

if __name__ == "__main__":
    unittest.main()
