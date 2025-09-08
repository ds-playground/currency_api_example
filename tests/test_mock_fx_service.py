import unittest
from unittest.mock import patch
from mock_fx_service.app import app
from config.app_config import MOCK_FX_RATES

class TestMockFXService(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_get_rate_success(self):
        # Test each rate in the config
        for pair, rate in MOCK_FX_RATES.items():
            response = self.client.get(f"/rate?ccy_pair={pair}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(float(response.data.decode()), rate)

    def test_get_rate_invalid_pair(self):
        response = self.client.get("/rate?ccy_pair=INVALID")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), "Rate not found")

    def test_get_rate_missing_pair(self):
        response = self.client.get("/rate")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), "Rate not found")

if __name__ == "__main__":
    unittest.main()
