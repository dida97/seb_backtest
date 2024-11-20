import logging
import sys
import os 
from backtester.config import Config
from backtester.data.manager import DataManager



def main():
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Simplified Event-Based Backtest...")
    
    # Load configuration
    logger.debug("Loading Configuration")
    config = Config() 

    # Load data
    logger.info("Loading data...")
    data_manager = DataManager(config)
    data_manager.load_data()

    # Format and Clean data
    logger.info("Formatting and cleaning data")
    data_manager.format_data()
    data_manager.clean_data()

        
if __name__ == "__main__":
    main()
