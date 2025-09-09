from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from services.fx_rate_service import FXRateService
from services.currency_conversion_service import CurrencyConversionService
from services.currency_validator import CurrencyValidator
from services.currency_rounder import CurrencyRounder

class ConversionRequest(BaseModel):
    ccy_from: str = Field(..., description="Source currency code")
    ccy_to: str = Field(..., description="Target currency code")
    quantity: float = Field(..., description="Amount to convert", ge=0)

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Quantity must be non-negative")
        return v

router = APIRouter()

@router.post("/convert")
async def convert_currency(request: ConversionRequest):
    try:
        CurrencyValidator.validate(request.ccy_from, request.ccy_to)
        
        fx_service = FXRateService()
        try:
            fx_rates = await fx_service.get_rates()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error: Failed to fetch rates")
        
        converter = CurrencyConversionService(fx_rates)
        try:
            converted = converter.convert(request.ccy_from, request.ccy_to, request.quantity)
            rounded = CurrencyRounder.round(converted)
            return {"quantity": rounded, "ccy": request.ccy_to}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
