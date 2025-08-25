
import requests

DIRECT_PAIRS = {"EURUSD", "GBPUSD", "USDCAD", "USDJPY", "EURGBP"}
FX_RATE_API_URL = "http://localhost:5001/rate"

def get_fx_rate(ccy_from, ccy_to):
    """
    Fetch FX rate for currency conversion.
    Uses direct rate if available, otherwise triangulates via USD.
    """
    pair = f"{ccy_from}{ccy_to}"
    if pair in DIRECT_PAIRS:
        response = requests.get(f"{FX_RATE_API_URL}?ccy_pair={pair}")
        return float(response.text)
    elif f"{ccy_to}{ccy_from}" in DIRECT_PAIRS:
        response = requests.get(f"{FX_RATE_API_URL}?ccy_pair={ccy_to}{ccy_from}")
        return 1 / float(response.text)
    else:
        if ccy_from != "USD" and ccy_to != "USD":
            rate_from_usd = get_fx_rate(ccy_from, "USD")
            rate_to_usd = get_fx_rate("USD", ccy_to)
            return rate_from_usd * rate_to_usd
        else:
            raise ValueError("Unsupported currency pair")
