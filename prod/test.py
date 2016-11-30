import datetime
import Updates_Manager
import MonteCarlo
import pickle

def main():
    return test_monte_carlo()

def create_portfolio():
    start_date = datetime.datetime(2015,10,3)
    P1 = (['AAPL','MSFT','AMZN'],[10,12,6],[99.6,45.5,532.5],900)
    p = Updates_Manager.start_manager_update_process(P1,start_date)
    return p

def pull_latest_portfolio():
    with open('portfolio.txt','rb') as f:
        olds = pickle.load(f)
    p = olds[-1].uncompile()
    return p

def test_monte_carlo():
    p = create_portfolio()
    mc_sim = MonteCarlo.Simulation(p)
    series = mc_sim.get_full_perf_quartile(1)
    return series

def test_exposures():
    p = create_portfolio()
    dic = dict(zip(['AAPL','MSFT','AMZN'],[0.4,0.4,0.2]))
    exp = p.get_exposures(dic)
    return exp

def test_stats():
    p = create_portfolio()
    print(p.get_variance())
    print(p.get_historical_expectation())
    print(p.find_YTD_performance())
    print(p.get_alpha())
    print(p.get_beta())
    print(p.get_information_ratio())
    print(p.get_sharpe_ratio())

def test_asset_allocation():
    p = create_portfolio()
    asset_alloc = p.get_asset_allocation()
    return asset_alloc

if __name__ == "__main__":
    main()


