
import unittest
import requests

class TestMockFXService(unittest.TestCase):
    """Integration test for mock FX rate service."""

    def test_get_rate(self):
        response = requests.get("http://localhost:5001/rate?ccy_pair=EURUSD")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.text), 1.10)

if __name__ == "__main__":
    unittest.main()
