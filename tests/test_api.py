import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app
from config.app_config import SUPPORTED_CURRENCIES

client = TestClient(app)

@pytest.fixture
def mock_rates():
    return {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.73,
        "JPY": 145.0
    }

@pytest.mark.asyncio
async def test_convert_endpoint_success(mock_rates):
    with patch("services.fx_rate_service.FXRateService.get_rates", new_callable=AsyncMock) as mock_get_rates:
        mock_get_rates.return_value = mock_rates
        
        response = client.post("/convert", json={
            "ccy_from": "USD",
            "ccy_to": "EUR",
            "quantity": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["ccy"] == "EUR"
        assert data["quantity"] == round(100 * 0.85, 2)

@pytest.mark.asyncio
async def test_convert_endpoint_same_currency(mock_rates):
    with patch("services.fx_rate_service.FXRateService.get_rates", new_callable=AsyncMock) as mock_get_rates:
        mock_get_rates.return_value = mock_rates
        
        response = client.post("/convert", json={
            "ccy_from": "USD",
            "ccy_to": "USD",
            "quantity": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["ccy"] == "USD"
        assert data["quantity"] == 100.00

def test_convert_endpoint_invalid_currency():
    response = client.post("/convert", json={
        "ccy_from": "XXX",
        "ccy_to": "USD",
        "quantity": 100
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported source currency: XXX"

def test_convert_endpoint_missing_fields():
    response = client.post("/convert", json={
        "ccy_from": "USD",
        "quantity": 100
    })
    
    assert response.status_code == 422  # FastAPI validation error

@pytest.mark.asyncio
async def test_convert_endpoint_zero_quantity(mock_rates):
    with patch("services.fx_rate_service.FXRateService.get_rates", new_callable=AsyncMock) as mock_get_rates:
        mock_get_rates.return_value = mock_rates
        
        response = client.post("/convert", json={
            "ccy_from": "USD",
            "ccy_to": "EUR",
            "quantity": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 0.00

@pytest.mark.asyncio
async def test_convert_endpoint_large_quantity(mock_rates):
    with patch("services.fx_rate_service.FXRateService.get_rates", new_callable=AsyncMock) as mock_get_rates:
        mock_get_rates.return_value = mock_rates
        
        response = client.post("/convert", json={
            "ccy_from": "JPY",
            "ccy_to": "USD",
            "quantity": 1000000
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["ccy"] == "USD"
        # JPY to USD: 1000000 / 145.0
        assert data["quantity"] == round(1000000 / 145.0, 2)

@pytest.mark.asyncio
async def test_convert_endpoint_negative_quantity():
    response = client.post("/convert", json={
        "ccy_from": "USD",
        "ccy_to": "EUR",
        "quantity": -100
    })
    
    assert response.status_code == 422  # Pydantic validation error
    data = response.json()
    assert "quantity" in data["detail"][0]["loc"]
    assert "Quantity must be non-negative" in data["detail"][0]["msg"]

@pytest.mark.asyncio
async def test_supported_currencies():
    for from_ccy in SUPPORTED_CURRENCIES:
        for to_ccy in SUPPORTED_CURRENCIES:
            with patch("services.fx_rate_service.FXRateService.get_rates", new_callable=AsyncMock) as mock_get_rates:
                mock_get_rates.return_value = {ccy: 1.0 for ccy in SUPPORTED_CURRENCIES}
                
                response = client.post("/convert", json={
                    "ccy_from": from_ccy,
                    "ccy_to": to_ccy,
                    "quantity": 100
                })
                
                assert response.status_code == 200
