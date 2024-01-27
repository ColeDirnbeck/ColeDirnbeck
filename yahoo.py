import os
import pandas as pd
import numpy as np
import sqlite3

import pandas_datareader as pdr

import yfinance as yf

import option

def get_daily_from_yahoo(ticker, start_date, end_date):                        #acquires daily stock data from Yahoo finance
    stock = yf.Ticker(ticker)                                                  #object representing stock/financial instrument to be called
                                                                               
    df = stock.history(period="1d", start=start_date, end=end_date)            #uses the history method the stock object and stores the data in dataframe 'df'
                                                                               
    return df                                                                  #returns Yahoo finance history for stock

def download_data_to_csv(opt, list_of_tickers):                                #takes daily stock data and downloads into csv file
    
    for ticker in list_of_tickers:
        # Get daily stock data for the ticker
        df = get_daily_from_yahoo(ticker, opt.start_date, opt.end_date)
        
        # Add a 'Ticker' column with the ticker symbol
        df['Ticker'] = ticker
        
        # Create the filename for the CSV file (e.g., AAPL_daily.csv)
        filename = os.path.join(opt.output_dir, f"{ticker}_daily.csv")
        
        # Save the DataFrame to a CSV file
        df.to_csv(filename)
        
        # Added from AP.py
        if df.shape[0] == 0:
            print(f"No data found for {ticker}")

    pass

def csv_to_table(csv_file_name, fields_map, db_connection, db_table):
    
        # insert data from a csv file to a table
        df = pd.read_csv(csv_file_name)
        if df.shape[0] <= 0:
            return
        # change the column header
        df.columns = [fields_map[x] for x in df.columns]

        # move ticker columns
        new_df = df[['Ticker']].copy()
        for c in df.columns[:-1]:
            new_df.loc[:, c] = df[c]

        # drop the StockSplits column
        new_df.drop(['StockSplits'], axis=1, inplace=True)
        # insert a TurnOver column with zero
        new_df.insert(loc = new_df.shape[1] - 1, column = 'TurnOver', value = [0] * new_df.shape[0])
        #print(new_df.head())

        ticker = os.path.basename(csv_file_name).replace('.csv','').replace("_daily", "")
        print(ticker)
        cursor = db_connection.cursor()

        # Delete old data for the ticker
        sql_delete = f"DELETE FROM {db_table} WHERE Ticker = '{ticker}'"
        #print(sql_delete)
        cursor.execute(sql_delete)
        
        #print(new_df)
        data = new_df.values.tolist()

        # Insert new data with IGNORE clause to handle duplicates
        sql_insert = f"INSERT OR REPLACE INTO {db_table} (Ticker, AsOfDate, Open, High, Low, Close, Volume, TurnOver, Dividend) "
        sql_insert += " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?); "
        #print(sql_insert)

        try:
            cursor.executemany(sql_insert, data)
            db_connection.commit()
            # Close the cursor and database connection
            cursor.close()
            # Print that data successfully inserted
            print("Data inserted successfully!")
        except Exception as e:
            print(f"Failed in uploading {ticker} because {e}")       

def save_daily_data_to_sqlite(opt, daily_file_dir, list_of_tickers):
    # read all daily.csv files from a dir and load them into sqlite table
    db_file = os.path.join(opt.sqlite_db)
    db_conn = sqlite3.connect(db_file)
    db_table = 'EquityDailyPrice'
    
    fields_map = {'Date': 'AsOfDate', 'Dividends': 'Dividend', 'Stock Splits': 'StockSplits'}
    for f in ['Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']:
        fields_map[f] = f

    for ticker in list_of_tickers:
        file_name = os.path.join(daily_file_dir, f"{ticker}_daily.csv")
        #print(file_name)
        csv_to_table(file_name, fields_map, db_conn, db_table)

    #close the db connection
    db_conn.close()
    
def _test():
    ticker = 'MSFT'
    start_date = '2020-01-01'
    end_date = '2023-08-01'

    print (f"Testing getting data for {ticker}:")
    df = get_daily_from_yahoo(ticker, start_date, end_date)
    print(df)

def run():
    #
    parser = option.get_default_parser()
    parser.add_argument('--data_dir', dest = 'data_dir', default='./data', help='data dir')    
    
    args = parser.parse_args()
    opt = option.Option(args = args)

    opt.output_dir = os.path.join(opt.data_dir, "daily")
    opt.sqlite_db = os.path.join(opt.data_dir, "sqlitedb/Equity.db")

    if opt.tickers is not None:
        list_of_tickers = opt.tickers.split(',')
    else:
        fname = "C:\Program Files\SQLiteStudio\LABS\data\S&P500.txt"
        list_of_tickers = list(pd.read_csv(fname, header=None).iloc[:, 0])
        print(f"Read tickers from {fname}")
        

    print(list_of_tickers)
    print(opt.start_date, opt.end_date)

    # download all daily price data into a output dir
    if 1:
        print(f"Download data to {opt.data_dir} directory")
        download_data_to_csv(opt, list_of_tickers)

    if 1:
        # read the csv file back and save the data into sqlite database
        save_daily_data_to_sqlite(opt, opt.output_dir, list_of_tickers)
    
if __name__ == "__main__":
    #_test()
    run()