# Algo Trading with Himmat
# Strategy - VWAP Crossover 
import time
from configparser import ConfigParser
from fyers_api import fyersModel
import pandas as pd
# import ta
import pandas_ta as ta
import datetime
import pytz

IST                 = pytz.timezone('Asia/Kolkata')

# read config.ini
config = ConfigParser()
config.read('config.ini')

# Fyers_APP details section
client_id       = config.get('Fyers_APP', 'client_id')

# generate access token
access_token      = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE2OTIyNDE1NjUsImV4cCI6MTY5MjMxODYwNSwibmJmIjoxNjkyMjQxNTY1LCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCazNZNmRVUWROeUU5ejNZeGNtUWttSF9IQzNsU3d3S0ppRm1GOEdqOTJhWUxKd2tBLW54NGlCQjVyS3U3NG5JSGRWWkVPN3NxNHpXZlJ5UW11ZGNvOGNSRGtIdHNkeUl0SGd3U1JKNk9IeFN2Tkd4ND0iLCJkaXNwbGF5X25hbWUiOiJISU1NQVQgSElORFVSQU8gUEFUSUwiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiI2MTgzZDAyOWRkMjMxMjYwNmQ2NmE0NGYxZTM5MzUyNGU2NzA5YTE1N2NmMzQwYWY4MDE1MGUyNSIsImZ5X2lkIjoiWEgwMTcxNCIsImFwcFR5cGUiOjEwMCwicG9hX2ZsYWciOiJOIn0.PUAUdvVXiz2KUG2ZRPN5ZoT0NfVxZ4-HDpdaU0OSW3M'
# create fyers object
fyers_obj         = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="fyers-logs/")

# Initialize variables
banknifty_symbol  = "NSE:BANKNIFTY23AUGFUT" # Should be future symbol for VWAP
is_long_trade     = False
is_short_trade    = False
vwap_period       = 20

# need to create fyers symbol strcture like NSE:BANKNIFTY2370644400CE
# Symbol - NSE:BANKNIFTY # Expiry - 23706 # Strike - 44400 # Side - CE or PE # will calculate run time when breakout happens 
option_symbol     = 'NSE:BANKNIFTY23713'
call_symbol       = ''
put_symbol        = ''

def calculate_vwap(data):
    data["Volume_Price"] = data[5] * data[4] # volume * close price
    data["Cumulative_Volume_Price"] = data["Volume_Price"].cumsum()
    data["Cumulative_Volume"] = data[5].cumsum()
    data["VWAP"] = data["Cumulative_Volume_Price"] / data["Cumulative_Volume"]
    # data['vwap'] = ta.volume.volume_weighted_average_price(data['high'], data['low'], data['close'], data['volume'], window=90, fillna=True)
    data['vwap_1'] = ta.vwap(data[2], data[3], data[4], data[5], anchor=None, offset=None)
    #data.reset_index(inplace = True)
    return data

def process_data(data):
    global is_long_trade, is_short_trade, call_symbol, put_symbol 
    df      = pd.DataFrame(data["candles"])
    #df.set_index(0, inplace=True)
    #df.index = pd.to_datetime(df.index)
    df[0] = pd.to_datetime(df[0], unit='s')
    #df.index = pd.to_datetime(df.index)
    df.set_index(0, inplace=True)
    data    = calculate_vwap(df)

    #print('data :: ', str(data))
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(data)

    print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
          " VWAP :: "+str(data["vwap_1"].iloc[-1])+" Close :: "+str(data[4].iloc[-1]))

    # Get the latest VWAP and close price
    previous_vwap   = data["VWAP"].iloc[-2]
    previous_close  = data[4].iloc[-2]
    current_vwap    = data["VWAP"].iloc[-1]
    current_close   = data[4].iloc[-1]
    
    #print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
    #      " -2 Candle : VWAP : "+str(previous_vwap)+" Close Price : "+str(previous_close))
    #print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
    #      " -1 Candle : VWAP : "+str(current_vwap)+" Close Price : "+str(current_close))
    
    # Check for VWAP crossover
    if previous_close < previous_vwap and current_close > current_vwap and not is_long_trade:
        # Place long trade
        #print("VWAP crossover: Buy Bank Nifty / Buy Call Option")
        round_to_strike = int(round(float(data[4].iloc[-1]), -2)) # round closed price to nearest strike price
        call_symbol     = str(option_symbol)+str(round_to_strike)+'CE'
        #print('call_symbol :: ', call_symbol)
        trade       = { 'symbol': call_symbol, 
                        'qty': 25,
                        'type': 2, # 1 Limit Order, 2 Market
                        'side': 1, # 1 => Buy & -1 => Sell
                        'productType': 'INTRADAY', # MARGIN, CNC, INTRADAY
                        'limitPrice': 0,
                        'stopPrice': 0,
                        'disclosedQty': 0,
                        'validity': 'DAY',
                        'offlineOrder': 'False',
                        'stopLoss': 0,
                        'takeProfit': 0 }
        #orderDetails = fyers_obj.place_order(data=trade)
        #print('orderDetails :: ', orderDetails)
        
        # Set trade flags
        #is_long_trade = True
        #is_short_trade = False
        
    elif previous_close > previous_vwap and current_close < current_vwap and not is_short_trade:
        # Place short trade
        #print("VWAP crossover: Sell Bank Nifty / Buy Put Option")
        round_to_strike = int(round(float(data[4].iloc[-1]), -2)) # round closed price to nearest strike price
        put_symbol     = str(option_symbol)+str(round_to_strike)+'PE'
        #print('call_symbol :: ', put_symbol)
        trade       = { 'symbol': put_symbol, 
                        'qty': 25,
                        'type': 2, # 1 Limit Order, 2 Market
                        'side': 1, # 1 => Buy & -1 => Sell
                        'productType': 'INTRADAY', # MARGIN, CNC, INTRADAY
                        'limitPrice': 0,
                        'stopPrice': 0,
                        'disclosedQty': 0,
                        'validity': 'DAY',
                        'offlineOrder': 'False',
                        'stopLoss': 0,
                        'takeProfit': 0 }
        #orderDetails = fyers_obj.place_order(data=trade)
        #print('orderDetails :: ', orderDetails)
        
        # Set trade flags
        #is_long_trade = False
        #is_short_trade = True

#start script at 9:15
t                   = datetime.datetime.now(IST)
t1                  = datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second)
startTime           = datetime.datetime(t.year,t.month,t.day,11,55)
print('sleep for : ', (startTime-t1).total_seconds())
#time.sleep((startTime-t1).total_seconds())

while True:
    current_time = int(time.time())
    range_from = current_time - (vwap_period + 1) * 60
    range_to = current_time
    #if(time.localtime().tm_min % 5 == 0 and time.localtime().tm_sec == 0):
    symbolData  = {
        "symbol":banknifty_symbol,
        "resolution":"5",
        "date_format":"1",
        "range_from": "2023-08-16",
        "range_to": "2023-08-17",
        "cont_flag":"1"
    }
    
    # Get the historical candles data 
    data = fyers_obj.history(data=symbolData)
    process_data(data)
    time.sleep(300)
