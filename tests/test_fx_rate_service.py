import pytest
from unittest.mock import AsyncMock, patch
import httpx
from services.fx_rate_service import FXRateService
from config.app_config import SUPPORTED_CURRENCIES, FX_RATE_API_URL

@pytest.fixture
def fx_service():
    service = FXRateService()
    service._cache.clear()  # Clear the cache before each test
    return service

@pytest.mark.asyncio
async def test_get_rate_direct_pair(fx_service):
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_response = AsyncMock()
        mock_response.text = "1.28"
        mock_response.aread.return_value = b"1.28"
        mock_response.is_error = False
        mock_response.raise_for_status = AsyncMock()
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client        
        rate = await fx_service.get_rate("GBPUSD")
        assert rate == 1.28
        
        # Test cache hit
        rate2 = await fx_service.get_rate("GBPUSD")
        assert rate2 == 1.28
        assert mock_client.get.call_count == 1  # Should only call API once due to caching


@pytest.mark.asyncio
async def test_get_rate_inverse_pair(fx_service):
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_response = AsyncMock()
        mock_response.text = "1.28"
        mock_response.aread = AsyncMock(return_value=b"1.28")
        mock_response.is_error = False
        mock_response.raise_for_status = AsyncMock()        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        rate = await fx_service.get_rate("USDGBP")
        assert rate == 1.28
        mock_client.get.assert_called_once_with(f"{FX_RATE_API_URL}?ccy_pair=USDGBP")

    @pytest.mark.asyncio
    async def test_get_rate_invalid_format(fx_service):
        """Test that the service raises ValueError when receiving non-numeric rate"""
        with patch("httpx.AsyncClient") as mock_client_class:
            # Create mock response with invalid rate
            mock_response = AsyncMock()
            mock_response.text = "not a number"
            mock_response.aread.return_value = b"not a number"
            mock_response.is_error = False
            mock_response.raise_for_status = AsyncMock()

            # Set up the mock client exactly like test_get_rate_direct_pair
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # First API call - should raise ValueError and not be cached
            # This verifies the basic error handling works
            with pytest.raises(ValueError) as exc_info:
                await fx_service.get_rate("GBPUSD")

            # Verify error details and that API was called
            assert "Invalid rate format" in str(exc_info.value)            
            assert mock_client.get.call_count == 1            
            mock_client.get.assert_called_with(f"{FX_RATE_API_URL}?ccy_pair=GBPUSD")

            # Second API call - verifies that error responses are not cached
            # Unlike successful responses (which are cached), errors should always
            # trigger a new API call to check if the error condition is resolved
            with pytest.raises(ValueError) as exc_info:
                await fx_service.get_rate("GBPUSD")
            assert "Invalid rate format" in str(exc_info.value)
            assert mock_client.get.call_count == 2  # Should be a fresh API call
            mock_client.get.assert_called_with(f"{FX_RATE_API_URL}?ccy_pair=GBPUSD")

@pytest.mark.asyncio
async def test_get_rates_partial_failure(fx_service):
    with patch("httpx.AsyncClient") as mock_client_class:
        async def mock_get(url, *args, **kwargs):
            ccy_pair = url.split("=")[1]
            mock_response = AsyncMock()
            if ccy_pair in ["USDJPY", "JPYUSD"]:
                async def raise_error(*args, **kwargs):
                    raise httpx.HTTPError("API Error")
                mock_response.text = "Error"
                mock_response.aread = AsyncMock(return_value=b"Error")
                mock_response.is_error = True
                mock_response.raise_for_status = AsyncMock(side_effect=raise_error)
            else:
                mock_response.text = "1.1"
                mock_response.aread = AsyncMock(return_value=b"1.1")
                mock_response.is_error = False
                mock_response.raise_for_status = AsyncMock()
            return mock_response
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=mock_get)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(ValueError) as exc_info:
            await fx_service.get_rates("JPY")
        assert "Could not get rate for JPY" in str(exc_info.value)

@pytest.mark.asyncio
async def test_cache_expiration(fx_service):
    mock_url = f"{FX_RATE_API_URL}?ccy_pair=GBPUSD"

    with patch("httpx.AsyncClient") as mock_client_class:
        # Create mock response
        mock_response = AsyncMock()
        mock_response.text = "1.28"
        mock_response.aread.return_value = b"1.28"
        mock_response.is_error = False
        mock_response.raise_for_status = AsyncMock()

        # Set up the client with response, exactly like test_get_rate_direct_pair
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # First call - cache miss, should make API call
        rate1 = await fx_service.get_rate("GBPUSD")
        assert rate1 == 1.28
        mock_client.get.assert_called_once_with(mock_url)

        # Reset mock call counter
        mock_client.get.reset_mock()

        # Second call - should hit cache
        rate2 = await fx_service.get_rate("GBPUSD")
        assert rate2 == 1.28
        assert mock_client.get.call_count == 0  # No API call due to cache hit

        # Manually expire cache
        fx_service._cache.clear()

        # Third call - should miss cache and make new API call
        rate3 = await fx_service.get_rate("GBPUSD")
        assert rate3 == 1.28
        mock_client.get.assert_called_once_with(mock_url)
