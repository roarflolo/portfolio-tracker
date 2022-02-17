import pandas as pd
import yfinance as yf
import datetime
import time
import requests
import io
import os
from pprint import pprint
import data
from tradelog import TradeLog
from tradelog import GainLoss


def Nasdaq_GetCSV():
    filename = "nasdaq-listed_csv.csv"
    if not os.path.exists(filename):
        print("Getting NASDAQ data from the web")
        url = "https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_csv/data/7665719fb51081ba0bd834fde71ce822/nasdaq-listed_csv.csv"
        s = requests.get(url).content
        with open(filename, 'w') as file:
            file.write(s.decode('utf-8'))

    data = ""
    with open(filename, 'r') as file:
        data = file.read()

    return data

#nasdaq_list = Nasdaq_GetCSV()
#companies = pd.read_csv(io.StringIO(nasdaq_list))
#symbols = companies['Symbol'].tolist()


def Test():
    symbols = ['AAPL']
    pprint(symbols)

    # create empty dataframe
    #stock_final = pd.DataFrame()

    start = datetime.datetime(2020, 2, 1)
    end = datetime.datetime(2020, 10, 11)

    # iterate over each symbol
    for i in symbols:
        # print the symbol which is being downloaded
        #print( str(symbols.index(i)) + str(' : ') + i, sep=',', end=',', flush=True)
        try:
            # download the stock price
            stock = []
            stock = yf.download(i, start=start, end=end, progress=False)

            # append the individual stock prices
            if len(stock) == 0:
                None
            else:
                stock['Name'] = i
                pprint(stock)
                #stock_final = stock_final.append(stock, sort=False)

        except Exception:
            None

    # pprint(stock_final.head())


d = data.update_ticker("AAPL")
d = data.update_ticker("MSFT")
d = data.update_ticker("ROKU")
# pprint(d)

last_day = data.get_lastday(d)
# pprint(last_day)
v = data.get_last(d)
print(v)

v = data.get(d, datetime.datetime(2022, 2, 14))
print(v)


#p = Portfolio("Growth")
t1 = TradeLog()
t1.buy("AAPL", datetime.datetime(2020, 2, 1), 10, 123.45)
t1.buy("AAPL", datetime.datetime(2020, 2, 2), 10, 121.45)
t1.sell("AAPL", datetime.datetime(2020, 2, 3), 20, 124.45)

t1.buy("MSFT", datetime.datetime(2020, 1, 10), 10, 1.0)
t1.buy("MSFT", datetime.datetime(2020, 1, 12), 10, 2.0)
t1.sell("MSFT", datetime.datetime(2020, 1, 13), 19, 3.0)
t1.save("data/test-1.csv")
# p.add(t1)
# print(p)

t2 = TradeLog()
t2.load("data/test-1.csv")
t2.save("data/test-2.csv")

gl = t2.calc_gain_loss("MSFT", 3.0)
print(gl)
