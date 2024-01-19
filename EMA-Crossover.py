# Algo Trading with Himmat
# Strategy - 10 & 30 EMA Crossover 
import time
from configparser import ConfigParser
from fyers_api import fyersModel
import pandas as pd

# read config.ini
config = ConfigParser()
config.read('config.ini')

# Fyers_APP details section
client_id       = config.get('Fyers_APP', 'client_id')

# generate access token
access_token      = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE2ODg0NDIxMzQsImV4cCI6MTY4ODUxNzAxNCwibmJmIjoxNjg4NDQyMTM0LCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCa281VVdBYjlZOE9UOVhwM3dub1FBLWwwd3lBVGlDZHZBYjBveW9xdHh5ZUlxTl9TNGRSVFBkSG42QXpwSVpBOFc2TXR1X3lZdzFkSDlGalZTUGlhTWxzRzFsOTY3TENkdEtrVGkxNEZpNVQtazBjQT0iLCJkaXNwbGF5X25hbWUiOiJISU1NQVQgSElORFVSQU8gUEFUSUwiLCJvbXMiOiJLMSIsImZ5X2lkIjoiWEgwMTcxNCIsImFwcFR5cGUiOjEwMCwicG9hX2ZsYWciOiJOIn0.SYrNVwgpB6CXoRvm18K4Fo6QauFuHi1WaVx1x3_OQUk'
fyers_obj         = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="fyers-logs/")
banknifty_symbol  = "NSE:NIFTYBANK-INDEX" # change or add multiple symbols

# Initialize variables
is_long_trade     = False
is_short_trade    = False
ema_short_period  = 10
ema_long_period   = 30

# need to create like this NSE:BANKNIFTY2370644400CE
# Symbol - NSE:BANKNIFTY # Expiry - 23706 # Strike - 44400 # Side - CE or PE # will calculate run time when breakout happens 
option_symbol   = 'NSE:BANKNIFTY23706'
call_symbol     = ''
put_symbol      = ''

# Define the WebSocket connection and data callback function
def process_data(data):
    global is_long_trade, is_short_trade, call_symbol, put_symbol 
    
    df = pd.DataFrame(data["candles"])
    
    # Calculate EMA values
    df['ema_short'] = df[4].ewm(span=ema_short_period, adjust=False).mean()
    df['ema_long'] = df[4].ewm(span=ema_long_period, adjust=False).mean()

    print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
          " Candle -2 :: 10 EMA : "+str(df['ema_short'].iloc[-2])+" 30 EMA : "+str(df['ema_long'].iloc[-2]))
    print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
          " Candle -1 :: 10 EMA : "+str(df['ema_short'].iloc[-1])+" 30 EMA : "+str(df['ema_long'].iloc[-1]))

    # Check for EMA crossover
    if df['ema_short'].iloc[-2] < df['ema_long'].iloc[-2] and df['ema_short'].iloc[-1] > df['ema_long'].iloc[-1]:
        # EMA crossover to the upside
        if not is_long_trade:
            print('Exit put position if any open')
            # write code here to square off put open position

            print("Placed call buy trade:")
            round_to_strike = int(round(float(df[4].iloc[-1]), -2)) # round closed price to nearest strike price
            call_symbol     = str(option_symbol)+str(round_to_strike)+'CE'
            print('call_symbol :: ', call_symbol)
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
            orderDetails = fyers_obj.place_order(data=trade)
            print('orderDetails :: ', orderDetails)
            is_long_trade = True
            is_short_trade = False
    
    elif df['ema_short'].iloc[-2] > df['ema_long'].iloc[-2] and df['ema_short'].iloc[-1] < df['ema_long'].iloc[-1]:
        # EMA crossover to the downside
        if not is_short_trade:
            print('Exit call position if any open')
            # write code here to square off call open position

            print("Placed put buy trade:")
            round_to_strike = int(round(float(df[4].iloc[-1]), -2)) # round closed price to nearest strike price
            put_symbol     = str(option_symbol)+str(round_to_strike)+'PE'
            print('call_symbol :: ', put_symbol)
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
            orderDetails = fyers_obj.place_order(data=trade)
            print('orderDetails :: ', orderDetails)
            is_short_trade = True
            is_long_trade = False

symbolData  = {
    "symbol":banknifty_symbol,
    "resolution":"5",
    "date_format":"1",
    "range_from":"2023-06-28",
    "range_to":"2023-07-04",
    "cont_flag":"1"
}
while True:
    # Get the historical candles data 
    data = fyers_obj.history(data=symbolData)
    process_data(data)
    time.sleep(300)
