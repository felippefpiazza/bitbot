import math
from mysql_handler import handler
from decimal import *
import kraken_methods



class Exchange(object):
	def __init__(self, exchange_id, onlypublic = False):
		self.trade_fee = Decimal(0.0026)
		self.db = handler.Handler()
		self.db.connect()
		self.exchange_id = exchange_id
		self.default_depth = 10


	def lastRun(self):
		query = "SELECT id FROM rates_runs order by id desc limit 1"
		cursor = self.db.execute(query)
		row = cursor.fetchone()
		return row["id"]

	def findLocalExchanges(self, rates_run_id = None):
		self.rates_run_id = rates_run_id
		self.buildXchangesObj(self.rates_run_id)
		if (rates_run_id != None):
			self.findPossiblePairs(True)
		else:
			self.findPossiblePairs(False)

	def getDepth(self,asset_pair_id,base,quote):
		k = kraken_methods.APIMethods(1)
		query = "select name from asset_pairs where id = {}".format(asset_pair_id)
		cursor = self.db.execute(query)
		row = cursor.fetchone()
		ret = k.getDepth(row["name"],self.default_depth)
		bids = self.insertOrders(asset_pair_id,row["name"],"s",ret["result"][row["name"]]["bids"])
		asks = self.insertOrders(asset_pair_id,row["name"],"b",ret["result"][row["name"]]["asks"])
		if self.xchanges_obj[base][quote]["type"] == "s":
			self.xchanges_obj[base][quote]["first_volume"] = ret["result"][row["name"]]["bids"][0][1]
			self.xchanges_obj[base][quote]["deep_volume"] = bids[0]
			self.xchanges_obj[base][quote]["deep_exchange"] = bids[1]
		else:
			self.xchanges_obj[base][quote]["first_volume"] = ret["result"][row["name"]]["asks"][0][1]
			self.xchanges_obj[base][quote]["deep_volume"] = asks[0]
			self.xchanges_obj[base][quote]["deep_exchange"] = asks[1]
		self.insertDepthInRates(bids,asks,asset_pair_id)
		return {"bids" : bids , "asks" : asks}

	def insertDepthInRates(self,bids,asks,asset_pair_id):
		update_params = { "depth" : {"quote" : False, "value" : str(self.default_depth)} , 
				"ask_deep_volume" : {"quote" : False, "value" : str(asks[0])},
				"ask_deep_exchange" : {"quote" : False, "value" : str(asks[1])},
				"bid_deep_volume" : {"quote" : False, "value" : str(bids[0])},
				"bid_deep_exchange" : {"quote" : False, "value" : str(bids[1])}
				}

		where_params = { "asset_pair_id" : {"quote" : False, "value" : str(asset_pair_id)} , 
				"rates_run_id" : {"quote" : False, "value" : str(self.rates_run_id)}
				}
		self.db.updateRow("rates", update_params, where_params, True)


	def insertOrders(self,asset_pair_id,asset_pair_name,type,order_array):
		i=0
		total_volume_exchange = 0
		total_volume = Decimal(0)
		while i < len(order_array):
			if Decimal(total_volume_exchange) < Decimal(order_array[i][0]):
				total_volume_exchange = Decimal(order_array[i][0])

			total_volume += Decimal(order_array[i][1])
			self.insertOrder(asset_pair_id,asset_pair_name,type,order_array[i][0],order_array[i][1],order_array[i][2])
			i+=1
		return [total_volume,total_volume_exchange]

	def insertOrder(self,asset_pair_id,asset_pair_name,type,exchange,volume,timestamp):
		params = { "asset_pair_id" : {"quote" : False, "value" : str(asset_pair_id)},
					"asset_pair_name" : asset_pair_name,
					"rates_run_id" : {"quote" : False, "value" : str(self.rates_run_id)},
					"type" : type,
					"exchange" : { "quote" : False , "value" : str(exchange)},
					"volume" : { "quote" : False , "value" : str(volume)},
					"timestamp" : { "quote" : False , "value" : "FROM_UNIXTIME({})".format(timestamp)}
					}
		self.db.insertIntoTable("orders",params,True)

	def insertOportunity(self):
		params = {"rates_run_id" : self.rates_run_id,
				"exchange_id" : self.exchange_id,
				"first_asset_id" : first_asset_id,
				"first_asset_name" : first_asset_name,
				"second_asset_id" : second_asset_id,
				"second_asset_name" : second_asset_name,
				"third_asset_id" : third_asset_id,
				"third_asset_name" : third_asset_name,
				"first_asset_pair_id" : first_asset_pair_id,
				"first_asset_pair_name" : first_asset_pair_name,
				"first_exchange" : first_exchange,
				"first_volume" : first_volume,
				"first_deep_volume" : first_deep_volume,
				"first_deep_exchange" : first_deep_exchange,
				"second_asset_pair_id" : second_asset_pair_id,
				"second_asset_pair_name" : second_asset_pair_name,
				"second_exchange" : second_exchange,
				"second_volume" : second_volume,
				"second_deep_volume" : second_deep_volume,
				"second_deep_exchange" : second_deep_exchange,
				"third_asset_pair_id" : third_asset_pair_id,
				"third_asset_pair_name" : third_asset_pair_name,
				"third_exchange" : third_exchange,
				"third_volume" : third_volume,
				"third_deep_volume" : third_deep_volume,
				"third_deep_exchange" : third_deep_exchange,
				"total_exchange" : total_exchange,
				"total_deep_exchange" : total_deep_exchange
				}

	def findPossiblePairs(self,dry_run = True):
		count = 0
		for key in self.xchanges_obj:
			for second_key in self.xchanges_obj[key]:
				for third_key in self.xchanges_obj[second_key]:
					if key in self.xchanges_obj[third_key]:
						exchange = self.calculateRate(key,second_key,third_key,False)
						if  exchange > 100:# or (key =="XXBT" and second_key =="ZUSD" and third_key == "XXLM"):
							
							self.getDepth(self.xchanges_obj[key][second_key]["asset_pair_id"],key,second_key)
							self.getDepth(self.xchanges_obj[second_key][third_key]["asset_pair_id"],second_key,third_key)
							self.getDepth(self.xchanges_obj[third_key][key]["asset_pair_id"],third_key,key)
							deep_exchange = self.calculateRate(key,second_key,third_key,True)

							self.insertOportunity()

							print("FOUND {} - {} - {} ".format(key,second_key,third_key))
							print ("First quote --> {} Volume {} / {} / {}".format(exchange,self.xchanges_obj[key][second_key]["first_volume"],self.xchanges_obj[second_key][third_key]["first_volume"],self.xchanges_obj[third_key][key]["first_volume"]))
							print ("Deep quote --> {} Volume {} / {} / {}".format(deep_exchange,self.xchanges_obj[key][second_key]["deep_volume"],self.xchanges_obj[second_key][third_key]["deep_volume"],self.xchanges_obj[third_key][key]["deep_volume"]))
							count += 1
		print("Found {} possible pairs".format(count))

	def calculateRate(self,first_asset,second_asset,third_asset,deep=False,debug=False):
		main_value = Decimal(100)
		if debug:
			print(main_value)
		main_value = self.Exchange(main_value,first_asset,second_asset,deep,debug)
		if debug:
			print(main_value)
		main_value = self.Exchange(main_value,second_asset,third_asset,deep,debug)
		if debug:
			print(main_value)
		main_value = self.Exchange(main_value,third_asset,first_asset,deep,debug)
		if debug:
			print(main_value)
		return main_value

	def Exchange(self, main_value, base, quote,deep=False,debug=False):
		exchange = "exchange"
		if debug:
			print("FIRST {} / {} / {}".format(main_value,base,self.xchanges_obj[base][quote]["exchange"]))
		exchange = "exchange"
		if deep:
			exchange = "deep_exchange"
		if self.xchanges_obj[base][quote]["type"] == "s":
			main_value = main_value * self.xchanges_obj[base][quote][exchange]
		else:
			main_value = main_value / self.xchanges_obj[base][quote][exchange]
		if debug:
				print("AFTER EXCHANGE {} / {} / {}".format(main_value,base,quote))
		
		
		main_value = self.roundDecimal(main_value,self.xchanges_obj[base][quote]["lot_decimal"])

		if debug:
				print("AFTER ROUND {} / {} / {}".format(main_value,base,quote))
		main_value = self.roundDecimal(self.removeFee(main_value),self.xchanges_obj[base][quote]["lot_decimal"])
		if debug:
				print("AFTER FEES {} / {} / {}".format(main_value,base,quote))
		return main_value

	def roundDecimal(self,dec,prec):
		pot = 10**prec
		return Decimal(repr(math.trunc(dec*pot)/pot))

	def removeFee(self, value):
		return value * (Decimal('1') - self.trade_fee)

	def buildXchangesObj(self, rates_run_id = None):
		query = "select rates.id,lot_decimal,pair_decimal,measure_datetime,rates.xchange_id,asset_pair_id,exchange_ask,exchange_bid,asset_pairs.base_asset_id,asset_pairs.base_asset_name,asset_pairs.quote_asset_id,asset_pairs.quote_asset_name "
		query += "from rates "
		query += "left outer join asset_pairs on "
		query += "rates.asset_pair_id = asset_pairs.id "
		query += "where rates.xchange_id={} ".format(self.exchange_id)
		if rates_run_id is None:
			self.rates_run_id = self.lastRun()
		query += " and rates_run_id = {}".format(self.rates_run_id)
		
		cursor = self.db.execute(query)
		self.xchanges_obj = {}
		for row in cursor.fetchall():
			tmp_x = {row["quote_asset_name"] : {
								"exchange" : row["exchange_bid"],
								"type" : "s",
								"asset_pair_id" : row["asset_pair_id"],
								"base_asset_id" : ["asset_pairs.base_asset_id"],
								"base_asset_name" : ["asset_pairs.base_asset_name"],
								"quote_asset_id" : ["asset_pairs.quote_asset_id"],
								"quote_asset_name" : ["asset_pairs.quote_asset_name"],
								"lot_decimal" :  row["lot_decimal"]
								}
							}
			tmp_y = {row["base_asset_name"] : {
								"exchange" : row["exchange_ask"],
								"type" : "b",
								"asset_pair_id" : row["asset_pair_id"],
								"base_asset_id" : ["asset_pairs.quote_asset_id"],
								"base_asset_name" : ["asset_pairs.quote_asset_name"],
								"quote_asset_id" : ["asset_pairs.base_asset_id"],
								"quote_asset_name" : ["asset_pairs.base_asset_name"],
								"lot_decimal" :  row["lot_decimal"]
								}
							}
			#STRUCTERE
			# "BUYING": {
			#   "SELLING": {
			#	  "exchange" : exchange_rate,
			#	  "type" : "s", ---> BUY (DIVIDE BY VALUE) OR SELL (MULTIPLY BY VALUE)
			#	  "asset_pair_id" : 1,
			#     "lot_decimal" :  8
			#   },
			#   "SELLING": {
			#	  "exchange" : exchange_rate,
			#	  "type" : "s", ---> BUY OR SELL
			#	  "asset_pair_id" : 2,
			#     "lot_decimal" :  8
			#   }			
			# }
			if row["base_asset_name"] not in self.xchanges_obj:
				self.xchanges_obj[row["base_asset_name"]] = tmp_x
			else:
				self.xchanges_obj[row["base_asset_name"]].update(tmp_x)

			if row["quote_asset_name"] not in self.xchanges_obj:
				self.xchanges_obj[row["quote_asset_name"]] = tmp_y
			else:
				self.xchanges_obj[row["quote_asset_name"]].update(tmp_y)

		#print(self.xchanges_obj)




