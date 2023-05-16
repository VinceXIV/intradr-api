from expression import Expression
from expressiontree import clean_expression
import pandas as pd

def get_backdated_values(expression_array, assets, backdate_period, return_dataframe = True):
    values = {}
    for b in reversed(range(backdate_period)):
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

            solution = expr.evaluate()

            if("MutableDenseMatrix" not in str(type(solution))):
                values[b][var] = solution

    if(return_dataframe):
        return pd.DataFrame(values).transpose()
    else:
        return values