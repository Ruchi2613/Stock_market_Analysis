from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from stk_data import get_data_by_date, get_current_data, MACD_NACDline, Stock_Line, Stock_Candel, RSI_calc, SMA_cal, buy_sell
import pandas as pd

app = Flask(__name__)

@app.route('/stock', methods=['post', 'get'])
def stock():
    """Invoke the search functionality to get the data
        and generate plots as required"""
    
    stk_info = []
    if request.method == 'POST':
        search = request.form.get('key')
        stk_info, hist_data = get_data_by_date(search)
        rsi = RSI_calc(search) # RSI indicator calculated on stock name
        sma = SMA_cal(search) # SMA indicator calculated on stock name
        MACD_NACDline(search) # Generates MACD Plot
        Stock_Line(search) # Generates Line Plot
        Stock_Candel(search) # Generates Candle Plot
        bs,b_count, s_count = buy_sell(search)

    return render_template('stock.html', search = search, stk_info = stk_info, hist_data = hist_data.values, rsi = rsi, sma = sma, bs = bs, b_count = b_count, s_count = s_count)


@app.route('/')
def index():
    """Renderes the Landing page with some famous stock details"""

    stk_info_apple = get_current_data("AAPL")
    stk_info_btc = get_current_data("BTC-USD")
    stk_info_amazon = get_current_data("AMZN")
    stk_info_clover = get_current_data("CLOV")
    stk_info_pfizer = get_current_data("PFE")
    stk_info_tesla = get_current_data("TSLA")
    stk_info_netflix = get_current_data("NFLX")
    stk_info_walmart = get_current_data("WMT")
    stk_info_google = get_current_data("GOOG")
    
    return render_template('index.html', stk_info_walmart = round(stk_info_walmart.values[0][0],2), stk_info_netflix = round(stk_info_netflix.values[0][0],2), stk_info_google = round(stk_info_google.values[0][0], 2), stk_info_apple = round(stk_info_apple.values[0][0], 2), stk_info_pfizer = round(stk_info_pfizer.values[0][0], 2), stk_info_btc = round(stk_info_btc.values[0][0], 2), stk_info_clover = round(stk_info_clover.values[0][0],2), stk_info_amazon = round(stk_info_amazon.values[0][0], 2), stk_info_tesla = round(stk_info_tesla.values[0][0], 2))


@app.route('/plotmacd')
def plotmacd():
    """Calls the MACD function to rendered the given plot generated"""
    return redirect(url_for('macd'))

@app.route('/plotline')
def plotline():
    """Calls the Line function to rendered the given plot generated"""
    return redirect(url_for('line'))

@app.route('/plotcandle')
def plotcandle():
    """Calls the Candle function to rendered the given plot generated"""
    return redirect(url_for('candle'))

@app.route('/macd')
def macd():
    return render_template('plots/macd.html')

@app.route('/line')
def line():
    return render_template('plots/line.html')
    
@app.route('/candle')
def candle():
    return render_template('plots/candle.html')

if __name__ == '__main__':
   app.run(debug=True)