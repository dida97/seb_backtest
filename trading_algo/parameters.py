from datetime import datetime, timedelta
import pandas as pd 
from pandas.tseries.offsets import BDay


class AlgoParameters: 
    def __init__(self): 
        
        self.daily_ewm_window = 10 # we give more weight to the last 2 weeks
        
        self.long_trend_days = 120
        self.ranking_days = 10
        self.reshuffle_frequency = 1

        self.trading_day = "2024-10-21" # TODO these dates need to be expressed better 

        # set when to start the daily and the intraday analysis # TODO rivedere
        self.start_date_daily = datetime.strftime((datetime.strptime(self.trading_day, "%Y-%m-%d") - pd.DateOffset(months=3)), "%Y-%m-%d")
        self.start_date_intraday = datetime.strftime((datetime.strptime(self.trading_day, "%Y-%m-%d")- BDay(20)), "%Y-%m-%d")