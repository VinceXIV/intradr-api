import yfinance as yf 
import utility_functions
import pandas as pd
import re
import dates
from datetime import datetime, timedelta

class Numerical:
    def __init__(self, period = "100d", interval="1d", time_zone = None, filter=None):
        self.period = period
        self.interval = interval
        self.time_zone = time_zone
        self.filter = filter
        self.historical_data = pd.DataFrame()

    def update_defaults(self, period = "100d", interval="1d", time_zone = None, filter=["return"]):
        self.period = period
        self.interval = interval
        self.time_zone = time_zone
        self.filter = filter

    def get_numeric_info(self, ticker):
        ticker_details = yf.Ticker(ticker)

        numeric_info = []
        for key in ticker_details.info.keys():
            val = ticker_details.info[key]
            if(type(val) == int or type(ticker_details.info[key]) == float):
                numeric_info.append({"name": key, "value": val})

        return numeric_info

    def get_historical_data(self, ticker, period = None, interval=None, time_zone = None, filter=None, backdate=0):
        period = period if period != None else self.period
        interval = interval if interval != None else self.interval
        time_zone = time_zone if time_zone != None else self.time_zone
        filter = filter if filter != None else self.filter

        if(type(ticker) != str):
            raise("Sorry, we only process one ticker at a time, and thus expect a string for the ticker argument")
        
        if(backdate == 0):
            return self.__get_historical_data(ticker, period, interval, time_zone, filter)
        elif(backdate > 0):
            # backdating means returning results assuming we are running the script n number of days ago. 
            # if backdate = 10, it means we are running this function 10 days ago.
            old_period_count = int(re.findall(r"\d+", period)[0])
            period_count = str(old_period_count + backdate)
            period_length = re.findall(r"[a-zA-Z]+", period)[0]
            new_period =  period_count + period_length

            if(len(self.historical_data) < old_period_count + backdate):
                self.historical_data = self.__get_historical_data(ticker, new_period, interval, time_zone, filter)

            if(interval == None):
                return self.__get_historical_data(ticker, new_period, interval, time_zone, filter)
            else:
                return self.__slice_data_by_date(historical_data = self.historical_data, period=period, backdate=backdate)
        

    
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
            field_name_snake_cased = utility_functions.snake_case(field)
            ticker_info["average_" + field_name_snake_cased] = data_mean[field]
            ticker_info["max_" + field_name_snake_cased] = data_max[field]
            ticker_info["min_" + field_name_snake_cased] = data_min[field]
            ticker_info["stdev_" + field_name_snake_cased] = data_stdev[field]

            return ticker_info
        
    def __get_historical_data(self, ticker, period, interval, time_zone, filter):
        # Add 1 to the period. For instance, if the period is 1d, add one so it becomes 2d
        # we are doing this because when calculating daily return, the first value will be NaN
        # and we don't want that NaN in our dataframe
        period_count = str(int(re.findall(r"\d+", period)[0])+1)
        period_length = re.findall(r"[a-zA-Z]", period)[0]
        period =  period_count + period_length

        data = yf.download(tickers=ticker, period=period, interval=interval, progress=False)
        data = data.index.tz_convert(time_zone) if time_zone != None else data
        data = data.reset_index("Date")
        data.columns = [utility_functions.snake_case(colname) for colname in data.columns]

        data['return'] = data["adj_close"].pct_change()

        # Remove the one record containing NaN in the "return" column
        data = data.iloc[1:,]

        if(filter != None):
            return data[filter]
        else:
            return data
    
    def __slice_data_by_date(self, historical_data, period, backdate):
        # period is expected to come in the form; "10d", "1wk", "1mo", etc.,
        # where d = day, wk = week, mo = month. Old period count extracts the
        # digit part of it. so if it is 11wk, old period count will be 11
        old_period_count = int(re.findall(r"\d+", period)[0])

        # Here, we add the backdate period. Backdate is expected to be an 
        # integer. so if we extracted 11 above, we simply add the backdate
        period_count = str(old_period_count + backdate)

        # We extract the letter part of the period. I mentioned initially that
        # the period can come in the form "10d", "1wk", "1mo", etc. period length
        # will be "d", "wk", "mo", etc
        period_length = re.findall(r"[a-zA-Z]+", period)[0]

        start_period =  period_count + period_length

        # dates.get_date() takes in a string in the form "1d" and returns a 
        # datetime.date object corresponding to the date. For instance, "1d"
        # simply means one day ago. So it returns the datetime object that
        # can be coerced into a string in the form <year>-<month>-<day> e.g "2023-05-1"
        start_date = dates.get_date(start_period)  
        end_date = dates.get_date(str(backdate)+period_length)

        after_startdate_mask = historical_data['date'].dt.date >= start_date
        before_enddate_mask = historical_data['date'].dt.date <= end_date

        return historical_data[after_startdate_mask & before_enddate_mask]
    
    def __slice_data_by_period(self, historical_data, period, backdate):
        # period is expected to come in the form; "10d", "1wk", "1mo", etc.,
        # where d = day, wk = week, mo = month. Old period count extracts the
        # digit part of it. so if it is 11wk, old period count will be 11
        end_period = historical_data.index.max() - int(re.findall(r"\d+", period)[0])

        # Here, we add the backdate period. Backdate is expected to be an 
        # integer. so if we extracted 11 above, we simply add the backdate
        start_period = historical_data.index.max() - (end_period + backdate)

        start_period_mask = historical_data.index >= start_period
        end_period_mask = historical_data.index <= end_period

        return historical_data[start_period_mask & end_period_mask]




        