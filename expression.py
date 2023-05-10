import re
from numericals import Numerical
from sympy.parsing.sympy_parser import parse_expr

class Expression:
    def __init__(self, str_expression, portfolio_assets = [], variable_dict = {}, 
                 period = "100d", interval="1d", time_zone = None, filter=None):
        self.numerical = Numerical(period = period, interval=interval, time_zone = time_zone, filter=filter)
        self.variable_dict = variable_dict
        self.expression = str_expression

        # functions that are expected to come in the form
        # <function name>(<asset_variable>, <period> <interval>)
        # e.g "average(AAPL_portfolio, 10d, 1d)"
        # I am calling them simple functions because they return a value.
        # Like, if you call _average(AAPL_return, 10d, 1d), you will get
        # value like 10
        self.simple_functions = [
            "_average", "_max", "_min", "_stdev"
        ]

        # These functions return a matrix. It can be (1, n), (n, 1) or (n, n) matrices 
        self.matrix_functions = [
            "_mmult", "_transpose",
            "_return", "_volume", "_price"
        ]

        # These functions are created by simply using the asset's name and quoting what
        # value from that asset you want. For instance, you can write "_AAPL(return, 10d, 1d)"
        # and you should get an array for the apple's return in the last ten days sampled daily
        self.asset_functions = ["_"+i for i in portfolio_assets]

        
    def evaluate(self, str_expression=None, variable_dict = {}):
        variable_dict = self.variable_dict if variable_dict == {} else variable_dict
        str_expression = self.expression if str_expression == None else str_expression

        # This function returns an object of arrays in the form {average: [], min: []}.
        # The arrays, on the other hand, are in the form; 
        # ["average(variable1, varable2, variable3)", "min(variable1, variable2, variable3)"]
        # We expect variable1 to be the asset (e.g AAPL_return), while variable2 and variable3
        # shows the period and interval that we can use with yfinance to get info on them
        simple_functions_used = self.get_simple_functions(str_expression)

        # Here, the f_expression_results will end up being in the form
        # {average(AAPL_return, 10d, 1m): 100, max(MSFT_vol, 15d, 1m): 50000}
        # with the key values being in string. Since the initial expression is
        # in string format (e.g x = "average(AAPL_return, 10d, 1m) + 10x + 60"),
        # we can thus simply string replace these values with whatever we get from
        # f_expression_results below
        f_expression_results = {}
        for f in simple_functions_used:
            for expression in simple_functions_used[f]:
                val = self.__evaluate_simple_function(function_=f, expression=expression)
                f_expression_results[expression] = val

        for key in f_expression_results:
            str_expression = str_expression.replace(key, str(f_expression_results[key]))

        # At this point, we have replaced all simple functions with values they evaluate to
        # for instance, if the function is "_average(AAPL_return, 10d, 1d)", we have evaluated
        # that and got the a values (e.g 10), for which we replace in the initial expression.
        # If there are still some functions that return matrices, we deal with them in
        # evaluate_complex_functions()
        if self.contains_non_simple_functions():
            return self.__parse_complex_expression(str_expression, variable_dict)
        else:
            return self.__parse_simple_expression(str_expression, variable_dict)
    
    # This function returns an object of arrays in the form {average: [], min: []}.
    # The arrays, on the other hand, are in the form; 
    # ["average(variable1, varable2, variable3)", "min(variable1, variable2, variable3)"]
    # We expect variable1 to be the asset (e.g AAPL_return), while variable2 and variable3
    # shows the period and interval that we can use with yfinance to get info on them
    def get_simple_functions(self, str_expression = None):
        str_expression = str_expression if str_expression != None else self.expression

        simple_functions = {}
        for f in self.simple_functions:
            if(f in str_expression):
                regex = r"{f}\(\w+,\s*\w+,\s*\w+\)".format(f=f)
                
                simple_functions[f] = re.findall(regex, str_expression)

        return simple_functions

    def get_matrix_functions(self, str_expression = None):
        str_expression = str_expression if str_expression != None else self.expression

        matrix_functions = {}
        for f in self.matrix_functions:
            if(f in str_expression):
                regex = r"{f}\(\w+,\s*\w+,\s*\w+\)".format(f=f)
                
                matrix_functions[f] = re.findall(regex, str_expression)

        return matrix_functions
                
    # Takes in simple_functions in the form "average(AAPL_return, 10d, 1m)" (**it is in string format**)
    # and returns the solution to the expression also in string format
    def __evaluate_simple_function(self, function_, expression):
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

        if(f == "_average"):
            return historical_data.mean()
        elif(f == "_max"):
            return historical_data.max()
        elif(f == "_min"):
            return historical_data.min()
        elif(f == "_stdev"):
            return historical_data.std()
    
    # This method accepts a string such as
    # "_mmult(_mmult(_transpose(Portfolio_weights), Portfolio_return), Portfolio_weights)"
    # in string format and returns the innermost function, which in this case is
    # "_transpose(_Portfolio_weights)". The return will be of array type (we may have multiple
    # inner functions) so effectively. So our return from above will be ["_transpose(_Portfolio_weights)"]
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
        return re.findall(regex, expr)
    
    # Receives a string in the form "average(var1, var2, var3)" and returns [var1, var2, var3]
    def get_arguments(self, expr):
        return re.findall(r"(?<=\().+(?=\))", expr)[0].replace(" ", "").split(",")
    
    # Takes in an expression such as
    # what(and, now, this, thes(whatever_what, aver_age(now, its, tough), inner(this, is, it) 1d))'
    # and returns the functions in that expression. In this case, it will return ['what', 'thes', 'aver_age', 'inner']
    def get_functions_used(self, expr = None):
        expr = expr if expr != None else self.expression
        regex = r"\w+(?=\()"
        return re.findall(regex, expr)
    
    def contains_non_simple_functions(self, expr):
        functions_used = self.get_functions_used(expr)

        for f in functions_used:
            if f in self.matrix_functions or f in self.asset_functions:
                return True
            
        return False

    def __parse_simple_expression(self, str_expression, variable_dict):
        return float(parse_expr(str_expression, evaluate=True, local_dict=variable_dict, transformations="all"))
    
    def __parse_complex_expression(self, str_expression, variable_dict):
        pass

    
