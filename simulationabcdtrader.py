"""
Author: Ngusum Akofu
Date Created: Feb 07, 2022
"""

import abcdtrader 
import indicators as indi
import supportresistance as supres
import backtrader as bt
import numpy as np
import pandas as pd
from pytz import timezone
import time
import config 
import assets
#import plot 
#import machinelearningengine as mle
#import trainingdata as tdata
#import analytics as ana
import pnl



# Get our account information.
account = config.api.get_account()

PACIFIC_TZ = timezone('US/Pacific')



# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
#print('${} is available as buying power.'.format(account.buying_power))


##Middle float 20 t0 500M shares , $10 to $100 
SPREAD_MULTIPLIER = 0.00025#0.0005#ie 5 cents for every hundred dollars. Multiply this by price to get spread in $$ #0.02#0.03
POSITION_SIZE = 1000
TOTAL_DAILY_PNL = 0
NUM_DAYS_RUN = 0
TOTAL_NUM_DAILY_TRANSACTIONS = 0
AVE_NUM_DAILY_TRANSACTIONS = 0
HIGHEST_MAX_NUM_OPEN_POSITIONS = -np.inf
LOWEST_MAX_NUM_OPEN_POSITIONS = np.inf
STOCK_INDEX = 0
LOWER_PRICE_THRESHOLD = 13#10#13
UPPER_PRICE_THRESHOLD = 5000#3500
VOL_THRESHOLD = 10000000#5000000#10000000#20000000
GAP_THRESHOLD = 5
abcd = None
TRAINING_WINDOW = '1 days'
#SCALING = 'fs'#fs = feature scaling, mn = mean_normalized
#SCALING = 'mn'
assets_dict = []



def get_shortable_assets(universe, all_shortable_assets):
	short_list = []
	for i in range(0, len(universe)):
		for j in range(0, len(all_shortable_assets)):
			if universe[i] == all_shortable_assets[j]:
				short_list.append(universe[i])
				break
	return short_list


def get_all_shortable_assets():
	active_assets = config.api.list_assets(status='active')
	short_list = []
	for asset in active_assets:
		if asset.easy_to_borrow and asset.marginable:
			short_list.append(asset.symbol)
	return short_list



def dow_snp_minus_set1(set1):
	new_list = []
	def add_content_from_list2_not_found_in_list1_into_new_list(list1, list2):
		for i in range(0, len(list2)):
			stock_from_list2_found_in_list1 = False
			for j in range(0, len(list1)):
				if list2[i] == list1[j]:
					stock_from_list2_found_in_list1 = True
					break
			if not stock_from_list2_found_in_list1:
				new_list.append(list2[i])

	add_content_from_list2_not_found_in_list1_into_new_list(set1, assets.dow_stocks)
	add_content_from_list2_not_found_in_list1_into_new_list(set1, assets.snp_stocks1)
	add_content_from_list2_not_found_in_list1_into_new_list(set1, assets.snp_stocks2)
	add_content_from_list2_not_found_in_list1_into_new_list(set1, assets.snp_stocks3)
	add_content_from_list2_not_found_in_list1_into_new_list(set1, assets.snp_stocks4)
	add_content_from_list2_not_found_in_list1_into_new_list(set1, assets.snp_stocks5)

	new_list = list(dict.fromkeys(new_list)) #Remove any duplicates 
	print(new_list)



def screen_universe_price_vol_threshold(df):
	num_cols = len(df.columns)
	boolean_series = ((df.xs('close', axis=1, level=1).mean() > LOWER_PRICE_THRESHOLD) & (df.xs('close', axis=1, level=1).mean() < UPPER_PRICE_THRESHOLD) & (df.xs('volume', axis=1, level=1).mean() > VOL_THRESHOLD)).to_numpy()
	num_sub_cols = int(num_cols/len(boolean_series))
	boolean_series = np.repeat(boolean_series, num_sub_cols)
	return df.loc[:, boolean_series]
	


def return_all_assets(all_assets):
	for asset_list in assets.active_assets:
		for asset in asset_list:
			all_assets.append(asset)
	all_assets = list(dict.fromkeys(all_assets)) #Remove any duplicates 	
	return sorted(all_assets)


