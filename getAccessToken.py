from configparser import ConfigParser
from fyers_api import accessToken
from fyers_api import fyersModel
from fyers_api.Websocket import ws

# read config.ini
config = ConfigParser()
config.read('config.ini')

# Fyers_APP details section
client_id       = config.get('Fyers_APP', 'client_id')
app_secret      = config.get('Fyers_APP', 'app_secret')
redirect_uri    = config.get('Fyers_APP', 'redirect_uri')

auth_code       = ''
access_token    = ''
session         = accessToken.SessionModel(
                    client_id=client_id,
                    secret_key=app_secret,
                    redirect_uri=redirect_uri,
                    response_type="code",
                    grant_type="authorization_code"
                )

# genetrate auth code url
def generate_auth_code_url():
    generate_auth_code_url = session.generate_authcode()
    print('generate_auth_code_url :: ', generate_auth_code_url)

# get access token
def get_access_token():
    auth_code   = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJpYXQiOjE2OTY5OTQzMzQsImV4cCI6MTY5NzAyNDMzNCwibmJmIjoxNjk2OTkzNzM0LCJhdWQiOiJbXCJ4OjBcIiwgXCJ4OjFcIiwgXCJ4OjJcIiwgXCJkOjFcIiwgXCJkOjJcIiwgXCJ4OjFcIiwgXCJ4OjBcIl0iLCJzdWIiOiJhdXRoX2NvZGUiLCJkaXNwbGF5X25hbWUiOiJYSDAxNzE0Iiwib21zIjoiSzEiLCJoc21fa2V5IjoiNjE4M2QwMjlkZDIzMTI2MDZkNjZhNDRmMWUzOTM1MjRlNjcwOWExNTdjZjM0MGFmODAxNTBlMjUiLCJub25jZSI6IiIsImFwcF9pZCI6IjBKRFNZVDBWNkoiLCJ1dWlkIjoiNzY4YTk0NGM0N2Q5NDM4MzlmNGRjNjBiYjJjNmE0MjIiLCJpcEFkZHIiOiIwLjAuMC4wIiwic2NvcGUiOiIifQ.Axo9j5KDYNaQRpoYF7zMzUzfSZxVH7mEE7X8mhPFNNA"
    session.set_token(auth_code)
    response = session.generate_token()
    access_token = response['access_token']
    print('access_token :: ', access_token)

# connect to broker
def connect_to_broker():
    access_token= "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE2ODc3OTY2NzMsImV4cCI6MTY4NzgyNTgzMywibmJmIjoxNjg3Nzk2NjczLCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCa21idkIzdlBOOWVWN1FvZ2JwTnlqRHl2MS1SdmpJSjdEajgyQ1gzRmJhU0c1WUxySjlieVpzTXg5N2RmdW9GUUJ3NEkxTW9fNV93c0xFMk5wZ1IyeEZrSUNkbTRYcDN0Rjc0SmlMV3VSRVVvWDM0ND0iLCJkaXNwbGF5X25hbWUiOiJISU1NQVQgSElORFVSQU8gUEFUSUwiLCJvbXMiOiJLMSIsImZ5X2lkIjoiWEgwMTcxNCIsImFwcFR5cGUiOjEwMCwicG9hX2ZsYWciOiJOIn0.SUOjgxb3apNf2TuZV3Z6_FML-fqSj-plOHufjmPCUqg"
    fyers       = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="fyers-logs/")
    #print(fyers.get_profile())
    print(fyers.funds())
    fyers.holdings()
    fyers.positions()
    fyers.tradebook()
    fyers.orderbook()

def custom_message(msg):       ### This function can be anything which you want to configure at your end 
    print (f"Custom:{msg}")

# get web socket data
def get_websocket_data():
    access_token= client_id+":eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE2ODc5MjczMDAsImV4cCI6MTY4Nzk5ODY0MCwibmJmIjoxNjg3OTI3MzAwLCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCa203b0VGaTg1VkE2enA1WVZCV09uN0lzemd3bGlYbllRSDZILWxwR2dQdmJNMkxVMTZKR2FOQ2k5T2ZvMmp3Y2h3TVljc0JKRHdsZXJpMWdwMjhZVTA0blROc1BTclpMNW5HLVZpMFFubzh5QUF2Yz0iLCJkaXNwbGF5X25hbWUiOiJISU1NQVQgSElORFVSQU8gUEFUSUwiLCJvbXMiOiJLMSIsImZ5X2lkIjoiWEgwMTcxNCIsImFwcFR5cGUiOjEwMCwicG9hX2ZsYWciOiJOIn0.qwnihs6N48upZrDb5k7GOxnGEESPG38weXmCNroZH3M"
    data_type = "symbolData"
    symbol = ["NSE:NIFTYBANK-INDEX"]
    fs = ws.FyersSocket(access_token=access_token,log_path="fyers-logs/")
    fs.websocket_data = custom_message
    fs.subscribe(symbol=symbol,data_type=data_type)
    fs.keep_running()

if __name__ == "__main__":
    #generate_auth_code_url()
    get_access_token()
    #connect_to_broker()
    #get_websocket_data()

