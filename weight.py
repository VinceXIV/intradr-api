from numericals import Numerical
from expression import Expression

class Weight:
    def __init__(self, portfolio_tickers=[], raw_calculations="", signals=[],
                 period = "100d", interval="1d", time_zone = None, filter=["Return"]):
        
        self.numerical = Numerical(period, interval, time_zone, filter)
        self.portfolio_tickers = portfolio_tickers if type(portfolio_tickers) == list else [portfolio_tickers]
        self.raw_calculations = raw_calculations
        self.signals = signals
        self.variable_dict = self.get_variable_dict()

        self.__updateVariableDict(raw_calculations)

    def update_numericals(self):
        self.numerical.update_defaults(period = "100d", interval="1d", time_zone = None, filter=["Return"])

    def get_weight():
        pass

    def evaluate_expression(self, str_expression, variable_dict = None):
        variable_dict = self.variable_dict if variable_dict == None else variable_dict
        expr = Expression(str_expression, variable_dict)

        return expr.evaluate()
    
    def get_variable_dict(self, porfolio_tickers=None, inplace=True):
        porfolio_tickers = self.portfolio_tickers if porfolio_tickers == None else porfolio_tickers

        variable_dict = {}
        for ticker in porfolio_tickers:
            numeric_info = self.numerical.get_numeric_info(ticker=ticker)

            for key in numeric_info:
                variable_dict[ticker+"_"+key] = numeric_info[key]

        if(inplace):
            self.variable_dict = variable_dict

        return variable_dict
    
    def __updateVariableDict(self, raw_calculations):
        equation_list = raw_calculations.split("\n")

        for equation in equation_list:
            equation_components = equation.split("=")
            if(len(equation_components) == 2):
                expression = equation_components[1]
                self.variable_dict[equation_components[0]] = self.evaluate_expression(expression)





