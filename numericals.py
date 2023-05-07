import yfinance as yf 
import utility_functions

class Numerical:
    def __init__(self, period = "100d", interval="1d", time_zone = None, filter=None):
        self.period = period
        self.interval = interval
        self.time_zone = time_zone
        self.filter = filter

    def update_defaults(self, period = "100d", interval="1d", time_zone = None, filter=["Return"]):
        self.period = period
        self.interval = interval
        self.time_zone = time_zone
        self.filter = filter

    def get_numeric_info(self, ticker):
        ticker_details = yf.Ticker(ticker)

        numeric_info = {}
        for key in ticker_details.info.keys():
            val = ticker_details.info[key]
            if(type(val) == int or type(ticker_details.info[key]) == float):
                numeric_info[key] = val

        return numeric_info