#
# # From https://github.com/marcusschiesser/intraday - slightly modified
#
import yfinance as yf
import pandas as pd
import numpy as np
import os
import ast
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
    try:
        return pd.read_csv(filename, parse_dates=True, index_col='Datetime')

    except ValueError:
        return pd.DataFrame()

    except FileNotFoundError:
        print("Ticker cache file '{}' not found.\n".format(filename))
        # return empty data frame on error
        return pd.DataFrame()


def get_lastday(df):
    if len(df) == 0:
        return date.today() - timedelta(days=365)
    max = df.index.max()
    return max.date()


def get_firstday(df):
    if len(df) == 0:
        return date.today() + timedelta(days=365)
    min = df.index.min()
    return min.date()


def update_ticker(ticker):
    existing_df = get_cache(ticker)
    start_date = get_lastday(existing_df) + timedelta(days=1)
    #end_date = start_date + timedelta(days=7)
    end_date = date.today() + timedelta(days=7)
    print("getting ticker {} from {} to {}".format(ticker, start_date, end_date))
    # get new data
    t = yf.Ticker(ticker)
    updated_df = t.history(start=start_date, end=end_date)
    if not updated_df.empty:
        # append new data
        existing_df = existing_df.append(updated_df, sort=False)
        # serialize to CSV
        existing_df.to_csv(get_tickerfile(ticker))
    # else:
    #    print("returned data for ticker is empty - do not update cache")

    return existing_df


def get_ticker(ticker):
    df = get_cache(ticker)
    # return latest data as UTC
    df_to_utc(df)
    return df
