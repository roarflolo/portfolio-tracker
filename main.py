import pandas as pd
import yfinance as yf
import datetime
import time
import requests
import io
import os
from pprint import pprint

def Nasdaq_GetCSV():
    filename = "nasdaq-listed_csv.csv";
    if not os.path.exists(filename):
        print("Getting NASDAQ data from the web")
        url = "https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_csv/data/7665719fb51081ba0bd834fde71ce822/nasdaq-listed_csv.csv"
        s = requests.get(url).content
        with open(filename, 'w') as file:
            file.write(s.decode('utf-8'))

    data = ""
    with open(filename, 'r') as file:
        data = file.read();

    return data

nasdaq_data = Nasdaq_GetCSV()
companies = pd.read_csv(io.StringIO(nasdaq_data))

symbols = companies['Symbol'].tolist()

symbols = ['AAPL']

pprint(symbols)


# create empty dataframe
#stock_final = pd.DataFrame()

start = datetime.datetime(2020,2,1)
end = datetime.datetime(2020,10,11)

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

#pprint(stock_final.head())
