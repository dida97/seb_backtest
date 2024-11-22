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
        self.instruments_number = 5
        self.notional = 1_000_000
        
        # Trading algo settings
        self.LONG_TREND_DAYS = 120
        
        self.daily_data_days = 180
        self.intraday_data_days = 60        

        # we use this as a starting point for backtest start (meaning 2 weeks after the first intraday data day)
        self.intraday_days_buffer = 14 

        self.RANKING_DAYS = 10
        self.RESHUFFLE_FREQUENCY = 1

        # Output settings
        self.results_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(self.results_dir, exist_ok=True)
