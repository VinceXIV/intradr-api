import numpy as np
import pandas as pd
import re
from numericals import Numerical
from sympy.parsing.sympy_parser import parse_expr

class Expression:
    def __init__(self, str_expression, variable_dict, 
                 period = "100d", interval="1d", time_zone = None, filter=None):
        self.numerical = Numerical(period = period, interval=interval, time_zone = time_zone, filter=filter)
        self.variable_dict = variable_dict
        self.expression = str_expression
        self.functions = [
            "average", "max", "min"
        ]
        
    def evaluate(self, str_expression, variable_dict = None):
        variable_dict = self.variable_dict if variable_dict == None else variable_dict

        # Find the functions used in the expressions for which
        # we have defined ways to solve
        functions_used = self.get_functions(str_expression)

        return parse_expr(str_expression, evaluate=True, local_dict=variable_dict, transformations="all")
    
    # This function returns an array in the form; 
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

    
