from flask import Flask, request, jsonify
from fx_service import get_fx_rate

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert_currency():
    """
    Endpoint to convert currency using FX rates.
    Expects JSON with 'ccy_from', 'ccy_to', and 'quantity'.
    Returns converted amount in target currency.
    """
    data = request.get_json()
    ccy_from = data["ccy_from"]
    ccy_to = data["ccy_to"]
    quantity = data["quantity"]

    try:
        rate = get_fx_rate(ccy_from, ccy_to)
        converted_quantity = quantity * rate
        return jsonify({"quantity": round(converted_quantity, 2), "ccy": ccy_to})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
