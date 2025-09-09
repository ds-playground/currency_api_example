from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, AsyncMock
from main import app
from services.fx_rate_service import FXRateService

client = TestClient(app)

@pytest.fixture
def mock_fx_rates():
    return {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.73
    }

@pytest.mark.asyncio
async def test_convert_endpoint_success(mock_fx_rates):
    with patch.object(FXRateService, 'get_rates', new_callable=AsyncMock) as mock_get_rates:
        mock_get_rates.return_value = mock_fx_rates
        
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
async def test_convert_endpoint_same_currency(mock_fx_rates):
    with patch.object(FXRateService, 'get_rates', new_callable=AsyncMock) as mock_get_rates:
        mock_get_rates.return_value = mock_fx_rates
        
        response = client.post("/convert", json={
            "ccy_from": "USD",
            "ccy_to": "USD",
            "quantity": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["ccy"] == "USD"
        assert data["quantity"] == 100.00

@pytest.mark.asyncio
async def test_convert_endpoint_invalid_currency():
    response = client.post("/convert", json={
        "ccy_from": "XXX",
        "ccy_to": "USD",
        "quantity": 100
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported source currency: XXX"

@pytest.mark.asyncio
async def test_convert_endpoint_missing_fields():
    response = client.post("/convert", json={
        "ccy_from": "USD",
        "quantity": 100
    })
    
    assert response.status_code == 422  # FastAPI validation error

@pytest.mark.asyncio
async def test_convert_endpoint_negative_quantity(mock_fx_rates):
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
async def test_convert_endpoint_rate_service_error():
    with patch.object(FXRateService, 'get_rates', new_callable=AsyncMock) as mock_get_rates:
        mock_get_rates.side_effect = Exception("Failed to fetch rates")
        
        response = client.post("/convert", json={
            "ccy_from": "USD",
            "ccy_to": "EUR",
            "quantity": 100
        })
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
