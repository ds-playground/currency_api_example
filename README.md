# Currency Converter REST API

This project implements a Currency Converter REST API using Python and Flask. It allows users to convert amounts between currencies using FX rates from a mock service.

## Features
- Convert currencies via POST request
- Uses direct FX rates when available
- Supports triangulation via USD for indirect conversions
- Modular code structure
- Includes unit and integration tests

## API Usage
### Endpoint
`POST /convert`

### Request Body (JSON)
```
{
  "ccy_from": "USD",
  "ccy_to": "GBP",
  "quantity": 1000
}
```

### Response (JSON)
```
{
  "quantity": 1280.0,
  "ccy": "GBP"
}
```

## Running the Application
```bash
python app.py
```

Ensure the mock FX rate service is running:
```bash
python mock_fx_service/app.py
```

## Running Unit Tests
```bash
python -m unittest discover tests
```

## Running Integration Tests
```bash
python -m unittest discover mock_fx_service/tests
```
## Example REST API Request
Use curl or any HTTP client to make a POST request to the /convert endpoint:

```bash
curl -X POST http://localhost:5000/convert      -H "Content-Type: application/json"      -d '{"ccy_from": "EUR", "ccy_to": "USD", "quantity": 100}'
```

### Example Response
```
{
  "quantity": 110.0,
  "ccy": "USD"
}
```

## Python Requests Examples

### Mock FX rate service
```python
import requests
url = "http://localhost:5001/rate?ccy_pair=GBPUSD"
response = requests.get(url)
print(response.json())

# Response
1.28
```

### Convert GBP to USD
```python
import requests
url = "http://localhost:5000/convert"
payload = {"ccy_from": "GBP", "ccy_to": "USD", "quantity": 100}
response = requests.post(url, json=payload)
print(response.json())

# Response
{'ccy': 'USD', 'quantity': 128.0}
```

### Convert EUR to GBP
```python
import requests
url = "http://localhost:5000/convert"
payload = {"ccy_from": "EUR", "ccy_to": "GBP", "quantity": 100}
response = requests.post(url, json=payload)
print(response.json())

# Response
{'ccy': 'GBP', 'quantity': 85.0}
```

### Convert GBP to JPY
```python
import requests
url = "http://localhost:5000/convert"
payload = {"ccy_from": "GBP", "ccy_to": "JPY", "quantity": 100}
response = requests.post(url, json=payload)
print(response.json())

# Response
{'ccy': 'JPY', 'quantity': 18560.0}
```
