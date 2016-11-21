import datetime
import Updates_Manager
import MonteCarlo

start_date = datetime.datetime(2015,10,3)
P1 = (['GILD', 'GLD', 'GPS', 'OIL', 'XOM'],[10,12,6,8,9],[78.03,124.9,21.57,5.83,86.54],900)
p = Updates_Manager.start_manager_update_process(P1,start_date)

asset_alloc = p.get_asset_allocation()


mc_sim = MonteCarlo.Simulation(p)


exp = p.get_exposures([0.2,0.2,0.2,0.2,0.2])
weights, curve = p.get_optimal_portfolio()

beta = p.get_beta()
alpha = p.get_alpha()
ir = p.get_information_ratio()
#start_daily_update_process()
#port = Updates_Manager.pull_latest_portfolio()
#port = port.uncompile()
#performance = port.daily_values