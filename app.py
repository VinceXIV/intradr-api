from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from stocksymbol import StockSymbol
from ssm import *



app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/assets', methods=['GET'])
@cross_origin(support_credentials=True)
def index():
    market = request.get_json()['market']
    index = request.get_json()['index']

    ss = StockSymbol(sym)
    result = ss.get_symbol_list(market=market, index=index)

    return jsonify(result)

