import pickle
import datetime
import pandas.io.data as web
import sys
import pandas as pd
sys.path.append('../prod/')
from Portfolio import Portfolio, Position
import os

def start_manager_update_process(p):
    if os.path.isfile('./portfolio.txt') is False:
        # a  few requirements to set up the data pipeline
        df = web.DataReader(['GOOGL','GLD'],'yahoo',datetime.datetime(2010, 1, 1))['Close']
        df = df.pct_change()[1:len(df)]
        df.columns = ['GOOGL','GLD']
        df.to_csv("returns_data.csv")
        with open('portfolio.txt','wb') as f:
            pickle.dump([],f)
  
    latest_portfolio = manager_portfolio_update(p)
    save_new_portfolio(latest_portfolio)
    return latest_portfolio

def manager_portfolio_update(p):
    tickers = p[0]
    weights = p[1]
    costs = p[2]
    df = manager_data_update(tickers)
    df = df.dropna(thresh=len(tickers), axis=0) #this line restrict historical calculations to data points shared by all equities
    all_dates = df.index
    assets = []
    for i in range(len(tickers)):
        symbol = tickers[i]
        w = weights[i]
        in_price = costs[i]
        returns = df[symbol]
        direction_pos = direction(w)
        assets.append(Position(symbol,returns,direction_pos,in_price,w))
    start_date = datetime.date.today()
    latest_portfolio = Portfolio(assets,start_date,all_dates)
    return latest_portfolio
    
#initially load csv with one series going back at least to 2010
def manager_data_update(tickers):
    df = pd.DataFrame.from_csv("returns_data.csv")
    tickers = set(tickers)
    new_tickers = list(tickers - set(df.columns))
    if len(new_tickers) > 0:
        new_columns = web.DataReader(new_tickers,'yahoo',datetime.datetime(2010, 1, 1))['Close']
        new_columns = new_columns.pct_change()[1:len(new_columns)]
        df = df.join(new_columns,how='outer')
        df.to_csv("returns_data.csv")
    return df

def save_new_portfolio(latest_portfolio):
    all_portfolios = pull_old_portfolios()
    all_portfolios.append(latest_portfolio.compile_portfolio())
    with open('portfolio.txt', 'wb') as f:
        pickle.dump(all_portfolios, f)
        
def direction(w):
    if w >= 0:
        return "long"
    else:
        return "short"

#use this to plot the historical performance of the fund, for whatever asset allocation
def pull_old_portfolios():
    with open('portfolio.txt','rb') as f:
        var = pickle.load(f)
    return var