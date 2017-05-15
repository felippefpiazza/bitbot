import kraken_methods
from mysql_handler import handler
from exchange_rate import exchange
import sys

k = kraken_methods.APIMethods(1)
e = exchange.Exchange(1)

def getAssets() :
	#GET KRAKEN ASSETS
	resp = k.getAssets()

def getAssetPair() :
	#GET KRAKEN AASSET PAIRS
	resp = k.getAssetPair()

def getTickers() :
	db = handler.Handler()
	db.connect()
	run_id = db.insertIntoTable("rates_runs",{},True)
	#GET KRAKEN TICKERS
	resp = k.getEnabledTickers(run_id)

def FindLocalGain(rates_run_id = None) :
	if rates_run_id is None:
		e.findLocalExchanges()
	elif int(rates_run_id) > 0:
		e.findLocalExchanges(rates_run_id)
	else:
		i = 1
		while i < 100:
			print("Checking Run --> {}".format(i))
			e.findLocalExchanges(i)
			i += 1

if len(sys.argv) > 1:
	if sys.argv[1] == 'getAssets':
		getAssets()
	if sys.argv[1] == 'getAssetPairs':
		getAssetPair()
	if sys.argv[1] == 'getTickers':
		getTickers()
	if sys.argv[1] == 'FindLocalGain':
		if len(sys.argv) > 2:
			FindLocalGain(sys.argv[2])
		else:
			getTickers()
			FindLocalGain()
else:
	resp = k.getDepth("XXBTZUSD",10)
	print(resp)
	print("Nothing to do")




#resp = k.getAssets()
#resp = k.getAssets("XXDG,XETC")
#resp = k.getAssetPair("XXBTZUSD")
#resp = k.getTickers("XXBTZUSD")
#resp = k.getOHLC("XXBTZUSD")
#resp = k.getDepth("XXBTZUSD",2)
#resp = k.getTrades("XXBTZUSD")
#resp = k.getSpread("XXBTZUSD")
#resp = k.getTradeBalance("XXDG")
#resp = k.getOpenOrders(True)
#resp = k.getClosedOrders()
#resp = k.getQueryOrders("OSK2K6-NU7LU-23LBQK,O73GJR-KH33T-OYOGJS")
#resp = k.getTradesHistory()
#resp = k.getQueryTrades("O73GJR-KH33T-OYOGJS")
#resp = k.getOpenPositions("OSK2K6-NU7LU-23LBQK,O73GJR-KH33T-OYOGJS")
#resp = k.getLedgers(1)
#resp = k.getQueryLedgers("LJOGRR-NJ5S6-ABR2IQ,LAZENU-GPW6P-Z4QTFP")
#resp = k.getTradeVolume("XXBTZUSD",True)

#VENDE 0.001 XBT por dollar a um cambio de 25000 dollares por XBT
#resp = k.getAddOrder("XXBTZUSD", "25000", "0.001", True, 'sell', 'limit')
#resp = k.getCancelOrder("OHLNBD-LPVTB-ZQIZD3")




#currency_pair = curr1+curr2
#exchange_ask = resp['result'][currency_pair]['a'][0]
#exchange_bid = resp['result'][currency_pair]['b'][0]
#exchange_last_trade = resp['result'][currency_pair]['c'][0]
#volume = resp['result'][currency_pair]['v'][0]

#sql = mysql_handler.Handler(username,password,db,host)
#sql.connect()
#query = "INSERT INTO rates "
#query += "(" + "measure_datetime," + "currency_pair," + "exchange_ask," + "exchange_bid," +  "exchange_last_trade," + "volume," + "updated_at," + "created_at" + ")" 
#query += " values " 
#query += "(" +  "NOW()," +  "'" +  currency_pair + "'," + "'" +  exchange_ask + "'," + "'" +  exchange_bid + "'," + "'" +  exchange_last_trade + "'," + "'" +  volume + "'," + "NOW()," + "NOW()" + ")"
#print(query)
#sql.execute(query)


