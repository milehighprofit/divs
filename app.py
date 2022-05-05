from flask import Flask, render_template
#from tickers import alle
from tickers1 import htf
#from tickers2 import ltf
from tickers2 import rsidata, perpnames
import datetime as dt
import pandas as pd
import numpy as np
import requests
import mplfinance as mpf
import schedule
import time




app = Flask(__name__)
schedule.every(2).minutes.do(
ltf = pd.concat(dict(zip(perpnames,rsidata)), axis=1)
    cols2 = (ltf.iloc[-3:] != 0).any()
    websitedata2 = ltf.iloc[-3:][cols2[cols2].index]
    print(websitedata2))
@app.route('/')
def home():
    cols1 = (htf.iloc[-3:] != 0).any()
    websitedata1 = htf.iloc[-3:][cols1[cols1].index]
    return render_template("home.html", tables1 = [websitedata1.to_html(classes='data')])
#
#@app.route('/1hour/')
#def about():
#    cols = (alle.iloc[-3:] != 0).any()
#    websitedata = alle.iloc[-3:][cols[cols].index]

@app.route('/5min/')
def lowtimeframe():
    wb = scheduled()
    return render_template("lowtimeframe.html", tables1 = [wb.to_html(classes='data')])

if __name__ == '__main__':
    app.run(host = '0.0.0.0')