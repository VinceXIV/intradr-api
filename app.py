from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from stocksymbol import StockSymbol
from expression import Expression
from expressiontree import clean_expression
import numpy as np
import graphs
import utility_functions as uf
import backdated
import apputilities
from numericals import Numerical
import os

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/assets', methods=['GET'])
@cross_origin(support_credentials=True)
def index():
    market = request.args['market']
    index = request.args['index'] if request.args['index'] != "N/A" else None
    limit = int(request.args["limit"])

    ss = os.getenv("STOCK_SYMBOL_KEY")
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
            results.append({"name": var, "value": str(uf.recursive_round(np.array(intermediate_solution).tolist(), 4)), "shape": intermediate_solution.shape})
        else:
            results.append({"name": var, "value": str(uf.recursive_round(intermediate_solution, 4)), "shape": 1})

    return jsonify({"results": results, "errors": error_list})

# @app.route('/graph', methods=['POST'])
# @cross_origin(support_credentials=True)
# def graph():
#     variables = request.get_json()['variables']
#     expression_array = request.get_json()['expression_array']
#     assets = request.get_json()['assets']
#     graph_type = request.get_json()['graph_type'] if 'graph_type' in request.get_json() else 'line'
#     backdate_period = request.get_json()['backdate_period'] if 'backdate_period' in request.get_json() else 30
#     figure_size = request.get_json()['figure_size'] if 'figure_size' in request.get_json() else (9, 4)

#     html_str_graph = graphs.plot(
#         graph_type = graph_type,
#         variables = variables,
#         expression_array = expression_array,
#         assets = assets,
#         backdate_period=backdate_period,
#         figsize= figure_size
#     )

#     return html_str_graph

@app.route('/graph_data', methods=['POST'])
@cross_origin(support_credentials=True)
def graph_data():
    xpa = request.get_json()['expression_array']
    ast = request.get_json()['assets']
    bd = request.get_json()['backdate_period'] if 'backdate_period' in request.get_json() else 5

    # breakpoint()
    result = backdated.get_backdated_values(
        expression_array = xpa,
        assets = ast,
        backdate_period = bd,
        return_dataframe = False
    )

    return jsonify({"graph_data": apputilities.process_data_dict(result)})

@app.route('/fundamentals', methods=['POST'])
@cross_origin(support_credentials=True)
def fundamentals():
    ticker = request.get_json()['ticker']

    num = Numerical()
    return jsonify({"name": ticker, "value": num.get_numeric_info(ticker=ticker)})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

