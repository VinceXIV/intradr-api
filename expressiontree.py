from sympy import parse_expr, postorder_traversal, Matrix
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

    # ordered operations is in the form ['x**2', '3*x**2', 'AAPLreturn10d1d_0 + 3*x**2']
    # (This has been obtained from the expression "3x^2 + AAPLreturn10d1d_0" if you are
    # curious). It simply means when solving that expression, we should start by solving
    # "x**2" then solve for "3*x**2" (we substitute the "x**2" with solution we found
    # earlier), and we continue doing that until everything is done
    ordered_operations = get_ordered_operations(expr)

    previous_operation = ""
    previous_results = None
    for operation, i in zip(ordered_operations, len(ordered_operations)):
        # We only want to use letters when referencing variables. We are doing this because
        # the functions we are using here such as "get_operators()", and "get_operands()" expect
        # us to have only one operator by default. We don't want to change this since we are
        # solving one expression at a time. In the expression ['x**2', '3*x**2', 'AAPLreturn10d1d_0 + 3*x**2']
        # for instance, in the second round, we will have already solved for "x**2". It makes sense to give it
        # an alias that is only made up of letters so when we move to the next part, which is "3*x**2", we can
        # rewrite it using that alias. An example would be "3*abracadabra", where abracadabra = x**2
        replacement_value = get_replacement_value(str_expression=expr, append=i)
        operation_expr = operation.replace(previous_operation, replacement_value)

        variable_dict[replacement_value] = previous_results

        # I want to be able to solve an expression containing as much as 10 operators
        # e.g "x + 10 + y + j + abc + blahblahblah..."
        operator = get_operators(operation_expr, min_operators = 1, max_operators = 10)
        operand1, operand2 = get_operands(operation_expr)
        operand1, operand2 = matricize_operands(operand1, operand2, operator, variable_dict)
        results = parse_expr("{operand1}{operator}{operand2}".format(operand1, operator, operand2))

        previous_results = results
        previous_operation = operation

    return previous_operation
      

def matricize_operands(operand1, operand2, operator, variable_dict):
    # operands in variable_dict are matrics. We are checking to determine how to process
    # when one is a matrix and another one not, or when both are or are not matrics
    # We are parsing expression containing matrices slighly different from how it is done
    # in sympy which doesn't allow operations such as "3 + Matrix([1, 2, 3])". We want to
    # make such kind of operation possible in our app though, so we are extending on what
    # is offered by sympy
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
    
def get_replacement_value(str_expression, append):
    '''
    Takes in an expression such as "_AAPL(return, 5d) + _AAPL(return, 10d, 1d)" and returns
    "AAPLreturn5dAAPLreturn10d1d_1" assuming append = 1
    '''
    pattern = r'[^a-zA-Z]|_'
    results_id = re.sub(pattern, "", str_expression) + "_" + str(append)

    return results_id

    







