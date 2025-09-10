import httpx
from cachetools import TTLCache
from config.app_config import FX_RATE_API_URL, CACHE_TTL, SUPPORTED_CURRENCIES

class FXRateService:
    def __init__(self):
        # Create a TTL cache that expires entries after CACHE_TTL seconds
        self._cache = TTLCache(maxsize=100, ttl=CACHE_TTL)  # Increased cache size for currency pairs

    async def get_rate(self, ccy_pair: str) -> float:
        # Try to get rate from cache first
        try:
            return self._cache[ccy_pair]
        except KeyError:
            # Cache miss, fetch from API
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{FX_RATE_API_URL}?ccy_pair={ccy_pair}")
                await response.aread()  # Ensure the response is fully read
                if response.is_error:  # Check for errors without async call
                    response.raise_for_status()  # This will raise the appropriate error
                rate = float(response.text)
                
                # Store in cache
                self._cache[ccy_pair] = rate
                return rate

    async def get_rates(self):
        rates = {"USD": 1.0}  # Base currency
        for ccy in SUPPORTED_CURRENCIES:
            if ccy != "USD":  # Skip USD as it's our base currency
                try:
                    # Try direct rate first (e.g., GBPUSD)
                    rate = await self.get_rate(f"{ccy}USD")
                    rates[ccy] = 1.0 / rate  # Invert since we got CCY/USD but need USD/CCY
                except httpx.HTTPError:
                    # If direct rate fails, try inverse rate (e.g., USDGBP)
                    try:
                        rate = await self.get_rate(f"USD{ccy}")
                        rates[ccy] = rate
                    except httpx.HTTPError as e:
                        # If both fail, raise error
                        raise ValueError(f"Could not get rate for {ccy}") from e
        return rates
