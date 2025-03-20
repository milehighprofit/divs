import datetime as dt
import requests
import pandas as pd
import numpy as np
import matplotlib
import json    
import requests

resp = requests.get('https://api.kraken.com/0/public/OHLC?pair=XBTUSD')


data = resp.json()

print(data)