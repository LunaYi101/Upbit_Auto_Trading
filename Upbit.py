import pyupbit 
import pandas as pd
import datetime 
import time 
import os
from datetime import datetime
from openpyxl import load_workbook

access_key = "hkdvoPjvx3GIO7XaEPOG8gQj8txUjyQUjWQdfXKB"
secret_key = "0nx6nJriz6BSnxlxOCzNxPrcy1LKaqBQS4wUFAQf"

upbit_token = pyupbit.Upbit(access_key, secret_key)

def rsi(ohlc: pd.DataFrame, period: int = 14): 
    delta = ohlc["close"].diff() 
    ups, downs = delta.copy(), delta.copy() 
    ups[ups < 0] = 0 
    downs[downs > 0] = 0 

    AU = ups.ewm(com = period-1, min_periods = period).mean() 
    AD = downs.abs().ewm(com = period-1, min_periods = period).mean() 
    RS = AU/AD 
    return pd.Series(100 - (100/(1 + RS)), name = "RSI") 

def by_value(item):
    return item[1]

def buy(ticker, cur_rsi, past_rsi):
    if cur_rsi <= past_rsi+0.05:
        return

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    cur_price = pyupbit.get_current_price(ticker)

    upbit_token.buy_market_order(ticker, 10000)

    new_data = [current_time , ticker, 'buy', cur_rsi, past_rsi, '10000', cur_price]
    print(new_data)

    wb = load_workbook('Records.xlsx')
    ws = wb.worksheets[0]

    ws.append(new_data)

    wb.save('Records.xlsx')

    bought_tickers = []
    with open('bought_list.txt') as f:
        bought_tickers = f.read().splitlines()

    if ticker not in bought_tickers:
        bought_tickers.append(ticker)

    with open("bought_list.txt", 'w') as output:
        for ticker in bought_tickers:
            output.write(str(ticker) + '\n')

def sell(ticker, cur_rsi, past_rsi):
    if cur_rsi >= past_rsi-0.05:
        return

    bought_tickers = []
    with open('bought_list.txt') as f:
        bought_tickers = f.read().splitlines()

    if ticker not in bought_tickers:
        return

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    cur_price = pyupbit.get_current_price(ticker)
    amount = upbit_token.get_balance(coin_name)

    if not (cur_rsi > 80 or past_rsi > 80):
        amount = amount / 2.0

    upbit_token.sell_market_order(coin_name, amount)

    new_data = [current_time , ticker, 'sell', cur_rsi, past_rsi, cur_price * amount, cur_price]

    wb = load_workbook('Records.xlsx')
    ws = wb.worksheets[0]

    ws.append(new_data)

    wb.save('Records.xlsx')

    print(new_data)

    bought_tickers.remove(coin_name)
    with open("bought_list.txt", 'w') as output:
        for ticker in bought_tickers:
            output.write(str(ticker) + '\n')

# getting korean tickers
tickers = pyupbit.get_tickers()
kr_tickers = []
past_rsi = {}

for ticker in tickers:
    if ticker[0:3] == "KRW":
        kr_tickers.append(ticker)

for ticker in kr_tickers:
    past_rsi[ticker] = 50

while True:
    for coin_name in kr_tickers:
        data = pyupbit.get_ohlcv(ticker = coin_name, interval="minute1")
        cur_rsi = rsi(data, 14).iloc[-1]
        
        if past_rsi[coin_name] < 30 and cur_rsi < 30:
            print("Attept to buy " + str(coin_name) + " at cur_rsi: " + str(cur_rsi) + " and past_rsi: " + str(past_rsi[coin_name]))
            buy(coin_name, cur_rsi, past_rsi = past_rsi[coin_name])

        elif past_rsi[coin_name] > 70:
            print("Attept to sell " + str(coin_name) + " at cur_rsi: " + str(cur_rsi) + " and past_rsi: " + str(past_rsi[coin_name]))
            sell(coin_name, cur_rsi, past_rsi=past_rsi[coin_name])
        
        else:
            print("Current State " + str(coin_name) + " at cur_rsi: " + str(cur_rsi) + " and past_rsi: " + str(past_rsi[coin_name]))
        
        past_rsi[coin_name] = cur_rsi
