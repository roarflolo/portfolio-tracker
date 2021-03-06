#
# From https://github.com/marcusschiesser/intraday - modified
# https://pythoninoffice.com/get-values-rows-and-columns-in-pandas-dataframe/
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.append.html
#
from pprint import pprint
import yfinance as yf
import pandas as pd
import numpy as np
import os
import ast
from decimal import Decimal
from datetime import datetime, date, timedelta, timezone


# def to_utc(d):
#    return d.tz_convert(timezone.utc)
#
#
# def df_to_utc(df):
#    df.index = df.index.map(to_utc)


def get_tickerfile(ticker):
    dirname = os.path.dirname(__file__)
    return dirname + '/data/' + ticker + '.csv'


def get_cache(ticker):
    filename = get_tickerfile(ticker)
    #print("get_cache " + ticker + " " + filename)
    try:
        #print("read_csv " + ticker + " " + filename)
        return pd.read_csv(filename, delimiter=",", parse_dates=True, index_col='Date')

    except ValueError:
        print("get_cache ValueError " + ticker)
        return pd.DataFrame()

    except FileNotFoundError:
        print("Ticker cache file '{}' not found.\n".format(filename))
        # return empty data frame on error
        return pd.DataFrame()


# get last date we have in our dataframe
def get_lastdate(df):
    if len(df) == 0:
        return date.today() - timedelta(days=5*365)
    max = df.index.max()
    return max.date()


# Get date/close pair at a specific date
def get(df, date):
    max = df.index.max()
    while date < max and date not in df.index:
        date = date + timedelta(days=1)

    if date in df.index:
        return {"date": date.date(), "close": Decimal(df.loc[date, 'Close'])}
    else:
        return {"date": date.date(), "close": Decimal(0)}


# Get last date/close pair
def get_last(df):
    max = df.index.max()
    # print(df.index)
    # print(df.columns)
    # print(df.Close)
    # print(df['Close'])
    # print(max.date(), df.loc[max, 'Close'])
    return {"date": max.date(), "close": Decimal(df.loc[max, 'Close'])}


# update the dataset for a ticker, getting new data from Yahoo Finance if needed
def update_ticker(ticker):
    existing_df = get_cache(ticker)

    # Figure out if we need to get more data from Yahoo Finance.
    # We do not get data from today as the market may still be open (could add check for that)
    last_date = get_lastdate(existing_df)
    start_date = last_date + timedelta(days=1)
    today = date.today()
    end_date = today - timedelta(days=1)
    #print("Ticker[{}] Update - Last[{}] Start[{}] Today[{}] End[{}]".format(ticker, last_date, start_date, today, end_date))
    if start_date < today and end_date >= start_date:
        print("Ticker[{}] Getting data Start[{}] End[{}]".format(ticker, start_date, end_date))
        t = yf.Ticker(ticker)
        updated_df = t.history(start=start_date, end=end_date)
        if not updated_df.empty:
            existing_df = pd.concat([existing_df, updated_df], sort=True)
            existing_df.to_csv(get_tickerfile(ticker))

    return existing_df