def select_universe_price_vol_threshold(universe, backtrader, period, date):
	for asset_list in assets.active_assets:
		df = backtrader.get_df(config, asset_list, period, 3, date.isoformat())
		#print(df.columns.droplevel(1))
		#print(list(dict.fromkeys(df.columns.droplevel(1))))
		df = screen_universe_price_vol_threshold(df)
		universe += list(dict.fromkeys(df.columns.droplevel(1)))
		#print(universe)
		print("selecting stocks...")
		
	universe = list(dict.fromkeys(universe)) #Remove any duplicates 



def select_universe_gapers(universe, backtrader, period, date):
	global GAP_THRESHOLD
	global VOL_THRESHOLD
	global LOWER_PRICE_THRESHOLD
	global UPPER_PRICE_THRESHOLD
	#pd.Timedelta('2 days')
	for asset_list in assets.active_assets:#Each asset list is a list of assets. We can't have all assets in just one list, so we break them up into many lists for easier management
		print("selecting stocks...")
		np_prev_close = backtrader.get_prev_day_c(config, asset_list, period, 2, date)[0]
		np_curr_open = backtrader.get_curr_day_o(config, asset_list, period, 1, date)[0]
		np_gap = np.subtract(np_curr_open ,np_prev_close)
		np_percentage_price_change = np.multiply(np.divide(np_gap, np_prev_close), 100)

		num_days_vol = 7
		df_last_n_vols = backtrader.get_last_n_vols(config, asset_list, period, num_days_vol, (date - pd.Timedelta('1 days')))
		df_last_n_vols_mean = df_last_n_vols.mean()
		np_last_n_vols_mean = df_last_n_vols_mean.to_numpy()

		#print("Last n vols "+str(df_last_n_vols))
		#print("Last n vols mean "+str(df_last_n_vols_mean))
		#print("Np last n vols mean "+str(np_last_n_vols_mean))

		for i in range(0, len(np_percentage_price_change)):
			if abs(np_percentage_price_change[i]) > GAP_THRESHOLD and np_last_n_vols_mean[i] > VOL_THRESHOLD and np_prev_close[i] > LOWER_PRICE_THRESHOLD and np_prev_close[i] < UPPER_PRICE_THRESHOLD:
				universe.append(asset_list[i])
		#print("prev close\n"+str(np_prev_close))
		#print("\ncurr open\n"+str(np_curr_open))
		#print("\ngap\n"+str(np_gap))
		#print("\npercent gap\n"+str(np_percentage_price_change))
	#return universe
	return list(dict.fromkeys(universe)) #Remove any duplicates 



