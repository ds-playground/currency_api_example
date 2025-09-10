import pytest
from unittest.mock import AsyncMock, patch
import httpx
from services.fx_rate_service import FXRateService
from config.app_config import SUPPORTED_CURRENCIES

@pytest.fixture
def fx_service():
    return FXRateService()

@pytest.mark.asyncio
async def test_get_rate_direct_pair(fx_service):
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.text = "1.28"
        mock_response.raise_for_status.return_value = None  # Synchronous method
        mock_get.return_value = mock_response

        rate = await fx_service.get_rate("GBPUSD")
        assert rate == 1.28
        
        # Test cache hit
        rate2 = await fx_service.get_rate("GBPUSD")
        assert rate2 == 1.28
        mock_get.assert_called_once()  # Should only call API once due to caching

@pytest.mark.asyncio
async def test_get_rates_all_currencies(fx_service):
    with patch("httpx.AsyncClient.get") as mock_get:
        async def mock_get_rate(url, *args, **kwargs):
            ccy_pair = url.split("=")[1]
            mock_response = AsyncMock()
            # Simulate mock FX service responses based on MOCK_FX_RATES
            if ccy_pair == "GBPUSD":
                mock_response.text = "1.28"
            elif ccy_pair == "EURUSD":
                mock_response.text = "1.10"
            elif ccy_pair == "USDJPY":
                mock_response.text = "145.0"
            elif ccy_pair == "USDCAD":
                mock_response.text = "1.25"
            else:
                raise httpx.HTTPError(f"Pair {ccy_pair} not found")
            mock_response.raise_for_status.return_value = None  # Synchronous method
            return mock_response
            
        mock_get.side_effect = mock_get_rate
        
        rates = await fx_service.get_rates()
        assert len(rates) == len(SUPPORTED_CURRENCIES)
        assert rates["USD"] == 1.0  # Base currency
        assert abs(rates["GBP"] - (1.0 / 1.28)) < 0.0001  # Inverse of GBPUSD
        assert abs(rates["EUR"] - (1.0 / 1.10)) < 0.0001  # Inverse of EURUSD
        assert abs(rates["JPY"] - 145.0) < 0.0001  # Direct USDJPY
        assert abs(rates["CAD"] - 1.25) < 0.0001  # Direct USDCAD

@pytest.mark.asyncio
async def test_get_rate_inverse_pair(fx_service):
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.text = "1.28"
        mock_response.raise_for_status.return_value = None  # Synchronous method
        mock_get.return_value = mock_response

        rate = await fx_service.get_rate("USDGBP")
        assert rate == 1.28

@pytest.mark.asyncio
async def test_get_rate_api_error(fx_service):
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = httpx.HTTPError("API Error")
        
        with pytest.raises(httpx.HTTPError):
            await fx_service.get_rate("GBPUSD")

@pytest.mark.asyncio
async def test_get_rates_partial_failure(fx_service):
    with patch("httpx.AsyncClient.get") as mock_get:
        async def mock_get_rate(url, *args, **kwargs):
            ccy_pair = url.split("=")[1]
            if ccy_pair in ["USDJPY", "JPYUSD"]:  # Fail both direct and inverse rates
                raise httpx.HTTPError("API Error")
            mock_response = AsyncMock()
            mock_response.text = "1.1"
            mock_response.raise_for_status.return_value = None  # Synchronous method
            return mock_response
            
        mock_get.side_effect = mock_get_rate
        
        with pytest.raises(ValueError) as exc_info:
            await fx_service.get_rates()
        assert "Could not get rate for JPY" in str(exc_info.value)

@pytest.mark.asyncio
async def test_cache_expiration(fx_service):
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.text = "1.28"
        mock_response.raise_for_status.return_value = None  # Synchronous method
        mock_get.return_value = mock_response

        # First call
        rate1 = await fx_service.get_rate("GBPUSD")
        assert rate1 == 1.28
        assert mock_get.call_count == 1

        # Second call - should hit cache
        rate2 = await fx_service.get_rate("GBPUSD")
        assert rate2 == 1.28
        assert mock_get.call_count == 1  # Still 1 because of cache hit

        # Manually expire cache
        fx_service._cache.clear()

        # Third call - should miss cache
        rate3 = await fx_service.get_rate("GBPUSD")
        assert rate3 == 1.28
        assert mock_get.call_count == 2  # Incremented because of cache miss
