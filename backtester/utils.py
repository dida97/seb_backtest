import os
from backtester.config import BKTConfig
from backtester.data.downloader import DataDownloader

bkt_config = BKTConfig()

def ensure_data_availability():
    """
    Check if data files exist in the 'data' folder. If not, run the data downloader.
    """
    data_folder = bkt_config.data_dir

    required_files = [
        bkt_config.daily_stocks_file,
        bkt_config.intraday_stocks_file,
        bkt_config.daily_index_file,
        bkt_config.intraday_index_file
    ]
    
    missing_files = [
        file for file in required_files if not os.path.isfile(os.path.join(data_folder, file))
    ]
    
    if missing_files:
        print("Missing data files detected:")
        for file in missing_files:
            print(f"- {file}")
        print("\nRunning data downloader to fetch missing files...")
        downloader = DataDownloader(bkt_config)
        downloader.download_data()
        print("Data download completed.")
    else:
        print("All required data files are present.")
