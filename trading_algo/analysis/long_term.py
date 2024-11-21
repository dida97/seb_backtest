import pandas as pd
from trading_algo.parameters import AlgoParameters


def trend_direction_analysis(daily_stocks:pd.DataFrame, algo_params:AlgoParameters):
    try: # TODO remove this try-except
        daily_returns = (daily_stocks.loc[algo_params.start_date_daily: algo_params.trading_day, :].pct_change()).drop(columns=["VLTO", "ADSK"]) # data not available for VLTO
    except KeyError:
        daily_returns = (daily_stocks.loc[algo_params.start_date_daily: algo_params.trading_day, :].pct_change())

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
