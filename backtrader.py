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


	def position_exists(self, asset):
		#global POSITIONS
		for dict in self.positions:
			#print("Looking at "+str(asset))
			if dict['asset'] == asset:
				#print("dict asset "+str(dict['asset'])+" = asset "+str(asset))
				#print("true")
				return True
		#print("false")
		return False


	def get_pos_for_asset(self, asset, trade_id, POSITIONS):
		for dict in POSITIONS:
			if dict['asset'] == asset and dict['trade id'] == trade_id:
				return dict
		return {}		


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


	def get_past_date(self, curr_date, periodA):
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
				df_close[i] = get_next_non_nan_price(i, curr_date)



	###STILL NEED TO WORK ON POSITIONS THAT ARE SHORTED AFTER A BUY OR VICE VERSA
	#def sell(self, date, shares, pos, close, POSITIONS, PORTFOLIO_VAL, SPREAD):
	def sell(self, date, shares, pos, close, SPREAD):
		#print("sell")
		#print("pos "+str(pos))
		#global POSITIONS
		realized = [0, 0, 0, 0, 0]
		shares_unsold = pos.get('shares') - shares#Shares that will be left unsold after this sell
		price = close - SPREAD
		#Compute profil/loss
		selling_price = shares*price#Price now
		cost_price = shares * pos.get('price per share')#Price in the past(current position)
		profit = selling_price - cost_price
		profit_per_share = price - pos.get('price per share')
		print("selling price "+str(selling_price)+" cost price "+str(cost_price)+" profit "+str(profit))
		#self.portfolio_val += profit
		#Update pos
		pos['shares'] = shares_unsold#Update num shares left
		pos['profit'] += profit
		pos['profit per share'] += profit_per_share
		#pos['price per share'] = price#Revise price to be the current sell price
		print(str(date)+": Sold "+str(shares)+ " shares for $" +str(price)+ "apiece for a profit of $"+str(profit))
		#pos['price'] = price#Revise price to be the current sell price
		#pos['peak price'] = pos.get('price')
		#pos['position value'] = shares_unsold*price
		#print("new pos "+str(pos))
		#Eliminate position if no shares left
		realized = [profit, profit_per_share, pos.get('profit'), pos.get('profit per share'), shares_unsold]
		self.portfolio_val += profit#MOVE THIS TO STRATEGY... OR PERHAPS NOT
		#self.cummulative_profit_per_share += pos.get('profit per share')		
		if shares_unsold == 0:
			#realized = (pos.get('profit'), pos.get('profit per share'))
			#self.portfolio_val += pos.get('profit')#MOVE THIS TO STRATEGY... OR PERHAPS NOT
			#self.cummulative_profit_per_share += pos.get('profit per share')
			print("No shares left")
			#print("PORTFOLIO_VAL now $"+str(PORTFOLIO_VAL))	
			self.winnerslosers.append({'asset':pos.get('asset'), 'profit':pos.get('profit')})		
			self.positions.remove(pos)
		else:
			#realized = (0, 0)
			print(str(shares_unsold)+" still left")
			#pos['side'] = 'none'
		return realized
	#!!!!ALSO REMOVE CORRESPONDING POSITIONS MANAGER IN STRATEGY CLASS. UPDATE PEAK PRICE TOO	


	#def cover(self, date, shares, pos, close, POSITIONS, PORTFOLIO_VAL, SPREAD):
	def cover(self, date, shares, pos, close, SPREAD):
		#print("pos "+str(pos))
		#global POSITIONS
		#print("date "+str(date)+" shares "+str(shares)+" price "+str(close)+" pos "+str(pos)+" spread "+str(SPREAD))
		#print("pos "+str(pos)+" Get shares "+str(pos.get('shares'))+" shares "+str(shares))
		realized = [0, 0, 0, 0, 0]
		shares_uncovered = pos.get('shares') - shares#Shares that will be left uncovered after this cover
		price = close + SPREAD
		#Compute profil/loss
		selling_price = shares * pos.get('price per share')#Price in the past(current position)
		cost_price = shares*price#price now
		profit = selling_price - cost_price
		profit_per_share = pos.get('price per share') - price
		print("selling price "+str(selling_price)+" cost price "+str(cost_price)+" profit "+str(profit))
		#self.portfolio_val += profit
		#Update pos
		pos['shares'] = shares_uncovered#Update num shares left
		pos['profit'] += profit
		pos['profit per share'] += profit_per_share
		#pos['price per share'] = price#Revise price to be the current sell price
		print(str(date)+": Covered "+str(shares)+ " shares for $" +str(price)+ "apiece for a profit of $"+str(profit))		
		#pos['price'] = price#Revise price to be the current sell price
		#pos['peak price'] = pos.get('price')
		#pos['position value'] = shares_uncovered*price
		#print("new pos "+str(pos))	
		#Eliminate position if no shares left
		realized = [profit, profit_per_share, pos.get('profit'), pos.get('profit per share'), shares_uncovered]
		self.portfolio_val += profit#MOVE THIS TO STRATEGY
		#self.cummulative_profit_per_share += pos.get('profit per share')		
		if shares_uncovered == 0:
			#realized = (pos.get('profit'), pos.get('profit per share'))
			#self.portfolio_val += pos.get('profit')#MOVE THIS TO STRATEGY
			#self.cummulative_profit_per_share += pos.get('profit per share')
			print("No shares left")	
			self.winnerslosers.append({'asset':pos.get('asset'), 'profit':pos.get('profit')})			
			self.positions.remove(pos)
		else:
			#realized = (0, 0)
			print(str(shares_uncovered)+" still left")
			#pos['side'] = 'none'
		return realized
	#!!!!ALSO REMOVE CORRESPONDING POSITIONS MANAGER IN STRATEGY CLASS. UPDATE PEAK PRICE TOO	


	#def buy(self, close, asset, POSITION_SIZE, POSITIONS, SPREAD):
	def buy(self, close, asset, POSITION_SIZE, SPREAD, trade_id):
		#global POSITIONS
		price = close + SPREAD
		shares_bought = int(POSITION_SIZE/price)
		additional_position_value = shares_bought*price
		price_per_share = price
		pos = self.get_pos_for_asset(asset, trade_id, self.positions)
		if pos != {}:#Position exists for that asset
		#if self.position_exists(asset):
			total_position_value = (pos.get('shares')*pos.get('price per share')) + additional_position_value#Revise pos value
			#pos = self.get_pos_for_asset(asset, self.positions)
			#pos['position value'] = pos.get('position value') + additional_position_value#Revise pos value
			#pos['price'] = price#Revise price to be the current buy price
			total_shares = pos.get('shares') + shares_bought
			pos['shares'] = total_shares
			#pos['peak price'] = pos.get('price')
			#pos['peak price'] = price#Update peak price to be current buy price
			#pos['shares'] = abs(pos.get('position value')/price)#Average out shares
			pos['price per share'] = abs(total_position_value/total_shares)#Average out price
			#pos['side'] = 'none'#Eliminates trailing ability
		else:#Create a position
			#pos = {'asset':asset, 'shares':shares, 'price':price, 'position value':position_value, 'peak price':price, 'side':'buy'}
			pos = {'asset':asset, 'shares':shares_bought, 'price per share':price_per_share, 'profit':0, 'profit per share':0, 'side':'long', 'trade id':trade_id}
			self.positions.append(pos)
		print("bought "+asset)
		#print(pos)
		#print(self.positions)
		#!!!!!ATTRIBS FROM PEAK PRICE, ONWARDS SHOULD BE IN A DIFFERENT DICT(WHICH WILL BELONG TO STRATEGY CLASS AND NOT TO BT CLASS)


	#def short(self, close, asset, POSITION_SIZE, POSITIONS, SPREAD):
	def short(self, close, asset, POSITION_SIZE, SPREAD, trade_id):
		#print("spread "+str(SPREAD))
		#global POSITIONS
		price = close - SPREAD
		shares_shorted = int(POSITION_SIZE/price)
		additional_position_value = shares_shorted*price*-1
		price_per_share = price
		pos = self.get_pos_for_asset(asset, trade_id, self.positions)
		if pos != {}:#Position exists for that asset		
		#if self.position_exists(asset):
			total_position_value = (pos.get('shares')*pos.get('price per share')) + additional_position_value#Notice additional_position_value is -ve, so we are subtracting from current
			#pos['position value'] = pos.get('position value') + additional_position_value#Notice position_value is -ve, so we are subtracting from current
			#pos = self.get_pos_for_asset(asset, self.positions)
			#pos['price'] = price#Revise price to be the current short price
			total_shares = pos.get('shares') - shares_shorted
			pos['shares'] = total_shares
			#pos['peak price'] = pos.get('price')
			#pos['peak price'] = price#Update peak price to be current buy price
			#pos['shares'] = abs(pos.get('position value')/price)#Average out shares 
			pos['price per share'] = abs(total_position_value/total_shares)#Average out price
			#pos['side'] = 'none'#Eliminates trailing ability
		else:#Create a position	
			#pos = {'asset':asset, 'shares':shares, 'price':price, 'position value':position_value, 'peak price':price, 'side':'short'}	
			pos = {'asset':asset, 'shares':shares_shorted, 'price per share':price_per_share, 'profit':0, 'profit per share':0, 'side':'short', 'trade id':trade_id}	
			self.positions.append(pos)		
		print("shorted "+asset)	
		#print(pos)	
		#print(self.positions)
		#!!!!!ATTRIBS FROM PEAK PRICE, ONWARDS SHOULD BE IN A DIFFERENT DICT(WHICH WILL BELONG TO STRATEGY CLASS AND NOT TO BT CLASS)


	#USERS MUST PASS NUMPY ARRAYS FOR EVERY FACTOR USED 
	#Make the essential params, class vars(strategy to periodB)  Everything else can be args*
	def run(self, strategy, assets, start_date, end_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, **kwargs):	
		#print("today's start state "+str(start_date)+" today's end date "+str(end_date))
		###strategy.init_peak_atr(assets)

		print("in Backtrader")
		print(assets)
		#Last n days
		"""last_n_dates = self.get_last_n_dates(kwargs['config'], assets, day_periodB, strategy.num_training_days, start_date)
		#print("last_n_dates "+str(last_n_dates))
		for i in range(0, len(last_n_dates.index)):
			#strategy.reset_queues(assets, kwargs['td'])
			###strategy.reset_peak_atr(assets)
			#print(last_n_dates.index[i])
			todays_date = last_n_dates.index[i].tz_convert(tz=kwargs['MY_TZ'])
			print("todays_date "+str(todays_date))
			#start_of_day = todays_date + pd.Timedelta('570 minutes')#To go from 0:00 to 6:30
			start_of_day = todays_date + pd.Timedelta('0 minutes')#0:00
			curr_date = start_of_day
			#next_day_date = start_date#For the last training day(index len(last_n_dates.index) - 1), next day date will be start date
			#if i < len(last_n_dates.index) - 1:#iterator less than the last index
				#next_day_date = last_n_dates.index[i+1]
			end_of_day = todays_date + pd.Timedelta('960 minutes')#To go from 0:00 to 13:00
			#print("training day start date "+str(curr_date)+" trining day end date "+str(next_day_date))
			while(curr_date <= end_of_day):
				#strategy.compute_factors(self, assets, curr_date, last_n_dates.index[i], periodB, kwargs)
				#strategy.execute(self, assets, start_of_day, curr_date, end_of_day, start_date, periodA, periodB, day_periodB, kwargs)
				strategy.execute(self, assets, start_of_day, curr_date, end_date, start_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, kwargs)
				curr_date += pd.Timedelta(_1min_periodA)#Increment time
			#strategy.collect_data_from_training_day(self, assets, curr_date, day_periodB, kwargs)
			#print("peak atr "+str(strategy.peak_atr_reached))
			print("////////////////////////////////////////DAY END/////////////////////////////////////////\n\n")"""
		
	
		#Current day
		"""curr_date = start_date
		strategy.reset_queues(assets, kwargs['td'])
		###strategy.reset_peak_atr(assets)
		#print("peak atr "+str(strategy.peak_atr_reached))
		#strategy.collect_data_from_prev_days(self, assets, curr_date, day_periodB, kwargs)
		while(curr_date <= end_date):
			strategy.execute(self, assets, start_date, curr_date, end_date, start_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, kwargs)
			#Updates
			curr_date += pd.Timedelta(_1min_periodA)#Increment time"""



		#Continuous data collection from test day - last n days till test day
		last_n_dates = self.get_last_n_dates(kwargs['config'], assets, day_periodB, strategy.num_training_days, start_date)#last_n_dates[-1] would be midnight of previous day, or of Friday if test day is Monday
		#initial_start_date = last_n_dates.index[-1].tz_convert(tz=kwargs['MY_TZ']) + pd.Timedelta('570minutes') + pd.Timedelta('570minutes') + pd.Timedelta('570minutes') + pd.Timedelta('300minutes')#06:30AM
		initial_start_date = last_n_dates.index[-1].tz_convert(tz=kwargs['MY_TZ']) + pd.Timedelta('570minutes') + pd.Timedelta('570minutes') + pd.Timedelta('570minutes')#01:30AM
		last_weekday = last_n_dates.index[-1].weekday()
		if last_weekday == 4:#Friday
			initial_start_date += pd.Timedelta('2880minutes')#Add 48 hours so as to skip over Saturday and Sunday
		#print("last date: "+str(last_n_dates.index[-1]))
		#print("last weekday: "+str(last_weekday))
		#print("init start date: "+str(initial_start_date)+"\n\n\n\n\n\n\n***************")
		#initial_start_date = last_n_dates.index[-1].tz_convert(tz=kwargs['MY_TZ']) + pd.Timedelta('570minutes')#Initially, the start of the first training day ie 06:30 of day before
		curr_date = initial_start_date
		#strategy.reset_queues(assets, kwargs['td'])
		###strategy.reset_peak_atr(assets)
		#print("peak atr "+str(strategy.peak_atr_reached))
		#strategy.collect_data_from_prev_days(self, assets, curr_date, day_periodB, kwargs)
		while(curr_date <= end_date):
			#weekday = curr_date.weekday()
			#print("Day of week: "+str(weekday))
			#if not (weekday == 5 or weekday == 6):#not Saturday of Sunday
			strategy.execute(self, assets, initial_start_date, curr_date, end_date, start_date, _1min_periodA, _1min_periodB, _5min_periodA, _5min_periodB, _15min_periodA, _15min_periodB, day_periodB, kwargs)
			#Updates
			curr_date += pd.Timedelta(_1min_periodA)#Increment time	


