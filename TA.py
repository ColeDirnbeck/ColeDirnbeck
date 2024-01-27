import os
import enum
import calendar
import math
import pandas as pd
import numpy as np
import sqlite3
import datetime

from datetime import date
from scipy.stats import norm

from math import log, exp, sqrt
import option

from stock import Stock


class SimpleMovingAverages(object):
    '''
    On given a OHLCV data frame, calculate corresponding simple moving averages
    '''
    def __init__(self, ohlcv_df, periods):
        #
        self.ohlcv_df = ohlcv_df
        self.periods = periods
        self._sma = {}

    def _calc(self, period, price_source):
        '''
        for a given period, calc the SMA as a pandas series from the price_source
        which can be  open, high, low or Close
        '''
        result = None       # initialize variable called 'result' to be empty
        
        if price_source not in self.ohlcv_df.columns:                                           # check if the specified 'price_source' is not a valid column in the OHLCV DataFrame.
            raise ValueError(f"'{price_source}' is not a valid column in the OHLCV DataFrame.") # if it's not a valid column, raise an error & provide an error message
        try:                                                                                    # try to calculate the SMA for the specified 'price_source' & 'period'
            result = self.ohlcv_df[price_source].rolling(window=period).mean()                  # calculate SMA using the rolling method: take a window of 'period' data points, compute the avg, & store the results in 'result' var
        except Exception as e:
            print(f"Error calculating SMA: {e}")                                                # if there's an error during the calculation, print an error message along w/ the specific error details

        return result                                                                           # return the calculated SMA result (or None if there was an error during calculation).

        
    def run(self, price_source = 'Close'):
        '''
        Calculate all the simple moving averages as a dict
        '''
        for period in self.periods:
            self._sma[period] = self._calc(period, price_source)
    
    def get_series(self, period):
        return(self._sma[period])

    
class ExponentialMovingAverages(object):
    '''
    On given a OHLCV data frame, calculate corresponding simple moving averages
    '''
    def __init__(self, ohlcv_df, periods):
        #
        self.ohlcv_df = ohlcv_df
        self.periods = periods
        self._ema = {}

    def _calc(self, period):
        '''
        for a given period, calc the SMA as a pandas series
        '''
        result = None           # initialize variable called 'result' to be empty

        if 'Close' not in self.ohlcv_df.columns:                                                # check if the specified 'Close' is not a valid column in the OHLCV DataFrame.
            raise ValueError("OHLCV DataFrame must have a 'Close' column to calculate EMA.")    # if it's not a valid column, raise an error & provide an error message
        try:                                                                                    # calculate the EMA using the 'Close' column for the specified period.
            result = self.ohlcv_df['Close'].ewm(span=period, adjust=False).mean()               # the 'adjust' parameter specifies how to normalize the EMA (True for unbiased, False for biased).
        except Exception as e:
            print(f"Error calculating EMA: {e}")                                                # if there's an error during the calculation, print an error message along w/ the specific error details

        return result                                                                           # return the calculated EMA result (or None if there was an error during calculation).
        
    def run(self):
        '''
        Calculate all the simple moving averages as a dict
        '''
        for period in self.periods:
            self._ema[period] = self._calc(period)

    def get_series(self, period):
        return(self._ema[period])


class RSI(object):

    def __init__(self, ohlcv_df, period = 14):
        self.ohlcv_df = ohlcv_df
        self.period = period
        self.rsi = None

    def get_series(self):
        return(self.rsi)

    def run(self):
        
        price_differences = self.ohlcv_df['Close'].diff(1)          # calculate price differences

        gain = price_differences.where(price_differences > 0, 0)    # separates gains and losses 
        loss = -price_differences.where(price_differences < 0, 0)
     
        avg_gain = gain.ewm(span=self.period, adjust=False).mean()  # calculates avg gain and loss w/ EMA
        avg_loss = loss.ewm(span=self.period, adjust=False).mean()
        
        rs = avg_gain / avg_loss            # calculate relative strength (given formula)
        
        self.rsi = 100 - (100 / (1 + rs))   # given

class VWAP(object):

    def __init__(self, ohlcv_df):
        self.ohlcv_df = ohlcv_df
        self.vwap = None

    def get_series(self):
        return(self.vwap)

    def run(self):
        # Step 1: Calculate the product of Price and Volume for each data point.
        price_volume_product = self.ohlcv_df['Close'] * self.ohlcv_df['Volume']

        # Step 2: Calculate the cumulative sum of the Price-Volume products, which represents the cumulative total value of the traded assets.
        cumulative_price_volume = price_volume_product.cumsum()

        # Step 3: Calculate the cumulative total volume, which represents the cumulative total number of assets traded.
        cumulative_volume = self.ohlcv_df['Volume'].cumsum()

        # Step 4: Calculate the VWAP as the ratio of cumulative Price-Volume to cumulative volume.
        self.vwap = cumulative_price_volume / cumulative_volume

def _test1():
    opt = option.Option()
    # set default settings

    # we use relative path here, you can set it with a full path
    opt.data_dir = "./data"
    opt.output_dir = os.path.join(opt.data_dir, "daily")
    opt.sqlite_db = os.path.join(opt.data_dir, "sqlitedb/Equity.db")

    ticker = 'AAPL'
    db_connection = sqlite3.connect(opt.sqlite_db)
    stock = Stock(opt, db_connection, ticker)

    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2023, 10, 1)

    #start_date = datetime.date(2015, 1, 1)
    #end_date = datetime.date(2019, 10, 1)
    
    df = stock.get_daily_hist_price(start_date, end_date)
    print(df.head())
    print(df.tail())
    
    periods = [9, 20, 50, 100, 200]
    smas = SimpleMovingAverages(df, periods)
    smas.run()
    s1 = smas.get_series(9)
    print("9 SMA", s1.index)
    print("9 SMA", s1.head(10))
    print("9 SMA", s1.tail(10))

    s2 = smas.get_series(50)
    print("50 SMA",s2.tail(10))
    
    rsi_indicator = RSI(df)
    rsi_indicator.run()

    print(f"RSI for {ticker} is {rsi_indicator.rsi}")

    vwap_indicator = VWAP(df)
    vwap_indicator.run()  # Calculate the VWAP
    vwap_1 = vwap_indicator.get_series()
    print("Volume Weighed Average Price (VWAP)")
    print(f"VWAP for {ticker} is {list(vwap_1.items())[-1][1]}")
    print(vwap_indicator.vwap)
    
if __name__ == "__main__":
    _test1()