import re
import numpy as np
import copy
from numericals import Numerical
from sympy.parsing.sympy_parser import parse_expr
import expressiontree

class Expression:
    def __init__(self, str_expression, portfolio_assets = [], variable_dict = {}, 
                 period = "100d", interval="1d", time_zone = None, filter=None):
        self.numerical = Numerical(period = period, interval=interval, time_zone = time_zone, filter=filter)
        self.variable_dict = variable_dict
        self.expression = str_expression

        # These functions return a matrix. It can be (1, n), (n, 1) or (n, n) matrices 
        self.matrix_functions = [
            "_mmult", "_transpose"
        ]

        # These functions are created by simply using the asset's name and quoting what
        # value from that asset you want. They come in two flavors; three argument, and two 
        # argument functions. the two variable one is considered "simple" as its evaluation
        # returns a value. The three argument one is considered complex as its evaluation returns
        # an array. An example of a complex asset function is "_AAPL(return, 10d, 1d)"
        # which returns an array for the apple's return in the last ten days sampled daily.
        # An example of a complex one is "_AAPL(price, 1d)", which returns apple's stock price one
        # day ago
        self.asset_functions = ["_"+i for i in portfolio_assets]

        
    def evaluate(self, str_expression=None, variable_dict = {}):
        variable_dict = self.variable_dict if variable_dict == {} else variable_dict
        str_expression = self.expression if str_expression == None else str_expression

        # This function returns an object of arrays in the form {__AAPL: [], min: []}.
        # The arrays, on the other hand, are in the form; 
        # ["_AAPL(return, 10d, 1d)", "_MSFT(return, 10d, 1d)"]
        simple_functions_used = self.get_simple_asset_functions(str_expression)

        # Here, the f_expression_results will end up being in the form
        # {"_AAPL(return, 10d, 1d): 0.01, _MSFT(return, 10d, 1d): 0.03}
        # with the key values being in string. Since the initial expression is
        # in string format (e.g x = "_MSFT(return, 10d, 1d) + 10x + 60"),
        # we can thus simply string replace these values with whatever we get from
        # f_expression_results below
        f_expression_results = {}
        for f in simple_functions_used:
            for expression in simple_functions_used[f]:
                val = self.__evaluate_simple_asset_function(function_name=f, expression=expression)
                f_expression_results[expression] = val

        for key in f_expression_results:
            str_expression = str_expression.replace(key, str(f_expression_results[key]))

        # At this point, we have replaced all simple functions with values they evaluate to
        # for instance, if the function is "_AAPL(return, 10d, 1d)", we have evaluated
        # that and got the a values (e.g 0.1), for which we replace in the initial expression.
        # If there are still some functions that return matrices, we deal with them in
        # evaluate_complex_functions()
        non_simple_functions = self.get_functions_used(str_expression)

        if len(non_simple_functions) > 0:
            return self.__parse_complex_expression(str_expression, variable_dict)
        else:
            return self.__parse_simple_expression(str_expression, variable_dict)
    
    # This function returns an object of arrays in the form {__AAPL: [], min: []}.
    # The arrays, on the other hand, are in the form; 
    # ["_AAPL(return, 10d, 1d)", "_MSFT(return, 10d, 1d)"]
    def get_simple_asset_functions(self, str_expression = None):
        str_expression = str_expression if str_expression != None else self.expression

        simple_functions = {}
        for f in self.asset_functions:
            if(f in str_expression):
                regex = r"{f}\(\s*\w+\s*,\s*\w+\s*\)".format(f=f)
                
                available_functions = re.findall(regex, str_expression)
                if(len(available_functions)):
                    simple_functions[f] = available_functions 

        return simple_functions

    def get_matrix_functions(self, str_expression = None):
        str_expression = str_expression if str_expression != None else self.expression

        matrix_functions = {}
        for f in self.matrix_functions:
            if(f in str_expression):
                regex = r"{f}\(\w+,\s*\w+,\s*\w+\)".format(f=f)
                
                matrix_functions[f] = re.findall(regex, str_expression)

        return matrix_functions
                
    # Takes in simple_functions in the form "_AAPL(return, 1d)"
    # and returns the solution, which in this case is apple's return 1 day ago
    def __evaluate_simple_asset_function(self, function_name, expression):
        f = function_name

        # If an expression is like _AAPL(return, 1d). I separate them such that
        # I get ticker = AAPL, val = return, period = 10d, and interval = 1m
        variables = expression.replace(f+"(", "").replace(")", "").replace(" ", "").split(",")
        ticker = function_name.replace("_", "")
        val = variables[0]
        period = variables[1]
        
        historical_data = self.numerical.get_historical_data(ticker=ticker, period=period)

        return str(float(historical_data.iloc[0, :][val]))
    
    def __evaluate_complex_function(self, function_name, str_expression, variable_dict={}):
        if function_name in self.asset_functions:
            variables = str_expression.replace(function_name+"(", "").replace(")", "").replace(" ", "").split(",")
            ticker = function_name.replace("_", "")
            val = variables[0]
            period = variables[1]   
            interval = variables[2]    

            historical_data = self.numerical.get_historical_data(ticker, period, interval)
            return np.matrix(list(historical_data[val]))
        else:
            function_arguments = self.get_function_arguments(str_expression)
            print(function_arguments)
            return 0
       

    
    # This method accepts a string such as
    # "_mmult(_mmult(_transpose(Portfolio_weights), Portfolio_return), Portfolio_weights)"
    # in string format and returns the innermost function, which in this case is
    # "_transpose(_Portfolio_weights)". The return will be of array type (we may have multiple
    # inner functions) so effectively our return from above will be ["_transpose(_Portfolio_weights)"]
    # We want to do this because in such a nested case, we want to
    # evaluate innermost functions first before we proceed with the outer ones
    # The function also accepts the number of arguments, which it uses to construct the
    # regex for extracting the innermost function
    def get_innermost_functions(self, str_expression = None, min_arg_count=1, max_arg_count=3):
        str_expression = str_expression if str_expression != None else self.expression

        # The ",\s*\w+" extracts a single argument. We want to be flexible with the
        # number of arguments we can extract. For instance, if we wnat to extract
        # an inner function that accepts two arguments, the regex for that will
        # be r"\w+\(\w+\s*,\s*\w+\)". That is what we are doing here
        innermost_functions = []

        for arg_count in range(min_arg_count, max_arg_count+1):
            r = "".join([",\s*\w+\s*" for i in range(arg_count)]) + r"\)"
            regex = r"\w+\(\s*\w+\s*" + r
            innermost_functions.extend(re.findall(regex, str_expression))

        return innermost_functions 
    
    # Receives a string in the form "average(var1, var2, var3)" and returns "average"
    def get_function_name(self, expr):
        regex = r"\w+(?=\()"
        return re.findall(regex, expr)[0]
    
    # Receives a string in the form "average(var1, var2, var3)" and returns [var1, var2, var3]
    def get_function_arguments(self, expr):
        return re.findall(r"(?<=\().+(?=\))", expr)[0].replace(" ", "").split(",")
    
    # Takes in an expression such as
    # "_mmult(_transpose(_AAPL(return, 10d, 1d) - _avg(_AAPL(return, 10d, 1d)), _AAPL(return, 10d, 1d) - _avg(_AAPL(return, 10d, 1d))"
    # and returns all the functions in that expression. In this case, it will return ["_mmult", "_transpose", "_AAPL", "_avg"]
    def get_functions_used(self, expr = None):
        expr = expr if expr != None else self.expression
        regex = r"\w+(?=\()"
        return re.findall(regex, expr)

    def __parse_simple_expression(self, str_expression, variable_dict):
        return float(parse_expr(str_expression, evaluate=True, local_dict=variable_dict, transformations="all"))
    
    def __parse_complex_expression(self, str_expression, variable_dict):
        expr = copy.deepcopy(str_expression)
        intermediate_solutions = {}
        innermost_functions = self.get_innermost_functions(expr)

        for function_expression, i in zip(innermost_functions, range(len(innermost_functions))):
            function_name = self.get_function_name(function_expression)
            result = self.__evaluate_complex_function(function_name, function_expression, intermediate_solutions)

            results_id = self.__get_intermediate_results_id(str_expression=function_expression, append=i)
            intermediate_solutions[results_id] = result
            expr = expr.replace(function_expression, results_id)
            print(i)

        print(expr)
        return expr
    
    def __get_intermediate_results_id(self, str_expression, append):
        '''
        Takes in an expression such as "_AAPL(return, 5d) + _AAPL(return, 10d, 1d)" and returns
        "AAPLreturn5dAAPLreturn10d1d"
        '''
        pattern = r'[^\w]|_'
        results_id = re.sub(pattern, "", str_expression) + "_" + str(append)

        return results_id


    