#def run(logs, logs1, start_date, end_date, min_periodA, min_periodB, day_periodB):
def run(logs, logs1, start_date, end_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days):	
	global st
	global SCALING
	global TOTAL_DAILY_PNL
	global NUM_DAYS_RUN
	global TOTAL_NUM_DAILY_TRANSACTIONS
	global HIGHEST_MAX_NUM_OPEN_POSITIONS
	global LOWEST_MAX_NUM_OPEN_POSITIONS
	#regression = "linear"
	#regression = "logistic"


	backtrader = bt.Backtrader()
	curr_date = start_date

	universe = []

	select_universe_price_vol_threshold(universe, backtrader, day_periodB, curr_date)
	universe = list(dict.fromkeys(universe)) #Remove any duplicates

	#universe = select_universe_gapers(universe, backtrader, day_periodB, curr_date)

	print(universe)
	print("Returned "+str(len(universe))+" stocks. Trading starts!")

	print("Stock plotted = "+str(sorted(universe)[STOCK_INDEX]))
	#st.file_log_write(str(curr_date))

	all_assets = return_all_assets([])
	#print("All assets: "+str(all_assets))


	all_shortable_assets = get_all_shortable_assets()
	#print("Len shortable assets: "+str(len(all_shortable_assets)))
	#print("All shortable assets: "+str(all_shortable_assets))


	shortable_assets = get_shortable_assets(universe, all_shortable_assets)
	print("Len shortable assets: "+str(len(shortable_assets)))
	print("Shortable assets: "+str(shortable_assets))


	#analytics = ana.Analytics()
	#mlengine = mle.Machinelearningengine()
	abcd = abcdtrader.Abcdtrader(logs, logs1)#New instance of strategy used in run func
	sr = supres.Supportresistance(len(universe))
	ind = indi.Indicators()
	abcd.num_training_days = num_training_days
	#td = tdata.Trainingdata()#New instance of Trainingdata
	plt = None# plot.Plot(len(universe))#New instamce of Plot
	pNl = pnl.PnL(len(universe))#New instance of PnL

	#print("time list "+str(plt.time_list)+" price list "+str(plt.price_list))
	#print(assets.active_assets)
	#Reset portfolio val
	backtrader.portfolio_val = 25000
	#print("Current time: "+str(now.isoformat()))
	print("Start time: "+str(start_date.isoformat()))
	print("Initial Portfolio Value: "+str(backtrader.portfolio_val))

	


	#print("from main initially training error short final "+str(analytics.training_error_short_final))
	#st.init_training_data(universe, td, mlengine, analytics)
	#st.init_support_resistance(universe, sr)
	#print("from main after init training error short final "+str(analytics.training_error_short_final))
	#print("init td "+str(td.Y0long)+" init mlenging "+str(mlengine.Y0long))
	

	backtrader.run(abcd, universe, start_date, end_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, shortable_assets=shortable_assets, all_assets=all_assets, position_size=POSITION_SIZE, spread_multiplier=SPREAD_MULTIPLIER, ind=ind, bt=backtrader, sr=sr, stock_index=STOCK_INDEX, config=config, num_assets=len(universe), pNl=pNl, plt=plt, MY_TZ=PACIFIC_TZ, ASSETS_DICT=assets_dict)
	#backtrader.run(st, universe, start_date, end_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, shortable_assets=shortable_assets, all_assets=all_assets, position_size=POSITION_SIZE, spread_multiplier=SPREAD_MULTIPLIER, ind=ind, bt=backtrader, sr=sr, stock_index=STOCK_INDEX, config=config, num_assets=len(universe), pNl=pNl, plt=plt, td=td, scaling=SCALING, regression=regression,  mlengine=mlengine, analytics=analytics, MY_TZ=PACIFIC_TZ, ASSETS_DICT=assets_dict)
	TOTAL_NUM_DAILY_TRANSACTIONS += pNl.num_daily_transactions
	if not pNl.daily_pnl == 0:
		NUM_DAYS_RUN += 1
		TOTAL_DAILY_PNL += pNl.daily_pnl

	if pNl.max_num_open_positions > HIGHEST_MAX_NUM_OPEN_POSITIONS:
		HIGHEST_MAX_NUM_OPEN_POSITIONS = pNl.max_num_open_positions 

	if pNl.max_num_open_positions < LOWEST_MAX_NUM_OPEN_POSITIONS:
		LOWEST_MAX_NUM_OPEN_POSITIONS = pNl.max_num_open_positions



