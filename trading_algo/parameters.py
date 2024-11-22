from datetime import datetime, timedelta
import pandas as pd 
from pandas.tseries.offsets import BDay


class AlgoParameters: 
    def __init__(self): 
        
        self.DAILY_EWM_WINDOW = 10 # we give more weight to the last 2 weeks
        
        self.LONG_TREND_DAYS = 120
        self.RANKING_DAYS = 10
        self.RESHUFFLE_FREQUENCY = 1

        self.INCLUDE_INDEX = False