"""
Author: Ngusum Akofu
Date Created: Nov 17, 2021
"""

import numpy as np
#import math
#import pandas as pd
#import plot as plt
#import copy
#import analytics as ana






class Indicators:
	
	def __init__(self):

		self._1min_sma200 = None
		self._1min_sma50 = None
		self._1min_sma26 = None
		self._1min_sma12 = None		
		self._1min_prev_ema12 = None
		self._1min_prev_ema26 = None
		self._1min_prev_ema50 = None
		self._1min_prev_ema200 = None
		self._1min_ema12 = None
		self._1min_ema26 = None
		self._1min_ema50 = None
		self._1min_ema200 = None
		self._1min_fast_ma = None
		self._1min_fast_ma_prev = None 
		self._1min_slow_ma = None 
		self._1min_trend_ma = None 
		self._1min_stop_ma = None 
		self._1min_stop_ma_prev = None 
		self._1min_close_price26_df = None
		self._1min_close_price12_df = None
		self._1min_close_price9_df = None
		self._1min_close_price_df = None	
		self._1min_fast_moving_ave = None
		self._1min_fast_moving_ave_prev = None
		self._1min_slow_moving_ave = None
		self._1min_stop_moving_ave = None
		self._1min_stop_moving_ave_prev = None
		self._1min_trend_moving_ave = None
		self._1min_macd_np = []
		self._1min_prev_macd_np = []
		self._1min_macd_signal_line_np = []
		self._1min_macd_signal_diff = None

		self._5min_sma200 = None
		self._5min_sma50 = None
		self._5min_sma26 = None
		self._5min_sma12 = None		
		self._5min_prev_ema12 = None
		self._5min_prev_ema26 = None
		self._5min_prev_ema50 = None
		self._5min_prev_ema200 = None
		self._5min_ema12 = None
		self._5min_ema26 = None
		self._5min_ema50 = None
		self._5min_ema200 = None
		self._5min_fast_ma = None
		self._5min_fast_ma_prev = None 
		self._5min_slow_ma = None 
		self._5min_trend_ma = None 
		self._5min_stop_ma = None 
		self._5min_stop_ma_prev = None 		
		self._5min_close_price26_df = None
		self._5min_close_price12_df = None
		self._5min_close_price9_df = None
		self._5min_close_price_df = None	
		self._5min_fast_moving_ave = None
		self._5min_fast_moving_ave_prev = None	
		self._5min_slow_moving_ave = None
		self._5min_stop_moving_ave = None
		self._5min_stop_moving_ave_prev = None
		self._5min_trend_moving_ave = None		
		self._5min_macd_np = []
		self._5min_prev_macd_np = []
		self._5min_macd_signal_line_np = []
		self._5min_macd_signal_diff = None

		self._15min_sma200 = None
		self._15min_sma50 = None
		self._15min_sma26 = None
		self._15min_sma12 = None		
		self._15min_prev_ema12 = None
		self._15min_prev_ema26 = None
		self._15min_prev_ema50 = None
		self._15min_prev_ema200 = None
		self._15min_ema12 = None
		self._15min_ema26 = None
		self._15min_ema50 = None
		self._15min_ema200 = None
		self._15min_fast_ma = None
		self._15min_fast_ma_prev = None 
		self._15min_slow_ma = None 
		self._15min_trend_ma = None 
		self._15min_stop_ma = None 
		self._15min_stop_ma_prev = None 
		self._15min_close_price26_df = None
		self._15min_close_price12_df = None
		self._15min_close_price9_df = None
		self._15min_close_price_df = None	
		self._15min_fast_moving_ave = None	
		self._15min_fast_moving_ave_prev = None
		self._15min_slow_moving_ave = None
		self._15min_stop_moving_ave = None
		self._15min_stop_moving_ave_prev = None
		self._15min_trend_moving_ave = None	
		self._15min_macd_np = []	
		self._15min_prev_macd_np = []
		self._15min_macd_signal_line_np = []
		self._15min_macd_signal_diff = None


		self._1min_macd = None
		self._1min_macd_signal_line = None
		self._1min_prev_macd = None
		self._1min_macd_list = []
		self._1min_prev_macd_lessthan_signal = []
		self._1min_macd_lessthan_signal = []
		self._5min_macd = None
		self._5min_macd_signal_line = None		
		self._5min_prev_macd = None
		self._5min_macd_list = []
		self._5min_prev_macd_lessthan_signal = []
		self._5min_macd_lessthan_signal = []
		self._15min_macd = None
		self._15min_macd_signal_line = None				
		self._15min_prev_macd = None
		self._15min_macd_list = []	
		self._15min_prev_macd_lessthan_signal = []
		self._15min_macd_lessthan_signal = []			

		self.prev_open = None
		self.positions_manager = []



		self._1min_vwap = 0 
		self._5min_vwap = 0 
		self._15min_vwap = 0 
		self.vwaps_num = 3
		self._1min_vwaps = [[]] * self.vwaps_num
		self._5min_vwaps = [[]] * self.vwaps_num
		self._15min_vwaps = [[]] * self.vwaps_num
		self._1min_cummulative_pv = []
		self._5min_cummulative_pv =[]
		self._15min_cummulative_pv = []
		self._1min_cummulative_vol = []
		self._5min_cummulative_vol = []
		self._15min_cummulative_vol = []
		
		self.signal_line_lookback_period = 9



		#self.macd0_np = None
		#self.prev_macd0_np = None
		#self.macd0_signal_line_np = None

		self._1min_prev_atr = 0
		self._1min_atr = 0
		self._1min_short_atr = 0
		self._1min_short_prev_atr = 0	
		self._5min_prev_atr = 0
		self._5min_atr = 0
		self._5min_short_atr = 0
		self._5min_short_prev_atr = 0	
		self._15min_prev_atr = 0
		self._15min_atr = 0
		self._15min_short_atr = 0
		self._15min_short_prev_atr = 0	
		self.atr_window = 14
		self.short_atr_window = 2#3
		self._1min_true_range_list = [] #[[]] * self.atr_window	
		self._5min_true_range_list = []		
		self._15min_true_range_list = []
		self._1min_short_true_range_list = [] #[[]] * self.atr_window	
		self._5min_short_true_range_list = []		
		self._15min_short_true_range_list = []			
		#self._1min_true_range = None	
		#self._5min_true_range = None	
		#self._15min_true_range = None	


		self._1min_rsi = None
		self._5min_rsi = None
		self._15min_rsi = None

		self._5min_last_open = []
		self._15min_last_open = []
		self._5min_last_close = []
		self._15min_last_close = []		

		self._1min_close_price15 = []
		self._5min_close_price15 = []
		self._15min_close_price15 = []

		self.RSI_PERIOD = 15
		#self.macd_signal_diff0 = None
		#self.prev_macd_signal_diff0 = None		



	def macd_almost_crossing_signal(self, macd, signal, n):
		arr = [False] * n
		for i in range(0, n):
			if abs(macd[i] - signal[i]) <= 0.02:
				arr[i] = True
		return arr


	def macd_less_than_signal(self, macd, signal, n):
		arr = [True] * n
		for i in range(0, n):
			if macd[i] > signal[i]:
				arr[i] = False
		return arr



	def compute_atr(self, num_assets, true_range_list):
		atr_sums = [0] * num_assets
		for i in range(0, len(true_range_list)):
			for j in range(0, num_assets):
				atr_sums[j] += true_range_list[i][j]
		return np.divide(atr_sums, len(true_range_list))
			

	def compute_true_range(self, num_assets, curr_hi, curr_lo, prev_close):
		tr = [0] * num_assets
		for i in range(0, num_assets):
			diff1 = abs(curr_hi[i] - curr_lo[i])
			diff2 = abs(curr_hi[i] - prev_close[i])
			diff3 = abs(curr_lo[i] - prev_close[i])
			tr[i] = diff1
			if diff2 > diff1:
				tr[i] = diff2
			if diff3 > diff2:
				tr[i] = diff3
		return tr



	def compute_sma(self, df):
		return df.mean(axis=0)

	

	def compute_ema(self, price, prev_ema, N):
		k = 2/(N+1)
		return ((price - prev_ema)*k + prev_ema)


	def compute_dema(self, ema, prev_ema, N):	
		return 2*ema - self.compute_ema(ema, prev_ema, N)



	def compute_rsi(self, prices, lookback, num_assets):
		cum_gain = [0] * num_assets
		cum_loss = [0] * num_assets
		i = 0
		while i < len(prices):
			if i > 0:
				gain = np.subtract(prices[i], prices[i-1])

				j = 0
				while j < num_assets:
					if gain[j] > 0.0:
						cum_gain[j] += gain[j]
					elif gain[j] < 0.0:
						cum_loss[j] += (gain[j] * -1)
					j += 1
			i += 1
		avg_gain = np.divide(cum_gain, (lookback - 1))
		avg_loss = np.divide(cum_loss, (lookback - 1))		

		rsi = [0] * num_assets
	
		i = 0
		while i < num_assets:
			if avg_loss[i] == 0:
				rsi[i] = 100
			else:
				rs = avg_gain[i]/avg_loss[i]
				rsi[i] = (100 - (100 / (1 + rs))) 
			i += 1 
		return rsi



	def macd_sma(self, df, end_index):
		new_df = []
		n = self.signal_line_lookback_period
		start_index = end_index - (n - 1)
		for i in range(start_index, end_index+1):
			new_df.append(df[i])
		S = sum(df)
		N = len(df)
		return S/N



	def generate_first_n_macds(self, df, N, fastN, slowN):

		prev_fast_ema = None
		prev_slow_ema = None
		macd_list = []

		i = N-1
		while i >= 0:
			df_slowN = None
			if i != 0:
				df_slowN = df[:i*-1].tail(n=slowN)#Remove the last i rows and then return the last n of what's left
			else:
				df_slowN = df.tail(n=slowN)

			close_price_df = df_slowN.tail(n=1)

			slow_sma = self.compute_sma(df_slowN)
			fast_sma = self.compute_sma(df_slowN.tail(n=N))

			if i == N-1:#First period
				prev_fast_ema = fast_sma
				prev_slow_ema = slow_sma

			slow_ema = self.compute_ema(close_price_df.mean(), prev_slow_ema, slowN)	
			fast_ema = self.compute_ema(close_price_df.mean(), prev_fast_ema, fastN)
			
			#print("fast ema "+str(fast_ema))
			#print("slow ema "+str(slow_ema))

			macd = fast_ema - slow_ema
			macd_list.append(macd)	

			#Updates
			prev_fast_ema = fast_ema
			prev_slow_ema = slow_ema	

			i -= 1
		#print("macd list "+str(macd_list))
		return macd_list



	def generate_first_n_true_ranges(self, assets, close_prices_df, hi_prices_df, lo_prices_df, atr_window, true_range_list):
		start_index = -2#Start period prior to open
		end_index = start_index - (atr_window - 1)
		for i in range(end_index, start_index + 1):
			true_range = self.compute_true_range(len(assets), hi_prices_df.to_numpy()[i], lo_prices_df.to_numpy()[i], close_prices_df.to_numpy()[i-1])
			true_range_list.append(true_range)


	def generate_first_n_vwaps(self, close, hi, lo, vol, N, vwaps):
		_cummulative_pv = []
		_cummulative_vol = []
		start_index = N*-1
		end_index = -1
		for i in range(start_index, end_index+1):

			if i == start_index:

				ave_price = np.divide(np.add(np.add(hi.to_numpy()[i], lo.to_numpy()[i]), close.to_numpy()[i]), 3)

				_cummulative_pv = np.multiply(ave_price, vol.to_numpy()[i])
				_cummulative_vol = vol.to_numpy()[i]

			else:
				pv = np.multiply(close.to_numpy()[i], vol.to_numpy()[i])
				_cummulative_pv = np.add(_cummulative_pv, pv)
				_cummulative_vol = np.add(_cummulative_vol, vol.to_numpy()[i])
			cummulative_pv = _cummulative_pv
			cummulative_vol = _cummulative_vol
			vwap = np.divide(_cummulative_pv, _cummulative_vol)
			del vwaps[0]#Delete first element
			vwaps.append(vwap)#Add newly computed factor to the end

			return [cummulative_pv, cummulative_vol]



	def compute_simple_moving_averages(self, close_prices_df):
		close_price26_df = close_prices_df.tail(n=26)
		close_price12_df = close_prices_df.tail(n=12)
		close_price9_df = close_prices_df.tail(n=9)
		close_price_df = close_prices_df.tail(n=1)
		sma200 = self.compute_sma(close_prices_df.tail(n=200))
		sma50 = self.compute_sma(close_prices_df.tail(n=50))
		sma26 = self.compute_sma(close_prices_df.tail(n=26))
		sma12 = self.compute_sma(close_prices_df.tail(n=12))
		return [close_price26_df, close_price12_df, close_price9_df, close_price_df, sma200, sma50, sma26, sma12]


	def compute_exponential_moving_averages(self, assets, curr_date, start_date, close_price_df, close_prices_df, sma200, sma50, sma26, sma12, _ema200, _ema50, _ema26, _ema12, _macd_list, _fast_moving_ave_prev, _stop_moving_ave_prev):#Also incorporates macds
		prev_ema200 = _ema200
		prev_ema50 = _ema50
		prev_ema26 = _ema26
		prev_ema12 = _ema12	
		macd_list = _macd_list
		if curr_date == start_date:
			prev_ema200 = sma200
			prev_ema50 = sma50
			prev_ema26 = sma26
			prev_ema12 = sma12
			len_list = self.signal_line_lookback_period + 8
			macd_list = self.generate_first_n_macds(close_prices_df.tail(n=26+len_list), len_list, 12, 26)#Enough to get first 9 periods from n = 1 to n = 9 + 26 so as to get sma26
			#self.generate_first_n_macds(close_prices_df.tail(n=50+len_list), len_list, 26, 50, self.macd1_list)#Enough to get first 9 periods from n = 1 to n = 9 + 50 so as to get sma50
		#print("In compute ema "+str(macd_list))

		ema200 = self.compute_ema(close_price_df.mean(), prev_ema200, 200)
		ema50 = self.compute_ema(close_price_df.mean(), prev_ema50, 50)
		ema26 = self.compute_ema(close_price_df.mean(), prev_ema26, 26)	
		ema12 = self.compute_ema(close_price_df.mean(), prev_ema12, 12)
		trend_moving_ave = ema200
		fast_moving_ave = ema12
		slow_moving_ave = ema26
		stop_moving_ave = ema50

		fast_moving_ave_prev = _fast_moving_ave_prev
		stop_moving_ave_prev = _stop_moving_ave_prev
		if curr_date == start_date:
			fast_moving_ave_prev = fast_moving_ave
			stop_moving_ave_prev = stop_moving_ave

		macd = fast_moving_ave - slow_moving_ave
		#print("macd "+str(macd[0]))
		prev_macd = macd_list[-1]#Last element in macd would be previous macd. So, no need to update this var since the last n of them are always in this array

		del macd_list[0]#Delete first element
		macd_list.append(macd)#Add new macd val to macd list
		macd_signal_line = self.macd_sma(macd_list, -1)	


		return[prev_ema200, prev_ema50, prev_ema26, prev_ema12, ema200, ema50, ema26, ema12, trend_moving_ave, fast_moving_ave, slow_moving_ave, stop_moving_ave, fast_moving_ave_prev, stop_moving_ave_prev, macd, prev_macd, macd_list, macd_signal_line]



	def compute_vwap(self, curr_date, start_date, close_prices_df, hi_prices_df, lo_prices_df, vol_df, vwaps, cummulative_pv, cummulative_vol):
		#vwap = 0
		if curr_date == start_date:
			cummulative_pv, cummulative_vol	= self.generate_first_n_vwaps(close_prices_df.tail(n=self.vwaps_num), hi_prices_df.tail(n=self.vwaps_num), lo_prices_df.tail(n=self.vwaps_num), vol_df.tail(n=self.vwaps_num), self.vwaps_num, vwaps)
			
			vwap = vwaps[-1]
		else:
			pv = np.multiply(close_prices_df.tail(n=1).to_numpy()[0], vol_df.tail(n=1).to_numpy()[0])
			cummulative_pv = np.add(cummulative_pv, pv)
			cummulative_vol = np.add(cummulative_vol, vol_df.tail(n=1).to_numpy()[0])
			vwap = np.divide(cummulative_pv, cummulative_vol)

			del vwaps[0]#Delete first element
			vwaps.append(vwap)#Add new vwap val to vwaplist

		return [vwap, cummulative_pv, cummulative_vol]




	def compute_average_true_range(self, assets, curr_date, start_date, close_prices_df, hi_prices_df, lo_prices_df, true_range_list, atr_window, atr, prev_atr):
		if curr_date == start_date:
			#print("Generating first n true ranges for "+str(curr_date))
			self.generate_first_n_true_ranges(assets, close_prices_df.tail(n=atr_window+2), hi_prices_df.tail(n=atr_window+2), lo_prices_df.tail(n=atr_window+2), atr_window, true_range_list)
			prev_atr = self.compute_atr(len(assets), true_range_list)#Uses true range list before it gets modified below
		else:
			prev_atr = atr#Uses true range list before it gets modified below

		true_range = self.compute_true_range(len(assets), hi_prices_df.to_numpy()[-1], lo_prices_df.to_numpy()[-1], close_prices_df.to_numpy()[-2])
		#print("TR list "+str(true_range_list))
		del true_range_list[0]#Delete first element
		true_range_list.append(true_range)
		return self.compute_atr(len(assets), true_range_list)	
			


	def numpify_moving_averages(self, fast_moving_ave, fast_moving_ave_prev, slow_moving_ave, trend_moving_ave, stop_moving_ave, stop_moving_ave_prev, macd, prev_macd, macd_signal_line):
		fast_ma = fast_moving_ave.to_numpy()
		fast_ma_prev = fast_moving_ave_prev.to_numpy()
		slow_ma = slow_moving_ave.to_numpy()
		trend_ma = trend_moving_ave.to_numpy()
		macd_np = macd.to_numpy()
		#self.macd1_np = self.macd1.to_numpy()
		prev_macd_np = prev_macd.to_numpy()
		macd_signal_line_np = macd_signal_line.to_numpy()
		stop_ma = stop_moving_ave.to_numpy()
		stop_ma_prev = stop_moving_ave_prev.to_numpy()
		return [fast_ma, fast_ma_prev, slow_ma, trend_ma, macd_np, prev_macd_np, macd_signal_line_np, stop_ma, stop_ma_prev]



	def generate_macd_signal_diff(self, num_assets, macd_np, macd_signal_line):
		i = 0
		macd_signal_diff = [[]]*num_assets
		while i < num_assets:
			macd_signal_diff[i] = np.subtract(macd_np[i], macd_signal_line[i])
			i += 1

		return macd_signal_diff				



	def generate_indicators(self, kwargs, assets, curr_date, today, atr, vwaps, close_price15, close_prices_df, hi_prices_df, lo_prices_df, vol_df, true_range_list, short_true_range_list, atr_window, prev_atr, short_atr, short_prev_atr, short_atr_window, cummulative_pv, cummulative_vol, sma200, sma50, sma26, sma12, prev_ema200, prev_ema50, prev_ema26, prev_ema12, ema200, ema50, ema26, ema12, trend_moving_ave, fast_moving_ave, slow_moving_ave, stop_moving_ave, fast_moving_ave_prev, stop_moving_ave_prev, prev_macd, macd_list):
		atr = self.compute_average_true_range(assets, curr_date, today, close_prices_df, hi_prices_df, lo_prices_df, true_range_list, atr_window, atr, prev_atr)
		short_atr = self.compute_average_true_range(assets, curr_date, today, close_prices_df, hi_prices_df, lo_prices_df, short_true_range_list, short_atr_window, short_atr, short_prev_atr)
		vwap, cummulative_pv, cummulative_vol = self.compute_vwap(curr_date, today, close_prices_df, hi_prices_df, lo_prices_df, vol_df, vwaps, cummulative_pv, cummulative_vol)
		close_price15 = close_prices_df.tail(n=self.RSI_PERIOD).to_numpy()
		rsi = self.compute_rsi(close_price15, self.RSI_PERIOD, kwargs['num_assets'])

		close_price26_df, close_price12_df, close_price9_df, close_price_df, sma200, sma50, sma26, sma12 = self.compute_simple_moving_averages(close_prices_df)
		prev_ema200, prev_ema50, prev_ema26, prev_ema12, ema200, ema50, ema26, ema12, trend_moving_ave, fast_moving_ave, slow_moving_ave, stop_moving_ave, fast_moving_ave_prev, stop_moving_ave_prev, macd, prev_macd, macd_list, macd_signal_line  = self.compute_exponential_moving_averages(assets, curr_date, today, close_price_df, close_prices_df, sma200, sma50, sma26, sma12, ema200, ema50, ema26, ema12, macd_list, fast_moving_ave_prev, stop_moving_ave_prev)
		fast_ma, fast_ma_prev, slow_ma, trend_ma, macd_np, prev_macd_np, macd_signal_line_np, stop_ma, stop_ma_prev = self.numpify_moving_averages(fast_moving_ave, fast_moving_ave_prev, slow_moving_ave, trend_moving_ave, stop_moving_ave, stop_moving_ave_prev, macd, prev_macd, macd_signal_line)
		macd_signal_diff = self.generate_macd_signal_diff(len(assets), macd_np, macd_signal_line)	

		return [atr, short_atr, vwap, cummulative_pv, cummulative_vol, close_price15, rsi, close_price26_df, close_price12_df, close_price9_df, close_price_df, sma200, sma50, sma26, sma12, prev_ema200, prev_ema50, prev_ema26, prev_ema12, ema200, ema50, ema26, ema12, trend_moving_ave, fast_moving_ave, slow_moving_ave, stop_moving_ave, fast_moving_ave_prev, stop_moving_ave_prev, macd, prev_macd, macd_list, macd_signal_line, fast_ma, fast_ma_prev, slow_ma, trend_ma, macd_np, prev_macd_np, macd_signal_line_np, stop_ma, stop_ma_prev, macd_signal_diff]



	def old(self):
		pass
		"""kwargs['ind']._1min_atr = kwargs['ind'].compute_average_true_range(assets, curr_date, today, _1min_close_prices_df, _1min_hi_prices_df, _1min_lo_prices_df, kwargs['ind']._1min_true_range_list, kwargs['ind'].atr_window, kwargs['ind']._1min_atr, kwargs['ind']._1min_prev_atr)
		kwargs['ind']._1min_short_atr = kwargs['ind'].compute_average_true_range(assets, curr_date, today, _1min_close_prices_df, _1min_hi_prices_df, _1min_lo_prices_df, kwargs['ind']._1min_short_true_range_list, kwargs['ind'].short_atr_window, kwargs['ind']._1min_short_atr, kwargs['ind']._1min_short_prev_atr)
		kwargs['ind']._1min_vwap, kwargs['ind']._1min_cummulative_pv, kwargs['ind']._1min_cummulative_vol = kwargs['ind'].compute_vwap(curr_date, today, _1min_close_prices_df, _1min_hi_prices_df, _1min_lo_prices_df, _1min_vol_df, kwargs['ind']._1min_vwaps, kwargs['ind']._1min_cummulative_pv, kwargs['ind']._1min_cummulative_vol)
		_1min_close_price15 = _1min_close_prices_df.tail(n=kwargs['ind'].RSI_PERIOD).to_numpy()
		kwargs['ind']._1min_rsi = kwargs['ind'].compute_rsi(_1min_close_price15, kwargs['ind'].RSI_PERIOD, kwargs['num_assets'])

		kwargs['ind']._1min_close_price26_df, kwargs['ind']._1min_close_price12_df, kwargs['ind']._1min_close_price9_df, kwargs['ind']._1min_close_price_df, kwargs['ind']._1min_sma200, kwargs['ind']._1min_sma50, kwargs['ind']._1min_sma26, kwargs['ind']._1min_sma12 = kwargs['ind'].compute_simple_moving_averages(_1min_close_prices_df)
		kwargs['ind']._1min_prev_ema200, kwargs['ind']._1min_prev_ema50, kwargs['ind']._1min_prev_ema26, kwargs['ind']._1min_prev_ema12, kwargs['ind']._1min_ema200, kwargs['ind']._1min_ema50, kwargs['ind']._1min_ema26, kwargs['ind']._1min_ema12, kwargs['ind']._1min_trend_moving_ave, kwargs['ind']._1min_fast_moving_ave, kwargs['ind']._1min_slow_moving_ave, kwargs['ind']._1min_stop_moving_ave, kwargs['ind']._1min_fast_moving_ave_prev, kwargs['ind']._1min_stop_moving_ave_prev, kwargs['ind']._1min_macd, kwargs['ind']._1min_prev_macd, kwargs['ind']._1min_macd_list, kwargs['ind']._1min_macd_signal_line  = kwargs['ind'].compute_exponential_moving_averages(assets, curr_date, today, _1min_close_price_df, _1min_close_prices_df, kwargs['ind']._1min_sma200, kwargs['ind']._1min_sma50, kwargs['ind']._1min_sma26, kwargs['ind']._1min_sma12, kwargs['ind']._1min_ema200, kwargs['ind']._1min_ema50, kwargs['ind']._1min_ema26, kwargs['ind']._1min_ema12, kwargs['ind']._1min_macd_list, kwargs['ind']._1min_fast_moving_ave_prev, kwargs['ind']._1min_stop_moving_ave_prev)
		kwargs['ind']._1min_fast_ma, kwargs['ind']._1min_fast_ma_prev, kwargs['ind']._1min_slow_ma, kwargs['ind']._1min_trend_ma, kwargs['ind']._1min_macd_np, kwargs['ind']._1min_prev_macd_np, kwargs['ind']._1min_macd_signal_line_np, kwargs['ind']._1min_stop_ma, kwargs['ind']._1min_stop_ma_prev = kwargs['ind'].numpify_moving_averages(kwargs['ind']._1min_fast_moving_ave, kwargs['ind']._1min_fast_moving_ave_prev, kwargs['ind']._1min_slow_moving_ave, kwargs['ind']._1min_trend_moving_ave, kwargs['ind']._1min_stop_moving_ave, kwargs['ind']._1min_stop_moving_ave_prev, kwargs['ind']._1min_macd, kwargs['ind']._1min_prev_macd, kwargs['ind']._1min_macd_signal_line)
		kwargs['ind']._1min_macd_signal_diff = kwargs['ind'].generate_macd_signal_diff(len(assets), kwargs['ind']._1min_macd_np, kwargs['ind']._1min_macd_signal_line)	
		"""		