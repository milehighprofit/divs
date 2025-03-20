import datetime as dt
import requests
import pandas as pd
import numpy as np
import matplotlib
import json
resp = requests.get('https://api.kraken.com/0/public/AssetPairs?')
data = resp.json()

def get_rsi(close, lookback):
    ret = close.diff()
    up = []
    down = []
    for i in range(len(ret)):
        if ret[i] < 0:
            up.append(0)
            down.append(ret[i])
        else:
            up.append(ret[i])
            down.append(0)
    up_series = pd.Series(up)
    down_series = pd.Series(down).abs()
    up_ewm = up_series.ewm(com = lookback - 1, adjust = False).mean()
    down_ewm = down_series.ewm(com = lookback - 1, adjust = False).mean()
    rs = up_ewm/down_ewm
    rsi = 100 - (100 / (1 + rs))
    rsi_df = pd.DataFrame(rsi).rename(columns = {0:'rsi'}).set_index(close.index)
    rsi_df = rsi_df.dropna()
    return rsi_df[3:]


def getmarkets(DATA):
    pairs = []
    navne = list(data["result"].keys())
    for navn in navne:
        if navn[-3:] == "USD":
            pairs.append(navn)
    return pairs
            

perpnames = getmarkets(data)[:10]



def now(lookback): 
    #get time now convert it to unix
    timenow = dt.datetime.utcnow()
    end_time = timenow.replace(tzinfo=dt.timezone.utc).timestamp()
    #get lookback and convert to unix 
    start_time = dt.datetime.utcnow() - dt.timedelta(hours = lookback)
    start_time = start_time.replace(tzinfo=dt.timezone.utc).timestamp() 
    return start_time, end_time

def ohlc(name, tf):
    _start_time, _end_time = now(14) 
    data = requests.get(f'https://api.kraken.com/0/public/OHLC?pair={name}&interval={tf}&since={_start_time}') 
    data = data.json()
    data = pd.DataFrame(data['result'])
    # Drop the last column
    data = data.iloc[:, :-1]
    
    return data


dfs = []
tf = 5

for perp in perpnames: 
    dfs.append(ohlc(perp, tf))

df3 = pd.DataFrame(dfs['teams'].to_list(), columns=['open','high',"low","close","vwap","Volume","Counter"])


df = pd.concat(dfs, axis=1)


def divs(closes, columns, ob=50, os=50, period=14):
    """Calculates bullish and bearish RSI divergences under oversold or overbought conditions"""

    closes['RSI'] = get_rsi(closes.iloc[:, columns], 14)
    closes['rolling_rsi_high'] = closes['RSI'].rolling(period).max()
    closes['rolling_rsi_low'] = closes['RSI'].rolling(period).min()
    closes['rolling_closing_high'] = closes.iloc[:, columns].rolling(period).max()
    closes['rolling_closing_low'] = closes.iloc[:, columns].rolling(period).min()


    closes['new_RSI_high'] = np.where(closes['rolling_rsi_high'] > closes['rolling_rsi_high'].shift(), 1, 0)
    closes['new_RSI_low'] = np.where(closes['rolling_rsi_low'] < closes['rolling_rsi_low'].shift(), 1, 0)


    closes['new_closing_high'] = np.where(closes['rolling_closing_high'] > closes['rolling_closing_high'].shift(), 1, 0)
    closes['new_closing_low'] = np.where(closes['rolling_closing_low'] < closes['rolling_closing_low'].shift(), 1, 0)

    closes['bearish_rsi_div'] = np.where((closes['new_closing_high'] == 1) & (closes['new_RSI_high'] == 0) & (closes['RSI'] > ob), 1, 0)
    closes['bullish_rsi_div'] = np.where((closes['new_closing_low'] == 1) & (closes['new_RSI_low'] == 0) & (closes['RSI'] < os), 1, 0)
    closes = closes.dropna()
    return closes[['bullish_rsi_div', 'bearish_rsi_div']]

længde = len(list(data["result"].keys()))
rsidata = [] 
for column in range(længde):
   rsidata.append(divs(closes, column))

