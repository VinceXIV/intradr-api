from stocksymbol import StockSymbol
from difflib import SequenceMatcher
import pandas as pd


class Asset:
    def __init__(self):
        self.ss = StockSymbol("fb6844dd-04c4-4a1e-9596-6b451a0461b3")

    def find(self, asset_name=None, market="US", index=None):
        if(asset_name == None):
            return self.ss.get_symbol_list(market=market, index=index)
        else:
            market_data = pd.DataFrame(self.ss.get_symbol_list(market=market, index=index))

        distances = []
        for asset in market_data["shortName"]:
            distances.append(self.__sequence_similarity(asset.lower(), asset_name.lower()))

        highest_similarity = distances.index(max(distances))
        print(highest_similarity)
        return market_data.iloc[highest_similarity, :]

    
    def __sequence_similarity(self, str1, str2):
        matcher = SequenceMatcher(None, str1, str2)
        return matcher.ratio()