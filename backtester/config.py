import os

class BKTConfig:
    def __init__(self):
        # Data settings
        self.data_dir = os.path.join(os.getcwd(), "data")
        self.sp500_tickers_file = os.path.join(self.data_dir, "sp500_tickers.txt")
        self.sp500_sectors_file = os.path.join(self.data_dir, "sp500_sectors.txt")
        self.daily_stocks_file = os.path.join(self.data_dir, "daily_stocks.csv")
        self.intraday_stocks_file = os.path.join(self.data_dir, "intraday_stocks.csv")
        self.daily_index_file = os.path.join(self.data_dir, "daily_index.csv")
        self.intraday_index_file = os.path.join(self.data_dir, "intraday_index.csv")
        
        # Backtest settings
        self.trading_day = "2023-09-11"
        self.instruments_number = 5
        self.notional = 1_000_000
        
        # Trading algo settings
        self.long_trend_days = 120
        self.ranking_days = 10
        self.reshuffle_frequency = 1

        # Output settings
        self.results_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(self.results_dir, exist_ok=True)
