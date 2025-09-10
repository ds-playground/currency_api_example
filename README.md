# Currency Converter REST API

This project implements a modern Currency Converter REST API using Python and FastAPI. It provides fast, type-safe currency conversion with robust error handling and built-in caching.

## Features
- Modern async RESTful API built with FastAPI for high performance and type safety
- Comprehensive validation using Pydantic models
- Smart FX rate handling:
  - Direct rate conversion when available
  - Automatic inverse rate calculation
  - USD-based triangulation for cross-rates
- Efficient caching with TTLCache for time-based expiration
- Clean modular architecture with service layers:
  - Currency Validation Service: Input validation and currency code verification
  - FX Rate Service: Async rate fetching with caching
  - Currency Conversion Service: Business logic for currency conversion
  - Currency Rounder Service: Precise decimal rounding for financial calculations
- Asynchronous HTTP client (httpx) for improved performance
- Comprehensive test suite with both unit and integration tests
- Clear separation of concerns following SOLID principles
- Configuration-driven design
- Detailed error messages and proper HTTP status codes
- Async/await support for improved scalability
- Production-ready features:
  - Request validation
  - Rate limiting
  - Cache control
  - Proper error handling
  - Comprehensive logging
  - API documentation (Swagger/ReDoc)
  - Performance monitoring

## API Documentation

### Convert Currency
**Endpoint:** `POST /convert`

#### Request
```json
{
  "ccy_from": "USD",
  "ccy_to": "GBP",
  "quantity": 1000.00
}
```

#### Parameters
- `ccy_from`: Source currency code (3 letters, supported currencies only)
- `ccy_to`: Target currency code (3 letters, supported currencies only)
- `quantity`: Amount to convert (non-negative number)

#### Response
```json
{
  "quantity": 781.25,
  "ccy": "GBP"
}
```

#### Error Responses
- `400 Bad Request`
  - Invalid currency codes
  - Negative quantity
  - Invalid number format
- `422 Unprocessable Entity`
  - Missing required fields
  - Invalid data types
- `500 Internal Server Error`
  - FX rate service unavailable
  - Rate not available for currency pair

## Setup and Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix/macOS
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Services

1. Start the mock FX rate service:
```bash
python mock_fx_service/app.py
```

2. Start the main API service:

For normal operation:
```bash
uvicorn main:app --reload
```

For debugging and detailed logging:
```bash
uvicorn main:app --reload --log-level debug
```

The API will be available at `http://localhost:8000`. When running with debug logging, you'll see:
- Cache operations (hits and misses)
- Current cache state
- API requests and responses
- Rate fetching details

### Interactive API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

Run the complete test suite:
```bash
python -m pytest tests/ -v
```

Run specific test categories:
```bash
# Unit tests only
python -m pytest tests/test_currency_*.py -v

# API tests only
python -m pytest tests/test_api.py -v

# Mock FX Service tests
python -m pytest tests/test_mock_fx_service.py -v
```

### Mock FX Service Tests

The mock service tests verify:
1. Rate availability for all configured currency pairs in MOCK_FX_RATES
2. Proper error handling for invalid currency pairs
3. Proper error handling for missing parameters

To run the mock service tests:
1. Start the mock FX service:
```bash
python mock_fx_service/app.py
```

2. In another terminal, run the tests:
```bash
pytest mock_fx_service/tests/test_mock_service.py -v
```

The test output will show:
- Rate availability for each configured currency pair
- Validation of error responses for invalid inputs
- Proper handling of missing parameters

### Test Coverage Report
```bash
python -m pytest tests/ --cov=services --cov=routers --cov-report=term-missing
```
## Usage Examples

### Using cURL
```bash
# Basic conversion
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{"ccy_from": "EUR", "ccy_to": "USD", "quantity": 100}'

# Response
{"quantity": 110.0, "ccy": "USD"}

# Error handling example (invalid currency)
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{"ccy_from": "XXX", "ccy_to": "USD", "quantity": 100}'

# Response
{"detail": "Unsupported source currency: XXX"}
```

### Mock FX Rate Service

The mock service runs on port 5001 and provides FX rates for testing and development.

