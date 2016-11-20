import pandas.io.data as web
import pandas as pd
import datetime
import Markowitz
import numpy as np
import math
import pickle

#Supports long only for now.

class Position:
    def __init__(self,symbol,returns,direction,in_price,n_shares,returns_sp):
        #format for dates: "YYYY-MM-dd"
        self.symbol = symbol
        self.returns = returns
        self.direction = direction
        self.in_price = in_price
        self.n_shares = n_shares
        df = pd.concat([returns, returns_sp], axis=1)
        df = df.dropna(thresh=2, axis=0)
        df = df * 100
        c = df.cov()
        self.beta = c.iloc[0][1] / c.iloc[1][1]
            
class Portfolio:
    def __init__(self,assets,start_date,all_dates,money):
        self.start_date = start_date
        self.positions = assets
        self.symbols = [asset.symbol for asset in self.positions]
        self.returns_grid = np.array([asset.returns for asset in self.positions])
        total_amount = 0
        for asset in self.positions:
            total_amount = total_amount + asset.in_price * asset.n_shares
        self.weights = np.array([(asset.in_price * asset.n_shares)/total_amount for asset in self.positions])
        self.cash = money - total_amount
        #historical
        self.historical_dates = all_dates
        self.historical_returns = np.dot(self.weights.transpose(),self.returns_grid)
        self.covariance_matrix = np.cov(self.returns_grid)
        self.net_variance = np.dot(self.weights.T,np.dot(self.covariance_matrix,self.weights))
        self.net_expectation = np.mean(self.historical_returns)
        #actual
        self.daily_values = calculate_values(assets,start_date,total_amount)

    def get_asset_allocation(self):
        current_prices = web.DataReader([asset.symbol for asset in self.positions], 'yahoo', datetime.date.today()-datetime.timedelta(1))['Open']
        total_amount = self.cash
        for asset in self.positions:
            total_amount = total_amount + current_prices.iloc[0][asset.symbol] * asset.n_shares
        symbols = self.symbols
        symbols.append("cash")
        weights = []
        for asset in self.positions:
            weights.append((current_prices.iloc[0][asset.symbol] * asset.n_shares)/total_amount)
        weights.append(self.cash/total_amount)
        return dict(zip(symbols, weights))
    def get_values(self):
        return self.daily_values
    def get_beta(self):
        beta_pos = [pos.beta for pos in self.positions]
        return np.dot(beta_pos,self.weights)
    def get_correlation_matrix(self):
        return np.corrcoef(self.returns_grid)
    def get_sharpe_ratio(self):
        return self.net_expectation/math.sqrt(self.net_variance)
    def get_historical_returns(self):
        return pd.Series(self.historical_returns,index=self.historical_dates)
    def get_variance(self):
        return self.net_variance
    def get_historical_expectation(self):
        return self.net_expectation
    def get_tickers(self):
        return self.symbols    
    def get_optimal_portfolio(self):
        #looking back one year only. subject to change
        start_index = len(self.historical_returns)-253
        end_index = len(self.historical_returns)-1
        return_grid = self.returns_grid[:,start_index:end_index]
        weights, poly = Markowitz.optimal_portfolio_quad(return_grid,frontier=True)
        return {'weights':weights,'curve':poly}
    def compile_portfolio(self):
        in_prices = []
        directions = []
        shares = []
        for i in range(len(self.positions)):
            in_prices.append(self.positions[i].in_price)
            directions.append(self.positions[i].direction)
            shares.append(self.positions[i].n_shares)
        compilation = Portfolio_Compiled(self.symbols,shares,self.start_date,in_prices,directions,self.historical_dates,self.cash)
        return compilation
    def find_YTD_performance(self):
        with open('portfolio.txt', 'rb') as f:
            all_portfolios = pickle.load(f)
        values = []
        i = len(all_portfolios)-1
        while len(values) < 252:
            port = all_portfolios[i].uncompile()
            values.extend(port.daily_values)
            i = i - 1
            if i < 0:
                val_year_ago = 10000
                val_today = values[0]
                ytd_perf = (val_today - val_year_ago) / val_year_ago
                return ytd_perf
        val_year_ago = values[-253]
        val_today = values[-1]
        ytd_perf = (val_today - val_year_ago) / val_year_ago
        return ytd_perf
    def get_alpha(self):
        df = pd.DataFrame.from_csv("returns_data.csv")
        prices_market = list(df['^GSPC'])[len(df)-252:len(df)]
        Rm = 1
        for rm in prices_market:
            Rm = Rm * (1 + rm)
        Rm = Rm - 1
        risk_free_rate = .007
        returns_cib = self.find_YTD_performance()
        beta = self.get_beta()
        alpha = returns_cib - risk_free_rate - (Rm - risk_free_rate) * beta
        return alpha
    #backtested for now. will link to actual account history after a while of trading.
    def get_information_ratio(self):
        df = pd.DataFrame.from_csv("returns_data.csv")
        returns_market = np.array(df.iloc[-254:-1]["^GSPC"]*100)
        returns_port = self.historical_returns[-254:-1]
        sd_diff = np.std(returns_port-returns_market)
        exp_diff = np.mean(returns_port)-np.mean(returns_market)
        return exp_diff/sd_diff
    def get_exposures(self,weights):
        funds = ["XLY", "XLP", "XLE", "XLF", "XLV", "XLI", "XLB", "XLK", "XLU"]
        prices_factors = web.DataReader(funds, "yahoo", self.start_date - datetime.timedelta(1))["Close"]
        returns_factors = prices_factors.pct_change()[1:len(prices_factors)] * 100
        returns_factors["Intercept"] = np.ones(len(returns_factors))
        A = np.array(returns_factors)
        grid = self.returns_grid.T
        returns_pos = grid[len(grid)-len(returns_factors)-1:-1]
        w = np.array(weights).T
        Y = returns_pos.dot(w) * 100
        beta = np.linalg.lstsq(A, Y)[0]
        print(len(beta))
        beta = list(beta[1:-1])
        factors = ["Consumer Discretionary","Consumer Staples","Energy","Financials","Healthcare","Industrials","Materials",\
                   "Technology","Utilities"]
        return dict(zip(factors, beta))


