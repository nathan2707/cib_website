import pickle
import datetime
import pandas.io.data as web
import sys
import pandas as pd
sys.path.append('../prod/')
from Portfolio import Portfolio, Position

def start_manager_update_process(p):
    latest_portfolio = manager_portfolio_update(p)
    save_new_portfolio(latest_portfolio)

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
    #start_date = datetime.date.today()
    start_date = datetime.datetime(2016,10,25)
    latest_portfolio = Portfolio(assets,start_date,all_dates)
    return latest_portfolio

#initially load csv with one series going back at least to 2010
def manager_data_update(tickers):
    df = pd.DataFrame.from_csv("returns_data.csv")
    tickers = set(tickers)
    new_tickers = list(tickers - set(df.columns))
    new_columns = web.DataReader(new_tickers,'yahoo',datetime.datetime(2010, 1, 1))['Close']
    new_columns = new_columns.pct_change()[1:len(new_columns)]
    df = df.join(new_columns,how='outer')
    df.to_csv("returns_data.csv")
    return df

def save_new_portfolio(latest_portfolio):
    with open('portfolio.txt', 'wb') as f:
        all_portfolios = pickle.load(f)
        all_portfolios.append(latest_portfolio.compile_portfolio())
        pickle.dump(all_portfolios, f)

def direction(w):
    if w >= 0:
        return "long"
    else:
        return "short"

def make_new_charts(latest_portfolio):
    return 'done'

#use this to plot the historical performance of the fund, for whatever asset allocation
def pull_old_portfolios():
    with open('portfolio.txt','rb') as f:
        var = pickle.load(f)
    return var