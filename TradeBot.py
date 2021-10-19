#%%
from talib import RSI, BBANDS
from datetime import datetime
import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time import time, sleep
import pprint

def get_coin_dataset(symbol, interval):
    root_url = 'https://api.binance.com/api/v3/klines'
    url = root_url + '?symbol=' + symbol + '&interval=' + interval + '&limit=' + str(100)
    data = json.loads(requests.get(url).text)
    df = pd.DataFrame(data)
    df.columns = ['open_time',
                 'open', 'high', 'low', 'close', 'volume',
                 'close_time', 'qav', 'num_trades',
                 'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [datetime.fromtimestamp(x/1000.0) for x in df.close_time]
    df.drop(df.tail(1).index,inplace=True) # drop last n rows
    return df

def get_current_price(symbol):
    root_url = 'https://api.binance.com/api/v3/ticker/price'
    url = root_url + '?symbol=' + symbol
    data = json.loads(requests.get(url).text)
    return float(data["price"])


symbol = input("Inserisci crypto da traddare: ")

# coin_dataset = get_coin_dataset(symbol,'1d')
# pprint.pprint(coin_dataset)

budget = 200
buyed_price = 0
selled_price = 0
profit = 0
n_coin = 0

BUY = False

while True:
    coin_dataset = get_coin_dataset(symbol,'3m')
    rsiCoin = RSI(coin_dataset['close'].astype('float'), timeperiod=6)

    last_price = get_current_price(symbol)
    last_rsi = rsiCoin.iloc[-1]

    if(last_rsi < 30 and not BUY):
        buyed_price = last_price
        n_coin = 200 / buyed_price
        print(datetime.now(), 'You bought ', n_coin, ' ', symbol, 'for ', budget, ' dollars, at price one: ', buyed_price)
        BUY = True

    if(last_rsi > 70 and BUY):
        selled_price = last_price
        profit = profit + (n_coin*selled_price) - budget
        print(datetime.now(), 'You sell ', n_coin, ' ', symbol, 'for ', n_coin*selled_price, ' dollars, at price one: ', selled_price)
        print(datetime.now(), 'Your Profit is ', profit, ' Dollars')
        print(datetime.now(), 'Your TOTAL Profit fort this coin is ', profit, ' Dollars')
        budget = n_coin*selled_price
        BUY = False

    if(last_rsi > 30 and BUY):
        print(datetime.now(), "Rsi value is: ", last_rsi, " HOLD")
    
    if(last_rsi > 30 and not BUY):
        print(datetime.now(), "Rsi value is: ", last_rsi, " Not Time to Buy")

    if(last_rsi < 30 and BUY):
        print(datetime.now(), "Rsi value is: ", last_rsi, " DUMP?")
    
    sleep(190)


# fig, (ax0, ax1) = plt.subplots(2, 1, sharex=True, figsize=(18, 11))

# ax0.plot(coin_dataset.index, coin_dataset['close'].astype('float'), label='AdjClose')
# ax0.set_ylabel('Price')
# ax0.grid()


# ax1.plot(coin_dataset.index, rsiCoin, label='RSI')
# plt.yticks(np.arange(0,110,step=10))
# ax1.set_xlabel('Date')
# ax1.set_ylabel('RSI')
# ax1.grid()




# %%
