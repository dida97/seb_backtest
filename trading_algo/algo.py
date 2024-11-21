import pandas as pd

from trading_algo.parameters import AlgoParameters
from backtester.data.manager import MarketData
from backtester.config import BKTConfig
import trading_algo.utils as algo_utils

class LongTermAnalysis: 
    def __init__(self, trading_algo:'TradingAlgo'): 
        self.trading_algo = trading_algo
        
    def trend_direction_analysis(self):
        cumulative_returns = (1 + self.trading_algo.daily_returns).ewm(span=self.trading_algo.algo_params.daily_ewm_window).mean()

        # Check if the cumulative returns are positive or negative
        positive_rets_df = cumulative_returns.iloc[-1] > 1
        negative_rets_df = cumulative_returns.iloc[-1] < 1

        # Sorted list of companies with positive and negative trends
        positive_rets_list = positive_rets_df[positive_rets_df].index.to_list()
        negative_rets_list = negative_rets_df[negative_rets_df].index.to_list()

        # sort the stocks according to the value of their cumulative returns
        self.trading_algo.stocks_pos_trend = (cumulative_returns[positive_rets_list].iloc[-1].sort_values(ascending=False).index.to_list())
        self.trading_algo.stocks_neg_trend = (cumulative_returns[negative_rets_list].iloc[-1].sort_values(ascending=True).index.to_list())

    def trend_stability_analysis(self):
        daily_returns_positive = self.trading_algo.daily_returns[self.trading_algo.stocks_pos_trend]
        daily_returns_negative = self.trading_algo.daily_returns[self.trading_algo.stocks_neg_trend]
        long_period_ewm_std_p = daily_returns_positive.ewm(span=10, min_periods=10).std() # TOOD ewm values as parameters
        long_period_ewm_std_n = daily_returns_negative.ewm(span=10, min_periods=10).std()

        mean_long_std_p = long_period_ewm_std_p.mean()
        mean_long_std_n = long_period_ewm_std_n.mean()

        self.trading_algo.pos_stocks_stable = mean_long_std_p.sort_values().dropna().index.to_list()
        self.trading_algo.neg_stocks_stable = mean_long_std_n.sort_values().dropna().index.to_list()

        
    def daily_var_analysis(self):
        
        # Calculate daily VaR for each stock with positive trend
        pos_var_stocks = {}
        self.daily_var_for_stocks(pos_var_stocks, self.trading_algo.stocks_pos_trend)

        # Calculate daily VaR for each stock with negative trend
        neg_var_stocks = {}
        self.daily_var_for_stocks(neg_var_stocks, self.trading_algo.stocks_neg_trend)

        sorted_positive_companies = sorted(pos_var_stocks.items(), key=lambda x: x[1], reverse=True)
        sorted_negative_companies = sorted(neg_var_stocks.items(), key=lambda x: x[1], reverse=True)

        # ordered by safest companies
        self.trading_algo.pos_stock_best_var = list(dict(sorted_positive_companies).keys())
        self.trading_algo.neg_stock_best_var = list(dict(sorted_negative_companies).keys())


    def daily_var_for_stocks(self, stocks_vars:dict, stocks):
        for stock in stocks:
            stock_daily_returns = self.trading_algo.daily_returns[stock]
            var = algo_utils.value_at_risk(stock_daily_returns)
            stocks_vars[stock] = var

    def perform_analysis(self): 
        self.trend_direction_analysis()
        self.trend_stability_analysis()
        self.daily_var_analysis()
    
    def aggregate_daily_analysis(self):
        self.best_positive_daily = algo_utils.rank_lists([self.trading_algo.stocks_pos_trend,self.trading_algo.pos_stocks_stable,self.trading_algo.pos_stock_best_var], self.trading_algo.stocks_ranking_dictionary)
        self.best_negative_daily = algo_utils.rank_lists([self.trading_algo.stocks_neg_trend,self.trading_algo.neg_stocks_stable,self.trading_algo.neg_stock_best_var], self.trading_algo.stocks_ranking_dictionary)


class ShortTermAnalysis: 
    def __init__(self, trading_algo) -> None:
        self.trading_algo = trading_algo


class TradingAlgo: 
    def __init__(self, bkt_config:BKTConfig, market_data:MarketData) -> None:
        self.bkt_config = bkt_config
        self.long_term_analysis = LongTermAnalysis(self)
        self.short_term_analysis = ShortTermAnalysis(self)
        
        self.algo_params = AlgoParameters()

        # Initialize data
        self.daily_stocks = market_data.daily_stocks
        self.intraday_stocks = market_data.intraday_stocks
        self.daily_index = market_data.daily_index
        self.intraday_index = market_data.intraday_index

        # Return variables
        self.daily_returns = pd.DataFrame()
        self.cumul_daily_returns = pd.DataFrame()

        # daily ranked companies
        ## trend direction analsys
        self.stocks_pos_trend = pd.DataFrame()
        self.stocks_neg_trend = pd.DataFrame()
        ## trend stability analysis
        self.pos_stocks_stable = pd.DataFrame() 
        self.neg_stocks_stable = pd.DataFrame()
        ## daily var analysis
        self.pos_stock_best_var = pd.DataFrame()
        self.neg_stock_best_var = pd.DataFrame()

        self.stocks_ranking_dictionary = {}


    def run(self, date): 
        self.daily_returns = (self.daily_stocks.loc[self.algo_params.start_date_daily: date, :].pct_change())
        self.long_term_analysis.perform_analysis()
        self.long_term_analysis.aggregate_daily_analysis()

    def stop(self): 
        pass


