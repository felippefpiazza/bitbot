from mysql_handler import handler
import json

class Data(object):

	def __init__(self, xchange_id, onlypublic = False):
		self.xchange_id = xchange_id
		self.db = handler.Handler()
		self.db.connect()

	def insertAssets(self, asset_cursor):
		cursor = self.db.execute("SELECT * FROM assets  where  xchange_id = {} and deleted_at is NULL".format(self.xchange_id))
		assets = []
		for row in cursor.fetchall():
			assets.append(row['name'])
		
		for asset in asset_cursor:
			if asset not in assets:
				print("New asset ({}) = ({})".format(asset, asset_cursor[asset]["altname"]))
				self.insertAsset(asset,
					asset_cursor[asset]["altname"],
					asset_cursor[asset]["decimals"],
					asset_cursor[asset]["display_decimals"])
				

	def insertAsset(self, name,altname,decimals,disp_decimals):
		params = { "xchange_id" : {"quote" : False, "value" : str(self.xchange_id)},
					"name" : name ,
					"altname" : altname,
					"decimals" : { "quote" : False , "value" : str(decimals)},
					"disp_decimals" : { "quote" : False , "value" : str(disp_decimals)}}
		self.db.insertIntoTable("assets",params,True)


	def insertAssetPairs(self, asset_pair_cursor):
		cursor = self.db.execute("SELECT * FROM asset_pairs  where  xchange_id = {} and deleted_at is NULL".format(self.xchange_id))
		asset_pairs = []
		for row in cursor.fetchall():
			asset_pairs.append(row['name'])
		
		for asset_pair in asset_pair_cursor:
			if asset_pair not in asset_pairs:
				print("New asset pair ({}) = ({})".format(asset_pair, asset_pair_cursor[asset_pair]["altname"]))
				self.insertAssetPair(asset_pair,
					asset_pair_cursor[asset_pair]["altname"],
					asset_pair_cursor[asset_pair]["base"],
					asset_pair_cursor[asset_pair]["quote"],
					asset_pair_cursor[asset_pair]["lot_decimals"],
					asset_pair_cursor[asset_pair]["pair_decimals"])

	def insertAssetPair(self, name,altname,base_asset_name, quote_asset_name, lot_decimal, pair_decimal):
		#FINDING ASSET IDS
		cursor = self.db.execute("SELECT id,name from assets where xchange_id = {} and name in (\"{}\",\"{}\") and deleted_at is NULL".format(self.xchange_id,base_asset_name,quote_asset_name))
		base_asset_id = 0
		quote_asset_id = 0
		for row in cursor.fetchall():
			if row["name"] == base_asset_name:
				base_asset_id = row["id"]
			elif row["name"] == quote_asset_name:
				quote_asset_id = row["id"]

		if quote_asset_id != 0 and base_asset_id != 0:
			params = { "xchange_id" : {"quote" : False, "value" : str(self.xchange_id)},
					"name" : name ,
					"altname" : altname,
					"base_asset_id" : { "quote" : False , "value" : str(base_asset_id)},
					"base_asset_name" : base_asset_name,
					"quote_asset_id" : { "quote" : False , "value" : str(quote_asset_id)},
					"quote_asset_name" : quote_asset_name,
					"lot_decimal" : { "quote" : False , "value" : str(lot_decimal)},
					"pair_decimal" : { "quote" : False , "value" : str(pair_decimal)}
			}

			self.db.insertIntoTable("asset_pairs",params,True)

	def getEnabledAssetPairs(self):
		return self.db.execute("SELECT id,name from asset_pairs where xchange_id = {} and enable=1".format(self.xchange_id))


	def insertRates(self, rates_cursor, run_id):
		asset_pairs = self.getEnabledAssetPairs()
		ap = {}
		for asset_pair in asset_pairs:
			ap[asset_pair["name"]] = asset_pair["id"]

		for key in rates_cursor:
			asset_pair_id = ap[key]
			params = { "xchange_id" : {"quote" : False, "value" : str(self.xchange_id)},
				"rates_run_id" : {"quote" : False, "value" : str(run_id)},
				"measure_datetime" : {"quote" : False, "value" : "NOW()"} ,
				"asset_pair_id" : {"quote" : False , "value" : asset_pair_id} ,
				"asset_pair" : key ,
				"exchange_ask" : {"quote" : False , "value" : rates_cursor[key]["a"][0]} ,
				"exchange_ask_whole_lot_volume" : {"quote" : False , "value" : rates_cursor[key]["a"][1]} ,
				"exchange_ask_lot_volume" : {"quote" : False , "value" : rates_cursor[key]["a"][2]} ,
				"exchange_bid" : {"quote" : False , "value" : rates_cursor[key]["b"][0]} ,
				"exchange_bid_whole_lot_volume" : {"quote" : False , "value" : rates_cursor[key]["b"][1]} ,
				"exchange_bid_lot_volume" : {"quote" : False , "value" : rates_cursor[key]["b"][2]} ,
				"exchange_last_trade" : {"quote" : False , "value" : rates_cursor[key]["c"][0]} ,
				"exchange_last_trade_lot_volume" : {"quote" : False , "value" :  rates_cursor[key]["c"][1]} ,
				"volume_today" : {"quote" : False , "value" : rates_cursor[key]["v"][0]} ,
				"volume_24h" : {"quote" : False , "value" : rates_cursor[key]["v"][1]} ,
				"weighted_avg_price_today" : {"quote" : False , "value" : rates_cursor[key]["p"][0]} ,
				"weighted_avg_price_24h" : {"quote" : False , "value" : rates_cursor[key]["p"][1]} ,
				"number_of_trades_today" : {"quote" : False , "value" : rates_cursor[key]["t"][0]} ,
				"number_of_trades_24h" : {"quote" : False , "value" : rates_cursor[key]["t"][1]} ,
				"low_today" : {"quote" : False , "value" : rates_cursor[key]["l"][0]} ,
				"low_24h" : {"quote" : False , "value" : rates_cursor[key]["l"][1]} ,
				"high_today" : {"quote" : False , "value" : rates_cursor[key]["h"][0]} ,
				"high_24h" : {"quote" : False , "value" : rates_cursor[key]["h"][1]} ,
				"opening" : {"quote" : False , "value" : rates_cursor[key]["o"]} 
				}
			self.db.insertIntoTable("rates",params,True)
		





