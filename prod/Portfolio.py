import pandas.io.data as web
import pandas as pd
import datetime
import Markowitz
import numpy as np
import math

class Position:
    def __init__(self,symbol,returns,direction,in_price,weight):
        #format for dates: "YYYY-MM-dd"
        self.symbol = symbol
        self.returns = returns
        self.direction = direction
        self.in_price = in_price
        self.weight = weight
        if direction == "long":
            self.returns *= 100
        else:
            self.returns *= -100
            
class Portfolio:
    def __init__(self,assets,start_date,all_dates):
        self.start_date = start_date
        self.positions = assets
        self.symbols = [asset.symbol for asset in self.positions]
        self.returns_grid = np.array([asset.returns for asset in self.positions])
        self.weights = np.array([asset.weight for asset in self.positions])
        #historical
        self.historical_dates = all_dates
        self.historical_returns = np.dot(self.weights.transpose(),self.returns_grid)
        self.covariance_matrix = np.cov(self.returns_grid)
        self.net_variance = np.dot(self.weights.T,np.dot(self.covariance_matrix,self.weights))
        self.net_expectation = np.mean(self.historical_returns)
        #actual
        self.daily_values = calculate_profits(assets,self.historical_returns,start_date,all_dates)
                
    def optimal_portfolio(self):
        #looking back one year only. subject to change
        start_index = len(self.returns)-253
        end_index = len(self.returns)-1
        return_grid = self.returns_grid[:,start_index:end_index]
        weights, poly = Markowitz.optimal_portfolio_quad(return_grid,frontier=True)
        return {'weights':weights,'curve':poly}
    
    def compile_portfolio(self):
        in_prices = []
        directions = []
        for i in range(len(self.positions)):
            in_prices.append(self.positions[i].in_price)
            directions.append(self.positions[i].direction)
        compilation = Portfolio_Compiled(self.symbols,self.start_date,self.weights,in_prices,directions,self.daily_values,self.net_variance,self.net_expectation,self.historical_dates)
        return compilation

def calculate_profits(assets,historical_returns,start_date,all_dates):
        #calculate first return taking into account price at which PM entered position
        first_return = 0
        for asset in assets:
            first_price = web.DataReader(asset.symbol,'yahoo',start_date)['Close'][0]
            r = 100*(first_price - asset.in_price)/asset.in_price
            if asset.direction != 'long':
                r = -r
            first_return = first_return + r
        #find index of first date
        for i in range(len(all_dates)-1,0,-1):
            if (start_date - all_dates[i].to_datetime()).days == 0:
                return np.insert(historical_returns[i:len(historical_returns)],0,first_return)    
    
    
    
class Portfolio_Compiled:
    def __init__(self,tickers,start_date,initial_weights,in_prices,directions,returns,net_variance,net_expectation,all_dates):
        self.tickers = tickers
        self.start_date = start_date
        self.in_prices = in_prices
        self.directions = directions
        self.initial_weights = initial_weights
        self.net_returns = returns
        self.net_variance = net_variance
        self.net_expectation = net_expectation
        self.historical_dates = all_dates
    
    def uncompile(self,df):
        positions = []
        for i in range(self.tickers):
                pos = Position(self.tickers[i],df[self.tickers[i]],self.directions[i],self.in_prices[i],self.initial_weights[i])
                positions.append(pos)
        portfolio = Portfolio(positions,self.start_date,self.historical_dates)
        return portfolio      