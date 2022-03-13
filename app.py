from flask import Flask, render_template, request
import datetime as dt
import requests
import pandas as pd
import numpy as np
import matplotlib
import mplfinance as mpf
import talib

app = Flask(__name__)
if __name__ == "__main__":
    app.debug = True

def now(lookback): 
    #get time now convert it to unix
    timenow = dt.datetime.utcnow()
    end_time = timenow.replace(tzinfo=dt.timezone.utc).timestamp()
    #get lookback and convert to unix 
    start_time = dt.datetime.utcnow() - dt.timedelta(lookback)
    start_time = start_time.replace(tzinfo=dt.timezone.utc).timestamp() 
    return start_time, end_time


def getmarkets(PERP):
    markets = requests.get(f"https://ftx.com/api/markets").json()
    markets = pd.DataFrame(markets['result'])
    markets = markets['name'].tolist()
    markets = [market for market in markets if market.endswith(PERP)]
    return markets

perpnames = getmarkets('PERP')

def ohlc(perpnames, tf, daysback):
    _start_time, _end_time = now(daysback) 
    data = requests.get(f"https://ftx.com/api//markets/{perpnames}/candles?resolution={tf}&start_time={_start_time}&end_time={_end_time}").json()
    data = pd.DataFrame(data['result'])
    return data

dfs = []
tf = 3600
daysback = 2
for perp in perpnames: 
    dfs.append(ohlc(perp, tf, daysback))


nameless = pd.concat(dfs, axis=1)
closes = nameless.loc[:,nameless.columns.get_level_values(0).isin(['close'])]


def divs(closes, columns, ob=70, os=30, period=14):
    """Calculates bullish and bearish RSI divergences under oversold or overbought conditions"""

    closes['RSI'] = talib.RSI(closes.iloc[:, columns])
    closes['rolling_rsi_high'] = closes['RSI'].rolling(period).max()
    closes['rolling_rsi_low'] = closes['RSI'].rolling(period).min()
    closes['rolling_closing_high'] = closes.iloc[:, columns].rolling(period).max()
    closes['rolling_closing_low'] = closes.iloc[:, columns].rolling(period).min()


    closes['new_RSI_high'] = np.where(closes['rolling_rsi_high'] > closes['rolling_rsi_high'].shift(), 1, 0)
    closes['new_RSI_low'] = np.where(closes['rolling_rsi_low'] < closes['rolling_rsi_low'].shift(), 1, 0)


    closes['new_closing_high'] = np.where(closes['rolling_closing_high'] > closes['rolling_closing_high'].shift(), 1, 0)
    closes['new_closing_low'] = np.where(closes['rolling_closing_low'] < closes['rolling_closing_low'].shift(), 1, 0)

    bearishrsidiv = np.where((closes['new_closing_high'] == 1) & (closes['new_RSI_high'] == 0) & (closes['RSI'] > ob), 1, 0)
    bullishrsidiv = np.where((closes['new_closing_low'] == 1) & (closes['new_RSI_low'] == 0) & (closes['RSI'] < os), 1, 0)
   # closes.insert(1, 'bearish_rsi_div', bearishrsidiv)
   # closes.insert(2, 'bullish_rsi_div', bullishrsidiv)
    closes['bearish_rsi_div'] = np.where((closes['new_closing_high'] == 1) & (closes['new_RSI_high'] == 0) & (closes['RSI'] > ob), 1, 0)
    closes['bullish_rsi_div'] = np.where((closes['new_closing_low'] == 1) & (closes['new_RSI_low'] == 0) & (closes['RSI'] < os), 1, 0)
    closes = closes.dropna()
    return closes[['RSI', 'bullish_rsi_div', 'bearish_rsi_div']]



@app.route("/")
def index():
    rsi = request.args.get('rsi', None)
    if rsi:
        rsidata = []
        for column in range(179):
            rsidata.append(divs(closes, column))
            all = pd.concat(dict(zip(perpnames,rsidata)), axis=1)

            try:
                result = all
                last = result.tail(1).values[0]
                if last != 0:
                    print("{}  div detected {}".format(column, 'bullish'))
            except:
                pass
            
    return render_template("index.html", rsi=rsi)

@app.route("/snapshot")
def snapshot():
    return {
        'code': 'success'
    }




