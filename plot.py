"""
Author: Ngusum Akofu
Date Created: Feb 24, 2021
"""

import matplotlib.pyplot as mplt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import matplotlib.ticker as mticker	
import pandas as pd
import numpy as np
import math



class Plot:
	
	def __init__(self, num_assets):

		self.ax = mplt.gca()
		self.ax1 = mplt.subplot2grid((1,1), (0,0))	
		#self.ax = []
		#self.ax1 = []
		self.fig = mplt.figure()
		self.ax3D = self.fig.add_subplot(111, projection='3d')
		

		self.time_list = []
		self.price_list = []
		self.fast_ma_list = []
		self.slow_ma_list = []
		self.really_slow_ma_list = []
		self.stop_ma_list = []
		self.rsi_list = []
		self.macd0_list = []
		self.macd0_signal_line_list = []
		self.macd1_list = []
		self.macd1_signal_line_list = []		
		self.atr_list = []
		self.vwap_list = []
		self.macd_signal_diff0_list = []
		self.ohlc = []


		for i in range(0, num_assets):
			#self.ax.append(mplt.gca())
			#self.ax1.append(mplt.subplot2grid((1,1), (0,0)))
			self.time_list.append([])
			self.price_list.append([])
			self.fast_ma_list.append([])
			self.slow_ma_list.append([])
			self.really_slow_ma_list.append([])
			self.stop_ma_list.append([])
			self.rsi_list.append([])
			self.macd0_list.append([])
			self.macd0_signal_line_list.append([])
			self.macd1_list.append([])
			self.macd1_signal_line_list.append([])		
			self.atr_list.append([])
			self.vwap_list.append([])
			self.macd_signal_diff0_list.append([])
			self.ohlc.append([])		


	#def populate_axes(time_list, price_list, fast_ma_list, slow_ma_list, really_slow_ma_list, time, price, fast_ma, slow_ma, really_slow_ma):	
	#def populate_axes(self, time, price, fast_ma, slow_ma, stop_ma, really_slow_ma, macd0, macd0_signal_line, macd1, macd1_signal_line, rsi, atr, vwap, macd_signal_diff0, kwargs):
	"""def populate_axes(self, time, price, fast_ma, slow_ma, stop_ma, really_slow_ma, macd0, macd0_signal_line, rsi, atr, vwap, macd_signal_diff0, candlestick, kwargs):
		self.time_list.append(time.timestamp())#Each entry is a time obj
		self.price_list.append(price[kwargs['stock_index']])#Each entry is a list of the closing price of each stock
		self.fast_ma_list.append(fast_ma[kwargs['stock_index']])#Each entry is a list of the fast mas of each stock
		self.slow_ma_list.append(slow_ma[kwargs['stock_index']])
		self.stop_ma_list.append(stop_ma[kwargs['stock_index']])
		self.really_slow_ma_list.append(really_slow_ma[kwargs['stock_index']])
		self.rsi_list.append(rsi[kwargs['stock_index']])
		self.macd0_list.append(macd0[kwargs['stock_index']])
		self.macd0_signal_line_list.append(macd0_signal_line[kwargs['stock_index']])
		#self.macd1_list.append(macd1[kwargs['stock_index']])
		#self.macd1_signal_line_list.append(macd1_signal_line[kwargs['stock_index']])		
		self.atr_list.append(atr[kwargs['stock_index']])
		self.vwap_list.append(vwap[kwargs['stock_index']])
		self.macd_signal_diff0_list.append(macd_signal_diff0[kwargs['stock_index']])
		self.ohlc.append(candlestick)"""


	def populate_axes(self, assets, time, price, fast_ma, slow_ma, stop_ma, really_slow_ma, macd0, macd0_signal_line, rsi, atr, vwap, macd_signal_diff0, candlestick):
		for i in range(0, len(assets)):
			self.time_list[i].append(time.timestamp())#Each entry is a time obj
			self.price_list.append(price[i])#Each entry is a list of the closing price of each stock
			self.fast_ma_list[i].append(fast_ma[i])#Each entry is a list of the fast mas of each stock
			self.slow_ma_list[i].append(slow_ma[i])
			self.stop_ma_list[i].append(stop_ma[i])
			self.really_slow_ma_list[i].append(really_slow_ma[i])
			self.rsi_list[i].append(rsi[i])
			self.macd0_list[i].append(macd0[i])
			self.macd0_signal_line_list[i].append(macd0_signal_line[i])
			#self.macd1_list[i].append(macd1[i])
			#self.macd1_signal_line_list[i].append(macd1_signal_line[i])		
			self.atr_list[i].append(atr[i])
			self.vwap_list[i].append(vwap[i])
			self.macd_signal_diff0_list[i].append(macd_signal_diff0[i])
			self.ohlc[i].append(candlestick[i])



	def populate_axes_orb(self, time, atr, vwap, rsi, macd0, macd0_signal_line, macd_signal_diff0, kwargs):	
		#print("in populate axis: atr "+str(atr))
		self.time_list.append(time)#Each entry is a time obj
		self.atr_list.append(atr[kwargs['stock_index']])	
		self.vwap_list.append(vwap[kwargs['stock_index']])		
		self.rsi_list.append(rsi[kwargs['stock_index']])	
		self.macd0_list.append(macd0[kwargs['stock_index']])
		self.macd0_signal_line_list.append(macd0_signal_line[kwargs['stock_index']])	
		self.macd_signal_diff0_list.append(macd_signal_diff0[kwargs['stock_index']])			


	def populate_axes_fast_slow_ma(self, time, price, fast_ma, slow_ma, kwargs):
		self.time_list.append(time)#Each entry is a time obj
		self.price_list.append(price[kwargs['stock_index']])#Each entry is a list of the closing price of each stock
		self.fast_ma_list.append(fast_ma[kwargs['stock_index']])#Each entry is a list of the fast mas of each stock
		self.slow_ma_list.append(slow_ma[kwargs['stock_index']])#Each entry is a list of the slow mas of each stock


	def fast_slow_ma_ribbon(self):
		return pd.DataFrame({'time':self.time_list, 'price':self.price_list, 'fast ma':self.fast_ma_list, 'slow ma':self.slow_ma_list})


	def ribbon(self):
		#return pd.DataFrame({'time':self.time_list, 'price':self.price_list, 'fast ma':self.fast_ma_list, 'slow ma':self.slow_ma_list, 'trend ma':self.really_slow_ma_list})
		return pd.DataFrame({'time':self.time_list, 'price':self.price_list, 'fast ma':self.fast_ma_list, 'slow ma':self.slow_ma_list, 'trend ma':self.really_slow_ma_list, 'stop ma':self.stop_ma_list, 'vwap':self.vwap_list})


	def rsi_ribbon(self):
		return pd.DataFrame({'time':self.time_list, 'rsi':self.rsi_list})


	def atr_ribbon(self):
		return pd.DataFrame({'time':self.time_list, 'atr':self.atr_list})		


	def vwap_ribbon(self):
		return pd.DataFrame({'time':self.time_list, 'vwap':self.vwap_list})			


	def macd0_ribbon(self):
		return pd.DataFrame({'time':self.time_list, 'macd0':self.macd0_list, 'macd0 signal line':self.macd0_signal_line_list, 'macd signal diff0':self.macd_signal_diff0_list})


	def macd1_ribbon(self):
		return pd.DataFrame({'time':self.time_list, 'macd1':self.macd1_list, 'macd1 signal line':self.macd1_signal_line_list})



	def plot_support_resistances(self, strategy, test_date, the_list, col, ax1):

		for j in range(0, len(the_list)):
			time = []
			level = []
			original_time = the_list[j].get("original time")
			latest_time = the_list[j].get("latest time")
			average_price_level = the_list[j].get("average price level")
			if strategy.plot_curr_date(original_time, test_date):
			#if True:
				time.append(original_time.timestamp() - 500)
				time.append(latest_time.timestamp() + 500)
				level.append(average_price_level)
				level.append(average_price_level)

			ax1.plot(time, level, color=col)



	def plot_risk_reward(self, strategy, test_date, the_list, marker_type, ax1):
		for j in range(0, len(the_list)):#Plot each risk rewar pair together with price point
			time_range = []
			risk_level = []
			reward_level = []

			time = the_list[j].get("entry time")
			risk = the_list[j].get("risk level")
			reward = the_list[j].get("reward level")	
			price = the_list[j].get("entry price")	

			print("time "+str(time))	
			print("risk "+str(risk))	
			print("reward "+str(reward))	
			print("price "+str(price))	

			if strategy.plot_curr_date(time, test_date):
			##if True:
				time_range.append(time.timestamp() - 400)
				time_range.append(time.timestamp() + 400)
				risk_level.append(risk)
				risk_level.append(risk)
				reward_level.append(reward)
				reward_level.append(reward)

			#ax1.plot(time_range, risk_level, color="orange", linestyle = 'dotted')
			#ax1.plot(time_range, reward_level, color="blue", linestyle = 'dotted')
			ax1.plot([time.timestamp()], [price], marker=marker_type, markersize=5, color="black")



	def plot_entry_exit(self, the_list, marker_type, marker_size, ax1):
		#color_map = ['#5900b3', '#008080', '#0073e6', '#660066', '#cc5200', '#996633', '#b3b300', '#29293d', '#00b300', '#e600e6', '#5900b3', '#008080', '#0073e6', '#660066', '#cc5200', '#996633', '#b3b300', '#29293d', '#00b300', '#e600e6', '#5900b3', '#008080', '#0073e6', '#660066', '#cc5200', '#996633', '#b3b300', '#29293d', '#00b300', '#e600e6', '#5900b3', '#008080', '#0073e6', '#660066', '#cc5200', '#996633', '#b3b300', '#29293d', '#00b300', '#e600e6', '#5900b3', '#008080', '#0073e6', '#660066', '#cc5200', '#996633', '#b3b300', '#29293d', '#00b300', '#e600e6']
		#color_map = ['#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300']
		color_map = ['#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00']#, '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300', '#000099', '#808000', '#990099', '#194d00', '#6600cc', '#262626', '#5c8a8a', '#e65c00', '#0059b3', '#b3b300', '#b300b3', '#00ff00', '#993300']
		for j in range(0, len(the_list)):
			entry_time = the_list[j].get("entry time")
			entry_price = the_list[j].get("entry price")
			exit_time = the_list[j].get("exit time")
			exit_price = the_list[j].get("exit price")			
			ax1.plot([entry_time.timestamp()], [entry_price], marker=marker_type, markersize=marker_size, color=color_map[j%len(color_map)])
			ax1.plot([exit_time.timestamp()], [exit_price], marker=marker_type, markersize=marker_size, color=color_map[j%len(color_map)])



	def plot_full_chart(self, strategy, test_date, support_list, resistance_list, uptrending_risk_reward, downtrending_risk_reward, ticker, i):

		ax1 = mplt.subplot2grid((1,1), (0,0))	

		candlestick_ohlc(ax1, self.ohlc[i], width=40, colorup='green', colordown='red')

		#self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
		ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
		ax1.grid(True)

		mplt.xlabel('Date')
		mplt.ylabel('Price')
		mplt.title(ticker)
		mplt.subplots_adjust(left=0.09, bottom=0.02, right=0.94, top=0.90, wspace=0.4, hspace=0)
		ax1.plot(self.time_list[i], self.fast_ma_list[i])
		ax1.plot(self.time_list[i], self.slow_ma_list[i])
		ax1.plot(self.time_list[i], self.stop_ma_list[i])
		ax1.plot(self.time_list[i], self.really_slow_ma_list[i])
		ax1.plot(self.time_list[i], self.vwap_list[i])

		self.plot_support_resistances(strategy ,test_date, support_list[i], "green", ax1)
		self.plot_support_resistances(strategy ,test_date, resistance_list[i], "red", ax1)

		#self.plot_risk_reward(strategy ,test_date, uptrending_risk_reward[i], "^", ax1)
		#self.plot_risk_reward(strategy ,test_date, downtrending_risk_reward[i], "o", ax1)

		self.plot_entry_exit(uptrending_risk_reward[i], "^", 5, ax1)
		self.plot_entry_exit(downtrending_risk_reward[i], "o", 5, ax1)
		
		mplt.show()	



	"""def plot_full_chart(self, strategy, test_date, support_list, resistance_list, ticker, i):

		candlestick_ohlc(self.ax1, self.ohlc, width=40, colorup='green', colordown='red')

		#self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
		self.ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
		self.ax1.grid(True)

		mplt.xlabel('Date')
		mplt.ylabel('Price')
		mplt.title(ticker)
		mplt.subplots_adjust(left=0.09, bottom=0.02, right=0.94, top=0.90, wspace=0.4, hspace=0)
		#self.ax1.plot(self.time_list, self.fast_ma_list)
		#self.ax1.plot(self.time_list, self.slow_ma_list)
		#self.ax1.plot(self.time_list, self.stop_ma_list)
		#self.ax1.plot(self.time_list, self.really_slow_ma_list)
		#self.ax1.plot(self.time_list, self.vwap_list)f

		self.plot_support_resistances(strategy ,test_date, support_list[i], "green")
		self.plot_support_resistances(strategy ,test_date, resistance_list[i], "red")

		mplt.show()	
	"""



	def plot_moving_averages(self, ribbon):
		#gca stands for 'get current axis'
		#ax = mplt.gca()
		ribbon.plot(kind='line', x='time', y='trend ma', color='blue', ax=self.ax)
		ribbon.plot(kind='line', x='time', y='stop ma', color='red', ax=self.ax)
		ribbon.plot(kind='line', x='time', y='slow ma', color='orange', ax=self.ax)
		ribbon.plot(kind='line', x='time', y='fast ma', color='yellow', ax=self.ax)
		ribbon.plot(kind='line', x='time', y='vwap', color='purple', ax=self.ax)
		"""
		ribbon.plot(kind='line', x='time', y='trend ma', color='blue', ax=self.ax)
		ribbon.plot(kind='line', x='time', y='slow ma', color='orange', ax=self.ax)
		ribbon.plot(kind='line', x='time', y='fast ma', color='green', ax=self.ax)
		"""
		#df_ribbon.plot(kind='scatter',x='time',y='bull',color='black')
		#df_ribbon.plot(kind='scatter',x='time',y='bear',color='red')
		#df_ribbon.plot(kind='line', x='time', y='bull', color='black', ax=self.ax)
		#df_ribbon.plot(kind='line', x='time', y='bear', color='red', ax=self.ax)	
		mplt.show()	


	def plot_fast_slow_ma(self, fast_slow_ma_ribbon):
		#gca stands for 'get current axis'
		#ax = mplt.gca()
		fast_slow_ma_ribbon.plot(kind='line', x='time', y='slow ma', color='orange', ax=self.ax)
		fast_slow_ma_ribbon.plot(kind='line', x='time', y='fast ma', color='green', ax=self.ax)
		mplt.show()	


	def plot_rsi(self, rsi_ribbon):
		#gca stands for 'get current axis'
		#ax = mplt.gca()
		rsi_ribbon.plot(kind='line', x='time', y='rsi', color='blue', ax=self.ax)	
		mplt.show()		


	def plot_atr(self, atr_ribbon):
		#gca stands for 'get current axis'
		#ax = mplt.gca()
		#print("time list "+str(self.time_list))
		#print("atr list "+str(self.atr_list))
		atr_ribbon.plot(kind='line', x='time', y='atr', color='green', ax=self.ax)	
		mplt.show()		


	def plot_vwap(self, vwap_ribbon):
		vwap_ribbon.plot(kind='line', x='time', y='vwap', color='blue', ax=self.ax)	
		mplt.show()					


	def plot_macd0(self, macd_ribbon):
		#gca stands for 'get current axis'
		#ax = mplt.gca()
		macd_ribbon.plot(kind='line', x='time', y='macd0', color='red', ax=self.ax)	
		macd_ribbon.plot(kind='line', x='time', y='macd0 signal line', color='black', ax=self.ax)		
		macd_ribbon.plot(kind='line', x='time', y='macd signal diff0', color='green', ax=self.ax)		
		mplt.show()		


	def plot_macd1(self, macd_ribbon):
		#gca stands for 'get current axis'
		#ax = mplt.gca()
		macd_ribbon.plot(kind='line', x='time', y='macd1', color='green', ax=self.ax)	
		macd_ribbon.plot(kind='line', x='time', y='macd1 signal line', color='grey', ax=self.ax)			
		mplt.show()	



	def plot_actual_v_hyo(self, actual, hyp):
		ribbon = pd.DataFrame({'actual':actual, 'hyp':hyp})
		ribbon.plot(kind='line', x='actual', y='hyp', color='green', ax=self.ax)			
		mplt.show()


	def plot_learning_curves(self, m, training_error, test_error):
		ribbon = pd.DataFrame({'Num examples':m, 'Training error':training_error, 'Test error':test_error})
		ribbon.plot(kind='line', x='Num examples', y='Training error', color='green', ax=self.ax)	
		ribbon.plot(kind='line', x='Num examples', y='Test error', color='red', ax=self.ax)			
		mplt.show()



	def plot_features_vs_profit(self, assets, stock_index, X, Y, feature_index, feature_name):

		feature_list = [] 
		profit_list = []
		feature_list_squared = [] 
		log_profit_list = []

		for i in range(0, len(X[stock_index])):
			feature_list.append(X[stock_index][i][feature_index])
			feature_list_squared.append((X[stock_index][i][feature_index])**2)
			profit_list.append(Y[stock_index][i])
			#log_profit_list.append(math.log(Y[stock_index][i], 2))


		x_axis_name = assets[stock_index]+" "+feature_name
		y_axis_name = "profit"
		ribbon = pd.DataFrame({x_axis_name:feature_list, y_axis_name:profit_list})
		ribbon.plot(kind='scatter', x=x_axis_name, y=y_axis_name, color='green', ax=self.ax)

		#mplt.title(str(assets[stock_index])+" "+str(feature_name)+" vs profit")
		#mplt.scatter(feature_list, profit_list, color = 'hotpink')


		x_axis_name1 = assets[stock_index]+" "+feature_name+" squared"
		y_axis_name1 = "profit"
		ribbon1 = pd.DataFrame({x_axis_name1:feature_list_squared, y_axis_name1:profit_list})
		ribbon1.plot(kind='scatter', x=x_axis_name1, y=y_axis_name1, color='green', ax=self.ax)


		mplt.show()	
		
		#print("Feature list\n"+str(feature_list))
		#print("Profit list\n"+str(profit_list))		
		#print("Length list "+str(len(X[stock_index]))+"\n")
		#print("X\n................................\n"+str(X[stock_index])+"\n")
		#print("Y\n................................\n"+str(Y[stock_index])+"\n")




	def plot_corr(self, assets, i, k, x_list, y_list, r):
		x_axis_name = assets[i]+" x"+str(k)+" correlation coeff: "+str(r)
		y_axis_name = "profit"
		ribbon = pd.DataFrame({x_axis_name:x_list, y_axis_name:y_list})
		ribbon.plot(kind='scatter', x=x_axis_name, y=y_axis_name, color='green', ax=self.ax)
		mplt.show()




	def plot_3Dfeatures_vs_profit(self, assets, stock_index, X, Y, feature1_index, feature2_index, feature1_name, feature2_name):
		fig = mplt.figure()
		ax = fig.add_subplot(111, projection='3d')

		x =[]
		y =[]
		z =[]

		for i in range(0, len(X[stock_index])):
			x.append(X[stock_index][i][feature1_index])
			y.append(X[stock_index][i][feature2_index])
			z.append(Y[stock_index][i])

		ax.scatter(x, y, z, c='r', marker='o')

		ax.set_xlabel(feature1_name)
		ax.set_ylabel(feature2_name)
		ax.set_zlabel('Profit')

		mplt.show()



	def plot_scatter_log_reg(self, X, Y):
		X1pos = []
		X2pos = []
		X1neg = []
		X2neg = []		
		for i in range(0, len(X[0])):
			if Y[0][i] > 0:
				X1pos.append(X[0][i][1])
				X2pos.append(X[0][i][2])
			else:		
				X1neg.append(X[0][i][1])
				X2neg.append(X[0][i][2])

		#ribbon = pd.DataFrame({'X1':X1, 'X2':X2})
		#ribbon.plot(kind='scatter', x='X1', y='X2', color='green', ax=self.ax)	
		#mplt.scatter(X1pos, X2pos, c='green') 
		#mplt.scatter(X1neg, X2neg, c='red') 
		ribbon1 = pd.DataFrame({'X1pos':X1pos, 'X2pos':X2pos})
		ribbon1.plot(kind='scatter', x='X1pos', y='X2pos', color='green', ax=self.ax)		
		ribbon1 = pd.DataFrame({'X1neg':X1neg, 'X2neg':X2neg})
		ribbon1.plot(kind='scatter', x='X1neg', y='X2neg', color='red', ax=self.ax)				
		mplt.show()	


	def plot_scatter_lin_reg(self, X, Y):
		X_list = []
		Y_list = Y[0]
		for i in range(0, len(X[0])):
			X_list.append(X[0][i][1])		
		#mplt.title(str(side)+" Plot")
		ribbon = pd.DataFrame({'X':X_list, 'Y':Y_list})
		ribbon.plot(kind='scatter', x='X', y='Y', color='green', ax=self.ax)	
		mplt.show()	


	def plot_test_grad_descent(self, X, Y, side):
		X_list = []
		Y_list = Y[0]
		for i in range(0, len(X[0])):
			X_list.append(X[0][i][1])

		#print(X_list)
		#print(Y_list)
		mplt.title(str(side)+" Plot")
		#mplt.scatter(X_list, Y_list, color = 'hotpink')
		#mplt.scatter(np.array([1,2,3]), np.array([1,2,3]))
		#mplt.scatter(np.array([1,2,3]), np.array([1,2,3]), color = 'hotpink')

		ribbon = pd.DataFrame({'X':X_list, 'Y':Y_list})
		ribbon.plot(kind='scatter', x='X', y='Y', color='green', ax=self.ax)	
		mplt.show()				



	def plotYactul_vsYhyp(self, i, assets, Yactual, Yhyp, side):
		mplt.title(str(assets[i])+" "+str(side)+" Plot")
		#mplt.scatter(Yactual, Yhyp, color = 'hotpink')
		#mplt.show()	
		Yactual2 = []
		for i in range(0, len(Yhyp)):
			Yactual2.append(Yactual[i])#Yyp may be shorter than Yactual
		#print(str(side)+" "+str(assets[i])+" Yhyp "+str(Yhyp)+" Yactual "+str(Yactual))	

		ribbon = pd.DataFrame({'Yhyp':Yhyp, 'Yactual':Yactual2})
		ribbon.plot(kind='scatter', x='Yhyp', y='Yactual', color='green', ax=self.ax)
		mplt.show()		



	def threeDplot_demo(self):
		xs =[1,2,3,4,5,6,7,8,9,10]
		ys =[5,6,2,3,13,4,1,2,4,8]
		zs =[2,3,3,3,5,7,9,11,9,10]

		xt =[-1,-2,-3,-4,-5,-6,-7,8,-9,-10, -11]
		yt =[-5,-6,-2,-3,-13,-4,-1,2,-4,-8, -11]
		zt =[-2,-3,-3,-3,-5,-7,9,-11,-9,-10, - 11]

		self.ax3D.scatter(xs, ys, zs, c='r', marker='o')
		self.ax3D.scatter(xt, yt, zt, c='b', marker='^')

		self.ax3D.set_xlabel('X Label')
		self.ax3D.set_ylabel('Y Label')
		self.ax3D.set_zlabel('Z Label')

		mplt.show()



	def plot_features3D_distinguished_by_profit(self, stock_index, X, Y, index1, index2, index3, title1, title2, title3):
		x_negative = []
		y_negative = []
		z_negative = []
		x_positive = []
		y_positive = []
		z_positive = []	

		for i in range(0, len(X[stock_index])):
			x = X[stock_index][i][index1]
			y = X[stock_index][i][index2]
			z = X[stock_index][i][index3]

			if Y[stock_index][i] > 0:
				x_positive.append(x)
				y_positive.append(y)
				z_positive.append(z)
			else:
				x_negative.append(x)
				y_negative.append(y)
				z_negative.append(z)

		"""
		print(str(title1)+" positives\n"+str(x_positive))
		print(str(title2)+" positives\n"+str(y_positive))
		print(str(title3)+" positives\n"+str(z_positive))
		print(str(title1)+" negatives\n"+str(x_negative))
		print(str(title2)+" negatives\n"+str(y_negative))
		print(str(title3)+" negatives\n"+str(z_negative))	
		"""

		self.ax3D.scatter(x_positive, y_positive, z_positive, c='r', marker='o')
		self.ax3D.scatter(x_negative, y_negative, z_negative, c='b', marker='^')

		self.ax3D.set_xlabel(title1)
		self.ax3D.set_ylabel(title2)
		self.ax3D.set_zlabel(title3)

		mplt.show()
	




	def plot_features3D_distinguished_by_profit2(self, stock_index, X, Y, index1, index2, index3, title1, title2, title3):

		colors = ['r', 'g', 'b', 'k', 'c', 'm', 'y']
		arr = [[], [], [], []]

		num_intervals = len(arr)#Based on # of categories above	

		for i in range(0, num_intervals):
			arr[i].append([])#x for that interval	
			arr[i].append([])#y for that interval	
			arr[i].append([])#z for that interval	


		max_profit = -np.inf
		min_profit = np.inf

		for i in range(0, len(Y[stock_index])):
			#print(Y[stock_index][i])
			if Y[stock_index][i] > max_profit:
				max_profit = Y[stock_index][i] 
			if Y[stock_index][i] < min_profit:
				min_profit = Y[stock_index][i] 			

		profit_range = max_profit - min_profit
		#print("max profit: "+str(max_profit)+" min profit: "+str(min_profit)+" range: "+str(profit_range))

		interval = profit_range/num_intervals


		for i in range(0, len(X[stock_index])):
			#print(i)
			x = X[stock_index][i][index1]
			y = X[stock_index][i][index2]
			z = X[stock_index][i][index3]
			lower_bound_iterator = min_profit#Position an iterator at the start of range ie at min profit
			upper_bound_iterator = min_profit + interval

			#print("x "+str(x)+" y "+str(y)+" z "+str(z))
			#Determine whihc group in which to place x,y,z
			j = 0#Keeps track of the interval number
			while lower_bound_iterator < max_profit:
				if Y[stock_index][i] > lower_bound_iterator and Y[stock_index][i] <= upper_bound_iterator:
					arr[j][0].append(x)
					arr[j][1].append(y)
					arr[j][2].append(z)
				lower_bound_iterator += interval 
				upper_bound_iterator += interval
				j += 1


		#for i in range(0, len(arr)):
			#print("Group "+str(i)+"............................\n"+str(arr[i]))


		for i in range(0, num_intervals):
			self.ax3D.scatter(arr[i][0], arr[i][1], arr[i][2], c=colors[i], marker='o')


		self.ax3D.set_xlabel(title1)
		self.ax3D.set_ylabel(title2)
		self.ax3D.set_zlabel(title3)

		mplt.show()



	def plot_gradient_descent(self, cost, converged_alpha, lmbda, ticker, side):
		iterations_list = [] 
		
		for i in range(0, len(cost)):
			iterations_list.append(i)

		mplt.title(str(side)+": "+str(ticker)+" lambda = "+str(lmbda)+" alpha = "+str(converged_alpha))
		#mplt.scatter(iterations_list, cost, color = 'hotpink')
		#x_axis = str(side)+": "+str(ticker)+" alpha = "+str(converged_alpha)
		#y_axis = "Cost"
		ribbon = pd.DataFrame({'x axis':iterations_list, 'y axis':cost})
		#ribbon.plot(kind='line', x=x_axis, y=y_axis, color='blue', ax=self.ax)
		ribbon.plot(kind='line', x='x axis', y='y axis', color='blue', ax=self.ax)
		mplt.show()		
