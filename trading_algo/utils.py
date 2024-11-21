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