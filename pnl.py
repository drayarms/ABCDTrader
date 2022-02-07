from csv import writer
import os.path

class PnL:
	
	def __init__(self, num_assets):

		self._5min_long_positions = []
		self._5min_short_positions = []
		self._5min_pnl_long = []
		self._5min_pnl_short = []
		self._5min_pnl = []
		self.daily_pnl = 0
		self.stock_pnl = []
		self.num_daily_transactions = 0
		self.max_num_open_positions = 0
		#self.position_size = 1000

		for i in range(0, num_assets):
			self._5min_long_positions.append([])
			self._5min_short_positions.append([])
			self._5min_pnl_long.append(0)
			self._5min_pnl_short.append(0)
			self._5min_pnl.append(0)
			self.stock_pnl.append(0)


	def update_max_num_open_positions(self, assets):
		total_num_open_positions = 0
		for i in range(0, len(assets)):#Each stock
			for j in range(0, len(self._5min_long_positions[i])):#Each long position
				if not self._5min_long_positions[i][j].get("position exited"):
					total_num_open_positions += 1
			for j in range(0, len(self._5min_short_positions[i])):#Each short position
				if not self._5min_short_positions[i][j].get("position exited"):
					total_num_open_positions += 1
		if total_num_open_positions > self.max_num_open_positions:
			self.max_num_open_positions = total_num_open_positions


	def process_pnl(self, assets, kwargs):

		"""def process_pnl1(positions, pnl_list)
			for i in range(0, len(positions)):#Each stock
				for j in range(0, len(positions[i])):#Each position

			return pnl_list"""

		for i in range(0, len(assets)):#Each stock
			for j in range(0, len(self._5min_long_positions[i])):#Each long position
				self._5min_pnl_long[i] += self._5min_long_positions[i][j].get("profit")
				#self.stock_pnl[i] += self._5min_long_positions[i][j].get("profit")
			for j in range(0, len(self._5min_short_positions[i])):#Each short position
				self._5min_pnl_short[i] += self._5min_short_positions[i][j].get("profit")
				#self.stock_pnl[i] += self._5min_short_positions[i][j].get("profit")	
			self._5min_pnl[i] = self._5min_pnl_long[i] + self._5min_pnl_short[i] 
			self.daily_pnl += self._5min_pnl[i]





	def log_pnl(self, strategy, assets, date, kwargs):
		
		#def log_transactions(the_list, long_stock_pnl, short_stock_pnl, net_stock_pnl, daily_pnl):
		def log_transactions(the_list):
			for i in range(0, len(assets)):#Each stock
				strategy.file_log1_write("\n\n"+str(assets[i])+"\n")
				for j in range(0, len(the_list[i])):#Each position
					asset = assets[i]
					side = the_list[i][j].get("side")
					num_shares = the_list[i][j].get("num shares")
					entry_price = the_list[i][j].get("entry price")
					entry_time = the_list[i][j].get("entry time")
					exit_price = the_list[i][j].get("exit price")
					exit_time = the_list[i][j].get("exit time")	
					profit = the_list[i][j].get("profit")
					pps = the_list[i][j].get("profit per share")
					if side == "long":			
						strategy.file_log1_write(str(entry_time)+" bought "+str(num_shares)+" shares @ $"+str(entry_price)+" per share\n "+str(exit_time)+" sold @ $"+str(exit_price)+" per share\n PPS "+str(pps)+"\n PNL $"+str(profit))
					if side == "short":			
						strategy.file_log1_write(str(entry_time)+" Shorted "+str(num_shares)+" shares @ $"+str(entry_price)+" per share\n "+str(exit_time)+" Covered @ $"+str(exit_price)+" per share\n PPS "+str(pps)+"\n PNL $"+str(profit))
						strategy.file_log1_write("\n")
					self.num_daily_transactions += 1

				#strategy.file_log_write(str(assets[i])+"\n")
				#strategy.file_log_write("long PNL = $"+str(long_stock_pnl[i])+" short PNL = $"+str(short_stock_pnl[i]))
				#strategy.file_log_write(" net PNL = $"+str(net_stock_pnl[i])+"\n")

		#log_transactions(self._5min_long_positions, self._5min_pnl_long, self._5min_pnl_short, self._5min_pnl, self.daily_pnl)
		#log_transactions(self._5min_short_positions, self._5min_pnl_long, self._5min_pnl_short, self._5min_pnl, self.daily_pnl)	
		log_transactions(self._5min_long_positions)
		log_transactions(self._5min_short_positions)				


		for i in range(0, len(assets)):#Each stock	
			strategy.file_log_write(str(assets[i])+"\n")
			strategy.file_log_write("long PNL = $"+str(self._5min_pnl_long[i])+" short PNL = $"+str(self._5min_pnl_short[i]))
			strategy.file_log_write(" net PNL = $"+str(self._5min_pnl[i])+"\n")

		strategy.file_log_write("\nMax num open positions = "+str(self.max_num_open_positions)+"\n")
		strategy.file_log_write("\nDaily PNL = $"+str(self.daily_pnl)+"\n###############################################################\n")



		cvs_filename1 = 'logs1.cvs'
		file1_exists = os.path.isfile(cvs_filename1)
		fields1 = ['Date']
		for i in range(0, len(kwargs['all_assets'])):
			fields1.append(kwargs['all_assets'][i])
		list_data1=[date]
		for i in range(0, len(kwargs['all_assets'])):
			list_data1.append(0)
		for i in range(0, len(kwargs['all_assets'])):
			for j in range(0, len(assets)):
				if kwargs['all_assets'][i] == assets[j]:
					list_data1[i+1] = self._5min_pnl[j]#Replace the 0. Each col in all_assets is in col + 1 in list data since col 0 is date
		with open(cvs_filename1, 'a', newline='') as f_object1:  #For the CSV file, create a file object 
			writer_object1 = writer(f_object1) # Pass the CSV  file object to the writer() function
			if not file1_exists:
				writer_object1.writerow(fields1) 
			writer_object1.writerow(list_data1)      # Result - a writer object # Pass the data in the list as an argument into the writerow() function
			f_object1.close() # Close the file object


		cvs_filename = 'logs.cvs'
		file_exists = os.path.isfile(cvs_filename)
		fields = ['Date', 'Daily PNL', 'Max Open Positions'] 
		list_data=[date, self.daily_pnl, self.max_num_open_positions]
		with open(cvs_filename, 'a', newline='') as f_object:  #For the CSV file, create a file object 
			writer_object = writer(f_object) # Pass the CSV  file object to the writer() function
			if not file_exists:
				writer_object.writerow(fields) 
			writer_object.writerow(list_data)      # Result - a writer object # Pass the data in the list as an argument into the writerow() function
			f_object.close() # Close the file object


		#strategy.file_log1_write("\n\nStock PNLs\n")
		#for i in range(0, len(assets)):
			#strategy.file_log1_write(str(assets[i])+" $"+str(self.stock_pnl[i])+"\n")

		