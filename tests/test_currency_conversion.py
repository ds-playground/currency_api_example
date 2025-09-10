import unittest
from decimal import Decimal
from services.currency_conversion_service import CurrencyConversionService
from services.currency_rounder import CurrencyRounder
from config.app_config import ROUNDING_PRECISION

class TestCurrencyConversion(unittest.TestCase):
    def setUp(self):
        self.fx_rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.73
        }
        self.converter = CurrencyConversionService(self.fx_rates)

    def test_same_currency_conversion(self):
        result = self.converter.convert("USD", "USD", 100)
        self.assertEqual(result, 100)

    def test_direct_currency_conversion(self):
        # Convert USD to EUR
        result = self.converter.convert("USD", "EUR", 100)
        expected = 100 * (self.fx_rates["EUR"] / self.fx_rates["USD"])
        self.assertEqual(result, expected)

    def test_reverse_currency_conversion(self):
        # Convert EUR to USD
        result = self.converter.convert("EUR", "USD", 100)
        expected = 100 * (self.fx_rates["USD"] / self.fx_rates["EUR"])
        self.assertEqual(result, expected)

    def test_cross_currency_conversion(self):
        # Convert EUR to GBP
        result = self.converter.convert("EUR", "GBP", 100)
        expected = 100 * (self.fx_rates["GBP"] / self.fx_rates["EUR"])
        self.assertEqual(result, expected)

    def test_invalid_currency_pair(self):
        with self.assertRaises(ValueError) as context:
            self.converter.convert("XXX", "USD", 100)
        self.assertEqual(str(context.exception), "No exchange rate found for XXX")

class TestCurrencyRounding(unittest.TestCase):
    def test_rounding_precision(self):
        value = 123.4567
        rounded = CurrencyRounder.round(value)
        self.assertEqual(rounded, round(value, ROUNDING_PRECISION))

    def test_rounding_up(self):
        self.assertEqual(CurrencyRounder.round(1.555), 1.56)
        self.assertEqual(CurrencyRounder.round(1.565), 1.57)

    def test_rounding_down(self):
        self.assertEqual(CurrencyRounder.round(1.554), 1.55)
        self.assertEqual(CurrencyRounder.round(1.544), 1.54)

    def test_negative_values(self):
        self.assertEqual(CurrencyRounder.round(-1.555), -1.56)
        self.assertEqual(CurrencyRounder.round(-1.544), -1.54)

    def test_custom_precision(self):
        value = 123.4567
        precision = 3
        self.assertEqual(CurrencyRounder.round(value, precision), round(value, precision))

class TestDecimalQuantization(unittest.TestCase):
    def test_quantize_decimal_standard_case(self):
        """Test standard decimal quantization with 2 decimal places"""
        value = Decimal('123.4567')
        result = CurrencyRounder._quantize_decimal(value, 2)
        self.assertEqual(str(result), '123.46')

    def test_quantize_decimal_higher_precision(self):
        """Test quantization with higher precision (4 decimal places)"""
        value = Decimal('123.45678')
        result = CurrencyRounder._quantize_decimal(value, 4)
        self.assertEqual(str(result), '123.4568')

    def test_quantize_decimal_zero_precision(self):
        """Test quantization with zero decimal places (rounding to integer)"""
        value = Decimal('123.6')
        result = CurrencyRounder._quantize_decimal(value, 0)
        self.assertEqual(str(result), '124')

    def test_quantize_decimal_exact_value(self):
        """Test quantization when value already has exact precision"""
        value = Decimal('123.45')
        result = CurrencyRounder._quantize_decimal(value, 2)
        self.assertEqual(str(result), '123.45')

    def test_quantize_decimal_negative_values(self):
        """Test quantization with negative values"""
        value = Decimal('-123.456')
        result = CurrencyRounder._quantize_decimal(value, 2)
        self.assertEqual(str(result), '-123.46')

    def test_quantize_decimal_midpoint_rounding(self):
        """Test midpoint rounding behavior (half-up)"""
        test_cases = [
            ('1.5', 0, '2'),     # 1.5 rounds up to 2
            ('2.5', 0, '3'),     # 2.5 rounds up to 3
            ('1.25', 1, '1.3'),  # 1.25 rounds up to 1.3
            ('1.35', 1, '1.4'),  # 1.35 rounds up to 1.4
        ]
        
        for value, precision, expected in test_cases:
            with self.subTest(value=value, precision=precision):
                result = CurrencyRounder._quantize_decimal(Decimal(value), precision)
                self.assertEqual(str(result), expected)

if __name__ == "__main__":
    unittest.main()
