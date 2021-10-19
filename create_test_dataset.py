import pytz
import dateparser
from talib import RSI, BBANDS
from datetime import datetime
import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time import time, sleep
import pprint

def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)

def get_coin_dataset(symbol, interval,endTime,limit):
    root_url = 'https://api.binance.com/api/v3/klines'
    url = root_url + '?symbol=' + symbol + '&interval=' + interval + '&limit=' + str(limit) + '&endTime=' + str(endTime)
    data = json.loads(requests.get(url).text)
    df = pd.DataFrame(data)
    df.columns = ['open_time',
                 'open', 'high', 'low', 'close', 'volume',
                 'close_time', 'qav', 'num_trades',
                 'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [datetime.fromtimestamp(x/1000.0) for x in df.close_time]
    df.drop(df.tail(1).index,inplace=True) # drop last n rows
    return df

symbol = 'BAKEUSDT'
interval = '15m'

def create_dataset_csv(symbol, interval):
    
    if(interval == '3m'):
        limit = 480
    elif(interval == '15m'):
        limit = 96
    elif(interval == '30m'):
        limit = 48
    elif(interval == '1h'):
        limit = 24
    elif(interval == '4h'):
        limit = 6
    elif(interval == '1d'):
        limit = 2
    
    coin_dataset = get_coin_dataset(symbol,interval,date_to_milliseconds(str(datetime.now())),limit)   

    for i in range(31):
        temp_coin_dataset = get_coin_dataset(symbol,interval,str(coin_dataset['close_time'].iloc[0]),limit)
        coin_dataset = pd.concat([temp_coin_dataset, coin_dataset], sort=False)

    coin_dataset.to_csv('coin_dataset.csv')


create_dataset_csv(symbol,interval)