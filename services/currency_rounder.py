from decimal import Decimal, ROUND_HALF_UP
from config.app_config import ROUNDING_PRECISION

class CurrencyRounder:
    @staticmethod
    def round(value: float, decimals: int = None) -> float:
        """
        Rounds a currency value using banker's rounding (half-up).
        
        Args:
            value: The value to round
            decimals: Number of decimal places (defaults to ROUNDING_PRECISION)
            
        Returns:
            float: The rounded value
            
        Raises:
            ValueError: If value is not a valid number
        """
        if not isinstance(value, (int, float, Decimal)):
            raise ValueError("Value must be a number")
            
        if decimals is None:
            decimals = ROUNDING_PRECISION
            
        if not isinstance(decimals, int) or decimals < 0:
            raise ValueError("Decimals must be a non-negative integer")
            
        # Convert to Decimal for precise rounding
        dec = Decimal(str(value))
        rounded = dec.quantize(Decimal('0.1') ** decimals, rounding=ROUND_HALF_UP)
        
        return float(rounded)
