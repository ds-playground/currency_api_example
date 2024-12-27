# Currency conversion API example

Users should be able to send GET requests to the Currency Converter REST API with parameters ccy_from=USD&ccy_to=GBP&quantity=1000 and receive a response in the JSON format {“quantity”: 779.77, “ccy”: “GBP”}.

The service should be using near-real-time FX rates that can be derived from the CoinDesk REST API (https://api.coindesk.com/v1/bpi/currentprice.json). This service provides real-time bitcoin prices in 3 currencies (USD, EUR, GBP)