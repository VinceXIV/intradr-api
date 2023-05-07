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

    def get_historical_data(self, ticker, period = None, interval=None, time_zone = None, filter=None):

        if(type(ticker) != str):
            raise("Sorry, we only process one ticker at a time, and thus expect a string for the ticker argument")
        
        period = period if period != None else self.period
        interval = interval if interval != None else self.interval
        time_zone = time_zone if time_zone != None else self.time_zone
        filter = filter if filter != None else self.filter

        data = yf.download(tickers=ticker, period=period, interval=interval)
        data = data.index.tz_convert(time_zone) if time_zone != None else data

        data['Return'] = data["Adj Close"].pct_change()

        if(filter != None):
            return data[filter]
        else:
            return data
    
    def summarize_historical_data(self, ticker, period = None, interval=None, time_zone = None, filter=None):
        ticker_info = {
            "period": self.period,
            "interval": self.interval,
            "time_zone": self.time_zone,
        }

        data = self.get_historical_data(ticker, period, interval, time_zone, filter)
        data_mean = data.mean()
        data_max = data.max()
        data_stdev = data.std()
        data_min = data.min()
  
        for field in data_mean.index:
            field_name_snake_cased = utility_functions.make_snake_case(field)
            ticker_info["average_" + field_name_snake_cased] = data_mean[field]
            ticker_info["max_" + field_name_snake_cased] = data_max[field]
            ticker_info["min_" + field_name_snake_cased] = data_min[field]
            ticker_info["stdev_" + field_name_snake_cased] = data_stdev[field]

            return ticker_info

        