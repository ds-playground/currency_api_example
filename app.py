from flask import Flask
from fx_service import convert_currency

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert():
    return convert_currency()

if __name__ == "__main__":
    app.run(debug=True)
