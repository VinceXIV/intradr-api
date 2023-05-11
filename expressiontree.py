from sympy import parse_expr, postorder_traversal
import re

def get_order_of_operations(str_expr):
    '''
    Takes in an expression such as "x^2 + y^2" and returns ['x**2', 'y**2', 'x**2 + y**2'],
    which basically means we will have to solve "x**2" first, then "y**2", and finally
    "x**2 + y**2"
    '''
    parsed_str = parse_expr(str_expr, evaluate=False, transformations="all")

    operators = r'([+\-*/%^=(){}\[\]]|\*\*)'

    order_of_operations = []
    for ar in postorder_traversal(parsed_str):
        if(re.findall(operators, str(ar))):
            order_of_operations.append(str(ar))

    return order_of_operations