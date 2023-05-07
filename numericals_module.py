import yfinance as yf 

class Numerical:
    def __init__(self, start_time = None, end_time = None, interval_time = None):
        self.start_time = start_time
        self.end_time = end_time
        self.interval_time = interval_time

    def get_numeric_info(self, ticker):
        ticker_details = yf.Ticker(ticker)

        numeric_info = {}
        for key in ticker_details.info.keys():
            val = ticker_details.info[key]
            if(type(val) == int or type(ticker_details.info[key]) == float):
                numeric_info[key] = val

        return numeric_info