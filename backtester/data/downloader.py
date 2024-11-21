import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from ..config import BKTConfig


class DataDownloader:
    def __init__(self, bkt_config:BKTConfig):
        self.sp500_tickers = self.get_sp500_tickers()
        self.index_ticker = "^GSPC"
        self.bkt_config = bkt_config
        self.data_path = self.bkt_config.data_dir

        # Initialize logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)
    
    def get_sp500_tickers(self):
        """
        Retrieves S&P 500 tickers from Wikipedia.
        """
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tickers = pd.read_html(url)[0]["Symbol"].tolist()
        
        # Handle tickers with special characters
        tickers = [ticker.replace(".", "-") for ticker in tickers]
        return tickers
    
    def download_daily_data(self):
        """
        Downloads daily data for the S&P 500 stocks and index for the last 6 months.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.bkt_config.daily_analysis_days)  # Approximately 6 months
        
        self.logger.debug(f"Downloading daily data from {start_date.date()} to {end_date.date()}...")
        
        # Download data
        stocks_data = yf.download(self.sp500_tickers, start=start_date, end=end_date, interval="1d")["Close"]
        index_data = yf.download(self.index_ticker, start=start_date, end=end_date, interval="1d")["Close"]
        
        # Save to CSV
        stocks_data.to_csv(self.bkt_config.daily_stocks_file)
        index_data.to_csv(self.bkt_config.daily_index_file)
        
        self.logger.debug("Daily data downloaded and saved.")

    def download_intraday_data(self):
        """
        Downloads 2-minute intraday data for the S&P 500 stocks and index for the last 60 days.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.bkt_config.intraday_analysis_days)
        
        self.logger.debug(f"Downloading intraday 2-minute data from {start_date.date()} to {end_date.date()}...")
        
        # Download data
        stocks_data = yf.download(self.sp500_tickers, start=start_date, end=end_date, interval="2m")["Close"]
        index_data = yf.download(self.index_ticker, start=start_date, end=end_date, interval="2m")["Close"]
        
        # Save to CSV
        stocks_data.to_csv(self.bkt_config.intraday_stocks_file)
        index_data.to_csv(self.bkt_config.intraday_index_file)
        
        self.logger.debug("Intraday data downloaded and saved.")

    def download_data(self):
        """
        Executes the downloading process for both daily and intraday data.
        """
        self.download_daily_data()
        self.download_intraday_data()
