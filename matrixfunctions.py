import pandas as pd
from sympy import parse_expr
from sympy.parsing.sympy_parser import T

def call(function_name, argument_array, variable_dict):
    argument_array = get_argument_values(argument_array, variable_dict)
    if(function_name == "_avg"):
        return pd.Series(list(argument_array[0])).mean()
    elif(function_name == "_max"):
        return pd.Series(list(argument_array[0])).max()
    elif(function_name == "_min"):
        return pd.Series(list(argument_array[0])).min()
    elif(function_name == "_std"):
        return pd.Series(list(argument_array[0])).std()
    elif(function_name == "_var"):
        return pd.Series(list(argument_array[0])).var()
    elif(function_name == "_quantile"):
        return pd.Series(list(argument_array[0])).quantile(argument_array[1])
    elif(function_name == "_mmult"):
        return parse_expr("{m1}*{m2}".format(m1 = argument_array[0], m2=argument_array[1]), evaluate=True, transformations=T[:11])
    elif(function_name == "_transpose"):
        return parse_expr("{m}.T".format(m=argument_array[0]))
    
def get_argument_values(argument_array, variable_dict):
    result = []
    for val in argument_array:
        if val in variable_dict:
            result.append(variable_dict[val])
        else:
            result.append(val)

    return result