#### Using cURL
```bash
# Get EUR/USD rate
curl "http://localhost:5001/rate?ccy_pair=EURUSD"
# Response: 1.10

# Get GBP/USD rate
curl "http://localhost:5001/rate?ccy_pair=GBPUSD"
# Response: 1.28

# Get USD/JPY rate
curl "http://localhost:5001/rate?ccy_pair=USDJPY"
# Response: 145.00
```

#### Using Python - Synchronous
```python
import requests

def get_fx_rate(ccy_pair: str) -> float:
    response = requests.get(f"http://localhost:5001/rate?ccy_pair={ccy_pair}")
    response.raise_for_status()
    return float(response.text)

# Examples
eur_usd = get_fx_rate("EURUSD")
print(f"EUR/USD: {eur_usd}")  # EUR/USD: 1.10

gbp_usd = get_fx_rate("GBPUSD")
print(f"GBP/USD: {gbp_usd}")  # GBP/USD: 1.28
```

#### Using Python - Modern Async Implementation
```python
import httpx
import asyncio
from typing import Dict, List, Tuple

class CurrencyClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def convert_currency(self, from_ccy: str, to_ccy: str, quantity: float) -> Dict:
        """
        Convert currency using the async API.
        """
        response = await self.client.post(
            f"{self.base_url}/convert",
            json={
                "ccy_from": from_ccy,
                "ccy_to": to_ccy,
                "quantity": quantity
            }
        )
        response.raise_for_status()
        return response.json()

    async def get_fx_rate(self, ccy_pair: str) -> float:
        """
        Get FX rate from the mock service.
        """
        response = await self.client.get(
            "http://localhost:5001/rate",
            params={"ccy_pair": ccy_pair}
        )
        response.raise_for_status()
        return float(response.text)

    async def batch_convert(self, conversions: List[Tuple[str, str, float]]) -> List[Dict]:
        """
        Perform multiple currency conversions concurrently.
        """
        tasks = [
            self.convert_currency(from_ccy, to_ccy, amount)
            for from_ccy, to_ccy, amount in conversions
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def close(self):
        await self.client.aclose()

# Usage example
async def main():
    client = CurrencyClient()
    try:
        # Single conversion
        result = await client.convert_currency("EUR", "USD", 100)
        print(f"EUR to USD: {result}")

        # Multiple concurrent conversions
        conversions = [
            ("EUR", "USD", 100),
            ("GBP", "JPY", 50),
            ("USD", "EUR", 75)
        ]
        results = await client.batch_convert(conversions)
        for conv, result in zip(conversions, results):
            if isinstance(result, Exception):
                print(f"Error converting {conv}: {result}")
            else:
                print(f"{conv[0]} to {conv[1]}: {result}")
    finally:
        await client.close()

# Run with:
# asyncio.run(main())
```

### Currency Conversion API

#### Traditional Method (Synchronous)
```python
import requests

# Simple conversion
url = "http://localhost:8000/convert"
payload = {"ccy_from": "GBP", "ccy_to": "USD", "quantity": 100}
response = requests.post(url, json=payload)
print(response.json())
# Output: {"quantity": 128.0, "ccy": "USD"}

# More examples
def convert_currency_sync(from_ccy: str, to_ccy: str, amount: float):
    response = requests.post(
        "http://localhost:8000/convert",
        json={
            "ccy_from": from_ccy,
            "ccy_to": to_ccy,
            "quantity": amount
        }
    )
    response.raise_for_status()
    return response.json()

# Usage examples with traditional method:
# EUR to USD
result = convert_currency_sync("EUR", "USD", 100)
print(result)  # {"quantity": 110.0, "ccy": "USD"}

# GBP to JPY (using triangulation)
result = convert_currency_sync("GBP", "JPY", 100)
print(result)  # {"quantity": 18560.0, "ccy": "JPY"}

# With error handling
try:
    result = convert_currency_sync("EUR", "USD", 100)
    print(f"Converted amount: {result['quantity']} {result['ccy']}")
except requests.exceptions.RequestException as e:
    print(f"Error during conversion: {e}")
```

#### Modern Method (Asynchronous)
```python
import httpx

async def convert_currency(from_ccy: str, to_ccy: str, amount: float):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/convert",
            json={
                "ccy_from": from_ccy,
                "ccy_to": to_ccy,
                "quantity": amount
            }
        )
        return response.json()

# Usage examples:
# EUR to USD conversion
result = await convert_currency("EUR", "USD", 100)
print(result)  # {"quantity": 110.0, "ccy": "USD"}

# GBP to JPY conversion (using triangulation)
result = await convert_currency("GBP", "JPY", 100)
print(result)  # {"quantity": 18560.0, "ccy": "JPY"}
```

