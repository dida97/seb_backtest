import pandas as pd

from trading_algo.parameters import AlgoParameters
from trading_algo.analysis import long_term
from backtester.data.manager import MarketData
from backtester.config import BKTConfig

class TradingAlgo: 
    def __init__(self, bkt_config:BKTConfig, market_data:MarketData) -> None:
        self.bkt_config = bkt_config
        self.algo_params = AlgoParameters()

        # Initialize data
        self.daily_stocks = market_data.daily_stocks
        self.intraday_stocks = market_data.intraday_stocks
        self.daily_index = market_data.daily_index
        self.intraday_index = market_data.intraday_index

        # Return variables
        self.daily_returns = pd.DataFrame()
        self.cumul_daily_returns = pd.DataFrame()

        # daily ranked companies
        ## trend direction analsys
        self.stocks_pos_trend = pd.DataFrame()
        self.stocks_neg_trend = pd.DataFrame()


    def long_term_analysis(self): 
        self.stocks_pos_trend, self.stocks_neg_trend = long_term.trend_direction_analysis(self.daily_stocks, self.algo_params)

        