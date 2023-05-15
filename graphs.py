from expression import Expression
from expressiontree import clean_expression

def graph(expression_array, assets, backdate_period):
    values = get_graph_values(expression_array, assets, backdate_period)
    return values

def get_graph_values(expression_array, assets, backdate_period):

    values = {}
    for b in range(backdate_period):
        values[b] = {}
        variable_dict = {}
        error_list = []
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
                expr = Expression(assets=assets, str_expression=expression, variable_dict=variable_dict, backdate=b)
            except SyntaxError:
                error_list.append({"error": "SyntaxError", "details": "{} is an invalid expression".format(expression)})
                continue

            print(b)
            print(expression)
            solution = expr.evaluate()

            if("MutableDenseMatrix" not in str(type(solution))):
                values[b][var] = solution

    return values