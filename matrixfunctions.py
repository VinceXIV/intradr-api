import pandas as pd
from sympy import parse_expr, Matrix
from sympy.parsing.sympy_parser import T

def call(function_name, argument_array, variable_dict={}):
    argument_array = get_argument_values(argument_array, function_name, variable_dict)
    if(function_name == "_avg"):
        return pd.Series(argument_array[0]).mean()
    elif(function_name == "_max"):
        return pd.Series(argument_array[0]).max()
    elif(function_name == "_min"):
        return pd.Series(argument_array[0]).min()
    elif(function_name == "_std"):
        return pd.Series(argument_array[0]).std()
    elif(function_name == "_var"):
        return pd.Series(argument_array[0]).var()
    elif(function_name == "_mmult"):
        return matrix_multiply_arguments(argument_array)
    elif(function_name == "_transpose"):
        return parse_expr("{m}.T".format(m=argument_array[0]), evaluate=True, transformations=T[:11])
    elif(function_name == "_matrix"):
        return matricize_arguments(argument_array)
    elif(function_name == "_matricize"):
        return matricize_scalar_variable(scalar_variable=argument_array[0], matrix_variable=argument_array[1])
    elif(function_name == "_mavg"):
        sv = pd.Series(list(argument_array[0])).mean()
        mv = argument_array[0]
        return matricize_scalar_variable(scalar_variable=sv, matrix_variable=mv)
    elif(function_name == "_mmax"):
        sv = pd.Series(list(argument_array[0])).max()
        mv = argument_array[0]
        return matricize_scalar_variable(scalar_variable=sv, matrix_variable=mv)
    elif(function_name == "_mmin"):
        sv = pd.Series(list(argument_array[0])).min()
        mv = argument_array[0]
        return matricize_scalar_variable(scalar_variable=sv, matrix_variable=mv)
    elif(function_name == "_mstd"):
        sv = pd.Series(list(argument_array[0])).std()
        mv = argument_array[0]
        return matricize_scalar_variable(scalar_variable=sv, matrix_variable=mv)
    elif(function_name == "_mvar"):
        sv = pd.Series(list(argument_array[0])).var()
        mv = argument_array[0]
        return matricize_scalar_variable(scalar_variable=sv, matrix_variable=mv)
    elif(function_name == "_greater"):
        val1 = argument_array[0]
        val2 = argument_array[1]
        return float(val1 > val2)
    elif(function_name == "_greater_or_equal"):
        val1 = argument_array[0]
        val2 = argument_array[1]
        return float(val1 >= val2)
    elif(function_name == "_less"):
        val1 = argument_array[0]
        val2 = argument_array[1]
        return float(val1 < val2)
    elif(function_name == "_less_or_equal"):
        val1 = argument_array[0]
        val2 = argument_array[1]
        return float(val1 <= val2)
    elif(function_name == "_equal"):
        val1 = argument_array[0]
        val2 = argument_array[1]
        return float(val1 == val2)        
    elif(function_name == "_not_equal"):
        val1 = argument_array[0]
        val2 = argument_array[1]
        return float(val1 != val2)        

def get_argument_values(argument_array, function_name, variable_dict):
    result = []
    for val in argument_array:
        if val in variable_dict:
            if function_name in ["_avg", "_max", "_min", "_std", "_var", "_quantile"]:
                result.append(list(variable_dict[val]))
            else:
                result.append(variable_dict[val])
        else:
            if function_name in ["_avg", "_max", "_min", "_std", "_var", "_quantile"]:
                result.append([val])
            else:
                result.append(val)

    return result

def matricize_arguments(argument_array):
    ncols = len(argument_array)

    total_val = 0
    for arg in argument_array:
        try:
            total_val += len(arg)
        # this error will be thrown when arg is of type such as int. e.g len(0)
        # in that case, we add 1
        except TypeError:
            total_val += 1

    nrows = int(total_val / ncols)
    
    return parse_expr("Matrix({args})".format(args=argument_array)).reshape(ncols, nrows).transpose()

def matrix_multiply_arguments(argument_array):
    return parse_expr("{m1}*{m2}".format(m1 = argument_array[0], m2=argument_array[1]),evaluate=True, transformations=T[:11])

def matricize_scalar_variable(scalar_variable, matrix_variable):
    nrows, ncols = matrix_variable.shape
    return Matrix([scalar_variable for i in range(nrows * ncols)]).reshape(nrows, ncols)

