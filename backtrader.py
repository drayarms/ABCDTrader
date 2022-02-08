"""
Author: Ngusum Akofu
Date Created: Nov 18, 2020
"""
import pandas as pd
#import matplotlib.pyplot as mplt
import math
from urllib.error import HTTPError
from werkzeug.exceptions import HTTPException
import time
#POSITIONS = []#Will hold dictionary of positions





##
#Values candlestic period1 can take: minute, 1Min, 5Min, 15Min, day or 1D. minute is an alias of 1Min. Similarly, day is of 1D.
#Candlestick period A and B should be same. They are just different formats of the same thing


class Backtrader:
	def __init__(self):
		self.positions = []
		self.winnerslosers = []
		self.portfolio_val = 0.0




	#def _get_df(assets, timeframe, limit, start_dt, end_dt):
	def _get_df(self, config, assets, timeframe, limit, end_dt):
		def get_barset(assets):
			"""return config.api.get_barset(
            	assets,
            	timeframe,
            	limit=limit,
            	#start=start_dt
            	end=end_dt,
            	#after=start_dt,
            	#until=end_dt
        	)"""

			barset_got = False
			while(not barset_got):
				try:
					return config.api.get_barset(#v1
					#return config.api.get_bars(#v2	
            			assets,
            			timeframe,
            			limit=limit,
            			#start=start_dt
            			end=end_dt,
            			#after=start_dt,
            			#until=end_dt
        			)
				#except HTTPError:
				except HTTPException:
					print("Waiting before retrying...")
					time.sleep(3)#Suspends thread for specified num seconds					
					barset_got = False



    	# Max number of symbols we can request at once is 200. So, we only want to get 200 rows at a time
		barset = None
		i = 0

		while i <= len(assets) - 1:
			if barset is None:
				barset = get_barset(assets[i:i+200])#Add all data for first company from row i to row i+200
			else:#Barset has cols already
				barset.update(get_barset(assets[i:i+200]))#Continue adding data from the rest of the companies from row i to row i+200
			i += 200

		return barset.df


	def get_last_n_dates(self, config, assets, periodB, limit, curr_date):
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		#return df.select_dtypes(include=['datetime64'])[:-1]
		return df.tail(n=limit).select_dtypes(include=['datetime64'])[:-1]

	def get_last_n_vols(self, config, assets, periodB, limit, curr_date):
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		return df.xs('volume', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)		


	def get_curr_day_o(self, config, assets, periodB, limit, curr_date):
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		return df.xs('open', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit).to_numpy()


	def get_prev_day_c(self, config, assets, periodB, limit, curr_date):
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		return df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy()


	def get_curr_day_c(self, config, assets, periodB, limit, curr_date):
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		return df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit).to_numpy()


	def get_curr_day_oc(self, config, assets, periodB, limit, curr_date):
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		return [df.xs('open', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit).to_numpy(), df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit).to_numpy()]


	def get_prev_day_ochlv(self, config, assets, periodB, limit, curr_date):
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		return [df.xs('open', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy(), df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy(), df.xs('high', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy(), df.xs('low', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy(), df.xs('volume', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy()]
		#return [df.xs('open', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1], df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1], df.xs('high', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1], df.xs('low', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1], df.xs('volume', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1]]


	def get_prev_days_ochlv(self, config, assets, periodB, limit, curr_date):
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		return [df.xs('open', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy(), df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy(), df.xs('high', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy(), df.xs('low', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy(), df.xs('volume', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1].to_numpy()]
		#return [df.xs('open', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1], df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1], df.xs('high', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1], df.xs('low', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1], df.xs('volume', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)[:-1]]


	#def get_df(assets, timeframe, limit, start_dt, end_dt):
	def get_df(self, config, assets, timeframe, limit, end_dt):
		#return _get_df(assets, timeframe, limit, start_dt, end_dt)
		return self._get_df(config, assets, timeframe, limit, end_dt)


	def get_closes_open_his_los_vol(self, config, assets, periodB, limit, curr_date):
		#df = self.get_prices(config, assets, periodB, limit, curr_date.isoformat()).xs('close', axis=1, level=1)
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		#print("Non fillna df "+str(df.xs('close', axis=1, level=1)))
		#print("fillna df "+str(df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0)))
		return [df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit), df.xs('open', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=1).to_numpy()[0], df.xs('high', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit), df.xs('low', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit), df.xs('volume', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)]


	def get_closes_open_his_los(self, config, assets, periodB, limit, curr_date):
		#df = self.get_prices(config, assets, periodB, limit, curr_date.isoformat()).xs('close', axis=1, level=1)
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		return [df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit), df.xs('open', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=1).to_numpy()[0], df.xs('high', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit), df.xs('low', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit)]


	def get_closes_open(self, config, assets, periodB, limit, curr_date):
		#df = self.get_prices(config, assets, periodB, limit, curr_date.isoformat()).xs('close', axis=1, level=1)
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat())
		return [df.xs('close', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=limit), df.xs('open', axis=1, level=1).fillna(method="ffill", axis=0).tail(n=1).to_numpy()[0]]
		

	def get_close_price_df(self, config, assets, periodB, limit, curr_date):
		#df = self.get_prices(config, assets, periodB, limit, curr_date.isoformat()).xs('close', axis=1, level=1)
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat()).xs('close', axis=1, level=1)
		return df.fillna(method="ffill", axis=0).tail(n=limit)#Push non NaN val to last row then return just last row. Note, synonym for 'ffill' is 'pad'
		#Geek for Geeks has excellent explanation for ffill and bfill


	def get_open_price_df(self, config, assets, periodB, limit, curr_date):
		#df = self.get_prices(config, assets, periodB, limit, curr_date.isoformat()).xs('close', axis=1, level=1)
		df = self.get_df(config, assets, periodB, limit, curr_date.isoformat()).xs('open', axis=1, level=1)
		return df.fillna(method="ffill", axis=0).tail(n=limit)#Push non NaN val to last row then return just last row. Note, synonym for 'ffill' is 'pad'
		#Geek for Geeks has excellent explanation for ffill and bfill


	def get_close_price(self, config, assets, periodA, periodB, curr_date):
		close = self.get_prices(config, assets, periodB, 1, curr_date.isoformat()).iloc[[-1]].xs('close', axis=1, level=1).to_numpy()[0]
		self.fill_price_gaps(config, close, assets, curr_date, periodA, periodB)#Fill the NAN holes with most recent available price
		return close


	def get_open_price(self, config, assets, periodA, periodB, curr_date):
		open_p = self.get_prices(config, assets, periodB, 1, curr_date.isoformat()).iloc[[-1]].xs('open', axis=1, level=1).to_numpy()[0]
		self.fill_price_gaps(config, open_p, assets, curr_date, periodA, periodB)#Fill the NAN holes with most recent available price
		return open_p


	def get_high_price(self, config, assets, periodA, periodB, curr_date):
		high = self.get_prices(config, assets, periodB, 1, curr_date.isoformat()).iloc[[-1]].xs('high', axis=1, level=1).to_numpy()[0]	
		self.fill_price_gaps(config, high, assets, curr_date, periodA, periodB)#Fill the NAN holes with most recent available price
		return high 


	def get_low_price(self, config, assets, periodA, periodB, curr_date):
		low = self.get_prices(config, assets, periodB, 1, curr_date.isoformat()).iloc[[-1]].xs('low', axis=1, level=1).to_numpy()[0]
		self.fill_price_gaps(config, low, assets, curr_date, periodA, periodB)#Fill the NAN holes with most recent available price
		return low


	def get_volume(self, config, assets, periodA, periodB, curr_date):
		volume = self.get_prices(config, assets, periodB, 1, curr_date.isoformat()).iloc[[-1]].xs('volume', axis=1, level=1).to_numpy()[0]
		self.fill_price_gaps(config, volume, assets, curr_date, periodA, periodB)#Fill the NAN holes with most recent available price
		return volume


	def get_prices(self, config, assets, bar_period, num_bars, last_bar_date):
		df = self.get_df(config, assets, bar_period, num_bars, last_bar_date)
		return df.drop(labels=['open', 'low', 'high', 'volume'], axis = 1, level = 1)#axis 1 for col level 1 for 2nd tier level col		


	"""def get_past_date(self, curr_date, periodA):
		global MOVING_PRICE_GRADIENT_PERIOD
		new_date = curr_date
		i = MOVING_PRICE_GRADIENT_PERIOD
		while i > 0:
			new_date -= pd.Timedelta(periodA)
			i -= 1
		print("past "+str(new_date))
		return new_date


	def get_past_close(self, config, assets, bar_periodB, num_bars, date, bar_periodA):
		past = self.get_df(config, assets, bar_periodB, num_bars, date.isoformat()).drop(labels=['open', 'low', 'high', 'volume'], axis = 1, level = 1).to_numpy()[0]
		fill_price_gaps(past, assets, date, bar_periodA, bar_periodB)#Fill the NAN holes with most recent available price
		return past


	def fill_price_gaps(self, config, df_close, assets, curr_date, periodA, periodB):
		def get_next_non_nan_price(i, date):
			return self.get_prices(config, assets, periodB, 1, date.isoformat()).to_numpy()[0][i]#Price of asset i on date
		#Only run if at least one col is NAN for performance reasons.
		run = False
		for i in range(0, len(assets)):
			if math.isnan(df_close[i]):
				run = True
				break	
		if run:
			for i in range(0, len(assets)):
				while math.isnan(get_next_non_nan_price(i, curr_date)):
					curr_date -= pd.Timedelta(periodA)#Keep moving the date backwards as long as price in NAN
				df_close[i] = get_next_non_nan_price(i, curr_date)"""





	#USERS MUST PASS NUMPY ARRAYS FOR EVERY FACTOR USED 
	#Make the essential params, class vars(strategy to periodB)  Everything else can be args*
	def run(self, strategy, assets, start_date, end_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, **kwargs):	


		print("in Backtrader")
		print(assets)
		


		#Continuous data collection from test day - last n days till test day
		last_n_dates = self.get_last_n_dates(kwargs['config'], assets, day_periodB, strategy.num_training_days, start_date)#last_n_dates[-1] would be midnight of previous day, or of Friday if test day is Monday
		#initial_start_date = last_n_dates.index[-1].tz_convert(tz=kwargs['MY_TZ']) + pd.Timedelta('570minutes') + pd.Timedelta('570minutes') + pd.Timedelta('570minutes') + pd.Timedelta('300minutes')#06:30AM
		#print("Last n dates [-1] "+str(last_n_dates.index[-1].tz_convert(tz=kwargs['MY_TZ'])))
		##initial_start_date = last_n_dates.index[-1].tz_convert(tz=kwargs['MY_TZ']) + pd.Timedelta('570minutes') + pd.Timedelta('570minutes') + pd.Timedelta('570minutes')#01:30AM
		initial_start_date = last_n_dates.index[-1].tz_convert(tz=kwargs['MY_TZ']) + pd.Timedelta('570minutes') #06:30AM prev day
		#print("Initial start date [-1] "+str(initial_start_date))
		last_weekday = last_n_dates.index[-1].weekday()
		if last_weekday == 4:#Friday
			initial_start_date += pd.Timedelta('2880minutes')#Add 48 hours so as to skip over Saturday and Sunday


		curr_date = initial_start_date

		while(curr_date <= end_date):

			"""if (curr_date.weekday() != 5 and curr_date.weekday() != 6):#Not Sat or Sun
				if curr_date.weekday() == 0 and curr_date.hour == 0:
					curr_date += pd.Timedelta('90minutes')#Add 90 mins to Monday at midnight so init date is 01:30AM
				print("Curr date: "+str(curr_date))"""
			strategy.execute(self, assets, initial_start_date, curr_date, end_date, start_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, kwargs)
			#Updates
			curr_date += pd.Timedelta(_1min_periodA)#Increment time	


