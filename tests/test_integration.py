
import unittest
from unittest.mock import patch, Mock
from app import app
from fx_service import round_money

class TestCurrencyConversionIntegration(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch("fx_service.requests.get")
    def test_convert_eurusd_success(self, mock_get):
        # Simulate FX rate API response
        mock_response = Mock()
        mock_response.text = "1.10"
        mock_get.return_value = mock_response

        payload = {
            "ccy_from": "EUR",
            "ccy_to": "USD",
            "quantity": 100
        }

        expected = round_money(100 * 1.10)

        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"quantity": expected, "ccy": "USD"})

    @patch("fx_service.requests.get")
    def test_convert_triangulated_pair(self, mock_get):
        # Simulate EURUSD and USDCAD
        mock_response_eurusd = Mock()
        mock_response_eurusd.text = "1.10"

        mock_response_usdcad = Mock()
        mock_response_usdcad.text = "1.25"

        mock_get.side_effect = [mock_response_eurusd, mock_response_usdcad]

        payload = {
            "ccy_from": "EUR",
            "ccy_to": "CAD",
            "quantity": 100
        }

        expected = round_money(100 * 1.10 * 1.25)

        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"quantity": expected, "ccy": "CAD"})

    @patch("fx_service.requests.get")
    def test_convert_invalid_quantity(self, mock_get):
        mock_get.return_value.text = "1.10"

        payload = {
            "ccy_from": "EUR",
            "ccy_to": "USD",
            "quantity": "invalid"
        }

        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    @patch("fx_service.requests.get")
    def test_convert_negative_quantity(self, mock_get):
        mock_get.return_value.text = "1.10"

        payload = {
            "ccy_from": "EUR",
            "ccy_to": "USD",
            "quantity": -100
        }

        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Quantity must be non-negative")

if __name__ == "__main__":
    unittest.main()
