# Strategy - Intraday 15Min Breakout 
# Entry - Breakout Above or Below 15Min Candle
# Exit/SL - Cross back opposite side of the candle 

import time
from configparser import ConfigParser
from fyers_api import fyersModel
from fyers_api.Websocket import ws

# read config.ini
config = ConfigParser()
config.read('config.ini')

# Fyers_APP details section
client_id       = config.get('Fyers_APP', 'client_id')
# generate Access Token (once in 24 hours)
access_token    = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE2ODgwOTQ1MzAsImV4cCI6MTY4ODE3MTQ1MCwibmJmIjoxNjg4MDk0NTMwLCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCa25rZEMwdUNNZ1JMWVduT0RUSTlpQWx0T1hpLXFsV3I5cFhaZ3pqWUt5M3dIWjlGdHJPZVdHZTZxWDh5N3kza0RwX1ZNTzEzN3RjNl9BQlpJUEpmdVBmclE3UERMcEh0TzNnZENxY1pOV1VvYnpnYz0iLCJkaXNwbGF5X25hbWUiOiJISU1NQVQgSElORFVSQU8gUEFUSUwiLCJvbXMiOiJLMSIsImZ5X2lkIjoiWEgwMTcxNCIsImFwcFR5cGUiOjEwMCwicG9hX2ZsYWciOiJOIn0.Zh2GI7ZcIfv-V8zRsfD7EwpklG5_Dmpamatilfi73fM'

# Create fyers instance
fyers_obj           = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="fyers-logs/")
banknifty_symbol    = "NSE:NIFTYBANK-INDEX" # change or add multiple symbols
# Symbol Data to fetch 15 mins details
symbolData  = {
    "symbol":banknifty_symbol,
    "resolution":"15",
    "date_format":"1",
    "range_from":"2023-06-30", # pass this as script param or keep in config.ini and read
    "range_to":"2023-06-30", # pass this as script param or keep in config.ini and read
    "cont_flag":"1"
}
# Get the historical candles data 
data = fyers_obj.history(data=symbolData)
print("1st 15Min Candle => Open :: "+str(data['candles'][0][1])+" High :: "+str(data['candles'][0][2])+\
      " Low :: "+str(data['candles'][0][3])+" Close :: "+str(data['candles'][0][4]))

# breakout examples
# first, second or third candle breakout
# red or green candle breakout
# Can be added with other indicator e.g. RSI or ADX etc.

# extract high and low price from the first 15-minute candle
high_price  = float(data['candles'][0][2])
low_price   = float(data['candles'][0][3])
time.sleep(2)

websocket_access_token  = client_id+':'+access_token # access token for websocket connection
data_type               = "symbolData"
fs                      = ws.FyersSocket(access_token=websocket_access_token, log_path="fyers-logs/")

# initialize variables
is_break_high   = False
is_break_low    = False
stop_loss       = None

# need to create like this NSE:BANKNIFTY23JUN44400CE
# Symbol - NSE:BANKNIFTY
# Expiry - 23JUN
# Strike - 44400 # will calculate run time when breakout happens 
# Side - CE or PE
option_symbol   = 'NSE:BANKNIFTY23706'
call_symbol     = ''
put_symbol      = ''

def on_price_update(data):
    global fs, is_break_high, is_break_low, stop_loss, option_symbol, call_symbol, put_symbol
    # extract LTP from the data
    ltp         = float(data[0]['ltp'])
    print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
          " ltp :: "+str(ltp)+" high :: "+str(high_price)+" low :: "+str(low_price))

    # check for buy signal (cross above high)
    if ltp > high_price and not is_break_high:
        print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
              " Buy ATM Call Option (Breakout Above)")
        round_to_strike = int(round(float(ltp), -2)) # round ltp to nearest strike price
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
        is_break_high   = True
        is_break_low    = False
        stop_loss       = low_price
    # check for sell signal (cross below low)
    elif ltp < low_price and not is_break_low:
        print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
              " Buy ATM Put Option (Breakout Below)")
        round_to_strike = int(round(float(ltp), -2)) # round ltp to nearest strike price
        put_symbol      = str(option_symbol)+str(round_to_strike)+'PE'
        print('put_symbol :: ', put_symbol)
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
        is_break_low    = True
        is_break_high   = False
        stop_loss       = high_price

    # set stop-loss based on breakout
    # you can also add target or TSL based on your requirements
    if is_break_high and ltp < stop_loss:
        print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
              " Stop Loss Hit: Breakout Below")
        trade       = { 'symbol': call_symbol, 
                        'qty': 25,
                        'type': 2, # 1 Limit Order, 2 Market
                        'side': -1, # 1 => Buy & -1 => Sell
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
    elif is_break_low and ltp > stop_loss:
        print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
              " Stop Loss Hit: Breakout Above")
        trade       = { 'symbol': put_symbol, 
                        'qty': 25,
                        'type': 2, # 1 Limit Order, 2 Market
                        'side': -1, # 1 => Buy & -1 => Sell
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

fs.websocket_data = on_price_update # function to run on every web socket response 
symbol            = [banknifty_symbol]
fs.subscribe(symbol=symbol, data_type=data_type)
fs.keep_running()
