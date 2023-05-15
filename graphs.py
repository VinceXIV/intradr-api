from expression import Expression
from expressiontree import clean_expression
import pandas as pd
import mpld3
import matplotlib.pyplot as plt

def graph(graph, variables, expression_array, assets, backdate_period=30, figsize=(9, 4)):
    df = get_value_df(expression_array, assets, backdate_period)

    fig = plt.figure(figsize = figsize)
    if(graph == "line"):
        for v in variables:
            print(v)
            print(df.index)
            plt.plot(df.index, df[v])

    html_str = mpld3.fig_to_html(fig)
    # Html_file= open("graph.html","w")
    # Html_file.write(html_str)
    # Html_file.close()
    return html_str
    

def get_value_df(expression_array, assets, backdate_period):

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

            solution = expr.evaluate()

            if("MutableDenseMatrix" not in str(type(solution))):
                values[b][var] = solution

    return pd.DataFrame(values).transpose()