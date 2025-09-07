import unittest
from unittest.mock import patch
from app import app
from fx_service import round_money

class TestCurrencyConversionEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch("fx_service.get_fx_rate")
    def test_convert_endpoint_success(self, mock_get_fx_rate):
        mock_get_fx_rate.return_value = 1.10
        payload = {"ccy_from": "EUR", "ccy_to": "USD", "quantity": 100}
        expected = round_money(100 * 1.10)

        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"quantity": expected, "ccy": "USD"})

    @patch("fx_service.get_fx_rate")
    def test_convert_endpoint_rounding(self, mock_get_fx_rate):
        mock_get_fx_rate.return_value = 1.10345
        payload = {"ccy_from": "EUR", "ccy_to": "USD", "quantity": 100}
        expected = round_money(100 * 1.10345)

        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"quantity": expected, "ccy": "USD"})

    @patch("fx_service.get_fx_rate")
    def test_convert_endpoint_zero_quantity(self, mock_get_fx_rate):
        mock_get_fx_rate.return_value = 1.25
        payload = {"ccy_from": "USD", "ccy_to": "CAD", "quantity": 0}
        expected = round_money(0 * 1.25)

        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"quantity": expected, "ccy": "CAD"})

    @patch("fx_service.get_fx_rate")
    def test_convert_endpoint_negative_quantity(self, mock_get_fx_rate):
        mock_get_fx_rate.return_value = 1.25
        payload = {"ccy_from": "USD", "ccy_to": "CAD", "quantity": -100}

        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())
        self.assertEqual(response.get_json()["error"], "Quantity must be non-negative")

    @patch("fx_service.get_fx_rate")
    def test_convert_endpoint_non_numeric_quantity(self, mock_get_fx_rate):
        mock_get_fx_rate.return_value = 1.10
        payload = {"ccy_from": "EUR", "ccy_to": "USD", "quantity": "one hundred"}

        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_convert_endpoint_missing_fields(self):
        payload = {"ccy_from": "EUR", "quantity": 100}
        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    @patch("fx_service.get_fx_rate")
    def test_convert_endpoint_unsupported_currency(self, mock_get_fx_rate):
        mock_get_fx_rate.side_effect = ValueError("Unsupported currency pair")
        payload = {"ccy_from": "GBP", "ccy_to": "CHF", "quantity": 100}

        response = self.client.post("/convert", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())
        self.assertEqual(response.get_json()["error"], "Unsupported currency pair")

if __name__ == "__main__":
    unittest.main()
