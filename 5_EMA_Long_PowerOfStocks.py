# Algo Trading with Himmat
# Strategy          - 5 EMA (Power of Stocks)
# Long / Call Buy   - 15 Min Candle
# Risk/Rewards      - 1:2
import time
from configparser import ConfigParser
from fyers_api import fyersModel
from fyers_api.Websocket import ws
import pandas as pd

# read config.ini
config = ConfigParser()
config.read('config.ini')

# Fyers_APP details section
client_id       = config.get('Fyers_APP', 'client_id')

# generate access token
access_token      = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE2OTE1NTIxOTksImV4cCI6MTY5MTYyNzQzOSwibmJmIjoxNjkxNTUyMTk5LCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCazB3bkhyb2psVkZ2MWo5ZmlNZm4wSUdMdjk1TnVFZ0pDSnFJa1IxVEF1eGdVMHpBSk5Eb1RweHkySFdQRzJiUC05a2FZY2EwUVp1LXNkdXNXX1AxZWxJei1HdWY2YmdhaG1jZ1NCdzVpRlBrMkVtTT0iLCJkaXNwbGF5X25hbWUiOiJISU1NQVQgSElORFVSQU8gUEFUSUwiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiI2MTgzZDAyOWRkMjMxMjYwNmQ2NmE0NGYxZTM5MzUyNGU2NzA5YTE1N2NmMzQwYWY4MDE1MGUyNSIsImZ5X2lkIjoiWEgwMTcxNCIsImFwcFR5cGUiOjEwMCwicG9hX2ZsYWciOiJOIn0.AefcN4oEnpqJLAG5qPsb6JPjGKIxWSWqmBJEdR-hOOo'
fyers_obj         = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="fyers-logs/")
banknifty_symbol  = "NSE:NIFTYBANK-INDEX" # change or add multiple symbols

# create web-socket object
websocket_access_token  = client_id+':'+access_token # access token for websocket connection
data_type               = "symbolData"
fs                      = ws.FyersSocket(access_token=websocket_access_token, log_path="fyers-logs/")

# initialize variables
is_trade          = False
ema_period        = 5
stop_loss_pts     = ''
target_pts        = ''
candle_low        = ''
candle_high       = ''
candle_ema        = ''

# need to create like this NSE:BANKNIFTY2380344400CE
# Symbol - NSE:BANKNIFTY
# Expiry - 23810
# Strike - 44400 # calculate run time 
# Side - CE or PE # calculate run time 
option_symbol   = 'NSE:BANKNIFTY23810'
fyers_symbol    = ''

def get_candle_details():
    if(time.localtime().tm_min % 15 == 0 and time.localtime().tm_sec > 5 and time.localtime().tm_sec < 15):
        global candle_low, candle_high, candle_ema
        symbolData  = {
            "symbol":banknifty_symbol,
            "resolution":"15",
            "date_format":"1",
            "range_from":"2023-08-08",
            "range_to":"2023-08-09",
            "cont_flag":"1"
        }
        data = fyers_obj.history(data=symbolData)
        df      = pd.DataFrame(data["candles"])
        # calculate EMA values
        df['ema_period'] = df[4].ewm(span=ema_period, adjust=False).mean()
        candle_low       = df[3].iloc[-1]
        candle_high      = df[2].iloc[-1]
        candle_ema       = df['ema_period'].iloc[-1]

def on_price_update(data):
    global fs, is_trade, stop_loss_pts, target_pts, fyers_symbol, candle_low, candle_high, candle_ema
    # extract LTP from the data
    ltp         = float(data[0]['ltp'])
    
    if(time.localtime().tm_min % 15 == 0 and time.localtime().tm_sec > 5 and time.localtime().tm_sec < 15):
        get_candle_details()

    print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
          " LTP : "+str(ltp)+" 5 EMA : "+str(candle_ema)+" High : "+str(candle_high)+" Low : "+str(candle_low))
    
    # check entry condition
    if candle_high < candle_ema and ltp > candle_high and not is_trade:
        print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
              " Buy ATM Call Option (Crosses Above)")
        round_to_strike = int(round(float(ltp), -2)) # round ltp to nearest strike price
        fyers_symbol    = str(option_symbol)+str(round_to_strike)+'CE'
        trade       = { 'symbol': fyers_symbol,
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
        print('Order Details :: ', orderDetails)
        stop_loss_pts       = candle_low
        target_pts          = candle_high + float(float(candle_high - candle_low) * 2)
        is_trade            = True

    # check for stop loss or target if trade is taken
    if is_trade:
        if ltp < stop_loss_pts or ltp > target_pts:
            print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)+\
              " Stop Loss / Target Hit")
            trade       = { 'symbol': fyers_symbol, 
                            'qty': 15,
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
            print('SL/Target Order Details :: ', orderDetails)
            is_trade = False

fs.websocket_data = on_price_update # function to run on every web socket response 
symbol            = [banknifty_symbol]
fs.subscribe(symbol=symbol, data_type=data_type)
fs.keep_running()
