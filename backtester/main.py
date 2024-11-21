import logging
import sys
import os 
from backtester.config import BKTConfig
from backtester.data.manager import DataManager
from trading_algo.algo import TradingAlgo


def main():
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    
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

    trading_algo.long_term_analysis()

    
if __name__ == "__main__":
    main()
