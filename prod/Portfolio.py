import pandas.io.data as web
import pandas as pd
import datetime
import Markowitz
import numpy as np

class Position:
    def __init__(self,symbol,returns,direction,in_price,n_shares):
        #format for dates: "YYYY-MM-dd"
        self.symbol = symbol
        self.returns = returns
        self.direction = direction
        self.in_price = in_price
        self.n_shares = n_shares
        if direction == "long":
            self.returns *= 100
        else:
            self.returns *= -100
            
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
        current_prices = web.DataReader([asset.symbol for asset in self.positions], 'yahoo', datetime.date.today())['Open']
        total_amount = self.cash
        for asset in self.positions:
            total_amount = total_amount + current_prices[asset.symbol] * asset.n_shares
        symbols = self.symbols.append("cash")
        weights = []
        i = 0
        for asset in self.positions:
            weights[i] = (current_prices[asset.symbol] * asset.n_shares)/total_amount
            i = i + 1
        weights.append(self.cash/total_amount)
        return dict(zip(symbols, weights))

    def get_values(self):
        return self.daily_values
    def get_covariance_matrix(self):
        return self.covariance_matrix
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
        compilation = Portfolio_Compiled(self.symbols,self.start_date,self.weights,in_prices,directions,self.daily_values,self.net_variance,self.net_expectation,self.historical_dates,self.cash)
        return compilation

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
    def __init__(self,tickers,start_date,initial_weights,in_prices,directions,returns,net_variance,net_expectation,all_dates,money):
        self.tickers = tickers
        self.start_date = start_date
        self.in_prices = in_prices
        self.directions = directions
        self.initial_weights = initial_weights
        self.net_returns = returns
        self.net_variance = net_variance
        self.net_expectation = net_expectation
        self.historical_dates = all_dates
        self.cash = money
    
    def uncompile_and_update(self,df):
        positions = []
        for i in range(len(self.tickers)):
                pos = Position(self.tickers[i],df[self.tickers[i]],self.directions[i],self.in_prices[i],self.initial_weights[i])
                positions.append(pos)
        portfolio = Portfolio(positions,self.start_date,self.historical_dates,self.cash)
        return portfolio
    
    def uncompile(self):
        df = pd.DataFrame.from_csv("returns_data.csv")
        positions = []
        for i in range(len(self.tickers)):
                pos = Position(self.tickers[i],df[self.tickers[i]],self.directions[i],self.in_prices[i],self.initial_weights[i])
                positions.append(pos)
        portfolio = Portfolio(positions,self.start_date,self.historical_dates,self.cash)
        return portfolio

##OLD/UNUSED Functions

def calculate_values_old(assets, historical_returns, start_date, all_dates):
    # calculate first return taking into account price at which PM entered position
    first_return = 0
    for asset in assets:
        first_date = start_date - datetime.timedelta(1)
        first_price = web.DataReader(asset.symbol, 'yahoo', first_date)['Close'][0]
        r = 100 * (first_price - asset.in_price) / asset.in_price
        if asset.direction != 'long':
            r = -r
        first_return = first_return + r
    # find index of first date
    values = []
    for i in range(len(all_dates) - 1, 0, -1):
        if (pd.Timestamp(start_date).to_datetime() - all_dates[i].to_datetime()).days == 0:
            returns = np.insert(historical_returns[i:len(historical_returns)], 0, first_return)
            roll = 1
            values = []
            for i in range(len(returns)):
                roll = roll * (1 + returns[i] / 100)
                values.append(roll)
            return values
    return values