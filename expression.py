import numpy as np
import pandas as pd
from sympy.parsing.sympy_parser import parse_expr

class Expression:
    def __init__(self, str_expression, variable_dict):
        self.variable_dict = variable_dict
        self.expression = str_expression
        pass

    def evaluate(self, str_expression, variable_dict = None):
        variable_dict = self.variable_dict if variable_dict == None else variable_dict
        return parse_expr(str_expression, evaluate=True, local_dict=variable_dict, transformations="all")
    
