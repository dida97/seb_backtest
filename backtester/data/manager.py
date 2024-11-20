import pandas as pd
from ..config import BKTConfig

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
            self.daily_stocks = pd.read_csv(self.config.daily_stocks_file, sep=";")
            self.intraday_stocks = pd.read_csv(self.config.intraday_stocks_file, sep=";")
            self.daily_index = pd.read_csv(self.config.daily_index_file, sep=";")
            self.intraday_index = pd.read_csv(self.config.intraday_index_file, sep=";")

            
        except FileNotFoundError as e:
            raise Exception(f"Data file not found: {e}")
        

    def format_data(self):
        """
        Format mrket_data so that the index column is Datetime.
        """
        self.daily_stocks["Date"] = pd.to_datetime(self.daily_stocks["Date"], dayfirst=True)
        self.daily_index["Date"] = pd.to_datetime(self.daily_index["Date"], dayfirst=True)
        self.intraday_stocks["Datetime"] = pd.to_datetime(self.intraday_stocks["Datetime"], dayfirst=True)
        self.intraday_index["Datetime"] = pd.to_datetime(self.intraday_index["Datetime"], dayfirst=True)
        
        self.daily_stocks.set_index("Date", inplace=True)
        self.daily_index.set_index("Date", inplace=True)
        self.intraday_stocks.set_index("Datetime", inplace=True)
        self.intraday_index.set_index("Datetime", inplace=True)

    def clean_data(self): 
        """
        Remove empty points by forward filling
        """
        self.daily_stocks.ffill()
        self.daily_index.ffill()
        self.intraday_stocks.ffill()
        self.intraday_index.ffill()
