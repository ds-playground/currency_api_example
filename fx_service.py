import requests
from flask import request, jsonify
from decimal import Decimal, ROUND_HALF_UP

DIRECT_PAIRS = {"EURUSD", "GBPUSD", "USDCAD", "USDJPY", "EURGBP"}
FX_RATE_API_URL = "http://localhost:5001/rate"

def get_fx_rate(ccy_from, ccy_to, visited=None):
    """
    Fetch FX rate for currency conversion.
    Uses direct rate if available, otherwise triangulates via USD, EUR, GBP, or JPY.
    Prevents infinite recursion by tracking visited pairs.
    """
    if visited is None:
        visited = set()

    pair = f"{ccy_from}{ccy_to}"
    inverse_pair = f"{ccy_to}{ccy_from}"

    # Check if this pair has already been tried
    if pair in visited or inverse_pair in visited:
        raise ValueError("Unsupported currency pair")

    visited.add(pair)

    if pair in DIRECT_PAIRS:
        response = requests.get(f"{FX_RATE_API_URL}?ccy_pair={pair}")
        return float(response.text)
    elif inverse_pair in DIRECT_PAIRS:
        response = requests.get(f"{FX_RATE_API_URL}?ccy_pair={inverse_pair}")
        return 1 / float(response.text)
    else:
        # Try triangulation via common base currencies
        for base in ["USD", "EUR", "GBP", "JPY"]:
            if ccy_from != base and ccy_to != base:
                try:
                    rate_from_base = get_fx_rate(ccy_from, base, visited)
                    rate_to_base = get_fx_rate(base, ccy_to, visited)
                    return rate_from_base * rate_to_base
                except ValueError:
                    continue  # Try next base currency

        raise ValueError("Unsupported currency pair")

def round_money(value, decimals=2):
    """
    Round a monetary value using Decimal and ROUND_HALF_UP.
    This avoids Python's default 'bankers rounding' (round half to even),
    which is not suitable for financial applications.
    """
    return float(Decimal(str(value)).quantize(Decimal(f"1.{'0'*decimals}"), rounding=ROUND_HALF_UP))

def convert_currency():
    """
    Endpoint to convert currency using FX rates.
    Expects JSON with 'ccy_from', 'ccy_to', and 'quantity'.
    Returns converted amount in target currency.
    Rejects negative quantities.
    """
    data = request.get_json()
    try:
        ccy_from = data["ccy_from"]
        ccy_to = data["ccy_to"]
        quantity = Decimal(str(data["quantity"]))

        if quantity < 0:
            raise ValueError("Quantity must be non-negative")

        rate = Decimal(str(get_fx_rate(ccy_from, ccy_to)))
        converted_quantity = round_money(quantity * rate)

        return jsonify({"quantity": converted_quantity, "ccy": ccy_to})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
