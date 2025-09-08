FX_RATE_API_URL = "http://localhost:5001/rate"
SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "CAD"}
ROUNDING_PRECISION = 2

# Cache settings
CACHE_TTL = 60  # Cache FX rates for 60 seconds

MOCK_FX_RATES = {
	"EURUSD": 1.10,
	"GBPUSD": 1.28,
	"USDCAD": 1.25,
	"USDJPY": 145.00,
	"EURGBP": 0.85
}
