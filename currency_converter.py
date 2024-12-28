from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def convert_currency():
    ccy_from = request.args.get('ccy_from')
    ccy_to = request.args.get('ccy_to')
    quantity = float(request.args.get('quantity'))

    # Fetch real-time FX rates from CoinDesk API
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    data = response.json()
    
    # Extract Bitcoin prices in USD, EUR, and GBP
    bpi = data['bpi']
    rate_dict = {i:bpi[i]['rate_float'] for i in bpi.keys()}

    # Calculate FX rates
    fx_rates = {f"{j}/{i}":rate_dict[i]/rate_dict[j] for i in bpi.keys() for j in bpi.keys() if i != j}

    # Perform currency conversion
    conversion_key = f'{ccy_from}/{ccy_to}'
    if conversion_key in fx_rates:
        converted_quantity = quantity * fx_rates[conversion_key]
        result = {'quantity': converted_quantity, 'ccy': ccy_to}
    else:
        result = {'error': 'Invalid currency pair'}

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False)
    # app.run(debug=True)

# Run the app
# python currency_converter.py

# Sample query
# http://127.0.0.1:5000/?ccy_from=USD&ccy_to=GBP&quantity=1000

# Sample output
# {“quantity”: 779.77, “ccy”: “GBP”}