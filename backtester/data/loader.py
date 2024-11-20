import pandas as pd
from ..config import Config

class DataLoader:
    def __init__(self, config:Config):
        self.config = config

    def load_data(self):
        """
        Load and return the datasets for S&P500 stocks and indices.
        """
        try:
            daily_stocks = pd.read_csv(self.config.daily_stocks_file, sep=";")
            intraday_stocks = pd.read_csv(self.config.intraday_stocks_file, sep=";")
            daily_index = pd.read_csv(self.config.daily_index_file, sep=";")
            intraday_index = pd.read_csv(self.config.intraday_index_file, sep=";")

            return {
                "daily_stocks": daily_stocks,
                "intraday_stocks": intraday_stocks,
                "daily_index": daily_index, 
                "intraday_index": intraday_index
            }
        except FileNotFoundError as e:
            raise Exception(f"Data file not found: {e}")
