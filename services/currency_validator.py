from config.app_config import SUPPORTED_CURRENCIES, MOCK_FX_RATES

class CurrencyValidator:
    @staticmethod
    def validate(ccy_from: str, ccy_to: str) -> None:
        """
        Validates currency codes for conversion.
        
        Args:
            ccy_from: Source currency code
            ccy_to: Target currency code
            
        Raises:
            ValueError: If currency codes are invalid or unsupported
        """
        if not isinstance(ccy_from, str) or not isinstance(ccy_to, str):
            raise ValueError("Currency codes must be strings")
        
        ccy_from = ccy_from.upper()
        ccy_to = ccy_to.upper()
        
        if len(ccy_from) != 3 or len(ccy_to) != 3:
            raise ValueError("Currency codes must be 3 characters")
            
        if not ccy_from.isalpha() or not ccy_to.isalpha():
            raise ValueError("Currency codes must contain only letters")
            
        # First check if the currency pair or its inverse exists in MOCK_FX_RATES
        direct_pair = f"{ccy_from}{ccy_to}" in MOCK_FX_RATES
        inverse_pair = f"{ccy_to}{ccy_from}" in MOCK_FX_RATES
        
        # If neither direct nor inverse pair exists, then check SUPPORTED_CURRENCIES
        if not direct_pair and not inverse_pair:
            if ccy_from not in SUPPORTED_CURRENCIES:
                raise ValueError(f"Unsupported source currency: {ccy_from}")
                
            if ccy_to not in SUPPORTED_CURRENCIES:
                raise ValueError(f"Unsupported target currency: {ccy_to}")
