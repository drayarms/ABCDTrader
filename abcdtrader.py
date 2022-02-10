"""
Author: Ngusum Akofu
Date Created: Feb 07, 2022
Mod Sept 07 aft
"""

import numpy as np
import math
import pandas as pd
#import plot as plt
import copy
import threading
from time import sleep



# Get our account information.
#account = config.api.get_account()


POSITION_SIZE = 1000
#POSITION_FRACTION = 1#1 represents the whole position
TRAILING_PERCENTAGE = 0.0017#0.17% Maybe should really be based on ATR
#MOVING_PRICE_GRADIENT_PERIOD = 10
RSI_LOW = 70
RSI_HI = 30
PROFIT_TO_RISK = 1.49952#1.49954#1.5 - 0.00046 -0.000017
#Values candlestic period1 can take: minute, 1Min, 5Min, 15Min, day or 1D. minute is an alias of 1Min. Similarly, day is of 1D.
#Candlestick period A and B should be same. They are just different formats of the same thing
MIN1_CANDLESTICK_PERIODS = {'A':'1 minutes', 'B':'1Min', 'terminal':'0 minutes'}
MIN5_CANDLESTICK_PERIODS = {'A':'5 minutes', 'B':'5Min', 'terminal':'0 minutes'}
MIN15_CANDLESTICK_PERIODS = {'A':'15 minutes', 'B':'15Min', 'terminal':'0 minutes'}
DAY_CANDLESTICK_PERIODS = {'A':'1 days', 'B':'1D', 'terminal':'0 days'}


