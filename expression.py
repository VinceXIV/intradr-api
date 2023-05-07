import numpy as np
import pandas as pd
import re
from numericals import Numerical
from sympy.parsing.sympy_parser import parse_expr

class Expression:
    def __init__(self, str_expression, variable_dict = {}, 
                 period = "100d", interval="1d", time_zone = None, filter=None):
        self.numerical = Numerical(period = period, interval=interval, time_zone = time_zone, filter=filter)
        self.variable_dict = variable_dict
        self.expression = str_expression
        self.functions = [
            "average", "max", "min"
        ]
        
    def evaluate(self, str_expression=None, variable_dict = {}):
        variable_dict = self.variable_dict if variable_dict == {} else variable_dict
        str_expression = self.expression if str_expression == None else str_expression

        # Find the functions used in the expressions for which
        # we have defined ways to solve
        functions_used = self.get_functions(str_expression)

        # Here, the f_expression_results will end up being in the form
        # {average(AAPL_return, 10d, 1m): 100, max(MSFT_vol, 15d, 1m): 50000}
        # with the key values being in string. Since the initial expression is
        # in string format (e.g x = "average(AAPL_return, 10d, 1m) + 10x + 60"),
        # we can thus simply string replace these values with whatever we get from
        # f_expression_results below
        f_expression_results = {}
        for f in functions_used:
            for expression in functions_used[f]:
                val = self.__evaluate_function(function_=f, expression=expression)
                f_expression_results[expression] = val

        for key in f_expression_results:
            str_expression = str_expression.replace(key, str(f_expression_results[key]))

        return float(parse_expr(str_expression, evaluate=True, local_dict=variable_dict, transformations="all"))
    
    # This function returns an object of arrays in the form {average: [], min: []}.
    # The arrays, on the other hand, are in the form; 
    # ["average(variable1, varable2, variable3)", "min(variable1, variable2, variable3)"]
    # We expect variable1 to be the asset (e.g AAPL_return), while variable2 and variable3
    # shows the period and interval that we can use with yfinance to get info on them
    def get_functions(self, str_expression):
        functions = {}
        for f in self.functions:
            if(f in str_expression):
                regex = r"{f}\(\w+,\s*\w+,\s*\w+\)".format(f=f)
                
                functions[f] = re.findall(regex, str_expression)

        return functions
    
    # Takes in functions in the form "average(AAPL_return, 10d, 1m)" (**it is in string format**)
    # and returns the solution to the expression also in string format
    def __evaluate_function(self, function_, expression):
        f = function_

        # If an expression is like average(AAPL_return, 10d, 1m) I separate them such that
        # I get ticker = AAPL, val = return, period = 10d, and interval = 1m
        variables = expression.replace(f+"(", "").replace(")", "").replace(" ", "").split(",")
        ticker = variables[0].split("_")[0]
        val = "_".join(variables[0].split("_")[1:])
        period = variables[1]
        interval = variables[2]

        # This will return the historical data in same format as yfinance with specified period
        # and interval. The "val" found above can be return, volume, etc
        numerical = Numerical(period = period, interval=interval, time_zone = None, filter=val)
        historical_data = numerical.get_historical_data(ticker = ticker)

        if(f == "average"):
            return historical_data.mean()
        elif(f == "max"):
            return historical_data.max()
        elif(f == "min"):
            return historical_data.min()
        elif(f == "stdev"):
            return historical_data.std()

    
