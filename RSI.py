# Algo Trading with Himmat
# Strategy - RSI Crossover 
import time
from configparser import ConfigParser
from fyers_api import fyersModel
import pandas as pd
import talib

# read config.ini
config = ConfigParser()
config.read('config.ini')

# Fyers_APP details section
client_id       = config.get('Fyers_APP', 'client_id')

# generate access token
access_token      = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE2OTE2NDExNjMsImV4cCI6MTY5MTcxMzgyMywibmJmIjoxNjkxNjQxMTYzLCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCazFHVkxBdGstSkJxNGlWeG94NWlqRlN6T1FHQjhZUjhNY2wwQTMteThpcF9ZSnFScEdmN0ZsWkJiRmxTMWpOVWhkd0tFcnVqLWlzZ2lkQXJfZlFUb3dOcmU5SU5yWUR0Qm5SVDljbW9QNUcyUVAxST0iLCJkaXNwbGF5X25hbWUiOiJISU1NQVQgSElORFVSQU8gUEFUSUwiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiI2MTgzZDAyOWRkMjMxMjYwNmQ2NmE0NGYxZTM5MzUyNGU2NzA5YTE1N2NmMzQwYWY4MDE1MGUyNSIsImZ5X2lkIjoiWEgwMTcxNCIsImFwcFR5cGUiOjEwMCwicG9hX2ZsYWciOiJOIn0.V1-XoVYsCLQUqG7Mb1apoMHclDj9_UIofZQzMtZugbQ'
fyers_obj         = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="fyers-logs/")

# initialize variables
banknifty_symbol   = "NSE:NIFTYBANK-INDEX" 
is_long_trade      = False
is_short_trade     = False
rsi_period         = 14
call_rsi_threshold = 60
put_rsi_threshold  = 40

# need to create fyers symbol strcture like NSE:BANKNIFTY2370644400CE
# Symbol - NSE:BANKNIFTY 
# Expiry - 23810 
# Strike - 45000 # will calculate run time 
# Side - CE or PE # will calculate run time 
option_symbol     = 'NSE:BANKNIFTY23810'
call_symbol       = ''
put_symbol        = ''

def process_data(data):
    global is_long_trade, is_short_trade, call_symbol, put_symbol 
    
    df          = pd.DataFrame(data["candles"])
    df['rsi']   = talib.RSI(df[4], timeperiod=rsi_period) 
    
    print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
          " RSI (-2 Candle) : "+str(df['rsi'].iloc[-2])+" RSI (-1 Candle) : "+str(df['rsi'].iloc[-1]))
    
    # Check for long entry condition
    if not is_long_trade and df['rsi'].iloc[-2] < call_rsi_threshold and df['rsi'].iloc[-1] > call_rsi_threshold:
        # Place long trade
        print("RSI crossover: Buy Bank Nifty / Buy Call Option")
        round_to_strike = int(round(float(df[4].iloc[-1]), -2)) # round closed price to nearest strike price
        call_symbol     = str(option_symbol)+str(round_to_strike)+'CE'
        trade       = { 'symbol': call_symbol, 
                        'qty': 15,
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
        orderDetails = fyers_obj.place_order(data=trade)
        print('orderDetails :: ', orderDetails)
        
        # Set trade flags
        is_long_trade = True
        is_short_trade = False
    
    if is_long_trade:
        print("Long entry has been taken. Check conditions for Stop loss or Target")
        # write your logic for stop loss or target
        # is_long_trade = False

    # Check for short entry condition
    if not is_short_trade and df['rsi'].iloc[-2] > put_rsi_threshold and df['rsi'].iloc[-1] < put_rsi_threshold:
        # Place short trade
        print("RSI crossover: Sell Bank Nifty / Buy Put Option")
        round_to_strike = int(round(float(df[4].iloc[-1]), -2)) # round closed price to nearest strike price
        put_symbol     = str(option_symbol)+str(round_to_strike)+'PE'
        trade       = { 'symbol': put_symbol, 
                        'qty': 15,
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
        orderDetails = fyers_obj.place_order(data=trade)
        print('orderDetails :: ', orderDetails)
        
        # Set trade flags
        is_long_trade = False
        is_short_trade = True

    if is_short_trade:
        print("Short entry has been taken. Check conditions for Stop loss or Target")
        # write your logic for stop loss or target
        # is_short_trade = False

symbolData  = {
    "symbol":banknifty_symbol,
    "resolution":"5",
    "date_format":"1",
    "range_from": "2023-08-09",
    "range_to": "2023-08-10",
    "cont_flag":"1"
}

while True:
    # Get the historical candles data 
    data = fyers_obj.history(data=symbolData)
    process_data(data)
    time.sleep(300)
