import pytest
from decimal import Decimal
from services.currency_rounder import CurrencyRounder
from config.app_config import ROUNDING_PRECISION

class TestCurrencyRounder:
    @pytest.mark.parametrize("value,decimals,expected", [
        (Decimal('1.234'), 2, Decimal('1.23')),
        (Decimal('1.235'), 2, Decimal('1.24')),  # Test rounding up
        (Decimal('-1.235'), 2, Decimal('-1.24')), # Test negative numbers
        (Decimal('1.2345'), 3, Decimal('1.235')),
        (Decimal('0'), 2, Decimal('0.00')),
        (Decimal('1.5'), 0, Decimal('2')),  # Test whole number rounding
    ])
    def test_quantize_decimal(self, value, decimals, expected):
        """Test decimal quantization with various inputs"""
        result = CurrencyRounder._quantize_decimal(value, decimals)
        assert result == expected
        assert isinstance(result, Decimal)

    @pytest.mark.parametrize("value,expected", [
        (1.234, 1.23),
        (1.235, 1.24),  # Test rounding up
        (-1.235, -1.24),  # Test negative numbers
        (1.2345, 1.23),  # Test extra precision
        (0, 0.00),  # Test zero
        (1.5, 1.50),  # Test adding decimal places
    ])
    def test_round_with_default_precision(self, value, expected):
        """Test public round method with default precision"""
        result = CurrencyRounder.round(value)
        assert result == expected
        assert isinstance(result, float)

    @pytest.mark.parametrize("value,decimals,expected", [
        (1.234, 3, 1.234),
        (1.2345, 3, 1.235),
        (-1.2345, 3, -1.235),
        (1.5, 0, 2),
        (1.4, 0, 1),
    ])
    def test_round_with_custom_precision(self, value, decimals, expected):
        """Test public round method with custom precision"""
        result = CurrencyRounder.round(value, decimals)
        assert result == expected
        assert isinstance(result, float)

    @pytest.mark.parametrize("value", [
        "not a number",
        None,
        [],
        {},
    ])
    def test_round_invalid_value(self, value):
        """Test handling of invalid values"""
        with pytest.raises(ValueError, match="Value must be a number"):
            CurrencyRounder.round(value)

    @pytest.mark.parametrize("decimals", [
        "2",
        -1,
        1.5,
        None,
    ])
    def test_round_invalid_decimals(self, decimals):
        """Test handling of invalid decimal places"""
        with pytest.raises(ValueError, match="Decimals must be a non-negative integer"):
            CurrencyRounder.round(1.23, decimals)

    def test_round_uses_config_precision(self):
        """Test that default precision comes from config"""
        value = 1.23456
        result = CurrencyRounder.round(value)
        expected = round(value, ROUNDING_PRECISION)
        assert result == expected
