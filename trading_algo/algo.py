from datetime import datetime
import numpy as np
import pandas as pd

from trading_algo.parameters import AlgoParameters
from backtester.data.manager import MarketData
from backtester.config import BKTConfig
import trading_algo.utils as algo_utils

class LongTermAnalysis: 
    def __init__(self, trading_algo:'TradingAlgo'): 
        self.trading_algo = trading_algo
        
    def trend_direction_analysis(self):
        cumulative_returns = (1 + self.trading_algo.daily_returns).ewm(span=self.trading_algo.algo_params.DAILY_EWM_WINDOW).mean()

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
    def __init__(self, trading_algo:'TradingAlgo') -> None:
        self.trading_algo = trading_algo

        self.stocks_intraday_cumrets = pd.DataFrame()
        
        # Stocks' rankings for intraday analysis
        self.intraday_positive = pd.DataFrame()
        self.intraday_negative = pd.DataFrame()
        self.intraday_max_dd_pos = pd.DataFrame()
        self.intraday_max_dd_neg = pd.DataFrame()
        self.intraday_var_pos = pd.DataFrame()
        self.intraday_var_neg = pd.DataFrame()

    def intraday_trend_analysis(self, date):
        def compute_returns(grouped_data):
            cum_returns = {}
            pct_rets = {}
            for day, group in grouped_data:
                intraday_data = group[pd.to_datetime("09:35:00").time() : pd.to_datetime("15:45:00").time()] #TODO start of the day should be parametrized 
                pct_change = intraday_data.pct_change(fill_method=None).fillna(0)
                cum_ret = ((1 + pct_change).cumprod().fillna(1)) 
                cum_returns[day] = cum_ret
                pct_rets[day] = pct_change
            return cum_returns, pct_rets

        def find_trend_count(cum_rets: dict[pd.DataFrame], valid_companies, sign: str):
            cum_rets_list = [elem.iloc[-1] for elem in cum_rets.values()]
            cumprod_group = pd.concat(cum_rets_list, axis=1).T
            if sign == "positive":
                cumprod_group = cumprod_group[valid_companies]
                trend_count = cumprod_group[cumprod_group[:] > 1]
            else:
                cumprod_group = cumprod_group[valid_companies]
                trend_count = cumprod_group[cumprod_group[:] < 1]

            return trend_count.count()


        intraday_stocks = self.trading_algo.intraday_stocks.loc[self.trading_algo.start_date_intraday : date, :]
        intraday_index = self.trading_algo.intraday_index.loc[self.trading_algo.start_date_intraday : date, :]

        grouped_stocks = intraday_stocks.groupby(intraday_stocks.index.date)
        grouped_index = intraday_index.groupby(intraday_index.index.date)

        self.index_indtraday_cumrets = compute_returns(grouped_index)[0]
        stock_returns = compute_returns(grouped_stocks)
        self.stocks_intraday_cumrets = stock_returns[0]
        self.stocks_intraday_rets = stock_returns[1]
        valid_positive_intraday = [stock for stock in list(self.stocks_intraday_cumrets.values())[0].columns if stock in self.trading_algo.stocks_pos_trend]
        valid_negative_intraday = [stock for stock in list(self.stocks_intraday_cumrets.values())[0].columns if stock in self.trading_algo.stocks_neg_trend]

        # index_intraday_rets = compute_returns(grouped_index)
        trend_count_positive = find_trend_count(self.stocks_intraday_cumrets, valid_positive_intraday, "positive").sort_values(ascending=False)
        trend_count_negative = find_trend_count(self.stocks_intraday_cumrets, valid_negative_intraday, "negative").sort_values(ascending=False)

        # stocks are ranked on the basis of how many days the intraday trend followed the multi-day trend
        self.intraday_positive = trend_count_positive.index.to_list()
        self.intraday_negative = trend_count_negative.index.to_list()

    def intraday_stability_analysis(self):
        # drawdown, rsi, VaR

        for day, df in self.stocks_intraday_cumrets.items():

            # drawdown
            self.intraday_max_dd_pos = algo_utils.intraday_max_drawdown(self.intraday_max_dd_pos, df, self.intraday_positive)
            self.intraday_max_dd_neg = algo_utils.intraday_max_drawdown(self.intraday_max_dd_neg, df, self.intraday_negative)

            # var
            self.intraday_var_pos = algo_utils.intraday_var(day, self.intraday_var_pos, self.stocks_intraday_rets, self.intraday_positive)
            self.intraday_var_neg = algo_utils.intraday_var(day, self.intraday_var_neg, self.stocks_intraday_rets, self.intraday_negative, negative_returns=True)
       
        
        self.intraday_max_dd_neg = (self.intraday_max_dd_neg.T.ewm(span=5, min_periods=1).mean().iloc[-1]) # TODO ewm 1 week -> parametrize
        self.intraday_max_dd_pos = (self.intraday_max_dd_pos.T.ewm(span=5, min_periods=1).mean().iloc[-1])
        self.intraday_var_pos = (self.intraday_var_pos.T.ewm(span=5, min_periods=1).mean().iloc[-1])
        self.intraday_var_neg = (self.intraday_var_neg.T.ewm(span=5, min_periods=1).mean().iloc[-1])

        self.intraday_max_dd_neg = self.intraday_max_dd_neg.sort_values(ascending=False)
        self.intraday_max_dd_pos = self.intraday_max_dd_pos.sort_values(ascending=False)
        self.intraday_var_pos = self.intraday_var_pos.sort_values(ascending=False)
        self.intraday_var_neg = self.intraday_var_neg.sort_values(ascending=False)  
    
    
    def perform_analysis(self, date): 
        self.intraday_trend_analysis(date)
        self.intraday_stability_analysis()

    def aggregate_intraday_analysis(self): 
        self.best_positive_intraday = algo_utils.rank_lists([self.intraday_positive,self.intraday_max_dd_pos.index,self.intraday_var_pos.index,], self.trading_algo.stocks_ranking_dictionary)
        self.best_negative_intraday = algo_utils.rank_lists([self.intraday_negative,self.intraday_max_dd_neg.index,self.intraday_var_neg.index,], self.trading_algo.stocks_ranking_dictionary)

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

        # Useful variables 
        self.start_date_daily = datetime.min
        self.start_date_intraday = datetime.min
        self.bkt_days_count = 1
        self.daily_prt_beta_list = []        

        # Return variables
        self.daily_returns = pd.DataFrame() # TODO consider to add as attribute of LongTermAnalysis
        
        # Stock's ranking for daily analysis
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
        self.selected_stocks_with_scores = list()
        
    def aggregate_total_analysis(self):
        self.best_positive = algo_utils.rank_lists([self.long_term_analysis.best_positive_daily, self.short_term_analysis.best_positive_intraday], self.stocks_ranking_dictionary)
        self.best_negative = algo_utils.rank_lists([self.long_term_analysis.best_negative_daily, self.short_term_analysis.best_negative_intraday], self.stocks_ranking_dictionary)

        # The number of stocks to buy and to sell is determined on the basis 
        # of the length of self.best_positive and self.best_negative
        majority_leg = int(self.bkt_config.instruments_number / 2) + 1
        minority_leg = self.bkt_config.instruments_number - majority_leg
        long_instr_n = (majority_leg if len(self.best_positive) > len(self.best_negative) else minority_leg)
        short_instr_n = self.bkt_config.instruments_number - long_instr_n
        
        instruments_list = (self.best_negative[:short_instr_n] + self.best_positive[:long_instr_n])
        self.selected_stocks_with_scores = sorted([stock for stock in self.stocks_ranking_dictionary.items() if stock[0] in instruments_list],key=lambda x: x[1],reverse=True)

    def create_portfolio(self):
        """
        self.selected_stocks_with_scores is [('AAPL', 1000), ('MSFT', 2000), ...]
        each tuple inside is first converted into a list, so that its content is modifiable
        at the end, the lists are converted back to tuples 
        """
        scores_sum = sum([stock[1] for stock in self.selected_stocks_with_scores])

        for idx, stock in enumerate(self.selected_stocks_with_scores):
            stock = list(stock)
            name = stock[0]
            weight = stock[1]
            # check sign of the trend of the company
            if name in self.short_term_analysis.intraday_positive:
                stock.append(1)
            else:
                stock.append(-1)

            stock[1] = int((weight / scores_sum) * self.bkt_config.notional)

            self.selected_stocks_with_scores[idx] = tuple(stock)
        self.portfolio = [stock[0] for stock in self.selected_stocks_with_scores]

    def compute_portfolio_beta(self):
        self.portfolio = [stock[0] for stock in self.selected_stocks_with_scores]
        total_invested = sum([stock[1] for stock in self.selected_stocks_with_scores])

        tot_intraday_stocks_returns = pd.concat(self.short_term_analysis.stocks_intraday_cumrets)
        tot_intraday_index_returns = pd.concat(self.short_term_analysis.index_indtraday_cumrets)
        total_intraday_cumrets = pd.concat([tot_intraday_stocks_returns[self.portfolio], tot_intraday_index_returns],axis=1)
        total_intrday_returns = total_intraday_cumrets.pct_change(fill_method=None).fillna(0)

        cov_matrix = total_intrday_returns.cov()

        market_var = cov_matrix["^GSPC"]["^GSPC"]

        # Step 1 compute stocks values
        beta_values = {}
        for ticker in total_intrday_returns.columns[:-1]:
            cov = cov_matrix["^GSPC"][ticker]
            beta = cov / market_var
            beta_values[ticker] = beta

        # Step 2 compute initial portfolio beta
        portfolio_beta = 0
        for ticker, weight, position in self.selected_stocks_with_scores:
            weight = abs(weight) / total_invested
            stock_beta = (beta_values[ticker] if ticker in beta_values else 0)  # Use 0 if beta is not available
            portfolio_beta += (weight * stock_beta * position)


        self.portfolio_beta = portfolio_beta
        self.daily_prt_beta_list.append(self.portfolio_beta) # compute the avg portfolio beta in the stats processing

    def reset_daily_ranking(self, date): 
        trading_day = datetime.strptime(date, "%Y-%m-%d")
        trading_day = np.datetime64(trading_day, 'D')
        start_date_daily = np.datetime64(self.start_date_daily, 'D')
        business_days = np.busday_count(start_date_daily, trading_day)
        if business_days >= 132: # TODO 6 months -> parametrize
            return True
        else:
            return False 

    def reset_intraday_ranking(self, date): 
        trading_day = datetime.strptime(date, "%Y-%m-%d")
        trading_day = np.datetime64(trading_day, 'D')
        start_date_intraday = np.datetime64(self.start_date_intraday, 'D')
        business_days = np.busday_count(start_date_intraday, trading_day)
        if business_days >= 44: # TODO 2 month -> parametrize
            return True
        else:
            return False

    def start_trading(self, date): 
        backtest_day_stocks_data = self.intraday_stocks.loc[date, self.portfolio]
        backtest_day_index_data = self.intraday_index.loc[date]
        backtest_day_data = pd.concat([backtest_day_stocks_data, backtest_day_index_data], axis=1)
        backtest_day_data = backtest_day_data[pd.to_datetime("09:35:00").time() : pd.to_datetime("15:45:00").time()] # TODO these should be parametrized

        pct_returns = backtest_day_data.pct_change(fill_method=None).fillna(0)
        pct_cumret = (pct_returns + 1).cumprod() - 1
        
        end_of_day_notional = pd.DataFrame()
        for instrument in self.portfolio + ["^GSPC"]:
            for spec in self.selected_stocks_with_scores:
                if instrument in spec:
                    size = spec[1]
                    pos_sign = spec[2]
            end_of_day_notional = pd.concat([end_of_day_notional,pd.DataFrame(((pct_cumret[instrument] * size * pos_sign) + size))],axis=1)

        idx_cumret = pct_cumret["^GSPC"]
        idx_end_of_day_notional = idx_cumret * self.bkt_config.notional + self.bkt_config.notional
        if self.algo_params.INCLUDE_INDEX == False: 
            end_of_day_notional = end_of_day_notional.drop(columns=["^GSPC"])

        end_of_day_notional = self.intraday_position_management(end_of_day_notional)

        prt_commissions = self.compute_commissions(date,end_of_day_notional)
        idx_commissions = self.compute_commissions(date,idx_end_of_day_notional,is_index=True)
        # compute commissions for the day  
        prt_daily_commission = prt_commissions[0]
        idx_daily_commission = idx_commissions[0]

        # produce the list of trades of the day 
        self.produce_list_of_trades_v2(end_of_day_notional, prt_commissions[1])        

        intraday_prt_vol = end_of_day_notional["prt"].std() / self.bkt_config.notional
        self.prt_intraday_volas.append(intraday_prt_vol)

        intraday_idx_vol = idx_end_of_day_notional.std() / self.bkt_config.notional
        self.idx_intraday_volas.append(intraday_idx_vol)
 

        prt_trad_ret_gross = (end_of_day_notional["prt"].iloc[-1] - end_of_day_notional["prt"].iloc[0])

        prt_trad_ret = (prt_trad_ret_gross) - prt_daily_commission
        self.list_idx_ret.append(prt_trad_ret)

        prt_perc_ret = (prt_trad_ret / end_of_day_notional["prt"].iloc[0])

        prt_drawdown = (
            end_of_day_notional["prt"] / end_of_day_notional["prt"].cummax() - 1
        )

        prt_max_drawdown = abs(prt_drawdown.min())

        self.total_commission += prt_daily_commission


        # comparison with index : 

        idx_trad_ret_gross = (
            idx_end_of_day_notional.iloc[-1] - idx_end_of_day_notional.iloc[0]
        ) 

        # idx_spread_costs = idx_end_of_day_notional.iloc[0]*0.0004
        # idx_commission_costs = 6.58
        # idx_trad_ret = (idx_trad_ret_gross) - idx_spread_costs - idx_commission_costs
        idx_trad_ret = (idx_trad_ret_gross) - idx_daily_commission

        idx_perc_ret = (
            (idx_trad_ret / idx_end_of_day_notional.iloc[0]) 
        )
        idx_drawdown = (
            idx_end_of_day_notional / idx_end_of_day_notional.cummax() - 1
        )
        idx_max_drawdown = abs(idx_drawdown.min())

        # self.total_idx_spread += idx_spread_costs 
        # self.total_idx_commission += idx_commission_costs
        # self.idx_total_commission += (idx_spread_costs + idx_commission_costs)
        self.idx_total_commission += idx_daily_commission

        # self.idx_average_invested += (
        #     self.global_sorted[-1][1] - self.idx_average_invested
        # ) / self.days_count
        

        # print(f"Stats for trading day: {self.trading_day}")
        # print(self.global_sorted)
        self.operative_sets_list.append(self.portfolio)
        # if "idx" in [instr[0] for instr in self.global_sorted]:
        #     print("index in operative set!")
        #     time.sleep(2)
        # invested = sum([cmp[1] for cmp in self.global_sorted])
        # print(f"total invested : {invested}")
        # print(f"portfolio beta : {self.portfolio_beta}")

        # print("Prt Stats")
        # ic(prt_trad_ret)
        # ic(prt_perc_ret)
        # ic(prt_max_drawdown)
        
        # try:
        self.total_gross_return += prt_trad_ret_gross
        self.total_return += prt_trad_ret
        self.idx_total_gross_return  += idx_trad_ret_gross 
        self.idx_total_return += idx_trad_ret

        # except TypeError:
        #     self.total_return += 0 # TODO perché ho messo questo try except?
        #     self.idx_total_return += 0 

        self.total_perc_ret = self.total_return / self.notional # TODO cambiare questo : non investo sempre 1 milione
        self.max_drawdown = (
            prt_max_drawdown
            if prt_max_drawdown > self.max_drawdown
            else self.max_drawdown
        )

        self.total_idx_perc_ret = self.idx_total_return / self.notional
        self.idx_max_drawdown = (
            idx_max_drawdown
            if idx_max_drawdown > self.idx_max_drawdown 
            else self.idx_max_drawdown
        )

        # self.avg_drawdown += (self.max_drawdown - self.avg_drawdown) / self.days_count
        # self.idx_avg_drawdown += (self.idx_max_drawdown - self.idx_avg_drawdown) / self.days_count

        self.avg_drawdown += (prt_max_drawdown - self.avg_drawdown) / self.days_count
        self.idx_avg_drawdown += (idx_max_drawdown - self.idx_avg_drawdown) / self.days_count

        # print(f"Total Portfolio P&L: {round(self.total_return,2)} $")
        # print(f"Total Portfolio %P&L: {round(total_perc_ret*100, 3)} %")
        # print(f"Total Commission paid: {round(self.total_commission,2)} $")
        # print(f"Total prt Max Drawdown: {round(self.max_drawdown*100, 3)} %")
        # print(f"Avg prt Max Drawdown: {round(self.avg_drawdown*100, 3)} %")
        # print(f"Avg portfolio Beta: {round(self.avg_portfolio_beta, 3)}")
        self.avg_drawdown_list.append(self.avg_drawdown)
        self.avg_idx_drawdown_list.append(self.idx_avg_drawdown)
        self.max_drawdown_list.append(self.max_drawdown)
        self.max_idx_drawdown_list.append(self.idx_max_drawdown)

        #     print("self.avg_drawdown_list")
        #     print(self.avg_drawdown_list)

        #     print("self.avg_idx_drawdown_list")
        #     print(self.avg_idx_drawdown_list)

        #     print("self.max_drawdown_list")
        #     print(self.max_drawdown_list)

        #     print("self.max_idx_drawdown_list")
        #     print(self.max_idx_drawdown_list)

        #     print(sum(self.max_drawdown_list) / len(self.max_drawdown_list))       

        #     sys.exit()
        # ic(self.total_return)
        # ic(total_perc_ret)
        # ic(self.total_commission)
        # ic(self.max_drawdown)
        # ic(self.avg_drawdown)
        # ic(self.avg_portfolio_beta)
        # print("\n")
        # print("Idx only stats")
        # ic(idx_trad_ret)
        # ic(idx_perc_ret)
        # ic(idx_max_drawdown)

        # print(f"Total Index P&L: {round(self.idx_total_return,2)} $")
        # print(f"Total Index %P&L: {round(total_idx_perc_ret*100, 3)} %")
        # print(f"Total Commission paid: {round(self.idx_total_commission,2)} $")
        # print(f"Total Idx Max Drawdown: {round(self.idx_max_drawdown*100, 3)} %")
        # print(f"Avg Idx Max Drawdown: {round(self.idx_avg_drawdown*100, 3)} %")

        # ic(self.idx_total_return)
        # ic(self.idx_total_commission)
        # ic(total_idx_perc_ret)
        # ic(self.idx_max_drawdown)
        # ic(self.idx_avg_drawdown)


        this_day_prt_return = pd.DataFrame.from_dict({"date" : self.trading_day, "ret":prt_perc_ret}, orient="index")
        self.daily_prt_returns_list = pd.concat([self.daily_prt_returns_list, this_day_prt_return], axis=1)

        this_day_idx_return = pd.DataFrame.from_dict({"date" : self.trading_day, "ret":idx_perc_ret}, orient="index")
        self.daily_idx_returns_list = pd.concat([self.daily_idx_returns_list, this_day_idx_return], axis=1)

    def compute_commissions(self,date, portfolio_data:pd.DataFrame, is_index=False):
        if not is_index:
            instruments = portfolio_data.columns.to_list()[:-1]
            prices = self.intraday_stocks.loc[date, instruments].iloc[0,:]
            shares_n = np.ceil((portfolio_data.iloc[0,:-1].divide(prices)))

        else:  
            prices = self.intraday_index.loc[date].iloc[0]
            shares_n = np.ceil((portfolio_data.iloc[0]/ prices))


        COMMISSION_PER_TRADE = 0.02
        TRADES_PER_SHARE = 2
        daily_commission = (shares_n * COMMISSION_PER_TRADE*TRADES_PER_SHARE)
        
        return daily_commission.sum(), daily_commission 


    def intraday_position_management(self, notional_invested:pd.DataFrame, is_index_only=False): 
        '''
        '''
        notional_invested["prt"] = notional_invested.sum(axis=1)

        drawdown = notional_invested["prt"] / notional_invested["prt"].cummax() - 1
        drawdown_filter = drawdown[(abs(drawdown) >= 0.6*abs(self.idx_avg_drawdown)) & (abs(drawdown) > 0.0)]

        if self.idx_avg_drawdown != 0.0 and not drawdown_filter.empty:
            notional_invested = notional_invested.loc[:drawdown_filter.index[0]]
        
        starting_notional = notional_invested["prt"].iloc[0]
        perc_cumret = (notional_invested["prt"] / starting_notional) - 1 

        profits = notional_invested[perc_cumret >= 0.006] # XXX parametri importanti da valutare 
        losses = notional_invested[perc_cumret <= -0.003]
        filtered_notional = pd.concat([profits, losses], axis=0)
        # filtered_notional = losses.copy()
        if filtered_notional.empty:
            return notional_invested
        filtered_notional = filtered_notional.sort_index()
        notional_invested = notional_invested.loc[:filtered_notional.index[0]]
        return notional_invested


    def run(self, date): 
        # Set the start dates for daily and intraday analyses 

        self.daily_returns = (self.daily_stocks.loc[self.start_date_daily: date, :].pct_change(fill_method=None))

        # PRE TRADE ANALYSIS
        ## Daily analysis
        self.long_term_analysis.perform_analysis()
        self.long_term_analysis.aggregate_daily_analysis()
        
        ## Intraday analysis
        self.short_term_analysis.perform_analysis(date)
        self.short_term_analysis.aggregate_intraday_analysis()

        ## Total analysis
        self.aggregate_total_analysis()

        ## Portfolio construction 
        self.create_portfolio()
        self.compute_portfolio_beta()

        # START_TRADING
        self.start_trading(date)

        # Check if the ranking dictionary needs to be reset
        if self.reset_daily_ranking(date): 
            self.stocks_ranking_dictionary = {}
            # Reset daily start date to 3 months prior 
            self.start_date_daily = datetime.strftime(datetime.strptime(date, "%Y-%m-%d") - pd.DateOffset(months=3), format="%Y-%m-%d")

        if self.reset_intraday_ranking(date): 
            # Reset intraday start date to 3 months prior 
            self.start_date_intraday = datetime.strftime(datetime.strptime(date, "%Y-%m-%d") - pd.DateOffset(months=1), format="%Y-%m-%d")

    def stop(self): 
        pass