def calculate_values(assets,start_date,first_amount):
    tickers = [asset.symbol for asset in assets]
    n_shares = [asset.n_shares for asset in assets]
    prices = web.DataReader(tickers, 'yahoo', start_date)['Close']
    values = []
    values.append(first_amount)
    for i in range(len(prices)):
        if i != 0:
           values.append(np.dot(prices.iloc[[i]], n_shares)[0])
    return values
                    
class Portfolio_Compiled:
    def __init__(self,tickers,shares,start_date,in_prices,directions,all_dates,money):
        self.tickers = tickers
        self.shares = shares
        self.start_date = start_date
        self.in_prices = in_prices
        self.directions = directions
        self.historical_dates = all_dates
        self.cash = money
    
    def uncompile_and_update(self,df):
        positions = []
        for i in range(len(self.tickers)):
                pos = Position(self.tickers[i],df[self.tickers[i]],self.directions[i],self.in_prices[i],self.shares[i],df['^GSPC'])
                positions.append(pos)
        portfolio = Portfolio(positions,self.start_date,self.historical_dates,self.cash)
        return portfolio
    
    def uncompile(self):
        df = pd.DataFrame.from_csv("returns_data.csv")
        positions = []
        for i in range(len(self.tickers)):
                pos = Position(self.tickers[i],df[self.tickers[i]],self.directions[i],self.in_prices[i],self.shares[i],df['^GSPC'])
                positions.append(pos)
        portfolio = Portfolio(positions,self.start_date,self.historical_dates,self.cash)
        return portfolio