class Abcdtrader:
	
	def __init__(self, logs, logs1, num_assets):

	#def __init__self(self, logs):
		#self.prev_ema9 = None

		self.file = logs#Log file
		self.file1 = logs1
		self.trades = 0
		self.wins = 0
		self.losses = 0
		self.max_num_positions = 0
		self.winners = []
		self.losers = []
		self.end_of_trading_session = False



		self.peak_atr_open = []
		self.peak_atr_close = []

		self.daily_peak = []
		self.daily_trough = []



		self.cummulative_green_macd_bars = []
		self.cummulative_red_macd_bars = []

		self.prev_day_open = []
		self.prev_day_close = []
		self.prev_day_hi = []
		self.prev_day_lo = []
		self.prev_day_vol = []
		self.curr_day_open = []
		self.curr_day_close = []

		self.peak_atr_reached = []

		self.rsi_at_open = None
		self.rsi_at_peak_atr = None

		self.queue_size = 6#1#10#7#6#4
		self.lookahead_period = 13#7#1#4#2
		self.vol_queue = []
		self.candlestick_size_queue = []
		self.candlestick_range_queue = []
		self.close_queue = []
		self.rsi_queue = []
		self.macd_queue = []
		self.price_vwap_gap_queue = []
		self.y_threshold_train = 0#0.4#0.4
		self.y_threshold_test = 0#0.4
		self.error_threshold = 0.1

		self.yesterday_hi = [-np.inf] * num_assets
		self.yesterday_lo = [np.inf] * num_assets
		self.today_hi = [-np.inf] * num_assets
		self.today_lo = [np.inf] * num_assets	
		self.yesterday_close = [0] * num_assets	
		self.today_open = [0] * num_assets	



	def file_log_write(self, txt):
		self.file.write(txt)


	def file_log_close(self):
		self.file.close


	def file_log1_write(self, txt):
		self.file1.write(txt)


	def file_log1_close(self):
		self.file1.close		



	def slope(self, macd_list, n):
		arr = []
		for i in range(0, n):
			if i == 0:
				arr.append(macd_list[0])
			else:
				arr.append(np.subtract(macd_list[i], macd_list[i-1]))
		return arr




	def is_same_day(self, date1, date2):
		return date1.year == date2.year and date1.month == date2.month and date1.day == date2.day



	def asset_is_shortable(self, asset_of_interest, shortable_assets):
		for asset in shortable_assets:
			if asset == asset_of_interest:
				return True
		return False
	

	def enter_position(self, assets, position, side, risk, reward, risk_level, reward_level, stop_level, close, time, kwargs):
		spread_multiplier = kwargs['spread_multiplier']
		spread = spread_multiplier*close
		entry_price = close
		if side == "long":
			entry_price = entry_price + spread
		if side == "short":
			entry_price = entry_price - spread	

		position_size = kwargs['position_size']
		num_shares = math.ceil(position_size/entry_price)

		position.append({"side":side, "risk":risk, "reward":reward, "risk level":risk_level, "reward level":reward_level, "stop level":stop_level, "entry price":entry_price, "exit price":entry_price, "peak price attained":entry_price, "entry time":time, "exit time":time, "num shares":num_shares, "position exited":False, "profit per share":0, "profit":0})	
		kwargs['pNl'].update_max_num_open_positions(assets)
		#return position



	def exit_position(self, side, position, close, time, kwargs):
		exit_price = close
		spread_multiplier = kwargs['spread_multiplier']
		spread = spread_multiplier*exit_price
		if side == "long":
			exit_price = exit_price - spread
		if side == "short":
			exit_price = exit_price + spread

		entry_price = position.get("entry price")
		profit_per_share = exit_price - entry_price
		if side == "short":
			profit_per_share = profit_per_share * -1

		position.update({"exit price":exit_price})
		position.update({"exit time":time})
		position.update({"position exited":True})
		position.update({"profit per share":profit_per_share})

		#position_size = kwargs['position_size']
		#entry_price = position.get("entry price")
		#num_shares = position_size/entry_price

		num_shares = position.get("num shares")
		profit = profit_per_share*num_shares	
		position.update({"profit":profit})	

		#return position		



	def determine_exit(self, assets, curr_date, test_date, long_positions, short_positions, close, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, _1min_macd_almost_crossing_signal, _1min_is_uptrending, _1min_is_downtrending, atr, kwargs):		
		is_end_of_trading_day = self.is_same_day(curr_date, test_date) and curr_date.hour == 12 and curr_date.minute == 59
		if is_end_of_trading_day:
			print("\n\nGET READY FOR MARKET CLOSE!!!!\n\n")

		def process_positions(positions):
			for i in range(0, len(positions)):
				for j in range(0, len(positions[i])):
					side = positions[i][j].get("side")
					risk_level = positions[i][j].get("risk level")
					entry_price = positions[i][j].get("entry price")
				
					peak_price_attained = positions[i][j].get("peak price attained")
					entry_time = positions[i][j].get("entry time")
					position_exited = positions[i][j].get("position exited")
					max_tolerable_loss_reached = False

					base_loss_rate = 0.002#0.0015#0.0085*atr[i]#0.0017#0.0015#Very important that this number stays low. This is the guard against taking a wrong position
					min_desired_profit_to_entry_price = 0.005#0.005#Minimum profit per share which must be reached before base loss rate is amplified
					#By this scheme, profit per share below 0.5%, willing to loose 0.15%, profit per share at 1%, willing to loose circa 0.3%, profit per share at @%, be willing to loose 0.6% ...


					if not position_exited:

						running_profit_per_share = close[i] - entry_price
						running_profit_per_share_to_entry_price = (running_profit_per_share/entry_price)

						if side == "short":
							running_profit_per_share = running_profit_per_share * -1
							running_profit_per_share_to_entry_price = running_profit_per_share_to_entry_price * -1

						#print("In process exit... Stock: "+str(assets[i])+" "+str(side)+"-- Close: "+str(close[i])+" Entry: "+str(entry_price)+" Running profit: "+str(running_profit))

						actual_profit_to_min_desired_profit = 1#By defualt, will apply when running profit per share rate is below min desired profit per share rate
						if running_profit_per_share_to_entry_price > min_desired_profit_to_entry_price:	
							actual_profit_to_min_desired_profit = running_profit_per_share_to_entry_price/min_desired_profit_to_entry_price#A float > 1

						loss_rate = base_loss_rate * actual_profit_to_min_desired_profit

						if (side == "long" and close[i] < peak_price_attained * (1 - loss_rate)):	
							max_tolerable_loss_reached = True
						if (side == "short" and close[i] > peak_price_attained * (1 + loss_rate)):			
							max_tolerable_loss_reached = True



						#Exit conditions
						support_levels = kwargs['sr']._5min_refined_support_levels
						resistance_levels = kwargs['sr']._5min_refined_resistance_levels
						
						#if (side == "long" and len(resistance_levels[i]) >= 2 and resistance_levels[i][-1].get("highest price level") > resistance_levels[i][-2].get("highest price level")and close[i] < resistance_levels[i][-2].get("highest price level")) or (side == "short" and len(support_levels[i]) >= 2 and support_levels[i][-1].get("lowest price level") < support_levels[i][-2].get("lowest price level") and close[i] > support_levels[i][-2].get("lowest price level")):
						if (
							(side == "long" and len(resistance_levels[i]) >= 2 and len(support_levels[i]) >= 1 and resistance_levels[i][-1].get("highest price level") < resistance_levels[i][-2].get("highest price level") and resistance_levels[i][-1].get("latest time").timestamp() > support_levels[i][-1].get("latest time").timestamp()) or 
							(side == "short" and len(support_levels[i]) >= 2 and len(resistance_levels[i]) >= 1 and support_levels[i][-1].get("lowest price level") > support_levels[i][-2].get("lowest price level") and support_levels[i][-1].get("latest time").timestamp() > resistance_levels[i][-1].get("latest time").timestamp()) or
							(side == "long" and len(resistance_levels[i]) >= 2 and len(support_levels[i]) >= 1 and resistance_levels[i][-1].get("highest price level") > resistance_levels[i][-2].get("highest price level")and close[i] < resistance_levels[i][-2].get("highest price level") and resistance_levels[i][-1].get("latest time").timestamp() > support_levels[i][-1].get("latest time").timestamp()) or 
							(side == "short" and len(support_levels[i]) >= 2 and len(resistance_levels[i]) >= 1 and support_levels[i][-1].get("lowest price level") < support_levels[i][-2].get("lowest price level") and close[i] > support_levels[i][-2].get("lowest price level") and support_levels[i][-1].get("latest time").timestamp() > resistance_levels[i][-1].get("latest time").timestamp())
						):
							#positions[i][j] = self.exit_position(side, positions[i][j], close[i], curr_date, kwargs)
							self.exit_position(side, positions[i][j], close[i], curr_date, kwargs)
						else:
							if max_tolerable_loss_reached or is_end_of_trading_day:
								#positions[i][j] = self.exit_position(side, positions[i][j], close[i], curr_date, kwargs)
								self.exit_position(side, positions[i][j], close[i], curr_date, kwargs)
							else:
								#Just update profit per share
								positions[i][j].update({"profit per share":running_profit_per_share})						




								#Update peak price after it has been used
								if close[i] > peak_price_attained:
									if side == "long":
										positions[i][j].update({"peak price attained":close[i]}) 
								else:
									if side == "short":
										positions[i][j].update({"peak price attained":close[i]}) 

			#return positions
			#End for loop
		#End process_positions func


		#long_positions = process_positions(long_positions)
		#short_positions = process_positions(short_positions)

		process_positions(long_positions)
		process_positions(short_positions)		

		#return long_positions, short_positions 



	def print_last_risk_reward(self, stock_index, assets, close, positions, support_list, resistance_list, time, price_between_last_risk_reward_levels, kwargs):
		#stock_index = kwargs['stock_index']
		if len(positions) > 0:
			print(assets[stock_index])
			print("Time: "+str(time))
			print("Timestamp: "+str(time.timestamp()))
			print("Price: "+str(close))
			print("Last risk level: "+str(positions[-1].get("risk level")))
			print("Last reward level: "+str(positions[-1].get("reward level")))
			print("Price btw last risk/reward levels: "+str(price_between_last_risk_reward_levels))
			"""if len(support_list) > 0:
				print("Support[-1]: "+str(support_list[-1]))
			if len(resistance_list) > 0:	
				print("Resitance[-1]: "+str(resistance_list[-1]))
			if len(support_list) > 1:
				print("Support[-2]: "+str(support_list[-2]))
			if len(resistance_list) > 2:
				print("Resitance[-2]: "+str(resistance_list[-2]))	"""
			print("---------------------------------------------------------------------------")	



	"""
	Enter if (last same side pos if exists has exited) AND (last opp side pos if exists has exited OR last opp side position if exists has not exited but is out of the money-in which case exit last opp position first-)
	"""
	def position_qualifies_for_entry(self, asset, side, same_side_positions, opposite_side_positions, close, time, kwargs):
		if len(same_side_positions) < 1 and len(opposite_side_positions) < 1:#No positions yet
			return True#Create new position
		else:#At least one position exists ie len(same side) >= 1 or len(opp side) >= 1

			if len(same_side_positions) >= 1:#At least one same side position exists
				if not same_side_positions[-1].get("position exited"):#Last same side position not exited
					return False#Don't create new position

			if len(opposite_side_positions) >= 1:#At least one opp side position exists
				if not opposite_side_positions[-1].get("position exited"):#Last opp side position not exited
					last_opposite_position_in_the_money = False#By defualt, assume opposite position is out of the money
					last_opposite_position_running_profit = opposite_side_positions[-1].get("profit per share")

					if last_opposite_position_running_profit > 0:
						last_opposite_position_in_the_money = True

					if not last_opposite_position_in_the_money:#Last opp position out of the money
						
						opposite_side_positions[-1] = self.exit_position(side, opposite_side_positions[-1], close, time, kwargs)
						return True#Create new position
					else:#Last opp position in the money, retain that position and don't enter new position
						return False#Don't create new position

			return True#Defualt(create new position) unless one of the above conditions failed. This is reached if last same side position has exited AND (last opposite side position has exited  OR hasn't but is out of the money)




	def determine_entry(self, assets, is_trending_up, is_trending_down, risk_reward_stop_uptrending, risk_reward_stop_downtrending, _1min_is_uptrending, _1min_is_downtrending, market_price, time, kwargs):


		def go_long(risk, reward, risk_level, reward_level, stop_level):
			if reward_level > 0 and  risk < 0.5*kwargs['ind']._5min_atr[i] and kwargs['sr'].appropriate_time(time, kwargs['sr']._5min_refined_support_levels[i][-1]):# and not _1min_is_downtrending[i]:# and reward > atr[i] and (risk/reward) < 1:
				if self.position_qualifies_for_entry(assets[i], "long", kwargs['pNl']._5min_long_positions[i], kwargs['pNl']._5min_short_positions[i], market_price[i], time, kwargs):	
					#kwargs['pNl']._5min_long_positions[i] = self.enter_position(assets, kwargs['pNl']._5min_long_positions[i], "long", risk, reward, risk_level, reward_level, stop_level, market_price[i], time, kwargs) 
					self.enter_position(assets, kwargs['pNl']._5min_long_positions[i], "long", risk, reward, risk_level, reward_level, stop_level, market_price[i], time, kwargs) 

		def go_short(risk, reward, risk_level, reward_level, stop_level):
			if self.asset_is_shortable(assets[i], kwargs['shortable_assets']) and reward_level > 0 and  risk < 0.5*kwargs['ind']._5min_atr[i] and kwargs['sr'].appropriate_time(time, kwargs['sr']._5min_refined_resistance_levels[i][-1]):# and not _1min_is_uptrending[i]:# and reward > kwargs['ind']._5min_atr[i] and (risk/reward) < 1:
				if self.position_qualifies_for_entry(assets[i], "short", kwargs['pNl']._5min_short_positions[i], kwargs['pNl']._5min_long_positions[i], market_price[i], time, kwargs):		
					#kwargs['pNl']._5min_short_positions[i] = self.enter_position(assets, kwargs['pNl']._5min_short_positions[i], "short", risk, reward, risk_level, reward_level, stop_level, market_price[i], time, kwargs)				
					self.enter_position(assets, kwargs['pNl']._5min_short_positions[i], "short", risk, reward, risk_level, reward_level, stop_level, market_price[i], time, kwargs)					


		def determine_entry_for_asset(i):
			if is_trending_up[i] or is_trending_down[i]:#Mutually exclusive events
				risk = risk_reward_stop_uptrending[i].get("risk")
				reward = risk_reward_stop_uptrending[i].get("reward")
				risk_level = risk_reward_stop_uptrending[i].get("risk level")
				reward_level = risk_reward_stop_uptrending[i].get("reward level")
				stop_level = risk_reward_stop_uptrending[i].get("stop level")

				if is_trending_down[i]:
					risk = risk_reward_stop_downtrending[i].get("risk")
					reward = risk_reward_stop_downtrending[i].get("reward")
					risk_level = risk_reward_stop_downtrending[i].get("risk level")
					reward_level = risk_reward_stop_downtrending[i].get("reward level")
					stop_level = risk_reward_stop_downtrending[i].get("stop level")

				#Take new position if one doesn't already exist in given direction
				#Up and down should be mutually exclusive

				#Go long and go short originally defined here

				if is_trending_up[i]:#Swing hi
					if not kwargs['sr']._5min_trend[i].get("current trend") == "down":#Curr trend is either up or none(such as at market open)

						go_long(risk, reward, risk_level, reward_level, stop_level)
						#print(str(i)+") "+str(assets[i])+" went long")

					else:#Current trend is down
						#Only take position if supports are holding the line on moving average
						pass
					kwargs['sr']._5min_trend[i].update({"current trend":"up"})



				if is_trending_down[i]:#Swing lo	
					if not kwargs['sr']._5min_trend[i].get("current trend") == "up":#Curr trend is either down or none(such as at market open)

						go_short(risk, reward, risk_level, reward_level, stop_level)
						#print(str(i)+") "+str(assets[i])+" went short")

					else:#current trend is up
						#Only take position if resistances are holding the line on moving average
						pass
					kwargs['sr']._5min_trend[i].update({"current trend":"down"})

				#print(str(i)+") "+str(assets[i])+" sleeping...")
				#sleep(0.5)	#Don't sleep here in the live app. Only sleep after the exit out of the money positions		


		T = []
		for i in range(0, len(assets)):	
			t = threading.Thread(target=determine_entry_for_asset, args=(i,))
			T.append(t)


		for t in T:
			t.start()

		for t in T:
			t.join()

											



	#def determine_entry_exit(self, assets, _1min_open_price, _1min_close, time, start_of_day, kwargs):	
	def determine_entry_exit(self, assets, market_price, time, start_of_day, kwargs):		
		#Each uptrending/downtrending pair must be mutually exclusive

		#TRENDS
		_1min_is_uptrending_over2cycles, _1min_risk_reward_uptrending_over2cycles = kwargs['sr'].access_uptrending(assets, 2, kwargs['sr']._1min_refined_support_levels, kwargs['sr']._1min_refined_resistance_levels, market_price, kwargs['ind']._1min_atr, kwargs['ind']._1min_rsi, time, start_of_day, 1, kwargs['sr']._1min_trend, kwargs)
		_1min_is_downtrending_over2cycles, _1min_risk_reward_downtrending_over2cycles = kwargs['sr'].access_downtrending(assets, 2, kwargs['sr']._1min_refined_support_levels, kwargs['sr']._1min_refined_resistance_levels, market_price, kwargs['ind']._1min_atr, kwargs['ind']._1min_rsi, time, start_of_day, 1, kwargs['sr']._1min_trend, kwargs)		
		_5min_is_uptrending_over2cycles, _5min_risk_reward_uptrending_over2cycles = kwargs['sr'].access_uptrending(assets, 2, kwargs['sr']._5min_refined_support_levels, kwargs['sr']._5min_refined_resistance_levels, market_price, kwargs['ind']._5min_atr, kwargs['ind']._5min_rsi, time, start_of_day, 5, kwargs['sr']._5min_trend, kwargs)
		_5min_is_downtrending_over2cycles, _5min_risk_reward_downtrending_over2cycles = kwargs['sr'].access_downtrending(assets, 2, kwargs['sr']._5min_refined_support_levels, kwargs['sr']._5min_refined_resistance_levels, market_price, kwargs['ind']._5min_atr, kwargs['ind']._5min_rsi, time, start_of_day, 5, kwargs['sr']._5min_trend, kwargs)

		#EXIT
		_1min_macd_almost_crossing_signal = kwargs['ind'].macd_almost_crossing_signal(kwargs['ind']._1min_macd_np, kwargs['ind']._1min_macd_signal_line_np, len(assets))
		#kwargs['sr']._5min_uptrending_risk_reward, kwargs['sr']._5min_downtrending_risk_reward = self.determine_exit(assets, time, start_of_day, kwargs['pNl']._5min_long_positions, kwargs['pNl']._5min_short_positions, market_price, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, _1min_macd_almost_crossing_signal, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, kwargs['ind']._5min_atr, kwargs)
		#kwargs['pNl']._5min_long_positions, kwargs['pNl']._5min_short_positions = self.determine_exit(assets, time, start_of_day, kwargs['pNl']._5min_long_positions, kwargs['pNl']._5min_short_positions, market_price, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, _1min_macd_almost_crossing_signal, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, kwargs['ind']._5min_atr, kwargs)
		self.determine_exit(assets, time, start_of_day, kwargs['pNl']._5min_long_positions, kwargs['pNl']._5min_short_positions, market_price, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, _1min_macd_almost_crossing_signal, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, kwargs['ind']._5min_atr, kwargs)
		#self.determine_exit(assets, time, start_of_day, kwargs['pNl']._5min_long_positions, kwargs['pNl']._5min_short_positions, market_price, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, _1min_macd_almost_crossing_signal, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, kwargs['ind']._5min_atr, kwargs)


		#ENTRY
		#self.determine_entry(assets, _5min_is_uptrending_over2cycles, _5min_risk_reward_uptrending_over2cycles, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, market_price, time, "hi", kwargs)
		#self.determine_entry(assets, _5min_is_downtrending_over2cycles, _5min_risk_reward_downtrending_over2cycles, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, market_price, time, "lo", kwargs)
		self.determine_entry(assets, _5min_is_uptrending_over2cycles, _5min_is_downtrending_over2cycles, _5min_risk_reward_uptrending_over2cycles, _5min_risk_reward_downtrending_over2cycles, _1min_is_uptrending_over2cycles, _1min_is_downtrending_over2cycles, market_price, time, kwargs)


	def plot_curr_date(self, curr_date, test_date):
		return curr_date.timestamp() >= (test_date - pd.Timedelta('15 minutes') - pd.Timedelta('15 minutes') - pd.Timedelta('15 minutes')).timestamp() 



	def update_daily_hi_lo(self, open_price ,close, assets):
		for i in range(0, len(assets)):
			lo = open_price[i] 
			hi = close[i]
			if close[i] < lo:
				lo = close[i]
				hi = open_price[i]

			if lo < self.today_lo[i]:
				self.today_lo[i] = lo

			if hi > self.today_hi[i]:
				self.today_hi[i] = hi



	def execute1(self, backtrader, assets, initial_start_date, curr_date, end_date, test_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, kwargs):
		if curr_date == test_date:
			print("////////////////////////START TEST DATE////////////////////////\n")
		if curr_date >= test_date:
			print("test")
		print("Year "+str(curr_date.year))
		print("Month "+str(curr_date.month))
		print("Day "+str(curr_date.day))
		print("current date "+str(curr_date))
		print("test date "+str(test_date))
		print("initial start date "+str(initial_start_date))




	#USERS MUST PASS NUMPY ARRAYS FOR EVERY FACTOR USED 
	#FUNCTION MUST BE IMPLEMENTED BY USER
	#***************This is a required function users must implement
	#def execute(self, backtrader, assets, curr_date, end_date, periodA, periodB, TIME_FRAMES, SPREAD):
	def execute(self, backtrader, assets, initial_start_date, curr_date, end_date, test_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, kwargs):
		#PORTFOLIO_VAL = PORTFOLIO_VAL + 100
		global POSITION_SIZE
		#Check for sell/cover conditions before anything else
		#TERMINATE IF PORTFOLIO FALLS BELOW CRITICAL VALUE
		print("date "+str(curr_date))
		#print("minute "+str(curr_date.minute))
		if curr_date.minute % 5 == 0 and curr_date.minute % 15 != 0:
			print("************************\n")
		if curr_date.minute % 15 == 0:
			print("++++++++++++++++++++++++++++++\n\n")

		limit = 201#51#16
		_1min_close_prices_df = []
		#close = []
		_1min_open_price = []
		_1min_hi_prices_df = []
		_1min_lo_prices_df = []
		_1min_vol_df = []

		_5min_close_prices_df = []
		_5min_open_price = []
		_5min_hi_prices_df = []
		_5min_lo_prices_df = []
		_5min_vol_df = []		
		_5min_close  = []

		_15min_close_prices_df = []
		_15min_open_price = []
		_15min_hi_prices_df = []
		_15min_lo_prices_df = []
		_15min_vol_df = []
		_15min_close  = []



		_1min_close_prices_df, _1min_open_price, _1min_hi_prices_df, _1min_lo_prices_df, _1min_vol_df = backtrader.get_closes_open_his_los_vol(kwargs['config'], assets, _1min_periodB, limit, curr_date)
		_1min_close_price_df = _1min_close_prices_df.tail(n=1)
		_1min_close = _1min_close_price_df.to_numpy()[0]	
		_1min_close_price15 = None
		#_1min_candlestick_ohlc = curr_date.timestamp(), _1min_open_price[kwargs['stock_index']], _1min_hi_prices_df.tail(n=1).to_numpy()[0][kwargs['stock_index']], _1min_lo_prices_df.tail(n=1).to_numpy()[0][kwargs['stock_index']], _1min_close[kwargs['stock_index']], _1min_vol_df.tail(n=1).to_numpy()[0][kwargs['stock_index']]
		_1min_candlestick_ohlc_all_stocks  = []

		for i in range(0, len(assets)):
			_1min_candlestick_ohlc = curr_date.timestamp(), _1min_open_price[i], _1min_hi_prices_df.tail(n=1).to_numpy()[0][i], _1min_lo_prices_df.tail(n=1).to_numpy()[0][i], _1min_close[i], _1min_vol_df.tail(n=1).to_numpy()[0][i]
			_1min_candlestick_ohlc_all_stocks.append(_1min_candlestick_ohlc)

		#print("1 min close price15: "+str(kwargs['ind']._1min_close_price15))
		kwargs['ind']._1min_atr, kwargs['ind']._1min_short_atr, kwargs['ind']._1min_vwap, kwargs['ind']._1min_cummulative_pv, kwargs['ind']._1min_cummulative_vol, kwargs['ind']._1min_close_price15, kwargs['ind']._1min_rsi, kwargs['ind']._1min_close_price26_df, kwargs['ind']._1min_close_price12_df, kwargs['ind']._1min_close_price9_df, kwargs['ind']._1min_close_price_df, kwargs['ind']._1min_sma200, kwargs['ind']._1min_sma50, kwargs['ind']._1min_sma26, kwargs['ind']._1min_sma12, kwargs['ind']._1min_prev_ema200, kwargs['ind']._1min_prev_ema50, kwargs['ind']._1min_prev_ema26, kwargs['ind']._1min_prev_ema12, kwargs['ind']._1min_ema200, kwargs['ind']._1min_ema50, kwargs['ind']._1min_ema26, kwargs['ind']._1min_ema12, kwargs['ind']._1min_trend_moving_ave, kwargs['ind']._1min_fast_moving_ave, kwargs['ind']._1min_slow_moving_ave, kwargs['ind']._1min_stop_moving_ave, kwargs['ind']._1min_fast_moving_ave_prev, kwargs['ind']._1min_stop_moving_ave_prev, kwargs['ind']._1min_macd, kwargs['ind']._1min_prev_macd, kwargs['ind']._1min_macd_list, kwargs['ind']._1min_macd_signal_line, kwargs['ind']._1min_fast_ma, kwargs['ind']._1min_fast_ma_prev, kwargs['ind']._1min_slow_ma, kwargs['ind']._1min_trend_ma, kwargs['ind']._1min_macd_np, kwargs['ind']._1min_prev_macd_np, kwargs['ind']._1min_macd_signal_line_np, kwargs['ind']._1min_stop_ma, kwargs['ind']._1min_stop_ma_prev, kwargs['ind']._1min_macd_signal_diff = kwargs['ind'].generate_indicators(kwargs, assets, curr_date, initial_start_date, kwargs['ind']._1min_atr, kwargs['ind']._1min_vwaps, _1min_close_price15, _1min_close_prices_df, _1min_hi_prices_df, _1min_lo_prices_df, _1min_vol_df, kwargs['ind']._1min_true_range_list, kwargs['ind']._1min_short_true_range_list, kwargs['ind'].atr_window, kwargs['ind']._1min_prev_atr, kwargs['ind']._1min_short_atr, kwargs['ind']._1min_short_prev_atr, kwargs['ind'].short_atr_window, kwargs['ind']._1min_cummulative_pv, kwargs['ind']._1min_cummulative_vol, kwargs['ind']._1min_sma200, kwargs['ind']._1min_sma50, kwargs['ind']._1min_sma26, kwargs['ind']._1min_sma12, kwargs['ind']._1min_prev_ema200, kwargs['ind']._1min_prev_ema50, kwargs['ind']._1min_prev_ema26, kwargs['ind']._1min_prev_ema12, kwargs['ind']._1min_ema200, kwargs['ind']._1min_ema50, kwargs['ind']._1min_ema26, kwargs['ind']._1min_ema12, kwargs['ind']._1min_trend_moving_ave, kwargs['ind']._1min_fast_moving_ave, kwargs['ind']._1min_slow_moving_ave, kwargs['ind']._1min_stop_moving_ave, kwargs['ind']._1min_fast_moving_ave_prev, kwargs['ind']._1min_stop_moving_ave_prev, kwargs['ind']._1min_prev_macd, kwargs['ind']._1min_macd_list)
		#if True:
		#if self.plot_curr_date(curr_date, test_date):
			#kwargs['plt'].populate_axes(assets, curr_date, _1min_close, kwargs['ind']._1min_fast_ma, kwargs['ind']._1min_slow_ma, kwargs['ind']._1min_stop_ma, kwargs['ind']._1min_trend_ma, kwargs['ind']._1min_macd_np, kwargs['ind']._1min_macd_signal_line_np, kwargs['ind']._1min_rsi, kwargs['ind']._1min_atr, kwargs['ind']._1min_vwap, kwargs['ind']._1min_macd_signal_diff, _1min_candlestick_ohlc_all_stocks)	

		
		if curr_date.minute % 5 == 0:
			_5min_close_prices_df, _5min_open_price, _5min_hi_prices_df, _5min_lo_prices_df, _5min_vol_df = backtrader.get_closes_open_his_los_vol(kwargs['config'], assets, _5min_periodB, limit, curr_date)
			_5min_close_price_df = _5min_close_prices_df.tail(n=1)
			_5min_close = _5min_close_price_df.to_numpy()[0]	
			_5min_close_price15 = None
			_5min_candlestick_ohlc_all_stocks = []
			
			for i in range(0, len(assets)):
				_5min_candlestick_ohlc = curr_date.timestamp(), _5min_open_price[i], _5min_hi_prices_df.tail(n=1).to_numpy()[0][i], _5min_lo_prices_df.tail(n=1).to_numpy()[0][i], _5min_close[i], _5min_vol_df.tail(n=1).to_numpy()[0][i]
				_5min_candlestick_ohlc_all_stocks.append(_5min_candlestick_ohlc)
			
			kwargs['ind']._5min_last_open = _5min_open_price
			kwargs['ind']._5min_last_close = _5min_close
			#print("5 min close price15: "+str(kwargs['ind']._5min_close_price15))
			kwargs['ind']._5min_atr, kwargs['ind']._5min_short_atr, kwargs['ind']._5min_vwap, kwargs['ind']._5min_cummulative_pv, kwargs['ind']._5min_cummulative_vol, kwargs['ind']._5min_close_price15, kwargs['ind']._5min_rsi, kwargs['ind']._5min_close_price26_df, kwargs['ind']._5min_close_price12_df, kwargs['ind']._5min_close_price9_df, kwargs['ind']._5min_close_price_df, kwargs['ind']._5min_sma200, kwargs['ind']._5min_sma50, kwargs['ind']._5min_sma26, kwargs['ind']._5min_sma12, kwargs['ind']._5min_prev_ema200, kwargs['ind']._5min_prev_ema50, kwargs['ind']._5min_prev_ema26, kwargs['ind']._5min_prev_ema12, kwargs['ind']._5min_ema200, kwargs['ind']._5min_ema50, kwargs['ind']._5min_ema26, kwargs['ind']._5min_ema12, kwargs['ind']._5min_trend_moving_ave, kwargs['ind']._5min_fast_moving_ave, kwargs['ind']._5min_slow_moving_ave, kwargs['ind']._5min_stop_moving_ave, kwargs['ind']._5min_fast_moving_ave_prev, kwargs['ind']._5min_stop_moving_ave_prev, kwargs['ind']._5min_macd, kwargs['ind']._5min_prev_macd, kwargs['ind']._5min_macd_list, kwargs['ind']._5min_macd_signal_line, kwargs['ind']._5min_fast_ma, kwargs['ind']._5min_fast_ma_prev, kwargs['ind']._5min_slow_ma, kwargs['ind']._5min_trend_ma, kwargs['ind']._5min_macd_np, kwargs['ind']._5min_prev_macd_np, kwargs['ind']._5min_macd_signal_line_np, kwargs['ind']._5min_stop_ma, kwargs['ind']._5min_stop_ma_prev, kwargs['ind']._5min_macd_signal_diff = kwargs['ind'].generate_indicators(kwargs, assets, curr_date, initial_start_date, kwargs['ind']._5min_atr, kwargs['ind']._5min_vwaps, _5min_close_price15, _5min_close_prices_df, _5min_hi_prices_df, _5min_lo_prices_df, _5min_vol_df, kwargs['ind']._5min_true_range_list, kwargs['ind']._5min_short_true_range_list, kwargs['ind'].atr_window, kwargs['ind']._5min_prev_atr, kwargs['ind']._5min_short_atr, kwargs['ind']._5min_short_prev_atr, kwargs['ind'].short_atr_window, kwargs['ind']._5min_cummulative_pv, kwargs['ind']._5min_cummulative_vol, kwargs['ind']._5min_sma200, kwargs['ind']._5min_sma50, kwargs['ind']._5min_sma26, kwargs['ind']._5min_sma12, kwargs['ind']._5min_prev_ema200, kwargs['ind']._5min_prev_ema50, kwargs['ind']._5min_prev_ema26, kwargs['ind']._5min_prev_ema12, kwargs['ind']._5min_ema200, kwargs['ind']._5min_ema50, kwargs['ind']._5min_ema26, kwargs['ind']._5min_ema12, kwargs['ind']._5min_trend_moving_ave, kwargs['ind']._5min_fast_moving_ave, kwargs['ind']._5min_slow_moving_ave, kwargs['ind']._5min_stop_moving_ave, kwargs['ind']._5min_fast_moving_ave_prev, kwargs['ind']._5min_stop_moving_ave_prev, kwargs['ind']._5min_prev_macd, kwargs['ind']._5min_macd_list)
			#if True:
			if self.plot_curr_date(curr_date, test_date):
				kwargs['plt'].populate_axes(assets, curr_date, _5min_close, kwargs['ind']._5min_fast_ma, kwargs['ind']._5min_slow_ma, kwargs['ind']._5min_stop_ma, kwargs['ind']._5min_trend_ma, kwargs['ind']._5min_macd_np, kwargs['ind']._5min_macd_signal_line_np, kwargs['ind']._5min_rsi, kwargs['ind']._5min_atr, kwargs['ind']._5min_vwap, kwargs['ind']._5min_macd_signal_diff, _5min_candlestick_ohlc_all_stocks)		



		if curr_date.minute % 15 == 0:
			_15min_close_prices_df, _15min_open_price, _15min_hi_prices_df, _15min_lo_prices_df, _15min_vol_df = backtrader.get_closes_open_his_los_vol(kwargs['config'], assets, _15min_periodB, limit, curr_date)
			_15min_close_price_df = _15min_close_prices_df.tail(n=1)
			_15min_close = _15min_close_price_df.to_numpy()[0]	
			_15min_close_price15 = None
			_15min_candlestick_ohlc_all_stocks = []
			
			for i in range(0, len(assets)):
				_15min_candlestick_ohlc = curr_date.timestamp(), _15min_open_price[i], _15min_hi_prices_df.tail(n=1).to_numpy()[0][i], _15min_lo_prices_df.tail(n=1).to_numpy()[0][i], _15min_close[i], _15min_vol_df.tail(n=1).to_numpy()[0][i]
				_15min_candlestick_ohlc_all_stocks.append(_15min_candlestick_ohlc)
			
			kwargs['ind']._15min_last_open = _15min_open_price
			kwargs['ind']._15min_last_close = _15min_close	
			#print("15 min close price15: "+str(kwargs['ind']._15min_close_price15))
			kwargs['ind']._15min_atr, kwargs['ind']._15min_short_atr, kwargs['ind']._15min_vwap, kwargs['ind']._15min_cummulative_pv, kwargs['ind']._15min_cummulative_vol, kwargs['ind']._15min_close_price15, kwargs['ind']._15min_rsi, kwargs['ind']._15min_close_price26_df, kwargs['ind']._15min_close_price12_df, kwargs['ind']._15min_close_price9_df, kwargs['ind']._15min_close_price_df, kwargs['ind']._15min_sma200, kwargs['ind']._15min_sma50, kwargs['ind']._15min_sma26, kwargs['ind']._15min_sma12, kwargs['ind']._15min_prev_ema200, kwargs['ind']._15min_prev_ema50, kwargs['ind']._15min_prev_ema26, kwargs['ind']._15min_prev_ema12, kwargs['ind']._15min_ema200, kwargs['ind']._15min_ema50, kwargs['ind']._15min_ema26, kwargs['ind']._15min_ema12, kwargs['ind']._15min_trend_moving_ave, kwargs['ind']._15min_fast_moving_ave, kwargs['ind']._15min_slow_moving_ave, kwargs['ind']._15min_stop_moving_ave, kwargs['ind']._15min_fast_moving_ave_prev, kwargs['ind']._15min_stop_moving_ave_prev, kwargs['ind']._15min_macd, kwargs['ind']._15min_prev_macd, kwargs['ind']._15min_macd_list, kwargs['ind']._15min_macd_signal_line, kwargs['ind']._15min_fast_ma, kwargs['ind']._15min_fast_ma_prev, kwargs['ind']._15min_slow_ma, kwargs['ind']._15min_trend_ma, kwargs['ind']._15min_macd_np, kwargs['ind']._15min_prev_macd_np, kwargs['ind']._15min_macd_signal_line_np, kwargs['ind']._15min_stop_ma, kwargs['ind']._15min_stop_ma_prev, kwargs['ind']._15min_macd_signal_diff = kwargs['ind'].generate_indicators(kwargs, assets, curr_date, initial_start_date, kwargs['ind']._15min_atr, kwargs['ind']._15min_vwaps, _15min_close_price15, _15min_close_prices_df, _15min_hi_prices_df, _15min_lo_prices_df, _15min_vol_df, kwargs['ind']._15min_true_range_list, kwargs['ind']._15min_short_true_range_list, kwargs['ind'].atr_window, kwargs['ind']._15min_prev_atr, kwargs['ind']._15min_short_atr, kwargs['ind']._15min_short_prev_atr, kwargs['ind'].short_atr_window, kwargs['ind']._15min_cummulative_pv, kwargs['ind']._15min_cummulative_vol, kwargs['ind']._15min_sma200, kwargs['ind']._15min_sma50, kwargs['ind']._15min_sma26, kwargs['ind']._15min_sma12, kwargs['ind']._15min_prev_ema200, kwargs['ind']._15min_prev_ema50, kwargs['ind']._15min_prev_ema26, kwargs['ind']._15min_prev_ema12, kwargs['ind']._15min_ema200, kwargs['ind']._15min_ema50, kwargs['ind']._15min_ema26, kwargs['ind']._15min_ema12, kwargs['ind']._15min_trend_moving_ave, kwargs['ind']._15min_fast_moving_ave, kwargs['ind']._15min_slow_moving_ave, kwargs['ind']._15min_stop_moving_ave, kwargs['ind']._15min_fast_moving_ave_prev, kwargs['ind']._15min_stop_moving_ave_prev, kwargs['ind']._15min_prev_macd, kwargs['ind']._15min_macd_list)


		#Get yesterday's close and today's open
		if curr_date.hour == end_date.hour and curr_date.minute == end_date.minute:
			if not self.is_same_day(curr_date, test_date):	
				pass

		if self.is_same_day(curr_date, test_date) and curr_date.timestamp() == test_date.timestamp():
			print("\n\n///////////////START OF TEST DAY OPEN PRICE = "+str(_1min_open_price)+" ////////////////////////////////\n\n")
			self.file_log_write("\n"+str(curr_date)+"\n\n*************************************************\n")
			self.file_log1_write("\n"+str(curr_date)+"\n\n*************************************************\n")
			
			yesterday_open, yesterday_close, yesterday_hi, yesterday_lo, yesterday_vol = backtrader.get_prev_day_ochlv(kwargs['config'], assets, day_periodB, 2, curr_date)
			self.yesterday_hi = yesterday_hi[0]
			self.yesterday_lo = yesterday_lo[0]
			self.yesterday_close = yesterday_close[0]
			self.today_open = _1min_open_price
			print("yesterday hi "+str(self.yesterday_hi))
			print("yesterday lo "+str(self.yesterday_lo))
			print("yesterday close "+str(self.yesterday_close))
			print("today open "+str(self.today_open))

		if self.is_same_day(curr_date, test_date) and curr_date.timestamp() >= test_date.timestamp():
			self.update_daily_hi_lo(_1min_open_price ,_1min_close, assets)


		kwargs['sr']._1min_potential_support_levels = kwargs['sr'].append_to_support_list(assets, kwargs['ind']._1min_short_atr, _1min_open_price, _1min_close, _1min_lo_prices_df.tail(n=1).to_numpy()[0], curr_date, kwargs['sr']._1min_potential_support_levels, kwargs['sr']._1min_left_flanking_candlestick_support)
		
		kwargs['sr']._1min_potential_resistance_levels = kwargs['sr'].append_to_resistance_list(assets, kwargs['ind']._1min_short_atr, _1min_open_price, _1min_close, _1min_hi_prices_df.tail(n=1).to_numpy()[0], curr_date, kwargs['sr']._1min_potential_resistance_levels, kwargs['sr']._1min_left_flanking_candlestick_resistance)

		kwargs['sr']._1min_refined_support_levels = kwargs['sr'].refine_potential_support_levels(kwargs['sr']._1min_potential_support_levels, kwargs['sr']._1min_refined_support_levels, kwargs['ind']._1min_short_atr, test_date)
		kwargs['sr']._1min_refined_resistance_levels =  kwargs['sr'].refine_potential_resistance_levels(kwargs['sr']._1min_potential_resistance_levels, kwargs['sr']._1min_refined_resistance_levels, kwargs['ind']._1min_short_atr, test_date)

		if curr_date.minute % 5 == 0:
			kwargs['sr']._5min_potential_support_levels = kwargs['sr'].append_to_support_list(assets, kwargs['ind']._5min_short_atr, _5min_open_price, _5min_close, _5min_lo_prices_df.tail(n=1).to_numpy()[0], curr_date, kwargs['sr']._5min_potential_support_levels, kwargs['sr']._5min_left_flanking_candlestick_support)
			kwargs['sr']._5min_potential_resistance_levels = kwargs['sr'].append_to_resistance_list(assets, kwargs['ind']._5min_short_atr, _5min_open_price, _5min_close, _5min_hi_prices_df.tail(n=1).to_numpy()[0], curr_date, kwargs['sr']._5min_potential_resistance_levels, kwargs['sr']._5min_left_flanking_candlestick_resistance)

			kwargs['sr']._5min_refined_support_levels = kwargs['sr'].refine_potential_support_levels(kwargs['sr']._5min_potential_support_levels, kwargs['sr']._5min_refined_support_levels, kwargs['ind']._5min_short_atr, test_date)
			kwargs['sr']._5min_refined_resistance_levels =  kwargs['sr'].refine_potential_resistance_levels(kwargs['sr']._5min_potential_resistance_levels, kwargs['sr']._5min_refined_resistance_levels, kwargs['ind']._5min_short_atr, test_date)

		if curr_date.minute % 15 == 0:
			kwargs['sr']._15min_potential_support_levels = kwargs['sr'].append_to_support_list(assets, kwargs['ind']._15min_short_atr, _15min_open_price, _15min_close, _15min_lo_prices_df.tail(n=1).to_numpy()[0], curr_date, kwargs['sr']._15min_potential_support_levels, kwargs['sr']._15min_left_flanking_candlestick_support)
			kwargs['sr']._15min_potential_resistance_levels = kwargs['sr'].append_to_resistance_list(assets, kwargs['ind']._15min_short_atr, _15min_open_price, _15min_close, _15min_hi_prices_df.tail(n=1).to_numpy()[0], curr_date, kwargs['sr']._15min_potential_resistance_levels, kwargs['sr']._15min_left_flanking_candlestick_resistance)

			kwargs['sr']._15min_refined_support_levels = kwargs['sr'].refine_potential_support_levels(kwargs['sr']._15min_potential_support_levels, kwargs['sr']._15min_refined_support_levels, kwargs['ind']._15min_short_atr, test_date)
			kwargs['sr']._15min_refined_resistance_levels =  kwargs['sr'].refine_potential_resistance_levels(kwargs['sr']._15min_potential_resistance_levels, kwargs['sr']._15min_refined_resistance_levels, kwargs['ind']._15min_short_atr, test_date)



		if self.is_same_day(curr_date, test_date) and curr_date.timestamp() >= test_date.timestamp():	
			#self.determine_entry_exit(assets, _1min_open_price, _1min_close, curr_date, test_date, kwargs)
			self.determine_entry_exit(assets, _1min_close, curr_date, test_date, kwargs)
			


		#At day's start, get yesterday's data
		if curr_date == initial_start_date:
			pass
			print("Hello Trading Day")


		#Train at end of day before test day 
		#if curr_date == end_date:
		if curr_date.hour == end_date.hour and curr_date.minute == end_date.minute:

			if self.is_same_day(curr_date, test_date):	

				for i in range(0, len(assets)):
					#kwargs['plt'].plot_full_chart(self, test_date ,kwargs['sr']._1min_refined_support_levels, kwargs['sr']._1min_refined_resistance_levels, kwargs['pNl']._5min_long_positions, kwargs['pNl']._5min_short_positions, assets[i], i)
					kwargs['plt'].plot_full_chart(self, test_date ,kwargs['sr']._5min_refined_support_levels, kwargs['sr']._5min_refined_resistance_levels, kwargs['pNl']._5min_long_positions, kwargs['pNl']._5min_short_positions, assets[i], i)
					pass

				print("End of test day reached. Let's do some analysis;)")
				for i in range(0, len(assets)):
					print(str(assets[i])+": Prev day hi "+str(self.yesterday_hi[i])+" prev day lo "+str(self.yesterday_lo[i])+" Today hi "+str(self.today_hi[i])+" Today lo "+str(self.today_lo[i]))
				kwargs['pNl'].process_pnl(assets, kwargs)
				kwargs['pNl'].log_pnl(self, assets, test_date, kwargs)
				#kwargs['sr'].print_support_resistance_list(assets, kwargs['stock_index'])

				#print("Risk/Rewards Uptrending\n"+str(kwargs['pNl']._5min_long_positions[kwargs['stock_index']]))
				#print("Risk/Rewards Downtrending\n"+str(kwargs['pNl']._5min_short_positions[kwargs['stock_index']]))
			



