import datetime
import Updates_Manager
import MonteCarlo

start_date = datetime.datetime(2015,10,3)
P1 = (['AAPL','MSFT','AMZN'],[10,12,6],[99.6,45.5,532.5],900)
p = Updates_Manager.start_manager_update_process(P1,start_date)
dic = dict(zip(['AAPL','MSFT','AMZN'],[0.4,0.4,0.2]))
exp = p.get_exposures(dic)


print(p.get_variance())
print(p.get_historical_expectation())
mc_sim = MonteCarlo.Simulation(p)
series = mc_sim.get_full_perf_quartile(1)
print("hey now brown cow")


asset_alloc = p.get_asset_allocation()



beta = p.get_beta()
alpha = p.get_alpha()
ir = p.get_information_ratio()
#start_daily_update_process()
#port = Updates_Manager.pull_latest_portfolio()
#port = port.uncompile()
#performance = port.daily_values