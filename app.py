from crypt import methods
from flask import Flask, render_template, request, redirect, url_for, flash
import datetime as dt
import requests
import pandas as pd
import numpy as np
import matplotlib
import mplfinance as mpf
import talib
from tickers import alle
from tickers1 import htf
app = Flask(__name__)


@app.route("/")
def index():
    cols = (alle.iloc[-3:] != 0).any()
    websitedata = alle.iloc[-3:][cols[cols].index]
    return render_template("index.html", tables = [websitedata.to_html(classes='data')])

app.route("/4hours")
def hightimeframe():
    cols1 = (htf.iloc[-3:] != 0).any()
    websitedata = alle.iloc[-3:][cols1[cols1].index]
    return render_template("high.html", tables1 = [websitedata.to_html(classes='data')])





