import os
import pandas as pd
import numpy as np
import sqlite3
import datetime 
import math

import option
from stock import Stock

class DiscountedCashFlowModel(object):
    '''
    DCF Model:

    FCC is assumed to go have growth rate by 3 periods, each of which has different growth rate:
           short_term_growth_rate for the next 5 years
           medium_term_growth_rate from year 6 to year 10
           long_term_growth_rate from year 11 to year 20
    '''

    def __init__(self, stock, as_of_date):
        self.stock = stock
        self.as_of_date = as_of_date

        self.short_term_growth_rate = None
        self.medium_term_growth_rate = None
        self.long_term_growth_rate = None


    def set_FCC_growth_rate(self, short_term_rate, medium_term_rate, long_term_rate):
        self.short_term_growth_rate = short_term_rate
        self.medium_term_growth_rate = medium_term_rate
        self.long_term_growth_rate = long_term_rate

    

    def calc_fair_value(self):
               
        eps5y = self.short_term_growth_rate
        eps6to10y = self.medium_term_growth_rate
        eps10to20y = self.long_term_growth_rate
        
        try:
            # calculate a yearly discount factor using the discount rate value acquired from lookup_wacc_by_beta
            discount_factor = 1 / (1 + self.stock.lookup_wacc_by_beta(self.stock.get_beta()))
            discounted_fcc = 0.00

            # get the Free Cash Flow
            free_cash_flow = self.stock.get_free_cashflow()

            # sum the discounted value of the FCC for the first 5 years using the short-term growth rate
            for year in range(1, 6):
                discounted_fcc += (free_cash_flow * (((1 + self.short_term_growth_rate) ** year) * (discount_factor ** year)))

            # add the discounted value of the FCC from year 6 to the 10th year using the medium-term growth rate
            for year in range(6, 11):
                discounted_fcc += (free_cash_flow * ((1 + self.short_term_growth_rate) ** 5)) * (((1 + self.medium_term_growth_rate) ** (year-5)) * (discount_factor ** year))
                
            # ad the discounted value of the FCC from year 10 to the 20th year using the long-term growth rate
            for year in range(11, 21):
                discounted_fcc += (free_cash_flow * ((1 + self.short_term_growth_rate) ** 5)) * (((1 + self.medium_term_growth_rate) ** 5)) * (((1 + self.long_term_growth_rate) ** (year-10)) * (discount_factor ** year))

            # compute the PV as cash + short-term investments - total debt + the above sum of discounted free cash flow
            cash_and_equivalent = self.stock.get_cash_and_cash_equivalent()
            total_debt = self.stock.get_total_debt()
            present_value = cash_and_equivalent - total_debt + discounted_fcc

            # return the stock fair value as PV divided by the number of shares outstanding
            fair_value = present_value / self.stock.get_num_shares_outstanding()
            return fair_value
        except Exception as e:
            print(f"An error occurred during DCF calculation: {str(e)}")
            return None

        return(result)


def _test1():
    # overried the various financial data
    class StockForTesting(Stock):
        # mark-up Stock object for testing and tie-out purpose
        def get_total_debt(self):
            result = 112723000 * 1000
            return result

        def get_free_cashflow(self):
            result = 71706000 * 1000
            return result

        def get_num_shares_outstanding(self):
            result = 17250000000                    # grabbed from blog
            return result

        def get_cash_and_cash_equivalent(self):
            result = 93025000 * 1000                # grabbed from blog
            return result
        
        def get_beta(self):
            result = 1.32
            return result

        def lookup_wacc_by_beta(self, beta):
            if beta < 0.80:                         # table grabbed from blog
                discount_rate = 0.05
            elif 0.80 <= beta < 1.00:
                discount_rate = 0.06
            elif 1.00 <= beta < 1.10:
                discount_rate = 0.065
            elif 1.10 <= beta < 1.20:
                discount_rate = 0.07
            elif 1.20 <= beta < 1.30:
                discount_rate = 0.075
            elif 1.30 <= beta < 1.50:
                discount_rate = 0.08
            elif 1.50 <= beta < 1.60:
                discount_rate = 0.085
            else:
                discount_rate = 0.09

            return discount_rate

    opt = None
    db_connection = None
    symbol = 'Testing AAPL'
    stock = StockForTesting(opt, db_connection, symbol)

    
    as_of_date = datetime.date(2020, 9, 28)
    model = DiscountedCashFlowModel(stock, as_of_date)

    print(f"Running test1 for {symbol} ")
    print("Shares ", stock.get_num_shares_outstanding())
    print("FCC ", stock.get_free_cashflow())
    beta = stock.get_beta()
    wacc = stock.lookup_wacc_by_beta(beta)
    print("Beta ", beta)
    print("WACC ", wacc)
    print("Total debt ", stock.get_total_debt())
    print("Cash ", stock.get_cash_and_cash_equivalent())

    # look up EPS next 5Y from Finviz, 12.46% from the medium blog
    eps5y = 0.1246
    model.set_FCC_growth_rate(eps5y, eps5y / 2, 0.04)

    model_price = model.calc_fair_value()
    print(f"DCF price for {symbol} as of {as_of_date} is {model_price}")

def _test2():
    #
    eps5YData = {'AAPL': 0.074, 'BABA': 0.1058, 'GOOGL': 0.2015, 'TSLA': 0.0855, 'NVDA': 0.7870} 

    symbols = ['AAPL', 'BABA', 'GOOGL', 'TSLA', 'NVDA'] # didn't realize that we did this in run_DCF.py, so this is pretty reductive

    # default option
    opt = option.Option()
    opt.data_dir = "./data"
    opt.output_dir = os.path.join(opt.data_dir, "daily")
    opt.sqlite_db = os.path.join(opt.data_dir, "sqlitedb/Equity.db")

    db_file = opt.sqlite_db
    db_connection = sqlite3.connect(db_file)

    as_of_date = datetime.date(2023, 10, 1)

    for symbol in symbols:
        stock = Stock(opt, db_connection, symbol)
        stock.load_financial_data()

        model = DiscountedCashFlowModel(stock, as_of_date)

        print("Shares ", stock.get_num_shares_outstanding())
        print("FCC ", stock.get_free_cashflow())
        beta = stock.get_beta()
        wacc = stock.lookup_wacc_by_beta(beta)
        print("Beta ", beta)
        print("WACC ", wacc)
        print("Total debt ", stock.get_total_debt())
        print("Cash ", stock.get_cash_and_cash_equivalent())

        # look up EPS next 5Y from Finviz, 12.46% from the medium blog
        eps5y = eps5YData[symbol]
    
        model.set_FCC_growth_rate(eps5y, eps5y / 2, 0.04)

        model_price = model.calc_fair_value()
        print(f"DCF price for {symbol} as of {as_of_date} is {model_price}")
  

def _test():
    _test1()
    _test2()
    
if __name__ == "__main__":
    _test()

