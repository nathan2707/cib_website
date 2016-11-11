import pickle
import datetime
import pandas.io.data as web
import pandas as pd
from Portfolio import Portfolio, Position
import os


def start_manager_update_process(p):
    if os.path.isfile('./portfolio.txt') is False:
        # a  few requirements to set up the data pipeline
        df = web.DataReader(['GOOGL', 'GLD'], 'yahoo', datetime.datetime(2010, 1, 1))['Close']
        df = df.pct_change()[1:len(df)]
        df.columns = ['GOOGL', 'GLD']
        df.to_csv("returns_data.csv")
        with open('portfolio.txt', 'wb') as f:
            pickle.dump([], f)

    latest_portfolio = manager_portfolio_update(p)
    save_new_portfolio(latest_portfolio)
    return latest_portfolio


def manager_portfolio_update(p):
    tickers = p[0]
    weights = p[1]
    costs = p[2]
    df = manager_data_update(tickers)
    df = df.dropna(thresh=len(tickers),axis=0) # this line restrict historical calculations to data points shared by all equities
    all_dates = df.index
    assets = []
    for i in range(len(tickers)):
        symbol = tickers[i]
        w = weights[i]
        in_price = costs[i]
        returns = df[symbol]
        direction_pos = direction(w)
        assets.append(Position(symbol, returns, direction_pos, in_price, w))
    start_date = datetime.datetime(2016, 10, 3)
    latest_portfolio = Portfolio(assets, start_date, all_dates)
    return latest_portfolio


# initially load csv with one series going back at least to 2010
def manager_data_update(tickers):
    df = pd.DataFrame.from_csv("returns_data.csv")
    tickers = set(tickers)
    new_tickers = list(tickers - set(df.columns))
    if len(new_tickers) > 0:
        new_columns = web.DataReader(new_tickers, 'yahoo', datetime.datetime(2010, 1, 1))['Close']
        new_columns = new_columns.pct_change()[1:len(new_columns)]
        df = df.join(new_columns, how='outer')
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

# use this to plot the historical performance of the fund, for whatever asset allocation
def pull_old_portfolios():
    with open('portfolio.txt', 'rb') as f:
        var = pickle.load(f)

def daily_data_update():
    df = pd.DataFrame.from_csv("returns_data.csv")
    tickers = df.columns
    today_row = web.DataReader(tickers,'yahoo',datetime.date.today() - datetime.timedelta(days=1),datetime.date.today())['Close']
    today_row = today_row.pct_change()[1:len(today_row)]
    df = df.append(today_row)
    df.to_csv("returns_data.csv")
    return df

def start_daily_update_process():
    latest_saved_portfolio = pull_latest_portfolio()
    df = daily_data_update()
    latest_portfolio = daily_portfolio_update(latest_saved_portfolio,df)
    update_last_portfolio(latest_portfolio)

def daily_portfolio_update(latest_saved_portfolio,return_grid):
    df = return_grid
    latest_portfolio = latest_saved_portfolio.uncompile_and_update(df)
    return latest_portfolio

def pull_latest_portfolio():
    olds = pull_old_portfolios()
    return olds[len(olds)-1]

def update_last_portfolio(latest_portfolio):
    all_portfolios = pull_old_portfolios()
    all_portfolios[len(all_portfolios)-1] = latest_portfolio.compile_portfolio()
    with open('portfolio.txt', 'wb') as f:
        pickle.dump(all_portfolios, f)

    #use this to plot the historical performance of the fund, for whatever asset allocation
def pull_old_portfolios():
    with open('portfolio.txt','rb') as f:
        var = pickle.load(f)
        return var

start_date = datetime.datetime(2016,10,3)
P1 = (['GILD', 'GLD', 'GPS', 'OIL', 'XOM'],[0.2,0.2,0.2,0.2,0.2],[78.03,124.9,21.57,5.83,86.54])
p = start_manager_update_process(P1)
#start_daily_update_process()
#port = pull_latest_portfolio()
#port = port.uncompile()
#port.daily_values