import trading_algo.parameters as parameters
from backtester.data.manager import MarketData

class TradingAlgo: 
    def __init__(self, bkt_config, market_data:MarketData) -> None:
        self.bkt_config = bkt_config
        
        # Initialize data
        self.daily_stocks = market_data.daily_stocks
        self.intraday_stocks = market_data.intraday_stocks
        self.daily_index = market_data.daily_index
        self.intraday_index = market_data.intraday_index

        