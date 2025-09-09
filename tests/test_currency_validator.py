import unittest
from services.currency_validator import CurrencyValidator
from config.app_config import SUPPORTED_CURRENCIES, MOCK_FX_RATES

class TestCurrencyValidator(unittest.TestCase):
    def test_direct_mock_rate_pair(self):
        # Should not raise an exception for pairs in MOCK_FX_RATES
        CurrencyValidator.validate("EUR", "USD")  # EURUSD in MOCK_FX_RATES
        CurrencyValidator.validate("GBP", "USD")  # GBPUSD in MOCK_FX_RATES
        CurrencyValidator.validate("USD", "JPY")  # USDJPY in MOCK_FX_RATES

    def test_inverse_mock_rate_pair(self):
        # Should not raise an exception for inverse of pairs in MOCK_FX_RATES
        CurrencyValidator.validate("USD", "EUR")  # Inverse of EURUSD
        CurrencyValidator.validate("USD", "GBP")  # Inverse of GBPUSD
        CurrencyValidator.validate("JPY", "USD")  # Inverse of USDJPY

    def test_supported_currency_fallback(self):
        # Should not raise an exception for supported currencies even if not in MOCK_FX_RATES
        for ccy_from in SUPPORTED_CURRENCIES:
            for ccy_to in SUPPORTED_CURRENCIES:
                if ccy_from != ccy_to:  # Skip same currency pairs
                    try:
                        CurrencyValidator.validate(ccy_from, ccy_to)
                    except ValueError as e:
                        self.fail(f"Validation failed for {ccy_from}/{ccy_to}: {str(e)}")

    def test_invalid_currency_not_in_mock_or_supported(self):
        # Should raise error for currencies not in MOCK_FX_RATES or SUPPORTED_CURRENCIES
        with self.assertRaises(ValueError) as context:
            CurrencyValidator.validate("XXX", "USD")
        self.assertEqual(str(context.exception), "Unsupported source currency: XXX")

        with self.assertRaises(ValueError) as context:
            CurrencyValidator.validate("USD", "XXX")
        self.assertEqual(str(context.exception), "Unsupported target currency: XXX")

    def test_same_currency(self):
        # Should not raise an exception when converting to same currency
        for currency in SUPPORTED_CURRENCIES:
            CurrencyValidator.validate(currency, currency)

if __name__ == "__main__":
    unittest.main()
