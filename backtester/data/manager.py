import pandas as pd
from ..config import BKTConfig

class MarketData: 
    def __init__(self, daily_stocks:pd.DataFrame, intraday_stocks:pd.DataFrame, daily_index:pd.DataFrame, intraday_index:pd.DataFrame):
        self.daily_stocks = daily_stocks
        self.intraday_stocks = intraday_stocks
        self.daily_index = daily_index
        self.intraday_index = intraday_index

class DataManager:
    def __init__(self, config:BKTConfig):
        self.config = config
        self.daily_stocks = pd.DataFrame()
        self.intraday_stocks = pd.DataFrame()
        self.daily_index = pd.DataFrame()
        self.intraday_index = pd.DataFrame()

    def load_data(self):
        """
        Load and return the datasets for S&P500 stocks and indices.
        """
        try:
            self.daily_stocks = pd.read_csv(self.config.daily_stocks_file, sep=",")
            self.intraday_stocks = pd.read_csv(self.config.intraday_stocks_file, sep=",")
            self.daily_index = pd.read_csv(self.config.daily_index_file, sep=",")
            self.intraday_index = pd.read_csv(self.config.intraday_index_file, sep=",")

            
        except FileNotFoundError as e:
            raise Exception(f"Data file not found: {e}")
        
    def format_data(self):
        """
        Format mrket_data so that the index column is Datetime.
        """
        
        self.daily_stocks[self.daily_stocks.columns[0]] = pd.to_datetime(self.daily_stocks[self.daily_stocks.columns[0]])
        self.daily_index[self.daily_index.columns[0]] = pd.to_datetime(self.daily_index[self.daily_index.columns[0]])
        self.intraday_stocks[self.intraday_stocks.columns[0]] = pd.to_datetime(self.intraday_stocks[self.intraday_stocks.columns[0]])
        self.intraday_index[self.intraday_index.columns[0]] = pd.to_datetime(self.intraday_index[self.intraday_index.columns[0]])
        
        self.daily_stocks.set_index(self.daily_stocks.columns[0], inplace=True, drop=True)
        self.daily_index.set_index(self.daily_index.columns[0], inplace=True, drop=True)
        self.intraday_stocks.set_index(self.intraday_stocks.columns[0], inplace=True, drop=True)
        self.intraday_index.set_index(self.intraday_index.columns[0], inplace=True, drop=True)

    def clean_data(self): 
        """
        Remove empty points by forward filling
        """
        self.daily_stocks.ffill()
        self.daily_index.ffill()
        self.intraday_stocks.ffill()
        self.intraday_index.ffill()
        

    def return_data(self) -> MarketData: 
        return MarketData(self.daily_stocks, self.intraday_stocks, self.daily_index, self.intraday_index)
