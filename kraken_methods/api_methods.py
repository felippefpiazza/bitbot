from krakenex import api
import kraken_methods.data
import json

class APIMethods(object):
	
	
	def __init__(self, xchange_id, onlypublic = False):
		self.k = api.API()
		self.xchange_id = xchange_id
		self.kd = kraken_methods.Data(xchange_id)
		
		if not (onlypublic):
			self.k.load_key('config/kraken.key')

	def ParseJson(self, resp):
		jdump = json.dumps(resp)
		return json.loads(jdump)

	#PUBLIC METHODS
	def getAssets(self,asset_list = ''):
		if (asset_list == ''):
			ret = self.ParseJson(self.k.query_public('Assets'))
		else:
			ret = self.ParseJson(self.k.query_public('Assets',{'asset': asset_list}))
		self.kd.insertAssets(ret["result"])
		return ret

	def getAssetPair(self,asset_pairs = ''):
		if (asset_pairs == ''):
			ret = self.ParseJson(self.k.query_public('AssetPairs'))
		else:
			ret = self.ParseJson(self.k.query_public('AssetPairs',{'pair':asset_pairs}))
		self.kd.insertAssetPairs(ret["result"])
		return ret

	def getEnabledTickers(self, run_id):
		asset_pairs = self.kd.getEnabledAssetPairs()
		pairs = []
		for row in asset_pairs:
			pairs.append(row["name"])
		resp = self.getTickers(",".join(pairs))
		print(resp)
		self.kd.insertRates(resp["result"], run_id)

	def getTickers(self, asset_pairs):
		return self.ParseJson(self.k.query_public('Ticker', {'pair': asset_pairs}))

	def getOHLC(self,pair,interval = 1):
		return self.ParseJson(self.k.query_public('OHLC', {'pair': pair,'interval':interval}))

	def getDepth(self,pair,count = ''):
		if (count == ''):
			return self.ParseJson(self.k.query_public('Depth',{'pair':pair}))
		else:
			return self.ParseJson(self.k.query_public('Depth',{'pair':pair , 'count': count}))

	def getTrades(self,pair,since = ''):
		if (since == ''):
			return self.ParseJson(self.k.query_public('Trades',{'pair':pair}))
		else:
			return self.ParseJson(self.k.query_public('Trades',{'pair':pair , 'since': since}))

	def getSpread(self,pair,since = ''):
		if (since == ''):
			return self.ParseJson(self.k.query_public('Spread',{'pair':pair}))
		else:
			return self.ParseJson(self.k.query_public('Spread',{'pair':pair , 'since': since}))

	#PRIVATE INFORMATION METHODS 
	def getTradeBalance(self,base_asset = ''):
		if (base_asset == ''):
			return self.ParseJson(self.k.query_private('TradeBalance'))
		else:
			return self.ParseJson(self.k.query_private('TradeBalance',{'asset':base_asset}))

	def getOpenOrders(self,include_trades = False):
			return self.ParseJson(self.k.query_private('OpenOrders', {"trades":str(include_trades)}))

	def getClosedOrders(self,trades = False, start = '', end = ''):
		req = {}
		if (trades):
			req = req + {'trades':str(trades)}
		if (start != ''):
			req = req + { 'start':start}
		if (end != ''):
			req = req + { 'end':end}
		
		return self.ParseJson(self.k.query_private('ClosedOrders',req))

	def getQueryOrders(self, txid , trades = False):
		req = {}
		if (trades):
			req['trades'] = str(trades).lower()
		
		req['txid'] =  txid
		
		return self.ParseJson(self.k.query_private('QueryOrders',req))
		
	def getTradesHistory(self,trades = False, start = '', end = ''):
		req = {}
		if (trades):
			req['trades'] = str(trades)
		if (start != ''):
			req['start'] = start
		if (end != ''):
			req['end'] = end
		
		return self.ParseJson(self.k.query_private('TradesHistory',req))
		
	def getQueryTrades(self, txid , trades = False):
		req = {}
		if (trades):
			req['trades'] = str(trades).lower()
		
		req['txid'] =  txid

		return self.ParseJson(self.k.query_private('QueryTrades',req))

	def getOpenPositions(self, txid , docalcs = False):
		req = {}
		if (docalcs):
			req['docalcs'] = str(trades).lower()
		
		req['txid'] =  txid

		return self.ParseJson(self.k.query_private('OpenPositions',req))

	def getLedgers(self, ofs, aclass = '' , asset = '', tp = '', start = '', end = ''):
		req = {}
		if (aclass != ''):
			req['aclass'] = aclass

		if (asset != ''):
			req['asset'] = asset

		if (tp != ''):
			req['type'] = tp

		if (start != ''):
			req['start'] = start

		if (end != ''):
			req['end'] = end

		req['ofs'] = ofs
	

		return self.ParseJson(self.k.query_private('Ledgers',req))

	def getQueryLedgers(self,id_list):
			return self.ParseJson(self.k.query_private('OpenOrders', {"id":id_list}))

	def getTradeVolume(self, pair = '' , fee_info = False):
		req = {}
		if (pair != ''):
			req['pair'] = pair

		if (fee_info):
			req['fee-info'] = str(fee_info).lower()
	

		return self.ParseJson(self.k.query_private('TradeVolume',req))

	#PRIVATE TRADING METHODS 
	def getAddOrder(self, pair, price, volume, validate = True, tp = 'buy', ordertype = 'limit'):
		req = {}

		if (ordertype):
			req['ordertype'] = ordertype
		
		req['type'] = tp
		req['pair'] = pair
		req['price'] = price
		req['volume'] = volume
		req['validade'] = str(validate).lower()

		return self.ParseJson(self.k.query_private('AddOrder',req))

	def getCancelOrder(self,txid):
			return self.ParseJson(self.k.query_private('CancelOrder', {"txid":txid}))
