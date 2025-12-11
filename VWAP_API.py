# Algo Trading with Himmat
import time
import requests
from configparser import ConfigParser
from fyers_api import fyersModel
import pandas as pd
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
access_token      = ''
fyers_obj         = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="fyers-logs/")
banknifty_symbol  = "NSE:BANKNIFTY23OCTFUT"
flag              = False

def get_candle_details():
    global flag
    symbolData  = {
        "symbol":banknifty_symbol,
        "resolution":"5",
        "date_format":"1",
        "range_from":"2023-10-04",
        "range_to":"2023-10-06",
        "cont_flag":"1"
    }
    data        = fyers_obj.history(data=symbolData)
    df          = pd.DataFrame(data["candles"])
    df[0]       = pd.to_datetime(df[0], unit='s')
    df.set_index(0, inplace=True)
    df['vwap']  = ta.vwap(df[2], df[3], df[4], df[5], anchor=None, offset=None)

    t      = datetime.datetime.now(IST)
    print(str(t.hour)+':'+str(t.minute)+\
        " VWAP (-2) :: "+str(df["vwap"].iloc[-2])+" VWAP (-1) :: "+str(df["vwap"].iloc[-1])+" Close (-1) :: "+str(df[4].iloc[-1]))
    flag        = True

    if(df[4].iloc[-2] < df["vwap"].iloc[-2] and df[4].iloc[-1] > df["vwap"].iloc[-1]):
        tradetronBuyApi     = "https://api.tradetron.tech/api?auth-token=f83dbdb5-e7cd-4a25-9e6b-6bcaf5718cfa&key=long_trade&value=1"
        responseSL          = requests.get(f"{tradetronBuyApi}")
        print(responseSL)

    if(df[4].iloc[-2] > df["vwap"].iloc[-2] and df[4].iloc[-1] < df["vwap"].iloc[-1]):
        tradetronSellApi    = "https://api.tradetron.tech/api?auth-token=f83dbdb5-e7cd-4a25-9e6b-6bcaf5718cfa&key=short_trade&value=1"
        responseSL          = requests.get(f"{tradetronSellApi}")
        print(responseSL)

while True:
    t      = datetime.datetime.now(IST)
    if(t.minute % 5 == 0 and t.second > 5 and time.localtime().tm_sec < 10 and flag == False):
        get_candle_details()
    elif(t.minute % 5 == 0 and t.second > 10):
        flag        = False
