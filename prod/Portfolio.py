import pandas.io.data as web
import pandas as pd
import datetime
import Markowitz
import numpy as np
import math

class Position:
    def __init__(self,symbol,direction,in_price,start_date,weight,exchange,asset_class):
        #format for dates: "YYYY-MM-dd"
        self.symbol = symbol
        self.direction = direction
        self.in_price = in_price
        self.start_date = start_date
        self.exchange = exchange
        self.asset_class = asset_class
        self.weight = weight
        request = web.DataReader(symbol,'yahoo',datetime.datetime(2010, 1, 1))['Close']
        self.returns = request.pct_change()[1:len(request)-1]
        if direction == "long":
            self.returns *= 100
        else:
            self.returns *= -100

class Portfolio:
    def __init__(self,assets):
        self.positions = assets
        self.symbols = [asset.symbol for asset in self.positions]
        self.returns_grid = np.array([asset.returns for asset in self.positions])
        self.weights = np.array([asset.weight for asset in self.positions])
        self.returns = np.dot(self.weights.transpose(),self.returns_grid)
        self.covariance_matrix = np.cov(self.returns_grid)
        self.net_variance = np.dot(self.weights.T,np.dot(self.covariance_matrix,self.weights))
        self.net_expectation = np.mean(self.returns)
    
    def optimal_portfolio(self):
        #looking back one year only. subject to change
        start_index = len(self.returns)-253
        end_index = len(self.returns)-1
        return_grid = self.returns_grid[:,start_index:end_index]
        weights, poly = Markowitz.optimal_portfolio_quad(return_grid,frontier=True)
        return {'weights':weights,'curve':poly}