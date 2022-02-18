#
# From https://github.com/marcusschiesser/intraday - slightly modified
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


def to_utc(d):
    return d.tz_convert(timezone.utc)


def df_to_utc(df):
    df.index = df.index.map(to_utc)


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


def get_lastday(df):
    if len(df) == 0:
        return date.today() - timedelta(days=5*365)
    max = df.index.max()
    return max.date()


def get(df, date):
    # TODO: If date doesn't exist, add a day at a time until it does
    return {"date": date.date(), "close": Decimal(df.loc[date, 'Close'])}


def get_last(df):
    max = df.index.max()
    # print(df.index)
    # print(df.columns)
    # print(df.Close)
    # print(df['Close'])
    # print(max.date(), df.loc[max, 'Close'])
    return {"date": max.date(), "close": Decimal(df.loc[max, 'Close'])}


def update_ticker(ticker):
    existing_df = get_cache(ticker)
    today = date.today()
    last_date = get_lastday(existing_df)
    start_date = last_date + timedelta(days=1)
    end_date = today + timedelta(days=7)
    #print("getting ticker[{}] Last[{}] Start[{}] Today[{}] End[{}]".format(ticker, last_date, start_date, today, end_date))
    if start_date <= today:
        #print("getting more data {} <= {}".format(start_date, today))
        # get new data
        t = yf.Ticker(ticker)
        updated_df = t.history(start=start_date, end=end_date)
        if not updated_df.empty:
            # append new data
            existing_df = existing_df.append(updated_df, sort=False)
            # serialize to CSV
            existing_df.to_csv(get_tickerfile(ticker))

    return existing_df


def get_ticker(ticker):
    df = get_cache(ticker)
    # return latest data as UTC
    # df_to_utc(df)
    return df
