

from flask import Flask, request
import sys
import os

# Add the root directory to Python path to find config module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.app_config import MOCK_FX_RATES

app = Flask(__name__)

FX_RATES = MOCK_FX_RATES

@app.route("/rate", methods=["GET"])
def get_rate():
    """
    Endpoint to return mock FX rate for a given currency pair.
    """
    ccy_pair = request.args.get("ccy_pair")
    if not ccy_pair:
        return "Missing ccy_pair parameter", 400
        
    ccy_pair = ccy_pair.upper()
    rate = FX_RATES.get(ccy_pair)
    if rate:
        return str(rate)
    else:
        return f"Rate not found for currency pair: {ccy_pair}", 404

if __name__ == "__main__":
    app.run(port=5001)
