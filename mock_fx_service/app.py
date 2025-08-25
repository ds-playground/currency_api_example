
from flask import Flask, request

app = Flask(__name__)

FX_RATES = {
    "EURUSD": 1.10,
    "GBPUSD": 1.28,
    "USDCAD": 1.25,
    "USDJPY": 145.00,
    "EURGBP": 0.85
}

@app.route("/rate", methods=["GET"])
def get_rate():
    """
    Endpoint to return mock FX rate for a given currency pair.
    """
    ccy_pair = request.args.get("ccy_pair")
    rate = FX_RATES.get(ccy_pair)
    if rate:
        return str(rate)
    else:
        return "Rate not found", 404

if __name__ == "__main__":
    app.run(port=5001)
