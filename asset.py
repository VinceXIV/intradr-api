from stocksymbol import StockSymbol
from difflib import SequenceMatcher
import pandas as pd


class Asset:
    def __init__(self, ticker, market="US", index=None):
        self.market = market
        self.index = index
        self.ss = StockSymbol("fb6844dd-04c4-4a1e-9596-6b451a0461b3")

        symbol_list = self.ss.get_symbol_list(market=market, index=index)
        info = dict(pd.DataFrame(symbol_list).set_index('symbol').loc[ticker, :])
        info["ticker"] = ticker

        self.info = info

    def find(self, asset_name=None, market=None, index=None):
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

    
    def __sequence_similarity(self, str1, str2):
        matcher = SequenceMatcher(None, str1, str2)
        return matcher.ratio()