from decimal import Decimal, ROUND_HALF_UP
from config.app_config import ROUNDING_PRECISION

class CurrencyRounder:
    @staticmethod
    def _quantize_decimal(value: Decimal, decimals: int) -> Decimal:
        """
        Quantizes a Decimal value to the specified number of decimal places using half-up rounding.
        
        Args:
            value: The Decimal value to quantize
            decimals: Number of decimal places
            
        Returns:
            Decimal: The quantized value
        """
        return value.quantize(Decimal('0.1') ** decimals, rounding=ROUND_HALF_UP)

    @staticmethod
    def round(value: float, decimals: int = ROUNDING_PRECISION) -> float:
        """
        Rounds a currency value using banker's rounding (half-up).
        
        Args:
            value: The value to round
            decimals: Number of decimal places (defaults to ROUNDING_PRECISION)
            
        Returns:
            float: The rounded value
            
        Raises:
            ValueError: If value is not a valid number or if decimals is not a non-negative integer
        """
        if not isinstance(value, (int, float, Decimal)):
            raise ValueError("Value must be a number")
            
        # None is invalid when explicitly passed
        if decimals is None:
            raise ValueError("Decimals must be a non-negative integer")
            
        # Validate decimals
        if not isinstance(decimals, int) or decimals < 0:
            raise ValueError("Decimals must be a non-negative integer")
            
        value_dec = Decimal(str(value))
        rounded = CurrencyRounder._quantize_decimal(value_dec, decimals)
        
        return float(rounded)
