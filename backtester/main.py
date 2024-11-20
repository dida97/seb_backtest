import logging
import sys
import os 
from backtester.config import BKTConfig
from backtester.data.manager import DataManager

from trading_algo.config import AlgoConfig



def main():
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Simplified Event-Based Backtest...")
    
    # Load configuration
    logger.debug("Loading Configuration")
    config = BKTConfig() 

    # Load data
    logger.info("Loading data...")
    data_manager = DataManager(config)
    data_manager.load_data()

    # Format and Clean data
    logger.info("Formatting and cleaning data")
    data_manager.format_data()
    data_manager.clean_data()

    # Initialize the trading algorithm

        
if __name__ == "__main__":
    main()
