from stocksymbol import StockSymbol
from difflib import SequenceMatcher
import pandas as pd
from ssm import *


class Asset:
    def __init__(self, ticker, market="US", index=None):
        self.market = market
        self.index = index
        self.ss = StockSymbol(sym)

        symbol_list = self.ss.get_symbol_list(market=market, index=index)
        info = dict(pd.DataFrame(symbol_list).set_index('symbol').loc[ticker, :])
        info["ticker"] = ticker

        self.info = dict(info)

    def get(self):
        return self.info
    
    def find(self, asset_name=None, market=None, index=None):
        '''
        Takes in a name (e.g micros) and returns the name of the company
        that matches that the most. It is used for searching company
        tickers using their names
        '''
        market = market if market != None else self.market
        index = index if index != None else self.index

        if(asset_name == None):
            return self.ss.get_symbol_list(market=market, index=index)
        else:
            market_data = pd.DataFrame(self.ss.get_symbol_list(market=market, index=index))

        distances = []
        for asset in market_data["shortName"]:
            distances.append(self.__sequence_similarity(asset.lower(), asset_name.lower()))

        highest_similarity = distances.index(max(distances))

        return market_data.iloc[highest_similarity, :]

    # Matches two strings and provides a value that indicates
    # how similar the two values are    
    def __sequence_similarity(self, str1, str2):
        matcher = SequenceMatcher(None, str1, str2)
        return matcher.ratio()