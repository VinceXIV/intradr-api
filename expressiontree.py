from sympy import parse_expr, postorder_traversal
import re

def get_ordered_operations(str_expr):
    '''
    Takes in an expression such as "x^2 + y^2" and returns ['x**2', 'y**2', 'x**2 + y**2'],
    which basically means we will have to solve "x**2" first, then "y**2", and finally
    "x**2 + y**2"
    '''
    parsed_str = parse_expr(str_expr, evaluate=False, transformations="all")

    operators = r'([+\-*/%^(){}\[\]]|\*\*)'

    ordered_operations = []
    for ar in postorder_traversal(parsed_str):
        if(re.findall(operators, str(ar))):
            ordered_operations.append(str(ar))

    return ordered_operations

def get_operators(expr, min_operators = 1, max_operators = 2):
    '''
    We are only expecting simple expressions here (e.g "x + y"). This function returns the operators
    in that expression. In the case of "x + y", it will return "+"
    '''

    expr = process_expression(expr)
    pattern = r'(\w+)'
    for i in re.findall(pattern, expr):
        expr = expr.replace(i, "")

    if(len(expr) not in range(min_operators, max_operators)):
        raise ValueError(
            "The expression contains {} operators which is out of the expected range".format(len(expr))
        )
    return expr

def get_operants(expr):
    '''
    We are only expecting simple expressions here (e.g "x + y"). This function returns the operants
    in that expression. In the case of "x + y", it will return ["x", "y"]
    '''
    expr = process_expression(expr)
    operator = get_operators(expr=expr)

    return expr.split(operator)

def process_expression(expr):
    '''
    Removes spaces and non alpha
    '''

    if(len(re.findall('\*{3,}', expr)) > 0):
        print(re.findall('\*{3,}', expr))
        # This will be raised if an expression contains more than 2 * e.g (y *** 3)
        raise ValueError("The expression contains invalid values")  
    elif(len(re.findall(r'\w+\s+\w+', expr))):
        print(re.findall(r'\w+\s+\w+', expr))
        raise ValueError("The expression contains operants with no operator")
    elif(len(re.findall(r'([^+\-*/%^{}\(\)\[\]\w\s])', expr)) > 0):
        print(re.findall(r'([^+\-*/%^{}\(\)\[\]\w\s])', expr))
        # This can be raised when a user calls this method with "X & Y"
        # This error is raised because & is neither considered a math operator
        # nor a valid operant
        raise ValueError("The expression contains invalid values")
    else:
        return re.sub(r' ', "", expr)

# Returns true if the string is in the form "x + y" (the + can be a -, /, %, etc.) and false otherwise 
def contains_operators(str_expression):
    return len(get_operators(str_expression, 0, 2)) > 0

def solve_expression(expr, variable_dict):
    ordered_operations = get_ordered_operations(expr)

    for operation in ordered_operations:
        # I want to be able to solve an expression containing as much as 10 operators
        # e.g "x + 10 + y + j + abc + blahblahblah..."
        operator = get_operators(expr, min_operators = 1, max_operators = 10)
