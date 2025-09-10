import httpx
import logging
from cachetools import TTLCache
from config.app_config import FX_RATE_API_URL, CACHE_TTL, SUPPORTED_CURRENCIES

logger = logging.getLogger(__name__)

class FXRateService:
    # Class-level cache shared across all instances
    _cache = TTLCache(maxsize=100, ttl=CACHE_TTL)  # Increased cache size for currency pairs

    def __init__(self):
        pass

    async def get_rate(self, ccy_pair: str) -> float:
        # Try to get rate from cache first
        try:
            logger.debug(f"Attempting to fetch rate from cache for {ccy_pair}")
            logger.debug(f"Current cache state: {self._cache}")
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
                logger.debug(f"Fetched rate from API for {ccy_pair}")
                logger.debug(f"Current cache state: {self._cache}")
                self._cache[ccy_pair] = rate
                return rate

    async def get_rates(self, ccy: str = "EUR"):
        # Validate currency first
        if ccy not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {ccy}")

        # Initialize with base currency
        rates = {"USD": 1.0}

        # Only fetch rate for the requested currency
        if ccy != "USD":  # Skip if USD since it's our base currency
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
        logger.debug(f"Final rates: {rates}")
        return rates
