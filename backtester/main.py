import logging
import sys
import os 
from backtester.config import Config
from backtester.data.loader import DataLoader


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
    data_loader = DataLoader(config)
    market_data = data_loader.load_data()
        
if __name__ == "__main__":
    main()
