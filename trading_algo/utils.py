import numpy as np
import pandas as pd

def rank_lists(post_analysis_lists: list[list], stocks_ranking_dictionary:dict):
    for stock_list in post_analysis_lists:
        max_score = len(stock_list)
        for i, element in enumerate(stock_list):
            if not element in stocks_ranking_dictionary:
                stocks_ranking_dictionary[element] = max_score - i
            else:
                stocks_ranking_dictionary[element] += max_score - i

    ranking = pd.Series(stocks_ranking_dictionary)

    sorted_ranking = ranking[stock_list].sort_values(ascending=False)
    result_list = sorted_ranking.index.to_list()

    return result_list

def value_at_risk(returns: pd.DataFrame):
        returns.dropna(inplace=True)
        confidence_level = 0.05
        # Calculate the mean and standard deviation of daily returns
        mean_return = returns.mean()
        std_dev = returns.std()

        # Calculate the Z-score for the confisdence level
        z_score = np.percentile(returns, 100 * (1 - confidence_level))
        var = mean_return - z_score * std_dev
        return var

def intraday_max_drawdown(max_drawdown_df, cumul_rets_df:pd.DataFrame, stocks_df:pd.DataFrame): 
    drawdown = (cumul_rets_df[stocks_df] / cumul_rets_df[stocks_df].cummax() - 1)
    max_drawdown = abs(drawdown.min())

    return pd.concat([max_drawdown_df, max_drawdown], axis=1)

def intraday_var(day, var_df, intraday_stocks_returns:pd.DataFrame, stocks_df:pd.DataFrame, negative_returns=False): 
    confidence = 0.05
    returns_sign_correction = -1 if negative_returns else 1 # *-1 because we want the sign to be positive for VaR computation
    returns = intraday_stocks_returns[day][stocks_df] * returns_sign_correction
    zscore = np.percentile(returns ,100 * (1 - confidence))
    mean = intraday_stocks_returns[day][stocks_df].mean()
    std = intraday_stocks_returns[day][stocks_df].std()
    var = mean - zscore * std
    return pd.concat([var_df, var], axis=1)