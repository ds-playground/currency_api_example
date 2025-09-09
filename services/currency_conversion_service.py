from decimal import Decimal
from typing import Dict, Union

Number = Union[int, float, Decimal]

class CurrencyConversionService:
    def __init__(self, fx_rates: Dict[str, float]):
        """
        Initialize the conversion service with FX rates.
        
        Args:
            fx_rates: Dictionary mapping currency codes to their rates against base currency
        """
        if not isinstance(fx_rates, dict):
            raise ValueError("FX rates must be provided as a dictionary")
        self.fx_rates = fx_rates

    def get_conversion_rate(self, ccy_from: str, ccy_to: str) -> float:
        """
        Get the conversion rate between two currencies.
        
        Args:
            ccy_from: Source currency code
            ccy_to: Target currency code
            
        Returns:
            float: The conversion rate
            
        Raises:
            ValueError: If currency pair is invalid or rate not found
        """
        if ccy_from == ccy_to:
            return 1.0
            
        try:
            from_rate = self.fx_rates[ccy_from.upper()]
            to_rate = self.fx_rates[ccy_to.upper()]
            return to_rate / from_rate
        except KeyError as e:
            missing = ccy_from if ccy_from not in self.fx_rates else ccy_to
            raise ValueError(f"No exchange rate found for {missing}")
        except ZeroDivisionError:
            raise ValueError(f"Invalid rate of 0 for {ccy_from}")

    def convert(self, ccy_from: str, ccy_to: str, quantity: Number) -> float:
        """
        Convert an amount from one currency to another.
        
        Args:
            ccy_from: Source currency code
            ccy_to: Target currency code
            quantity: Amount to convert
            
        Returns:
            float: The converted amount
            
        Raises:
            ValueError: If quantity is invalid or conversion fails
        """
        if not isinstance(quantity, (int, float, Decimal)):
            raise ValueError("Quantity must be a number")
            
        if quantity < 0:
            raise ValueError("Quantity must be non-negative")
            
        rate = self.get_conversion_rate(ccy_from, ccy_to)
        return float(Decimal(str(quantity)) * Decimal(str(rate)))
