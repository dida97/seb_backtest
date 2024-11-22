import logging
from datetime import datetime
from tqdm import tqdm
import sys
import os 
from backtester.config import BKTConfig
from backtester.data.manager import DataManager
from trading_algo.algo import TradingAlgo
import backtester.utils as utils

class Backtester: 
    def __init__(self, trading_algo:TradingAlgo) -> None:
        self.algo = trading_algo
        self.backtest_day = datetime.strptime(self.algo.algo_params.trading_day, "%Y-%m-%d")
        self.backtest_days = self.get_backtest_days()
        

    def get_backtest_days(self): 
        backtest_days = self.algo.daily_stocks.loc[self.algo.algo_params.trading_day:]
        return sorted(set(backtest_days.index), reverse=False)

    def start_backtest(self): 
        """
        For each day we convert the date to a string... For the moment it is too much refactoring to use only datetimes
        """
        for date in tqdm(self.backtest_days): # We should not use trading_day because we can use date
            date = datetime.strftime(date, "%Y-%m-%d")
            if not self.algo.stop(): 
                
                # Let the algo perform its actions
                self.algo.run(date)


def main():
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    
    # Ensure data availability
    utils.ensure_data_availability()

    logger.info("Starting Simplified Event-Based Backtest...")
    
    # Load configuration
    logger.debug("Loading Configuration")
    bkt_config = BKTConfig() 

    # Load data
    logger.info("Loading data...")
    data_manager = DataManager(bkt_config)
    data_manager.load_data()

    # Format and Clean data
    logger.info("Formatting and cleaning data")
    data_manager.format_data()
    data_manager.clean_data()

    # Initialize the trading algorithm
    logger.info("Initializing Trading Algorithm")
    trading_algo = TradingAlgo(bkt_config, data_manager.return_data())
    del data_manager

    backtester = Backtester(trading_algo)

    backtester.start_backtest()

    
if __name__ == "__main__":
    main()