def main():
	global TOTAL_DAILY_PNL
	global NUM_DAYS_RUN
	global TOTAL_NUM_DAILY_TRANSACTIONS
	global AVE_NUM_DAILY_TRANSACTIONS
	global HIGHEST_MAX_NUM_OPEN_POSITIONS
	global LOWEST_MAX_NUM_OPEN_POSITIONS
	#print("In main")
	#w opens file for writing, creates one if not exist. a opens file for appending. Creates one if not exist
	logs = open("logs.txt", "a")
	logs1 = open("logs1.txt", "a")
	#logs1 = open("logs1.txt", "w")



	_1min_periodA = abcdtrader.MIN1_CANDLESTICK_PERIODS.get('A')	
	_1min_periodB = abcdtrader.MIN1_CANDLESTICK_PERIODS.get('B')
	_5min_periodA = abcdtrader.MIN5_CANDLESTICK_PERIODS.get('A')	
	_5min_periodB = abcdtrader.MIN5_CANDLESTICK_PERIODS.get('B')
	_15min_periodA = abcdtrader.MIN15_CANDLESTICK_PERIODS.get('A')	
	_15min_periodB = abcdtrader.MIN15_CANDLESTICK_PERIODS.get('B')	
	day_periodA = abcdtrader.DAY_CANDLESTICK_PERIODS.get('A')
	day_periodB = abcdtrader.DAY_CANDLESTICK_PERIODS.get('B')		
	num_training_days = 2


	
	"""
	run(logs, logs1, pd.Timestamp('2021-01-04 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-04 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-05 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-05 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	"""
	"""
	run(logs, logs1, pd.Timestamp('2021-01-06 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-06 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-07 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-07 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-08 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-08 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-11 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-11 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-12 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-12 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-13 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-13 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-14 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-14 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-15 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-15 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-19 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-19 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-20 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-20 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-21 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-21 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-22 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-22 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-25 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-25 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-26 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-26 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-27 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-27 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-28 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-28 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-01-29 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-01-29 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	
	
	run(logs, logs1, pd.Timestamp('2021-02-01 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-01 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-02 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-02 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-03 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-03 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-04 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-04 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-05 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-05 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-08 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-08 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-09 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-09 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-10 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-10 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-11 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-11 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-12 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-12 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-16 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-16 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-17 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-17 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-18 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-18 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-19 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-19 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-22 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-22 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-23 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-23 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-24 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-24 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-25 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-25 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-02-26 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-02-26 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	
	run(logs, logs1, pd.Timestamp('2021-03-01 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-01 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	#**AAL bugrun(logs, logs1, pd.Timestamp('2021-03-02 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-02 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	#**AAL bugrun(logs, logs1, pd.Timestamp('2021-03-03 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-03 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	#**AAL bugrun(logs, logs1, pd.Timestamp('2021-03-04 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-04 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-05 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-05 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-08 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-08 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-09 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-09 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-10 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-10 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-11 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-11 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-12 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-12 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-15 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-15 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-16 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-16 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-17 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-17 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-18 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-18 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-19 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-19 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	
	run(logs, logs1, pd.Timestamp('2021-03-22 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-22 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-23 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-23 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-24 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-24 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-25 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-25 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-26 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-26 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-29 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-29 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-30 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-30 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-03-31 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-03-31 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)

	run(logs, logs1, pd.Timestamp('2021-04-01 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-01 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-05 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-05 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-06 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-06 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-07 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-07 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-08 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-08 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-09 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-09 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-12 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-12 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-13 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-13 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-14 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-14 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-15 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-15 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-16 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-16 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-19 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-19 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-20 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-20 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-21 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-21 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-22 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-22 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-23 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-23 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-26 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-26 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-27 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-27 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-28 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-28 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-29 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-29 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-04-30 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-04-30 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	
	run(logs, logs1, pd.Timestamp('2021-05-03 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-03 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-04 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-04 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-05 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-05 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-06 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-06 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-07 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-07 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-10 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-10 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-11 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-11 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-12 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-12 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-13 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-13 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-14 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-14 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-17 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-17 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-18 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-18 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-19 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-19 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-20 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-20 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-21 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-21 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-24 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-24 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-25 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-25 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-26 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-26 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-27 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-27 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-28 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-28 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-05-31 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-05-31 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)

	run(logs, logs1, pd.Timestamp('2021-06-01 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-01 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-02 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-02 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-03 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-03 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-04 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-04 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-07 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-07 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-08 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-08 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-09 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-09 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-10 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-10 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-11 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-11 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-14 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-14 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-15 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-15 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-16 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-16 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-17 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-17 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-21 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-21 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-22 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-22 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-23 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-23 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-24 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-24 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-25 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-25 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-28 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-28 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-29 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-29 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-06-30 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-06-30 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)

	run(logs, logs1, pd.Timestamp('2021-07-06 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-06 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-07 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-07 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-08 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-08 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-09 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-09 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-12 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-12 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-13 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-13 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-14 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-14 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-15 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-15 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-16 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-16 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-19 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-19 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-20 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-20 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-21 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-21 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-22 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-22 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-23 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-23 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-26 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-26 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-27 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-27 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-28 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-28 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-29 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-29 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-07-30 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-07-30 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)

	run(logs, logs1, pd.Timestamp('2021-08-02 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-02 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-03 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-03 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-04 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-04 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-05 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-05 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-06 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-06 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-09 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-09 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-10 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-10 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-11 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-11 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-12 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-12 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-13 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-13 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-16 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-16 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-17 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-17 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-18 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-18 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-19 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-19 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-20 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-20 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-23 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-23 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-24 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-24 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-25 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-25 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-26 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-26 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-27 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-27 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-30 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-30 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-08-31 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-08-31 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	
	run(logs, logs1, pd.Timestamp('2021-09-01 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-01 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-02 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-02 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-03 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-03 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-07 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-07 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-08 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-08 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-09 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-09 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-10 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-10 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-13 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-13 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-14 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-14 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-15 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-15 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-16 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-16 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-17 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-17 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-20 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-20 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-21 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-21 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-22 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-22 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-23 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-23 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-24 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-24 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-27 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-27 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-28 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-28 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-29 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-29 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-09-30 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-09-30 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)

	run(logs, logs1, pd.Timestamp('2021-10-01 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-01 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-04 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-04 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-05 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-05 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-06 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-06 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-07 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-07 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-08 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-08 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-11 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-11 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-12 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-12 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-13 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-13 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-14 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-14 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-15 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-15 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-18 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-18 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-19 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-19 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-20 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-20 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-21 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-21 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-22 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-22 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-25 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-25 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-26 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-26 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-27 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-27 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-28 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-28 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-10-29 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-10-29 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	
	run(logs, logs1, pd.Timestamp('2021-11-01 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-01 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-02 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-02 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-03 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-03 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-04 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-04 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-05 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-05 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-08 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-08 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-09 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-09 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-10 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-10 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-11 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-11 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-12 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-12 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-15 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-15 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-16 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-16 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-17 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-17 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-18 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-18 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-19 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-19 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-22 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-22 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-23 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-23 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-24 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-24 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	#run(logs, logs1, pd.Timestamp('2021-11-26 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-26 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-29 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-29 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-11-30 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-11-30 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)

	run(logs, logs1, pd.Timestamp('2021-12-01 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-01 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-02 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-02 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-03 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-03 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)	
	run(logs, logs1, pd.Timestamp('2021-12-06 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-06 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-07 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-07 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-08 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-08 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-09 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-09 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-10 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-10 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-13 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-13 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-14 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-14 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-15 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-15 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-16 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-16 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-17 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-17 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-20 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-20 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-21 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-21 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-22 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-22 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	#run(logs, logs1, pd.Timestamp('2021-12-23 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-23 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-27 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-27 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-28 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-28 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-29 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-29 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2021-12-30 06:30',tz=PACIFIC_TZ), pd.Timestamp('2021-12-30 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	"""


	run(logs, logs1, pd.Timestamp('2022-01-03 06:30',tz=PACIFIC_TZ), pd.Timestamp('2022-01-03 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2022-01-04 06:30',tz=PACIFIC_TZ), pd.Timestamp('2022-01-04 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2022-01-05 06:30',tz=PACIFIC_TZ), pd.Timestamp('2022-01-05 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2022-01-06 06:30',tz=PACIFIC_TZ), pd.Timestamp('2022-01-06 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2022-01-07 06:30',tz=PACIFIC_TZ), pd.Timestamp('2022-01-07 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2022-01-10 06:30',tz=PACIFIC_TZ), pd.Timestamp('2022-01-10 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2022-01-11 06:30',tz=PACIFIC_TZ), pd.Timestamp('2022-01-11 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2022-01-12 06:30',tz=PACIFIC_TZ), pd.Timestamp('2022-01-12 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	run(logs, logs1, pd.Timestamp('2022-01-13 06:30',tz=PACIFIC_TZ), pd.Timestamp('2022-01-13 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	#run(logs, logs1, pd.Timestamp('2022-01-14 06:30',tz=PACIFIC_TZ), pd.Timestamp('2022-01-14 13:00',tz=PACIFIC_TZ), _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, num_training_days)
	


	AVE_NUM_DAILY_TRANSACTIONS = TOTAL_NUM_DAILY_TRANSACTIONS/NUM_DAYS_RUN
	st.file_log_write("\n\nTOTAL DAILY PNL "+str(TOTAL_DAILY_PNL)+" over "+str(NUM_DAYS_RUN)+" days. Average "+str(TOTAL_DAILY_PNL/NUM_DAYS_RUN)+" per day. Average num transactions per day "+str(AVE_NUM_DAILY_TRANSACTIONS)+"\n")
	st.file_log_write("Highest max num open positions "+str(HIGHEST_MAX_NUM_OPEN_POSITIONS)+" lowest max num open positions "+str(LOWEST_MAX_NUM_OPEN_POSITIONS)+"\n")

	#analyze_learning_curves(logs, logs1, min_periodA, min_periodB, day_periodB)

	
	st.file_log_close()
	st.file_log1_close()



if __name__== '__main__':
   main()
   #dow_snp_minus_set1(['MSFT', 'AAPL', 'TSLA', 'NIO', 'TQQQ', 'SQQQ', 'BP', 'TD', 'INTU', 'NOW', 'CVS', 'DEO', 'FIS', 'SPGI', 'BLK', 'SNE', 'SBUX', 'BUD', 'JD', 'MMM', 'HDB', 'GILD', 'RY', 'LMT', 'BA', 'HSBC', 'WFC', 'UPS', 'HON', 'TOT', 'GSK', 'LOW', 'CIT', 'IBM', 'QCOM', 'PM', 'UNP', 'LIN', 'MDT', 'NEE', 'CHTR', 'TMUS', 'DHR', 'BMY', 'MCD', 'ACN', 'AZN', 'COST', 'BNTC', 'PFE', 'COST', 'AMGN', 'NKE', 'TMO', 'CVX', 'LLY', 'ABT', 'ASML', 'ABBV', 'TM', 'SAP', 'ORCL', 'XOM', 'CRM', 'CMCSA', 'PEP', 'KO', 'MRK', 'BAC', 'CSCO', 'NVS', 'DIS', 'T', 'PYPL', 'ADBE', 'NFLX', 'VZ', 'INTC', 'HD', 'UNH', 'JPM', 'MA', 'PG', 'TSM', 'WMT', 'JNJ', 'V', 'BRK.B', 'FB', 'BABA', 'GOOG', 'GOOGL', 'AMZN', 'PLTR', 'JMIA', 'AAL', 'BABA', 'AMGN', 'CAT', 'CVX', 'GS', 'HD', 'HON', 'IBM', 'INTC', 'JNJ', 'JPM', 'MCD', 'MMM', 'MRK', 'NIKE', 'PG', 'TRV', 'UNH', 'CRM', 'VZ', 'V', 'WBA', 'WMT', 'DIS', 'DOW', 'ATVI', 'ADBE', 'AIG', 'AVGO', 'DAL', 'FB', 'FIS', 'F', 'HON', 'HUM', 'LLY', 'MGM', 'MCHP', 'ORCL', 'WU'])
   #mle.Machinelearningengine().test_grad_descent_lin_reg()
   #mle.Machinelearningengine().test_grad_descent_log_reg()
   #print(list(dict.fromkeys(['MSFT', 'AAPL', 'TSLA', 'NIO', 'TQQQ', 'SQQQ', 'BP', 'TD', 'INTU', 'NOW', 'CVS', 'DEO', 'FIS', 'SPGI', 'BLK', 'SNE', 'SBUX', 'BUD', 'JD', 'MMM', 'HDB', 'GILD', 'RY', 'LMT', 'BA', 'HSBC', 'WFC', 'UPS', 'HON', 'TOT', 'GSK', 'LOW', 'CIT', 'IBM', 'QCOM', 'PM', 'UNP', 'LIN', 'MDT', 'NEE', 'CHTR', 'TMUS', 'DHR', 'BMY', 'MCD', 'ACN', 'AZN', 'COST', 'BNTC', 'PFE', 'COST', 'AMGN', 'NKE', 'TMO', 'CVX', 'LLY', 'ABT', 'ASML', 'ABBV', 'TM', 'SAP', 'ORCL', 'XOM', 'CRM', 'CMCSA', 'PEP', 'KO', 'MRK', 'BAC', 'CSCO', 'NVS', 'DIS', 'T', 'PYPL', 'ADBE', 'NFLX', 'VZ', 'INTC', 'HD', 'UNH', 'JPM', 'MA', 'PG', 'TSM', 'WMT', 'JNJ', 'V', 'BRK.B', 'FB', 'BABA', 'GOOG', 'GOOGL', 'AMZN', 'PLTR', 'JMIA', 'AAL', 'BABA', 'AMGN', 'CAT', 'CVX', 'GS', 'HD', 'HON', 'IBM', 'INTC', 'JNJ', 'JPM', 'MCD', 'MMM', 'MRK', 'NIKE', 'PG', 'TRV', 'UNH', 'CRM', 'VZ', 'V', 'WBA', 'WMT', 'DIS', 'DOW', 'ATVI', 'ADBE', 'AIG', 'AVGO', 'DAL', 'FB', 'FIS', 'F', 'HON', 'HUM', 'LLY', 'MGM', 'MCHP', 'ORCL', 'WU'])))


