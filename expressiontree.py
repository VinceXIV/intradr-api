from sympy import parse_expr, postorder_traversal, Matrix
from sympy.parsing.sympy_parser import T
import copy
import re

def get_ordered_operations(str_expr):
    '''
    Takes in an expression such as "x^2 + y^2" and returns ['x**2', 'y**2', 'x**2 + y**2'],
    which basically means we will have to solve "x**2" first, then "y**2", and finally
    "x**2 + y**2"
    '''
    parsed_str = parse_expr(str_expr, evaluate=False, transformations="all")

    ordered_operations = []
    for ar in postorder_traversal(parsed_str):
        if(len(re.findall(r'\w+', str(ar))) > 1):
            ordered_operations.append(str(ar))

    return ordered_operations

def get_operators(expr, min_operators = 1, max_operators = 2):
    '''
    We are only expecting simple expressions here (e.g "x + y"). This function returns the operators
    in that expression. In the case of "x + y", it will return "+"
    '''

    expr = clean_expression(expr)
    pattern = r'(\w+)'
    for i in re.findall(pattern, expr):
        expr = expr.replace(i, "")

    if(len(expr) not in range(min_operators, max_operators)):
        raise ValueError(
            "The expression contains {} operators which is out of the expected range".format(len(expr))
        )
    return expr

def get_operands(expr):
    '''
    We are only expecting simple expressions here (e.g "x + y"). This function returns the operants
    in that expression. In the case of "x + y", it will return ["x", "y"]
    '''
    expr = clean_expression(expr)
    operator = get_operators(expr=expr)

    return expr.split(operator)

def clean_expression(expr):
    '''
    Removes spaces and also checks whether the expression makes sense
    '''

    if(len(re.findall('\*{3,}', expr)) > 0):
        print(re.findall('\*{3,}', expr))
        # This will be raised if an expression contains more than 2 * e.g (y *** 3)
        raise ValueError("The expression contains invalid values")  
    elif(len(re.findall(r'\w+\s+\w+', expr))):
        print(re.findall(r'\w+\s+\w+', expr))
        # This will be raised when a user passes in an expression such as "2 y"
        raise ValueError("The expression contains operands with no operator")
    elif(len(re.findall(r'([^+\-.*/%^{}\(\)\[\]\w\s])', expr)) > 0):
        print(re.findall(r'([^+\-.*/%^{}\(\)\[\]\w\s])', expr))
        # This can be raised when a user calls this method with "X & Y"
        # This error is raised because & is neither considered a math operator
        # nor a valid operand in our app
        raise ValueError("The expression contains invalid values")
    else:
        return re.sub(r' ', "", expr)

# Returns true if the string is in the form "x + y" (the + can be a -, /, %, etc.) and false otherwise 
def contains_operators(str_expression):
    return len(get_operators(str_expression, 0, 2)) > 0

def solve_expression(expr, variable_dict):
    modified_expression = copy.deepcopy(expr)
    for key in variable_dict:
        if key in expr:
            modified_expression = modified_expression.replace(key, str(variable_dict[key]))

    return parse_expr(modified_expression, evaluate=True, transformations=T[:11])
      

def matricize_operands(operand1, operand2, operator, variable_dict):
    # operands in variable_dict are matrices. We are checking to determine how to process
    # when one is a matrix and another one is not, or when both are or are not matrices
    # We are parsing expression containing matrices slighly different from how it is done
    # in sympy which doesn't allow operations such as "3 + Matrix([1, 2, 3])". We want to
    # make such kind of operation possible in our app by converting the 3 into a matrix the same
    # shape as the one we want to add it to. Son the expression "3 + Matrix([1, 2, 3]) will be
    # turned into the expression Matrix([3, 3, 3]) + Matrix([1, 2, 3])". We are doing this so
    # we can use sympy to solve that expression (which by default it doesn't) for us
    if(operand1 in variable_dict and operand2 in variable_dict):
        return (operand1, operand2)
    elif(operand1 not in variable_dict and operand2 not in variable_dict):
        return (operand1, operand2)
    elif(operator != "+" and operator != "-"):
        return (operand1, operand2)
    elif(operand1 in variable_dict and operand2 not in variable_dict):
        # operand1 is a matrix while operand2 is not
        operand1 = variable_dict[operand1]
        matrix_operand_size = operand1.shape[0]*operand1.shape[1]
        transformed_operand2 = Matrix([operand2 for i in range(matrix_operand_size)])
        transformed_operand2 = transformed_operand2.reshape(operand1.shape[0], operand1.shape[1])
        return (operand1, transformed_operand2)
    elif(operand2 in variable_dict and operand1 not in variable_dict):
        # operand2 is a matrix while operand1 is not
        operand2 = variable_dict[operand2]
        matrix_operand_size = operand2.shape[0]*operand2.shape[1]
        transformed_operand1 =  Matrix([operand1 for i in range(matrix_operand_size)])
        transformed_operand1 = transformed_operand1.reshape(operand2.shape[0], operand2.shape[1]) 
        return (transformed_operand1, operand2)

# Takes in an expression such as "_AAPL(return, 5d) + _AAPL(return, 10d, 1d)" and returns
# "AAPLreturn5dAAPLreturn10d1d_1" assuming append = 1. the underscore is very important as
# it prevents sympy from interpreting an expression such as "3abc - 2" as "3*a*b*c - 2"    
def get_replacement_value(str_expression, append):
    pattern = r'[^a-zA-Z]|_'
    results_id = re.sub(pattern, "", str_expression) + "_" + str(append)

    return results_id