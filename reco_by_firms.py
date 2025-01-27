# Recommendations from big firms

import pandas as pd
import yfinance as yf

# Issue returns historical data

def rec_by_firms(stock_code):

    d = yf.Ticker(stock_code)

    pred = d.recommendations

    return pred

pr = rec_by_firms('AAPL')
pr.to_csv('pred.csv')