#### Error Handling

#### Traditional Error Handling (Synchronous)
```python
import requests
from requests.exceptions import RequestException
from typing import Dict, Any

def safe_convert_currency_sync(from_ccy: str, to_ccy: str, amount: float) -> Dict[str, Any]:
    try:
        response = requests.post(
            "http://localhost:8000/convert",
            json={
                "ccy_from": from_ccy,
                "ccy_to": to_ccy,
                "quantity": amount
            },
            timeout=5  # Add timeout for safety
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print(f"Validation error: {e.response.json()['detail']}")
        elif e.response.status_code == 422:
            print("Invalid input format")
        elif e.response.status_code == 500:
            print("Service temporarily unavailable")
        raise
    except requests.exceptions.Timeout:
        print("Request timed out")
        raise
    except requests.exceptions.ConnectionError:
        print("Connection error - service may be down")
        raise
    except RequestException as e:
        print(f"An error occurred: {e}")
        raise

# Usage example with error handling
try:
    # Valid conversion
    result = safe_convert_currency_sync("EUR", "USD", 100)
    print(f"Converted amount: {result['quantity']} {result['ccy']}")

    # Invalid currency
    result = safe_convert_currency_sync("XXX", "USD", 100)
except RequestException as e:
    print(f"Request failed: {e}")

# Batch processing with error handling
def batch_convert_sync(conversions: list[tuple[str, str, float]]) -> list[Dict[str, Any]]:
    results = []
    for from_ccy, to_ccy, amount in conversions:
        try:
            result = safe_convert_currency_sync(from_ccy, to_ccy, amount)
            results.append(result)
        except RequestException as e:
            print(f"Failed to convert {amount} {from_ccy} to {to_ccy}: {e}")
    return results

# Batch conversion example
conversions = [
    ("EUR", "USD", 100),
    ("GBP", "JPY", 50),
    ("USD", "EUR", 75)
]
results = batch_convert_sync(conversions)
```

### Additional Traditional Examples

#### Using Sessions for Multiple Requests
```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Create a session with retry strategy
def create_currency_session(retries=3):
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=0.5,  # Wait 0.5, 1, 2... seconds between retries
        status_forcelist=[500, 502, 503, 504]  # Retry on these HTTP status codes
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Use session for better performance with multiple requests
def convert_with_session(conversions: list[tuple[str, str, float]]):
    results = []
    with create_currency_session() as session:
        for from_ccy, to_ccy, amount in conversions:
            try:
                response = session.post(
                    "http://localhost:8000/convert",
                    json={
                        "ccy_from": from_ccy,
                        "ccy_to": to_ccy,
                        "quantity": amount
                    },
                    timeout=5
                )
                response.raise_for_status()
                results.append(response.json())
            except requests.exceptions.RequestException as e:
                print(f"Error converting {from_ccy} to {to_ccy}: {e}")
    return results

# Example usage with session
pairs = [
    ("EUR", "USD", 100),
    ("EUR", "USD", 200),
    ("EUR", "USD", 300)
]
results = convert_with_session(pairs)
```

#### Parallel Processing for Large Batches
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple

