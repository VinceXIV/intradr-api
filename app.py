from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from stocksymbol import StockSymbol
from ssm import *
from expression import Expression
from expressiontree import clean_expression
import numpy as np

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/assets', methods=['GET'])
@cross_origin(support_credentials=True)
def index():
    market = request.args['market']
    index = request.args['index'] if request.args['index'] != "N/A" else None
    limit = int(request.args["limit"])

    ss = StockSymbol(sym)
    result = ss.get_symbol_list(market=market, index=index)[:limit]

    return jsonify(result)

@app.route('/evaluate', methods=['POST'])
@cross_origin(support_credentials=True)
def evaluate():
    expression_array = request.get_json()['expression_array']
    assets = request.get_json()['assets']

    variable_dict = {}
    error_list = []
    results = []
    for var_expression in expression_array:
        var = ""
        expression = ""
        expr = None

        try:
            var, expression = var_expression.split("=")
            var = clean_expression(var)
        except ValueError:
            error_list.append({"error": "ValueError", "details": "expected {} to be in the form x = <some expression>".format(var_expression)})
            continue
        try:
            # breakpoint()
            expr = Expression(assets=assets, str_expression=expression, variable_dict=variable_dict)
        except SyntaxError:
            error_list.append({"error": "SyntaxError", "details": "{} is an invalid expression".format(expression)})
            continue
        
        intermediate_solution = expr.evaluate()
        variable_dict[var] = intermediate_solution

        if("MutableDenseMatrix" in str(type(intermediate_solution))):
            results.append({"name": var, "value": str(np.array(intermediate_solution).tolist())})
        else:
            results.append({"name": var, "value": str(intermediate_solution)})

    return jsonify({"results": results, "errors": error_list})


if __name__ == "__main__":
    app.run()

