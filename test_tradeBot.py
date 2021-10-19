from talib import RSI, BBANDS
from datetime import datetime
import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time import time, sleep
import pprint

def get_coin_dataset():
    df = pd.read_csv('coin_dataset.csv')
    return df

def get_current_price(symbol):
    root_url = 'https://api.binance.com/api/v3/ticker/price'
    url = root_url + '?symbol=' + symbol
    data = json.loads(requests.get(url).text)
    return float(data["price"])

def take_by_period(dataframe,startPeriod,endPeriod):
    df = pd.DataFrame()
    for i in range(startPeriod,endPeriod):
        df = df.append(dataframe.iloc[i],ignore_index=True)

    return df


symbol = 'BAKEUSDT'

initial_budget = 2000

buyed_price = 0
selled_price = 0
profit = 0
n_coin = 0
operations = 0

BUY = False

coin_dataset = get_coin_dataset()

startPeriod = 0
endPeriod = 15

RSI_PERIOD = 14

DATASET_READING = True
RSI_MIN_LIMIT = 30
RSI_MAX_LIMIT = 70


budget = initial_budget
last_rsi = 0

FIRST = True
dump = False
pump = False

possible_pump = False


while DATASET_READING:

    if(endPeriod >= coin_dataset.shape[0]):
        DATASET_READING = False

    temp = take_by_period(coin_dataset,startPeriod,endPeriod)
    startPeriod = startPeriod + 1
    endPeriod = endPeriod + 1

    rsiCoin = RSI(temp['close'].astype('float'), timeperiod=RSI_PERIOD)

    current_rsi = rsiCoin.iloc[-1]

    last_price = temp['close'].iloc[-1]
    date = datetime.fromtimestamp(int(temp['close_time'].iloc[-1])/1000.0)
    date = date.strftime('%Y-%m-%d %H:%M:%S')

    if(last_rsi < RSI_MIN_LIMIT and current_rsi < last_rsi and not FIRST):
        dump = True
        print('dump! last rsi: ', last_rsi,' current_rsi: ', current_rsi)
    else:
        # print('stop dump! last rsi: ', last_rsi,' current_rsi: ', current_rsi)
        dump = False

    if(last_rsi < RSI_MAX_LIMIT and current_rsi > RSI_MAX_LIMIT and not FIRST and not possible_pump and BUY):
        possible_pump = True
        last_rsi = current_rsi
        FIRST = False
        continue
    
    if(current_rsi > last_rsi and possible_pump and BUY):
        possible_pump = True
        last_rsi = current_rsi
        FIRST = False
        continue
   
    elif(current_rsi < last_rsi and current_rsi > RSI_MAX_LIMIT and possible_pump and BUY): #>urrent_rsi > RSI_MAX_LIMIT in prova
        selled_price = last_price
        operations = operations + 1

        print(date,': You selled ', n_coin, ' ', symbol, 'for ', n_coin*selled_price, ' dollars, at price one: ', selled_price, '. RSI: ', current_rsi)

        print('Your Profit is ', (selled_price - buyed_price)*n_coin, ' Dollars')

        profit = (n_coin*selled_price) - initial_budget
        budget = n_coin*selled_price
        # profit = profit - (0.1/1000)*budget
        print('Your TOTAL Profit fort this coin is ', profit, ' Dollars')
        possible_pump = False
        BUY = False
        
        last_rsi = current_rsi
        FIRST = False
        continue


    if(current_rsi < RSI_MIN_LIMIT and not BUY and not dump):
        operations = operations + 1
        buyed_price = last_price
        n_coin = budget / buyed_price
        print(date,': You bought ', n_coin, ' ', symbol, 'for ', budget, ' dollars, at price one: ', buyed_price,'. RSI: ', current_rsi)
        # profit = profit - (0.1/1000)*budget
        BUY = True
        
        last_rsi = current_rsi
        FIRST = False
        continue

    if(not FIRST and BUY and dump):
        selled_price = last_price
        operations = operations + 1
        print(date,': DUMP??? You selled ', n_coin, ' ', symbol, 'for ', n_coin*selled_price, ' dollars, at price one: ', selled_price, '. RSI: ', current_rsi)
        print('Your Lose is ', (selled_price - buyed_price)*n_coin, ' Dollars')
        profit = (n_coin*selled_price) - initial_budget
        budget = n_coin*selled_price
        # profit = profit - (0.1/1000)*budget
        print('Your TOTAL Profit fort this coin is ', profit, ' Dollars')
        BUY = False  
        
        last_rsi = current_rsi
        FIRST = False
        continue

    last_rsi = current_rsi
    FIRST = False
    # if(current_rsi > RSI_MAX_LIMIT and BUY):
    #     selled_price = last_price
    #     operations = operations + 1

    #     print(date,': You selled ', n_coin, ' ', symbol, 'for ', n_coin*selled_price, ' dollars, at price one: ', selled_price, '. RSI: ', current_rsi)

    #     print('Your Profit is ', (selled_price - buyed_price)*n_coin, ' Dollars')

    #     profit = (n_coin*selled_price) - initial_budget
    #     budget = n_coin*selled_price
    #     # profit = profit - (0.1/1000)*budget
    #     print('Your TOTAL Profit fort this coin is ', profit, ' Dollars')
    #     BUY = False

    
    # if(current_rsi > RSI_MIN_LIMIT and BUY):
    #     print(datetime.now(), "Rsi value is: ", current_rsi, " HOLD")

    # if(current_rsi > RSI_MAX_LIMIT and not BUY):
    #     print(datetime.now(), "Rsi value is: ", current_rsi, " Not Time to Buy")

    # if(current_rsi < RSI_MIN_LIMIT and BUY):
    #     print(datetime.now(), "Rsi value is: ", current_rsi, " DUMP?")

if(BUY):
    print("You have: ", n_coin, "for a value of: ", n_coin*get_current_price(symbol), "So your ipotetically profit is: ", n_coin*get_current_price(symbol) - initial_budget)

print("Total Operations: ", operations)