def convert_currency_parallel(conversions: List[Tuple[str, str, float]], 
                            max_workers: int = 5) -> List[Dict[str, Any]]:
    """
    Convert multiple currency pairs in parallel using threads.
    
    Args:
        conversions: List of (from_currency, to_currency, amount) tuples
        max_workers: Maximum number of parallel threads
        
    Returns:
        List of conversion results
    """
    results = []
    session = create_currency_session()

    def convert_single(conv: Tuple[str, str, float]) -> Dict[str, Any]:
        from_ccy, to_ccy, amount = conv
        response = session.post(
            "http://localhost:8000/convert",
            json={
                "ccy_from": from_ccy,
                "ccy_to": to_ccy,
                "quantity": amount
            }
        )
        response.raise_for_status()
        return response.json()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_conv = {
            executor.submit(convert_single, conv): conv 
            for conv in conversions
        }
        
        for future in as_completed(future_to_conv):
            conv = future_to_conv[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Conversion failed for {conv}: {e}")
    
    return results

# Example usage with parallel processing
large_batch = [
    ("EUR", "USD", amount) 
    for amount in range(100, 1100, 100)
]
parallel_results = convert_currency_parallel(large_batch)
```

#### CSV Processing Example
```python
import csv
import pandas as pd
from datetime import datetime

def process_currency_file(input_file: str, output_file: str):
    """
    Process a CSV file containing currency conversion requests.
    
    Expected CSV format:
    from_currency,to_currency,amount
    EUR,USD,100
    GBP,JPY,200
    ...
    """
    # Read conversions from CSV
    df = pd.read_csv(input_file)
    
    # Perform conversions
    results = []
    session = create_currency_session()
    
    for _, row in df.iterrows():
        try:
            response = session.post(
                "http://localhost:8000/convert",
                json={
                    "ccy_from": row["from_currency"],
                    "ccy_to": row["to_currency"],
                    "quantity": float(row["amount"])
                }
            )
            response.raise_for_status()
            result = response.json()
            results.append({
                "from_currency": row["from_currency"],
                "to_currency": row["to_currency"],
                "original_amount": row["amount"],
                "converted_amount": result["quantity"],
                "conversion_time": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error processing row {row}: {e}")
    
    # Save results
    pd.DataFrame(results).to_csv(output_file, index=False)
    return results

# Example usage
file_results = process_currency_file(
    "conversions.csv",
    f"conversion_results_{datetime.now():%Y%m%d_%H%M%S}.csv"
)
```

#### Rate Monitoring Example
```python
import time
from typing import Dict, List

def monitor_exchange_rates(currency_pairs: List[Tuple[str, str]], 
                         interval: int = 60,
                         duration: int = 3600):
    """
    Monitor exchange rates for specified currency pairs.
    
    Args:
        currency_pairs: List of (from_currency, to_currency) tuples
        interval: Seconds between checks
        duration: Total monitoring duration in seconds
    """
    session = create_currency_session()
    start_time = time.time()
    rate_history: Dict[str, List[Dict]] = {
        f"{from_ccy}/{to_ccy}": [] 
        for from_ccy, to_ccy in currency_pairs
    }
    
    while time.time() - start_time < duration:
        for from_ccy, to_ccy in currency_pairs:
            try:
                response = session.post(
                    "http://localhost:8000/convert",
                    json={
                        "ccy_from": from_ccy,
                        "ccy_to": to_ccy,
                        "quantity": 1
                    }
                )
                response.raise_for_status()
                result = response.json()
                rate_history[f"{from_ccy}/{to_ccy}"].append({
                    "time": datetime.now().isoformat(),
                    "rate": result["quantity"]
                })
                print(f"{from_ccy}/{to_ccy}: {result['quantity']}")
            except Exception as e:
                print(f"Error monitoring {from_ccy}/{to_ccy}: {e}")
        
        time.sleep(interval)
    
    return rate_history

# Example usage
pairs_to_monitor = [
    ("EUR", "USD"),
    ("GBP", "USD"),
    ("USD", "JPY")
]
rate_history = monitor_exchange_rates(
    pairs_to_monitor,
    interval=60,    # Check every minute
    duration=3600   # Monitor for 1 hour
)
```

#### Modern Service Errors (Asynchronous)
```python
import httpx
from typing import Optional, Dict, Any

class FXServiceError(Exception):
    """Base exception for FX service errors"""
    pass

class RateNotFoundError(FXServiceError):
    """Raised when a rate is not available"""
    pass

async def get_fx_rate_safe(ccy_pair: str) -> Optional[float]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:5001/rate",
                params={"ccy_pair": ccy_pair}
            )
            response.raise_for_status()
            return float(response.text)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise RateNotFoundError(f"Rate not found for {ccy_pair}")
        raise FXServiceError(f"FX service error: {e}")
    except httpx.RequestError as e:
        raise FXServiceError(f"Connection error: {e}")
    except ValueError as e:
        raise FXServiceError(f"Invalid rate format: {e}")

#### Conversion API Errors
```python
async def safe_convert_currency(from_ccy: str, to_ccy: str, amount: float) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/convert",
                json={
                    "ccy_from": from_ccy,
                    "ccy_to": to_ccy,
                    "quantity": amount
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                print(f"Validation error: {e.response.json()['detail']}")
            elif e.response.status_code == 422:
                print("Invalid input format")
            elif e.response.status_code == 500:
                print("Service temporarily unavailable")
            raise
```

## Supported Currencies

The service currently supports the following currencies:
- USD (US Dollar) - Base currency
- EUR (Euro)
- GBP (British Pound)
- JPY (Japanese Yen)

### Rate Calculation Methods
1. **Direct Rate**: Used when a direct exchange rate exists (e.g., EUR/USD)
2. **Inverse Rate**: Automatically calculated when needed (e.g., USD/EUR = 1/EUR/USD)
3. **Triangulation**: For cross-rates without direct conversion (e.g., EUR/JPY via USD)

## Configuration

The service is configurable through `config/app_config.py`:

### Core Settings
```python
# FX Rate Service URL
FX_RATE_API_URL = "http://localhost:5001/rate"

# List of supported currency codes
SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "JPY"}

# Number of decimal places for rounding
ROUNDING_PRECISION = 2
```

### Cache Settings
```python
# Cache duration for FX rates in seconds
CACHE_TTL = 60

# TTLCache settings
CACHE_MAX_SIZE = 100  # Maximum number of currency pairs to cache
CACHE_TTL = 60      # Time-to-live in seconds for cache entries
```

### Service Layer Architecture
The application follows a clean, modular architecture with distinct service layers:

1. **Currency Validation Service** (`services/currency_validator.py`)
   - Validates currency codes against supported currencies
   - Ensures input data meets business rules
   - Provides reusable validation logic

2. **FX Rate Service** (`services/fx_rate_service.py`)
   - Handles async communication with FX rate providers
   - Implements TTLCache for automatic cache expiration
   - Manages cached rate lookups and refreshes
   - Supports direct rates and calculated cross-rates

3. **Currency Conversion Service** (`services/currency_conversion_service.py`)
   - Implements core conversion business logic
   - Coordinates between other services
   - Handles conversion calculations and error cases

4. **Currency Rounder Service** (`services/currency_rounder.py`)
   - Provides precise decimal rounding for financial calculations
   - Ensures consistent rounding behavior across the application
   - Configurable precision levels

### Mock Service Configuration
```python
# Default mock exchange rates
MOCK_FX_RATES = {
    "EURUSD": 1.10,
    "GBPUSD": 1.28,
    "USDJPY": 145.00,
    # ... additional pairs
}
```

## Project Structure
```
currency_api_example/
├── config/
│   └── app_config.py          # Configuration settings
├── mock_fx_service/
│   ├── app.py                 # Mock FX rate service
│   └── tests/
│       └── test_mock_service.py
├── routers/
│   └── currency_router.py     # API route handlers
├── services/
│   ├── currency_conversion_service.py  # Currency conversion logic
│   ├── currency_rounder.py            # Currency rounding utilities
│   ├── currency_validator.py          # Currency validation
│   ├── fx_rate_service.py            # FX rate fetching with caching
│   └── http_client.py                # HTTP client utilities
├── tests/
│   ├── test_api.py                   # API integration tests
│   ├── test_currency_api.py          # Currency API tests
│   ├── test_currency_conversion.py   # Conversion service tests
│   ├── test_currency_rounder.py      # Rounding utility tests
│   ├── test_currency_validator.py    # Validation tests
│   ├── test_fx_rate_service.py       # FX rate service tests
│   └── test_mock_fx_service.py       # Mock service tests
├── main.py                           # FastAPI application entry point
└── requirements.txt                  # Project dependencies
```

## Development Guidelines

### Adding New Currencies
1. Add the currency code to `SUPPORTED_CURRENCIES` in `config/app_config.py`
2. Update the mock FX rates in `MOCK_FX_RATES`
3. Add relevant test cases in `tests/test_currency_*.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all function parameters and returns
- Document all public functions and classes
- Ensure test coverage for new features

### Testing Requirements
- Write unit tests for all new functionality
- Include both success and error cases
- Test edge cases (e.g., zero amounts, large numbers)
- Add integration tests for new currency pairs

### Pull Request Guidelines
1. Update tests and ensure all pass
2. Update documentation if adding features
3. Add appropriate error handling
4. Follow existing code style
5. Include test coverage report
