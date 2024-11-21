import pandas as pd
from trading_algo.parameters import AlgoParameters


def trend_direction_analysis(daily_returns:pd.DataFrame, algo_params:AlgoParameters):
    

    cumulative_returns = (1 + daily_returns).ewm(span=algo_params.daily_ewm_window).mean()

    # Check if the cumulative returns are positive or negative
    positive_rets_df = cumulative_returns.iloc[-1] > 1
    negative_rets_df = cumulative_returns.iloc[-1] < 1

    # Sorted list of companies with positive and negative trends
    positive_rets_list = positive_rets_df[positive_rets_df].index.to_list()
    negative_rets_list = negative_rets_df[negative_rets_df].index.to_list()

    # sort the stocks according to the value of their cumulative returns
    stocks_pos_trend = (cumulative_returns[positive_rets_list].iloc[-1].sort_values(ascending=False).index.to_list())
    stocks_neg_trend = (cumulative_returns[negative_rets_list].iloc[-1].sort_values(ascending=True).index.to_list())

    return stocks_pos_trend, stocks_neg_trend

def trend_stability_analysis(daily_returns:pd.DataFrame, positive_stocks:pd.DataFrame, negative_stocks:pd.DataFrame):
    daily_returns_positive = daily_returns[positive_stocks]
    daily_returns_negative = daily_returns[negative_stocks]
    long_period_ewm_std_p = daily_returns_positive.ewm(span=10, min_periods=10).std() # TOOD ewm values as parameters
    long_period_ewm_std_n = daily_returns_negative.ewm(span=10, min_periods=10).std()

    mean_long_std_p = long_period_ewm_std_p.mean()
    mean_long_std_n = long_period_ewm_std_n.mean()

    positive_stocks_stable = mean_long_std_p.sort_values().dropna().index.to_list()
    negative_stocks_stable = mean_long_std_n.sort_values().dropna().index.to_list()

    return positive_stocks_stable, negative_stocks_stable
    
