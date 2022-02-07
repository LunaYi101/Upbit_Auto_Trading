import pyupbit 
import pandas as pd
import datetime 
import time 
import os
from datetime import datetime
from openpyxl import load_workbook


def sell_all(upbit_token):
    account = upbit_token.get_balances()
    
    for coin in account:
        print(coin)
        if coin['currency'] == "KRW":
            continue

        ticker = str(coin['unit_currency']) + "-" + str(coin['currency'])
        
        amount = upbit_token.get_balance(ticker)
        upbit_token.sell_market_order(ticker, amount)

        # bought_tickers = []
        
        # with open('bought_list.txt') as f:
        #     bought_tickers = f.read().splitlines()
        
        # with open("bought_list.txt", 'w') as output:
        #     for ticker in bought_tickers:
        #         output.write(str(ticker) + '\n')

        print("sold " +str(ticker))

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        cur_price = pyupbit.get_current_price(ticker)

        new_data = [current_time , ticker, 'sell', 999, 999, cur_price * amount, cur_price]

        wb = load_workbook('Records.xlsx')
        ws = wb.worksheets[0]

        ws.append(new_data)

        wb.save('Records.xlsx')

        print(new_data)

        # bought_tickers.remove(ticker)
        # with open("bought_list.txt", 'w') as output:
        #     for ticker in bought_tickers:
        #         output.write(str(ticker) + '\n')


def main():
    access_key = "hkdvoPjvx3GIO7XaEPOG8gQj8txUjyQUjWQdfXKB"
    secret_key = "0nx6nJriz6BSnxlxOCzNxPrcy1LKaqBQS4wUFAQf"

    upbit_token = pyupbit.Upbit(access_key, secret_key)

    sell_all(upbit_token)


if __name__ == '__main__':
    main()