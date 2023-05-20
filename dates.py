import numpy as np
import re
from datetime import datetime

def get_date(str_periods_ago):
    '''
    Receives the number of periods ago in terms of days, weeks, months or years,
    converts the periods to days, and returns the date. For instance, one can pass
    "10d" as an argument for which the function will return date in the form 
    "2023-05-09". Other periods in which the function supports include wk, y, and mo
    '''

    # If one passes "10d", returns "d", if one passes 3wk, returns "wk"
    period = re.findall(r"[a-zA-Z]+", str_periods_ago)[0]

    if(period == "d"):
        return get_business_days_ago(int(re.findall(r"\d+", str_periods_ago)[0]))
    elif(period == "wk"):
        return get_business_days_ago(7 * int(re.findall(r"\d+", str_periods_ago)[0]))
    elif(period == "mo"):
        return get_business_days_ago(30 * int(re.findall(r"\d+", str_periods_ago)[0]))
    elif(period == "y"):
        return get_business_days_ago(365 * int(re.findall(r"\d+", str_periods_ago)[0]))

def get_business_days_ago(n):
    '''
    Returns the date for the day that happened n business days ago
    '''
    
    today = datetime.today().date()
    business_days = np.busday_offset(today, -n, roll='backward', weekmask='1111100')

    return business_days.astype(datetime).strftime('%Y-%m-%d')
