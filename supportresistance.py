
import numpy as np


class Supportresistance:
	
	def __init__(self, num_assets):

		self.overbought = 60
		self.oversold = 40
		self._1min_potential_support_levels = []
		self._1min_potential_resistance_levels = []
		self._1min_refined_support_levels = []
		self._1min_refined_resistance_levels = []	
		self._1min_left_flanking_candlestick_support = []
		self._1min_left_flanking_candlestick_resistance = []

		self._5min_potential_support_levels = []
		self._5min_potential_resistance_levels = []
		self._5min_refined_support_levels = []
		self._5min_refined_resistance_levels = []	
		self._5min_left_flanking_candlestick_support = []
		self._5min_left_flanking_candlestick_resistance = []
		#self._5min_uptrending_risk_reward = []
		#self._5min_downtrending_risk_reward = []

		self._1min_trend = []
		self._5min_trend = []

		self._5min_developing_candlestick = []

		self._15min_potential_support_levels = []
		self._15min_potential_resistance_levels = []
		self._15min_refined_support_levels = []
		self._15min_refined_resistance_levels = []	
		self._15min_left_flanking_candlestick_support = []
		self._15min_left_flanking_candlestick_resistance = []				

		self.max_price_differential_to_atr_ratio = 0.4#0.45#0.3#0.25#The larger this value, the wider the allowable range of candlesticks that can be grouped together at one level
		self.max_lookback_period = 3000#ie 10 candlesticks or 50 minutes or 3000 seconds
		self.one_candlesticks_time_gap = 300#ie 1 candlesticks or 5 minutes or 300 seconds
		self.two_candlesticks_time_gap = 600#ie 2 candlesticks or 10 minutes or 600 seconds
		self.three_candlesticks_time_gap = 900#ie 3 candlesticks or 15 minutes or 900 seconds



		for i in range(0, num_assets):
			self._1min_potential_support_levels.append([])
			self._1min_potential_resistance_levels.append([])
			self._1min_refined_support_levels.append([])
			self._1min_refined_resistance_levels.append([])			
			self._1min_left_flanking_candlestick_support.append({"level":np.inf, "time":np.inf})
			self._1min_left_flanking_candlestick_resistance.append({"level":-np.inf, "time":-np.inf})

			self._5min_potential_support_levels.append([])
			self._5min_potential_resistance_levels.append([])
			self._5min_refined_support_levels.append([])
			self._5min_refined_resistance_levels.append([])			
			self._5min_left_flanking_candlestick_support.append({"level":np.inf, "time":np.inf})
			self._5min_left_flanking_candlestick_resistance.append({"level":-np.inf, "time":-np.inf})
			#self._5min_uptrending_risk_reward.append([])
			#self._5min_downtrending_risk_reward.append([])

			self._15min_potential_support_levels.append([])
			self._15min_potential_resistance_levels.append([])
			self._15min_refined_support_levels.append([])
			self._15min_refined_resistance_levels.append([])			
			self._15min_left_flanking_candlestick_support.append({"level":np.inf, "time":np.inf})
			self._15min_left_flanking_candlestick_resistance.append({"level":-np.inf, "time":-np.inf})	

			self._1min_trend.append({"current trend":"none"})	
			self._5min_trend.append({"current trend":"none"})

			self._5min_developing_candlestick.append({"lo":-np.inf, "hi":np.inf})			



	def append_to_support_list(self, assets, atr, opn, close, lo, time, potential_support_levels, left_flanking_candlestick_support):
		for i in range(0, len(potential_support_levels)):
			lower_end_of_candlestick = opn[i]
			higher_end_of_candlestick = close[i]
			if close[i] < lower_end_of_candlestick:
				lower_end_of_candlestick = close[i]
				higher_end_of_candlestick = opn[i]
			#potential_support_levels[i].append({"original price level":lower_end_of_candlestick, "average price level":lower_end_of_candlestick, "original time":time, "latest time":time, "occurences":0})
			potential_support_levels[i] = self.update_support_list(potential_support_levels[i], lower_end_of_candlestick, higher_end_of_candlestick, time, atr[i], i, left_flanking_candlestick_support)
			#if i == 0:
				#print("Suport price: $"+str(lower_end_of_candlestick))
				#print("atr: $"+str(atr[i]))
		return potential_support_levels



	def update_support_list(self, stock_support_list, new_price_level, new_hi, new_time, atr, i, left_flanking_candlestick_support):
		added_to_existing_price_level = False
		for j in range(0, len(stock_support_list)):
			#if (new_time - stock_support_list[j].get("time")).seconds > 0:#Time with which we are comparing is in the past of current time
			#time_diff = (new_time - stock_support_list[j].get("original time")).seconds
			#if i == 0:
				#print("Cluster: "+str(j)+") "+str(stock_support_list[j]))
			time_diff = (new_time - stock_support_list[j].get("latest time")).seconds
			#if i == 0:
				#print("time diff "+str(time_diff))
			if time_diff > 0 and time_diff <= self.one_candlesticks_time_gap:#Time with which we are comparing is in the past of current time and isn't more than 1 time peiods past ahead of current time
				old_price_level = stock_support_list[j].get("average price level")
				#if i == 0:
					#print("old price level :"+str(old_price_level))
					#print("new price level: "+str(new_price_level))
					#print("abs old - new price level: "+str(abs(new_price_level - old_price_level)))
					#print("atr to max_price_differential_to_atr_ratio: "+str(atr*self.max_price_differential_to_atr_ratio))
				if abs(new_price_level - old_price_level) < atr*self.max_price_differential_to_atr_ratio:
					#if i == 0:
						#print("ADD TO CLUSTER")
					#Add to stock support level. Update the price level(average of old price level and current price level), time, and occurences
					average_price_level = (new_price_level+old_price_level)/2
					stock_support_list[j].update({"average price level": average_price_level})
					stock_support_list[j].update({"latest price level": new_price_level})
					stock_support_list[j].update({"latest time": new_time})
					stock_support_list[j].update({"occurences": (stock_support_list[j].get("occurences"))+1})
					if new_price_level < stock_support_list[j].get("lowest price level"):
						stock_support_list[j].update({"lowest price level": new_price_level})	
					if new_hi > stock_support_list[j].get("highest price level"):
						stock_support_list[j].update({"highest price level": new_hi})											
					added_to_existing_price_level = True
		#Becomes the right flank of most recent cluster before new cluster is created from current price level if at all
		if len(stock_support_list) > 0:#Not first candlestick of the day
			stock_support_list[-1].update({"right flank level":new_price_level})
			stock_support_list[-1].update({"right flank hi":new_hi})
			stock_support_list[-1].update({"right flank time":new_time})
		if not added_to_existing_price_level:#Need to create a new price level since wasn't added to any existing price level
			#Mark the last cluster as processed before creating a new cluster. 
			if len(stock_support_list) > 0:#There should be at least 1 cluster already present
				stock_support_list[-1].update({"cluster ready to process":True})
			#Create a new price level
			#New cluster needs a left flank. Use last assigned left flank(which is either last candlestick for non start of day or inf for start of day) as left flank for new price level
			stock_support_list.append({
				"original price level":new_price_level, 
				"average price level":new_price_level, 
				"latest price level":new_price_level,
				"lowest price level":new_price_level,
				"highest price level":new_hi,
				"left flank hi":new_hi,
				"original time":new_time, 
				"latest time":new_time, 
				"occurences":1, 
				"left flank level":left_flanking_candlestick_support[i].get("level"), 
				"left flank time":left_flanking_candlestick_support[i].get("time"),
				"right flank level":np.inf,
				"right flank time":np.inf,
				"cluster ready to process":False,
				"cluster processed":False})
		
			
		#Current candlestick becomes new left flank which will be applied to next cluster if any
		left_flanking_candlestick_support[i].update({"level":new_price_level})
		left_flanking_candlestick_support[i].update({"left flank hi":new_hi})
		left_flanking_candlestick_support[i].update({"time":new_time})
	#def update_support_list(self, assets, atr, opn, close, lo, time, periodA):
		#pass
		return stock_support_list




	def append_to_resistance_list(self, assets, atr, opn, close, hi, time, potential_resistance_levels, left_flanking_candlestick_resistance):
		for i in range(0, len(potential_resistance_levels)):
			higher_end_of_candlestick = opn[i]
			lower_end_of_candlestick = close[i]
			if close[i] > higher_end_of_candlestick:
				higher_end_of_candlestick = close[i]
				lower_end_of_candlestick = opn[i]
			#potential_resistance_levels[i].append({"original price level":higher_end_of_candlestick, "average price level":higher_end_of_candlestick, "original time":time, "latest time":time, "occurences":0})
			potential_resistance_levels[i] = self.update_resistance_list(potential_resistance_levels[i], higher_end_of_candlestick, lower_end_of_candlestick, time, atr[i], i, left_flanking_candlestick_resistance)
		return potential_resistance_levels



	def update_resistance_list(self, stock_resistance_list, new_price_level, new_lo, new_time, atr, i, left_flanking_candlestick_resistance):
		added_to_existing_price_level = False
		for j in range(0, len(stock_resistance_list)):
			#if (new_time - stock_resistance_list[j].get("time")).seconds > 0:#Time with which we are comparing is in the past of current time
			#time_diff = (new_time - stock_resistance_list[j].get("original time")).seconds
			#if i == 0:
				#print("Cluster: "+str(j)+") "+str(stock_resistance_list[j]))		
			time_diff = (new_time - stock_resistance_list[j].get("latest time")).seconds
			#if i == 0:
				#print("time diff "+str(time_diff))			
			if time_diff > 0 and time_diff <= self.one_candlesticks_time_gap:#Time with which we are comparing is in the past of current time and isn't more than 1 time peiods past ahead of current time
				old_price_level = stock_resistance_list[j].get("average price level")
				#if i == 0:
					#print("old price level :"+str(old_price_level))
					#print("new price level: "+str(new_price_level))
					#print("abs old - new price level: "+str(abs(new_price_level - old_price_level)))
					#print("atr to max_price_differential_to_atr_ratio: "+str(atr*self.max_price_differential_to_atr_ratio))				
				if abs(new_price_level - old_price_level) < atr*self.max_price_differential_to_atr_ratio:
					#if i == 0:
						#print("ADD TO CLUSTER")					
					#Add to stock resistance level. Update the price level(average of old price level and current price level), time, and occurences
					average_price_level = (new_price_level+old_price_level)/2
					stock_resistance_list[j].update({"average price level": average_price_level})
					stock_resistance_list[j].update({"latest price level": new_price_level})
					stock_resistance_list[j].update({"latest time": new_time})
					stock_resistance_list[j].update({"occurences": (stock_resistance_list[j].get("occurences"))+1})
					if new_price_level > stock_resistance_list[j].get("highest price level"):
						stock_resistance_list[j].update({"highest price level": new_price_level})
					if new_lo < stock_resistance_list[j].get("lowest price level"):
						stock_resistance_list[j].update({"lowest price level": new_lo})						
					added_to_existing_price_level = True
		#Becomes the right flank of most recent cluster before new cluster is created from current price level if at all
		if len(stock_resistance_list) > 0:#Not first candlestick of the day
			stock_resistance_list[-1].update({"right flank level":new_price_level})
			stock_resistance_list[-1].update({"right flank lo":new_lo})
			stock_resistance_list[-1].update({"right flank time":new_time})
		if not added_to_existing_price_level:#Need to create a new price level since wasn't added to any existing price level
			#Mark the last cluster as processed before creating a new cluster. 
			if len(stock_resistance_list) > 0:#There should be at least 1 cluster already present
				stock_resistance_list[-1].update({"cluster ready to process":True})			
			#Create a new price level
			#New cluster needs a left flank. Use last assigned left flank(which is either last candlestick for non start of day or inf for start of day) as left flank for new price level
			stock_resistance_list.append({
				"original price level":new_price_level, 
				"average price level":new_price_level, 
				"latest price level":new_price_level,
				"highest price level":new_price_level,
				"lowest price level":new_lo,
				"left flank lo":new_lo,
				"original time":new_time, 
				"latest time":new_time, 
				"occurences":1, 				
				"left flank level":left_flanking_candlestick_resistance[i].get("level"), 
				"left flank time":left_flanking_candlestick_resistance[i].get("time"),
				"right flank level":-np.inf,
				"right flank time":-np.inf,
				"cluster ready to process":False,
				"cluster processed":False})
		
		#Current candlestick becomes new left flank which will be applied to next cluster if any
		left_flanking_candlestick_resistance[i].update({"level":new_price_level})
		left_flanking_candlestick_resistance[i].update({"left flank lo":new_lo})
		left_flanking_candlestick_resistance[i].update({"time":new_time})
	#def update_resistance_list(self, assets, atr, opn, close, hi, time, periodA):
		#pass
		return stock_resistance_list	




	def refine_potential_support_levels(self, potential_support_levels, refined_support_levels, short_atr, start_of_day):
		#print("len supports "+str(len(potential_support_levels)))
		for i in range(0, len(potential_support_levels)):#Each stock
			#print("i = "+str(i))
			#print("len supports in stock "+str(len(potential_support_levels[i])))		
			#refined_support_levels_for_stock = []
			for j in range(0, len(potential_support_levels[i])):#Each cluster
				if potential_support_levels[i][j].get("cluster ready to process") and not potential_support_levels[i][j].get("cluster processed"):
					#if i == 0:# and j == 26:
						#print("Cluster: "+str(self.potential_support_levels[i][j]))
					cluster_qualifies = False
					left_outer = potential_support_levels[i][j].get("left flank level")
					right_outer = potential_support_levels[i][j].get("right flank level")
					left_outer_hi = potential_support_levels[i][j].get("left flank hi")
					right_outer_hi = potential_support_levels[i][j].get("right flank hi")					
					left_inner = potential_support_levels[i][j].get("original price level")
					right_inner = potential_support_levels[i][j].get("latest price level")
					lowest_price = potential_support_levels[i][j].get("lowest price level")#lowest in cluster
					highest_price = potential_support_levels[i][j].get("highest price level")#highest in cluster
					occurences = potential_support_levels[i][j].get("occurences")
					original_time = potential_support_levels[i][j].get("original time")	

					if occurences >= 2:
						#Outer flanks suffice for all cases
						if right_outer > lowest_price and left_outer > lowest_price:
							cluster_qualifies = True
					else:#1 occurrence
						if (right_outer - lowest_price) > 2*short_atr[i] and original_time == start_of_day:
							cluster_qualifies = True
						if ((right_outer - lowest_price) > self.max_price_differential_to_atr_ratio*short_atr[i]) and ((left_outer - lowest_price) > self.max_price_differential_to_atr_ratio*short_atr[i]):
							cluster_qualifies = True							

					if (right_outer_hi - highest_price) > 0 and (right_outer_hi - highest_price) > self.max_price_differential_to_atr_ratio*short_atr[i] and (left_outer_hi - highest_price) > 0 and (left_outer_hi - highest_price) > self.max_price_differential_to_atr_ratio*short_atr[i]:
						cluster_qualifies = True

					if cluster_qualifies:
						refined_support_levels[i].append(potential_support_levels[i][j])

					potential_support_levels[i][j].update({"cluster processed":True})

		return refined_support_levels
			



	def refine_potential_resistance_levels(self, potential_resistance_levels, refined_resistance_levels, short_atr, start_of_day):
		#print("len resistances "+str(len(potential_resistance_levels)))
		for i in range(0, len(potential_resistance_levels)):#Each stock
			#print("i = "+str(i))
			#print("len resistances in stock "+str(len(potential_resistance_levels[i])))
			#refined_resistance_levels_for_stock = []
			for j in range(0, len(potential_resistance_levels[i])):#Each cluster
				if potential_resistance_levels[i][j].get("cluster ready to process") and not potential_resistance_levels[i][j].get("cluster processed"):
					#if i == 0:# and j == 26:
						#print("Cluster: "+str(self.potential_resistance_levels[i][j]))			
					cluster_qualifies = False
					left_outer = potential_resistance_levels[i][j].get("left flank level")
					right_outer = potential_resistance_levels[i][j].get("right flank level")
					left_outer_lo = potential_resistance_levels[i][j].get("left flank lo")
					right_outer_lo = potential_resistance_levels[i][j].get("right flank lo")					
					left_inner = potential_resistance_levels[i][j].get("original price level")
					right_inner = potential_resistance_levels[i][j].get("latest price level")
					highest_price = potential_resistance_levels[i][j].get("highest price level")#highest in cluster
					lowest_price = potential_resistance_levels[i][j].get("lowest price level")#lowest in cluster
					occurences = potential_resistance_levels[i][j].get("occurences")	
					original_time = potential_resistance_levels[i][j].get("original time")	

					if occurences >= 2:
						#Outer flanks suffice for all cases
						if right_outer < highest_price and left_outer < highest_price:
							cluster_qualifies = True
					else:#1 occurrence
						if (highest_price - right_outer) > 2*short_atr[i] and original_time == start_of_day:
							cluster_qualifies = True
						if ((highest_price - right_outer) > self.max_price_differential_to_atr_ratio*short_atr[i]) and ((highest_price - left_outer) > self.max_price_differential_to_atr_ratio*short_atr[i]):
							cluster_qualifies = True

					if (lowest_price - right_outer_lo) > 0 and (lowest_price - right_outer_lo) > self.max_price_differential_to_atr_ratio*short_atr[i] and (lowest_price - left_outer_lo) > 0 and (lowest_price - left_outer_lo) > self.max_price_differential_to_atr_ratio*short_atr[i]:
						cluster_qualifies = True

					if cluster_qualifies:
						refined_resistance_levels[i].append(potential_resistance_levels[i][j])

					potential_resistance_levels[i][j].update({"cluster processed":True})				

		return refined_resistance_levels




	def print_support_resistance_list(self, assets, i):

		def print_list(the_list, title):

			print(title+str(assets[i])+"\n*************************")
			for j in range(0, len(the_list)):
				#if the_list[j].get("occurences") > 1:
				if True:
					print("Left flank("+str(the_list[j].get('left flank time'))+", $"+str(the_list[j].get('left flank level'))+")")
					print("Time Range: "+str(the_list[j].get('original time'))+" - "+str(the_list[j].get('latest time'))+" Ave Price Level: "+str(the_list[j].get('average price level'))+" Occurences: "+str(the_list[j].get('occurences')))
					if "lowest price level" in the_list[j]:
						print("Lowest price in cluster: "+str(the_list[j].get("lowest price level"))) 
					if "highest price level" in the_list[j]:
						print("Highest price in cluster: "+str(the_list[j].get("highest price level"))) 						
					print("Right flank("+str(the_list[j].get('right flank time'))+", $"+str(the_list[j].get('right flank level'))+")")
					print("-------------------------------")
			print("\n\n")

		#print_list(self._1min_refined_support_levels[i], "1min Support Levels for ")
		#print_list(self._1min_refined_resistance_levels[i], "1 min Resistance Levels for ")
		print_list(self._5min_refined_support_levels[i], "5min Support Levels for ")
		print_list(self._5min_refined_resistance_levels[i], "5 min Resistance Levels for ")
		#print_list(self._15min_refined_support_levels[i], "15min Support Levels for ")
		#print_list(self._15min_refined_resistance_levels[i], "15 min Resistance Levels for ")		



	def appropriate_time(self, time, risk_level):
		return time.timestamp() < (risk_level.get("latest time")).timestamp() + 700
		

	def price_between_last_risk_reward_pair(self, close, risk_reward):
		if len(risk_reward) > 0:
			lower_level = risk_reward[-1].get("risk level")
			upper_level = risk_reward[-1].get("reward level")			
			if risk_reward[-1].get("risk level") > risk_reward[-1].get("reward level"):
				upper_level = risk_reward[-1].get("risk level")	
				lower_level = risk_reward[-1].get("reward level")
			return close < upper_level and close > lower_level
		else:
			return False#False by defualt if list is not yet populated



	def get_downtrending_reward(self, support_list, resistance_list, price):
		#Retrun price - last support if any
		reward = 0
		reward_level = 0

		if len(support_list) >= 1:
			#reward_level = support_list[-1].get("average price level")
			reward_level = support_list[-1].get("lowest price level")
			reward = price - reward_level

		return reward, reward_level



	def get_uptrending_reward(self, support_list, resistance_list, price):
		#Retrun last resistance if any - price
		reward = 0
		reward_level = 0

		if len(resistance_list) >= 1:
			#reward_level = resistance_list[-1].get("average price level")
			reward_level = resistance_list[-1].get("highest price level")
			reward = reward_level - price

		return reward, reward_level	



	def get_risk_reward_stop_up(self, i, risk_reward_stop, support_list, resistance_list, market_price):
		risk_level = support_list[i][-1].get("lowest price level")
		stop_level = support_list[i][-1].get("lowest price level")
		risk = market_price[i] - risk_level#abs(hi - support_list[i][-2].get("lowest price level"))	
		reward, reward_level = self.get_uptrending_reward(support_list[i], resistance_list[i], market_price[i])	
		risk_reward_stop[i].update({"risk":risk})
		risk_reward_stop[i].update({"reward":reward})	
		risk_reward_stop[i].update({"risk level":risk_level})
		risk_reward_stop[i].update({"reward level":reward_level})							
		risk_reward_stop[i].update({"stop level":stop_level})	

		return risk_reward_stop	



	def get_risk_reward_stop_down(self, i, risk_reward_stop, support_list, resistance_list, market_price):
		risk_level = resistance_list[i][-1].get("highest price level")
		stop_level = resistance_list[i][-1].get("highest price level")
		risk = risk_level - market_price[i]#lo)
		reward, reward_level = self.get_downtrending_reward(support_list[i], resistance_list[i], market_price[i])	
		risk_reward_stop[i].update({"risk":risk})
		risk_reward_stop[i].update({"reward":reward})
		risk_reward_stop[i].update({"risk level":risk_level})
		risk_reward_stop[i].update({"reward level":reward_level})
		risk_reward_stop[i].update({"stop level":stop_level})

		return risk_reward_stop



	#def access_downtrending(self, assets, n, support_list, resistance_list, opn, close, atr, rsi, time, start_of_day, time_frame, trend, kwargs):
	def access_downtrending(self, assets, n, support_list, resistance_list, market_price, atr, rsi, time, start_of_day, time_frame, trend, kwargs):
		#risk_reward_stop = [{"risk":0, "reward":0, "risk level":0, "reward level":0, "stop level":0}] * len(assets)
		risk_reward_stop = []
		downtrending = [] 
		for i in range(0, len(assets)):
			risk_reward_stop.append({"risk":0, "reward":0, "risk level":0, "reward level":0, "stop level":0})
			downtrending.append(False)
		#downtrending = [False] * len(assets)
		negative_n = n * -1
		negative_n_minus1 = (n-1) * -1
		effective_downward_strenth = 0
		effective_upward_strenth = 0		
		average_downward_strenth = 0
		average_upward_strenth = 0
		downward_to_upward_strength_ratio = 0

		for i in range(0, len(assets)):#Each stock
			"""#print("downtrending i "+str(i))
			hi = opn[i]
			if market_price[i] > hi:
				hi = market_price[i]	

			lo = opn[i]
			if market_price[i] < lo:
				lo = market_price[i]"""				

			
			if len(support_list[i]) >= 1 and len(resistance_list[i]) >= 1 and time >= start_of_day:

				#if len(support_list[i]) >= n and len(resistance_list[i]) >= 1:#Need at least n support levels to determine if we have a downtrend of n cycles
				if (support_list[i][-1].get('latest time')).timestamp() > (resistance_list[i][-1].get('latest time')).timestamp(): #Most recent support is more recent than most recent resistance (ie most recent sup/res level is a support level)
					pass
				else:#Most recent resistance is more recent than most recent support (ie most recent sup/res level is a resistance level)

					if len(resistance_list[i]) >= n and len(support_list[i]) >= n-1:#Need at least n resistance levels to determine if we have a downtrend of n cycles
						last_n_resistances = resistance_list[i][negative_n:]
						last_n_resistances_declining = True

						last_n_supports = support_list[i][negative_n:]
						last_n_supports_declining = True
						last_n_minus1_supports = support_list[i][negative_n_minus1:]
						last_n_minus1_supports_declining = True						

						for j in range(0, len(last_n_resistances) - 1):
							if last_n_resistances[j].get("highest price level") < last_n_resistances[j+1].get("highest price level"):#Not declining, so false
								last_n_resistances_declining = False
								break

						if len(support_list[i]) >= n:
							for j in range(0, len(last_n_supports) - 1):
								if last_n_supports[j].get("lowest price level") < last_n_supports[j+1].get("lowest price level"):#Not declining, so false
									last_n_supports_declining = False
									break								
						else:#Not enough support levels, so false
							last_n_supports_declining = False

						if len(support_list[i]) >= n-1:
							for j in range(0, len(last_n_minus1_supports) - 1):
								if last_n_minus1_supports[j].get("lowest price level") < last_n_minus1_supports[j+1].get("lowest price level"):#Not declining, so false
									last_n_minus1_supports_declining = False
									break								
						else:#Not enough support levels, so false
							last_n_minus1_supports_declining = False


						#if last_n_resistances_declining and last_n_minus1_supports_declining and market_price[i] < resistance_list[i][-1].get("highest price level") and market_price[i] > support_list[i][-1].get("lowest price level") and support_list[i][-1].get("lowest price level") < resistance_list[i][-1].get("highest price level") and support_list[i][-1].get("lowest price level") < resistance_list[i][-2].get("highest price level"):#last n resistances declining and last n-1 supports declining and close < last reistance and close > last support and last support < last resistance and last support < last n-1 resistance	
						"""if last_n_resistances_declining and (
								(trend[i].get("current trend") == "up" and last_n_supports_declining) or (not trend[i].get("current trend") == "up" and last_n_minus1_supports_declining)#or use not none, none?
						) and (market_price[i] < resistance_list[i][-1].get("highest price level") and market_price[i] > support_list[i][-1].get("lowest price level") and support_list[i][-1].get("lowest price level") < resistance_list[i][-1].get("highest price level") and support_list[i][-1].get("lowest price level") < resistance_list[i][-2].get("highest price level")):
						"""
						if last_n_resistances_declining and (
								(trend[i].get("current trend") == "up" and last_n_minus1_supports_declining) or (not trend[i].get("current trend") == "up" and last_n_minus1_supports_declining)#or use not none, none?
						) and (market_price[i] < resistance_list[i][-1].get("highest price level") and market_price[i] > support_list[i][-1].get("lowest price level") and support_list[i][-1].get("lowest price level") < resistance_list[i][-1].get("highest price level") and support_list[i][-1].get("lowest price level") < resistance_list[i][-2].get("highest price level")):
							downtrending[i] = True#Stock is downtrending						
							risk_reward_stop = self.get_risk_reward_stop_down(i, risk_reward_stop, support_list, resistance_list, market_price)

		return downtrending, risk_reward_stop#, downward_to_upward_strength_ratio




	#def access_uptrending(self, assets, n, support_list, resistance_list, opn, close, atr, rsi, time, start_of_day, time_frame, trend, kwargs):
	def access_uptrending(self, assets, n, support_list, resistance_list, market_price, atr, rsi, time, start_of_day, time_frame, trend, kwargs):
		#risk_reward_stop = [{"risk":0, "reward":0, "risk level":0, "reward level":0, "stop level":0}] * len(assets)
		risk_reward_stop = []
		uptrending = [] 
		for i in range(0, len(assets)):
			risk_reward_stop.append({"risk":0, "reward":0, "risk level":0, "reward level":0, "stop level":0})	
			uptrending.append(False)	
		#uptrending = [False] * len(assets)
		negative_n = n * -1
		negative_n_minus1 = (n-1) * -1
		effective_downward_strenth = 0
		effective_upward_strenth = 0			
		average_downward_strenth = 0
		average_upward_strenth = 0	
		downward_to_upward_strength_ratio = 0	
		#print("OPEN "+str(opn))
		
		for i in range(0, len(assets)):#Each stock
			"""#print("uptrending i "+str(i))
			hi = opn[i]
			if market_price[i] > hi:
				hi = market_price[i]	

			lo = opn[i]
			if market_price[i] < lo:
				lo = market_price[i]"""


			if len(support_list[i]) >= 1 and len(resistance_list[i]) >= 1 and time >= start_of_day:

				#if len(resistance_list[i]) >= n and len(support_list[i]) >= 1:#Need at least n resistance levels to determine if we have an upward of n cycles
				if (resistance_list[i][-1].get('latest time')).timestamp() > (support_list[i][-1].get('latest time')).timestamp(): #Most recent resistance is more recent than most recent support (ie most recent sup/res level is a resistance level)
					pass
				else:#Most recent support is more recent than most recent resistance (ie most recent sup/res level is a support level)

					if len(support_list[i]) >= n and len(resistance_list[i]) >= n-1:#Need at least n support levels to determine if we have an upward of n cycles
						last_n_supports = support_list[i][negative_n:]
						last_n_supports_ascending = True

						last_n_resistances = resistance_list[i][negative_n:]
						last_n_resistances_ascending = True
						last_n_minus1_resistances = resistance_list[i][negative_n_minus1:]
						last_n_minus1_resistances_ascending = True						

						for j in range(0, len(last_n_supports) - 1):
							if last_n_supports[j].get("lowest price level") > last_n_supports[j+1].get("lowest price level"):#Not ascending, so false
								last_n_supports_ascending = False
								break

						if len(resistance_list[i]) >= n:
							for j in range(0, len(last_n_resistances) - 1):
								if last_n_resistances[j].get("highest price level") > last_n_resistances[j+1].get("highest price level"):#Not ascending, so false
									last_n_resistances_ascending = False
									break
						else:#Not enough resistance levels, so false
							last_n_resistances_ascending = False

						if len(resistance_list[i]) >= n-1:
							for j in range(0, len(last_n_minus1_resistances) - 1):
								if last_n_minus1_resistances[j].get("highest price level") > last_n_minus1_resistances[j+1].get("highest price level"):#Not ascending, so false
									last_n_minus1_resistances_ascending = False
									break
						else:#Not enough resistance levels, so false
							last_n_minus1_resistances_ascending = False
						

						#if last_n_supports_ascending and last_n_minus1_resistances_ascending and market_price[i] < resistance_list[i][-1].get("highest price level") and market_price[i] > support_list[i][-1].get("lowest price level") and support_list[i][-1].get("lowest price level") < resistance_list[i][-1].get("highest price level") and support_list[i][-2].get("lowest price level") < resistance_list[i][-1].get("highest price level"):#last n supports ascending and last n-1 resistances ascending and close < last resistamce and close > last support and last support < last resistance and last n-1 support < last resitance
						"""if last_n_supports_ascending and(
								((trend[i].get("current trend") == "down" and last_n_resistances_ascending) or (not trend[i].get("current trend") == "down" and last_n_minus1_resistances_ascending))#or use not none, none
							) and (market_price[i] < resistance_list[i][-1].get("highest price level") and market_price[i] > support_list[i][-1].get("lowest price level") and support_list[i][-1].get("lowest price level") < resistance_list[i][-1].get("highest price level") and support_list[i][-2].get("lowest price level") < resistance_list[i][-1].get("highest price level")):
						"""
						if last_n_supports_ascending and(
								((trend[i].get("current trend") == "down" and last_n_minus1_resistances_ascending) or (not trend[i].get("current trend") == "down" and last_n_minus1_resistances_ascending))#or use not none, none
							) and (market_price[i] < resistance_list[i][-1].get("highest price level") and market_price[i] > support_list[i][-1].get("lowest price level") and support_list[i][-1].get("lowest price level") < resistance_list[i][-1].get("highest price level") and support_list[i][-2].get("lowest price level") < resistance_list[i][-1].get("highest price level")):

							uptrending[i] = True#Stock is uptrending
							risk_reward_stop = self.get_risk_reward_stop_up(i, risk_reward_stop, support_list, resistance_list, market_price)

		return uptrending, risk_reward_stop#, downward_to_upward_strength_ratio




	def print_trends(self,
		 _5min_is_uptrending_over2cycles, _5min_is_downtrending_over2cycles, 
		 _5min_risk_reward_uptrending_over2cycles, _5min_risk_reward_downtrending_over2cycles
		):
		#print("5 min down "+str(_5min_downtrending_over2cycles))
		if _5min_is_uptrending_over2cycles:
			print("5 min uptrending over 2 cycles")	
			print("Risk: " + str(_5min_risk_reward_uptrending_over2cycles.get("risk")) + "  Reward: " + str(_5min_risk_reward_uptrending_over2cycles.get("reward")) + "  Risk Reward Ratio: " +  str(_5min_risk_reward_uptrending_over2cycles.get("risk")/_5min_risk_reward_uptrending_over2cycles.get("reward")) + "\n")

		if _5min_is_downtrending_over2cycles:
			print("5 min downtrending over 2 cycles")
			print("Risk: " + str(_5min_risk_reward_downtrending_over2cycles.get("risk")) + "  Reward: " + str(_5min_risk_reward_downtrending_over2cycles.get("reward")) + "  Risk Reward Ratio: " +  str(_5min_risk_reward_downtrending_over2cycles.get("risk")/_5min_risk_reward_downtrending_over2cycles.get("reward")) + "\n")		




	def print_trends1(self, _1min_uptrending_over2cycles, _1min_downtrending_over2cycles, _1min_uptrending_over3cycles, _1min_downtrending_over3cycles,
		 _5min_uptrending_over2cycles, _5min_downtrending_over2cycles, _5min_uptrending_over3cycles, _5min_downtrending_over3cycles,
		 _15min_uptrending_over2cycles, _15min_downtrending_over2cycles, _15min_uptrending_over3cycles, _15min_downtrending_over3cycles,
		 _1min_risk_reward_uptrending_over2cycles, _1min_risk_reward_downtrending_over2cycles, _1min_risk_reward_uptrending_over3cycles, _1min_risk_reward_downtrending_over3cycles, 
		 _5min_risk_reward_uptrending_over2cycles, _5min_risk_reward_downtrending_over2cycles, _5min_risk_reward_uptrending_over3cycles, _5min_risk_reward_downtrending_over3cycles, 
		 _15min_risk_reward_uptrending_over2cycles, _15min_risk_reward_downtrending_over2cycles, _15min_risk_reward_uptrending_over3cycles, _15min_risk_reward_downtrending_over3cycles,
		 _1min_downward_to_upward_strength_over2cycles, _1min_downward_to_upward_strength_over3cycles, _5min_downward_to_upward_strength_over2cycles, _5min_downward_to_upward_strength_over3cycles, _15min_downward_to_upward_strength_over2cycles, _15min_downward_to_upward_strength_over3cycles
		):

		if _5min_uptrending_over2cycles:
			print("5 min uptrending over 2 cycles")	
			print("Downward to upward strength ratio: "+str(_5min_downward_to_upward_strength_over2cycles))
			print("Risk: " + str(_5min_risk_reward_uptrending_over2cycles.get("risk")) + "  Reward: " + str(_5min_risk_reward_uptrending_over2cycles.get("reward")) + "  Risk Reward Ratio: " +  str(_5min_risk_reward_uptrending_over2cycles.get("risk")/_5min_risk_reward_uptrending_over2cycles.get("reward")) + "\n")

		if _5min_downtrending_over2cycles:
			print("5 min downtrending over 2 cycles")
			print("Downward to upward strength ratio: "+str(_5min_downward_to_upward_strength_over2cycles))
			print("Risk: " + str(_5min_risk_reward_downtrending_over2cycles.get("risk")) + "  Reward: " + str(_5min_risk_reward_downtrending_over2cycles.get("reward")) + "  Risk Reward Ratio: " +  str(_5min_risk_reward_downtrending_over2cycles.get("risk")/_5min_risk_reward_downtrending_over2cycles.get("reward")) + "\n")		

		if _5min_uptrending_over3cycles:
			print("5 min uptrending over 3 cycles")	
			print("Downward to upward strength ratio: "+str(_5min_downward_to_upward_strength_over3cycles))
			print("Risk: " + str(_5min_risk_reward_uptrending_over3cycles.get("risk")) + "  Reward: " + str(_5min_risk_reward_uptrending_over3cycles.get("reward")) + "  Risk Reward Ratio: " +  str(_5min_risk_reward_uptrending_over3cycles.get("risk")/_5min_risk_reward_uptrending_over3cycles.get("reward")) + "\n")

		if _5min_downtrending_over3cycles:
			print("5 min downtrending over 3 cycles")
			print("Downward to upward strength ratio: "+str(_5min_downward_to_upward_strength_over3cycles))
			print("Risk: " + str(_5min_risk_reward_downtrending_over3cycles.get("risk")) + "  Reward: " + str(_5min_risk_reward_downtrending_over3cycles.get("reward")) + "  Risk Reward Ratio: " +  str(_5min_risk_reward_downtrending_over3cycles.get("risk")/_5min_risk_reward_downtrending_over3cycles.get("reward")) + "\n")				


